# -*- coding: utf-8 -*-
"""Licensing Validation Module

Machine ID generation, license cache loading/saving, license status calculation.
"""

import os
import json
import hashlib
import platform
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from .core import (
    is_developer,
    DEV_TIER_INFO,
    get_license_path,
    DEFAULT_TIER,
    get_tier_info,
    guess_tier_from_key,
)


# ============================================================
# Machine ID
# ============================================================

def get_machine_id() -> str:
    """Generate unique machine ID."""
    components = []
    computer_name = os.environ.get("COMPUTERNAME") or platform.node() or "unknown"
    components.append(computer_name)
    components.append(platform.system())
    components.append(platform.machine())

    mac = uuid.getnode()
    # MAC 주소가 유효한지 확인 (랜덤 생성된 경우 40번째 비트가 1)
    if mac and (mac >> 40) % 2 == 0:
        mac_str = ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8))
        components.append(mac_str)

    username = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if username:
        components.append(username)

    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


# ============================================================
# Cache 읽기/쓰기
# ============================================================

def load_license_cache() -> Optional[Dict[str, Any]]:
    """Load license data from cache file."""
    license_path = get_license_path()
    if license_path.exists():
        try:
            return json.loads(license_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return None


def save_license_cache(data: Dict[str, Any]) -> bool:
    """Save license data to cache file.

    Returns:
        True if successful, False otherwise.
    """
    license_path = get_license_path()
    try:
        license_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except OSError:
        return False


def delete_license_cache() -> bool:
    """Delete license cache file.

    Returns:
        True if successful or file doesn't exist, False otherwise.
    """
    license_path = get_license_path()
    if license_path.exists():
        try:
            license_path.unlink()
            return True
        except OSError:
            return False
    return True


# ============================================================
# License Status 공통 로직
# ============================================================

PREMIUM_UNLOCK_DAYS = 7


def calculate_license_status(cached: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate license status from cached data.

    공통 반환값 구조를 보장.
    license.py, license_free.py 모두 이 함수 사용 권장.
    """
    # 개발자 자동 Pro 처리
    if is_developer():
        return {
            "has_license": True,
            "tier": "developer",
            "tier_info": DEV_TIER_INFO,
            "license_key": "DEV-MODE",
            "machine_id": get_machine_id(),
            "activated_at": datetime.now().isoformat(),
            "days_since_activation": 999,
            "premium_unlocked": True,
            "premium_unlock_remaining": 0,
            "is_developer": True,
            "message": "[DEV] Developer Mode (Auto Pro)"
        }

    if not cached:
        return {
            "has_license": False,
            "message": "라이선스가 없습니다.\n\n구매: https://polar.sh/clouvel"
        }

    # tier 정보 (기본값: personal)
    tier = cached.get("tier", DEFAULT_TIER)
    tier_info = cached.get("tier_info", get_tier_info(tier))

    # license key (api_client.py 호환: "key" 또는 "license_key")
    license_key = cached.get("license_key") or cached.get("key") or ""

    # 활성화 시간
    activated_at = cached.get("activated_at", "")

    # 경과 일수 계산
    days = 0
    if activated_at:
        try:
            activated_time = datetime.fromisoformat(activated_at)
            days = (datetime.now() - activated_time).days
        except (ValueError, TypeError):
            pass

    # 프리미엄 잠금 해제 (7일 후)
    premium_unlocked = days >= PREMIUM_UNLOCK_DAYS

    return {
        "has_license": True,
        "tier": tier,
        "tier_info": tier_info,
        "license_key": (license_key[:12] + "...") if license_key else "N/A",
        "machine_id": cached.get("machine_id", "unknown"),
        "activated_at": activated_at,
        "days_since_activation": days,
        "premium_unlocked": premium_unlocked,
        "premium_unlock_remaining": max(0, PREMIUM_UNLOCK_DAYS - days),
        "message": "라이선스가 활성화되어 있습니다."
    }


# ============================================================
# License Data 생성
# ============================================================

def create_license_data(license_key: str, tier: str = None) -> Dict[str, Any]:
    """Create license data structure for saving.

    Args:
        license_key: License key string
        tier: Tier name (if None, guess from key pattern)

    Returns:
        License data dict ready to save.
    """
    if tier is None:
        tier = guess_tier_from_key(license_key)

    tier_info = get_tier_info(tier)

    return {
        "key": license_key,  # api_client.py 호환
        "license_key": license_key,  # 기존 호환
        "activated_at": datetime.now().isoformat(),
        "machine_id": get_machine_id(),
        "tier": tier,
        "tier_info": tier_info,
    }
