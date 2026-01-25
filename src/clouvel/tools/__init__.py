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

# Manager 도구 (API 기반 - v1.6.0)
# Pro 기능은 Cloudflare Workers API로 제공됨
from ..api_client import call_manager_api, get_trial_status as get_api_trial_status

def manager(
    context: str,
    mode: str = "auto",
    managers: list = None,
    include_checklist: bool = True,
    topic: str = None,
    **kwargs
):
    """
    8 C-Level manager feedback via API.

    Args:
        context: Content to review
        mode: 'auto', 'all', or 'specific'
        managers: List of managers when mode='specific'
        topic: Topic hint (auth, api, payment, etc.)

    Returns:
        Manager feedback and recommendations
    """
    return call_manager_api(
        context=context,
        topic=topic,
        mode=mode,
        managers=managers,
    )

def ask_manager(manager_key: str, question: str):
    """Ask a specific manager a question."""
    return call_manager_api(
        context=question,
        mode="specific",
        managers=[manager_key],
    )

def list_managers():
    """List available managers."""
    return [
        {"key": "PM", "emoji": "👔", "title": "Product Manager", "focus": "Scope & Requirements"},
        {"key": "CTO", "emoji": "🛠️", "title": "CTO", "focus": "Architecture & Tech Debt"},
        {"key": "QA", "emoji": "🧪", "title": "QA Lead", "focus": "Testing & Quality"},
        {"key": "CDO", "emoji": "🎨", "title": "Chief Design Officer", "focus": "UX & Accessibility"},
        {"key": "CMO", "emoji": "📢", "title": "CMO", "focus": "Launch & Positioning"},
        {"key": "CFO", "emoji": "💰", "title": "CFO", "focus": "Cost & ROI"},
        {"key": "CSO", "emoji": "🔒", "title": "CSO", "focus": "Security & Compliance"},
        {"key": "ERROR", "emoji": "🔥", "title": "Error Handler", "focus": "Error Handling & Recovery"},
    ]

MANAGERS = {m["key"]: m for m in list_managers()}
_HAS_MANAGER = True

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
    # tracking (v1.5)
    "record_file", "list_files",
    # knowledge (Free, v1.4)
    "record_decision", "record_location", "search_knowledge", "get_context", "init_knowledge", "rebuild_index",
    "unlock_decision", "list_locked_decisions",
    # manager (Pro, v1.2)
    "manager", "ask_manager", "list_managers", "MANAGERS",
    # ship (Pro, v1.2)
    "ship", "quick_ship", "full_ship",
    # errors (Pro, v1.4, v2.0)
    "error_record", "error_check", "error_learn", "log_error", "analyze_error", "get_error_summary",
    "error_search", "error_resolve", "error_get", "error_stats",
]
