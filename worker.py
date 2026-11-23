#!/usr/bin/env python3
import json
import time
import sys
import os
from pathlib import Path
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

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

def render_page(url, extract_type=None):
    """Render a page using Playwright and extract relevant content.

    Args:
        url: The URL to render
        extract_type: Optional extraction type. If None, returns full HTML.
                     'title-metadata' returns only title-related HTML sections
                     Custom regex pattern can also be passed

    Returns:
        Extracted content based on extract_type, or full HTML if extract_type is None
    """
    import re
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, wait_until='networkidle')
                html = page.content()
                browser.close()

                # If no extraction type specified, return full HTML
                if not extract_type:
                    return html

                # Extract title-related metadata only (for Salesforce Help articles, etc.)
                if extract_type == 'title-metadata':
                    result_parts = []

                    # Extract <title> tag
                    title_match = re.search(r'<title\b[^>]*>[\s\S]*?</title\s*>', html, re.IGNORECASE)
                    if title_match:
                        result_parts.append(title_match.group(0))

                    # Extract og:title meta tag
                    og_match = re.search(r'<meta\s+property="og:title"[^>]*>', html, re.IGNORECASE)
                    if og_match:
                        result_parts.append(og_match.group(0))

                    # Extract h1.article-title
                    h1_match = re.search(r'<h1\b[^>]*class="[^"]*article-title[^"]*"[^>]*>[\s\S]*?</h1\s*>', html, re.IGNORECASE)
                    if h1_match:
                        result_parts.append(h1_match.group(0))

                    # Extract JSON-LD blocks
                    ld_matches = re.finditer(r'<script\s+type="application/ld\+json"[^>]*>[\s\S]*?</script\s*>', html, re.IGNORECASE)
                    for match in ld_matches:
                        result_parts.append(match.group(0))

                    return '\n'.join(result_parts)

                # Try to use extract_type as regex pattern
                try:
                    match = re.search(extract_type, html, re.DOTALL)
                    if match:
                        return match.group(0) if match.groups() == () else match.group(1)
                except re.error:
                    # If regex fails, return full HTML
                    return html

                return ""
            except Exception as e:
                browser.close()
                raise Exception(f"Failed to render page: {str(e)}")
    except Exception as e:
        raise Exception(f"Browser error: {str(e)}")

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
                    payload_str = r[2] if len(r) > 2 else ""
                    extract_type = r[3] if len(r) > 3 else None

                    print(f"Processing job {job_id}: URL={payload_str}, extract_type={extract_type}")
                    sh.update_cell(i, 2, "running")

                    try:
                        result = render_page(payload_str, extract_type)
                        sh.update(f"B{i}:E{i}", [[
                            "done",
                            result,
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
