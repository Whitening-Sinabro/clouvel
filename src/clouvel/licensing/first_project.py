# -*- coding: utf-8 -*-
"""Licensing First Project Module

First Project Unlimited (Reverse Trial) logic.
v3.0.0: 첫 프로젝트에 모든 Pro 기능 제공.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .core import is_developer
from .validation import get_machine_id, load_license_cache
from .trial import is_full_trial_active


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
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def register_first_project(project_path: str) -> Dict[str, Any]:
    """Register the first project (one-time, per machine).

    v4.0: Server-first registration (immutable on server).
    Auto-migration: If projects.json has 1 active project and no
    first_project.json exists, auto-register that project.

    Returns:
        dict with path_hash, machine_id, registered_at, version
    """
    fp_path = _get_first_project_path()

    # Already registered -- don't overwrite
    existing = get_first_project()
    if existing is not None:
        return existing

    normalized = str(Path(project_path).resolve())
    path_hash = _hash_path(normalized)
    mid = get_machine_id()

    # 1. Try server registration
    try:
        from .sync import SyncState
        result = SyncState.get().register_project(path_hash)
        if result and result.get("registered"):
            # Server accepted — save locally
            data = {
                "path": normalized,
                "path_hash": result.get("path_hash", path_hash),
                "machine_id": mid,
                "registered_at": datetime.now().isoformat(),
                "version": "3.0.0",
            }
            try:
                fp_path.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            except OSError:
                pass
            return data
    except (ImportError, OSError, ConnectionError, ValueError):
        pass

    # 2. Fallback: local registration
    data = {
        "path": normalized,
        "path_hash": path_hash,
        "machine_id": mid,
        "registered_at": datetime.now().isoformat(),
        "version": "3.0.0",
    }

    try:
        fp_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except OSError:
        pass

    # Queue for next sync
    try:
        from .sync import mark_pending_sync
        mark_pending_sync("project_register", {"path_hash": path_hash})
    except (ImportError, OSError):
        pass

    # Log event
    try:
        from ..analytics import log_event
        log_event("first_project_registered", {
            "path_hash": data["path_hash"][:8],
            "machine_id": data["machine_id"][:8],
        })
    except (ImportError, OSError):
        pass

    return data


def _auto_migrate_first_project() -> Optional[str]:
    """Auto-migrate: if projects.json has exactly 1 active project, return its path.

    Called during get_project_tier when no first_project.json exists.
    """
    # Import here to avoid circular dependency with projects.py
    from .projects import load_projects
    try:
        data = load_projects()
        projects = data.get("projects", [])
        active = [p for p in projects if p.get("status") == "active"]
        if len(active) == 1:
            return active[0].get("path")
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return None


def get_project_tier(project_path: str) -> str:
    """Get tier for a specific project.

    v4.0: Server state used for immutable first-project verification.

    Returns:
        "pro"        -- Pro license / developer / trial active
        "first"      -- First project (all Pro features)
        "additional" -- Second+ project (Pro required)
    """
    # 1) Developer/License/Trial -> "pro"
    if is_developer():
        return "pro"

    cached = load_license_cache()
    if cached and cached.get("tier"):
        return "pro"

    if is_full_trial_active():
        return "pro"

    # 2) Check server state for first project (immutable)
    normalized = str(Path(project_path).resolve())
    current_hash = _hash_path(normalized)
    try:
        from .sync import SyncState
        ss = SyncState.get()
        if ss.is_synced():
            fp_server = ss.get_first_project()
            if fp_server and fp_server.get("locked") and fp_server.get("path_hash"):
                if fp_server["path_hash"] == current_hash:
                    return "first"
                return "additional"
    except (ImportError, OSError):
        pass

    # 3) Fallback: local first project check
    first = get_first_project()

    if first is None:
        # Auto-migration: check projects.json for existing single active project
        migrated_path = _auto_migrate_first_project()
        if migrated_path:
            register_first_project(migrated_path)
            first = get_first_project()
            if first and first.get("path_hash") == current_hash:
                return "first"
            elif first:
                return "additional"
        # No migration candidate -- register current project as first
        register_first_project(normalized)
        return "first"

    if first.get("path_hash") == current_hash:
        return "first"

    # Machine ID mismatch -> additional (anti-abuse)
    if first.get("machine_id") != get_machine_id():
        return "additional"

    return "additional"
