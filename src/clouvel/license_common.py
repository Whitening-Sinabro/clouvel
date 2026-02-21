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
    "personal": {"name": "Personal", "price": "$7.99/mo", "seats": 1},
    "team": {"name": "Team", "price": "$79/mo", "seats": 10},
    "enterprise": {"name": "Enterprise", "price": "$199/mo", "seats": 999},
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

# FREE tier project limit (v5.0: first project unlimited, second+ needs Pro)
FREE_PROJECT_LIMIT = 1  # Legacy: kept for backward compat
FREE_ACTIVE_PROJECT_LIMIT = 1  # First project = unlimited Pro, additional = blocked

# FREE tier template layout limit
FREE_LAYOUTS = ["lite", "minimal"]  # v3.3: minimal added for quick unblock
PRO_LAYOUTS = ["lite", "minimal", "standard", "detailed"]


def is_feature_available(feature: str) -> Dict[str, Any]:
    """Check if feature is available for current license.

    v5.0: First project = full Pro (8 managers, BLOCK, KB, unlimited)
          Additional projects = Pro license required

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

    # Full Pro Trial active = treat as Pro
    if is_full_trial_active():
        trial_status = get_full_trial_status()
        return {
            "available": True,
            "reason": "trial",
            "remaining_days": trial_status.get("remaining_days", 0),
        }

    # Pro features require license
    if has_license:
        return {"available": True, "reason": "pro"}

    return {"available": False, "reason": "free", "upgrade_hint": "$49/yr"}


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
    """Load registered projects from tracking file.

    v3.3: Migrates old format (list of paths) to new format (list of dicts).
    New format: {"projects": [{"path": "...", "status": "active"|"archived", "registered_at": "..."}]}
    """
    projects_path = get_projects_path()
    if projects_path.exists():
        try:
            data = json.loads(projects_path.read_text(encoding="utf-8"))

            # v3.3: Migrate old format to new format
            projects = data.get("projects", [])
            if projects and isinstance(projects[0], str):
                # Old format: list of path strings
                migrated = []
                for p in projects:
                    migrated.append({
                        "path": p,
                        "status": "active",
                        "registered_at": data.get("last_updated") or datetime.now().isoformat()
                    })
                data["projects"] = migrated
                data["migrated_at"] = datetime.now().isoformat()
                # Save migrated data
                save_projects(data)

            return data
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

    v5.1: Single source of truth via get_project_tier().
          Removes redundant Pro/developer/trial checks.

    Returns:
        dict with keys:
        - allowed: bool
        - count: int (active project count)
        - limit: int (project limit)
        - is_new: bool (True if newly registered)
        - tier: str (pro/first/additional)
    """
    # v5.1: Single tier check (handles developer, license, trial, first, additional)
    try:
        tier = get_project_tier(project_path)
    except Exception:
        tier = "additional"  # Safe fallback: require Pro

    # Pro/developer/trial = unlimited
    if tier == "pro":
        return {"allowed": True, "count": 0, "limit": 999, "is_new": False, "tier": "pro"}

    # First project = unlimited (all Pro features)
    if tier == "first":
        return {"allowed": True, "count": 0, "limit": 999, "is_new": False, "tier": "first"}

    # Additional project = Pro required
    first = get_first_project()
    first_path = first.get("path", "Unknown") if first else "Unknown"

    # Log project limit hit event
    try:
        from .analytics import log_event
        log_event("project_limit_hit", {
            "active_count": 1,
            "limit": FREE_ACTIVE_PROJECT_LIMIT,
            "active_project": first_path,
            "project_tier": "additional",
            "user_id_hash": get_machine_id()[:8],
        })
    except Exception:
        pass

    return {
        "allowed": False,
        "count": 1,
        "limit": FREE_ACTIVE_PROJECT_LIMIT,
        "is_new": False,
        "tier": "additional",
        "active_projects": [{"path": first_path}],
        "needs_upgrade": True,
        "message": _get_project_limit_message([{"path": first_path}]),
    }


