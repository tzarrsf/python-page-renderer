# Page Renderer

A simple Flask service that uses Playwright to fetch and render HTML from URLs, exposing a REST endpoint for external clients.

## Python Version

This project requires **Python 3.8 or higher**. You can verify your Python version with:
```bash
python --version
```

### Windows

**Option 1: Windows Official Installer (Recommended)**
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Click the yellow "Download Python" button (latest version 3.x)
3. Run the installer
4. **Important:** Check the box "Add Python to PATH" during installation
5. Click "Install Now"

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
