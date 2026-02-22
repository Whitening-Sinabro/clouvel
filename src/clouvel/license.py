# -*- coding: utf-8 -*-
"""라이선스 검증 및 활성화 (Lemon Squeezy 연동)

v4: Heartbeat 시스템 추가
- 24시간마다 서버와 통신하여 라이선스 상태 확인
- 오프라인 유예 기간: 3일
- 환불 감지 시 즉시 기능 차단
"""

import os
import sys
import json
import hashlib
import platform
import uuid
import requests
from pathlib import Path
from datetime import datetime, timedelta
from mcp.types import TextContent

# 공통 모듈에서 import (경로/기본값 통일)
from .license_common import (
    get_license_path,
    get_machine_id as common_get_machine_id,
    get_tier_info,
    TIER_INFO as COMMON_TIER_INFO,
    DEFAULT_TIER,
    is_developer,
    DEV_TIER_INFO,
)

# 라이선스 파일 경로 (공통 모듈 사용)
LICENSE_FILE = get_license_path()

# Lemon Squeezy API
LEMONSQUEEZY_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"
LEMONSQUEEZY_ACTIVATE_URL = "https://api.lemonsqueezy.com/v1/licenses/activate"

# 환불 차단 확인 API (Cloudflare Workers)
# 배포 후 실제 URL로 교체 필요
REVOKE_CHECK_URL = os.environ.get(
    "CLOUVEL_REVOKE_CHECK_URL",
    "https://clouvel-api.vnddns999.workers.dev/api/v2/check"
)

# 라이선스 티어 (variant_id로 매핑)
TIERS = {
    "personal": {"name": "Personal", "price": "$29", "seats": 1},
    "team": {"name": "Team", "price": "$79", "seats": 10},
    "enterprise": {"name": "Enterprise", "price": "$199", "seats": -1},
}

# 캐시 유효 기간 (3일로 단축 - 보안 강화)
CACHE_VALID_DAYS = 3

# 프리미엄 기능 잠금 해제 기간 (7일)
PREMIUM_UNLOCK_DAYS = 7

# 개발 모드 (표준 is_developer() 사용)
# - 온라인 검증 스킵
# - 7일 잠금 해제
# - 테스트 라이선스로 모든 기능 사용 가능
DEV_MODE = is_developer()

# Heartbeat 설정
HEARTBEAT_URL = os.environ.get(
    "CLOUVEL_HEARTBEAT_URL",
    "https://clouvel-api.vnddns999.workers.dev/api/v2/heartbeat"
)
HEARTBEAT_FILE = Path.home() / ".clouvel-heartbeat"
HEARTBEAT_INTERVAL_SECONDS = 24 * 60 * 60  # 24시간
OFFLINE_GRACE_DAYS = 3  # 오프라인 유예 기간


def _hash_key(key: str) -> str:
    """라이선스 키 해시"""
    return hashlib.sha256(key.encode()).hexdigest()[:16]


# 공통 모듈의 get_machine_id 사용 (중복 제거)
_get_machine_id = common_get_machine_id
get_machine_id = common_get_machine_id


def get_cached_license() -> dict:
    """외부에서 사용할 수 있는 캐시된 라이선스 조회"""
    return _load_cached_license()


# ============================================================
# Heartbeat 시스템
# ============================================================

def _load_heartbeat_cache() -> dict:
    """Heartbeat 캐시 로드"""
    if not HEARTBEAT_FILE.exists():
        return None

    try:
        data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
        return data
    except Exception:
        return None


