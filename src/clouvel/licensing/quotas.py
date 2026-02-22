# -*- coding: utf-8 -*-
"""Licensing Quotas Module

WARN count tracking, KB Trial management, Meeting quotas.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .first_project import get_project_tier
from .validation import get_machine_id


# ============================================================
# WARN 횟수 추적 (v3.1: 전환율 개선)
# ============================================================

def _get_warn_count_path() -> Path:
    """Get warn count tracking file path: ~/.clouvel/warn_count.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "warn_count.json"


def increment_warn_count(project_path: str) -> int:
    """Increment WARN count for a project and return new count."""
    path = _get_warn_count_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

    normalized = str(Path(project_path).resolve())
    count = data.get(normalized, 0) + 1
    data[normalized] = count

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    return count


def get_warn_count(project_path: str) -> int:
    """Get current WARN count for a project."""
    path = _get_warn_count_path()
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        normalized = str(Path(project_path).resolve())
        return data.get(normalized, 0)
    except (OSError, json.JSONDecodeError, ValueError):
        return 0


# ============================================================
# KB Trial 관리 (v3.1: 7일 체험)
# ============================================================

def _get_kb_trial_path() -> Path:
    """Get KB trial tracking file path: ~/.clouvel/kb_trial.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "kb_trial.json"


def get_kb_trial_start(project_path: str) -> Optional[str]:
    """Get KB trial start date for a project. Returns ISO date string or None."""
    path = _get_kb_trial_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        normalized = str(Path(project_path).resolve())
        return data.get(normalized)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def start_kb_trial(project_path: str) -> str:
    """Start KB trial for a project. Returns the start date."""
    path = _get_kb_trial_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

    normalized = str(Path(project_path).resolve())
    # Don't overwrite existing trial
    if normalized in data:
        return data[normalized]

    start_date = datetime.now().isoformat()
    data[normalized] = start_date

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    return start_date


def is_kb_trial_active(project_path: str) -> bool:
    """Check if KB trial is still active (within 7 days).

    v5.0: First project always has KB access (no trial needed).
    """
    # v5.0: First project gets unlimited KB
    try:
        tier = get_project_tier(project_path)
        if tier in ("pro", "first"):
            return True
    except (OSError, json.JSONDecodeError, ValueError):
        pass

    start = get_kb_trial_start(project_path)
    if start is None:
        return True  # No trial started yet = can start one

    try:
        start_time = datetime.fromisoformat(start)
        days = (datetime.now() - start_time).days
        return days < 7
    except (ValueError, TypeError):
        return False


# ============================================================
# 주간 풀 매니저 체험 (v3.1)
# ============================================================

def _get_weekly_meeting_path() -> Path:
    """Get weekly meeting tracking file path: ~/.clouvel/weekly_meeting.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "weekly_meeting.json"


def can_use_weekly_full_meeting(project_path: str) -> Dict[str, Any]:
    """Check if user can use weekly full meeting trial.

    Returns dict with:
    - available: bool
    - last_used_week: str (ISO week, e.g. "2026-W05")
    - current_week: str
    """
    path = _get_weekly_meeting_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

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
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

    normalized = str(Path(project_path).resolve())
    now = datetime.now()
    current_week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    data[normalized] = current_week

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


# ============================================================
# Monthly Meeting Quota (v3.3: 월 3회 Full Meeting 체험)
# ============================================================

FREE_MONTHLY_MEETINGS = 3


def _get_quota_exhausted_message() -> str:
    """Get the quota exhausted message (shared by server and local paths)."""
    return f"""
\U0001f3af \uc774\ubc88 \ub2ec \ubb34\ub8cc Meeting {FREE_MONTHLY_MEETINGS}\ud68c\ub97c \ubaa8\ub450 \uc0ac\uc6a9\ud588\uc2b5\ub2c8\ub2e4!

8\uba85 C-level \ub9e4\ub2c8\uc800\uc758 \ud53c\ub4dc\ubc31\uc774 \ub3c4\uc6c0\uc774 \ub418\uc168\ub098\uc694?

Pro \uac1c\ubc1c\uc790\ub4e4\uc758 \ud6c4\uae30:
"\ud63c\uc790 \uac1c\ubc1c\ud560 \ub54c \ub193\uce58\uae30 \uc26c\uc6b4 \ubcf4\uc548 \uc774\uc288\ub97c CSO\uac00 \uc7a1\uc544\uc918\uc11c \uc88b\uc544\uc694"
"\ucd9c\uc2dc \uc804 CFO \ud53c\ub4dc\ubc31\uc73c\ub85c \uc218\uc775 \ubaa8\ub378 \uad6c\uba4d\uc744 \ubc1c\uacac\ud588\uc2b5\ub2c8\ub2e4"

\ub2e4\uc74c \ub2ec\uae4c\uc9c0 \uae30\ub2e4\ub9ac\uac70\ub098, \uc9c0\uae08 \ubc14\ub85c \ubb34\uc81c\ud55c\uc73c\ub85c \uc0ac\uc6a9\ud558\uc138\uc694.

\U0001f4b0 \uc6d4 $7.99 (\uc5f0\uac04 \uacb0\uc81c \uc2dc 70% \ud560\uc778)
\u2192 https://polar.sh/clouvel
"""


