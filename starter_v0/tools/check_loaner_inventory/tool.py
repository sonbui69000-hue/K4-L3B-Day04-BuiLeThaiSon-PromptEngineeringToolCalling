from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text


LOANER_FILE = ROOT / "helpdesk_data" / "loaners.json"
_VALID_TYPES = {"any", "laptop", "desktop", "mobile", "peripheral"}
_VALID_OS = {"any", "windows", "macos", "linux", "ios"}


def _clean(value: str | None) -> str:
    return fold_text((value or "").strip())


def check_loaner_inventory(
    device_type: str = "any",
    location: str = "",
    os_family: str = "any",
    max_results: int = 3,
) -> dict[str, Any]:
    try:
        data = json.loads(LOANER_FILE.read_text(encoding="utf-8"))
        wanted_type = _clean(device_type) or "any"
        wanted_location = _clean(location)
        wanted_os = _clean(os_family) or "any"
        if wanted_type not in _VALID_TYPES:
            return {
                "tool": "check_loaner_inventory",
                "error": "invalid_device_type",
                "device_type": device_type,
                "allowed_device_types": sorted(_VALID_TYPES),
            }
        if wanted_os not in _VALID_OS:
            return {
                "tool": "check_loaner_inventory",
                "error": "invalid_os_family",
                "os_family": os_family,
                "allowed_os_families": sorted(_VALID_OS),
            }

        matches: list[dict[str, Any]] = []
        for item in data["loaners"]:
            if item["status"] != "available":
                continue
            if wanted_type != "any" and item["device_type"] != wanted_type:
                continue
            if wanted_os != "any" and item["os_family"] != wanted_os:
                continue
            if wanted_location and wanted_location not in _clean(item["location"]):
                continue
            matches.append(item)

        limit = max(1, min(int(max_results or 3), 10))
        return {
            "tool": "check_loaner_inventory",
            "device_type": wanted_type,
            "location": location.strip(),
            "os_family": wanted_os,
            "available_count": len(matches),
            "matches": matches[:limit],
            "snapshot_at": data["snapshot_at"],
            "side_effect": False,
        }
    except Exception as exc:
        return err("check_loaner_inventory", exc)