def _get_project_limit_message(active_projects: list) -> str:
    """Generate project limit reached message (v3.0.0: first-project-aware)."""
    if not active_projects:
        return "프로젝트 제한에 도달했습니다."

    # v3.0.0: Show first project info
    first = get_first_project()
    if first:
        first_name = Path(first.get("path", "Unknown")).name
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔒 Pro Required for Additional Projects

  Your first project ({first_name}) has full Pro features.
  To unlock Pro for all your projects:

  Monthly: $7.99/mo
  Annual:  $49/yr (Early Adopter Pricing)
  → https://polar.sh/clouvel

  💡 Pro developers manage 3.2 projects on average.
     Knowledge Base remembers each project's context.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    active_name = Path(active_projects[0].get("path", "Unknown")).name
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔒 Pro Required for Additional Projects

  Your first project ({active_name}) has full Pro features.
  To unlock Pro for all your projects:

  Monthly: $7.99/mo
  Annual:  $49/yr (Early Adopter Pricing)
  → https://polar.sh/clouvel

  💡 Pro developers manage 3.2 projects on average.
     Knowledge Base remembers each project's context.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def get_project_count() -> int:
    """Get current ACTIVE project count."""
    data = load_projects()
    projects = data.get("projects", [])
    return len([p for p in projects if p.get("status") == "active"])


def archive_project(project_path: str) -> Dict[str, Any]:
    """Archive a project (remove from active count).

    v3.3: Archived projects don't count toward FREE limit.

    Returns:
        dict with success, message, archived_at
    """
    data = load_projects()
    projects = data.get("projects", [])
    normalized_path = str(Path(project_path).resolve())

    # Find project
    project = next((p for p in projects if p.get("path") == normalized_path), None)

    if not project:
        return {
            "success": False,
            "message": f"프로젝트를 찾을 수 없습니다: {project_path}"
        }

    if project.get("status") == "archived":
        return {
            "success": False,
            "message": "이미 아카이브된 프로젝트입니다."
        }

    # Archive
    project["status"] = "archived"
    project["archived_at"] = datetime.now().isoformat()
    save_projects(data)

    # Log event
    try:
        from .analytics import log_event
        log_event("project_archived", {"path": normalized_path[:50]})
    except Exception:
        pass

    return {
        "success": True,
        "message": f"✅ 프로젝트가 아카이브되었습니다: {Path(project_path).name}\n\n이제 새 프로젝트를 시작할 수 있습니다.",
        "archived_at": project["archived_at"],
    }


def reactivate_project(project_path: str) -> Dict[str, Any]:
    """Reactivate an archived project.

    v3.3: If another project is active, it will be archived first.

    Returns:
        dict with success, message, previously_active (if any)
    """
    # Check license/developer status
    if is_developer():
        return {"success": True, "message": "[DEV] Developer mode - no limit"}

    cached = load_license_cache()
    has_license = cached is not None and cached.get("tier") is not None

    if has_license or is_full_trial_active():
        return {"success": True, "message": "Pro 사용자 - 제한 없음"}

    data = load_projects()
    projects = data.get("projects", [])
    normalized_path = str(Path(project_path).resolve())

    # Find project to reactivate
    project = next((p for p in projects if p.get("path") == normalized_path), None)

    if not project:
        return {
            "success": False,
            "message": f"프로젝트를 찾을 수 없습니다: {project_path}"
        }

    if project.get("status") == "active":
        return {
            "success": True,
            "message": "이미 활성화된 프로젝트입니다."
        }

    # Check if we need to archive current active project
    active_projects = [p for p in projects if p.get("status") == "active"]
    previously_active = None

    if len(active_projects) >= FREE_ACTIVE_PROJECT_LIMIT:
        # Auto-archive the oldest active project
        oldest = min(active_projects, key=lambda x: x.get("registered_at", ""))
        oldest["status"] = "archived"
        oldest["archived_at"] = datetime.now().isoformat()
        previously_active = oldest.get("path")

    # Reactivate
    project["status"] = "active"
    project["reactivated_at"] = datetime.now().isoformat()
    save_projects(data)

    # Log event
    try:
        from .analytics import log_event
        log_event("project_reactivated", {
            "path": normalized_path[:50],
            "swapped": previously_active is not None
        })
    except Exception:
        pass

    result = {
        "success": True,
        "message": f"✅ 프로젝트가 재활성화되었습니다: {Path(project_path).name}",
        "reactivated_at": project["reactivated_at"],
    }

    if previously_active:
        result["previously_active"] = previously_active
        result["message"] += f"\n\n📦 '{Path(previously_active).name}'가 자동 아카이브되었습니다."

    return result


