from __future__ import annotations
import httpx
from typing import Any

def _value_of(record: list[dict[str, Any]], key: str) -> Any:
    for item in record:
        if item.get("name") == key:
            return item.get("value")
    return None

def _extract_records(data: dict) -> list:
    # Expected shape: {"response":{"records":[ [ {name,value},... ], ... ]}}
    resp = data.get("response") or {}
    recs = resp.get("records")
    if isinstance(recs, list):
        return recs
    return []

def _post(client: httpx.Client, api_url: str, payload: dict) -> dict:
    r = client.post(api_url, json=payload, follow_redirects=True)
    r.raise_for_status()
    return r.json()

def get_availability_via_api(
    serial_no: str,
    api_url: str,
    timeout: float = 20.0,
) -> int:
    """
    Call the JSON endpoint and return the 'Available Seats' for the row
    whose 'Serial No' equals `serial_no` (e.g. 'BMC-58').

    Tries both a minimal payload and the wrapped 'inputData' payload,
    because the backend sometimes requires one or the other.
    """
    headers = {"Content-Type": "application/json"}
    with httpx.Client(timeout=timeout, headers=headers) as client:
        # Attempt 1: minimal payload (often accepted)
        p1 = {
            "index": 1,
            "pgSize": 200,
            "templateID": 3,
            "filters": {"Category Name": "Mountaineering"},
        }
        data = _post(client, api_url, p1)
        records = _extract_records(data)

        # Attempt 2: wrapped payload if needed
        if not records:
            p2 = {
                "inputData": {
                    "index": 1,
                    "pgSize": 200,
                    "isDownload": False,
                    "userID": 0,
                    "parentID": 40330,
                    "numberOfFieldsView": 50,
                    "filters": {"Category Name": "Mountaineering"},
                    "templateID": 3,
                }
            }
            data = _post(client, api_url, p2)
            records = _extract_records(data)

        if not records:
            raise RuntimeError("API returned no records; payload/endpoint may have changed.")

        for rec in records:
            if not isinstance(rec, list):
                continue
            if _value_of(rec, "Serial No") == serial_no:
                avail = _value_of(rec, "Available Seats")
                try:
                    return int(str(avail).replace(",", ""))
                except Exception as e:
                    raise ValueError(f"Non-integer availability for {serial_no}: {avail!r}") from e

        # Useful debugging hint: list first few serials if missing
        sample = [str(_value_of(r, "Serial No")) for r in records[:8]]
        raise ValueError(f"Serial No {serial_no!r} not found. Sample serials: {sample}")
