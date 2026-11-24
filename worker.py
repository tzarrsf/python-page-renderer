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

def extract_title_from_html(html):
    """Extract article title from HTML using multiple strategies."""
    import re
    import html as html_module

    # Strategy 1: JSON-LD headline
    ld_matches = re.finditer(r'<script\s+type="application/ld\+json"[^>]*>([\s\S]*?)</script\s*>', html, re.IGNORECASE)
    for match in ld_matches:
        try:
            data = json.loads(match.group(1))
            headline = extract_headline_from_json(data)
            if headline:
                return headline
        except:
            pass

    # Strategy 2: og:title meta tag
    og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html, re.IGNORECASE)
    if og_match:
        return html_module.unescape(og_match.group(1)).strip()

    # Strategy 3: <title> tag
    title_match = re.search(r'<title\b[^>]*>([\s\S]*?)</title\s*>', html, re.IGNORECASE)
    if title_match:
        title_text = title_match.group(1).strip()
        title_text = re.sub(r'\s+\|\s+Salesforce\s+Help\s*$', '', title_text, flags=re.IGNORECASE)
        if title_text and not re.match(r'^Salesforce\s+Help\s*$', title_text, re.IGNORECASE):
            return title_text

    # Strategy 4: h1.article-title
    h1_match = re.search(r'<h1\b[^>]*class="[^"]*article-title[^"]*"[^>]*>([\s\S]*?)</h1\s*>', html, re.IGNORECASE)
    if h1_match:
        title_text = re.sub(r'<[^>]+>', '', h1_match.group(1))
        return html_module.unescape(title_text).replace('\n', ' ').strip()

    return ""

def extract_headline_from_json(data):
    """Recursively extract headline from JSON-LD data."""
    if isinstance(data, dict):
        types = data.get('@type', [])
        if isinstance(types, str):
            types = [types]

        is_article = any(t.endswith(('Article', 'TechArticle', 'NewsArticle', 'BlogPosting')) for t in types)
        if is_article and 'headline' in data:
            return data['headline'].strip()

        for v in data.values():
            result = extract_headline_from_json(v)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = extract_headline_from_json(item)
            if result:
                return result

    return ""

def convert_js_regex_to_python(js_regex):
    """Convert JavaScript regex literal to Python regex pattern.

    Handles patterns like: /<pattern>/i, /pattern/, or just pattern
    Returns: (pattern, flags)
    """
    import re as re_module
    js_regex = js_regex.strip()

    # Check if it's a JavaScript regex literal (starts and ends with /)
    if js_regex.startswith('/') and '/' in js_regex[1:]:
        last_slash = js_regex.rfind('/')
        pattern = js_regex[1:last_slash]
        flags_str = js_regex[last_slash + 1:]

        # Convert JS flags to Python flags
        flags = 0
        if 'i' in flags_str:
            flags |= re_module.IGNORECASE
        if 'm' in flags_str:
            flags |= re_module.MULTILINE
        if 's' in flags_str:
            flags |= re_module.DOTALL

        return pattern, flags

    # Otherwise treat as plain pattern
    return js_regex, re_module.DOTALL

def render_page(url, extract_type=None, debug=False):
    """Render a page using Playwright and extract relevant content.

    Args:
        url: The URL to render
        extract_type: Optional extraction type. If None or empty, extracts title from Salesforce Help articles.
                     Can be a JavaScript regex like /<pattern>/flags or just the pattern.
        debug: If True, dump rendered HTML to html_dumps folder

    Returns:
        Extracted content based on extract_type
    """
    import re
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                html = page.content()
                browser.close()

                if debug:
                    dump_html(url, html)

                # Default: extract title for Salesforce Help articles
                if not extract_type:
                    return extract_title_from_html(html)

                # Try to use extract_type as regex pattern
                try:
                    pattern, flags = convert_js_regex_to_python(extract_type)
                    match = re.search(pattern, html, flags)
                    if match:
                        return match.group(1) if match.groups() else match.group(0)
                except re.error as e:
                    return f"Regex error: {str(e)}"

                return ""
            except Exception as e:
                browser.close()
                raise Exception(f"Failed to render page: {str(e)}")
    except Exception as e:
        raise Exception(f"Browser error: {str(e)}")

