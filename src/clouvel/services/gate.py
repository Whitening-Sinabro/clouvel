# -*- coding: utf-8 -*-
"""Feature Gate Service — Pro gating and nudge logic.

Extracts repeated gating patterns from tool_dispatch.py _wrap_* functions.
"""

from typing import Optional
from mcp.types import TextContent

# Error tools availability (imported once, shared)
try:
    from ..tools.errors import (
        error_record, error_check, error_learn, memory_status,
        memory_list, memory_search, memory_archive, memory_report,
        memory_promote, memory_global_search,
        set_project_domain,
    )
    _HAS_ERROR_TOOLS = True
except ImportError:
    _HAS_ERROR_TOOLS = False


_PRO_ERROR_MSG = """
# Clouvel Pro Feature

Error Learning requires **Clouvel Pro**.

Start a free 7-day trial: `license_status(action="trial")`
"""

_PRO_MEMORY_MSG = (
    "# Clouvel Pro Feature\n\n"
    "Regression Memory requires **Clouvel Pro**.\n\n"
    'Start a free 7-day trial: `license_status(action="trial")`\n'
)

_PRO_CROSS_PROJECT_MSG = (
    "# Clouvel Pro Feature\n\n"
    "Cross-project memory requires **Clouvel Pro**.\n\n"
    'Start a free 7-day trial: `license_status(action="trial")`\n'
)

_PRO_DOMAIN_MSG = (
    "# Clouvel Pro Feature\n\n"
    "Domain scoping requires **Clouvel Pro**.\n\n"
    'Start a free 7-day trial: `license_status(action="trial")`\n'
)


def require_error_tools(feature_name: str = "error") -> Optional[list[TextContent]]:
    """Check if error tools are available. Returns block message or None.

    Replaces the 11x repeated `if not _HAS_ERROR_TOOLS` pattern.
    """
    if _HAS_ERROR_TOOLS:
        return None

    # Pick message based on feature name
    if feature_name in ("memory_promote", "memory_global_search"):
        msg = _PRO_CROSS_PROJECT_MSG
    elif feature_name == "set_project_domain":
        msg = _PRO_DOMAIN_MSG
    elif feature_name.startswith("memory"):
        msg = _PRO_MEMORY_MSG
    else:
        msg = _PRO_ERROR_MSG

    return [TextContent(type="text", text=msg)]


def require_kb_access(project_path: str) -> Optional[list[TextContent]]:
    """Check KB access. Returns block message or None.

    Replaces the duplicated KB trial gate in _wrap_record_decision
    and _wrap_record_location.
    """
    from .quota import check_kb_access
    result = check_kb_access(project_path)
    if not result.allowed:
        return [TextContent(type="text", text=result.message)]
    return None


def append_free_nudge(
    result: list[TextContent], project_path: str, tool_name: str
) -> list[TextContent]:
    """Append ghost data teaser to Free user's error tool output.

    Replaces _append_ghost_data in tool_dispatch.py.
    """
    from .tier import is_pro
    try:
        if is_pro(project_path):
            return result
    except Exception:
        return result

    teasers = {
        "error_record": (
            "\n\n---\n"
            "**Pro**: Auto-generate NEVER/ALWAYS rules from your error patterns "
            '→ `license_status(action="trial")`'
        ),
        "error_check": (
            "\n\n---\n"
            "**Pro**: Search all past errors by keyword + share lessons across projects "
            '→ `license_status(action="trial")`'
        ),
    }

    teaser = teasers.get(tool_name)
    if teaser and result and len(result) > 0:
        original = result[0].text if hasattr(result[0], 'text') else str(result[0])
        result[0] = TextContent(type="text", text=original + teaser)

    return result
