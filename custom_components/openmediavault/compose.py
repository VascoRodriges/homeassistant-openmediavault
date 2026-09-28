"""Helpers for normalizing OpenMediaVault Compose responses."""

from __future__ import annotations

import json
from typing import Any


def normalize_compose_state(status: Any) -> str:
    """Normalize an OMV/Docker Compose status for Home Assistant."""
    value = str(status or "").strip().lower()
    if "restarting" in value:
        return "restarting"
    if "paused" in value:
        return "paused"
    if "running" in value or value.startswith("up"):
        return "running"
    if "created" in value:
        return "created"
    if "dead" in value:
        return "dead"
    return "exited"


def parse_compose_background_output(raw_output: str) -> list[dict[str, Any]]:
    """Parse and normalize the JSON returned by an OMV background job."""
    response = json.loads(raw_output)
    if not isinstance(response, dict):
        raise ValueError("OMV Compose response must be an object")

    data = response.get("data", [])
    if not isinstance(data, list):
        raise ValueError("OMV Compose response data must be a list")

    rows = []
    for item in data:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "name": item.get("name", "unknown"),
                "uuid": item.get("uuid", "unknown"),
                "state": normalize_compose_state(item.get("status")),
                "image": item.get("image", "unknown"),
                "project": item.get("description", "unknown"),
                "service": item.get("svcname", "unknown"),
                "created": item.get("filedate", "unknown"),
            }
        )
    return rows
