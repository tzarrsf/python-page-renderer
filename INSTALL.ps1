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

    Step "Upgrading pip..."
    & $VenvPython -m pip install --upgrade pip
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
    Info "To run the service:"
    Write-Host "    .\$VenvDir\Scripts\python.exe main.py" -ForegroundColor Yellow
    Write-Host ""
}
catch {
    ErrorMsg "Installation failed: $_"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"
