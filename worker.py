#!/usr/bin/env python3
import json
import time
import sys
import os
from pathlib import Path
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_credentials():
    """Load credentials from gspread_service_account.json in the project root."""
    creds_path = Path(__file__).parent / "gspread_service_account.json"
    if not creds_path.exists():
        raise FileNotFoundError(
            f"gspread_service_account.json not found at {creds_path}\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create a Service Account (see README.md for detailed steps)\n"
            "3. Download the JSON key file\n"
            "4. Save it as gspread_service_account.json in this directory\n"
            "5. Share your Google Sheet with the service account email"
        )
    return Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)

def render_page(url):
    """Render a page and return the HTML. Update this with your existing page-renderer logic."""
    # TODO: Import and call your existing page-renderer logic
    # This is a placeholder that returns a mock response
    return {
        "html": "<html><body>Rendered content for: " + url + "</body></html>",
        "status": "success"
    }

def main(sheet_id):
    try:
        creds = get_credentials()
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id).worksheet("Jobs")
    except SpreadsheetNotFound:
        error_msg = f"❌ SHEET_NOT_FOUND: Sheet with ID '{sheet_id}' not found or not shared with authenticated account."
        print(error_msg)
        print("   Ensure:")
        print("   1. The Sheet ID is correct")
        print("   2. The Sheet is shared with the email used to authenticate this worker")
        print("   3. You authenticated with the correct Google account")
        sys.exit(1)
    except APIError as e:
        if "403" in str(e) or "Forbidden" in str(e):
            error_msg = "❌ SHEET_NOT_SHARED: Sheet is not shared with the authenticated account."
            print(error_msg)
            print("   Fix: In Google Sheets, click Share and grant access to the email used to authenticate this worker.")
            sys.exit(1)
        else:
            raise

    print(f"✅ Worker started, polling sheet {sheet_id}")

    while True:
        try:
            rows = sh.get_all_values()

            for i, r in enumerate(rows[1:], start=2):  # Skip header row
                if len(r) > 1 and r[1] == "pending":
                    job_id = r[0]
                    payload = json.loads(r[2])

                    print(f"Processing job {job_id}: {payload}")
                    sh.update_cell(i, 2, "running")

                    try:
                        result = render_page(payload.get("url", ""))
                        sh.update(f"B{i}:E{i}", [[
                            "done",
                            json.dumps(result),
                            "",
                            time.strftime("%Y-%m-%d %H:%M:%S")
                        ]])
                        print(f"✅ Job {job_id} completed")
                    except Exception as e:
                        error_str = str(e)
                        sh.update(f"B{i}:E{i}", [[
                            "error",
                            error_str,
                            "",
                            time.strftime("%Y-%m-%d %H:%M:%S")
                        ]])
                        print(f"❌ Job {job_id} failed: {error_str}")

            time.sleep(5)
        except APIError as e:
            if "403" in str(e) or "Forbidden" in str(e):
                error_msg = "❌ SHEET_NOT_SHARED: Sheet access lost or not shared with authenticated account."
                print(error_msg)
                print("   Reconnecting in 30 seconds...")
                time.sleep(30)
            else:
                print(f"❌ Worker error: {e}")
                time.sleep(5)
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python worker.py SHEET_ID")
        print("")
        print("SHEET_ID: The Google Sheet ID from the URL (long string between /d/ and /edit)")
        print("Example: python worker.py 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p")
        sys.exit(1)

    sheet_id = sys.argv[1]
    main(sheet_id)