def find_header_column(headers, expected_header):
    """Find column index by header name (case-insensitive, ignoring spaces/underscores)."""
    normalized_expected = expected_header.strip().lower().replace(' ', '').replace('_', '')
    for i, header in enumerate(headers):
        normalized_header = header.strip().lower().replace(' ', '').replace('_', '')
        if normalized_header == normalized_expected:
            return i
    return -1

def dump_html(url, html):
    """Write rendered HTML to html_dumps folder with sanitized URL as filename."""
    import re
    dump_dir = Path("html_dumps")
    dump_dir.mkdir(exist_ok=True)

    # Sanitize URL for use as filename
    sanitized = re.sub(r'[^\w\-._~]', '_', url)[:200]
    filepath = dump_dir / f"{sanitized}.html"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"💾 HTML dump saved to {filepath}")

def main(sheet_id, debug=False):
    COLUMNS = [
        'id',
        'status',
        'input',
        'pattern',
        'output',
        'timestamp',
    ]

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

    print(f"🔄️ Worker started, polling sheet {sheet_id}")

    while True:
        try:
            rows = sh.get_all_values()
            if len(rows) < 1:
                time.sleep(5)
                continue

            headers = rows[0]
            col_positions = {name: find_header_column(headers, name) for name in COLUMNS}

            missing = [name for name in COLUMNS if col_positions[name] == -1]
            if missing:
                expected = ', '.join(COLUMNS)
                missing_str = ', '.join(missing)
                print(f"❌ Required columns not found in Jobs sheet. Expected: {expected}. Missing: {missing_str}")
                time.sleep(5)
                continue

            id_col = col_positions['id']
            status_col = col_positions['status']
            input_col = col_positions['input']
            pattern_col = col_positions['pattern']
            output_col = col_positions['output']
            timestamp_col = col_positions['timestamp']

            for i, r in enumerate(rows[1:], start=2):  # Skip header row
                if len(r) > status_col and r[status_col] == "pending":
                    job_id = r[id_col] if len(r) > id_col else ""
                    payload_str = r[input_col] if len(r) > input_col else ""
                    extract_type = r[pattern_col] if pattern_col != -1 and len(r) > pattern_col else None

                    print(f"🟨 Job {job_id} processing: URL → {payload_str}, pattern → {extract_type}")
                    sh.update_cell(i, status_col + 1, "running")

                    try:
                        result = render_page(payload_str, extract_type, debug=debug)
                        sh.update_cell(i, status_col + 1, "done")

                        # Prepare update values with output and timestamp
                        update_values = [[result]]
                        if timestamp_col != -1:
                            update_values[0].append(time.strftime("%Y-%m-%d %H:%M:%S"))

                        # Update output column (and timestamp if present)
                        start_col = output_col + 1
                        end_col = timestamp_col + 1 if timestamp_col != -1 else output_col + 1
                        sh.update(range_name=f"{chr(64 + start_col)}{i}:{chr(64 + end_col)}{i}", values=update_values)
                        print(f"✅ Job {job_id} completed.")
                    except Exception as e:
                        error_str = str(e)
                        sh.update_cell(i, status_col + 1, "error")

                        # Prepare update values with error and timestamp
                        update_values = [[error_str]]
                        if timestamp_col != -1:
                            update_values[0].append(time.strftime("%Y-%m-%d %H:%M:%S"))

                        # Update output column (and timestamp if present)
                        start_col = output_col + 1
                        end_col = timestamp_col + 1 if timestamp_col != -1 else output_col + 1
                        sh.update(range_name=f"{chr(64 + start_col)}{i}:{chr(64 + end_col)}{i}", values=update_values)
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

def extract_sheet_id(input_str):
    """Extract sheet ID from full URL or return as-is if already an ID."""
    import re
    # Try to extract from Google Sheets URL
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', input_str)
    if match:
        return match.group(1)
    # Assume it's already the ID
    return input_str

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python worker.py SHEET_ID_OR_URL [--debug]")
        print("")
        print("SHEET_ID_OR_URL: Either the Google Sheet ID or the full Sheet URL")
        print("Sheet ID Example: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p")
        print("URL Example: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p/edit")
        print("")
        print("Options:")
        print("  --debug    Dump rendered HTML to html_dumps/ folder")
        sys.exit(1)

    sheet_input = sys.argv[1]
    debug = "--debug" in sys.argv
    sheet_id = extract_sheet_id(sheet_input)
    main(sheet_id, debug=debug)
