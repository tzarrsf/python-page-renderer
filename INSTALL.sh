#!/bin/bash
set -e

cd "$(dirname "$0")"

VENV_DIR=".venv"
PY="python3"

echo "[*] Installation process started"
echo ""

echo "[>] Checking Python 3+..."
if ! command -v $PY &> /dev/null; then
    echo "[x] Python 3 was not found."
    echo ""
    exit 1
fi

echo "[>] Removing any existing virtual environment..."
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
fi

echo "[>] Creating virtual environment in $VENV_DIR..."
$PY -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "[x] Failed to create virtual environment."
    echo ""
    exit 1
fi

VENV_PY="$VENV_DIR/bin/python"

echo "[>] Upgrading pip..."
"$VENV_PY" -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[x] Failed to upgrade pip."
    echo ""
    exit 1
fi

echo "[>] Installing requirements..."
"$VENV_PY" -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[x] Failed to install requirements."
    echo ""
    exit 1
fi

echo "[>] Installing playwright for Chromium..."
"$VENV_PY" -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "[x] Failed to install playwright."
    echo ""
    exit 1
fi

echo "[+] Installation complete."
echo ""
echo "[i] To run the service:"
echo "    ./$VENV_DIR/bin/python main.py"
echo ""
