@echo off
setlocal DisableDelayedExpansion
:: Usage: deploy.bat "C:\path\to\project" /nopause
:: /nopause also leaves optional dependency installation to the operator.
set "NO_PAUSE="
if /I "%~2"=="/nopause" set "NO_PAUSE=1"
if not "%~1"=="" (
    set "DEST=%~f1"
    set "PROJECT=%~nx1"
    goto :validate_project
)
setlocal enabledelayedexpansion

echo.
echo  ==========================================
echo    UEFN TOOLBELT  ^|  Deploy Script
echo  ==========================================
echo.

:: Find Fortnite Projects folder
set "FP_ROOT=%USERPROFILE%\Documents\Fortnite Projects"
if not exist "%FP_ROOT%\" (
    echo  ERROR: Could not find your Fortnite Projects folder at:
    echo    %FP_ROOT%
    echo.
    echo  Make sure UEFN is installed and you have created at least one project.
    if not defined NO_PAUSE pause
    exit /b 1
)

:: List available UEFN projects
set /a count=0
echo  Found UEFN projects:
echo.
for /d %%D in ("%FP_ROOT%\*") do (
    if exist "%%~fD\*.uefnproject" (
        set /a count+=1
        set "proj_!count!=%%~nxD"
        echo    [!count!]  %%~nxD
    )
)

if %count%==0 (
    echo  No projects found. Create a project in UEFN first.
    if not defined NO_PAUSE pause
    exit /b 1
)

echo.
if %count%==1 (
    set choice=1
    echo  Only one project found — selecting it automatically.
) else (
    set /p choice="  Enter the number of the project to deploy to: "
)

set "PROJECT=!proj_%choice%!"
if "!PROJECT!"=="" (
    echo  Invalid selection.
    if not defined NO_PAUSE pause
    exit /b 1
)

set "DEST=%FP_ROOT%\!PROJECT!"
:validate_project
setlocal enabledelayedexpansion
if not exist "!DEST!\*.uefnproject" (
    echo  ERROR: Target must contain a .uefnproject descriptor.
    goto :error
)
echo.
echo  Deploying to:  !DEST!
echo.

:: Use the canonical staged installer so removed modules cannot survive upgrades.
set "INSTALL_PYTHON="
if exist "%~dp0.venv\Scripts\python.exe" set "INSTALL_PYTHON=%~dp0.venv\Scripts\python.exe"
if not defined INSTALL_PYTHON (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "INSTALL_PYTHON=%%P"
)
if not defined INSTALL_PYTHON (
    for %%P in (
        "C:\Program Files\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
        "C:\Program Files (x86)\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
        "D:\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
        "E:\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
    ) do if exist %%P if not defined INSTALL_PYTHON set "INSTALL_PYTHON=%%~P"
)
if not defined INSTALL_PYTHON (
    echo  ERROR: Python 3.11 or newer is required for staged deployment.
    goto :error
)
"!INSTALL_PYTHON!" -c "import sys; sys.exit(sys.version_info < (3,11))" >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python 3.11 or newer is required for staged deployment.
    goto :error
)
set "PYTHONUTF8=1"
echo  [1/1]  Installing package, startup and Verse reference...
"!INSTALL_PYTHON!" "%~dp0install.py" --project "!DEST!" --skip-dependencies --preserve-startup --install-reference
if errorlevel 1 ( echo         FAILED & goto :error ) else ( echo         OK )

:: PySide6 check ? tries multiple install locations
if defined NO_PAUSE (
    echo  Optional PySide6 installation skipped in unattended mode.
    goto :done
)
echo.
set "UE_PYTHON="
for %%P in (
    "C:\Program Files\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
    "C:\Program Files (x86)\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
    "D:\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
    "E:\Epic Games\Fortnite\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
) do (
    if exist %%P (
        if "!UE_PYTHON!"=="" set "UE_PYTHON=%%~P"
    )
)

if not "!UE_PYTHON!"=="" (
    echo  UE Python: !UE_PYTHON!
    "!UE_PYTHON!" -c "import PySide6" >nul 2>&1
    if errorlevel 1 (
        echo  PySide6 not installed. Installing now...
        "!UE_PYTHON!" -m pip install PySide6 --quiet
        if errorlevel 1 (
            echo  WARNING: PySide6 install failed. Dashboard UI may not work.
        ) else (
            echo  PySide6 installed OK.
        )
    ) else (
        echo  PySide6 already installed.
    )
) else (
    echo  NOTE: Could not find UE Python — tried C:, D:, E: drives.
    echo  Run install.py for a full drive scan, or install manually in a terminal:
    echo    "^<UE_PATH^>\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" -m pip install PySide6
)

:: Done
:done
:: The selection loop needs delayed expansion, but leaving it enabled here eats
:: literal exclamation marks. That turned "Syntax passing != working" into the
:: exact opposite in the final safety banner and erased "!! BEFORE COMMITTING !!".
setlocal DisableDelayedExpansion
echo.
echo ==========================================
echo   All files deployed successfully!
echo ==========================================
echo.
echo BEFORE LAUNCH SESSION OR PUSH CHANGES:
echo   Run prepare_launch.bat to move every .py outside the UEFN project.
echo   After the upload finishes, run restore_after_launch.bat.
echo   UEFN 42.00 rejects project .py files for the VKCreateUGC role.
echo.
echo Restart UEFN to verify automatic startup after deployment.
echo New modules or persistent window changes require a full UEFN restart.
echo For existing-module changes only, use the guarded reload below.
echo.
echo [STANDARD] Reload + open dashboard:
echo import UEFN_Toolbelt as tb; tb.hard_reload(); tb.launch_qt()
echo.
echo [SMOKE TEST] Reload + verify health:
echo import UEFN_Toolbelt as tb; tb.hard_reload(); tb.run("toolbelt_smoke_test")
echo.
echo [INTEGRATION TEST] Invasive: requires the dedicated ToolbeltAcceptance project:
echo import UEFN_Toolbelt as tb; tb.hard_reload(); tb.run("toolbelt_integration_test", allow_mutation=True, preserve_bridge=True)
echo.
echo [MASTER SYNC] Reload + sync docs ^& Verse IQ:
echo import UEFN_Toolbelt as tb; tb.hard_reload(); tb.run("api_sync_master")
echo.
echo [VERSE GRAPH] Reload + open device graph:
echo import UEFN_Toolbelt as tb; tb.hard_reload(); tb.run("verse_graph_open")
echo.
echo ==========================================
echo   !! BEFORE COMMITTING !!
echo ==========================================
echo   1. Run drift check (catches stale counts + versions):
echo      python scripts/drift_check.py
echo   2. Run the SMOKE TEST command above in UEFN.
echo   3. Confirm the dashboard opens and your change works.
echo   Only run "git commit" after you see it working live.
echo   Syntax passing != working in the editor.
echo ==========================================
echo.
echo TIP: UEFN can sandbox third-party top-bar menus. Use the Qt dashboard.
echo.
if not defined NO_PAUSE pause
exit /b 0

:error
echo.
echo  Deploy failed. Check that UEFN is not currently open and locking the files.
if not defined NO_PAUSE pause
exit /b 1