def list_projects() -> Dict[str, Any]:
    """List all registered projects with their status.

    Returns:
        dict with active, archived lists and counts
    """
    data = load_projects()
    projects = data.get("projects", [])

    active = [p for p in projects if p.get("status") == "active"]
    archived = [p for p in projects if p.get("status") == "archived"]

    # Check tier
    is_pro = is_developer()
    if not is_pro:
        cached = load_license_cache()
        is_pro = cached is not None and cached.get("tier") is not None
    if not is_pro:
        is_pro = is_full_trial_active()

    return {
        "active": [{"path": p.get("path"), "name": Path(p.get("path", "")).name, "registered_at": p.get("registered_at")} for p in active],
        "archived": [{"path": p.get("path"), "name": Path(p.get("path", "")).name, "archived_at": p.get("archived_at")} for p in archived],
        "active_count": len(active),
        "archived_count": len(archived),
        "limit": 999 if is_pro else FREE_ACTIVE_PROJECT_LIMIT,
        "is_pro": is_pro,
    }

# ============================================================
# v3.0.0: First Project Unlimited (Reverse Trial)
# ============================================================

def _get_first_project_path() -> Path:
    """Get first project tracking file: ~/.clouvel/first_project.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "first_project.json"


def _hash_path(path: str) -> str:
    """SHA256 hash of normalized path."""
    return hashlib.sha256(path.encode()).hexdigest()[:32]


def get_first_project() -> Optional[Dict[str, Any]]:
    """Load first project data. Returns None if not registered."""
    fp_path = _get_first_project_path()
    if not fp_path.exists():
        return None
    try:
        data = json.loads(fp_path.read_text(encoding="utf-8"))
        # Validate structure
        if "path_hash" in data and "machine_id" in data:
            return data
        return None
    except Exception:
        return None


def register_first_project(project_path: str) -> Dict[str, Any]:
    """Register the first project (one-time, per machine).

    Auto-migration: If projects.json has 1 active project and no
    first_project.json exists, auto-register that project.

    Returns:
        dict with path_hash, machine_id, registered_at, version
    """
    fp_path = _get_first_project_path()

    # Already registered — don't overwrite
    existing = get_first_project()
    if existing is not None:
        return existing

    normalized = str(Path(project_path).resolve())

    data = {
        "path": normalized,
        "path_hash": _hash_path(normalized),
        "machine_id": get_machine_id(),
        "registered_at": datetime.now().isoformat(),
        "version": "3.0.0",
    }

    try:
        fp_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass

    # Log event
    try:
        from .analytics import log_event
        log_event("first_project_registered", {
            "path_hash": data["path_hash"][:8],
            "machine_id": data["machine_id"][:8],
        })
    except Exception:
        pass

    return data


def _auto_migrate_first_project() -> Optional[str]:
    """Auto-migrate: if projects.json has exactly 1 active project, return its path.

    Called during get_project_tier when no first_project.json exists.
    """
    try:
        data = load_projects()
        projects = data.get("projects", [])
        active = [p for p in projects if p.get("status") == "active"]
        if len(active) == 1:
            return active[0].get("path")
    except Exception:
        pass
    return None


def get_project_tier(project_path: str) -> str:
    """Get tier for a specific project.

    Returns:
        "pro"        — Pro license / developer / trial active
        "first"      — First project (all Pro features)
        "additional" — Second+ project (Pro required)
    """
    # 1) Developer/License/Trial → "pro"
    if is_developer():
        return "pro"

    cached = load_license_cache()
    if cached and cached.get("tier"):
        return "pro"

    if is_full_trial_active():
        return "pro"

    # 2) First project check
    normalized = str(Path(project_path).resolve())
    first = get_first_project()

    if first is None:
        # Auto-migration: check projects.json for existing single active project
        migrated_path = _auto_migrate_first_project()
        if migrated_path:
            register_first_project(migrated_path)
            first = get_first_project()
            if first and first.get("path_hash") == _hash_path(normalized):
                return "first"
            elif first:
                return "additional"
        # No migration candidate — register current project as first
        register_first_project(normalized)
        return "first"

    if first.get("path_hash") == _hash_path(normalized):
        return "first"

    # Machine ID mismatch → additional (anti-abuse)
    if first.get("machine_id") != get_machine_id():
        return "additional"

    return "additional"


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


# ============================================================
# WARN 횟수 추적 (v3.1: 전환율 개선)
# ============================================================

def _get_warn_count_path() -> Path:
    """Get warn count tracking file path: ~/.clouvel/warn_count.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "warn_count.json"


