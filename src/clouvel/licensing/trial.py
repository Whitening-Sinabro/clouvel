# -*- coding: utf-8 -*-
"""Licensing Trial Module

Full Pro Trial (v3.2: 7일 전체 기능 체험).
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .validation import get_machine_id


# ============================================================
# Full Pro Trial (v3.2: 7일 전체 기능 체험)
# ============================================================

FULL_TRIAL_DAYS = 7


def _get_full_trial_path() -> Path:
    """Get full trial tracking file path: ~/.clouvel/full_trial.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "full_trial.json"


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
            try:
                _get_full_trial_path().write_text(
                    json.dumps(local_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            except OSError:
                pass
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
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

    mid = get_machine_id()

    # Already started - don't overwrite
    if "started_at" in data and data.get("machine_id") == mid:
        return get_full_trial_status()

    data["started_at"] = datetime.now().isoformat()
    data["machine_id"] = mid

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

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

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
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
