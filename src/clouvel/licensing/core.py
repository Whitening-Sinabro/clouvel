# -*- coding: utf-8 -*-
"""Licensing Core Module

Developer detection, paths, tier defaults.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any


# ============================================================
# 개발자 감지
# ============================================================

def is_developer() -> bool:
    """Check if running as Clouvel developer.

    개발자 조건:
    1. CLOUVEL_DEV=1 환경변수 설정
    2. 또는 소스 코드가 clouvel git 저장소 내에 있는 경우
    """
    # 환경변수로 명시적 개발자 모드
    if os.environ.get("CLOUVEL_DEV") == "1":
        return True

    # git remote 확인 (소스 파일 위치 기준)
    # __file__ 기반으로 체크해서 MCP 서버 cwd와 무관하게 동작
    try:
        source_dir = Path(__file__).parent.parent
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(source_dir)
        )
        if result.returncode == 0:
            output = result.stdout.lower()
            if "clouvel" in output and ("github.com" in output or "origin" in output):
                return True
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass

    return False


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
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:  # Unix
        base = Path.home()

    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "license.json"


# ============================================================
# Tier 기본값
# ============================================================

DEFAULT_TIER = "personal"

TIER_INFO = {
    "personal": {"name": "Personal", "price": "$7.99/mo", "seats": 1},
    "team": {"name": "Team", "price": "$79/mo", "seats": 10},
    "enterprise": {"name": "Enterprise", "price": "$199/mo", "seats": 999},
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
