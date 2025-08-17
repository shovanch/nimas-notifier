from __future__ import annotations
import re
from playwright.sync_api import sync_playwright

def get_availability_via_playwright(
    page_url: str,
    serial_no: str,
    timeout_ms: int = 30000,
) -> int:
    """
    Render the page, find the row where first cell == `serial_no`,
    return the integer in the 'Availability' column.
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
