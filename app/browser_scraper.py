from __future__ import annotations
import re
from playwright.sync_api import sync_playwright

def get_availability_via_browser(url: str, row_match: str, timeout_ms: int = 30000) -> int:
    """
    Load the page with Chromium, wait for the table to appear,
    find the row whose first cell equals row_match (case-insensitive),
    and return the integer from the 'Availability' column.
    """
    row_match_norm = row_match.strip().lower()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)

            # Wait for any table rows to be present (tune this selector if needed)
            page.wait_for_selector("table tbody tr", timeout=timeout_ms)

            # Find header index for 'Availability' to avoid hard-coding column numbers
            headers = page.locator("table thead tr th")
            avail_idx = None
            count = headers.count()
            for i in range(count):
                h = headers.nth(i).inner_text().strip().lower()
                if h.startswith("availability"):
                    avail_idx = i
                    break
            if avail_idx is None:
                # Fallback to index 6 (0-based) per your HTML snapshot
                avail_idx = 6

            # Walk rows and match the first cell to row_match
            rows = page.locator("table tbody tr")
            rcount = rows.count()
            for r in range(rcount):
                cells = rows.nth(r).locator("td")
                if cells.count() == 0:
                    continue
                first = cells.nth(0).inner_text().strip().lower()
                if first == row_match_norm:
                    value_text = cells.nth(avail_idx).inner_text().strip()
                    m = re.search(r"\d+", value_text.replace(",", ""))
                    if not m:
                        raise ValueError(f"Matched row but no integer in availability cell: {value_text!r}")
                    return int(m.group(0))

            raise ValueError(f"Row with first cell == {row_match!r} not found")
        finally:
            browser.close()
