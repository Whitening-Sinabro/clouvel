# -*- coding: utf-8 -*-
"""Tier Service — Single source of truth for user tier resolution.

Replaces duplicated _is_pro() logic in:
- tool_dispatch.py (_is_pro, _get_list_tools_tier, _get_call_tool_tier)
- utils/entitlements.py (can_use_pro)
- tools/meeting/core.py (_can_use_pro)
- tools/proactive.py (_can_use_pro)
"""

from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    FIRST = "first"    # First project (Pro feature access via reverse trial)
    TRIAL = "trial"    # 7-day full trial
    PRO = "pro"        # Paid license
    DEV = "dev"        # Developer mode

    def is_pro_equivalent(self) -> bool:
        """Paid Pro-level access? (license/trial/developer)"""
        return self in (Tier.PRO, Tier.TRIAL, Tier.DEV)

    def is_first_or_above(self) -> bool:
        """First project or above? (KB, meeting, manager access)"""
        return self in (Tier.FIRST, Tier.PRO, Tier.TRIAL, Tier.DEV)


def resolve_tier(project_path: Optional[str] = None) -> Tier:
    """Resolve user tier — this function is the single source of truth.

    Priority:
    1. Developer mode (env var or clouvel repo detection) → DEV
    2. Valid license cache → PRO
    3. Active full trial → TRIAL
    4. First project → FIRST
    5. Default → FREE
    """
    # Direct licensing imports (Phase 4: license_common shim removed)
    try:
        from ..licensing.core import is_developer
        from ..licensing.validation import load_license_cache
        from ..licensing.trial import is_full_trial_active
        from ..licensing.first_project import get_project_tier
    except ImportError:
        return Tier.FREE

    # 1. Developer
    if is_developer():
        return Tier.DEV

    # 2. License
    cached = load_license_cache()
    if cached and cached.get("tier"):
        return Tier.PRO

    # 3. Trial
    if is_full_trial_active():
        return Tier.TRIAL

    # 4. First project
    if project_path:
        tier = get_project_tier(project_path)
        if tier in ("pro", "first"):
            return Tier.FIRST

    # 5. Default
    return Tier.FREE


def is_pro(project_path: Optional[str] = None) -> bool:
    """Convenience: does user have paid Pro access? (license/trial/dev)

    Returns True ONLY for paid Pro users.
    'first' project without license = False (Free limitations apply).
    """
    return resolve_tier(project_path).is_pro_equivalent()


def can_use_pro(project_path: Optional[str] = None) -> bool:
    """Convenience: can user use Pro features? (first project OR paid Pro)

    Returns True for first project AND paid users.
    """
    return resolve_tier(project_path).is_first_or_above()


def get_tool_filter_tier(project_path: Optional[str] = None) -> str:
    """Registry filtering tier: 'pro' or 'free'.

    Only developer/license/trial → 'pro'.
    Everyone else (including 'first' project) → 'free'.
    Free users see 10 Core tools only.
    """
    return "pro" if is_pro(project_path) else "free"