def _save_heartbeat_cache(data: dict):
    """Heartbeat 캐시 저장"""
    HEARTBEAT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def send_heartbeat(license_key: str = None, force: bool = False) -> dict:
    """서버에 Heartbeat 전송

    Args:
        license_key: 라이선스 키 (없으면 캐시에서)
        force: 강제 전송 (interval 무시)

    Returns:
        {
            "success": True/False,
            "status": "valid"/"revoked"/"invalid"/"error",
            "message": "...",
            "next_heartbeat": datetime (다음 heartbeat 시간)
        }
    """
    # 라이선스 키 확인
    key = license_key or os.environ.get("CLOUVEL_LICENSE")
    cached_license = _load_cached_license()

    if not key and cached_license:
        key = cached_license.get("license_key")

    if not key:
        return {
            "success": False,
            "status": "no_license",
            "message": "라이선스 키가 없습니다."
        }

    # 마지막 heartbeat 확인 (강제가 아닌 경우)
    if not force:
        heartbeat_cache = _load_heartbeat_cache()
        if heartbeat_cache:
            last_heartbeat = heartbeat_cache.get("last_heartbeat")
            if last_heartbeat:
                try:
                    last_time = datetime.fromisoformat(last_heartbeat)
                    elapsed = (datetime.now() - last_time).total_seconds()
                    if elapsed < HEARTBEAT_INTERVAL_SECONDS:
                        remaining = HEARTBEAT_INTERVAL_SECONDS - elapsed
                        return {
                            "success": True,
                            "status": "cached",
                            "message": f"다음 heartbeat까지 {int(remaining / 3600)}시간 남음",
                            "next_heartbeat": last_time + timedelta(seconds=HEARTBEAT_INTERVAL_SECONDS),
                            "cached": True
                        }
                except Exception:
                    pass

    # 서버에 Heartbeat 전송
    machine_id = _get_machine_id()

    try:
        response = requests.post(
            HEARTBEAT_URL,
            json={
                "license_key": key,
                "machine_id": machine_id,
                "client_version": "4.0.0"  # v4: Heartbeat 추가
            },
            timeout=15
        )

        data = response.json()

        if response.status_code == 200 and data.get("status") == "valid":
            # 성공 - 캐시 업데이트
            now = datetime.now()
            _save_heartbeat_cache({
                "last_heartbeat": now.isoformat(),
                "server_timestamp": data.get("timestamp"),
                "tier": data.get("tier"),
                "features": data.get("features", {})
            })

            next_heartbeat = now + timedelta(seconds=HEARTBEAT_INTERVAL_SECONDS)
            return {
                "success": True,
                "status": "valid",
                "message": "Heartbeat 성공",
                "next_heartbeat": next_heartbeat,
                "tier": data.get("tier"),
                "features": data.get("features", {})
            }

        elif data.get("status") == "revoked":
            # 환불됨 - 로컬 캐시 삭제
            if LICENSE_FILE.exists():
                LICENSE_FILE.unlink()
            if HEARTBEAT_FILE.exists():
                HEARTBEAT_FILE.unlink()

            return {
                "success": False,
                "status": "revoked",
                "message": data.get("message", "라이선스가 취소되었습니다."),
                "revoked_at": data.get("revoked_at")
            }

        elif data.get("status") == "seat_limit_exceeded":
            return {
                "success": False,
                "status": "seat_limit",
                "message": data.get("message", "기기 수 제한 초과"),
                "current_machines": data.get("current_machines"),
                "max_machines": data.get("max_machines")
            }

        else:
            return {
                "success": False,
                "status": data.get("status", "error"),
                "message": data.get("message", "Heartbeat 실패")
            }

    except requests.exceptions.Timeout:
        return _handle_offline_heartbeat("연결 시간 초과")
    except requests.exceptions.ConnectionError:
        return _handle_offline_heartbeat("네트워크 연결 실패")
    except Exception as e:
        return _handle_offline_heartbeat(f"오류: {str(e)}")


def _handle_offline_heartbeat(error_message: str) -> dict:
    """오프라인 상태에서 Heartbeat 처리 (유예 기간 확인)"""
    heartbeat_cache = _load_heartbeat_cache()

    if not heartbeat_cache:
        # 캐시 없음 - 한 번도 heartbeat한 적 없음
        return {
            "success": False,
            "status": "offline_no_cache",
            "message": f"{error_message}\n\n첫 heartbeat가 필요합니다. 인터넷 연결 후 다시 시도하세요."
        }

    last_heartbeat = heartbeat_cache.get("last_heartbeat")
    if not last_heartbeat:
        return {
            "success": False,
            "status": "offline_no_cache",
            "message": error_message
        }

    try:
        last_time = datetime.fromisoformat(last_heartbeat)
        offline_days = (datetime.now() - last_time).days

        if offline_days <= OFFLINE_GRACE_DAYS:
            # 유예 기간 내 - 허용
            remaining_days = OFFLINE_GRACE_DAYS - offline_days
            return {
                "success": True,
                "status": "offline_grace",
                "message": f"오프라인 모드 ({remaining_days}일 유예 남음)",
                "offline": True,
                "grace_remaining_days": remaining_days
            }
        else:
            # 유예 기간 초과 - 차단
            return {
                "success": False,
                "status": "offline_expired",
                "message": f"오프라인 유예 기간({OFFLINE_GRACE_DAYS}일) 초과.\n\n"
                          f"마지막 연결: {offline_days}일 전\n"
                          f"인터넷 연결 후 heartbeat를 전송하세요."
            }
    except Exception:
        return {
            "success": False,
            "status": "error",
            "message": error_message
        }


