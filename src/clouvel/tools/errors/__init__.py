# -*- coding: utf-8 -*-
"""Error tools subpackage — re-exports all public functions.

Submodules:
  legacy.py  — log_error, analyze_error, watch_logs, check_logs,
                add_prevention_rule, get_error_summary
  core.py    — error_record, error_check, error_learn, error_search,
                error_resolve, error_get, error_stats
  memory.py  — memory_status, memory_list, memory_search, memory_archive,
                memory_report, memory_promote, memory_global_search,
                set_project_domain
"""

from .legacy import (
    log_error,
    analyze_error,
    watch_logs,
    check_logs,
    add_prevention_rule,
    get_error_summary,
)

from .core import (
    error_record,
    error_check,
    error_learn,
    error_search,
    error_resolve,
    error_get,
    error_stats,
)

from .memory import (
    memory_status,
    memory_list,
    memory_search,
    memory_archive,
    memory_report,
    memory_promote,
    memory_global_search,
    set_project_domain,
)

# Internal helpers (re-exported for tests)
from ._shared import (
    _get_error_log_path,
    _classify_error,
    _extract_stack_info,
    ERROR_PATTERNS,
)

__all__ = [
    # legacy
    "log_error",
    "analyze_error",
    "watch_logs",
    "check_logs",
    "add_prevention_rule",
    "get_error_summary",
    # core
    "error_record",
    "error_check",
    "error_learn",
    "error_search",
    "error_resolve",
    "error_get",
    "error_stats",
    # memory
    "memory_status",
    "memory_list",
    "memory_search",
    "memory_archive",
    "memory_report",
    "memory_promote",
    "memory_global_search",
    "set_project_domain",
]
