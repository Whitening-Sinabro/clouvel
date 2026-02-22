# -*- coding: utf-8 -*-
"""
Clouvel MCP Server v5.1.0
MCP server that remembers AI mistakes and prevents regressions

Thin hub: delegates to tool_schemas, tool_dispatch, and cli modules.
"""

import os

from mcp.server import Server
from mcp.types import Tool, TextContent


def _bootstrap_env() -> None:
    """Bootstrap environment before tool imports.

    MCP environments may inject env vars AFTER module import.
    This syncs CLOUVEL_DEV and CLOUVEL_DEV_MODE to avoid timing issues.
    """
    dev = os.getenv("CLOUVEL_DEV")
    dev_mode = os.getenv("CLOUVEL_DEV_MODE")

    # Sync: if one is set, copy to the other
    if dev_mode is None and dev is not None:
        os.environ["CLOUVEL_DEV_MODE"] = dev
    if dev is None and dev_mode is not None:
        os.environ["CLOUVEL_DEV"] = dev_mode


# MUST run before tool imports
_bootstrap_env()

from .tool_schemas import TOOL_DEFINITIONS
from .tool_dispatch import (
    TOOL_HANDLERS,
    _get_list_tools_tier,
    _get_call_tool_tier,
    _check_version_once,
    _ensure_sync_once,
    _get_analytics,
    _get_ab_report,
    _get_monthly_report,
    _decide_winner,
)
from .registry import filter_tools_by_tier, is_tool_allowed, get_redirect_message
from .version_check import get_cached_update_info, get_update_banner
from .analytics import log_tool_call

server = Server("clouvel")

# Version check state
_version_check_done = False


@server.list_tools()
async def list_tools() -> list[Tool]:
    # Debug override: show all tools (for development/testing)
    if os.getenv("CLOUVEL_SHOW_ALL_TOOLS"):
        return TOOL_DEFINITIONS

    tier = _get_list_tools_tier()
    return filter_tools_by_tier(TOOL_DEFINITIONS, tier)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    global _version_check_done

    # First call: version check + server sync (any tool)
    if not _version_check_done:
        _check_version_once()
        _ensure_sync_once()
        _version_check_done = True

    # Deprecated tool redirect
    redirect = get_redirect_message(name)
    if redirect:
        return [TextContent(type="text", text=f"⚠️ `{name}` is deprecated.\n\n{redirect}")]

    # Defense-in-depth: PRO tool gating
    project_path = arguments.get("path", arguments.get("project_path", None))
    if project_path and not is_tool_allowed(name, _get_call_tool_tier(project_path)):
        return [TextContent(type="text", text=(
            f"`{name}` requires **Clouvel Pro**.\n\n"
            "Start a free 7-day trial: `license_status(action=\"trial\")`"
        ))]

    # Analytics logging
    if name != "get_analytics":
        try:
            log_tool_call(name, success=True, project_path=project_path)
        except Exception:
            pass

    # Special analytics handlers
    if name == "get_analytics":
        return await _get_analytics(arguments.get("path", None), arguments.get("days", 30))
    if name == "get_ab_report":
        return await _get_ab_report(arguments.get("days", 7), arguments.get("experiment"))
    if name == "get_monthly_report":
        return await _get_monthly_report(arguments.get("days", 30))
    if name == "decide_winner":
        return await _decide_winner(
            arguments.get("experiment", ""),
            arguments.get("min_confidence", "medium")
        )

    # Dispatch to handler
    handler = TOOL_HANDLERS.get(name)
    if handler:
        result = await handler(arguments)

        # Update banner on first call
        update_info = get_cached_update_info()
        if update_info and update_info.get("update_available"):
            banner = get_update_banner()
            if banner and result and len(result) > 0:
                original_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                result[0] = TextContent(type="text", text=banner + "\n" + original_text)
                update_info["update_available"] = False

        return result

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# Backward compatibility re-exports
# (tests and other modules may import these from server)
from .cli import main, run_server, _run_setup  # noqa: F401, E402
from .tool_dispatch import (  # noqa: F401, E402
    _is_pro, _apply_free_error_limit, _append_ghost_data,
)

# Re-export FREE_ERROR_LIMIT if it exists in tool_dispatch
try:
    from .tool_dispatch import FREE_ERROR_LIMIT  # noqa: F401, E402
except ImportError:
    pass
