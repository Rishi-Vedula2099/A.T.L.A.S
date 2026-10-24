@echo off
REM ==============================================================================
REM A.T.L.A.S - Windows installer launcher (cmd.exe entrypoint)
REM ==============================================================================
REM Thin wrapper that invokes install.ps1 via PowerShell. All logic lives in
REM PowerShell so the same code runs from cmd, Explorer double-click, and pwsh.
REM
REM Usage:
REM   install.bat                         full bootstrap
REM   install.bat --force-secrets         rotate all secrets (destructive)
REM   install.bat --profile observability
REM   install.bat --skip-open
REM ==============================================================================

setlocal enableextensions

REM Locate PowerShell (prefer pwsh Core, fall back to Windows PowerShell).
where pwsh >nul 2>nul
if %errorlevel%==0 (
    set "PS=pwsh -NoProfile -ExecutionPolicy Bypass -File"
) else (
    set "PS=powershell -NoProfile -ExecutionPolicy Bypass -File"
)

REM %~dp0 = directory of this batch file, with trailing backslash.
set "SCRIPT_DIR=%~dp0"

REM Forward all args through to install.ps1 (PowerShell will parse them).
%PS% "%SCRIPT_DIR%install.ps1" %*
set "RC=%errorlevel%"

endlocal & exit /b %RC%
