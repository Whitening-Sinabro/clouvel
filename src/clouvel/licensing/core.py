# -*- coding: utf-8 -*-
"""Licensing Core Module

Developer detection, paths, tier defaults.
"""

import os
from pathlib import Path
from typing import Dict, Any


# ============================================================
# 개발자 감지
# ============================================================

def is_developer(project_path: str = None) -> bool:
    """Check if running as Clouvel developer.

    Delegates to utils.entitlements.is_developer() for MCP-safe detection.
    project_path parameter added for backward compat (default None).
    """
    try:
        from ..utils.entitlements import is_developer as _ent_is_developer
        return _ent_is_developer(project_path)
    except ImportError:
        # Fallback: env-only check
        return os.environ.get("CLOUVEL_DEV") == "1"


DEV_TIER_INFO = {
    "name": "Developer",
    "price": "$0 (Dev)",
    "seats": 999,
}


# ============================================================
# 경로 설정
# ============================================================

def get_license_path() -> Path:
    """Get license file path: ~/.clouvel/license.json

    api_client.py, trial.py와 동일한 경로 사용.
    """
    from .paths import get_clouvel_file
    return get_clouvel_file("license.json")


# ============================================================
# Tier 기본값
# ============================================================

DEFAULT_TIER = "personal"

TIER_INFO = {
    "personal": {"name": "Personal", "price": "free", "seats": 1},
    "team": {"name": "Team", "price": "free", "seats": 10},
    "enterprise": {"name": "Enterprise", "price": "free", "seats": 999},
}


def get_tier_info(tier: str) -> Dict[str, Any]:
    """Get tier info with fallback to Personal."""
    return TIER_INFO.get(tier, TIER_INFO[DEFAULT_TIER])


def guess_tier_from_key(license_key: str) -> str:
    """Guess tier from license key pattern."""
    if not license_key:
        return DEFAULT_TIER
    if license_key.startswith("TEAM"):
        return "team"
    if license_key.startswith("ENT"):
        return "enterprise"
    return DEFAULT_TIER
