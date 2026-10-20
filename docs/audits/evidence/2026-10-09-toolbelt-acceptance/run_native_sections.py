"""Reviewed local UEFN-console driver; never exposed as a remote command."""
import json
import shutil
import time
from pathlib import Path

import unreal

import UEFN_Toolbelt as tb
from UEFN_Toolbelt.tools import integration_test as suite

OUTPUT = Path("C:/Users/mikea/Documents/MCP/UEFN-TOOLBELT/docs/audits/evidence/2026-10-09-toolbelt-acceptance/native-sections-r2")
assert not OUTPUT.exists(), "Preserve the prior run and choose a fresh output directory."
identity = suite._acceptance_identity()
sections = list(suite._SECTION_NAMES)
assert sections and len(set(sections)) == len(sections)
OUTPUT.mkdir(parents=True)
original_run = tb.run
state = {"identity": identity, "sections": sections, "results": [], "calls": [],
         "completed": False, "current_section": "", "stop_reason": "",
         "in_progress": False, "started_sections": []}
handle = None
busy = False
stopped = False
next_tick = time.monotonic() + 1


def flush():
    temporary = OUTPUT / "run.json.tmp"
    temporary.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    temporary.replace(OUTPUT / "run.json")


def observed_run(tool_name, **kwargs):
    call = {"section": state["current_section"], "tool": tool_name, "kwargs": kwargs}
    try:
        call["result"] = original_run(tool_name, **kwargs)
        return call["result"]
    except Exception as exc:
        call["raised"] = str(exc)
        raise
    finally:
        state["calls"].append(call)
        flush()


def finish(reason=""):
    global handle, stopped
    stopped = True
    state["in_progress"] = False
    tb.run = original_run
    state["stop_reason"] = reason
    state["completed"] = not reason and len(state["results"]) == len(sections)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    flush()
    unreal.log("[ACCEPTANCE] Driver finished: " + (reason or "all sections attempted"))


def tick(_delta):
    global next_tick, busy
    if busy or stopped or time.monotonic() < next_tick:
        return
    busy = True
    try:
        assert suite._acceptance_identity() == identity, "Native project identity changed."
        index = len(state["results"])
        if index == len(sections):
            finish()
            return
        section = sections[index]
        assert section not in state["started_sections"], "Refusing to repeat an already-started section."
        state["current_section"] = section
        state["in_progress"] = True
        state["started_sections"].append(section)
        flush()  # Persist the exact in-flight operation before any event-pumping tool.
        unreal.log(f"[ACCEPTANCE] Section {index + 1}/{len(sections)}: {section}")
        result = original_run("toolbelt_integration_test", sections=[section],
                              allow_mutation=True, preserve_bridge=True)
        state["results"].append({"section": section, "result": result})
        for key, suffix in (("report", ".txt"), ("json_report", ".json")):
            if isinstance(result, dict) and result.get(key):
                shutil.copyfile(result[key], OUTPUT / f"{index + 1:02}_{section}{suffix}")
        state["in_progress"] = False
        flush()
        if not isinstance(result, dict) or result.get("completed") is not True:
            finish("Incomplete section; inspect state before recovery.")
            return
        next_tick = time.monotonic() + 0.25
    except Exception as exc:
        finish(str(exc))
    finally:
        busy = False


tb.run = observed_run
try:
    handle = unreal.register_slate_post_tick_callback(tick)
    flush()
except BaseException:
    stopped = True
    tb.run = original_run
    if handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(handle)
        except Exception:
            pass  # Even if unregister is refused, stopped makes the callback inert.
        else:
            handle = None
    raise
unreal.log("[ACCEPTANCE] Local section driver scheduled in ToolbeltAcceptance.")
