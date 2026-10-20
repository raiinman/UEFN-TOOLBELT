"""
UEFN TOOLBELT — Texture Editing Tools
=======================================
Tools for reading and writing texture settings on Texture2D assets.

Complements memory_scan_textures (which REPORTS oversized textures) by
providing tools that actually FIX them — setting compression, mip generation,
texture groups, and sRGB flags in bulk.

What Python CAN do:
  • Read compression settings, texture group, sRGB, mip gen settings
  • Set TextureCompressionSettings on selected or folder textures
  • Set TextureGroup on a batch of textures
  • Toggle sRGB on a batch of textures
  • Apply sensible presets (game / ui / normal / hdr)

What Python CANNOT do:
  • Re-compress source art (read-only source data)
  • Create Texture2D assets from raw pixel data via Python
  • Modify virtual texture settings (VT streaming is editor-only UI)

API: EditorAssetLibrary, AssetRegistry, Texture2D editor properties
"""

from __future__ import annotations

import unreal

from ..core import (
    log_error,
    log_info,
    log_warning,
    resolve_scan_path,
    save_loaded_asset,
    undo_transaction,
)
from ..registry import register_tool


def _ar():
    return unreal.AssetRegistryHelpers.get_asset_registry()


def _load_textures_in_folder(scan_path: str) -> list:
    """Return all Texture2D assets under scan_path."""
    filt = unreal.ARFilter(
        class_names=["Texture2D"],
        package_paths=[scan_path],
        recursive_paths=True,
    )
    return _ar().get_assets(filt)


# ── Compression setting name → enum mapping ──────────────────────────────────

_COMPRESSION_MAP = {
    "TC_DEFAULT":          "TC_DEFAULT",
    "TC_EDITOR_ICON":      "TC_EDITOR_ICON",
    "TC_NORMALMAP":        "TC_NORMALMAP",
    "TC_MASKS":            "TC_MASKS",
    "TC_GRAYSCALE":        "TC_GRAYSCALE",
    "TC_ALPHA":            "TC_ALPHA",
    "TC_HDR":              "TC_HDR",
    "TC_BC7":              "TC_BC7",
    "TC_USERINTERFACE2D":  "TC_EDITOR_ICON",
    "TC_UI":               "TC_EDITOR_ICON",
}

_TEXTURE_GROUP_MAP = {
    "world":            "TEXTUREGROUP_WORLD",
    "world_normalmap":  "TEXTUREGROUP_WORLD_NORMAL_MAP",
    "character":        "TEXTUREGROUP_CHARACTER",
    "ui":               "TEXTUREGROUP_UI",
    "lightmap":         "TEXTUREGROUP_LIGHTMAP",
    "effects":          "TEXTUREGROUP_EFFECTS",
    "skybox":           "TEXTUREGROUP_SKYBOX",
    "vehicle":          "TEXTUREGROUP_VEHICLE",
    "weapon":           "TEXTUREGROUP_WEAPON",
    "cinematic":        "TEXTUREGROUP_CINEMATIC",
}

# Presets: (compression, texture_group, srgb, mip_gen)
_PRESETS = {
    "game":     ("TC_DEFAULT",          "world",      True,  "TMGS_FROM_TEXTURE_GROUP"),
    "ui":       ("TC_EDITOR_ICON",  "ui",         True,  "TMGS_NO_MIPMAPS"),
    "normal":   ("TC_NORMALMAP",        "world_normalmap", False, "TMGS_FROM_TEXTURE_GROUP"),
    "mask":     ("TC_MASKS",            "world",      False, "TMGS_FROM_TEXTURE_GROUP"),
    "hdr":      ("TC_HDR",              "world",      False, "TMGS_FROM_TEXTURE_GROUP"),
    "icon":     ("TC_EDITOR_ICON",  "ui",         True,  "TMGS_NO_MIPMAPS"),
    "grayscale":("TC_GRAYSCALE",        "world",      False, "TMGS_FROM_TEXTURE_GROUP"),
}


def _enum_value(enum_name: str, member: str):
    enum_type = getattr(unreal, enum_name, None)
    value = getattr(enum_type, member, None)
    if value is None:
        raise ValueError(f"This build does not expose {enum_name}.{member}")
    return value


_MONITORED_TEXTURE_PROPERTIES = ("srgb", "compression_settings", "lod_group", "mip_gen_settings")


def _serialize_texture_values(values: dict) -> dict:
    return {key: value if isinstance(value, bool) else str(value) for key, value in values.items()}


def _observe_texture_properties(tex, name: str, stage: str, unknown_reads: list) -> dict:
    values = {}
    for prop in _MONITORED_TEXTURE_PROPERTIES:
        try:
            values[prop] = tex.get_editor_property(prop)
        except Exception as exc:
            unknown_reads.append({"name": name, "stage": stage, "property": prop, "error": str(exc)})
    return values


