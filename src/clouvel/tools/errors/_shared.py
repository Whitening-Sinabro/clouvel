# -*- coding: utf-8 -*-
"""Shared constants, imports, and helpers for the errors subpackage."""

import re
from pathlib import Path

# License module import (use Free stub if Pro version unavailable)
try:
    from ...license import require_license, require_license_premium
except ImportError:
    pass

# New DB module import (v2.0)
try:
    from ...db import (
        init_db,
        record_error as db_record_error,
        get_error as db_get_error,
        list_errors as db_list_errors,
        resolve_error as db_resolve_error,
        get_error_stats as db_get_error_stats,
        add_rule as db_add_rule,
        get_rules as db_get_rules,
        search_similar_errors as db_search_similar,
        is_vector_search_available,
        add_error_embedding,
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Regression Memory import (v4.0)
try:
    from ...db.regression import (
        normalize_error_signature,
        create_memory,
        match_all_levels,
        increment_hit_count,
        get_memory_stats as db_get_memory_stats,
        # v4.0 Phase 2
        list_memories as db_list_memories_reg,
        search_memories as db_search_memories,
        archive_memory as db_archive_memory,
        unarchive_memory as db_unarchive_memory,
        mark_stale_memories as db_mark_stale_memories,
        get_memory_report as db_get_memory_report,
        # v5.0: Cross-Project Memory Transfer
        get_memory as db_get_memory,
        get_memory_for_promote as db_get_memory_for_promote,
    )
    REGRESSION_AVAILABLE = True
except ImportError:
    REGRESSION_AVAILABLE = False

# Global Memory import (v5.0)
try:
    from ...db.knowledge import (
        promote_memory as kb_promote_memory,
        search_global_memories as kb_search_global_memories,
        get_or_create_project as kb_get_or_create_project,
        increment_global_hit as kb_increment_global_hit,
        get_project_domain as kb_get_project_domain,
        set_project_domain as kb_set_project_domain,
    )
    GLOBAL_MEMORY_AVAILABLE = True
except ImportError:
    GLOBAL_MEMORY_AVAILABLE = False

# Error pattern definitions
ERROR_PATTERNS = {
    "type_error": {
        "patterns": [r"TypeError:", r"type\s+error", r"is not a function", r"undefined is not"],
        "category": "Type Error",
        "prevention": "Strengthen type checking, enable TypeScript strict mode"
    },
    "null_error": {
        "patterns": [r"null|undefined", r"Cannot read propert", r"is null", r"is undefined"],
        "category": "Null Reference",
        "prevention": "Use optional chaining, add null checks"
    },
    "import_error": {
        "patterns": [r"Cannot find module", r"Module not found", r"ImportError", r"ModuleNotFoundError"],
        "category": "Import Error",
        "prevention": "Verify dependencies, validate paths"
    },
    "syntax_error": {
        "patterns": [r"SyntaxError", r"Unexpected token", r"Parse error"],
        "category": "Syntax Error",
        "prevention": "Enable linter, format on save"
    },
    "network_error": {
        "patterns": [r"ECONNREFUSED", r"fetch failed", r"NetworkError", r"timeout", r"ETIMEDOUT"],
        "category": "Network Error",
        "prevention": "Implement retry logic, configure timeouts"
    },
    "permission_error": {
        "patterns": [r"EACCES", r"Permission denied", r"PermissionError", r"403"],
        "category": "Permission Error",
        "prevention": "Check permissions, proper error handling"
    },
    "database_error": {
        "patterns": [r"SQLITE", r"PostgreSQL", r"MySQL", r"duplicate key", r"constraint violation"],
        "category": "Database Error",
        "prevention": "Use transactions, validate constraints"
    },
}


def _get_error_log_path(project_path: str) -> Path:
    """Get error log path."""
    return Path(project_path) / ".clouvel" / "errors"


def _classify_error(error_text: str) -> dict:
    """Classify error."""
    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, error_text, re.IGNORECASE):
                return {
                    "type": error_type,
                    "category": config["category"],
                    "prevention": config["prevention"]
                }

    return {
        "type": "unknown",
        "category": "Other Error",
        "prevention": "Analyze logs and add pattern"
    }


def _extract_stack_info(error_text: str) -> dict:
    """Extract information from stack trace."""
    info = {
        "file": None,
        "line": None,
        "function": None
    }

    # JavaScript/TypeScript pattern
    js_match = re.search(r'at\s+(\S+)\s+\(([^:]+):(\d+):', error_text)
    if js_match:
        info["function"] = js_match.group(1)
        info["file"] = js_match.group(2)
        info["line"] = js_match.group(3)
        return info

    # Python pattern
    py_match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\S+)', error_text)
    if py_match:
        info["file"] = py_match.group(1)
        info["line"] = py_match.group(2)
        info["function"] = py_match.group(3)
        return info

    return info
