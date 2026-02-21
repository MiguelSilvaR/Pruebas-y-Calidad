"""
Storage utilities shared across the project.

This module centralizes JSON persistence helpers used by multiple domain
services (e.g., customers, hotels, reservations) to avoid duplicated code.

Behavior:
- safe_load_list: best-effort JSON list loading; returns [] on errors.
- safe_write_list: best-effort JSON list writing;
  logs errors instead of raising.
- print_data_error: prints a standardized data error message.
"""
from __future__ import annotations

import json
from typing import List


def print_data_error(message: str) -> None:
    """
    Prints a data-related error
    without raising (best-effort persistence).
    """
    print(f"[DATA ERROR] {message}")


def safe_load_list(path: str) -> List[dict]:
    """
    Loads a JSON list from path.
    Returns [] on errors or invalid root type.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            print_data_error(f"Expected list in {path}")
            return []
        return [x for x in data if isinstance(x, dict)]
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError) as exc:
        print_data_error(f"Cannot read {path}: {exc}")
        return []


def safe_write_list(path: str, items: List[dict]) -> None:
    """Writes items as a JSON list to path. Logs errors instead of raising."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(items, handle, indent=2, ensure_ascii=False)
    except OSError as exc:
        print_data_error(f"Cannot write {path}: {exc}")
