# -*- coding: utf-8 -*-
"""License Common Module (SHIM)

이 파일은 하위 호환성을 위한 SHIM입니다.
실제 구현은 licensing/ 서브패키지에 있습니다.

모든 기존 import는 그대로 동작합니다:
    from .license_common import is_developer
    from .license_common import get_machine_id
    등

사이드이펙트 방지:
- 이 파일은 수정하지 마세요
- 새 함수/상수 추가는 licensing/ 서브패키지에서 하세요
- 추가 후 이 파일과 licensing/__init__.py에 re-export 추가
"""

# Re-export everything from the licensing subpackage
from .licensing import (  # noqa: F401
    # === core.py ===
    is_developer,
    DEV_TIER_INFO,
    get_license_path,
    DEFAULT_TIER,
    TIER_INFO,
    get_tier_info,
    guess_tier_from_key,
    # === validation.py ===
    get_machine_id,
    load_license_cache,
    save_license_cache,
    delete_license_cache,
    PREMIUM_UNLOCK_DAYS,
    calculate_license_status,
    create_license_data,
    # === trial.py ===
    FULL_TRIAL_DAYS,
    start_full_trial,
    is_full_trial_active,
    get_full_trial_status,
    _get_full_trial_path,
    # === first_project.py ===
    get_first_project,
    register_first_project,
    get_project_tier,
    _get_first_project_path,
    _hash_path,
    _auto_migrate_first_project,
    # === projects.py ===
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
    _get_project_limit_message,
    # === quotas.py ===
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
    _get_warn_count_path,
    _get_kb_trial_path,
    _get_weekly_meeting_path,
    _get_monthly_meeting_path,
    # === experiments.py ===
    EXPERIMENTS,
    get_ab_group,
    is_in_rollout,
    get_experiment_variant,
    get_experiment_value,
    get_all_experiment_assignments,
    track_conversion_event,
    _get_ab_flags_path,
    # === sync.py (v4.0) ===
    SyncState,
    mark_pending_sync,
)
