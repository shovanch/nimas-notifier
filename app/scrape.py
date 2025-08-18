"""Main scraping orchestration module."""

from app.api_scraper import get_availability_via_api


def get_availability(
    page_url: str, api_url: str, serial_no: str, backend: str
) -> int:
    """Get availability using specified backend: api, playwright, or auto (fallback)."""
    backend = (backend or 'auto').strip().lower()

    if backend == 'api':
        return get_availability_via_api(serial_no=serial_no, api_url=api_url)

    if backend == 'playwright':
        from app.playwright_scraper import get_availability_via_playwright

        return get_availability_via_playwright(page_url, serial_no)

    # auto
    try:
        return get_availability_via_api(serial_no=serial_no, api_url=api_url)
    except Exception as e:
        # fallback only if Playwright is installed
        try:
            from app.playwright_scraper import get_availability_via_playwright
        except Exception as import_err:
            raise RuntimeError(
                f'API failed ({e}); Playwright not available: {import_err}'
            ) from e
        return get_availability_via_playwright(page_url, serial_no)
