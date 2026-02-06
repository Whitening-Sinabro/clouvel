# -*- coding: utf-8 -*-
"""라이선스 Free 버전 Stub

이 파일은 PyPI 배포용 Free 버전입니다.
Pro 기능은 라이선스 활성화 후 사용 가능합니다.

실제 라이선스 검증 로직은 license.py에 있으며,
해당 파일이 없으면 이 stub이 사용됩니다.

NOTE: 공통 로직은 license_common.py에서 가져옴.
      인터페이스 변경 시 license.py와 동기화 필수.
"""

from mcp.types import TextContent

# 공통 모듈에서 import
from .license_common import (
    get_license_path,
    get_machine_id,
    get_tier_info,
    guess_tier_from_key,
    load_license_cache,
    save_license_cache,
    delete_license_cache,
    calculate_license_status,
    create_license_data,
    is_feature_available,
    register_project,
    get_project_count,
    DEFAULT_TIER,
    TIER_INFO,
    PRO_ONLY_FEATURES,
    FREE_PROJECT_LIMIT,
)


def get_cached_license() -> dict:
    """캐시된 라이선스 조회 (하위 호환성)"""
    return load_license_cache()


def verify_license(license_key: str = None, check_machine_id: bool = True) -> dict:
    """라이선스 검증 (Free 버전)"""
    return {
        "valid": False,
        "tier": None,
        "message": "Clouvel Pro 라이선스가 필요합니다.\n\n구매: https://polar.sh/clouvel"
    }


def activate_license_cli(license_key: str) -> dict:
    """CLI용 라이선스 활성화 (Free 버전 → Pro 다운로드)"""
    if not license_key:
        return {
            "success": False,
            "message": "라이선스 키를 입력하세요."
        }

    # 1. 라이선스 키 저장 (공통 모듈 사용)
    try:
        license_data = create_license_data(license_key)
        if not save_license_cache(license_data):
            return {
                "success": False,
                "message": "라이선스 저장 실패"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"라이선스 저장 실패: {e}"
        }

    # 2. Pro 모듈 다운로드
    try:
        from .pro_downloader import install_pro
        result = install_pro(license_key=license_key)

        tier_info = license_data.get("tier_info", get_tier_info(DEFAULT_TIER))

        if result["success"]:
            installed = ", ".join(result["installed"])
            return {
                "success": True,
                "tier_info": tier_info,
                "machine_id": license_data.get("machine_id", "unknown"),
                "product": "Clouvel Pro",
                "message": f"""Clouvel Pro 활성화 완료!

설치된 모듈: {installed}
버전: {result.get('version', 'unknown')}

Pro 기능을 사용할 수 있습니다."""
            }
        else:
            failed = [f["module"] for f in result.get("failed", [])]
            return {
                "success": False,
                "message": f"일부 모듈 설치 실패: {failed}\n라이선스 키를 확인하세요."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Pro 다운로드 실패: {e}\n라이선스 키가 유효한지 확인하세요."
        }


def get_license_status() -> dict:
    """CLI용 라이선스 상태 확인

    license.py와 동일한 반환값 유지 필요:
    - tier_info: 티어 정보 (name, price, seats)
    - days_since_activation: 활성화 후 경과 일수
    - premium_unlocked: 프리미엄 기능 잠금 해제 여부
    - premium_unlock_remaining: 잠금 해제까지 남은 일수
    """
    cached = load_license_cache()
    return calculate_license_status(cached)


def deactivate_license_cli() -> dict:
    """CLI용 라이선스 비활성화"""
    if delete_license_cache():
        return {
            "success": True,
            "message": "라이선스가 비활성화되었습니다."
        }
    return {
        "success": False,
        "message": "라이선스 파일 삭제 실패"
    }


def get_license_age_days() -> int:
    """라이선스 활성화 후 경과 일수 (Free 버전)"""
    status = get_license_status()
    return status.get("days_since_activation", 0)


def require_license(func):
    """기본 라이선스 체크 데코레이터 (Free 버전 - 차단)"""
    async def wrapper(*args, **kwargs):
        return [TextContent(type="text", text="""
# Clouvel Pro 라이선스 필요

이 기능은 Pro 라이선스가 필요합니다.

## 구매
https://polar.sh/clouvel

## 가격
- Monthly: $7.99/mo ($1 first month with code FIRST1)
- Annual: $23.99/yr (code LAUNCH70) - save 70%
""")]
    return wrapper


def require_license_premium(func):
    """프리미엄 기능 데코레이터 (Free 버전 - 차단)"""
    async def wrapper(*args, **kwargs):
        return [TextContent(type="text", text="""
# Clouvel Pro 프리미엄 기능

이 기능은 Pro 라이선스 + 7일 경과 후 사용 가능합니다.

## 구매
https://polar.sh/clouvel

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
https://polar.sh/clouvel

## Team 기능
- 팀원 초대/관리
- C-Level 역할 커스터마이징
- 팀 에러 패턴 공유
""")]
    return wrapper
