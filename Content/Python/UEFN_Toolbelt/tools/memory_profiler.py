"""
UEFN TOOLBELT — Memory Inspection
=================================
Inspects registry-listed Texture2D, StaticMesh and SoundWave assets in the
resolved project mount. Failed loading and unavailable metrics remain unknown.

Measurements are authoring heuristics: texture pixel dimensions and base-level
uncompressed RGBA estimates, LOD0 vertex counts, LOD counts, and sound duration.
These do not measure Fortnite runtime memory, residency, compression, collision,
particle cost, or the island's publish budget. Use native memory calculation for
runtime budget acceptance. The LOD convenience action delegates to the existing
LOD tool; its result determines availability and outcome.

Full reports are written atomically to the native project's
Saved/UEFN_Toolbelt/memory_report.json with project/scan identity and unknown
counts. Subfolder reports cannot establish full-project readiness.

Usage:
    import UEFN_Toolbelt as tb
    # Inspect the resolved /<project mount> and save a scoped report.
    tb.run("memory_scan", scan_path="")
    tb.run("memory_scan_textures", scan_path="", max_size_px=2048)
    tb.run("memory_scan_meshes", scan_path="")
    tb.run("memory_top_offenders", scan_path="", top_n=10)
    tb.run("memory_autofix_lods", scan_path="")
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path

import unreal

from ..core import (
    detect_project_mount,
    load_asset,
    log_info,
    native_project_dir,
    resolve_scan_path,
    scannable_assets,
)
from ..registry import register_tool

# ─────────────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Texture resolution thresholds (pixels, square)
TEXTURE_WARN_PX  = 2048   # Flag as large
TEXTURE_CRIT_PX  = 4096   # Flag as critical

# Mesh LOD0 vertex-count thresholds
MESH_WARN_TRIS   = 50_000
MESH_CRIT_TRIS   = 200_000

# Sound duration thresholds (seconds)
SOUND_WARN_SECS  = 30.0
SOUND_CRIT_SECS  = 120.0

# ─────────────────────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _list_assets_of_class(scan_path: str, class_name: str) -> list[tuple[str, unreal.Object]]:
    """Use class metadata to retain assets whose native loading is unavailable."""
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    metadata = registry.get_assets_by_path(scan_path, recursive=True)
    if metadata is None:
        raise ValueError("Asset registry enumeration is unavailable")
    results = []
    for item in metadata:
        if str(item.asset_class_path.asset_name) != class_name:
            continue
        path = f"{item.package_name}.{item.asset_name}"
        if not scannable_assets([path]):
            continue
        try:
            asset = load_asset(path)
            if asset is not None and str(asset.get_class().get_name()) != class_name:
                asset = None
        except Exception:
            asset = None
        results.append((path, asset))
    return results


def _checked_number(value, *, integer=False, minimum=0):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < minimum
            or (integer and int(value) != value)):
        raise ValueError("Inspection returned an invalid numeric value")
    return int(value) if integer else float(value)


def _texture_info(asset: unreal.Texture2D) -> dict:
    """Extract checked resolution; unavailable dimensions are never zero estimates."""
    width = height = None
    unknown = []
    for field, method, prop, fallback in (
            ("width", "blueprint_get_size_x", "blueprint_width", "source_art_width"),
            ("height", "blueprint_get_size_y", "blueprint_height", "source_art_height")):
        try:
            value = _checked_number(getattr(asset, method)(), integer=True, minimum=1)
        except Exception:
            try:
                value = _checked_number(asset.get_editor_property(prop), integer=True, minimum=1)
            except Exception:
                try:
                    value = _checked_number(getattr(asset, fallback), integer=True, minimum=1)
                except Exception:
                    value = None
                    unknown.append(field)
        if field == "width":
            width = value
        else:
            height = value
    complete = not unknown
    max_dim = max(width, height) if complete else None
    estimate = round(width * height * 4 / 1024, 1) if complete else None
    severity = "unknown" if not complete else (
        "critical" if max_dim >= TEXTURE_CRIT_PX else
        "warning" if max_dim >= TEXTURE_WARN_PX else "ok")
    return {"width": width, "height": height, "max_dim": max_dim,
            "estimated_vram_kb": estimate, "severity": severity,
            "inspection_complete": complete, "unknown_fields": unknown,
            "load_failed": asset is None}


def _mesh_info(asset: unreal.StaticMesh) -> dict:
    """Extract checked vertex/LOD counts; uninspected LODs are not missing LODs."""
    lod_count = vertices = None
    unknown = []
    if asset is None:
        return {"lod_count": None, "approx_verts": None, "missing_lods": None,
                "severity": "unknown", "inspection_complete": False,
                "unknown_fields": ["lod_count", "approx_verts"], "load_failed": True}
    try:
        mesh_sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    except Exception:
        mesh_sub = None
    try:
        lod_count = _checked_number(mesh_sub.get_lod_count(asset), integer=True)
    except Exception:
        unknown.append("lod_count")
    try:
        vertices = _checked_number(mesh_sub.get_number_verts(asset, 0), integer=True)
    except Exception:
        unknown.append("approx_verts")
    missing = lod_count <= 1 if lod_count is not None else None
    severity = "unknown" if unknown else "ok"
    if vertices is not None and vertices >= MESH_CRIT_TRIS:
        severity = "critical"
    elif (vertices is not None and vertices >= MESH_WARN_TRIS) or missing is True:
        severity = "warning"
    return {"lod_count": lod_count, "approx_verts": vertices, "missing_lods": missing,
            "severity": severity, "inspection_complete": not unknown,
            "unknown_fields": unknown, "load_failed": False}


def _sound_info(asset: unreal.SoundWave) -> dict:
    """Extract checked duration; unknown duration cannot pass the threshold audit."""
    try:
        duration = _checked_number(asset.get_editor_property("duration"))
    except Exception:
        return {"duration_secs": None, "severity": "unknown",
                "inspection_complete": False, "unknown_fields": ["duration_secs"],
                "load_failed": asset is None}
    severity = ("critical" if duration >= SOUND_CRIT_SECS else
                "warning" if duration >= SOUND_WARN_SECS else "ok")
    return {"duration_secs": round(duration, 1), "severity": severity,
            "inspection_complete": True, "unknown_fields": [], "load_failed": False}


def _severity_icon(s: str) -> str:
    return {"ok": "✓", "warning": "⚠", "critical": "✗"}.get(s, "?")


def _write_report(data: dict) -> str:
    project = Path(native_project_dir()).resolve()
    path = project / "Saved/UEFN_Toolbelt/memory_report.json"
    if not path.resolve().is_relative_to(project):
        raise ValueError("Memory report resolves outside the native project")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = ""
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".memory.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(data, stream, indent=2)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.remove(temporary)
    return str(path)


# ─────────────────────────────────────────────────────────────────────────────
#  Registered Tools
# ─────────────────────────────────────────────────────────────────────────────

@register_tool(
    name="memory_scan",
    category="Optimization",
    description="Full island memory scan — textures, meshes, sounds. Saves JSON report.",
    tags=["memory", "profiler", "scan", "optimize", "performance"],
)
def run_memory_scan(scan_path: str = "", **kwargs) -> dict:
    """
    Scans all asset types and prints a summary dashboard.
    Full results saved to Saved/UEFN_Toolbelt/memory_report.json.

    Args:
        scan_path: Content Browser folder to scan.

    Returns:
        dict: {"status", "path", "summary": {counts, warnings, criticals}}
    """
    scan_path = resolve_scan_path(scan_path)
    log_info(f"Memory scan: {scan_path} …")
    mount = detect_project_mount()
    try:
        inventory = {kind: _list_assets_of_class(scan_path, class_name)
                     for kind, class_name in (("textures", "Texture2D"),
                                              ("meshes", "StaticMesh"), ("sounds", "SoundWave"))}
    except Exception as exc:
        return {"status": "error", "reason": "asset_registry_unavailable", "message": str(exc)}

    report: dict = {
        "timestamp": datetime.now().isoformat(),
        "scan_path": scan_path,
        "project_mount": mount,
        "full_project_scan": scan_path.rstrip("/") == "/" + mount,
        "registry_enumeration_complete": True,
        "textures": [],
        "meshes":   [],
        "sounds":   [],
    }

    # ── Textures ──────────────────────────────────────────────────────────
    tex_assets = inventory["textures"]
    tex_warn = tex_crit = 0
    for path, asset in tex_assets:
        info = _texture_info(asset)
        info["path"] = path
        report["textures"].append(info)
        if info["severity"] == "warning":  tex_warn += 1
        if info["severity"] == "critical": tex_crit += 1

    # ── Meshes ────────────────────────────────────────────────────────────
    mesh_assets = inventory["meshes"]
    mesh_warn = mesh_crit = mesh_no_lod = 0
    for path, asset in mesh_assets:
        info = _mesh_info(asset)
        info["path"] = path
        report["meshes"].append(info)
        if info["severity"] == "warning":  mesh_warn += 1
        if info["severity"] == "critical": mesh_crit += 1
        if info["missing_lods"]:           mesh_no_lod += 1

    # ── Sounds ────────────────────────────────────────────────────────────
    sound_assets = inventory["sounds"]
    snd_warn = snd_crit = 0
    for path, asset in sound_assets:
        info = _sound_info(asset)
        info["path"] = path
        report["sounds"].append(info)
        if info["severity"] == "warning":  snd_warn += 1
        if info["severity"] == "critical": snd_crit += 1

    # ── Summary ───────────────────────────────────────────────────────────
    total_tex_kb = sum(t["estimated_vram_kb"] for t in report["textures"]
                       if t["estimated_vram_kb"] is not None)
    unknowns = {kind: sum(not item["inspection_complete"] for item in report[kind])
                for kind in ("textures", "meshes", "sounds")}
    unknown_total = sum(unknowns.values())
    report["summary"] = {
        "total_textures":      len(tex_assets),
        "texture_warnings":    tex_warn,
        "texture_criticals":   tex_crit,
        "estimated_vram_mb":   round(total_tex_kb / 1024, 1) if not unknowns["textures"] else None,
        "known_vram_mb":       round(total_tex_kb / 1024, 1),
        "estimate_complete":   not unknowns["textures"],
        "unknown_textures":    unknowns["textures"],
        "unknown_meshes":      unknowns["meshes"],
        "unknown_sounds":      unknowns["sounds"],
        "unknown_assets":      unknown_total,
        "total_meshes":        len(mesh_assets),
        "mesh_warnings":       mesh_warn,
        "mesh_criticals":      mesh_crit,
        "meshes_missing_lods": mesh_no_lod,
        "total_sounds":        len(sound_assets),
        "sound_warnings":      snd_warn,
        "sound_criticals":     snd_crit,
    }

    lines = [
        "\n" + "═" * 58,
        "  UEFN TOOLBELT — Memory Report",
        "  " + scan_path,
        "═" * 58,
        "",
        f"  TEXTURES  ({len(tex_assets)} scanned)",
        f"    Known VRAM estimate: {total_tex_kb / 1024:.1f} MB; unknown textures: {unknowns['textures']}",
        f"    ⚠ Warnings:      {tex_warn}  (≥{TEXTURE_WARN_PX}px)",
        f"    ✗ Critical:      {tex_crit}  (≥{TEXTURE_CRIT_PX}px)",
        "",
        f"  MESHES  ({len(mesh_assets)} scanned)",
        f"    ⚠ High poly:     {mesh_warn}  (≥{MESH_WARN_TRIS:,} verts)",
        f"    ✗ Very high:     {mesh_crit}  (≥{MESH_CRIT_TRIS:,} verts)",
        f"    ⚠ Missing LODs:  {mesh_no_lod}",
        "",
        f"  SOUNDS  ({len(sound_assets)} scanned)",
        f"    ⚠ Long files:    {snd_warn}  (≥{SOUND_WARN_SECS:.0f}s)",
        f"    ✗ Very long:     {snd_crit}  (≥{SOUND_CRIT_SECS:.0f}s)",
        "",
        "  RECOMMENDED ACTIONS:",
    ]

    if tex_crit > 0:
        lines.append(f"    → Run memory_scan_textures to find the {tex_crit} critical texture(s)")
    if mesh_no_lod > 0:
        lines.append(f"    → Run memory_autofix_lods to add LODs to {mesh_no_lod} mesh(es)")
    if unknown_total:
        lines.append(f"    → Inspection incomplete for {unknown_total} asset(s); inspect unavailable fields in the editor.")
    elif tex_crit == 0 and mesh_no_lod == 0 and snd_crit == 0:
        lines.append("    → No critical issues in the inspected heuristics; run native memory calculation before publishing.")

    lines += ["", "═" * 58]
    log_info("\n".join(lines))

    try:
        report_path = _write_report(report)
    except Exception as exc:
        return {"status": "error", "reason": "memory_report_unavailable", "message": str(exc),
                "summary": report["summary"]}
    log_info(f"Full report → {report_path}")
    return {"status": "ok", "path": report_path, "summary": report["summary"]}


@register_tool(
    name="memory_scan_textures",
    category="Optimization",
    description="Audit all textures in a folder and flag oversized ones.",
    tags=["memory", "texture", "resolution", "optimize"],
)
def run_memory_scan_textures(
    scan_path: str = "",
    max_size_px: int = 2048,
    **kwargs,
) -> dict:
    """
    Args:
        scan_path:   Content Browser folder to scan.
        max_size_px: Flag textures larger than this (width or height).

    Returns:
        dict: {"status", "count", "offenders": [{"path", "width", "height",
               "max_dim", "estimated_vram_kb", "severity"}]}
    """
    scan_path = resolve_scan_path(scan_path)
    try:
        tex_assets = _list_assets_of_class(scan_path, "Texture2D")
    except Exception as exc:
        return {"status": "error", "reason": "asset_registry_unavailable", "message": str(exc)}
    if not tex_assets:
        log_info("No Texture2D assets found.")
        return {"status": "ok", "count": 0, "offenders": [], "unknown": []}

    raw_offenders = []
    unknown = []
    for path, asset in tex_assets:
        info = _texture_info(asset)
        if not info["inspection_complete"]:
            unknown.append({"path": path, **info})
            continue
        if info["max_dim"] > max_size_px:
            raw_offenders.append((path, info))

    raw_offenders.sort(key=lambda x: x[1]["max_dim"], reverse=True)

    if not raw_offenders:
        log_info(f"No inspected textures exceed {max_size_px}px; {len(unknown)} inspection(s) unavailable.")
        return {"status": "ok", "count": 0, "offenders": [], "unknown": unknown}

    lines = [f"\n⚠ {len(raw_offenders)} textures exceed {max_size_px}px:\n"]
    for path, info in raw_offenders:
        icon = _severity_icon(info["severity"])
        lines.append(
            f"  {icon} {path.split('/')[-1]:40s}  "
            f"{info['width']}×{info['height']}  "
            f"~{info['estimated_vram_kb']:.0f} KB VRAM"
        )
    log_info("\n".join(lines))

    offenders = [{"path": p, **info} for p, info in raw_offenders]
    return {"status": "ok", "count": len(offenders), "offenders": offenders, "unknown": unknown}


@register_tool(
    name="memory_scan_meshes",
    category="Optimization",
    description="Inspect static meshes — approximate vertex counts and LOD availability.",
    tags=["memory", "mesh", "lod", "polygon", "optimize"],
)
def run_memory_scan_meshes(scan_path: str = "", **kwargs) -> dict:
    """
    Args:
        scan_path: Content Browser folder to scan.

    Returns:
        dict: {"status", "count", "offenders": [{"path", "lod_count",
               "approx_verts", "missing_lods", "severity"}]}
    """
    scan_path = resolve_scan_path(scan_path)
    try:
        mesh_assets = _list_assets_of_class(scan_path, "StaticMesh")
    except Exception as exc:
        return {"status": "error", "reason": "asset_registry_unavailable", "message": str(exc)}
    if not mesh_assets:
        log_info("No StaticMesh assets found.")
        return {"status": "ok", "count": 0, "offenders": []}

    raw_offenders = []
    for p, a in mesh_assets:
        info = _mesh_info(a)
        if info["severity"] != "ok" or info["missing_lods"]:
            raw_offenders.append((p, info))
    raw_offenders.sort(key=lambda x: x[1]["approx_verts"] if x[1]["approx_verts"] is not None else -1, reverse=True)

    if not raw_offenders:
        log_info("All meshes look good (reasonable vertex count + LODs present).")
        return {"status": "ok", "count": 0, "offenders": []}

    lines = [f"\n⚠ {len(raw_offenders)} mesh issues:\n"]
    for path, info in raw_offenders:
        icon     = _severity_icon(info["severity"])
        lod_flag = (" [LOD inspection unavailable]" if info["lod_count"] is None else
                    " [NO LODs]" if info["missing_lods"] else f" [{info['lod_count']} LODs]")
        lines.append(
            f"  {icon} {path.split('/')[-1]:40s}  "
            f"vertices={info['approx_verts'] if info['approx_verts'] is not None else 'unknown'}{lod_flag}"
        )
    log_info("\n".join(lines))
    if any(info["missing_lods"] is True for _, info in raw_offenders):
        log_info("Run memory_autofix_lods for meshes with confirmed missing LODs.")

    offenders = [{"path": p, **info} for p, info in raw_offenders]
    return {"status": "ok", "count": len(offenders), "offenders": offenders,
            "unknown_count": sum(not item["inspection_complete"] for item in offenders)}


@register_tool(
    name="memory_top_offenders",
    category="Optimization",
    description="Rank measured textures by RGBA estimate and meshes by vertex count; report unknowns separately.",
    tags=["memory", "profiler", "top", "heaviest", "optimize"],
)
def run_memory_top_offenders(
    scan_path: str = "",
    top_n: int = 10,
    **kwargs,
) -> dict:
    """
    Args:
        scan_path: Content Browser folder to scan.
        top_n:     Number of top offenders to list per category.

    Returns:
        dict: {"status", "textures": [{"path", ...}], "meshes": [{"path", ...}]}
    """
    scan_path = resolve_scan_path(scan_path)
    try:
        tex_assets = _list_assets_of_class(scan_path, "Texture2D")
        mesh_assets = _list_assets_of_class(scan_path, "StaticMesh")
    except Exception as exc:
        return {"status": "error", "reason": "asset_registry_unavailable", "message": str(exc)}
    tex_info = [(p, _texture_info(a)) for p, a in tex_assets]
    tex_sorted = sorted(
        [(path, info) for path, info in tex_info if info["estimated_vram_kb"] is not None],
        key=lambda x: x[1]["estimated_vram_kb"],
        reverse=True,
    )[:top_n]

    lines = [f"\n=== Top {top_n} Heaviest Textures ==="]
    for path, info in tex_sorted:
        lines.append(
            f"  {info['width']}×{info['height']}  "
            f"estimated KB={info['estimated_vram_kb']}  "
            f"{path.split('/')[-1]}"
        )

    mesh_info = [(p, _mesh_info(a)) for p, a in mesh_assets]
    mesh_sorted = sorted(
        [(path, info) for path, info in mesh_info if info["approx_verts"] is not None],
        key=lambda x: x[1]["approx_verts"],
        reverse=True,
    )[:top_n]

    lines += [f"\n=== Top {top_n} Most Complex Meshes ==="]
    for path, info in mesh_sorted:
        lod_flag = ("unknown LODs" if info["lod_count"] is None else
                    "NO LODs" if info["missing_lods"] else f"{info['lod_count']} LODs")
        lines.append(
            f"  vertices={info['approx_verts']}  [{lod_flag}]  "
            f"{path.split('/')[-1]}"
        )

    log_info("\n".join(lines))

    textures = [{"path": p, **info} for p, info in tex_sorted]
    meshes   = [{"path": p, **info} for p, info in mesh_sorted]
    return {"status": "ok", "textures": textures, "meshes": meshes,
            "unknown_textures": [{"path": path, **info} for path, info in tex_info
                                 if not info["inspection_complete"]],
            "unknown_meshes": [{"path": path, **info} for path, info in mesh_info
                               if not info["inspection_complete"]],
            "limitation": "Ranked known estimates only; unavailable measurements cannot be compared."}


@register_tool(
    name="memory_autofix_lods",
    category="Optimization",
    description="Auto-generate LODs on all meshes missing them in a folder.",
    tags=["memory", "lod", "autofix", "optimize", "auto"],
)
def run_memory_autofix_lods(
    scan_path: str = "",
    num_lods: int = 3,
    **kwargs,
) -> dict:
    """
    Convenience wrapper: finds meshes with LOD count ≤ 1 and generates LODs.
    Equivalent to lod_auto_generate_folder with skip_existing=True.

    Args:
        scan_path: Content Browser folder to scan.
        num_lods:  Number of LODs to generate.

    Returns:
        dict: Passes through the structured return from lod_auto_generate_folder.
    """
    scan_path = resolve_scan_path(scan_path)
    import UEFN_Toolbelt as tb
    result = tb.run("lod_auto_generate_folder",
                    folder_path=scan_path,
                    num_lods=num_lods,
                    skip_existing=True)
    return result if isinstance(result, dict) else {"status": "ok"}
