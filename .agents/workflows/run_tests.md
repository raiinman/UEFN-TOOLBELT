---
description: How to run UEFN Toolbelt smoke and integration tests
---

Follow these steps to verify selected Toolbelt behavior in native UEFN. Record the tested scope and actual outcomes.

## 1. Deploy Changes
Ensure your latest code is synced to the UEFN project's `Content/Python` directory.
```powershell
.\deploy.bat
```

## 2. Open UEFN Python Console
1. Open your UEFN project.
2. In the menu bar, go to **Window -> Output Log**.
3. At the bottom of the Output Log, change the command type from "Cmd" to **Python**.

## 3. Run the "Guarded Reload"
For changes to existing pure tool modules, this command closes live windows
before reloading and rebuilding the registry:
```python
import UEFN_Toolbelt as tb; tb.hard_reload()
```

If the change added a new module to `tools/__init__.py`, or touched a PySide6
window with persistent callbacks, do a full UEFN restart instead. Guarded reload
is unsafe for those cases; see Quirks #26 and #38.

## 4. Execute the Smoke Test (Layer 1-6)
Checks module loading and tool registration: the package and every expected
module load, the registry holds at least a minimum count, and six named tools
are registered. It executes no tool and validates no schema.
```python
import UEFN_Toolbelt as tb; tb.run("toolbelt_smoke_test")
```

## 5. Execute the Integration Test (Layer 7)
**[WARNING: INVASIVE]** Spawns and deletes actors in the live viewport. Requires the dedicated ToolbeltAcceptance project. It also changes assets, files and persistent settings.
```python
import UEFN_Toolbelt as tb; tb.run("toolbelt_integration_test", allow_mutation=True, preserve_bridge=True)
```
Read the returned checks and capture both `.json` and `.txt` report files after
each run. Preserve failed/incomplete runs. Outcomes, execution-only checks,
refusals and unavailable capabilities stay separate. Use small sections and
independent readback; the harness does not cover every registered tool. Preserve
and restore shared Saved reports/templates/snippets around the disposable run.

## 6. If remote validation is next

Run every Python-based audit before staging. Then use:

```text
publish_audit while Python is loaded
prepare_launch.bat
Launch Session / Push Changes / publish; wait for the remote result
restore_after_launch.bat
```

Do not restart or hot-reload Toolbelt while the Python stash is active.
