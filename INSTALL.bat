@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "PY=py -3"

echo [*] Installation process started
echo.

echo [>] Checking Python 3+...
%PY% --version >nul 2>&1
if errorlevel 1 (
    echo [x] Python 3 was not found.
    echo.
    pause
    exit /b 1
)

echo [>] Removing any existing virtual environment...
if exist "%VENV_DIR%" (
    taskkill /f /im python.exe >nul 2>&1
    rd /s /q "%VENV_DIR%" >nul 2>&1
)

echo [>] Creating virtual environment in %VENV_DIR%...
%PY% -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo [x] Failed to create virtual environment.
    echo.
    pause
    exit /b 1
)

set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

echo [>] Upgrading pip...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [x] Failed to upgrade pip.
    echo.
    pause
    exit /b 1
)

echo [>] Installing requirements...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [x] Failed to install requirements.
    echo.
    pause
    exit /b 1
)

echo [>] Installing playwright for Chromium...
"%VENV_PY%" -m playwright install chromium
if errorlevel 1 (
    echo [x] Failed to install playwright.
    echo.
    pause
    exit /b 1
)

echo [+] Installation complete.
echo.
echo [i] To run the service:
echo     %VENV_PY% main.py
echo.
pause
endlocal
