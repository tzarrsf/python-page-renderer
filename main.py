"""
Rendered page fetcher service.
Provides HTTP endpoint to fetch and render HTML from URLs using Playwright.
"""

from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

def fetch_rendered_html(url: str) -> dict:
    """
    Fetch a URL and return the rendered HTML.

    Args:
        url: The URL to fetch

    Returns:
        dict with 'html' key containing the rendered HTML, or 'error' on failure
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(url, wait_until='networkidle')
                html = page.content()
                browser.close()
                return {'html': html, 'status': 200}
            except Exception as e:
                browser.close()
                return {
                    'error': f'Failed to render page: {str(e)}',
                    'status': 500
                }
    except Exception as e:
        return {
            'error': f'Browser error: {str(e)}',
            'status': 500
        }


@app.route('/getRenderedHtmlViaPython', methods=['GET'])
def getRenderedHtmlViaPython():
    """
    GET endpoint to fetch and render HTML.

    Query parameters:
        url: The URL to fetch and render (URL-encoded)

    Returns:
        JSON with 'html' key on success, or 'error' on failure
    """
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    try:
        url = unquote(url)
    except Exception as e:
        return jsonify({'error': f'Invalid URL encoding: {str(e)}'}), 400

    result = fetch_rendered_html(url)

    if 'error' in result:
        return jsonify(result), result.get('status', 500)

    return jsonify(result), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info('Starting rendered page fetcher service on http://localhost:3000')
    app.run(host='127.0.0.1', port=3000, debug=False, threaded=True)
