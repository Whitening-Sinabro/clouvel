# -*- coding: utf-8 -*-
"""Licensing Quotas Module

WARN count tracking, KB Trial management, Meeting quotas.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .paths import get_clouvel_file, load_json, save_json
from .first_project import get_project_tier
from .validation import get_machine_id


# ============================================================
# WARN 횟수 추적 (v3.1: 전환율 개선)
# ============================================================

def _get_warn_count_path() -> Path:
    """Get warn count tracking file path: ~/.clouvel/warn_count.json"""
    return get_clouvel_file("warn_count.json")


def increment_warn_count(project_path: str) -> int:
    """Increment WARN count for a project and return new count."""
    path = _get_warn_count_path()
    data = load_json(path, {})

    normalized = str(Path(project_path).resolve())
    count = data.get(normalized, 0) + 1
    data[normalized] = count

    save_json(path, data)
    return count


def get_warn_count(project_path: str) -> int:
    """Get current WARN count for a project."""
    data = load_json(_get_warn_count_path(), {})
    normalized = str(Path(project_path).resolve())
    return data.get(normalized, 0)


# ============================================================
# KB Trial 관리 (v3.1: 7일 체험)
# ============================================================

def _get_kb_trial_path() -> Path:
    """Get KB trial tracking file path: ~/.clouvel/kb_trial.json"""
    return get_clouvel_file("kb_trial.json")


def get_kb_trial_start(project_path: str) -> Optional[str]:
    """Get KB trial start date for a project. Returns ISO date string or None."""
    data = load_json(_get_kb_trial_path(), {})
    normalized = str(Path(project_path).resolve())
    return data.get(normalized)


def start_kb_trial(project_path: str) -> str:
    """Start KB trial for a project. Returns the start date."""
    path = _get_kb_trial_path()
    data = load_json(path, {})

    normalized = str(Path(project_path).resolve())
    # Don't overwrite existing trial
    if normalized in data:
        return data[normalized]

    start_date = datetime.now().isoformat()
    data[normalized] = start_date
    save_json(path, data)

    return start_date


# ============================================================
# 주간 풀 매니저 체험 (v3.1)
# ============================================================

def _get_weekly_meeting_path() -> Path:
    """Get weekly meeting tracking file path: ~/.clouvel/weekly_meeting.json"""
    return get_clouvel_file("weekly_meeting.json")


def can_use_weekly_full_meeting(project_path: str) -> Dict[str, Any]:
    """Check if user can use weekly full meeting trial.

    Returns dict with:
    - available: bool
    - last_used_week: str (ISO week, e.g. "2026-W05")
    - current_week: str
    """
    path = _get_weekly_meeting_path()
    data = load_json(path, {})

    normalized = str(Path(project_path).resolve())
    now = datetime.now()
    current_week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"

    last_used_week = data.get(normalized)

    return {
        "available": last_used_week != current_week,
        "last_used_week": last_used_week,
        "current_week": current_week,
    }


def mark_weekly_meeting_used(project_path: str) -> None:
    """Mark weekly full meeting as used for this week."""
    path = _get_weekly_meeting_path()
    data = load_json(path, {})

    normalized = str(Path(project_path).resolve())
    now = datetime.now()
    current_week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    data[normalized] = current_week
    save_json(path, data)


# ============================================================
# Monthly Meeting Quota (v3.3: 월 3회 Full Meeting 체험)
# ============================================================

FREE_MONTHLY_MEETINGS = 3


def _get_quota_exhausted_message() -> str:
    """Get the quota exhausted message (shared by server and local paths)."""
    return f"""
\U0001f3af \uc774\ubc88 \ub2ec \ubb34\ub8cc Meeting {FREE_MONTHLY_MEETINGS}\ud68c\ub97c \ubaa8\ub450 \uc0ac\uc6a9\ud588\uc2b5\ub2c8\ub2e4!

8\uba85 C-level \ub9e4\ub2c8\uc800\uc758 \ud53c\ub4dc\ubc31\uc774 \ub3c4\uc6c0\uc774 \ub418\uc168\ub098\uc694?

Clouvel v6.0\uc5d0\uc11c\ub294 \ubaa8\ub4e0 \uae30\ub2a5\uc774 \ubb34\ub8cc\uc785\ub2c8\ub2e4!
"""


def _get_monthly_meeting_path() -> Path:
    """Get monthly meeting quota tracking file path: ~/.clouvel/monthly_meeting.json"""
    return get_clouvel_file("monthly_meeting.json")


def _mirror_meeting_to_local(server_result: dict) -> None:
    """Mirror server meeting state to local file."""
    current_month = datetime.now().strftime("%Y-%m")
    data = {"month": current_month, "used": server_result.get("used", 0)}
    save_json(_get_monthly_meeting_path(), data)
