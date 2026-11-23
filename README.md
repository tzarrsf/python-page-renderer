# Page Renderer

A simple Flask service that uses Playwright to fetch and render HTML from URLs, exposing a REST endpoint for external clients.

## Python Version

This project requires **Python 3.8 or higher**. You can verify your Python version with:
```bash
python --version
```

### Check Your Current Python Installation

Before installing, check if you already have Python and whether it's official:

```bash
python -c "import sys; print(sys.executable)"
```

**Official installations typically show paths like:**
- Windows: `C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe`
- macOS (Homebrew): `/usr/local/bin/python3.12` or `/opt/homebrew/bin/python3.12`
- macOS (Official): `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12`

**Non-official versions to avoid:**
- Microsoft Store: `C:\Program Files\WindowsApps\PythonSoftwareFoundation...` (causes greenlet compilation errors)
- Anaconda/Miniconda: `C:\Users\<username>\anaconda3\python.exe` (may have compatibility issues)
- System Python: `/usr/bin/python3` on macOS (often outdated)

If you have a non-official version, see the [Removing Non-Official Python](#removing-non-official-python) section below.

### Multiple Python Versions Installed

If you have multiple Python versions on your system (check Settings → Apps → Installed apps, search "Python"), this can cause confusion about which one is being used. **It's best to keep only one official Python version.**

To see which versions you have:
```bash
# Windows: Use the Python Launcher to see all versions
py --list-paths
```

**On Windows, if you have multiple official Python versions:**
1. Open Settings → Apps → Installed apps
2. Search for "Python"
3. Keep only one version (preferably 3.12 or higher)
4. Uninstall all others by clicking the three dots and selecting "Uninstall"
5. Keep the "Python Launcher" if present (it helps manage versions)

After uninstalling extra versions, verify the remaining one:
```bash
python --version
python -c "import sys; print(sys.executable)"
```

### Windows

**Option 1: Windows Official Installer (Recommended)**
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Click the yellow "Download Python" button (latest version 3.x)
3. Run the installer
4. **Important:** Check the box "Add Python to PATH" during installation
5. Click "Install Now"

**If you forgot to check "Add Python to PATH":**
1. Find your Python installation directory (typically `C:\Users\<username>\AppData\Local\Programs\Python\Python312`)
2. Open Settings → System → Environment variables
3. Click "Edit the system environment variables"
4. Click "Environment Variables..." at the bottom
5. Under "System variables," find `Path` and click "Edit"
6. Click "New" and add: `C:\Users\<username>\AppData\Local\Programs\Python\Python312`
7. Click "New" again and add: `C:\Users\<username>\AppData\Local\Programs\Python\Python312\Scripts`
8. Click OK on all dialogs
9. **Close and reopen ALL terminal/IDE windows** (PowerShell, Command Prompt, VS Code, etc.) — environment variables are only loaded when a process starts
10. Verify with: `python --version`

**Option 2: Windows Package Manager (winget)**
```bash
winget install Python.Python.3.12
```

**Option 3: Microsoft Store** ⚠️ NOT RECOMMENDED
Search for "Python 3.12" in the Microsoft Store app and install

> **⚠️ Important:** Microsoft Store Python has restrictions that prevent building C extensions (like greenlet used by Playwright). If you get a `greenlet` compilation error during setup, you must use **Option 1** (Official Installer) instead.

### macOS

**Option 1: Homebrew (Recommended)**
```bash
brew install python@3.12
```

**Option 2: Official Installer**
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download the macOS installer (Intel or Apple Silicon)
3. Run the `.pkg` installer and follow the prompts

**Option 3: MacPorts**
```bash
sudo port install python312
```

### Removing Non-Official Python

**Windows (Microsoft Store Python):**
1. Open Settings → Apps → Installed apps
2. Search for "Python"
3. Click the three dots next to "Python" and select "Uninstall"
4. Confirm the uninstall

**Windows (Anaconda/Miniconda):**
1. Open Control Panel → Programs → Programs and Features
2. Find "Anaconda3" or "Miniconda3"
3. Click "Uninstall"
4. Restart your computer

**macOS (Homebrew Python):**
```bash
brew uninstall python@3.12
```

**macOS (Official Installer):**
1. Open Finder → Applications → Utilities → Terminal
2. Run: `sudo rm -rf /Library/Frameworks/Python.framework/Versions/3.12`
3. Remove symlinks: `sudo rm /usr/local/bin/python* /usr/local/bin/pip*` (if applicable)

## Setup

**Windows (Batch):**
```bash
INSTALL.bat
```

**Windows (PowerShell):**
```powershell
.\INSTALL.ps1
```

**macOS / Linux:**
```bash
chmod +x INSTALL.sh
./INSTALL.sh
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
playwright install chromium
```

## Running

```bash
python main.py
```

Service will start on `http://localhost:3000`

## Usage

### Fetch rendered HTML from a URL

```
GET http://localhost:3000/getRenderedHtmlViaPython?url=<URL-encoded-url>
```

**Example:**
```
GET http://localhost:3000/getRenderedHtmlViaPython?url=https%3A%2F%2Fhelp.salesforce.com%2Fs%2FarticleView%3Fid%3D005388918%26type%3D1
```

**Response (success):**
```json
{
  "html": "<!DOCTYPE html>...",
  "status": 200
}
```

**Response (error):**
```json
{
  "error": "Failed to render page: ...",
  "status": 500
}
```

### Health check

```
GET http://localhost:3000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

## Calling from Google Apps Script

```javascript
function getRenderedHtmlViaPython(url) {
  const encodedUrl = encodeURIComponent(url);
  const endpoint = `http://localhost:3000/getRenderedHtmlViaPython?url=${encodedUrl}`;
  
  try {
    const response = UrlFetchApp.fetch(endpoint, {
      method: 'get',
      muteHttpExceptions: false
    });
    const result = JSON.parse(response.getContentText());
    return result.html;
  } catch (error) {
    throw new Error(`Failed to fetch rendered HTML: ${error.message}`);
  }
}
```

## Thread Safety

- Flask is configured with `threaded=True` to handle concurrent requests
- Playwright instances are created per-request (not shared), so they're inherently thread-safe
- ThreadPoolExecutor is available for future optimization if needed
