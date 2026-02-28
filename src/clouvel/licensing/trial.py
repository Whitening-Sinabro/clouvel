# -*- coding: utf-8 -*-
"""Licensing Trial Module

Full Pro Trial (v3.2: 7일 전체 기능 체험).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .paths import get_clouvel_file, load_json, save_json
from .validation import get_machine_id


# ============================================================
# Full Pro Trial (v3.2: 7일 전체 기능 체험)
# ============================================================

FULL_TRIAL_DAYS = 7


def _get_full_trial_path() -> Path:
    """Get full trial tracking file path: ~/.clouvel/full_trial.json"""
    return get_clouvel_file("full_trial.json")


def start_full_trial() -> Dict[str, Any]:
    """Start 7-day Full Pro trial.

    v4.0: Server-first with local fallback.

    Returns:
        dict with started_at, machine_id, remaining_days
    """
    # 1. Try server
    try:
        from .sync import SyncState
        result = SyncState.get().start_trial()
        if result:
            # Mirror to local
            local_data = {
                "started_at": result.get("started_at", datetime.now().isoformat()),
                "machine_id": get_machine_id(),
            }
            save_json(_get_full_trial_path(), local_data)
            return {
                "active": result.get("active", True),
                "started_at": local_data["started_at"],
                "remaining_days": result.get("remaining_days", FULL_TRIAL_DAYS),
                "message": f"Pro trial activated! {FULL_TRIAL_DAYS} days of full access.",
            }
    except (ImportError, OSError, ConnectionError, ValueError):
        pass

    # 2. Fallback: local logic
    path = _get_full_trial_path()
    data = load_json(path, {})

    mid = get_machine_id()

    # Already started - don't overwrite
    if "started_at" in data and data.get("machine_id") == mid:
        return get_full_trial_status()

    data["started_at"] = datetime.now().isoformat()
    data["machine_id"] = mid

    save_json(path, data)

    # Queue for next sync
    try:
        from .sync import mark_pending_sync
        mark_pending_sync("trial_start", data)
    except (ImportError, OSError):
        pass

    try:
        from ..analytics import log_event
        log_event("full_trial_started", {"machine_id": mid[:8]})
    except (ImportError, OSError):
        pass

    return {
        "active": True,
        "started_at": data["started_at"],
        "remaining_days": FULL_TRIAL_DAYS,
        "message": f"Pro trial activated! {FULL_TRIAL_DAYS} days of full access.",
    }


def is_full_trial_active() -> bool:
    """Check if Full Pro trial is still active."""
    status = get_full_trial_status()
    return status.get("active", False)


def get_full_trial_status() -> Dict[str, Any]:
    """Get full trial status with remaining days.

    v4.0: Server-first (server clock prevents date tampering).

    Returns:
        dict with active, started_at, remaining_days, elapsed_days
    """
    # 1. Try server state (cached from last sync)
    try:
        from .sync import SyncState
        ss = SyncState.get()
        if ss.is_synced():
            trial = ss.get_trial_status()
            if trial and "remaining_days" in trial:
                return {
                    "active": trial.get("active", False),
                    "remaining_days": trial.get("remaining_days", 0),
                    "started_at": trial.get("started_at"),
                    "source": "server",
                }
    except (ImportError, OSError):
        pass

    # 2. Fallback: local logic
    path = _get_full_trial_path()
    if not path.exists():
        return {"active": False, "remaining_days": 0, "never_started": True}

    data = load_json(path, None)
    if data is None:
        return {"active": False, "remaining_days": 0, "never_started": True}

    started_at = data.get("started_at")
    stored_mid = data.get("machine_id")
    if not started_at:
        return {"active": False, "remaining_days": 0, "never_started": True}

    # Machine ID mismatch = different machine, trial not valid
    current_mid = get_machine_id()
    if stored_mid and stored_mid != current_mid:
        return {"active": False, "remaining_days": 0, "machine_mismatch": True}

    try:
        start_time = datetime.fromisoformat(started_at)
        elapsed = (datetime.now() - start_time).days
        remaining = max(0, FULL_TRIAL_DAYS - elapsed)
        return {
            "active": remaining > 0,
            "started_at": started_at,
            "elapsed_days": elapsed,
            "remaining_days": remaining,
        }
    except (ValueError, TypeError):
        return {"active": False, "remaining_days": 0}
