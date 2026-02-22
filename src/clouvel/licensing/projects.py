# -*- coding: utf-8 -*-
"""Licensing Projects Module

Feature availability checking and project tracking.
v3.0: Feature availability & project tracking.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .core import is_developer
from .validation import get_machine_id, load_license_cache
from .trial import is_full_trial_active, get_full_trial_status
from .first_project import (
    get_first_project,
    get_project_tier,
)


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
        except (OSError, json.JSONDecodeError, ValueError):
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
    except OSError:
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
    except (OSError, json.JSONDecodeError, ValueError):
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
        from ..analytics import log_event
        log_event("project_limit_hit", {
            "active_count": 1,
            "limit": FREE_ACTIVE_PROJECT_LIMIT,
            "active_project": first_path,
            "project_tier": "additional",
            "user_id_hash": get_machine_id()[:8],
        })
    except (ImportError, OSError):
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
        from ..analytics import log_event
        log_event("project_archived", {"path": normalized_path[:50]})
    except (ImportError, OSError):
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
        from ..analytics import log_event
        log_event("project_reactivated", {
            "path": normalized_path[:50],
            "swapped": previously_active is not None
        })
    except (ImportError, OSError):
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