def increment_warn_count(project_path: str) -> int:
    """Increment WARN count for a project and return new count."""
    path = _get_warn_count_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    normalized = str(Path(project_path).resolve())
    count = data.get(normalized, 0) + 1
    data[normalized] = count

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return count


def get_warn_count(project_path: str) -> int:
    """Get current WARN count for a project."""
    path = _get_warn_count_path()
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        normalized = str(Path(project_path).resolve())
        return data.get(normalized, 0)
    except Exception:
        return 0


# ============================================================
# KB Trial 관리 (v3.1: 7일 체험)
# ============================================================

def _get_kb_trial_path() -> Path:
    """Get KB trial tracking file path: ~/.clouvel/kb_trial.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "kb_trial.json"


def get_kb_trial_start(project_path: str) -> Optional[str]:
    """Get KB trial start date for a project. Returns ISO date string or None."""
    path = _get_kb_trial_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        normalized = str(Path(project_path).resolve())
        return data.get(normalized)
    except Exception:
        return None


def start_kb_trial(project_path: str) -> str:
    """Start KB trial for a project. Returns the start date."""
    path = _get_kb_trial_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    normalized = str(Path(project_path).resolve())
    # Don't overwrite existing trial
    if normalized in data:
        return data[normalized]

    start_date = datetime.now().isoformat()
    data[normalized] = start_date

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return start_date


def is_kb_trial_active(project_path: str) -> bool:
    """Check if KB trial is still active (within 7 days).

    v5.0: First project always has KB access (no trial needed).
    """
    # v5.0: First project gets unlimited KB
    try:
        tier = get_project_tier(project_path)
        if tier in ("pro", "first"):
            return True
    except Exception:
        pass

    start = get_kb_trial_start(project_path)
    if start is None:
        return True  # No trial started yet = can start one

    try:
        start_time = datetime.fromisoformat(start)
        days = (datetime.now() - start_time).days
        return days < 7
    except Exception:
        return False


# ============================================================
# 주간 풀 매니저 체험 (v3.1)
# ============================================================

def _get_weekly_meeting_path() -> Path:
    """Get weekly meeting tracking file path: ~/.clouvel/weekly_meeting.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "weekly_meeting.json"


def can_use_weekly_full_meeting(project_path: str) -> Dict[str, Any]:
    """Check if user can use weekly full meeting trial.

    Returns dict with:
    - available: bool
    - last_used_week: str (ISO week, e.g. "2026-W05")
    - current_week: str
    """
    path = _get_weekly_meeting_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    normalized = str(Path(project_path).resolve())
    now = datetime.now()
    current_week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"

    last_used_week = data.get(normalized)

    return {
        "available": last_used_week != current_week,
        "last_used_week": last_used_week,
        "current_week": current_week,
    }


def mark_weekly_meeting_used(project_path: str) -> None:
    """Mark weekly full meeting as used for this week."""
    path = _get_weekly_meeting_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    normalized = str(Path(project_path).resolve())
    now = datetime.now()
    current_week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    data[normalized] = current_week

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ============================================================
# Monthly Meeting Quota (v3.3: 월 3회 Full Meeting 체험)
# ============================================================

FREE_MONTHLY_MEETINGS = 3


