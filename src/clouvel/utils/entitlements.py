# src/clouvel/utils/entitlements.py
"""Runtime entitlement checks for Clouvel.

Solves the MCP environment variable timing issue:
- Module-time constants (_IS_DEVELOPER) are evaluated at import
- MCP may inject env vars AFTER import
- This module uses runtime functions instead of constants

v3.2: project_path based detection for MCP compatibility.
"""
from __future__ import annotations
import os
from pathlib import Path

_TRUE = {"1", "true", "yes", "y", "on", "enable", "enabled", "dev"}


def env_flag(*names: str) -> bool:
    """Check if any of the given env vars is truthy."""
    for name in names:
        v = os.getenv(name)
        if v is None:
            continue
        if v.strip().lower() in _TRUE:
            return True
    return False


def is_clouvel_repo(project_path: str | None) -> bool:
    """Check if project_path is the clouvel repository.

    Detection methods:
    1. src/clouvel folder exists (development repo structure)
    2. pyproject.toml with clouvel project name
    3. .git folder with clouvel remote
    """
    if not project_path:
        return False

    p = Path(project_path)
    if not p.exists():
        return False

    # 1) src/clouvel folder exists (primary indicator)
    if (p / "src" / "clouvel").exists():
        return True

    # 2) Check pyproject.toml for clouvel project
    pyproject = p / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if 'name = "clouvel"' in content or "name = 'clouvel'" in content:
                return True
        except Exception:
            pass

    # 3) .git with clouvel in remote (optional extra check)
    git_dir = p / ".git"
    if git_dir.exists():
        config_file = git_dir / "config"
        if config_file.exists():
            try:
                content = config_file.read_text(encoding="utf-8")
                if "clouvel" in content.lower():
                    return True
            except Exception:
                pass

    return False


def is_developer(project_path: str | None = None) -> bool:
    """Runtime developer mode check.

    Priority:
    1. ENV explicit: CLOUVEL_DEV=1 or CLOUVEL_DEV_MODE=1
    2. project_path is clouvel repo (MCP-friendly auto-detection)

    This ensures MCP can work without env vars if project_path is provided.
    """
    # 1) env explicit takes priority
    if env_flag("CLOUVEL_DEV_MODE", "CLOUVEL_DEV"):
        return True

    # 2) project_path based auto-detection (MCP-friendly)
    return is_clouvel_repo(project_path)


def pro_enabled_by_env() -> bool:
    """Check if Pro features are enabled by environment only.

    DEPRECATED: Use is_developer(project_path) or can_use_pro() instead.
    Kept for backward compatibility.
    """
    return env_flag("CLOUVEL_DEV_MODE", "CLOUVEL_DEV")


def has_valid_license() -> bool:
    """Check for valid license (non-env based).

    Delegates to license_common if available.
    """
    try:
        from ..license_common import check_license_status
        status = check_license_status()
        return status.get("valid", False)
    except (ImportError, Exception):
        return False


def can_use_pro(project_path: str | None = None, license_checker: callable = None) -> bool:
    """Combined check: env-based OR path-based OR license-based OR first-project Pro access.

    Args:
        project_path: Project path for auto-detection (MCP-friendly)
        license_checker: Optional callable that returns bool for license validity
                        If None, uses has_valid_license()

    Returns:
        True if Pro features should be enabled
    """
    # 1) Developer mode (env or path-based)
    if is_developer(project_path):
        return True

    # 2) First project tier check (v3.0.0: Reverse Trial)
    if project_path:
        try:
            from ..license_common import get_project_tier
            if get_project_tier(project_path) in ("pro", "first"):
                return True
        except ImportError:
            pass

    # 3) License check
    if license_checker is not None:
        return license_checker()
    return has_valid_license()
