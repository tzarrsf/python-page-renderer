@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PY=py -3"

call :header "Installation process started"

:: --- Check Python 3+ ---
call :step "Checking Python 3+..."
%PY% --version >nul 2>&1
if errorlevel 1 (
    call :error "Python 3 was not found."
    goto :fail
)

:: --- Remove existing venv ---
call :step "Removing any existing virtual environment..."
if exist "%VENV_DIR%" (
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im python3.exe >nul 2>&1
    rd /s /q "%VENV_DIR%"
)

if exist "%VENV_DIR%" (
    call :error "Could not remove .venv. Falling back to .venv2."
    set "VENV_DIR=.venv2"
)

:: --- Create venv ---
call :step "Creating virtual environment in %VENV_DIR%..."
%PY% -m venv "%VENV_DIR%"
if errorlevel 1 goto :fail

set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

:: --- Install ---
call :step "Upgrading pip..."
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :fail

call :step "Installing requirements..."
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

call :step "Installing playwright for Chromium..."
"%VENV_PY%" -m playwright install chromium
if errorlevel 1 goto :fail

:: --- Done ---
call :success "Installation complete."
echo.

call :info "To run the service:" Cyan
echo     %VENV_PY% main.py
echo.

goto :end

:fail
call :error "Installation failed."
echo.
pause
exit /b 1

:: --- Styled output helpers (PowerShell-backed) ---
:header
powershell -NoProfile -Command "Write-Host '[*]  %~1' -ForegroundColor Cyan"
exit /b

:step
powershell -NoProfile -Command "Write-Host '[>]  %~1' -ForegroundColor Yellow"
exit /b

:success
powershell -NoProfile -Command "Write-Host '[+]  %~1' -ForegroundColor Green"
exit /b

:info
powershell -NoProfile -Command "Write-Host '[i]  %~1' -ForegroundColor %~2"
exit /b

:error
powershell -NoProfile -Command "Write-Host '[x]  %~1' -ForegroundColor Red"
exit /b

:end
pause
endlocal