def check_heartbeat_required() -> dict:
    """Heartbeat가 필요한지 확인

    Returns:
        {
            "required": True/False,
            "reason": "...",
            "last_heartbeat": datetime or None,
            "offline_days": int or None
        }
    """
    heartbeat_cache = _load_heartbeat_cache()

    if not heartbeat_cache:
        return {
            "required": True,
            "reason": "첫 heartbeat 필요",
            "last_heartbeat": None
        }

    last_heartbeat = heartbeat_cache.get("last_heartbeat")
    if not last_heartbeat:
        return {
            "required": True,
            "reason": "heartbeat 기록 없음",
            "last_heartbeat": None
        }

    try:
        last_time = datetime.fromisoformat(last_heartbeat)
        elapsed = (datetime.now() - last_time).total_seconds()

        if elapsed >= HEARTBEAT_INTERVAL_SECONDS:
            return {
                "required": True,
                "reason": f"마지막 heartbeat: {int(elapsed / 3600)}시간 전",
                "last_heartbeat": last_time
            }

        return {
            "required": False,
            "reason": "최근 heartbeat 유효",
            "last_heartbeat": last_time,
            "next_heartbeat_in": HEARTBEAT_INTERVAL_SECONDS - elapsed
        }
    except Exception:
        return {
            "required": True,
            "reason": "heartbeat 파싱 오류",
            "last_heartbeat": None
        }


