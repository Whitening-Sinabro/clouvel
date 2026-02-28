# -*- coding: utf-8 -*-
"""Licensing Paths & JSON I/O Module

Centralizes ~/.clouvel/ directory resolution and JSON file operations.
All licensing modules delegate path/IO here to eliminate duplication.
"""

import os
import json
from pathlib import Path
from typing import Any


def get_clouvel_dir() -> Path:
    """Get ~/.clouvel/ directory, creating it if needed.

    Handles Windows (USERPROFILE) vs Unix (HOME) transparently.
    """
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    d = base / ".clouvel"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_clouvel_file(filename: str) -> Path:
    """Get path to a file inside ~/.clouvel/, ensuring directory exists.

    Args:
        filename: File name (e.g. "license.json", "full_trial.json")
    """
    return get_clouvel_dir() / filename


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON from path, returning default on any error.

    Args:
        path: File path to read
        default: Value to return if file missing or invalid (default: None)
    """
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return default


def save_json(path: Path, data: Any) -> bool:
    """Write data as JSON to path.

    Returns True on success, False on failure.
    """
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True
    except OSError:
        return False
