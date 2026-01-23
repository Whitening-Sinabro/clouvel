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

# Manager 도구 (Pro 기능 - 폴더가 없으면 스킵)
try:
    from .manager import (
        manager,
        ask_manager,
        list_managers,
        MANAGERS,
    )
    _HAS_MANAGER = True
except ImportError:
    _HAS_MANAGER = False
    manager = None
    ask_manager = None
    list_managers = None
    MANAGERS = {}

from .ship import (
    ship,
    quick_ship,
    full_ship,
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
    # manager (Pro, v1.2)
    "manager", "ask_manager", "list_managers", "MANAGERS",
    # ship (Pro, v1.2)
    "ship", "quick_ship", "full_ship",
    # errors (Pro, v1.4, v2.0)
    "error_record", "error_check", "error_learn", "log_error", "analyze_error", "get_error_summary",
    "error_search", "error_resolve", "error_get", "error_stats",
]