def _get_monthly_meeting_path() -> Path:
    """Get monthly meeting quota tracking file path: ~/.clouvel/monthly_meeting.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "monthly_meeting.json"


def check_meeting_quota(project_path: str = None) -> Dict[str, Any]:
    """Check monthly meeting quota for Free users.

    v3.3: Replaces weekly trial with monthly 3-time quota.
    v5.0: First project bypasses quota entirely.

    Returns:
        dict with:
        - allowed: bool
        - used: int (used this month)
        - remaining: int (remaining this month)
        - limit: int (monthly limit)
        - current_month: str (YYYY-MM)
        - notice: str (optional, shown when 1 remaining)
        - message: str (shown when quota exhausted)
    """
    # v5.0: First project gets unlimited meetings
    if project_path:
        try:
            tier = get_project_tier(project_path)
            if tier in ("pro", "first"):
                return {"allowed": True, "used": 0, "remaining": 999, "limit": 999, "current_month": datetime.now().strftime("%Y-%m")}
        except Exception:
            pass
    path = _get_monthly_meeting_path()
    current_month = datetime.now().strftime("%Y-%m")

    data = {"month": current_month, "used": 0, "history": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Reset if month changed
            if data.get("month") != current_month:
                data = {"month": current_month, "used": 0, "history": []}
        except Exception:
            data = {"month": current_month, "used": 0, "history": []}

    used = data.get("used", 0)
    remaining = max(0, FREE_MONTHLY_MEETINGS - used)

    result = {
        "allowed": remaining > 0,
        "used": used,
        "remaining": remaining,
        "limit": FREE_MONTHLY_MEETINGS,
        "current_month": current_month,
    }

    # Notice when last meeting remaining
    if remaining == 1:
        result["notice"] = (
            "⚡ 이번 달 마지막 무료 Meeting입니다!\n"
            "Pro 업그레이드로 무제한 사용하세요.\n"
            "→ https://polar.sh/clouvel"
        )

    # Message when quota exhausted (Pain Point #3)
    if remaining <= 0:
        result["message"] = f"""
🎯 이번 달 무료 Meeting {FREE_MONTHLY_MEETINGS}회를 모두 사용했습니다!

8명 C-level 매니저의 피드백이 도움이 되셨나요?

Pro 개발자들의 후기:
"혼자 개발할 때 놓치기 쉬운 보안 이슈를 CSO가 잡아줘서 좋아요"
"출시 전 CFO 피드백으로 수익 모델 구멍을 발견했습니다"

다음 달까지 기다리거나, 지금 바로 무제한으로 사용하세요.

💰 월 $7.99 (연간 결제 시 70% 할인)
→ https://polar.sh/clouvel
"""

    return result


def consume_meeting_quota(project_path: str = None) -> Dict[str, Any]:
    """Consume one meeting from monthly quota.

    v5.0: First project bypasses quota entirely.

    Returns:
        dict with used, remaining, notice (if applicable)
    """
    # v5.0: First project gets unlimited meetings
    if project_path:
        try:
            tier = get_project_tier(project_path)
            if tier in ("pro", "first"):
                return {"used": 0, "remaining": 999}
        except Exception:
            pass
    path = _get_monthly_meeting_path()
    current_month = datetime.now().strftime("%Y-%m")

    data = {"month": current_month, "used": 0, "history": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("month") != current_month:
                data = {"month": current_month, "used": 0, "history": []}
        except Exception:
            data = {"month": current_month, "used": 0, "history": []}

    # Increment usage
    data["used"] = data.get("used", 0) + 1
    data["history"] = data.get("history", []) + [datetime.now().isoformat()]

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    # Log event
    try:
        from .analytics import log_event
        _tier = "unknown"
        try:
            if project_path:
                _tier = get_project_tier(project_path)
        except Exception:
            pass
        log_event("meeting_quota_used", {
            "used": data["used"],
            "remaining": FREE_MONTHLY_MEETINGS - data["used"],
            "project_tier": _tier,
            "user_id_hash": get_machine_id()[:8],
        })
    except Exception:
        pass

    remaining = max(0, FREE_MONTHLY_MEETINGS - data["used"])

    result = {
        "used": data["used"],
        "remaining": remaining,
    }

    # Notice after consumption
    if remaining == 1:
        result["notice"] = (
            "⚡ 이번 달 1회 남았습니다!\n"
            "Pro 업그레이드로 무제한 사용하세요."
        )
    elif remaining == 0:
        result["notice"] = (
            "🎯 이번 달 무료 Meeting을 모두 사용했습니다.\n"
            "Pro: 무제한 Meeting + 8명 매니저\n"
            "→ https://polar.sh/clouvel"
        )

    return result


# ============================================================
# Full Pro Trial (v3.2: 7일 전체 기능 체험)
# ============================================================

FULL_TRIAL_DAYS = 7


def _get_full_trial_path() -> Path:
    """Get full trial tracking file path: ~/.clouvel/full_trial.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "full_trial.json"