def _verify_requested_texture_properties(tex, settings: dict, stage: str) -> None:
    for prop, value in settings.items():
        if tex.get_editor_property(prop) != value:
            raise ValueError(f"Property readback refused requested {prop} {stage}")


def _apply_texture_settings(assets, settings: dict, dry_run: bool) -> dict:
    changes, skipped, errors, implicit_changes, unknown_reads, observations = [], [], [], [], [], []
    for asset in assets:
        name = str(asset.asset_name)
        tex = None
        before_observed = {}
        try:
            tex = unreal.EditorAssetLibrary.load_asset(f"{asset.package_name}.{asset.asset_name}")
            if not isinstance(tex, unreal.Texture2D):
                tex = None
                raise ValueError("Asset could not be loaded as Texture2D")
            before_observed = _observe_texture_properties(tex, name, "before", unknown_reads)
            missing_requested = [prop for prop in settings if prop not in before_observed]
            if missing_requested:
                raise ValueError(f"Requested properties unavailable: {missing_requested}")
            before = {prop: before_observed[prop] for prop in settings}
            if all(before[prop] == value for prop, value in settings.items()):
                skipped.append(name)
                continue
            if not dry_run:
                with undo_transaction("Toolbelt: texture settings"):
                    for prop, value in settings.items():
                        tex.set_editor_property(prop, value)
                    _verify_requested_texture_properties(tex, settings, "after setting")
                    if not save_loaded_asset(tex, name):
                        raise ValueError("Saving texture failed; in-memory properties may have changed")
                    _verify_requested_texture_properties(tex, settings, "after saving")
            from_values = _serialize_texture_values(before)
            to_values = _serialize_texture_values(settings)
            changes.append({"name": name,
                            "from": next(iter(from_values.values())) if len(settings) == 1 else from_values,
                            "to": next(iter(to_values.values())) if len(settings) == 1 else to_values})
        except Exception as exc:
            errors.append({"name": name, "error": str(exc), "may_have_changed": not dry_run})
            log_warning(f"[texture settings] {name}: {exc}")
        finally:
            if tex is not None:
                after = _observe_texture_properties(tex, name, "after_attempt", unknown_reads)
                observations.append({"name": name, "before": _serialize_texture_values(before_observed),
                                     "after": _serialize_texture_values(after)})
                for prop in _MONITORED_TEXTURE_PROPERTIES:
                    if prop not in settings and prop in before_observed and prop in after and before_observed[prop] != after[prop]:
                        implicit_changes.append({"name": name, "property": prop,
                                                 "from": _serialize_texture_values({prop: before_observed[prop]})[prop],
                                                 "to": _serialize_texture_values({prop: after[prop]})[prop]})
    return {"status": "error" if errors else "ok", "dry_run": dry_run,
            "changed": len(changes), "skipped": len(skipped), "changes": changes, "errors": errors,
            "implicit_changes": implicit_changes, "unknown_reads": unknown_reads,
            "property_observations": observations}


# ── Tools ──────────────────────────────────────────────────────────────────────

@register_tool(
    name="texture_audit",
    category="Textures",
    description=(
        "Audit all Texture2D assets in a folder — lists compression setting, "
        "texture group, sRGB flag, and mip gen mode for each texture. "
        "Use this to find misconfigured textures before optimizing."
    ),
    tags=["texture", "audit", "compression", "settings", "scan"],
    example='tb.run("texture_audit", scan_path="")',
)
def run_texture_audit(scan_path: str = "", max_results: int = 200, **kwargs) -> dict:
    # Uses AR tag data only — never calls load_asset(), safe on pak-heavy projects.
    scan_path = resolve_scan_path(scan_path)
    try:
        assets = _load_textures_in_folder(scan_path)[:max_results]
        results = []
        for a in assets:
            entry = {
                "name": str(a.asset_name),
                "path": str(a.package_name),
                "compression": str(a.get_tag_value("CompressionSettings") or "unknown"),
                "texture_group": str(a.get_tag_value("LODGroup") or "unknown"),
                "srgb": a.get_tag_value("SRGB"),
                "size_x": a.get_tag_value("SizeX"),
                "size_y": a.get_tag_value("SizeY"),
            }
            results.append(entry)

        log_info(f"[texture_audit] {len(results)} textures audited in {scan_path}")
        return {"status": "ok", "count": len(results), "textures": results}
    except Exception as e:
        log_error(f"[texture_audit] {e}")
        return {"status": "error", "message": str(e)}


