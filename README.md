# Python Page Renderer

A simple service that uses Playwright to fetch and render HTML from URLs, with two modes of operation:
- **Proxy Mode** — HTTP service on localhost:3000 for direct page rendering requests
- **Worker Mode** — Background worker that polls a Google Sheet for rendering jobs and processes them asynchronously

The worker is designed to be memory-efficient: it stores only URLs in the payload column and extracted content (not full HTML) in the result column, keeping all entries well under the 50,000 character limit.

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

---

# Two Modes of Operation

This service can run in two different modes:

1. **Proxy Mode** — HTTP service listening on localhost:3000. External clients (like Google Apps Script) make requests to fetch rendered HTML.
2. **Worker Mode** — Background worker that polls a Google Sheet for jobs and processes them asynchronously.

You can run either mode, or both simultaneously (on different machines or terminals).

---

## Mode 1: Proxy Mode (HTTP Service)

Runs as an HTTP service on `http://localhost:3000`. External clients make requests to render pages.

### Setup

**First time only:**
```bash
INSTALL.bat
```

### Running

**Windows:**
```bash
.venv\Scripts\python main.py
```

**macOS / Linux:**
```bash
.venv/bin/python main.py
```

**Verify it's running:**
```bash
curl http://localhost:3000/health
```

You should see: `{"status": "ok"}`

### API Endpoints