def start_full_trial() -> Dict[str, Any]:
    """Start 7-day Full Pro trial.

    Returns:
        dict with started_at, machine_id, remaining_days
    """
    path = _get_full_trial_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    mid = get_machine_id()

    # Already started - don't overwrite
    if "started_at" in data and data.get("machine_id") == mid:
        return get_full_trial_status()

    data["started_at"] = datetime.now().isoformat()
    data["machine_id"] = mid

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    try:
        from .analytics import log_event
        log_event("full_trial_started", {"machine_id": mid[:8]})
    except Exception:
        pass

    return {
        "active": True,
        "started_at": data["started_at"],
        "remaining_days": FULL_TRIAL_DAYS,
        "message": f"Pro trial activated! {FULL_TRIAL_DAYS} days of full access.",
    }


def is_full_trial_active() -> bool:
    """Check if Full Pro trial is still active."""
    status = get_full_trial_status()
    return status.get("active", False)


def get_full_trial_status() -> Dict[str, Any]:
    """Get full trial status with remaining days.

    Returns:
        dict with active, started_at, remaining_days, elapsed_days
    """
    path = _get_full_trial_path()
    if not path.exists():
        return {"active": False, "remaining_days": 0, "never_started": True}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"active": False, "remaining_days": 0, "never_started": True}

    started_at = data.get("started_at")
    stored_mid = data.get("machine_id")
    if not started_at:
        return {"active": False, "remaining_days": 0, "never_started": True}

    # Machine ID mismatch = different machine, trial not valid
    current_mid = get_machine_id()
    if stored_mid and stored_mid != current_mid:
        return {"active": False, "remaining_days": 0, "machine_mismatch": True}

    try:
        start_time = datetime.fromisoformat(started_at)
        elapsed = (datetime.now() - start_time).days
        remaining = max(0, FULL_TRIAL_DAYS - elapsed)
        return {
            "active": remaining > 0,
            "started_at": started_at,
            "elapsed_days": elapsed,
            "remaining_days": remaining,
        }
    except Exception:
        return {"active": False, "remaining_days": 0}


# ============================================================
# A/B 테스트 플래그 (v3.3: 전환율 실험 확장)
# ============================================================

# Experiment configurations with multiple variants
# v3.3: Added rollout_percent for gradual traffic rollout (Week 3)
EXPERIMENTS = {
    "meeting_quota": {
        "variants": ["control", "variant_a"],
        "description": "Meeting quota for additional projects: weekly vs monthly 3",
        "values": {"control": "weekly", "variant_a": "monthly_3"},
        "rollout_percent": 50,
        "started_at": "2026-02-01",
    },
    "kb_retention": {
        "variants": ["control", "variant_a"],
        "description": "KB retention for additional projects: unlimited vs 7 days",
        "values": {"control": "unlimited", "variant_a": "7_days"},
        "rollout_percent": 50,
        "started_at": "2026-02-01",
    },
    "pain_point_message": {
        "variants": ["control", "variant_a"],
        "description": "Message style: simple vs detailed",
        "values": {"control": "simple", "variant_a": "detailed"},
        "rollout_percent": 100,  # Full rollout - low risk
        "started_at": "2026-02-01",
    },
}


