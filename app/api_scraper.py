"""JSON API scraping module for NIMAS data."""

from typing import Any

import httpx


def _value_of(record: list[dict[str, Any]], key: str) -> Any:
    """Extract value from record list by key name."""
    for item in record:
        if item.get('name') == key:
            return item.get('value')
    return None


def _extract_records(data: dict) -> list:
    """Extract records from API response data."""
    # Expected shape: {"response":{"records":[ [ {name,value},... ], ... ]}}
    resp = data.get('response') or {}
    recs = resp.get('records')
    if isinstance(recs, list):
        return recs
    return []


def _post(client: httpx.Client, api_url: str, payload: dict) -> Any:
    """Make POST request and return JSON response."""
    r = client.post(api_url, json=payload, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def get_availability_via_api(
    serial_no: str,
    api_url: str,
    timeout: float = 20.0,
) -> int:
    """Get availability data via JSON API endpoint.

    Calls the JSON endpoint and returns the 'Available Seats' for the row
    whose 'Serial No' equals the provided serial number.

    Args:
        serial_no: The serial number to look up (e.g. 'BMC-58').
        api_url: The API endpoint URL.
        timeout: Request timeout in seconds.

    Returns:
        The number of available seats.

    Raises:
        RuntimeError: If API returns no records.
        ValueError: If serial number not found or availability is non-integer.
    """
    headers = {'Content-Type': 'application/json'}
    with httpx.Client(timeout=timeout, headers=headers) as client:
        # Attempt 1: minimal payload (often accepted)
        p1 = {
            'index': 1,
            'pgSize': 200,
            'templateID': 3,
            'filters': {'Category Name': 'Mountaineering'},
            'isDownload': False,
            'NumberOfFieldsView': 50,
        }
        data = _post(client, api_url, p1)
        records = _extract_records(data)

        if not records:
            raise RuntimeError(
                'API returned no records; payload/endpoint may have changed.'
            )

        for rec in records:
            if not isinstance(rec, list):
                continue
            if _value_of(rec, 'Serial No') == serial_no:
                avail = _value_of(rec, 'Available Seats')
                try:
                    return int(str(avail).replace(',', ''))
                except Exception as e:
                    raise ValueError(
                        f'Non-integer availability for {serial_no}: {avail!r}'
                    ) from e

        # Useful debugging hint: list first few serials if missing
        sample = [str(_value_of(r, 'Serial No')) for r in records[:8]]
        raise ValueError(
            f'Serial No {serial_no!r} not found. Sample serials: {sample}'
        )