@register_tool(
    name="texture_set_compression",
    category="Textures",
    description=(
        "Batch-set TextureCompressionSettings on textures in a folder. "
        "Valid compression values: TC_DEFAULT, TC_NORMALMAP, TC_MASKS, TC_GRAYSCALE, "
        "TC_ALPHA, TC_HDR, TC_BC7, TC_UI (alias for TC_EDITOR_ICON). "
        "Always dry_run=True first to preview which textures will change."
    ),
    tags=["texture", "compression", "batch", "set"],
    example='tb.run("texture_set_compression", scan_path="", compression="TC_NORMALMAP", dry_run=False)',
)
def run_texture_set_compression(
    scan_path: str = "",
    compression: str = "TC_DEFAULT",
    dry_run: bool = True,
    max_assets: int = 500,
    **kwargs,
) -> dict:
    try:
        key = compression.upper()
        if key not in _COMPRESSION_MAP:
            raise ValueError(f"Unknown compression '{compression}'. Valid: {list(_COMPRESSION_MAP)}")
        member = _COMPRESSION_MAP[key]
        value = _enum_value("TextureCompressionSettings", member)
        assets = _load_textures_in_folder(resolve_scan_path(scan_path))[:max_assets]
        result = _apply_texture_settings(assets, {"compression_settings": value}, dry_run)
        result["compression"] = member
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc), "changed": 0, "errors": [{"error": str(exc)}]}


@register_tool(
    name="texture_set_group",
    category="Textures",
    description=(
        "Batch-set the TextureGroup (LOD group) on textures in a folder. "
        "Valid groups: world, world_normalmap, character, ui, lightmap, effects, skybox, weapon, vehicle, cinematic. "
        "TextureGroup controls mip streaming budget and quality tier."
    ),
    tags=["texture", "group", "lod", "batch", "set"],
    example='tb.run("texture_set_group", scan_path="", group="ui", dry_run=False)',
)
def run_texture_set_group(
    scan_path: str = "",
    group: str = "world",
    dry_run: bool = True,
    **kwargs,
) -> dict:
    try:
        key = group.lower()
        if key not in _TEXTURE_GROUP_MAP:
            raise ValueError(f"Unknown group '{group}'. Valid: {list(_TEXTURE_GROUP_MAP)}")
        member = _TEXTURE_GROUP_MAP[key]
        value = _enum_value("TextureGroup", member)
        assets = _load_textures_in_folder(resolve_scan_path(scan_path))
        result = _apply_texture_settings(assets, {"lod_group": value}, dry_run)
        result["group"] = member
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc), "changed": 0, "errors": [{"error": str(exc)}]}


@register_tool(
    name="texture_set_srgb",
    category="Textures",
    description=(
        "Batch-set the sRGB flag on textures in a folder. "
        "sRGB=True for albedo/diffuse color textures. "
        "sRGB=False for normal maps, masks, roughness, metalness, and data textures. "
        "Incorrect sRGB settings cause color-space errors in materials."
    ),
    tags=["texture", "srgb", "color", "batch", "set"],
    example='tb.run("texture_set_srgb", scan_path="", srgb=False, dry_run=False)',
)
def run_texture_set_srgb(
    scan_path: str = "",
    srgb: bool = True,
    dry_run: bool = True,
    **kwargs,
) -> dict:
    try:
        assets = _load_textures_in_folder(resolve_scan_path(scan_path))
        result = _apply_texture_settings(assets, {"srgb": srgb}, dry_run)
        result["srgb"] = srgb
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc), "changed": 0, "errors": [{"error": str(exc)}]}


@register_tool(
    name="texture_apply_preset",
    category="Textures",
    description=(
        "Apply a named texture preset to all Texture2D assets in a folder. "
        "Presets set compression + texture group + sRGB + mip gen in one call. "
        "Presets: game, ui, normal, mask, hdr, icon, grayscale. "
        "Always dry_run=True first — this changes multiple settings at once."
    ),
    tags=["texture", "preset", "batch", "compression", "fix"],
    example='tb.run("texture_apply_preset", scan_path="", preset="ui", dry_run=False)',
)
def run_texture_apply_preset(
    scan_path: str = "",
    preset: str = "game",
    dry_run: bool = True,
    **kwargs,
) -> dict:
    try:
        key = preset.lower()
        if key not in _PRESETS:
            raise ValueError(f"Unknown preset '{preset}'. Valid: {list(_PRESETS)}")
        comp, group, srgb, mip = _PRESETS[key]
        # Resolve the entire preset before loading or changing any texture.
        settings = {
            "compression_settings": _enum_value("TextureCompressionSettings", comp),
            "lod_group": _enum_value("TextureGroup", _TEXTURE_GROUP_MAP[group]),
            "srgb": srgb,
            "mip_gen_settings": _enum_value("TextureMipGenSettings", mip),
        }
        assets = _load_textures_in_folder(resolve_scan_path(scan_path))
        result = _apply_texture_settings(assets, settings, dry_run)
        result.update(preset=preset, settings={"compression": comp, "group": group, "srgb": srgb, "mip_gen": mip})
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc), "changed": 0, "errors": [{"error": str(exc)}]}
