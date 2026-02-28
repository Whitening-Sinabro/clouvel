# -*- coding: utf-8 -*-
"""Licensing Projects Module

Feature availability checking and project tracking.
v3.0: Feature availability & project tracking.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .paths import get_clouvel_file, load_json, save_json
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
    """v6.0: Always available — all features free."""
    return {"available": True, "reason": "free"}


def get_projects_path() -> Path:
    """Get projects tracking file path: ~/.clouvel/projects.json"""
    return get_clouvel_file("projects.json")


def load_projects() -> Dict[str, Any]:
    """Load registered projects from tracking file.

    v3.3: Migrates old format (list of paths) to new format (list of dicts).
    New format: {"projects": [{"path": "...", "status": "active"|"archived", "registered_at": "..."}]}
    """
    projects_path = get_projects_path()
    data = load_json(projects_path, None)
    if data is None:
        return {"projects": [], "last_updated": None}

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


def save_projects(data: Dict[str, Any]) -> bool:
    """Save projects data to tracking file."""
    data["last_updated"] = datetime.now().isoformat()
    return save_json(get_projects_path(), data)


def register_project(project_path: str) -> Dict[str, Any]:
    """v6.0: Always allowed — unlimited projects."""
    return {"allowed": True, "count": 0, "limit": 999, "is_new": False, "tier": "free"}


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
  All projects are now free in Clouvel v6.0!
  Your project ({first_name}) has full features.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    active_name = Path(active_projects[0].get("path", "Unknown")).name
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  All projects are now free in Clouvel v6.0!
  Your project ({active_name}) has full features.
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