def _check_revoked(license_key: str) -> dict:
    """환불로 차단된 라이선스인지 확인 (Cloudflare Workers KV)"""
    try:
        response = requests.get(
            REVOKE_CHECK_URL,
            params={"key": license_key},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("revoked"):
                return {
                    "revoked": True,
                    "revoked_at": data.get("revoked_at"),
                    "reason": data.get("reason", "refund")
                }
        return {"revoked": False}

    except Exception:
        # 차단 확인 실패 시 통과 (가용성 우선)
        return {"revoked": False}


def _validate_online(license_key: str, instance_name: str = None) -> dict:
    """Lemon Squeezy API로 온라인 검증"""
    try:
        response = requests.post(
            LEMONSQUEEZY_VALIDATE_URL,
            json={
                "license_key": license_key,
                "instance_name": instance_name or "clouvel-pro"
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("valid"):
                license_data = data.get("license_key", {})
                meta = data.get("meta", {})

                # 상품 이름에서 티어 추출
                product_name = meta.get("product_name", "").lower()
                if "team" in product_name:
                    tier = "team"
                elif "enterprise" in product_name:
                    tier = "enterprise"
                else:
                    tier = "personal"

                return {
                    "valid": True,
                    "tier": tier,
                    "tier_info": TIERS[tier],
                    "license_data": license_data,
                    "instance_id": data.get("instance", {}).get("id"),
                    "message": f"✅ {TIERS[tier]['name']} 라이선스 검증됨"
                }
            else:
                return {
                    "valid": False,
                    "tier": None,
                    "message": data.get("error", "라이선스가 유효하지 않습니다.")
                }
        else:
            return {
                "valid": False,
                "tier": None,
                "message": f"API 오류: {response.status_code}"
            }
    except requests.exceptions.Timeout:
        return {"valid": None, "message": "연결 시간 초과"}
    except requests.exceptions.ConnectionError:
        return {"valid": None, "message": "네트워크 연결 실패"}
    except Exception as e:
        return {"valid": None, "message": f"검증 오류: {str(e)}"}


def _load_cached_license() -> dict:
    """로컬 캐시에서 라이선스 로드"""
    if not LICENSE_FILE.exists():
        return None

    try:
        data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))

        # 캐시 유효성 확인
        cached_at = data.get("validated_at")
        if cached_at:
            cached_time = datetime.fromisoformat(cached_at)
            if datetime.now() - cached_time < timedelta(days=CACHE_VALID_DAYS):
                return data

        return data  # 캐시 만료되어도 키는 반환
    except Exception:
        return None


def _save_license_cache(license_key: str, tier: str, tier_info: dict, instance_id: str = None, preserve_activated_at: bool = True):
    """라이선스 캐시 저장 (activated_at, machine_id 보존)"""
    # 기존 캐시에서 activated_at 보존
    existing_activated_at = None
    existing_machine_id = None

    if preserve_activated_at and LICENSE_FILE.exists():
        try:
            existing = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
            # 같은 키인 경우에만 보존
            if existing.get("key_hash") == _hash_key(license_key):
                existing_activated_at = existing.get("activated_at")
                existing_machine_id = existing.get("machine_id")
        except Exception:
            pass

    # 현재 머신 ID
    current_machine_id = _get_machine_id()

    license_data = {
        "license_key": license_key,
        "tier": tier,
        "tier_info": tier_info,
        "instance_id": instance_id,
        "key_hash": _hash_key(license_key),
        "machine_id": existing_machine_id or current_machine_id,
        "validated_at": datetime.now().isoformat(),
        "activated_at": existing_activated_at or datetime.now().isoformat()
    }
    LICENSE_FILE.write_text(json.dumps(license_data, indent=2), encoding="utf-8")


def verify_license(license_key: str = None, check_machine_id: bool = True) -> dict:
    """라이선스 검증 (온라인 우선, 오프라인 캐시 폴백)

    Args:
        license_key: 라이선스 키 (없으면 환경변수/캐시 사용)
        check_machine_id: 머신 ID 검증 여부
    """
    # 0. 개발자 자동 Pro 처리
    if is_developer():
        return {
            "valid": True,
            "tier": "developer",
            "tier_info": DEV_TIER_INFO,
            "message": "🔧 개발자 모드 (자동 Pro 활성화)",
            "is_developer": True,
            "dev_mode": True
        }

    # 1. 키 획득 (인자 > 환경변수 > 캐시)
    key = license_key or os.environ.get("CLOUVEL_LICENSE")
    cached = _load_cached_license()

    if not key and cached:
        key = cached.get("license_key")

    if not key:
        return {
            "valid": False,
            "tier": None,
            "message": "라이선스 키가 없습니다. activate_license로 활성화하세요."
        }

    # DEV_MODE: 캐시만 사용, 온라인 검증 스킵
    if DEV_MODE and cached and cached.get("tier"):
        tier = cached["tier"]
        tier_info = cached.get("tier_info") or TIERS.get(tier, TIERS["personal"])
        return {
            "valid": True,
            "tier": tier,
            "tier_info": tier_info,
            "message": f"🔧 {tier_info['name']} 라이선스 (DEV MODE)",
            "dev_mode": True
        }

    # 1.5. 환불 차단 확인 (먼저 체크)
    revoke_check = _check_revoked(key)
    if revoke_check.get("revoked"):
        # 로컬 캐시 삭제
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink()
        return {
            "valid": False,
            "tier": None,
            "message": f"❌ 라이선스가 환불로 차단되었습니다. ({revoke_check.get('revoked_at', 'N/A')})",
            "revoked": True
        }

    # 1.6. 머신 ID 검증 (캐시된 machine_id와 현재 machine_id 비교)
    if check_machine_id and cached:
        cached_machine_id = cached.get("machine_id")
        current_machine_id = _get_machine_id()

        if cached_machine_id and cached_machine_id != current_machine_id:
            return {
                "valid": False,
                "tier": None,
                "message": f"❌ 이 라이선스는 다른 기기에서 활성화되었습니다.\n\n"
                          f"등록된 기기: `{cached_machine_id[:8]}...`\n"
                          f"현재 기기: `{current_machine_id[:8]}...`\n\n"
                          f"다른 기기에서 사용하려면:\n"
                          f"1. Team/Enterprise로 업그레이드\n"
                          f"2. 기존 기기에서 비활성화 후 재활성화",
                "machine_mismatch": True
            }

    # 2. 온라인 검증 시도
    online_result = _validate_online(key)

    # 온라인 검증 성공
    if online_result.get("valid") is True:
        # 캐시 업데이트
        _save_license_cache(
            key,
            online_result["tier"],
            online_result["tier_info"],
            online_result.get("instance_id")
        )
        return online_result

    # 온라인 검증 실패 (명확히 invalid) - 캐시 폴백 시도
    if online_result.get("valid") is False:
        # 캐시가 있으면 폴백 (테스트 라이선스 지원)
        if cached and cached.get("tier"):
            tier = cached["tier"]
            tier_info = cached.get("tier_info") or TIERS.get(tier, TIERS["personal"])
            return {
                "valid": True,
                "tier": tier,
                "tier_info": tier_info,
                "message": f"✅ {tier_info['name']} 라이선스 (오프라인 캐시)",
                "offline": True
            }
        return online_result

    # 3. 네트워크 오류 시 캐시 폴백
    if cached and cached.get("tier"):
        tier = cached["tier"]
        tier_info = cached.get("tier_info") or TIERS.get(tier, TIERS["personal"])
        return {
            "valid": True,
            "tier": tier,
            "tier_info": tier_info,
            "message": f"✅ {tier_info['name']} 라이선스 (오프라인 캐시)",
            "offline": True
        }

    return {
        "valid": False,
        "tier": None,
        "message": online_result.get("message", "라이선스 검증 실패")
    }


async def activate_license(license_key: str) -> list[TextContent]:
    """라이선스 활성화 (Lemon Squeezy 온라인 검증)"""

    if not license_key or not license_key.strip():
        return [TextContent(type="text", text="""
# ❌ 라이선스 키를 입력하세요

## 사용법
```
activate_license(license_key="YOUR-LICENSE-KEY")
```

## 구매
https://clouvel.lemonsqueezy.com
""")]

    # 현재 머신 ID 생성
    machine_id = _get_machine_id()

    # Lemon Squeezy API로 활성화 (activate는 instance를 생성)
    # instance_name에 machine_id를 사용하여 기기별 구분
    try:
        response = requests.post(
            LEMONSQUEEZY_ACTIVATE_URL,
            json={
                "license_key": license_key.strip(),
                "instance_name": f"clouvel-{machine_id}"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("activated") or data.get("valid"):
                meta = data.get("meta", {})
                instance = data.get("instance", {})

                # 티어 추출
                product_name = meta.get("product_name", "").lower()
                if "team" in product_name:
                    tier = "team"
                elif "enterprise" in product_name:
                    tier = "enterprise"
                else:
                    tier = "personal"

                tier_info = TIERS[tier]

                # 캐시 저장 (machine_id 포함)
                _save_license_cache(
                    license_key.strip(),
                    tier,
                    tier_info,
                    instance.get("id"),
                    preserve_activated_at=False  # 새 활성화이므로 덮어쓰기
                )

                seats_text = f"{tier_info['seats']}대" if tier_info['seats'] > 0 else "무제한"

                return [TextContent(type="text", text=f"""
# ✅ 라이선스 활성화 완료

## 정보
- **티어**: {tier_info['name']}
- **허용 기기**: {seats_text}
- **현재 기기**: `{machine_id[:8]}...`
- **상품**: {meta.get('product_name', 'Clouvel Pro')}
- **활성화**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🔒 기기 바인딩

이 라이선스는 현재 기기에 바인딩됩니다.
- Personal: 1대의 기기에서만 사용 가능
- Team: 최대 10대 기기에서 사용 가능
- Enterprise: 무제한 기기

다른 기기에서 사용하려면 기존 기기를 해제하거나 상위 티어로 업그레이드하세요.

## ⏳ 7일 잠금 정책

프리미엄 기능은 **활성화 후 7일**이 지나야 사용할 수 있습니다.

### 지금 사용 가능 (Day 1-7)
- `watch_logs` - 로그 감시 설정
- `check_logs` - 로그 체크

### 7일 후 사용 가능 (Day 8+)
- `install_shovel` - Shovel 설치
- `sync_commands` - 커맨드 동기화
- `log_error`, `analyze_error`, `add_prevention_rule`, `get_error_summary`

**7일 후 모든 기능이 잠금 해제됩니다!**
""")]
            else:
                error_msg = data.get("error", "라이선스가 유효하지 않습니다.")
                return [TextContent(type="text", text=f"""
# ❌ 라이선스 활성화 실패

**오류**: {error_msg}

## 확인사항
- 라이선스 키가 정확한지 확인
- 활성화 횟수 제한 확인 (Personal: 1회)

## 구매
https://clouvel.lemonsqueezy.com
""")]

    except requests.exceptions.Timeout:
        return [TextContent(type="text", text="""
# ❌ 연결 시간 초과

Lemon Squeezy 서버에 연결할 수 없습니다.
인터넷 연결을 확인하고 다시 시도하세요.
""")]
    except requests.exceptions.ConnectionError:
        return [TextContent(type="text", text="""
# ❌ 네트워크 오류

인터넷 연결을 확인하세요.
""")]
    except Exception as e:
        return [TextContent(type="text", text=f"""
# ❌ 활성화 오류

{str(e)}

문제가 지속되면 support@clouvel.dev로 문의하세요.
""")]


def get_license_age_days() -> int:
    """라이선스 활성화 후 경과 일수 반환"""
    cached = _load_cached_license()
    if not cached:
        return 0

    activated_at = cached.get("activated_at")
    if not activated_at:
        return 0

    try:
        activated_time = datetime.fromisoformat(activated_at)
        delta = datetime.now() - activated_time
        return delta.days
    except Exception:
        return 0


# ============================================================
# CLI 전용 함수 (MCP 의존성 없음)
# ============================================================

def activate_license_cli(license_key: str) -> dict:
    """CLI용 라이센스 활성화 (MCP 의존성 없음)

    TEST-로 시작하는 테스트 라이선스는 Worker API로 검증.
    일반 라이선스는 Lemon Squeezy API로 검증.

    Returns:
        {
            "success": True/False,
            "message": "...",
            "tier": "personal"/"team"/"enterprise",
            "machine_id": "..."
        }
    """
    if not license_key or not license_key.strip():
        return {
            "success": False,
            "message": "라이선스 키를 입력하세요."
        }

    license_key = license_key.strip()
    machine_id = _get_machine_id()

    # 테스트 라이선스 처리 (TEST-로 시작)
    if license_key.startswith("TEST-"):
        return _activate_test_license(license_key, machine_id)

    # 일반 라이선스: Lemon Squeezy API
    try:
        response = requests.post(
            LEMONSQUEEZY_ACTIVATE_URL,
            json={
                "license_key": license_key,
                "instance_name": f"clouvel-{machine_id}"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("activated") or data.get("valid"):
                meta = data.get("meta", {})
                instance = data.get("instance", {})

                # 티어 추출
                product_name = meta.get("product_name", "").lower()
                if "team" in product_name:
                    tier = "team"
                elif "enterprise" in product_name:
                    tier = "enterprise"
                else:
                    tier = "personal"

                tier_info = TIERS[tier]

                # 캐시 저장
                _save_license_cache(
                    license_key,
                    tier,
                    tier_info,
                    instance.get("id"),
                    preserve_activated_at=False
                )

                return {
                    "success": True,
                    "message": f"✅ {tier_info['name']} 라이선스 활성화 완료",
                    "tier": tier,
                    "tier_info": tier_info,
                    "machine_id": machine_id,
                    "product": meta.get("product_name", "Clouvel Pro")
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 활성화 실패: {data.get('error', '라이선스가 유효하지 않습니다.')}"
                }
        else:
            return {
                "success": False,
                "message": f"❌ API 오류: {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {"success": False, "message": "❌ 연결 시간 초과"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "❌ 네트워크 연결 실패"}
    except Exception as e:
        return {"success": False, "message": f"❌ 오류: {str(e)}"}


def _activate_test_license(license_key: str, machine_id: str) -> dict:
    """테스트 라이선스 활성화 (Worker API로 검증)"""
    try:
        # Worker API로 heartbeat 전송하여 검증
        response = requests.post(
            HEARTBEAT_URL,
            json={
                "license_key": license_key,
                "machine_id": machine_id,
                "client_version": "1.3.0"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "valid":
                tier = data.get("tier", "team")
                tier_info = TIERS.get(tier, TIERS["team"])
                expires_at = data.get("expires_at", "")
                expires_in_days = data.get("expires_in_days", 7)

                # 캐시 저장
                _save_license_cache(
                    license_key,
                    tier,
                    tier_info,
                    None,
                    preserve_activated_at=False
                )

                return {
                    "success": True,
                    "message": f"✅ 테스트 라이선스 활성화 완료 ({tier_info['name']})",
                    "tier": tier,
                    "tier_info": tier_info,
                    "machine_id": machine_id,
                    "product": "Clouvel Pro (Test)",
                    "test_license": True,
                    "expires_at": expires_at,
                    "expires_in_days": expires_in_days
                }
            elif data.get("status") == "expired":
                return {
                    "success": False,
                    "message": f"❌ 테스트 라이선스 만료: {data.get('message', '')}"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 테스트 라이선스 검증 실패: {data.get('message', '유효하지 않습니다.')}"
                }
        else:
            return {
                "success": False,
                "message": f"❌ 테스트 라이선스 검증 실패: HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {"success": False, "message": "❌ 연결 시간 초과"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "❌ 네트워크 연결 실패"}
    except Exception as e:
        return {"success": False, "message": f"❌ 오류: {str(e)}"}


def get_license_status() -> dict:
    """CLI용 라이센스 상태 확인

    Returns:
        {
            "has_license": True/False,
            "tier": "personal"/"team"/"enterprise"/None,
            "machine_id": "...",
            "activated_at": "...",
            "days_since_activation": int,
            "premium_unlocked": True/False
        }
    """
    # 개발자 자동 Pro 처리
    if is_developer():
        return {
            "has_license": True,
            "tier": "developer",
            "tier_info": DEV_TIER_INFO,
            "license_key": "DEV-MODE",
            "machine_id": _get_machine_id(),
            "activated_at": datetime.now().isoformat(),
            "days_since_activation": 999,
            "premium_unlocked": True,
            "premium_unlock_remaining": 0,
            "is_developer": True,
            "message": "🔧 개발자 모드 (자동 Pro 활성화)"
        }

    cached = _load_cached_license()

    if not cached:
        return {
            "has_license": False,
            "message": "라이선스가 없습니다. 'clouvel activate <key>'로 활성화하세요."
        }

    # 기본값: personal (Unknown 방지 - license_common과 동일)
    tier = cached.get("tier") or DEFAULT_TIER
    tier_info = cached.get("tier_info") or get_tier_info(tier)
    machine_id = cached.get("machine_id", "unknown")
    activated_at = cached.get("activated_at", "")

    # 활성화 후 경과 일수
    days = get_license_age_days()
    # DEV_MODE에서는 7일 대기 우회
    premium_unlocked = DEV_MODE or days >= PREMIUM_UNLOCK_DAYS

    return {
        "has_license": True,
        "tier": tier,
        "tier_info": tier_info,
        "machine_id": machine_id,
        "activated_at": activated_at,
        "days_since_activation": days,
        "premium_unlocked": premium_unlocked,
        "premium_unlock_remaining": max(0, PREMIUM_UNLOCK_DAYS - days)
    }


def deactivate_license_cli() -> dict:
    """CLI용 라이센스 비활성화 (로컬 캐시만 삭제)

    Returns:
        {"success": True/False, "message": "..."}
    """
    try:
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink()
        if HEARTBEAT_FILE.exists():
            HEARTBEAT_FILE.unlink()
        return {
            "success": True,
            "message": "✅ 로컬 라이선스 캐시가 삭제되었습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 삭제 실패: {str(e)}"
        }


def require_license(func):
    """기본 라이선스 체크 데코레이터 (Day 1부터 사용 가능)"""
    async def wrapper(*args, **kwargs):
        result = verify_license()
        if not result["valid"]:
            return [TextContent(type="text", text=f"""
# ❌ Clouvel Pro 라이선스 필요

{result['message']}

## 구매
https://clouvel.lemonsqueezy.com
""")]
        return await func(*args, **kwargs)
    return wrapper


def require_license_premium(func):
    """프리미엄 기능 데코레이터 (Day 8+부터 사용 가능)

    Buy-Use-Refund 공격 방어:
    - 활성화 후 7일이 지나야 핵심 기능 사용 가능
    - 환불 기간(보통 7-14일) 동안은 기본 기능만 제공

    Heartbeat 체크:
    - 24시간마다 서버 통신 필요
    - 오프라인 유예: 3일

    DEV_MODE:
    - 7일 잠금 해제
    - Heartbeat 스킵
    """
    async def wrapper(*args, **kwargs):
        result = verify_license()
        if not result["valid"]:
            return [TextContent(type="text", text=f"""
# Clouvel Pro 라이선스 필요

{result['message']}

## 구매
https://clouvel.lemonsqueezy.com
""")]

        # DEV_MODE: 7일 잠금 및 Heartbeat 스킵
        if DEV_MODE or result.get("dev_mode"):
            return await func(*args, **kwargs)

        # 7일 잠금 체크
        age_days = get_license_age_days()
        remaining = PREMIUM_UNLOCK_DAYS - age_days

        if remaining > 0:
            return [TextContent(type="text", text=f"""
# 프리미엄 기능 잠금 중

이 기능은 **활성화 후 {PREMIUM_UNLOCK_DAYS}일**이 지나야 사용할 수 있습니다.

## 현재 상태
- **활성화 경과**: {age_days}일
- **잠금 해제까지**: {remaining}일 남음

## 지금 사용 가능한 기능
- `watch_logs` - 로그 감시 설정
- `check_logs` - 로그 체크

## 왜 7일 잠금인가요?
Buy-Use-Refund 공격 방지를 위해 핵심 기능은 환불 기간 이후에 제공됩니다.
정상 사용자에게는 불편을 드려 죄송합니다.

**{remaining}일 후에 다시 시도해주세요!**
""")]

        # Heartbeat 체크 (7일 잠금 해제 후에만)
        heartbeat_result = send_heartbeat()

        if not heartbeat_result.get("success"):
            status = heartbeat_result.get("status", "error")

            if status == "revoked":
                return [TextContent(type="text", text=f"""
# 라이선스 취소됨

{heartbeat_result.get('message', '라이선스가 취소되었습니다.')}

취소 시각: {heartbeat_result.get('revoked_at', 'N/A')}

## 재구매
https://clouvel.lemonsqueezy.com
""")]

            elif status == "offline_expired":
                return [TextContent(type="text", text=f"""
# 오프라인 유예 기간 초과

{heartbeat_result.get('message', '')}

## 해결 방법
1. 인터넷 연결 확인
2. VPN 사용 시 일시 해제
3. 방화벽에서 clouvel-api.vnddns999.workers.dev 허용

연결 후 자동으로 heartbeat가 전송됩니다.
""")]

            elif status == "seat_limit":
                return [TextContent(type="text", text=f"""
# 기기 수 제한 초과

{heartbeat_result.get('message', '')}

현재: {heartbeat_result.get('current_machines', '?')}대
최대: {heartbeat_result.get('max_machines', '?')}대

## 해결 방법
1. 기존 기기에서 라이선스 비활성화
2. Team/Enterprise로 업그레이드

## 업그레이드
https://clouvel.lemonsqueezy.com
""")]

            elif status not in ["cached", "offline_grace"]:
                # 심각한 오류가 아닌 경우 경고만 표시하고 진행
                pass

        return await func(*args, **kwargs)
    return wrapper


def require_team_license(func):
    """Team 라이선스 체크 데코레이터 (Team/Enterprise 전용)

    Team 기능:
    - 멤버 관리
    - C-Level 역할 토글
    - 팀 에러 패턴 공유
    - 시니어 리뷰 시스템
    """
    async def wrapper(*args, **kwargs):
        result = verify_license()
        if not result["valid"]:
            return [TextContent(type="text", text=f"""
# ❌ Clouvel Pro 라이선스 필요

{result['message']}

## 구매
https://clouvel.lemonsqueezy.com
""")]

        # Team/Enterprise 티어 확인
        tier = result.get("tier", "personal")
        if tier not in ["team", "enterprise"]:
            return [TextContent(type="text", text=f"""
# ❌ Team 라이선스 필요

현재 티어: **{tier.capitalize()}**

이 기능은 **Team ($79)** 또는 **Enterprise ($199)** 라이선스가 필요합니다.

## Team 기능
- 팀원 초대/관리 (최대 10명)
- C-Level 역할 커스터마이징
- 팀 에러 패턴 공유
- 시니어 리뷰 시스템
- 프로젝트 컨텍스트 동기화

## 업그레이드
https://clouvel.lemonsqueezy.com
""")]

        return await func(*args, **kwargs)
    return wrapper
