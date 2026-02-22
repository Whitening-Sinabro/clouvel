# -*- coding: utf-8 -*-
"""Quota Service — Business logic for rate limits and feature quotas.

Extracts quota/limit logic from tool_dispatch.py _wrap_* functions.
"""

from dataclasses import dataclass
from typing import Optional

# Constants previously scattered in tool_dispatch.py
FREE_ERROR_LIMIT = 5
FREE_PERSPECTIVES_MANAGERS = 2
FREE_PERSPECTIVES_QUESTIONS = 1
PRO_DEFAULT_PERSPECTIVES_MANAGERS = 4
PRO_DEFAULT_PERSPECTIVES_QUESTIONS = 2


@dataclass
class QuotaResult:
    allowed: bool
    message: str = ""
    remaining: int = -1  # -1 = unlimited


def check_error_view_quota(project_path: str) -> QuotaResult:
    """Check how many error records a Free user can view.

    Replaces _apply_free_error_limit counting logic in tool_dispatch.py.
    """
    total_errors = 0
    try:
        from pathlib import Path as _P
        log_file = _P(project_path) / ".claude" / "errors" / "error_log.jsonl"
        if log_file.exists():
            total_errors = sum(1 for _ in open(log_file, "r", encoding="utf-8"))
    except Exception:
        pass

    if total_errors > FREE_ERROR_LIMIT:
        return QuotaResult(
            allowed=True,  # Still allowed, just limited
            message=(
                f"Checked **{FREE_ERROR_LIMIT} of {total_errors}** error records (Free limit).\n"
                f"Older errors may contain relevant patterns.\n\n"
                f"Unlock full error history with Pro → `license_status(action=\"trial\")`"
            ),
            remaining=FREE_ERROR_LIMIT,
        )
    return QuotaResult(allowed=True, remaining=total_errors)


def check_kb_access(project_path: str) -> QuotaResult:
    """Check KB write access for current tier.

    Replaces the duplicated KB trial check in _wrap_record_decision
    and _wrap_record_location.
    """
    try:
        from ..licensing.core import is_developer
        from ..licensing.quotas import is_kb_trial_active, start_kb_trial
        if is_developer():
            return QuotaResult(allowed=True)
        # Start trial on first use (no-op for first project)
        start_kb_trial(project_path)
        if not is_kb_trial_active(project_path):
            from ..messages.en import CAN_CODE_KB_TRIAL_EXPIRED
            return QuotaResult(
                allowed=False,
                message=CAN_CODE_KB_TRIAL_EXPIRED.format(decision_count="N/A"),
            )
    except ImportError:
        pass
    return QuotaResult(allowed=True)


def check_meeting_quota(project_path: str) -> QuotaResult:
    """Check meeting quota. Facade to licensing.quotas.check_meeting_quota."""
    try:
        from ..licensing.quotas import check_meeting_quota as _check
        result = _check(project_path)
        return QuotaResult(
            allowed=result.get("allowed", True),
            message=result.get("message", ""),
            remaining=result.get("remaining", -1),
        )
    except ImportError:
        return QuotaResult(allowed=True)


def get_perspectives_limits(project_path: Optional[str] = None) -> dict:
    """Get max managers/questions for quick_perspectives.

    Replaces hardcoded values in _wrap_quick_perspectives.
    """
    from .tier import is_pro
    if is_pro(project_path or ""):
        return {
            "max_managers": PRO_DEFAULT_PERSPECTIVES_MANAGERS,
            "max_questions": PRO_DEFAULT_PERSPECTIVES_QUESTIONS,
        }
    return {
        "max_managers": FREE_PERSPECTIVES_MANAGERS,
        "max_questions": FREE_PERSPECTIVES_QUESTIONS,
    }
