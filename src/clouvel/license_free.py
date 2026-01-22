# -*- coding: utf-8 -*-
"""라이선스 Free 버전 Stub

이 파일은 PyPI 배포용 Free 버전입니다.
Pro 기능은 라이선스 활성화 후 사용 가능합니다.

실제 라이선스 검증 로직은 license.py에 있으며,
해당 파일이 없으면 이 stub이 사용됩니다.
"""

import os
import hashlib
import platform
import uuid
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent


# 라이선스 파일 경로
LICENSE_FILE = Path.home() / ".clouvel-license"


def _get_machine_id() -> str:
    """고유 머신 ID 생성"""
    components = []
    computer_name = os.environ.get("COMPUTERNAME") or platform.node() or "unknown"
    components.append(computer_name)
    components.append(platform.system())
    components.append(platform.machine())

    mac = uuid.getnode()
    if (mac >> 40) % 2 == 0:
        mac_str = ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8))
        components.append(mac_str)

    username = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if username:
        components.append(username)

    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def get_machine_id() -> str:
    """외부에서 사용할 수 있는 머신 ID 조회"""
    return _get_machine_id()


def get_cached_license() -> dict:
    """캐시된 라이선스 조회 (Free 버전은 None)"""
    return None


def verify_license(license_key: str = None, check_machine_id: bool = True) -> dict:
    """라이선스 검증 (Free 버전)"""
    return {
        "valid": False,
        "tier": None,
        "message": "Clouvel Pro 라이선스가 필요합니다.\n\n구매: https://clouvel.lemonsqueezy.com"
    }


def activate_license_cli(license_key: str) -> dict:
    """CLI용 라이선스 활성화 (Free 버전)"""
    return {
        "success": False,
        "message": """Clouvel Pro 라이선스가 필요합니다.

구매: https://clouvel.lemonsqueezy.com

활성화 방법:
1. 위 링크에서 라이선스 구매
2. clouvel activate <LICENSE_KEY> 실행
"""
    }


def get_license_status() -> dict:
    """CLI용 라이선스 상태 확인 (Free 버전)"""
    return {
        "has_license": False,
        "message": "라이선스가 없습니다.\n\n구매: https://clouvel.lemonsqueezy.com"
    }


def deactivate_license_cli() -> dict:
    """CLI용 라이선스 비활성화 (Free 버전)"""
    return {
        "success": True,
        "message": "라이선스가 없습니다."
    }


def get_license_age_days() -> int:
    """라이선스 활성화 후 경과 일수 (Free 버전)"""
    return 0


def require_license(func):
    """기본 라이선스 체크 데코레이터 (Free 버전 - 차단)"""
    async def wrapper(*args, **kwargs):
        return [TextContent(type="text", text="""
# Clouvel Pro 라이선스 필요

이 기능은 Pro 라이선스가 필요합니다.

## 구매
https://clouvel.lemonsqueezy.com

## 가격
- Personal: $19.99/월
- Team 5: $49.99/월
- Team 10: $79.99/월
""")]
    return wrapper


def require_license_premium(func):
    """프리미엄 기능 데코레이터 (Free 버전 - 차단)"""
    async def wrapper(*args, **kwargs):
        return [TextContent(type="text", text="""
# Clouvel Pro 프리미엄 기능

이 기능은 Pro 라이선스 + 7일 경과 후 사용 가능합니다.

## 구매
https://clouvel.lemonsqueezy.com

## 프리미엄 기능
- Error Learning (error_record, error_check, error_learn)
- Ship (테스트→검증→증거 자동화)
- Manager (8명 C-Level 매니저 피드백)
""")]
    return wrapper


def require_team_license(func):
    """Team 라이선스 체크 데코레이터 (Free 버전 - 차단)"""
    async def wrapper(*args, **kwargs):
        return [TextContent(type="text", text="""
# Clouvel Team 라이선스 필요

이 기능은 Team 라이선스가 필요합니다.

## 구매
https://clouvel.lemonsqueezy.com

## Team 기능
- 팀원 초대/관리
- C-Level 역할 커스터마이징
- 팀 에러 패턴 공유
""")]
    return wrapper
