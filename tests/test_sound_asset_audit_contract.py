"""Unavailable sound inspection must never be reported as a clean asset."""

from types import SimpleNamespace

import pytest

from UEFN_Toolbelt.tools import sound_asset_tools as sound


@pytest.fixture
def audit_sound(monkeypatch):
    class SoundWave:
        def get_editor_property(self, name):
            return object()

    monkeypatch.setattr(sound.unreal, "SoundWave", SoundWave)
    monkeypatch.setattr(sound, "resolve_scan_path", lambda _: "/Island")

    def run(duration="10", loaded=None, property_error=False, load_error=False, tag_error=False,
            no_class=False, wrong_class=False):
        def tag(name):
            if tag_error:
                raise RuntimeError("metadata unavailable")
            return duration

        class InspectedWave(SoundWave):
            def get_editor_property(self, name):
                if property_error:
                    raise RuntimeError("property unavailable")
                return None if no_class else object()

        def load(path):
            if load_error:
                raise RuntimeError("load failed")
            if wrong_class:
                return object()
            return InspectedWave() if loaded is not False else None

        metadata = SimpleNamespace(asset_name="Example", package_name="/Island/Example", get_tag_value=tag)
        monkeypatch.setattr(sound, "_ar", lambda: SimpleNamespace(get_assets=lambda _: [metadata]))
        monkeypatch.setattr(sound.unreal.EditorAssetLibrary, "load_asset", load)
        return sound.run_sound_asset_audit()

    return run


@pytest.mark.parametrize("duration", [None, "", "unparseable", "nan", "inf", "-1"])
def test_unavailable_or_invalid_duration_is_unknown(audit_sound, duration):
    result = audit_sound(duration=duration)
    assert result["clean"] == 0
    assert result["issues"] == result["unknown"] == 1
    assert "Duration unavailable" in result["issue_list"][0]["issues"][0]


@pytest.mark.parametrize("failure", ["property_error", "load_error", "tag_error", "wrong_class"])
def test_failed_inspection_cannot_pass_clean(audit_sound, failure):
    result = audit_sound(**{failure: True})
    assert result["clean"] == 0
    assert result["issues"] == result["unknown"] == 1


def test_missing_loaded_asset_is_unknown(audit_sound):
    result = audit_sound(loaded=False)
    assert result["clean"] == 0
    assert result["unknown"] == 1


def test_known_missing_sound_class_is_an_issue(audit_sound):
    result = audit_sound(no_class=True)
    assert result["clean"] == 0
    assert result["issues"] == 1
    assert result["unknown"] == 0
    assert result["issue_list"][0]["issues"] == ["No SoundClass assigned"]


def test_positive_duration_and_class_reads_are_clean(audit_sound):
    result = audit_sound()
    assert result["clean"] == 1
    assert result["issues"] == result["unknown"] == 0
