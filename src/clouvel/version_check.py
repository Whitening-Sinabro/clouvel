# -*- coding: utf-8 -*-
"""
Clouvel Version Check
PyPI에서 최신 버전 확인 및 업데이트 알림
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

# 캐시 설정
CACHE_DIR = Path.home() / ".clouvel"
CACHE_FILE = CACHE_DIR / "version_cache.json"
CACHE_TTL = 86400  # 24시간 (초)

# 현재 버전 (pyproject.toml과 동기화)
CURRENT_VERSION = "3.0.1"

# v3.0 마이그레이션 공지 (한 번만 표시)
V3_MIGRATION_NOTICE_FILE = CACHE_DIR / "v3_notice_shown.json"


def _get_current_version() -> str:
    """현재 설치된 버전 반환"""
    try:
        from importlib.metadata import version
        return version("clouvel")
    except Exception:
        return CURRENT_VERSION


def _fetch_latest_version() -> Optional[str]:
    """PyPI에서 최신 버전 조회"""
    try:
        import requests
        response = requests.get(
            "https://pypi.org/pypi/clouvel/json",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()["info"]["version"]
    except Exception:
        pass
    return None


def _load_cache() -> Optional[Dict[str, Any]]:
    """캐시 파일 로드"""
    try:
        if CACHE_FILE.exists():
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            # TTL 체크
            if time.time() - data.get("timestamp", 0) < CACHE_TTL:
                return data
    except Exception:
        pass
    return None


def _save_cache(data: Dict[str, Any]) -> None:
    """캐시 파일 저장"""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data["timestamp"] = time.time()
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def _compare_versions(current: str, latest: str) -> int:
    """
    버전 비교
    Returns:
        -1: current < latest (업데이트 필요)
         0: current == latest
         1: current > latest
    """
    def parse(v: str):
        # "1.3.3" -> [1, 3, 3]
        try:
            return [int(x) for x in v.split(".")]
        except (ValueError, AttributeError):
            return [0]

    curr_parts = parse(current)
    latest_parts = parse(latest)

    # 길이 맞추기
    max_len = max(len(curr_parts), len(latest_parts))
    curr_parts.extend([0] * (max_len - len(curr_parts)))
    latest_parts.extend([0] * (max_len - len(latest_parts)))

    for c, l in zip(curr_parts, latest_parts):
        if c < l:
            return -1
        elif c > l:
            return 1
    return 0


def check_for_updates(force: bool = False) -> Dict[str, Any]:
    """
    업데이트 확인

    Args:
        force: 캐시 무시하고 강제 체크

    Returns:
        {
            "current_version": "1.3.3",
            "latest_version": "1.4.0",
            "update_available": True,
            "message": "업데이트 메시지"
        }
    """
    current = _get_current_version()
    result = {
        "current_version": current,
        "latest_version": None,
        "update_available": False,
        "message": None,
        "from_cache": False
    }

    # 캐시 확인
    if not force:
        cache = _load_cache()
        if cache and cache.get("latest_version"):
            result["latest_version"] = cache["latest_version"]
            result["from_cache"] = True

    # 캐시 없으면 PyPI 조회
    if not result["latest_version"]:
        latest = _fetch_latest_version()
        if latest:
            result["latest_version"] = latest
            # 캐시 저장
            _save_cache({"latest_version": latest})

    # 비교
    if result["latest_version"]:
        comparison = _compare_versions(current, result["latest_version"])
        if comparison < 0:
            result["update_available"] = True
            result["message"] = f"🆕 Clouvel {result['latest_version']} 사용 가능! (현재: {current})\n   pip install --upgrade clouvel"

    return result


def get_update_banner() -> Optional[str]:
    """
    업데이트 배너 반환 (업데이트 있을 때만)
    도구 출력에 추가할 수 있음
    """
    result = check_for_updates()
    if result["update_available"]:
        return f"""
╔════════════════════════════════════════════════╗
║  🆕 Clouvel {result['latest_version']} 업데이트 가능!              ║
║  현재: {result['current_version']} → 최신: {result['latest_version']}                  ║
║  pip install --upgrade clouvel                 ║
╚════════════════════════════════════════════════╝
"""
    return None


# 전역 상태 (서버 시작 시 한 번만 체크)
_update_info: Optional[Dict[str, Any]] = None


def init_version_check() -> Dict[str, Any]:
    """
    서버 시작 시 호출 - 버전 체크 초기화
    """
    global _update_info
    _update_info = check_for_updates()
    return _update_info


def get_cached_update_info() -> Optional[Dict[str, Any]]:
    """
    캐시된 업데이트 정보 반환
    """
    return _update_info


# ============================================================
# v3.0 Migration Notice
# ============================================================

V3_NOTICE_EN = """
================================================
  CLOUVEL v3.0 - FREE/PRO TIER CHANGES
================================================

FREE tier is now lighter (easier to start):
  - Managers: 3 -> 1 (PM only)
  - can_code: BLOCK -> WARN (you can proceed)
  - Projects: 1 limit

PRO tier is now heavier (full protection):
  - Managers: 8 (all C-Level)
  - can_code: BLOCK (enforced)
  - Projects: Unlimited

Upgrade: https://polar.sh/clouvel (code: FIRST01)

================================================
"""

V3_NOTICE_KO = """
================================================
  CLOUVEL v3.0 - FREE/PRO 티어 변경
================================================

FREE 티어가 가벼워졌습니다 (시작이 쉬워짐):
  - 매니저: 3명 -> 1명 (PM만)
  - can_code: BLOCK -> WARN (진행 가능)
  - 프로젝트: 1개 제한

PRO 티어가 강력해졌습니다 (완전 보호):
  - 매니저: 8명 (전체 C-Level)
  - can_code: BLOCK (강제)
  - 프로젝트: 무제한

업그레이드: https://polar.sh/clouvel (코드: FIRST01)

================================================
"""


def _should_show_v3_notice() -> bool:
    """Check if v3.0 migration notice should be shown."""
    try:
        if V3_MIGRATION_NOTICE_FILE.exists():
            data = json.loads(V3_MIGRATION_NOTICE_FILE.read_text(encoding="utf-8"))
            return not data.get("shown", False)
    except Exception:
        pass
    return True


def _mark_v3_notice_shown() -> None:
    """Mark v3.0 migration notice as shown."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        V3_MIGRATION_NOTICE_FILE.write_text(
            json.dumps({"shown": True, "timestamp": time.time()}),
            encoding="utf-8"
        )
    except Exception:
        pass


def get_v3_migration_notice(lang: str = "en") -> Optional[str]:
    """
    Get v3.0 migration notice if not shown yet.

    Args:
        lang: "en" or "ko"

    Returns:
        Notice string or None if already shown
    """
    if not _should_show_v3_notice():
        return None

    _mark_v3_notice_shown()

    if lang == "ko":
        return V3_NOTICE_KO
    return V3_NOTICE_EN


def reset_v3_notice() -> None:
    """Reset v3.0 notice (for testing)."""
    try:
        if V3_MIGRATION_NOTICE_FILE.exists():
            V3_MIGRATION_NOTICE_FILE.unlink()
    except Exception:
        pass
