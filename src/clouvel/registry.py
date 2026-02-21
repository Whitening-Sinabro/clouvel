# -*- coding: utf-8 -*-
"""
Clouvel Tool Registry v5.0.0

Tool visibility filtering by license tier.
Controls which tools appear in list_tools() for the MCP client.

Architecture:
  - TOOL_TIERS: maps tool name → ToolTier
  - filter_tools(): filters TOOL_DEFINITIONS by current license tier
  - get_redirect(): returns new tool name for deprecated tools
"""

from enum import Enum
from typing import Optional


class ToolTier(Enum):
    """Tool visibility tier."""
    CORE = "core"              # Always visible (Free users)
    PRO = "pro"                # Visible only to Pro users
    INTERNAL = "internal"      # Never exposed via MCP (used internally)
    DEPRECATED = "deprecated"  # Returns redirect message


# ============================================================
# Tool → Tier Mapping
# ============================================================
# Total: ~95 tools
# CORE: 10 tools (visible to Free users)
# PRO: 10 tools (visible to Pro users only)
# INTERNAL: ~60 tools (not exposed via MCP)
# DEPRECATED: ~5 tools (redirect to new tool)
# LEGACY: ~10 tools (kept for now, hidden)

TOOL_TIERS: dict[str, ToolTier] = {
    # ── CORE (10) ── Always visible ──────────────────────
    "can_code":           ToolTier.CORE,
    "start":              ToolTier.CORE,
    "save_prd":           ToolTier.CORE,
    "error_check":        ToolTier.CORE,
    "error_record":       ToolTier.CORE,
    "context_save":       ToolTier.CORE,
    "context_load":       ToolTier.CORE,
    "quick_perspectives": ToolTier.CORE,
    "gate":               ToolTier.CORE,
    "license_status":     ToolTier.CORE,

    # ── PRO (10) ── Visible to Pro users ─────────────────
    "error_learn":          ToolTier.PRO,   # natural upgrade: error_record → learn patterns
    "memory_status":        ToolTier.PRO,   # natural upgrade: error tracking → memory dashboard
    "memory_search":        ToolTier.PRO,   # natural upgrade: search past errors
    "memory_global_search": ToolTier.PRO,   # natural upgrade: cross-project patterns
    "drift_check":          ToolTier.PRO,   # natural upgrade: context_save → drift detection
    "record_decision":      ToolTier.PRO,   # persistent knowledge base
    "search_knowledge":     ToolTier.PRO,   # search knowledge base
    "plan":                 ToolTier.PRO,   # detailed execution plans
    "meeting":              ToolTier.PRO,   # natural upgrade: quick_perspectives → full meeting
    "ship":                 ToolTier.PRO,   # natural upgrade: gate → one-click ship + evidence

    # ── INTERNAL ── Not exposed via MCP ──────────────────
    # Core internals (absorbed into core tools)
    "scan_docs":         ToolTier.INTERNAL,
    "analyze_docs":      ToolTier.INTERNAL,
    "init_docs":         ToolTier.INTERNAL,

    # Docs internals
    "get_prd_template":    ToolTier.INTERNAL,
    "list_templates":      ToolTier.INTERNAL,
    "write_prd_section":   ToolTier.INTERNAL,
    "get_prd_guide":       ToolTier.INTERNAL,
    "get_verify_checklist": ToolTier.INTERNAL,
    "get_setup_guide":     ToolTier.INTERNAL,

    # Setup
    "init_clouvel":  ToolTier.INTERNAL,
    "setup_cli":     ToolTier.INTERNAL,

    # Rules
    "init_rules":  ToolTier.INTERNAL,
    "get_rule":    ToolTier.INTERNAL,
    "add_rule":    ToolTier.INTERNAL,

    # Verify (gate absorbs these)
    "verify":   ToolTier.INTERNAL,
    "handoff":  ToolTier.INTERNAL,
    "quick_ship": ToolTier.INTERNAL,
    "full_ship":  ToolTier.INTERNAL,

    # Planning (context_save/load absorbs these)
    "init_planning":  ToolTier.INTERNAL,
    "save_finding":   ToolTier.INTERNAL,
    "refresh_goals":  ToolTier.INTERNAL,
    "update_progress": ToolTier.INTERNAL,

    # Knowledge internals
    "record_location":      ToolTier.INTERNAL,
    "get_context":          ToolTier.INTERNAL,
    "init_knowledge":       ToolTier.INTERNAL,
    "rebuild_index":        ToolTier.INTERNAL,
    "unlock_decision":      ToolTier.INTERNAL,
    "list_locked_decisions": ToolTier.INTERNAL,

    # Tracking
    "record_file": ToolTier.INTERNAL,
    "list_files":  ToolTier.INTERNAL,

    # Manager internals
    "manager":       ToolTier.INTERNAL,
    "list_managers":  ToolTier.INTERNAL,

    # Architecture
    "arch_check":       ToolTier.INTERNAL,
    "check_imports":    ToolTier.INTERNAL,
    "check_duplicates": ToolTier.INTERNAL,
    "check_sync":       ToolTier.INTERNAL,

    # Debug
    "debug_runtime": ToolTier.INTERNAL,

    # Proactive internals
    "pattern_watch": ToolTier.INTERNAL,
    "auto_remind":   ToolTier.INTERNAL,

    # Meeting internals
    "meeting_topics":      ToolTier.INTERNAL,
    "rate_meeting":        ToolTier.INTERNAL,
    "get_meeting_stats":   ToolTier.INTERNAL,
    "export_training_data": ToolTier.INTERNAL,
    "enable_ab_testing":    ToolTier.INTERNAL,
    "disable_ab_testing":   ToolTier.INTERNAL,
    "get_variant_performance": ToolTier.INTERNAL,
    "list_variants":        ToolTier.INTERNAL,
    "configure_meeting":    ToolTier.INTERNAL,
    "add_persona_override": ToolTier.INTERNAL,
    "get_meeting_config":   ToolTier.INTERNAL,
    "reset_meeting_config": ToolTier.INTERNAL,

    # Memory internals (memory_status absorbs)
    "memory_list":    ToolTier.INTERNAL,
    "memory_archive": ToolTier.INTERNAL,
    "memory_report":  ToolTier.INTERNAL,
    "memory_promote": ToolTier.INTERNAL,
    "set_project_domain": ToolTier.INTERNAL,

    # Project management
    "archive_project": ToolTier.INTERNAL,
    "list_projects":   ToolTier.INTERNAL,

    # License internals (license_status absorbs)
    "activate_license": ToolTier.INTERNAL,
    "start_trial":      ToolTier.INTERNAL,
    "upgrade_pro":      ToolTier.INTERNAL,

    # Analytics (internal only)
    "get_analytics":     ToolTier.INTERNAL,
    "get_ab_report":     ToolTier.INTERNAL,
    "get_monthly_report": ToolTier.INTERNAL,
    "decide_winner":     ToolTier.INTERNAL,

    # ── DEPRECATED ── Redirect to new tool ───────────────
    "spawn_explore":   ToolTier.DEPRECATED,
    "spawn_librarian": ToolTier.DEPRECATED,
    "hook_design":     ToolTier.DEPRECATED,
    "hook_verify":     ToolTier.DEPRECATED,
    "quick_start":     ToolTier.DEPRECATED,
}