See [Usage](#usage) section below for full API documentation.

---

## Mode 2: Worker Mode (Sheet Polling)

Continuously polls a Google Sheet for rendering jobs (rows with status "pending") and processes them.

### Prerequisites

1. **GCP Setup** — Complete Steps 1-3 of the [Google Sheets Setup](#calling-from-google-apps-script-via-sheet-job-queue) section below
2. **Service Account JSON** — `gspread_service_account.json` must exist in the project root
3. **Venv Setup** — Run `INSTALL.bat` (or `INSTALL.ps1` / `INSTALL.sh`)

### Running

You can pass either the Sheet ID or the full Google Sheets URL.

**Windows:**
```bash
.venv\Scripts\python worker.py YOUR_SHEET_ID [--debug]
```

**macOS / Linux:**
```bash
.venv/bin/python worker.py YOUR_SHEET_ID [--debug]
```

**Examples:**

Using Sheet ID:
```bash
.venv\Scripts\python worker.py 1H-a6BGoKKrwUi5stro7pusYa9SrqziTEAvOZFsR4y5g
```

Using full URL:
```bash
.venv\Scripts\python worker.py https://docs.google.com/spreadsheets/d/1H-a6BGoKKrwUi5stro7pusYa9SrqziTEAvOZFsR4y5g/edit
```

Using debug mode (saves rendered HTML to `html_dumps/` folder):
```bash
.venv\Scripts\python worker.py YOUR_SHEET_ID --debug
```

The worker will start polling the Sheet immediately. Press `Ctrl+C` to stop it.

---

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

## Calling from Google Apps Script via Sheet Job Queue

This service communicates with Google Apps Script via a Google Sheet job queue. Follow these steps to set up:

### Step 1: Create a Google Sheet

1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new spreadsheet
3. Add a tab named `Jobs`
4. In the `Jobs` tab, add a header row with these columns:
   - Column A: `id` — Unique job identifier
   - Column B: `status` — Job status (pending, running, done, error)
   - Column C: `input` — The URL to render
   - Column D: `pattern` — Optional regex pattern for content extraction
   - Column E: `output` — The extracted result (never the full HTML)
   - Column F: `timestamp` — When the job was processed

**Pattern Examples (Column D):**
- Leave empty: Extracts title from the page (default for Salesforce Help articles)
- JavaScript regex like `/pattern/flags` (e.g., `/<h1>(.*?)<\/h1>/i`): Extracts matching content
- Plain regex pattern: `title="([^"]*)"` extracts title attribute values

**Important:** Always keep results under 50,000 characters. Use extraction patterns to avoid storing full HTML.

5. Keep the Sheet open for now (don't share yet)

### Step 2: Set Up Google Cloud Project & Create Service Account

**2a. Create a Google Cloud Project:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click **NEW PROJECT**
4. Enter a project name (e.g., "Page Renderer")
5. Click **CREATE**
6. Wait for the project to be created, then select it from the dropdown

**2b. Enable Required APIs:**
1. In the Google Cloud Console, search for "Sheets API" in the search bar
2. Click on **Google Sheets API** and click **ENABLE**
3. Search for "Drive API" in the search bar
4. Click on **Google Drive API** and click **ENABLE**

**2c. Create a Service Account:**
1. Go to **APIs & Services** → **Credentials** (left sidebar)
2. Click **+ CREATE CREDENTIALS** → **Service Account**
3. Enter a service account name (e.g., "page-renderer-worker")
4. Click **CREATE AND CONTINUE**
5. Grant the service account the **Editor** role (required to modify Sheets)
6. Click **CONTINUE** and then **DONE**

**2d. Create and Download the Service Account Key:**
1. Go back to **APIs & Services** → **Service Accounts** (left sidebar)
2. Find and click the service account you just created
3. Click the **KEYS** tab
4. Click **ADD KEY** → **Create new key**
5. Select **JSON** as the key type
6. Click **CREATE**
7. The JSON file will download automatically to your Downloads folder
8. **Important:** Keep this file secure and never commit it to git

**2e. Save the Service Account JSON File:**
1. Find the downloaded JSON file (usually named something like `page-renderer-xxxxx.json`)
2. Rename it to `gspread_service_account.json`
3. Move it to the page-renderer project root directory (same folder as `main.py`, `worker.py`, and `INSTALL.bat`)
4. Add `gspread_service_account.json` to `.gitignore` to prevent accidental commits

### Step 3: Share the Sheet with Your Service Account

1. Find your service account email:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Go to **APIs & Services** → **Service Accounts**
   - Click the service account you created
   - Copy the email address (looks like `page-renderer-worker@project-name.iam.gserviceaccount.com`)

2. Share the Google Sheet:
   - Open your Google Sheet in [sheets.google.com](https://sheets.google.com)
   - Click **Share** (top right)
   - Paste the service account email
   - Select **Editor** from the role dropdown
   - Click **Share** (you don't need to send an email since this is a service account)

**Important:** The Sheet MUST be shared with the service account email, or the worker will fail with a clear error.

### Step 4: Verify Everything is Set Up

Before running the worker, verify:
- [ ] `gspread_service_account.json` exists in the project root
- [ ] The Google Sheet has a "Jobs" tab with headers: id, status, input, pattern, output, timestamp
- [ ] The Sheet is shared with the service account email
- [ ] You have either the Sheet ID or the full URL

### Step 5: Run the Worker

First, install dependencies:

```bash
INSTALL.bat
```

Then run the worker with your Sheet ID or URL:

**Using Sheet ID:**
```bash
.venv\Scripts\python worker.py 1H-a6BGoKKrwUi5stro7pusYa9SrqziTEAvOZFsR4y5g
```

**Using full URL:**
```bash
.venv\Scripts\python worker.py https://docs.google.com/spreadsheets/d/1H-a6BGoKKrwUi5stro7pusYa9SrqziTEAvOZFsR4y5g/edit
```

**Using debug mode (saves HTML to html_dumps/):**
```bash
.venv\Scripts\python worker.py YOUR_SHEET_ID --debug
```

**Job Processing:**
- The worker polls the Sheet every 5 seconds for rows with status "pending"
- For each pending job:
  1. Reads the URL from column C (input)
  2. Reads the regex pattern from column D (pattern)
  3. Renders the page using Playwright
  4. Extracts content using the pattern (or extracts title if pattern is empty)
  5. Writes the result to column E (output)
  6. Updates status to "done" or "error" in column B
  7. Records the timestamp in column F
- Press `Ctrl+C` to stop the worker at any time

**Examples:**

Extracting title from a Salesforce Help article (no pattern needed):
| id | status | input | pattern | output | timestamp |
|-|-|-|-|-|-|
| abc-123 | pending | https://help.salesforce.com/s/articleView?id=005388918&type=1 | | | |

Extracting with a regex pattern:
| id | status | input | pattern | output | timestamp |
|-|-|-|-|-|-|
| xyz-789 | pending | https://example.com/product | /price:\s*\$?([\d,]+\.?\d*)/i | | |

### Error Handling

If the Sheet is not shared with the authenticated account, the worker will:
1. Log a clear error message to the terminal
2. Write the error to the Jobs sheet in the result column
3. The error will be surfaced in GAS via `sideBarConsole.error()`

Example error message:
```
❌ SHEET_NOT_SHARED: Sheet not shared with authenticated account. 
   Share the Sheet with the email used to authenticate the worker.
```

## Thread Safety

- Flask is configured with `threaded=True` to handle concurrent requests
- Playwright instances are created per-request (not shared), so they're inherently thread-safe
- ThreadPoolExecutor is available for future optimization if needed
