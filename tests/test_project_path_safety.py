"""Unknown project detection must not default reads or writes to Fortnite content."""

import pytest

from UEFN_Toolbelt import core


@pytest.mark.parametrize("mount", ["", "Game", "Engine", "Temp", "FortniteGame"])
def test_unresolved_or_reserved_default_mount_is_refused(monkeypatch, mount):
    monkeypatch.setattr(core, "detect_project_mount", lambda: mount)
    with pytest.raises(ValueError, match="project mount"):
        core.resolve_scan_path("")
    with pytest.raises(ValueError, match="project mount"):
        core.resolve_content_path("/Game/Materials")


def test_uuid_mount_and_explicit_read_path_keep_their_identity(monkeypatch):
    monkeypatch.setattr(core, "detect_project_mount", lambda: "96af6cef-b385-4bf5-a7ec-1ea0c19944c5")
    assert core.resolve_scan_path("") == "/96af6cef-b385-4bf5-a7ec-1ea0c19944c5"
    assert core.resolve_content_path("/Game/Materials") == "/96af6cef-b385-4bf5-a7ec-1ea0c19944c5/Materials"
    assert core.resolve_scan_path("/Explicit/Folder") == "/Explicit/Folder"