# Redirect map: deprecated tool → replacement info
TOOL_REDIRECTS: dict[str, str] = {
    "spawn_explore":   "Use Claude Code's Task tool with subagent_type='Explore' instead.",
    "spawn_librarian": "Use Claude Code's Task tool with subagent_type='Explore' instead.",
    "hook_design":     "Use Claude Code native hooks in .claude/settings.json instead.",
    "hook_verify":     "Use Claude Code native hooks in .claude/settings.json instead.",
    "quick_start":     "Use 'start' tool instead.",
}


# ============================================================
# Filtering Functions
# ============================================================

def get_tool_tier(name: str) -> ToolTier:
    """Get tier for a tool. Defaults to INTERNAL if not mapped."""
    return TOOL_TIERS.get(name, ToolTier.INTERNAL)


def filter_tools_by_tier(tools: list, tier: str) -> list:
    """Filter TOOL_DEFINITIONS list by license tier.

    Args:
        tools: list of mcp.types.Tool objects
        tier: "pro" or "free"

    Returns:
        Filtered list of Tool objects
    """
    visible_tiers = {ToolTier.CORE}

    if tier == "pro":
        visible_tiers.add(ToolTier.PRO)

    return [t for t in tools if get_tool_tier(t.name) in visible_tiers]


def get_redirect_message(name: str) -> Optional[str]:
    """Get redirect message for deprecated tools."""
    return TOOL_REDIRECTS.get(name)


def is_tool_allowed(name: str, tier: str) -> bool:
    """Check if a tool is allowed for the given tier.

    Used in call_tool() as defense-in-depth.
    Internal/deprecated tools are always callable (for backward compat).
    Only PRO tools are gated — requires "pro" tier (license/trial/developer).
    """
    tool_tier = get_tool_tier(name)

    if tool_tier == ToolTier.PRO and tier != "pro":
        return False

    return True


# ============================================================
# Stats (for debugging)
# ============================================================

def get_tier_stats() -> dict[str, int]:
    """Count tools per tier."""
    stats: dict[str, int] = {}
    for tier_val in TOOL_TIERS.values():
        key = tier_val.value
        stats[key] = stats.get(key, 0) + 1
    return stats