def _get_ab_flags_path() -> Path:
    """Get A/B test flags file path: ~/.clouvel/ab_flags.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "ab_flags.json"


def get_ab_group(experiment_name: str) -> str:
    """Get A/B test group for an experiment (legacy).

    Returns "control" or "treatment". Assignment is random on first call
    and persisted for consistency.
    """
    return get_experiment_variant(experiment_name)


def is_in_rollout(experiment_name: str, user_id: str = None) -> bool:
    """Check if user is in the experiment's rollout percentage.

    v3.3: Gradual traffic rollout control.
    - 10% rollout: only 10% of users see the experiment
    - 50% rollout: 50% of users see the experiment
    - 100% rollout: all users see the experiment

    Users not in rollout get "control" behavior.
    """
    if user_id is None:
        user_id = get_machine_id()

    config = EXPERIMENTS.get(experiment_name, {})
    rollout_percent = config.get("rollout_percent", 100)

    # Hash user_id + experiment to get deterministic 0-99 value
    hash_input = f"{user_id}:rollout:{experiment_name}".encode()
    hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16) % 100

    return hash_value < rollout_percent


def get_experiment_variant(experiment_name: str, user_id: str = None) -> str:
    """Get experiment variant with deterministic assignment.

    v3.3: Uses hash-based assignment for consistency across sessions.
    Supports multiple variants per experiment and rollout control.

    Args:
        experiment_name: Name of the experiment
        user_id: Optional user ID for deterministic assignment

    Returns:
        Variant name (e.g., "control", "variant_a", "variant_b")
    """
    path = _get_ab_flags_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    # Check if already assigned
    experiments = data.get("experiments", {})
    if experiment_name in experiments:
        return experiments[experiment_name]["variant"]

    # Get experiment config
    config = EXPERIMENTS.get(experiment_name, {
        "variants": ["control", "treatment"],
        "description": "Unknown experiment",
    })
    variants = config.get("variants", ["control", "treatment"])

    # Deterministic assignment based on machine_id + experiment name
    if user_id is None:
        user_id = get_machine_id()

    # v5.1: Detect license tier for analytics filtering
    # Pro-equivalent users get variant assigned but marked as "pro" to avoid data contamination
    _license_tier = "free"
    try:
        if is_developer():
            _license_tier = "developer"
        elif is_full_trial_active():
            _license_tier = "trial"
        else:
            cached = load_license_cache()
            if cached and cached.get("tier"):
                _license_tier = "pro"
    except Exception:
        pass

    # v3.3: Check rollout percentage first
    if not is_in_rollout(experiment_name, user_id):
        variant = "control"  # Users not in rollout get control
    else:
        hash_input = f"{user_id}:{experiment_name}".encode()
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
        variant = variants[hash_value % len(variants)]

    # Save assignment
    if "experiments" not in data:
        data["experiments"] = {}
    data["experiments"][experiment_name] = {
        "variant": variant,
        "assigned_at": datetime.now().isoformat(),
        "user_id_hash": user_id[:8],
        "license_tier": _license_tier,
    }

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    # Log assignment
    try:
        from .analytics import log_event
        log_event("experiment_assigned", {
            "experiment": experiment_name,
            "variant": variant,
            "user_id_hash": user_id[:8],
            "license_tier": _license_tier,
        })
    except Exception:
        pass

    return variant


def get_experiment_value(experiment_name: str) -> Any:
    """Get the actual value for the current variant.

    Example:
        value = get_experiment_value("project_limit")  # Returns 1, 2, or 3
    """
    variant = get_experiment_variant(experiment_name)
    config = EXPERIMENTS.get(experiment_name, {})
    values = config.get("values", {})
    return values.get(variant, values.get("control"))


def get_all_experiment_assignments() -> Dict[str, Any]:
    """Get all experiment assignments for the current user."""
    path = _get_ab_flags_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("experiments", {})
    except Exception:
        return {}


def track_conversion_event(experiment_name: str, event_type: str, metadata: Dict = None) -> None:
    """Track a conversion event for A/B testing.

    Args:
        experiment_name: The experiment this event is for
        event_type: Type of event (e.g., "upgrade_prompt_shown", "pro_conversion")
        metadata: Additional data about the event
    """
    variant = get_experiment_variant(experiment_name)

    event_data = {
        "experiment": experiment_name,
        "variant": variant,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    }

    # Log to analytics
    try:
        from .analytics import log_event
        log_event(f"ab_{event_type}", event_data)
    except Exception:
        pass

    # Also save to local file for offline analysis
    path = _get_ab_flags_path()
    try:
        data = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))

        if "events" not in data:
            data["events"] = []

        # Keep last 100 events
        data["events"].append(event_data)
        data["events"] = data["events"][-100:]

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
