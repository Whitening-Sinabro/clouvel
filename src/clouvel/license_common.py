# -*- coding: utf-8 -*-
"""License Common Module

공통 라이선스 로직을 모아둔 모듈.
license.py와 license_free.py에서 공유.

사이드이펙트 방지:
- 이 파일 수정 시 license.py, license_free.py 모두 확인
- 반환값 구조 변경 시 server.py도 확인
"""

import os
import json
import hashlib
import platform
import subprocess
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


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
        source_dir = Path(__file__).parent
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
    except Exception:
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
    "personal": {"name": "Personal", "price": "$29", "seats": 1},
    "team": {"name": "Team", "price": "$79", "seats": 10},
    "enterprise": {"name": "Enterprise", "price": "$199", "seats": 999},
}

# ============================================================
# v3.0: Feature Availability & Project Tracking
# ============================================================

PRO_ONLY_FEATURES = [
    "full_prd_validation",
    "code_blocking",
    "full_managers",
    "unlimited_projects",
    "knowledge_base",
    "error_learning",
]

# FREE tier project limit
FREE_PROJECT_LIMIT = 1


def is_feature_available(feature: str) -> Dict[str, Any]:
    """Check if feature is available for current license.

    v3.0: FREE tier = light (warns, 1 PM, 1 project)
          PRO tier = heavy (blocks, 8 managers, unlimited)

    Returns:
        dict with keys:
        - available: bool
        - reason: "developer" | "pro" | "free"
        - upgrade_hint: str (only if not available)
    """
    if is_developer():
        return {"available": True, "reason": "developer"}

    cached = load_license_cache()
    has_license = cached is not None and cached.get("tier") is not None

    # Non-pro features are always available
    if feature not in PRO_ONLY_FEATURES:
        return {"available": True, "reason": "free"}

    # Pro features require license
    if has_license:
        return {"available": True, "reason": "pro"}

    return {"available": False, "reason": "free", "upgrade_hint": "FIRST01"}


def get_projects_path() -> Path:
    """Get projects tracking file path: ~/.clouvel/projects.json"""
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:  # Unix
        base = Path.home()

    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "projects.json"


def load_projects() -> Dict[str, Any]:
    """Load registered projects from tracking file."""
    projects_path = get_projects_path()
    if projects_path.exists():
        try:
            return json.loads(projects_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"projects": [], "last_updated": None}


def save_projects(data: Dict[str, Any]) -> bool:
    """Save projects data to tracking file."""
    projects_path = get_projects_path()
    try:
        data["last_updated"] = datetime.now().isoformat()
        projects_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def register_project(project_path: str) -> Dict[str, Any]:
    """Register a project and check if within FREE tier limit.

    v3.0: FREE tier = 1 project only
          PRO tier = unlimited

    Returns:
        dict with keys:
        - allowed: bool
        - count: int (current project count)
        - limit: int (project limit)
        - is_new: bool (True if newly registered)
    """
    # Developers and Pro users have unlimited projects
    if is_developer():
        return {"allowed": True, "count": 0, "limit": 999, "is_new": False}

    cached = load_license_cache()
    has_license = cached is not None and cached.get("tier") is not None

    if has_license:
        return {"allowed": True, "count": 0, "limit": 999, "is_new": False}

    # FREE tier: check project limit
    data = load_projects()
    projects = data.get("projects", [])

    # Normalize path for comparison
    normalized_path = str(Path(project_path).resolve())

    # Check if project is already registered
    if normalized_path in projects:
        return {
            "allowed": True,
            "count": len(projects),
            "limit": FREE_PROJECT_LIMIT,
            "is_new": False
        }

    # Check if we're at the limit
    if len(projects) >= FREE_PROJECT_LIMIT:
        return {
            "allowed": False,
            "count": len(projects),
            "limit": FREE_PROJECT_LIMIT,
            "is_new": False,
            "existing_project": projects[0] if projects else None
        }

    # Register new project
    projects.append(normalized_path)
    data["projects"] = projects
    save_projects(data)

    return {
        "allowed": True,
        "count": len(projects),
        "limit": FREE_PROJECT_LIMIT,
        "is_new": True
    }


def get_project_count() -> int:
    """Get current registered project count."""
    data = load_projects()
    return len(data.get("projects", []))

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
        except Exception:
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
    except Exception:
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
        except Exception:
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
        except Exception:
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
