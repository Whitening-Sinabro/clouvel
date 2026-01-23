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
    """캐시된 라이선스 조회"""
    import json
    if LICENSE_FILE.exists():
        try:
            return json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def verify_license(license_key: str = None, check_machine_id: bool = True) -> dict:
    """라이선스 검증 (Free 버전)"""
    return {
        "valid": False,
        "tier": None,
        "message": "Clouvel Pro 라이선스가 필요합니다.\n\n구매: https://polar.sh/clouvel"
    }


def activate_license_cli(license_key: str) -> dict:
    """CLI용 라이선스 활성화 (Free 버전 → Pro 다운로드)"""
    import json

    if not license_key:
        return {
            "success": False,
            "message": "라이선스 키를 입력하세요."
        }

    # 1. 라이선스 키 저장
    try:
        license_data = {
            "license_key": license_key,
            "activated_at": datetime.now().isoformat(),
            "machine_id": _get_machine_id()
        }
        LICENSE_FILE.write_text(json.dumps(license_data, indent=2), encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "message": f"라이선스 저장 실패: {e}"
        }

    # 2. Pro 모듈 다운로드
    try:
        from .pro_downloader import install_pro
        result = install_pro(license_key=license_key)

        if result["success"]:
            installed = ", ".join(result["installed"])
            return {
                "success": True,
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
    """CLI용 라이선스 상태 확인"""
    cached = get_cached_license()
    if cached:
        return {
            "has_license": True,
            "license_key": cached.get("license_key", "")[:12] + "...",
            "activated_at": cached.get("activated_at"),
            "message": "라이선스가 활성화되어 있습니다."
        }
    return {
        "has_license": False,
        "message": "라이선스가 없습니다.\n\n구매: https://polar.sh/clouvel"
    }


def deactivate_license_cli() -> dict:
    """CLI용 라이선스 비활성화"""
    if LICENSE_FILE.exists():
        try:
            LICENSE_FILE.unlink()
            return {
                "success": True,
                "message": "라이선스가 비활성화되었습니다."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"라이선스 파일 삭제 실패: {e}"
            }
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
https://polar.sh/clouvel

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