def _get_monthly_meeting_path() -> Path:
    """Get monthly meeting quota tracking file path: ~/.clouvel/monthly_meeting.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "monthly_meeting.json"


def check_meeting_quota(project_path: str = None) -> Dict[str, Any]:
    """Check monthly meeting quota for Free users.

    v3.3: Replaces weekly trial with monthly 3-time quota.
    v4.0: Server-first for tamper-proof counting.
    v5.0: First project bypasses quota entirely.

    Returns:
        dict with:
        - allowed: bool
        - used: int (used this month)
        - remaining: int (remaining this month)
        - limit: int (monthly limit)
        - current_month: str (YYYY-MM)
        - notice: str (optional, shown when 1 remaining)
        - message: str (shown when quota exhausted)
    """
    # v5.0: First project gets unlimited meetings
    if project_path:
        try:
            tier = get_project_tier(project_path)
            if tier in ("pro", "first"):
                return {"allowed": True, "used": 0, "remaining": 999, "limit": 999, "current_month": datetime.now().strftime("%Y-%m")}
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    # v4.0: Try server state first
    try:
        from .sync import SyncState
        ss = SyncState.get()
        if ss.is_synced():
            mq = ss.get_meeting_quota()
            if mq and "used" in mq:
                used = mq["used"]
                remaining = mq.get("remaining", max(0, FREE_MONTHLY_MEETINGS - used))
                result = {
                    "allowed": remaining > 0,
                    "used": used,
                    "remaining": remaining,
                    "limit": mq.get("limit", FREE_MONTHLY_MEETINGS),
                    "current_month": mq.get("month", datetime.now().strftime("%Y-%m")),
                }
                if remaining == 1:
                    result["notice"] = (
                        "\u26a1 \uc774\ubc88 \ub2ec \ub9c8\uc9c0\ub9c9 \ubb34\ub8cc Meeting\uc785\ub2c8\ub2e4!\n"
                        "Pro \uc5c5\uadf8\ub808\uc774\ub4dc\ub85c \ubb34\uc81c\ud55c \uc0ac\uc6a9\ud558\uc138\uc694.\n"
                        "\u2192 https://polar.sh/clouvel"
                    )
                if remaining <= 0:
                    result["message"] = _get_quota_exhausted_message()
                return result
    except (ImportError, OSError):
        pass

    # Fallback: local logic
    path = _get_monthly_meeting_path()
    current_month = datetime.now().strftime("%Y-%m")

    data = {"month": current_month, "used": 0, "history": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Reset if month changed
            if data.get("month") != current_month:
                data = {"month": current_month, "used": 0, "history": []}
        except (OSError, json.JSONDecodeError, ValueError):
            data = {"month": current_month, "used": 0, "history": []}

    used = data.get("used", 0)
    remaining = max(0, FREE_MONTHLY_MEETINGS - used)

    result = {
        "allowed": remaining > 0,
        "used": used,
        "remaining": remaining,
        "limit": FREE_MONTHLY_MEETINGS,
        "current_month": current_month,
    }

    # Notice when last meeting remaining
    if remaining == 1:
        result["notice"] = (
            "⚡ 이번 달 마지막 무료 Meeting입니다!\n"
            "Pro 업그레이드로 무제한 사용하세요.\n"
            "→ https://polar.sh/clouvel"
        )

    # Message when quota exhausted (Pain Point #3)
    if remaining <= 0:
        result["message"] = _get_quota_exhausted_message()

    return result


def consume_meeting_quota(project_path: str = None) -> Dict[str, Any]:
    """Consume one meeting from monthly quota.

    v4.0: Server-first for tamper-proof counting.
    v5.0: First project bypasses quota entirely.

    Returns:
        dict with used, remaining, notice (if applicable)
    """
    # v5.0: First project gets unlimited meetings
    if project_path:
        try:
            tier = get_project_tier(project_path)
            if tier in ("pro", "first"):
                return {"used": 0, "remaining": 999}
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    # v4.0: Try server consumption first
    try:
        from .sync import SyncState
        from .first_project import _hash_path
        project_hash = None
        if project_path:
            from pathlib import Path as P
            project_hash = _hash_path(str(P(project_path).resolve()))
        license_key = None
        try:
            from .validation import load_license_cache
            cached_lic = load_license_cache()
            if cached_lic and cached_lic.get("key"):
                license_key = cached_lic["key"]
        except (ImportError, OSError):
            pass
        result = SyncState.get().consume_meeting(
            project_hash=project_hash,
            license_key=license_key,
        )
        if result and "used" in result:
            # Mirror to local
            _mirror_meeting_to_local(result)
            remaining = result.get("remaining", 0)
            out = {"used": result["used"], "remaining": remaining}
            if remaining == 1:
                out["notice"] = (
                    "\u26a1 \uc774\ubc88 \ub2ec 1\ud68c \ub0a8\uc558\uc2b5\ub2c8\ub2e4!\n"
                    "Pro \uc5c5\uadf8\ub808\uc774\ub4dc\ub85c \ubb34\uc81c\ud55c \uc0ac\uc6a9\ud558\uc138\uc694."
                )
            elif remaining == 0:
                out["notice"] = (
                    "\U0001f3af \uc774\ubc88 \ub2ec \ubb34\ub8cc Meeting\uc744 \ubaa8\ub450 \uc0ac\uc6a9\ud588\uc2b5\ub2c8\ub2e4.\n"
                    "Pro: \ubb34\uc81c\ud55c Meeting + 8\uba85 \ub9e4\ub2c8\uc800\n"
                    "\u2192 https://polar.sh/clouvel"
                )
            return out
    except (ImportError, OSError, ConnectionError, ValueError):
        pass

    # Fallback: local logic
    path = _get_monthly_meeting_path()
    current_month = datetime.now().strftime("%Y-%m")

    data = {"month": current_month, "used": 0, "history": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("month") != current_month:
                data = {"month": current_month, "used": 0, "history": []}
        except (OSError, json.JSONDecodeError, ValueError):
            data = {"month": current_month, "used": 0, "history": []}

    # Increment usage
    data["used"] = data.get("used", 0) + 1
    data["history"] = data.get("history", []) + [datetime.now().isoformat()]

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    # Queue for next sync
    try:
        from .sync import mark_pending_sync
        mark_pending_sync("meeting_consume", {"used": data["used"], "month": current_month})
    except (ImportError, OSError):
        pass

    # Log event
    try:
        from ..analytics import log_event
        _tier = "unknown"
        try:
            if project_path:
                _tier = get_project_tier(project_path)
        except (OSError, json.JSONDecodeError, ValueError):
            pass
        log_event("meeting_quota_used", {
            "used": data["used"],
            "remaining": FREE_MONTHLY_MEETINGS - data["used"],
            "project_tier": _tier,
            "user_id_hash": get_machine_id()[:8],
        })
    except (ImportError, OSError):
        pass

    remaining = max(0, FREE_MONTHLY_MEETINGS - data["used"])

    result = {
        "used": data["used"],
        "remaining": remaining,
    }

    # Notice after consumption
    if remaining == 1:
        result["notice"] = (
            "\u26a1 \uc774\ubc88 \ub2ec 1\ud68c \ub0a8\uc558\uc2b5\ub2c8\ub2e4!\n"
            "Pro \uc5c5\uadf8\ub808\uc774\ub4dc\ub85c \ubb34\uc81c\ud55c \uc0ac\uc6a9\ud558\uc138\uc694."
        )
    elif remaining == 0:
        result["notice"] = (
            "\U0001f3af \uc774\ubc88 \ub2ec \ubb34\ub8cc Meeting\uc744 \ubaa8\ub450 \uc0ac\uc6a9\ud588\uc2b5\ub2c8\ub2e4.\n"
            "Pro: \ubb34\uc81c\ud55c Meeting + 8\uba85 \ub9e4\ub2c8\uc800\n"
            "\u2192 https://polar.sh/clouvel"
        )

    return result


def _mirror_meeting_to_local(server_result: dict) -> None:
    """Mirror server meeting state to local file."""
    path = _get_monthly_meeting_path()
    current_month = datetime.now().strftime("%Y-%m")
    data = {"month": current_month, "used": server_result.get("used", 0)}
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
