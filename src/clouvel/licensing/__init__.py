# -*- coding: utf-8 -*-
"""Licensing Subpackage

Re-exports all public names from licensing sub-modules.
This package replaces the monolithic license_common.py.
"""

# === core.py: Developer detection, paths, tier defaults ===
from .core import (
    is_developer,
    DEV_TIER_INFO,
    get_license_path,
    DEFAULT_TIER,
    TIER_INFO,
    get_tier_info,
    guess_tier_from_key,
)

# === validation.py: Machine ID, license cache/status ===
from .validation import (
    get_machine_id,
    load_license_cache,
    save_license_cache,
    delete_license_cache,
    PREMIUM_UNLOCK_DAYS,
    calculate_license_status,
    create_license_data,
)

# === trial.py: Full Pro Trial ===
from .trial import (
    FULL_TRIAL_DAYS,
    start_full_trial,
    is_full_trial_active,
    get_full_trial_status,
)

# === first_project.py: First Project Unlimited logic ===
from .first_project import (
    get_first_project,
    register_first_project,
    get_project_tier,
    # Private but re-exported for backward compat with license_common shim
    _get_first_project_path,
    _hash_path,
    _auto_migrate_first_project,
)

# === projects.py: Feature availability, project tracking ===
from .projects import (
    PRO_ONLY_FEATURES,
    FREE_PROJECT_LIMIT,
    FREE_ACTIVE_PROJECT_LIMIT,
    FREE_LAYOUTS,
    PRO_LAYOUTS,
    is_feature_available,
    get_projects_path,
    load_projects,
    save_projects,
    register_project,
    get_project_count,
    archive_project,
    reactivate_project,
    list_projects,
    # Private but re-exported for backward compat
    _get_project_limit_message,
)

# === quotas.py: Warn counts, KB Trial, Meeting quotas ===
from .quotas import (
    increment_warn_count,
    get_warn_count,
    get_kb_trial_start,
    start_kb_trial,
    is_kb_trial_active,
    can_use_weekly_full_meeting,
    mark_weekly_meeting_used,
    FREE_MONTHLY_MEETINGS,
    check_meeting_quota,
    consume_meeting_quota,
    # Private but re-exported for backward compat
    _get_warn_count_path,
    _get_kb_trial_path,
    _get_weekly_meeting_path,
    _get_monthly_meeting_path,
)

# === experiments.py: A/B testing flags ===
from .experiments import (
    EXPERIMENTS,
    get_ab_group,
    is_in_rollout,
    get_experiment_variant,
    get_experiment_value,
    get_all_experiment_assignments,
    track_conversion_event,
    # Private but re-exported for backward compat
    _get_ab_flags_path,
)

# === sync.py: Server-side state synchronization (v4.0) ===
from .sync import (
    SyncState,
    mark_pending_sync,
)

# === Private trial helper (re-exported for backward compat) ===
from .trial import _get_full_trial_path


__all__ = [
    # core
    "is_developer",
    "DEV_TIER_INFO",
    "get_license_path",
    "DEFAULT_TIER",
    "TIER_INFO",
    "get_tier_info",
    "guess_tier_from_key",
    # validation
    "get_machine_id",
    "load_license_cache",
    "save_license_cache",
    "delete_license_cache",
    "PREMIUM_UNLOCK_DAYS",
    "calculate_license_status",
    "create_license_data",
    # trial
    "FULL_TRIAL_DAYS",
    "start_full_trial",
    "is_full_trial_active",
    "get_full_trial_status",
    # first_project
    "get_first_project",
    "register_first_project",
    "get_project_tier",
    # projects
    "PRO_ONLY_FEATURES",
    "FREE_PROJECT_LIMIT",
    "FREE_ACTIVE_PROJECT_LIMIT",
    "FREE_LAYOUTS",
    "PRO_LAYOUTS",
    "is_feature_available",
    "get_projects_path",
    "load_projects",
    "save_projects",
    "register_project",
    "get_project_count",
    "archive_project",
    "reactivate_project",
    "list_projects",
    # quotas
    "increment_warn_count",
    "get_warn_count",
    "get_kb_trial_start",
    "start_kb_trial",
    "is_kb_trial_active",
    "can_use_weekly_full_meeting",
    "mark_weekly_meeting_used",
    "FREE_MONTHLY_MEETINGS",
    "check_meeting_quota",
    "consume_meeting_quota",
    # experiments
    "EXPERIMENTS",
    "get_ab_group",
    "is_in_rollout",
    "get_experiment_variant",
    "get_experiment_value",
    "get_all_experiment_assignments",
    "track_conversion_event",
    # sync
    "SyncState",
    "mark_pending_sync",
    # private (backward compat)
    "_get_first_project_path",
    "_hash_path",
    "_auto_migrate_first_project",
    "_get_project_limit_message",
    "_get_warn_count_path",
    "_get_kb_trial_path",
    "_get_weekly_meeting_path",
    "_get_monthly_meeting_path",
    "_get_ab_flags_path",
    "_get_full_trial_path",
]
