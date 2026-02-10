# Clouvel Tools Package
# 모듈별로 도구 구현을 분리
# Free 기능만 포함 (v0.8까지)

from .core import (
    can_code,
    scan_docs,
    analyze_docs,
    init_docs,
    REQUIRED_DOCS,
)

from .docs import (
    get_prd_template,
    list_templates,
    write_prd_section,
    get_prd_guide,
    get_verify_checklist,
    get_setup_guide,
)

from .setup import (
    init_clouvel,
    setup_cli,
)

from .rules import (
    init_rules,
    get_rule,
    add_rule,
)

from .verify import (
    verify,
    gate,
    handoff,
)

from .planning import (
    init_planning,
    save_finding,
    refresh_goals,
    update_progress,
    create_detailed_plan,
)

from .agents import (
    spawn_explore,
    spawn_librarian,
)

from .hooks import (
    hook_design,
    hook_verify,
)

from .install import (
    run_install,
)

from .start import (
    start,
    quick_start,
    save_prd,
)

# Tracking 도구 (v1.5)
from .tracking import (
    record_file,
    list_files,
)

# Knowledge Base 도구 (Free, v1.4)
from .knowledge import (
    record_decision,
    record_location,
    search_knowledge,
    get_context,
    init_knowledge,
    rebuild_index,
    unlock_decision,
    list_locked_decisions,
)

# Manager 도구 (v1.8.0 - 단일 소스)
# 아키텍처 결정 #30: tools/__init__.py에서만 export, 중복 정의 금지
# tools/manager/에서 import하여 re-export
try:
    from .manager import (
        manager,
        ask_manager,
        list_managers,
        MANAGERS,
        quick_perspectives,
        generate_meeting_sync,  # Dynamic meeting generation
    )
    _HAS_MANAGER = True
except ImportError as e:
    # manager 모듈 로드 실패 시 fallback
    # Python 3에서 except 블록 종료 후 e가 삭제되므로 미리 저장
    _MANAGER_IMPORT_ERROR = str(e)
    _HAS_MANAGER = False
    MANAGERS = {}

    def manager(*args, _err=_MANAGER_IMPORT_ERROR, **kwargs):
        return {"error": f"Manager module not available: {_err}"}

    def ask_manager(*args, _err=_MANAGER_IMPORT_ERROR, **kwargs):
        return {"error": f"Manager module not available: {_err}"}

    def list_managers():
        return []

    def quick_perspectives(*args, _err=_MANAGER_IMPORT_ERROR, **kwargs):
        return {"error": f"Manager module not available: {_err}"}

    def generate_meeting_sync(*args, **kwargs):
        return "Manager module not available"

from .ship import (
    ship,
    quick_ship,
    full_ship,
)

# Architecture Guard 도구 (v1.8 + v3.1)
from .architecture import (
    arch_check,
    check_imports,
    check_duplicates,
    check_sync,  # v3.1: Sideeffect sync checker
)

# Proactive 도구 (v2.0)
from .proactive import (
    drift_check,
    pattern_watch,
    auto_remind,
)

# Meeting 도구 (Free, v2.1)
from .meeting import (
    meeting,
    meeting_topics,
)

# Meeting Feedback & Tuning (Free, v2.2)
from .meeting_feedback import (
    save_meeting,
    rate_meeting,
    get_meeting_stats,
    export_training_data,
)
from .meeting_tuning import (
    enable_ab_testing,
    disable_ab_testing,
    get_variant_performance,
    list_variants,
)

# Context Checkpoint (Free)
from .checkpoint import (
    context_save,
    context_load,
)

# Meeting Personalization (Free, v2.3)
from .meeting_personalization import (
    configure_meeting,
    add_persona_override,
    add_custom_prompt,
    get_meeting_config,
    reset_meeting_config,
)

# Error Learning 도구 (Pro 기능 - 파일이 없으면 스킵)
try:
    from .errors import (
        error_record,
        error_check,
        error_learn,
        log_error,
        analyze_error,
        get_error_summary,
        # v2.0 새 도구
        error_search,
        error_resolve,
        error_get,
        error_stats,
        # v4.0 Regression Memory
        memory_status,
        # v4.0 Phase 2
        memory_list,
        memory_search,
        memory_archive,
        memory_report,
        # v5.0 Cross-Project Memory Transfer
        memory_promote,
        memory_global_search,
        # v1.0 Domain scoping
        set_project_domain,
    )
    _HAS_ERRORS = True
except ImportError:
    _HAS_ERRORS = False
    error_record = None
    error_check = None
    error_learn = None
    log_error = None
    analyze_error = None
    get_error_summary = None
    error_search = None
    error_resolve = None
    error_get = None
    error_stats = None
    memory_status = None
    memory_list = None
    memory_search = None
    memory_archive = None
    memory_report = None
    memory_promote = None
    memory_global_search = None
    set_project_domain = None

# Pro 기능은 clouvel-pro 패키지로 분리됨
# pip install clouvel-pro

__all__ = [
    # core
    "can_code", "scan_docs", "analyze_docs", "init_docs", "REQUIRED_DOCS",
    # docs
    "get_prd_template", "list_templates", "write_prd_section", "get_prd_guide", "get_verify_checklist", "get_setup_guide",
    # setup
    "init_clouvel", "setup_cli",
    # rules (v0.5)
    "init_rules", "get_rule", "add_rule",
    # verify (v0.5)
    "verify", "gate", "handoff",
    # planning (v0.6, v1.3)
    "init_planning", "save_finding", "refresh_goals", "update_progress", "create_detailed_plan",
    # agents (v0.7)
    "spawn_explore", "spawn_librarian",
    # hooks (v0.8)
    "hook_design", "hook_verify",
    # install
    "run_install",
    # start (Free, v1.2)
    "start", "quick_start", "save_prd",
    # tracking (v1.5)
    "record_file", "list_files",
    # knowledge (Free, v1.4)
    "record_decision", "record_location", "search_knowledge", "get_context", "init_knowledge", "rebuild_index",
    "unlock_decision", "list_locked_decisions",
    # manager (Pro, v1.2)
    "manager", "ask_manager", "list_managers", "MANAGERS",
    # ship (Pro, v1.2)
    "ship", "quick_ship", "full_ship",
    # errors (Pro, v1.4, v2.0, v4.0)
    "error_record", "error_check", "error_learn", "log_error", "analyze_error", "get_error_summary",
    "error_search", "error_resolve", "error_get", "error_stats",
    "memory_status",
    "memory_list", "memory_search", "memory_archive", "memory_report",
    "memory_promote", "memory_global_search", "set_project_domain",
    # architecture (v1.8 + v3.1)
    "arch_check", "check_imports", "check_duplicates", "check_sync",
    # proactive (v2.0)
    "drift_check", "pattern_watch", "auto_remind",
    # meeting (Free, v2.1)
    "meeting", "meeting_topics",
    # meeting feedback & tuning (Free, v2.2)
    "save_meeting", "rate_meeting", "get_meeting_stats", "export_training_data",
    "enable_ab_testing", "disable_ab_testing", "get_variant_performance", "list_variants",
    # meeting personalization (Free, v2.3)
    "configure_meeting", "add_persona_override", "add_custom_prompt", "get_meeting_config", "reset_meeting_config",
    # context checkpoint (Free)
    "context_save", "context_load",
]
