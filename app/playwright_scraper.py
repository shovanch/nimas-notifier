"""Playwright-based web scraping module."""

from __future__ import annotations
import re
from playwright.sync_api import sync_playwright

def get_availability_via_playwright(
    page_url: str,
    serial_no: str,
    timeout_ms: int = 30000,
) -> int:
    """Scrape availability data using headless browser automation.
    
    Renders the page, finds the row where the first cell matches the serial number,
    and returns the integer value from the 'Availability' column.
    
    Args:
        page_url: The web page URL to scrape.
        serial_no: The serial number to search for in the first column.
        timeout_ms: Page load and element wait timeout in milliseconds.
        
    Returns:
        The availability number from the matching row.
        
    Raises:
        ValueError: If the serial number is not found or availability cell
                   doesn't contain a valid integer.
    """
    target = serial_no.strip().lower()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(page_url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_selector("table tbody tr", timeout=timeout_ms)

            # Find the index of 'Availability' in headers
            headers = page.locator("table thead tr th")
            idx = None
            for i in range(headers.count()):
                h = headers.nth(i).inner_text().strip().lower()
                if h.startswith("availability"):
                    idx = i
                    break
            if idx is None:
                idx = 6  # fallback (0-based) per current table

            rows = page.locator("table tbody tr")
            for r in range(rows.count()):
                cells = rows.nth(r).locator("td")
                if cells.count() == 0:
                    continue
                first = cells.nth(0).inner_text().strip().lower()
                if first == target:
                    raw = cells.nth(idx).inner_text().strip()
                    m = re.search(r"\d+", raw.replace(",", ""))
                    if not m:
                        raise ValueError(f"Matched row but no integer found in availability cell: {raw!r}")
                    return int(m.group(0))
            raise ValueError(f"Row with first cell == {serial_no!r} not found in DOM.")
        finally:
            browser.close()
