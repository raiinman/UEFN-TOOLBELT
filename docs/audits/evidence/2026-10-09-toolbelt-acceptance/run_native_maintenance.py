"""Reviewed LOCAL-console acceptance after cold restart; no callbacks or retries.

Audits and backups do not publish anything. Only the three named integration
sections mutate the descriptor/world-confirmed disposable acceptance project.
Completion records attempts; it never establishes acceptance of all 362 tools.
"""
import hashlib
import json
import math
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import unreal

import UEFN_Toolbelt as tb
from UEFN_Toolbelt import core
from UEFN_Toolbelt.tools import (
    actor_visibility,
    memory_profiler,
    project_admin,
    publish_audit,
    sound_asset_tools,
    texture_tools,
)
from UEFN_Toolbelt.tools import integration_test as suite

SCRIPT_PATH = Path("C:/Users/mikea/Documents/MCP/UEFN-TOOLBELT/docs/audits/evidence/2026-10-09-toolbelt-acceptance/run_native_maintenance.py")
OUTPUT = SCRIPT_PATH.parent / "native-maintenance-r1"
PRIOR = SCRIPT_PATH.parent / "native-assets-r1/run.json"
SECTIONS = ("visibility_tools", "lighting_extended", "bulk_ops")


def main():
    if OUTPUT.exists():
        raise ValueError("Preserve prior evidence and choose a fresh output directory.")
    identity = suite._acceptance_identity()
    project = Path(core.native_project_dir()).resolve()
    if Path(identity["project_dir"]).resolve() != project or getattr(suite, "_integration_running", False):
        raise ValueError("Disposable project identity mismatch or another integration run is active.")
    prior_bytes = PRIOR.read_bytes()
    prior = json.loads(prior_bytes)
    if prior["identity"] != identity:
        raise ValueError("Cold-restart fixture provenance belongs to another project/world.")
    mount = "/" + identity["mount"]
    fixtures = mount + "/AcceptanceFixtures"
    texture_path = fixtures + "/Textures/T_Acceptance"
    sound_path = fixtures + "/Audio/SW_Acceptance"
    expected_memory_file = project / "Saved/UEFN_Toolbelt/memory_report.json"
    if not expected_memory_file.resolve().is_relative_to(project):
        raise ValueError("Native memory report path resolves outside its project.")
    state = {"schema_version": 1, "identity": identity,
             "started_at_utc": datetime.now(UTC).isoformat(),
             "script_sha256": hashlib.sha256(SCRIPT_PATH.read_bytes()).hexdigest(),
             "prior_asset_run_sha256": hashlib.sha256(prior_bytes).hexdigest(),
             "runtime_sources": {}, "calls": [], "active_calls": [], "checks": [],
             "observations": [], "completed": False, "fatal": "",
             "limitation": "Exact scoped reads/calls only. Backups contain native assets and Verse, not all project files. Integration sections mutate disposable state. Completion does not mean every check passed or all registered tools were accepted."}
    OUTPUT.mkdir(parents=True)
    shutil.copyfile(SCRIPT_PATH, OUTPUT / "driver.py")
    original_run = tb.run
    call_sequence = 0

    def flush():
        temporary = OUTPUT / "run.json.tmp"
        temporary.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        temporary.replace(OUTPUT / "run.json")

    def guard():
        if (suite._acceptance_identity() != identity
                or Path(core.native_project_dir()).resolve() != project):
            raise ValueError("Native project identity changed; stop without retry.")

    def observed_run(tool_name, **kwargs):
        nonlocal call_sequence
        guard()
        call_sequence += 1
        entry = {"sequence": call_sequence, "depth": len(state["active_calls"]),
                 "tool": tool_name, "kwargs": kwargs}
        state["active_calls"].append(entry)
        try:
            flush()
            entry["result"] = original_run(tool_name, **kwargs)
            return entry["result"]
        except Exception as exc:
            entry["raised"] = str(exc)
            raise
        finally:
            state["active_calls"].pop()
            state["calls"].append(entry)
            flush()

    def check(name, passed, detail):
        state["checks"].append({"name": name, "passed": passed is True, "detail": detail})
        flush()

    def saved_fixture(kind, asset_path, relative_file, cls):
        guard()
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        expected_object = asset_path + "." + asset_path.rsplit("/", 1)[-1]
        if not isinstance(asset, cls) or asset.get_path_name() != expected_object:
            raise ValueError("Named " + kind + " fixture is not the exact expected native class/object.")
        file = project / relative_file
        if not file.resolve().is_relative_to(project) or not file.is_file():
            raise ValueError("Named fixture has no contained saved native .uasset.")
        return asset, file

    def memory_snapshot(label, result):
        guard()
        if not isinstance(result, dict) or result.get("status") != "ok":
            raise ValueError("Memory scan did not produce a completed report.")
        if Path(result.get("path", "")).resolve() != expected_memory_file.resolve():
            raise ValueError("Memory scan report path is outside the expected project-local report.")
        raw = expected_memory_file.read_bytes()
        report = json.loads(raw)
        (OUTPUT / (label + "-memory.json")).write_bytes(raw)
        state["observations"].append({"name": label + " memory report", "path": str(expected_memory_file),
                                       "sha256": hashlib.sha256(raw).hexdigest(), "report": report})
        flush()
        return report

    def memory_check(label, report, audit, full_scope):
        guard()
        audit_checks = audit.get("checks") if isinstance(audit, dict) else None
        memory = audit_checks.get("memory") if isinstance(audit_checks, dict) else None
        memory_present = isinstance(memory, dict) and "pass" in memory
        if not isinstance(memory, dict):
            memory = {}
        unknown = report.get("summary", {}).get("unknown_assets")
        flags_match = (report.get("project_mount") == identity["mount"]
                       and report.get("full_project_scan") is full_scope
                       and report.get("registry_enumeration_complete") is True
                       and report.get("scan_path", "").rstrip("/") == (mount if full_scope else fixtures))
        check(label + " memory scope identity", flags_match,
              {key: report.get(key) for key in ("project_mount", "scan_path", "full_project_scan", "registry_enumeration_complete")})
        if not full_scope or (isinstance(unknown, int) and not isinstance(unknown, bool) and unknown > 0):
            check(label + " publish memory is unknown", memory_present and memory["pass"] is None,
                  {"memory": memory, "memory_check_present": memory_present, "unknown_assets": unknown})
        else:
            summary = report.get("summary", {})
            estimate = summary.get("estimated_vram_mb")
            complete = (summary.get("estimate_complete") is True and all(
                type(summary.get(key)) is int and summary[key] == 0
                for key in ("unknown_assets", "unknown_textures", "unknown_meshes", "unknown_sounds")))
            numeric = type(estimate) in (int, float) and math.isfinite(estimate) and estimate >= 0
            expected_pass = estimate < 512 if numeric and complete and flags_match else None
            check(label + " publish memory agrees with independent report", memory_present and memory["pass"] is expected_pass,
                  {"estimate": estimate, "complete": complete, "expected_pass": expected_pass,
                   "memory_check_present": memory_present, "memory": memory})

    try:
        guard()
        for module in (tb, core, suite, actor_visibility, memory_profiler, project_admin,
                       publish_audit, sound_asset_tools, texture_tools):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(project):
                raise ValueError("Runtime module is not deployed in the confirmed native project.")
            state["runtime_sources"][module.__name__] = {
                "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        state["declared_tools"] = tb.__tool_count__
        state["registered_tools"] = len(tb.registry.list_tools())
        check("Registry inventory count", state["declared_tools"] == state["registered_tools"] == 362,
              {"declared": state["declared_tools"], "registered": state["registered_tools"]})
        texture, texture_file = saved_fixture("PNG", texture_path,
                                             "Content/AcceptanceFixtures/Textures/T_Acceptance.uasset", unreal.Texture2D)
        properties = {}
        for name in ("srgb", "compression_settings", "lod_group", "mip_gen_settings"):
            guard()
            value = texture.get_editor_property(name)
            properties[name] = value if isinstance(value, bool) else str(value)
        expected = prior["native_readbacks"][-1]
        expected_targets = {
            "srgb": False,
            "compression_settings": str(unreal.TextureCompressionSettings.TC_GRAYSCALE),
            "lod_group": str(unreal.TextureGroup.TEXTUREGROUP_WORLD),
            "mip_gen_settings": str(unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP),
        }
        check("Cold-restart PNG properties persist", expected["object_path"] == texture.get_path_name()
              and properties == expected["properties"] == expected_targets,
              {"observed": properties, "expected_r1_final": expected["properties"],
               "expected_named_members": expected_targets})
        guard()
        width, height = texture.blueprint_get_size_x(), texture.blueprint_get_size_y()
        check("Cold-restart PNG dimensions", type(width) is int and type(height) is int and width == height == 32,
              {"width": width, "height": height, "expected": [32, 32]})
        sound, sound_file = saved_fixture("WAV", sound_path,
                                         "Content/AcceptanceFixtures/Audio/SW_Acceptance.uasset", unreal.SoundWave)
        guard()
        duration = sound.get_editor_property("duration")
        check("Read-only SoundWave duration", type(duration) in (int, float)
              and math.isfinite(duration) and abs(duration - 0.1) < 0.01,
              {"duration": duration, "expected_seconds": 0.1, "mutation_performed": False})
        tb.run = observed_run
        partial = memory_snapshot("partial", tb.run("memory_scan", scan_path=fixtures))
        texture_rows = [row for row in partial.get("textures", [])
                        if row.get("path") in (texture_path, texture_path + ".T_Acceptance")]
        check("Memory scan observes known PNG dimensions", len(texture_rows) == 1
              and texture_rows[0].get("width") == texture_rows[0].get("height") == 32
              and texture_rows[0].get("inspection_complete") is True,
              {"texture_rows": texture_rows})
        memory_check("Partial", partial, tb.run("publish_audit"), False)
        full = memory_snapshot("full", tb.run("memory_scan", scan_path=mount))
        memory_check("Full", full, tb.run("publish_audit"), True)
        backup_paths = []
        for index in range(2):
            result = tb.run("system_backup_project")
            guard()
            if not isinstance(result, dict) or result.get("status") != "ok":
                raise ValueError("Native backup failed; stop without automatic retry.")
            archive_path = Path(result.get("path", "")).resolve()
            expected_root = (project / "Saved/UEFN_Toolbelt/backups").resolve()
            if (not expected_root.is_relative_to(project) or archive_path.parent != expected_root
                    or not archive_path.is_file() or archive_path in backup_paths):
                raise ValueError("Backup path is not unique, saved, and native-project-local.")
            backup_paths.append(archive_path)
            matches = {}
            with zipfile.ZipFile(archive_path) as archive:
                for file in (texture_file, sound_file):
                    guard()
                    member = file.relative_to(project).as_posix()
                    actual = file.read_bytes()
                    zipped = archive.read(member)
                    matches[member] = {"matched": actual == zipped,
                                       "actual_sha256": hashlib.sha256(actual).hexdigest(),
                                       "archive_sha256": hashlib.sha256(zipped).hexdigest()}
            check("Native backup fixture bytes " + str(index + 1), all(item["matched"] for item in matches.values()),
                  {"path": str(archive_path), "entries": matches, "scope": "Saved PNG/WAV .uasset representations only; not all project-file coverage."})
        check("Repeated native backups preserve distinct archives", len(set(backup_paths)) == 2,
              {"paths": list(map(str, backup_paths))})
        for index, section in enumerate(SECTIONS, 1):
            result = tb.run("toolbelt_integration_test", sections=[section], allow_mutation=True, preserve_bridge=True)
            guard()
            for key, suffix in (("report", ".txt"), ("json_report", ".json")):
                if isinstance(result, dict) and result.get(key):
                    shutil.copyfile(result[key], OUTPUT / f"{index:02}_{section}{suffix}")
            if not isinstance(result, dict) or result.get("completed") is not True:
                raise ValueError("Incomplete integration section; stop and inspect before recovery.")
            check("Integration section recorded " + section, result.get("status") == "ok",
                  {"passed": result.get("passed"), "failed": result.get("failed"),
                   "total": result.get("total"), "scope": "Recorded checks only; unsupported outcomes remain failures."})
        state["completed"] = True
        state["finished_at_utc"] = datetime.now(UTC).isoformat()
    except Exception as exc:
        state["fatal"] = str(exc)
    finally:
        tb.run = original_run
        flush()
    unreal.log("[ACCEPTANCE] Maintenance evidence written; completed=" + str(state["completed"]))
    return state


if __name__ == "__main__":
    main()
