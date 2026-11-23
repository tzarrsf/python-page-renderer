$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Set-Location -Path $PSScriptRoot

$VenvDir = ".venv"
$PythonLauncher = "py"

function Header($msg)   { Write-Host "[*] $msg" -ForegroundColor Cyan }
function Step($msg)     { Write-Host "[>] $msg" -ForegroundColor Yellow }
function Success($msg)  { Write-Host "[+] $msg" -ForegroundColor Green }
function Info($msg)     { Write-Host "[i] $msg" -ForegroundColor Gray }
function ErrorMsg($msg) { Write-Host "[x] $msg" -ForegroundColor Red }

try {
    Header "Installation process started"

    Step "Checking Python 3+..."
    & $PythonLauncher -3 --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        ErrorMsg "Python 3 was not found."
        throw
    }

    Step "Removing any existing virtual environment..."
    if (Test-Path $VenvDir) {
        Remove-Item -Recurse -Force $VenvDir -ErrorAction SilentlyContinue
    }

    Step "Creating virtual environment in $VenvDir..."
    & $PythonLauncher -3 -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment."
    }

    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"

    Step "Upgrading pip, wheel, and setuptools..."
    & $VenvPython -m pip install --upgrade pip wheel setuptools
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip."
    }

    Step "Installing requirements..."
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install requirements."
    }

    Step "Installing playwright for Chromium..."
    & $VenvPython -m playwright install chromium
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install playwright."
    }

    Success "Installation complete."
    Write-Host ""
    Info "Virtual environment created in: $VenvDir"
    Info "To use the venv, run:"
    Write-Host "    .\$VenvDir\Scripts\python.exe main.py" -ForegroundColor Yellow
    Write-Host "    or" -ForegroundColor Gray
    Write-Host "    .\$VenvDir\Scripts\python.exe worker.py SHEET_ID" -ForegroundColor Yellow
    Write-Host ""
}
catch {
    ErrorMsg "Installation failed: $_"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"
