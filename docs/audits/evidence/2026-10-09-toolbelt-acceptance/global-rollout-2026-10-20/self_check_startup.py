import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(r"C:/Users/mikea/Documents/MCP/uefn-toolbelt-startup/codex_toolbelt_startup.py")

@pytest.fixture
def loader(monkeypatch):
    world = SimpleNamespace(path="/Unknown/Map.Map")
    fake = SimpleNamespace(UnrealEditorSubsystem=object(),
        get_editor_subsystem=lambda _: SimpleNamespace(get_editor_world=lambda: SimpleNamespace(get_path_name=lambda:world.path)))
    monkeypatch.setitem(sys.modules, "unreal", fake)
    spec=importlib.util.spec_from_file_location("startup_check", SOURCE)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    monkeypatch.setattr(sys, "path", [])
    return mod, world


def project(tmp_path, name="Unlisted", mount="fresh-mount"):
    root=tmp_path/name
    python=root/"Content/Python"
    (python/"UEFN_Toolbelt").mkdir(parents=True)
    (python/"UEFN_Toolbelt/__init__.py").write_text("# installed fixture")
    (root/(name+".uefnproject")).write_text(json.dumps({"plugins":[{"name":mount,"bIsRoot":True}]}))
    return python


def test_unlisted_project_is_discovered_from_sys_path(loader,tmp_path):
    mod,w=loader; python=project(tmp_path); sys.path.append(str(python)); w.path="/fresh-mount/Map.Map"
    assert mod._select_project([])["python_dir"] == str(python.resolve())


def test_unknown_world_does_not_fall_back_to_installed_path(loader,tmp_path):
    mod,w=loader; sys.path.append(str(project(tmp_path)))
    assert mod._select_project([]) is None


@pytest.mark.parametrize("world",["/Temp/Untitled.Untitled","/Game/Untitled.Untitled"])
def test_untitled_requires_unique_sys_path_candidate(loader,tmp_path,world):
    mod,w=loader; w.path=world; sys.path.append(str(project(tmp_path)))
    assert mod._select_project([])["mount"]=="fresh-mount"
    sys.path.append(str(project(tmp_path,"Other","other-mount")))
    assert mod._select_project([]) is None


def test_duplicate_mount_is_ambiguous_even_when_one_is_only_fallback(loader,tmp_path):
    mod,w=loader; first=project(tmp_path); second=project(tmp_path,"Other")
    sys.path.append(str(first)); w.path="/fresh-mount/Map.Map"
    assert mod._select_project([{"python_dir":str(second)}]) is None


def test_duplicate_paths_are_one_candidate(loader,tmp_path):
    mod,w=loader; python=project(tmp_path); sys.path.extend([str(python),str(python)+"/."]); w.path="/fresh-mount/Map.Map"
    assert len(mod._project_candidates([{"python_dir":str(python)}]))==1
    assert mod._select_project([])


@pytest.mark.parametrize("damage",["missing_package","multiple_descriptors","bad_json","multiple_roots","not_root","bad_mount","reserved_mount"])
def test_untrusted_metadata_refuses(loader,tmp_path,damage):
    mod,w=loader; python=project(tmp_path); descriptor=python.parent.parent/"Unlisted.uefnproject"
    if damage=="missing_package": (python/"UEFN_Toolbelt/__init__.py").unlink()
    if damage=="multiple_descriptors": descriptor.with_name("Other.uefnproject").write_text("{}")
    if damage=="bad_json": descriptor.write_text("{")
    if damage=="multiple_roots": descriptor.write_text(json.dumps({"plugins":[{"name":"A","bIsRoot":True},{"name":"B","bIsRoot":True}]}))
    if damage=="not_root": descriptor.write_text(json.dumps({"plugins":[{"name":"A","bIsRoot":1}]}))
    if damage=="bad_mount": descriptor.write_text(json.dumps({"plugins":[{"name":"../A","bIsRoot":True}]}))
    if damage=="reserved_mount": descriptor.write_text(json.dumps({"plugins":[{"name":"Temp","bIsRoot":True}]}))
    assert mod._installed_project(python) is None


def test_optional_fallback_still_requires_metadata_and_world(loader,tmp_path):
    mod,w=loader; python=project(tmp_path); w.path="/fresh-mount/Map.Map"
    assert mod._select_project([{"python_dir":str(python)}])
    assert mod._installed_project(tmp_path) is None


@pytest.mark.parametrize("contents",[None,"not-json","{}"])
def test_missing_or_invalid_registry_does_not_block_schedule(loader,tmp_path,contents):
    mod,w=loader; mod.__file__=str(tmp_path/"startup.py")
    if contents is not None: (tmp_path/"projects.json").write_text(contents)
    callbacks=[]; mod.unreal.register_slate_post_tick_callback=lambda cb:callbacks.append(cb) or 1
    mod.unreal.log=lambda *_:None
    mod.schedule()
    assert len(callbacks)==1 and mod._handle==1


def test_eight_actual_project_metadata(loader):
    mod,w=loader
    entries=json.loads(SOURCE.with_name("projects.json").read_text())
    entries.append({"python_dir":r"C:/Users/mikea/Documents/Codex/2026-09-30/i/outputs/MyProject/Content/Python","mount":"0e39e566-c18d-4ec7-83f3-a3b8f883511e"})
    for entry in entries:
        found=mod._installed_project(entry["python_dir"])
        assert found is not None, entry["python_dir"]
        assert found["mount"]==entry["mount"]
        sys.path[:]=[entry["python_dir"]]; w.path="/"+entry["mount"]+"/Map.Map"
        assert mod._select_project([])==found


def test_tick_discovers_project_path_added_after_schedule(loader,tmp_path):
    mod,w=loader; callbacks=[]; calls=[]
    mod.__file__=str(tmp_path/"startup.py")
    mod.unreal.register_slate_post_tick_callback=lambda cb:callbacks.append(cb) or 1
    mod.unreal.unregister_slate_post_tick_callback=lambda handle:calls.append(("stop",handle))
    mod.unreal.log=lambda *_:None
    mod.unreal.log_warning=lambda *_:None
    mod.unreal.log_error=lambda *_:None
    clock=[0.0]; mod.time=SimpleNamespace(monotonic=lambda:clock[0])
    mod.schedule()
    python=project(tmp_path); sys.path.append(str(python)); w.path="/fresh-mount/Map.Map"
    package=SimpleNamespace(__file__=str(python/"UEFN_Toolbelt/__init__.py"),
        register=lambda:calls.append(("register",)),
        run=lambda tool:calls.append((tool,)) or {"status":"ok"})
    sys.modules["UEFN_Toolbelt"]=package
    try:
        clock[0]=6.0; callbacks[0](0.1)
        assert calls==[("stop",1),("register",),("mcp_start",),("launch_qt",)]
        assert mod._finished is True and mod._handle is None
    finally:
        sys.modules.pop("UEFN_Toolbelt",None)
