# -*- coding: utf-8 -*-
"""
Clouvel MCP Server v4.0.0
MCP server that remembers AI mistakes and prevents regressions

Free version - For Pro features, see clouvel-pro package
"""

import os


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

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .analytics import log_tool_call, get_stats, format_stats
from .api_client import call_manager_api  # v1.8: Worker API 사용
from .version_check import get_v3_migration_notice, get_v1_pivot_notice  # v3.0 + v1.0 notices
from .tools import (
    # core
    can_code, scan_docs, analyze_docs, init_docs, REQUIRED_DOCS,
    # docs
    get_prd_template, list_templates, write_prd_section, get_prd_guide, get_verify_checklist, get_setup_guide,
    # setup
    init_clouvel, setup_cli,
    # rules (v0.5)
    init_rules, get_rule, add_rule,
    # verify (v0.5)
    verify, gate, handoff,
    # planning (v0.6, v1.3)
    init_planning, save_finding, refresh_goals, update_progress, create_detailed_plan,
    # agents (v0.7)
    spawn_explore, spawn_librarian,
    # hooks (v0.8)
    hook_design, hook_verify,
    # start (Free, v1.2)
    start, quick_start, save_prd,
    # tracking (v1.5)
    record_file, list_files,
    # knowledge (Free, v1.4)
    record_decision, record_location, search_knowledge, get_context, init_knowledge, rebuild_index,
    unlock_decision, list_locked_decisions,
    # manager (Pro, v1.2) - 아키텍처 결정: Worker API 사용 (call_manager_api)
    # manager, quick_perspectives, generate_meeting_sync 제거됨 - Worker API로 이동
    list_managers, MANAGERS,
    # ship (Pro, v1.2)
    ship, quick_ship, full_ship,
    # architecture (v1.8 + v3.1)
    arch_check, check_imports, check_duplicates, check_sync,
    # proactive (v2.0)
    drift_check, pattern_watch, auto_remind,
    # meeting (Free, v2.1)
    meeting, meeting_topics,
    # meeting feedback & tuning (Free, v2.2)
    rate_meeting, get_meeting_stats, export_training_data,
    enable_ab_testing, disable_ab_testing, get_variant_performance, list_variants,
    # meeting personalization (Free, v2.3)
    configure_meeting, add_persona_override, get_meeting_config, reset_meeting_config,
    # context checkpoint (Free)
    context_save, context_load,
)

# Error Learning tools (Pro feature - separate import)
try:
    from .tools.errors import (
        error_record, error_check, error_learn, memory_status,
        # v4.0 Phase 2
        memory_list, memory_search, memory_archive, memory_report,
        # v5.0 Cross-Project Memory Transfer
        memory_promote, memory_global_search,
        # v1.0 Domain scoping
        set_project_domain,
    )
    _HAS_ERROR_TOOLS = True
except ImportError:
    _HAS_ERROR_TOOLS = False
    error_record = None
    error_check = None
    error_learn = None
    memory_status = None
    memory_list = None
    memory_search = None
    memory_archive = None
    memory_report = None
    memory_promote = None
    memory_global_search = None
    set_project_domain = None
# License module import (use Free stub if Pro version not available)
try:
    from .license import activate_license_cli, get_license_status
except ImportError:
    from .license_free import activate_license_cli, get_license_status
from .version_check import init_version_check, get_cached_update_info, get_update_banner
from .registry import filter_tools_by_tier, is_tool_allowed, get_redirect_message

server = Server("clouvel")

# Version check on server start (processed asynchronously)
_version_check_done = False


# ============================================================
# Tool Definitions (Free - up to v0.8)
# ============================================================

TOOL_DEFINITIONS = [
    # === Core Tools ===
    Tool(
        name="can_code",
        description="Check before writing code. Verifies project docs exist so you don't start coding without a plan.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project docs folder path"},
                "mode": {"type": "string", "enum": ["pre", "post"], "description": "pre (default): check before coding, post: verify file tracking after coding"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="scan_docs",
        description="Scan project docs folder. Returns file list.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs folder path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="analyze_docs",
        description="Analyze docs folder. Check required documents.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs folder path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="init_docs",
        description="Initialize docs folder + generate templates.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "project_name": {"type": "string", "description": "Project name"}
            },
            "required": ["path", "project_name"]
        }
    ),

    # === Docs Tools ===
    Tool(
        name="get_prd_template",
        description="Generate PRD template. Choose template and layout.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name"},
                "output_path": {"type": "string", "description": "Output path"},
                "template": {"type": "string", "enum": ["web-app", "api", "cli", "generic"], "description": "Template type"},
                "layout": {"type": "string", "enum": ["lite", "standard", "detailed"], "description": "Layout (content amount)"}
            },
            "required": ["project_name", "output_path"]
        }
    ),
    Tool(
        name="list_templates",
        description="List available PRD templates.",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="write_prd_section",
        description="PRD section writing guide.",
        inputSchema={
            "type": "object",
            "properties": {
                "section": {"type": "string", "enum": ["summary", "principles", "input_spec", "output_spec", "errors", "state_machine", "api_endpoints", "db_schema"]},
                "content": {"type": "string", "description": "Section content"}
            },
            "required": ["section"]
        }
    ),
    Tool(name="get_prd_guide", description="PRD writing guide.", inputSchema={"type": "object", "properties": {}}),
    Tool(name="get_verify_checklist", description="Verification checklist.", inputSchema={"type": "object", "properties": {}}),
    Tool(
        name="get_setup_guide",
        description="Installation/setup guide.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "code", "vscode", "cursor", "all"]}}
        }
    ),
    Tool(
        name="get_analytics",
        description="Tool usage statistics.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project path"},
                "days": {"type": "integer", "description": "Query period (default: 30 days)"}
            }
        }
    ),
    Tool(
        name="get_ab_report",
        description="A/B testing analytics report. Shows experiment results, conversion rates, and recommendations. (v3.3)",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Analysis period in days (default: 7)"},
                "experiment": {"type": "string", "description": "Specific experiment name (optional, shows all if not specified)"}
            }
        }
    ),
    Tool(
        name="get_monthly_report",
        description="Monthly KPI dashboard with conversion funnel, pain point effectiveness, and recommendations. (v3.3 Week 4)",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Analysis period in days (default: 30)"}
            }
        }
    ),
    Tool(
        name="decide_winner",
        description="Analyze A/B test and decide if a winner can be promoted to 100% rollout. (v3.3 Week 4)",
        inputSchema={
            "type": "object",
            "properties": {
                "experiment": {"type": "string", "description": "Experiment name to analyze"},
                "min_confidence": {"type": "string", "enum": ["low", "medium", "high"], "description": "Minimum confidence level required (default: medium)"}
            },
            "required": ["experiment"]
        }
    ),

    # === Setup Tools ===
    Tool(
        name="init_clouvel",
        description="Clouvel onboarding. Custom setup after platform selection.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "vscode", "cli", "ask"]}}
        }
    ),
    Tool(
        name="setup_cli",
        description="CLI environment setup. Generate hooks, CLAUDE.md, pre-commit. Now includes: --rules, --hook, --proactive options. (v2.0 extended)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "level": {"type": "string", "enum": ["remind", "strict", "full"]},
                "rules": {"type": "string", "description": "Initialize rules (replaces init_rules)", "enum": ["web", "api", "fullstack", "minimal"]},
                "hook": {"type": "string", "description": "Create hook (replaces hook_design, hook_verify)", "enum": ["design", "verify"]},
                "hook_trigger": {"type": "string", "description": "Trigger for hook", "enum": ["pre_code", "pre_feature", "pre_refactor", "pre_api", "post_code", "post_feature", "pre_commit", "pre_push"]},
                "proactive": {"type": "string", "description": "Setup proactive hooks (v2.0) - auto PRD check, drift detection", "enum": ["free", "pro"]}
            },
            "required": ["path"]
        }
    ),

    # === Rules Tools (v0.5) ===
    Tool(
        name="init_rules",
        description="v0.5: Initialize rules modularization.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "template": {"type": "string", "enum": ["web", "api", "fullstack", "minimal"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="get_rule",
        description="v0.5: Load rules based on path.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "context": {"type": "string", "enum": ["coding", "review", "debug", "test"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="add_rule",
        description="v0.5: Add new rule.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "rule_type": {"type": "string", "enum": ["never", "always", "prefer"]},
                "content": {"type": "string", "description": "Rule content"},
                "category": {"type": "string", "enum": ["api", "frontend", "database", "security", "general"]}
            },
            "required": ["path", "rule_type", "content"]
        }
    ),

    # === Verify Tools (v0.5) ===
    Tool(
        name="verify",
        description="v0.5: Context Bias removal verification.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Verification target path"},
                "scope": {"type": "string", "enum": ["file", "feature", "full"]},
                "checklist": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="gate",
        description="Run lint, test, and build in sequence. Catches broken code before you commit.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "steps": {"type": "array", "items": {"type": "string"}},
                "fix": {"type": "boolean"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="handoff",
        description="v0.5: Record intent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Completed feature"},
                "decisions": {"type": "string"},
                "warnings": {"type": "string"},
                "next_steps": {"type": "string"}
            },
            "required": ["path", "feature"]
        }
    ),

    # === Planning Tools (v0.6, v1.3) ===
    Tool(
        name="init_planning",
        description="v0.6: Initialize persistent context.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "task": {"type": "string", "description": "Current task"},
                "goals": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path", "task"]
        }
    ),
    Tool(
        name="plan",
        description="Generate a detailed execution plan with action items, dependencies, and verification points.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "task": {"type": "string", "description": "Task to perform"},
                "goals": {"type": "array", "items": {"type": "string"}, "description": "Goals to achieve"},
                "meeting_file": {"type": "string", "description": "Previous meeting file name (e.g., 2026-01-24_14-00_feature.md). If provided, generates plan based on meeting results"}
            },
            "required": ["path", "task"]
        }
    ),
    Tool(
        name="save_finding",
        description="v0.6: Save research findings.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "topic": {"type": "string"},
                "question": {"type": "string"},
                "findings": {"type": "string"},
                "source": {"type": "string"},
                "conclusion": {"type": "string"}
            },
            "required": ["path", "topic", "findings"]
        }
    ),
    Tool(
        name="refresh_goals",
        description="v0.6: Goals reminder.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Project root path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="update_progress",
        description="v0.6: Update progress status.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "completed": {"type": "array", "items": {"type": "string"}},
                "in_progress": {"type": "string"},
                "blockers": {"type": "array", "items": {"type": "string"}},
                "next": {"type": "string"}
            },
            "required": ["path"]
        }
    ),

    # === Context Checkpoint (Free) ===
    Tool(
        name="context_save",
        description="Save your working state before context runs out. One call captures everything needed for recovery.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "reason": {"type": "string", "description": "Why saving (e.g., 'before refactor')"},
                "notes": {"type": "string", "description": "Important context to preserve"},
                "active_files": {"type": "array", "items": {"type": "string"}, "description": "Files currently being worked on"},
                "decisions_this_session": {"type": "array", "items": {"type": "string"}, "description": "Decisions made this session"},
                "depth": {"type": "string", "enum": ["quick", "full"], "description": "quick: current.md + git only, full: everything (default)"},
                "task": {"type": "string", "description": "Current task description (initializes planning context)"},
                "goals": {"type": "array", "items": {"type": "string"}, "description": "Session goals to track"},
                "findings": {"type": "string", "description": "Research findings to preserve"},
                "handoff": {"type": "string", "description": "Handoff notes for next session (what was done, what's next)"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="context_load",
        description="Restore your working state after context compression or a new session.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "checkpoint": {"type": "string", "description": "\"latest\" (default) or specific filename"},
                "show_goals": {"type": "boolean", "description": "Include saved goals in the loaded context (default: true)"},
            },
            "required": ["path"],
        },
    ),

    # === Agent Tools (v0.7) ===
    Tool(
        name="spawn_explore",
        description="v0.7: Exploration specialist agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Exploration question"},
                "scope": {"type": "string", "enum": ["file", "folder", "project", "deep"]},
                "save_findings": {"type": "boolean"}
            },
            "required": ["path", "query"]
        }
    ),
    Tool(
        name="spawn_librarian",
        description="v0.7: Librarian agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "topic": {"type": "string", "description": "Research topic"},
                "type": {"type": "string", "enum": ["library", "api", "migration", "best_practice"]},
                "depth": {"type": "string", "enum": ["quick", "standard", "thorough"]}
            },
            "required": ["path", "topic"]
        }
    ),

    # === Hook Tools (v0.8) ===
    Tool(
        name="hook_design",
        description="v0.8: Create design hook.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "trigger": {"type": "string", "enum": ["pre_code", "pre_feature", "pre_refactor", "pre_api"]},
                "checks": {"type": "array", "items": {"type": "string"}},
                "block_on_fail": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),
    Tool(
        name="hook_verify",
        description="v0.8: Create verification hook.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "trigger": {"type": "string", "enum": ["post_code", "post_feature", "pre_commit", "pre_push"]},
                "steps": {"type": "array", "items": {"type": "string"}},
                "parallel": {"type": "boolean"},
                "continue_on_error": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),

    # === Start Tool (Free, v1.2 → v1.9 extended) ===
    Tool(
        name="start",
        description="Set up a new project. Auto-detects project type, checks for PRD, and guides you through onboarding.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_type": {"type": "string", "description": "Force project type (optional)", "enum": ["web-app", "api", "cli", "chrome-ext", "discord-bot", "landing-page", "generic"]},
                "template": {"type": "string", "description": "Get PRD template (replaces get_prd_template)", "enum": ["web-app", "api", "cli", "chrome-ext", "discord-bot", "landing-page", "saas", "generic"]},
                "layout": {"type": "string", "description": "Template layout", "enum": ["lite", "standard", "detailed"], "default": "standard"},
                "guide": {"type": "boolean", "description": "Show PRD writing guide (replaces get_prd_guide)", "default": False},
                "init": {"type": "boolean", "description": "Initialize docs folder with templates", "default": False},
                "rules": {"type": "string", "description": "Initialize coding rules template (web, api, fullstack, minimal)", "enum": ["web", "api", "fullstack", "minimal"]},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="save_prd",
        description="Save your PRD to the project docs folder. Write requirements through conversation, then persist them.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "content": {"type": "string", "description": "PRD content (markdown)"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_type": {"type": "string", "description": "Project type (optional)"}
            },
            "required": ["path", "content"]
        }
    ),

    # === Project Management Tools (Free, v3.3) ===
    Tool(
        name="archive_project",
        description="Archive a project to free up the active slot. Free tier allows 1 active project. (Free)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project path to archive"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="list_projects",
        description="List all registered projects with their status (active/archived). (Free)",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),

    # === Knowledge Base Tools (Pro, v1.4) ===
    Tool(
        name="record_decision",
        description="Save an architectural or design decision. Persists across sessions so context is never lost.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Decision category (architecture, pricing, security, feature, etc.)"},
                "decision": {"type": "string", "description": "The actual decision made"},
                "reasoning": {"type": "string", "description": "Why this decision was made"},
                "alternatives": {"type": "array", "items": {"type": "string"}, "description": "Other options that were considered"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_path": {"type": "string", "description": "Project path (optional)"},
                "locked": {"type": "boolean", "description": "If true, decision is LOCKED and should not be changed without explicit unlock"}
            },
            "required": ["category", "decision"]
        }
    ),
    Tool(
        name="record_location",
        description="Record a code location to the knowledge base. Track where important code lives. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Descriptive name (e.g., 'License validation endpoint')"},
                "repo": {"type": "string", "description": "Repository name (e.g., 'clouvel-workers')"},
                "path": {"type": "string", "description": "File path within repo (e.g., 'src/index.js:42')"},
                "description": {"type": "string", "description": "What this code does"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_path": {"type": "string", "description": "Project path (optional)"}
            },
            "required": ["name", "repo", "path"]
        }
    ),
    Tool(
        name="search_knowledge",
        description="Search past decisions, code locations, and context from your knowledge base.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (FTS5 syntax supported)"},
                "project_name": {"type": "string", "description": "Filter by project (optional)"},
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_context",
        description="Get recent context for a project. Returns recent decisions and code locations. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name"},
                "project_path": {"type": "string", "description": "Project path"},
                "include_decisions": {"type": "boolean", "description": "Include recent decisions (default true)"},
                "include_locations": {"type": "boolean", "description": "Include code locations (default true)"},
                "limit": {"type": "integer", "description": "Max items per category (default 10)"}
            }
        }
    ),
    Tool(
        name="init_knowledge",
        description="Initialize the knowledge base. Creates SQLite database at ~/.clouvel/knowledge.db. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            }
        }
    ),
    Tool(
        name="rebuild_index",
        description="Rebuild the knowledge base search index. Use if search results seem incomplete. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            }
        }
    ),
    Tool(
        name="unlock_decision",
        description="Unlock a locked decision. Requires explicit reason. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "decision_id": {"type": "integer", "description": "The ID of the decision to unlock"},
                "reason": {"type": "string", "description": "Why this decision is being unlocked (required for audit)"},
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            },
            "required": ["decision_id", "reason"]
        }
    ),
    Tool(
        name="list_locked_decisions",
        description="List all locked decisions. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Filter by project name (optional)"},
                "project_path": {"type": "string", "description": "Filter by project path (optional)"}
            }
        }
    ),

    # === Tracking Tools (v1.5) ===
    Tool(
        name="record_file",
        description="Record a file creation to .claude/files/created.md. Use this when creating important files that should not be deleted.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "file_path": {"type": "string", "description": "Relative path of the created file"},
                "purpose": {"type": "string", "description": "What this file does"},
                "deletable": {"type": "boolean", "description": "Whether this file can be deleted (default: false)"},
                "session": {"type": "string", "description": "Session name for grouping (optional)"}
            },
            "required": ["path", "file_path", "purpose"]
        }
    ),
    Tool(
        name="list_files",
        description="List all recorded files from .claude/files/created.md.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"}
            },
            "required": ["path"]
        }
    ),

    # === Manager Tool (Pro, v1.2) ===
    Tool(
        name="manager",
        description="Context-based collaborative feedback from 8 C-Level managers. PM/CTO/QA/CDO/CMO/CFO/CSO/Error. Set use_dynamic=true for natural meeting transcript generation. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Content to review (plan, code, questions, etc.)"},
                "mode": {"type": "string", "enum": ["auto", "all", "specific"], "description": "Manager selection mode"},
                "managers": {"type": "array", "items": {"type": "string"}, "description": "Manager list when mode=specific"},
                "include_checklist": {"type": "boolean", "description": "Include checklist"},
                "use_dynamic": {"type": "boolean", "description": "If true, generate natural meeting transcript via Claude API (ANTHROPIC_API_KEY required)"},
                "topic": {"type": "string", "enum": ["auth", "api", "payment", "ui", "feature", "launch", "error", "security", "performance", "maintenance", "design"], "description": "Meeting topic hint (when use_dynamic=true)"}
            },
            "required": ["context"]
        }
    ),
    Tool(
        name="list_managers",
        description="List available managers. (Pro)",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="quick_perspectives",
        description="Get 3-4 critical questions before coding. Surfaces blind spots you might miss.",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "What you're about to build/do"},
                "max_managers": {"type": "integer", "description": "Max managers to include (default 4)"},
                "questions_per_manager": {"type": "integer", "description": "Questions per manager (default 2)"}
            },
            "required": ["context"]
        }
    ),

    # === Ship Tool (Pro, v1.2) ===
    Tool(
        name="ship",
        description="One-click ship: lint, typecheck, test, build in sequence. Generates verification evidence.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"},
                "steps": {"type": "array", "items": {"type": "string"}, "description": "Steps to execute ['lint', 'typecheck', 'test', 'build']"},
                "generate_evidence": {"type": "boolean", "description": "Generate evidence file"},
                "auto_fix": {"type": "boolean", "description": "Attempt auto-fix for lint errors"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="quick_ship",
        description="Quick ship - run lint and test only. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="full_ship",
        description="Full ship - all verification steps + auto fix. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"}
            },
            "required": ["path"]
        }
    ),

    # === Error Learning Tools (Pro, v1.4) ===
    Tool(
        name="error_record",
        description="Record an error with 5 Whys root cause analysis. Builds your project's error memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "error_text": {"type": "string", "description": "Error message"},
                "context": {"type": "string", "description": "Error context description"},
                "five_whys": {"type": "array", "items": {"type": "string"}, "description": "5 Whys analysis results"},
                "root_cause": {"type": "string", "description": "Root cause"},
                "solution": {"type": "string", "description": "Solution"},
                "prevention": {"type": "string", "description": "Prevention measures"}
            },
            "required": ["path", "error_text"]
        }
    ),
    Tool(
        name="error_check",
        description="Check for known error patterns before modifying code. Warns you before repeating past mistakes.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "context": {"type": "string", "description": "Current work context"},
                "file_path": {"type": "string", "description": "File path to modify"},
                "operation": {"type": "string", "description": "Operation to perform"}
            },
            "required": ["path", "context"]
        }
    ),
    Tool(
        name="error_learn",
        description="Analyze error patterns and auto-generate NEVER/ALWAYS rules for CLAUDE.md.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "auto_update_claude_md": {"type": "boolean", "description": "Auto update CLAUDE.md"},
                "min_count": {"type": "integer", "description": "Minimum error count for NEVER rule generation"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_status",
        description="See your error memory dashboard: active patterns, hit counts, and time saved.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_list",
        description="List regression memories. Filter by category, show archived. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "category": {"type": "string", "description": "Filter by error category (optional)"},
                "include_archived": {"type": "boolean", "description": "Include archived memories (default false)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_search",
        description="Search your error memories by keyword. Find past root causes and prevention rules.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Search keyword"},
                "category": {"type": "string", "description": "Filter by category (optional)"},
            },
            "required": ["path", "query"]
        }
    ),
    Tool(
        name="memory_archive",
        description="Archive or unarchive a regression memory. Archived memories are excluded from matching. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "memory_id": {"type": "integer", "description": "Memory ID to archive/unarchive"},
                "action": {"type": "string", "enum": ["archive", "unarchive"], "description": "Action (default: archive)"},
            },
            "required": ["path", "memory_id"]
        }
    ),
    Tool(
        name="memory_report",
        description="Monthly regression memory report. Shows savings, prevention count, top patterns, and time saved estimate. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "days": {"type": "integer", "description": "Report period in days (default 30)"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_promote",
        description="Promote a local regression memory to global. Shared across all projects. Only root_cause and prevention_rule are promoted (no raw error text). Requires hit_count >= 1. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "memory_id": {"type": "integer", "description": "Local memory ID to promote"},
            },
            "required": ["path", "memory_id"]
        }
    ),
    Tool(
        name="memory_global_search",
        description="Search error patterns across all your projects. Reuse lessons learned everywhere.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Search keyword"},
                "category": {"type": "string", "description": "Filter by error category (optional)"},
                "domain": {"type": "string", "description": "Filter by domain (personal/work/client). Auto-detected if not specified.", "enum": ["personal", "work", "client"]},
            },
            "required": ["path", "query"]
        }
    ),

    Tool(
        name="set_project_domain",
        description="Set the domain for the current project. Domains isolate memories: personal/work/client. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "domain": {"type": "string", "description": "Domain scope", "enum": ["personal", "work", "client"]},
            },
            "required": ["path", "domain"]
        }
    ),

    # === License Tools ===
    Tool(
        name="activate_license",
        description="Activate license. Supports Polar.sh or test license.",
        inputSchema={
            "type": "object",
            "properties": {
                "license_key": {"type": "string", "description": "License key"}
            },
            "required": ["license_key"]
        }
    ),
    Tool(
        name="license_status",
        description="Check your Clouvel license, trial status, and available features.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "activate", "trial", "upgrade"],
                    "description": "Action: status (default), activate (with license_key), trial (start 7-day), upgrade (show Pro guide)",
                },
                "license_key": {
                    "type": "string",
                    "description": "License key (required when action=activate)",
                },
            },
        },
    ),
    Tool(
        name="start_trial",
        description="Start 7-day Full Pro trial. No credit card required. All Pro features unlocked for 7 days.",
        inputSchema={"type": "object", "properties": {}}
    ),

    # === Pro Guide ===
    Tool(
        name="upgrade_pro",
        description="Clouvel Pro guide. Shovel auto-install, Error Learning, etc.",
        inputSchema={"type": "object", "properties": {}}
    ),

    # === Architecture Guard (v1.8) ===
    Tool(
        name="arch_check",
        description="Check existing code before adding new function/module. Prevents duplicate definitions.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"description": "Function/class name to add", "type": "string"},
                "purpose": {"description": "Purpose description", "type": "string"},
                "path": {"description": "Project root path", "type": "string"},
            },
            "required": ["name", "purpose"]
        }
    ),
    Tool(
        name="check_imports",
        description="Validate server.py import patterns. Detects architecture rule violations.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    Tool(
        name="check_duplicates",
        description="Detect duplicate function definitions across __init__.py files.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    # v3.1: Sideeffect sync checker
    Tool(
        name="check_sync",
        description="v3.1: Verify sync between file pairs (license.py ↔ license_free.py, messages/en.py ↔ ko.py). Detects missing functions and signature mismatches.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    # v3.2: Debug runtime environment (MCP debugging)
    Tool(
        name="debug_runtime",
        description="Debug MCP runtime environment. Shows Python executable, clouvel path, and entitlement status. Use to diagnose MCP/interpreter issues.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path for is_developer check", "type": "string"},
            },
        }
    ),
    # v2.0: Proactive MCP tools
    Tool(
        name="drift_check",
        description="Detect when your work drifts from original goals. Catches scope creep early.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "silent": {"description": "If True, return minimal output (for hooks)", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    Tool(
        name="pattern_watch",
        description="v2.0: Watch for repeated error patterns. Detects when same error occurs multiple times. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "threshold": {"description": "Number of occurrences to trigger alert (default: 3)", "type": "integer"},
                "check_only": {"description": "If True, only check without recording", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    Tool(
        name="auto_remind",
        description="v2.0: Configure automatic progress reminders. Reminds to update current.md periodically. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "interval": {"description": "Reminder interval in minutes (default: 30)", "type": "integer"},
                "enabled": {"description": "Enable or disable reminders", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    # Meeting (Free, v2.1)
    Tool(
        name="meeting",
        description="Simulate a C-Level review with 8 virtual managers (PM, CTO, QA, CSO, CDO, CMO, CFO, Error). Get multi-perspective feedback on your plan or code.",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"description": "Meeting topic or situation to review", "type": "string"},
                "topic": {
                    "description": "Topic hint for auto-selecting relevant managers",
                    "type": "string",
                    "enum": ["auth", "api", "payment", "ui", "feature", "launch", "error", "security", "performance", "design", "cost", "maintenance"],
                },
                "managers": {
                    "description": "Specific managers to include (auto-selected if omitted): PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR",
                    "type": "array",
                    "items": {"type": "string"},
                },
                "project_path": {"description": "Project path (for Knowledge Base integration)", "type": "string"},
                "include_example": {"description": "Include few-shot examples (default: true)", "type": "boolean"},
            },
            "required": ["context"],
        }
    ),
    Tool(
        name="meeting_topics",
        description="List available meeting topics.",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
    # Meeting Feedback & Tuning (Free, v2.2)
    Tool(
        name="rate_meeting",
        description="Rate meeting quality (1-5) with optional feedback.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "meeting_id": {"description": "Meeting ID (shown after running meeting tool)", "type": "string"},
                "rating": {"description": "Quality rating (1-5). 1: not helpful, 3: average, 5: very useful", "type": "integer", "minimum": 1, "maximum": 5},
                "feedback": {"description": "Text feedback (optional)", "type": "string"},
                "tags": {"description": "Tags (e.g., natural, actionable, specific)", "type": "array", "items": {"type": "string"}},
            },
            "required": ["project_path", "meeting_id", "rating"],
        }
    ),
    Tool(
        name="get_meeting_stats",
        description="Meeting quality statistics by topic and version.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "days": {"description": "Analysis period in days", "type": "integer"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="export_training_data",
        description="Export high-quality meeting transcripts (rating >= 4).",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "min_rating": {"description": "Minimum rating (default: 4)", "type": "integer"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="enable_ab_testing",
        description="Enable A/B testing for prompt variants.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "variants": {"description": "Variants to test (default: all)", "type": "array", "items": {"type": "string"}},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="disable_ab_testing",
        description="Disable A/B testing. Optionally set a winner.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "set_winner": {"description": "Variant to set as active", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="get_variant_performance",
        description="Compare prompt variant performance.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="list_variants",
        description="List available prompt variants.",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
    # Meeting Personalization (Free, v2.3)
    Tool(
        name="configure_meeting",
        description="Configure meeting settings per project: manager weights, default managers by topic, language/format.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "manager_weights": {
                    "description": "Weight per manager (0.0-2.0). Example: {\"CSO\": 1.5, \"CDO\": 0.5}",
                    "type": "object",
                },
                "default_managers": {
                    "description": "Default managers per topic. Example: {\"auth\": [\"PM\", \"CTO\", \"CSO\"]}",
                    "type": "object",
                },
                "preferences": {
                    "description": "Language (ko/en), format (formal/casual), detail (full/summary/minimal)",
                    "type": "object",
                },
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="add_persona_override",
        description="Customize a manager persona with project-specific phrases and focus areas.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "manager": {"description": "Manager key (PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR)", "type": "string"},
                "overrides": {
                    "description": "Override settings. Example: {\"pet_phrases\": [\"watch tech debt\"], \"focus_areas\": [\"security\"]}",
                    "type": "object",
                },
            },
            "required": ["project_path", "manager", "overrides"],
        }
    ),
    Tool(
        name="get_meeting_config",
        description="View current meeting configuration.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="reset_meeting_config",
        description="Reset meeting configuration to defaults.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
]


def _get_list_tools_tier() -> str:
    """Determine license tier for list_tools() filtering.

    Only developer/license/trial → "pro".
    Everyone else (including "first" project) → "free".
    Free users see 10 Core tools only.
    """
    try:
        from .license_common import (
            is_developer, load_license_cache,
            is_full_trial_active,
        )

        if is_developer():
            return "pro"

        cached = load_license_cache()
        if cached and cached.get("tier"):
            return "pro"

        if is_full_trial_active():
            return "pro"

        return "free"
    except ImportError:
        return "free"


def _get_call_tool_tier(project_path: str) -> str:
    """Determine tier for call_tool() defense-in-depth.

    Only developer/license/trial → "pro". Everything else → "free".
    Consistent with _get_list_tools_tier() and _is_pro().
    """
    if _is_pro(project_path):
        return "pro"
    return "free"


def _is_pro(project_path: str) -> bool:
    """Check if user has actual Pro access (license or trial).

    Returns True ONLY for paid Pro users.
    "first" project without license = False (Free limitations apply).
    """
    try:
        from .license_common import is_developer, load_license_cache, is_full_trial_active
        if is_developer():
            return True
        cached = load_license_cache()
        if cached and cached.get("tier"):
            return True
        if is_full_trial_active():
            return True
        return False
    except ImportError:
        return False


@server.list_tools()
async def list_tools() -> list[Tool]:
    # Debug override: show all tools (for development/testing)
    if os.getenv("CLOUVEL_SHOW_ALL_TOOLS"):
        return TOOL_DEFINITIONS

    tier = _get_list_tools_tier()
    return filter_tools_by_tier(TOOL_DEFINITIONS, tier)


# ============================================================
# Tool Handlers
# ============================================================

# v1.0: Wrapper to prepend migration notices (v3.0 + v1.0 pivot)
async def _with_notices(coro):
    """Wrapper that prepends migration notices to tool output."""
    result = await coro
    # Collect notices (newer first)
    notices = []
    pivot = get_v1_pivot_notice()
    if pivot:
        notices.append(pivot)
    v3 = get_v3_migration_notice()
    if v3:
        notices.append(v3)
    if notices and result:
        if isinstance(result, list) and len(result) > 0:
            original_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result[0] = TextContent(type="text", text="\n".join(notices) + "\n" + original_text)
    return result


async def _can_code_with_notice(path: str, mode: str = "pre"):
    """can_code with migration notices."""
    return await _with_notices(can_code(path, mode))


TOOL_HANDLERS = {
    # Core (v3.0: with migration notice)
    "can_code": lambda args: _can_code_with_notice(args.get("path", ""), args.get("mode", "pre")),
    "scan_docs": lambda args: scan_docs(args.get("path", "")),
    "analyze_docs": lambda args: analyze_docs(args.get("path", "")),
    "init_docs": lambda args: init_docs(args.get("path", ""), args.get("project_name", "")),

    # Docs
    "get_prd_template": lambda args: get_prd_template(args.get("project_name", ""), args.get("output_path", ""), args.get("template", "generic"), args.get("layout", "standard")),
    "list_templates": lambda args: list_templates(),
    "write_prd_section": lambda args: write_prd_section(args.get("section", ""), args.get("content", "")),
    "get_prd_guide": lambda args: get_prd_guide(),
    "get_verify_checklist": lambda args: get_verify_checklist(),
    "get_setup_guide": lambda args: get_setup_guide(args.get("platform", "all")),

    # Setup
    "init_clouvel": lambda args: init_clouvel(args.get("platform", "ask")),
    "setup_cli": lambda args: setup_cli(args.get("path", ""), args.get("level", "strict"), args.get("rules", ""), args.get("hook", ""), args.get("hook_trigger", ""), args.get("proactive", "")),

    # Rules (v0.5)
    "init_rules": lambda args: init_rules(args.get("path", ""), args.get("template", "minimal")),
    "get_rule": lambda args: get_rule(args.get("path", ""), args.get("context", "coding")),
    "add_rule": lambda args: add_rule(args.get("path", ""), args.get("rule_type", "always"), args.get("content", ""), args.get("category", "general")),

    # Verify (v0.5)
    "verify": lambda args: verify(args.get("path", ""), args.get("scope", "file"), args.get("checklist", [])),
    "gate": lambda args: gate(args.get("path", ""), args.get("steps", ["lint", "test", "build"]), args.get("fix", False)),
    "handoff": lambda args: handoff(args.get("path", ""), args.get("feature", ""), args.get("decisions", ""), args.get("warnings", ""), args.get("next_steps", "")),

    # Planning (v0.6, v1.3)
    "init_planning": lambda args: init_planning(args.get("path", ""), args.get("task", ""), args.get("goals", [])),
    "plan": lambda args: create_detailed_plan(args.get("path", ""), args.get("task", ""), args.get("goals", []), meeting_file=args.get("meeting_file")),
    "save_finding": lambda args: save_finding(args.get("path", ""), args.get("topic", ""), args.get("question", ""), args.get("findings", ""), args.get("source", ""), args.get("conclusion", "")),
    "refresh_goals": lambda args: refresh_goals(args.get("path", "")),
    "update_progress": lambda args: update_progress(args.get("path", ""), args.get("completed", []), args.get("in_progress", ""), args.get("blockers", []), args.get("next", "")),

    # Context Checkpoint (Free)
    "context_save": lambda args: _wrap_context_save(args),
    "context_load": lambda args: _wrap_context_load(args),

    # Agents (v0.7)
    "spawn_explore": lambda args: spawn_explore(args.get("path", ""), args.get("query", ""), args.get("scope", "project"), args.get("save_findings", True)),
    "spawn_librarian": lambda args: spawn_librarian(args.get("path", ""), args.get("topic", ""), args.get("type", "library"), args.get("depth", "standard")),

    # Hooks (v0.8)
    "hook_design": lambda args: hook_design(args.get("path", ""), args.get("trigger", "pre_code"), args.get("checks", []), args.get("block_on_fail", True)),
    "hook_verify": lambda args: hook_verify(args.get("path", ""), args.get("trigger", "post_code"), args.get("steps", ["lint", "test", "build"]), args.get("parallel", False), args.get("continue_on_error", False)),

    # Start (Free, v1.2)
    "start": lambda args: _wrap_start(args),
    "save_prd": lambda args: _wrap_save_prd(args),

    # Project Management (Free, v3.3)
    "archive_project": lambda args: _wrap_archive_project(args),
    "list_projects": lambda args: _wrap_list_projects(args),

    # Knowledge (Free, v1.4)
    "record_decision": lambda args: _wrap_record_decision(args),
    "record_location": lambda args: _wrap_record_location(args),
    "search_knowledge": lambda args: _wrap_search_knowledge(args),
    "get_context": lambda args: _wrap_get_context(args),
    "init_knowledge": lambda args: _wrap_init_knowledge(args),
    "rebuild_index": lambda args: _wrap_rebuild_index(args),
    "unlock_decision": lambda args: _wrap_unlock_decision(args),
    "list_locked_decisions": lambda args: _wrap_list_locked_decisions(args),

    # Tracking (v1.5)
    "record_file": lambda args: _wrap_record_file(args),
    "list_files": lambda args: _wrap_list_files(args),

    # Manager (Pro, v1.2)
    "manager": lambda args: _wrap_manager(args),
    "list_managers": lambda args: _wrap_list_managers(),
    "quick_perspectives": lambda args: _wrap_quick_perspectives(args),

    # Ship (Pro, v1.2)
    "ship": lambda args: _wrap_ship(args),
    "quick_ship": lambda args: _wrap_quick_ship(args),
    "full_ship": lambda args: _wrap_full_ship(args),

    # Error Learning (Pro, v1.4) + Regression Memory (v4.0)
    "error_record": lambda args: _wrap_error_record(args),
    "error_check": lambda args: _wrap_error_check(args),
    "error_learn": lambda args: _wrap_error_learn(args),
    "memory_status": lambda args: _wrap_memory_status(args),
    "memory_list": lambda args: _wrap_memory_list(args),
    "memory_search": lambda args: _wrap_memory_search(args),
    "memory_archive": lambda args: _wrap_memory_archive(args),
    "memory_report": lambda args: _wrap_memory_report(args),
    "memory_promote": lambda args: _wrap_memory_promote(args),
    "memory_global_search": lambda args: _wrap_memory_global_search(args),
    "set_project_domain": lambda args: _wrap_set_project_domain(args),

    # License
    "activate_license": lambda args: _wrap_activate_license(args),
    "license_status": lambda args: _wrap_license_status(args),
    "start_trial": lambda args: _wrap_start_trial(),

    # Pro 안내
    "upgrade_pro": lambda args: _upgrade_pro(),

    # Architecture Guard (v1.8 + v3.1)
    "arch_check": lambda args: arch_check(args.get("name", ""), args.get("purpose", ""), args.get("path", ".")),
    "check_imports": lambda args: check_imports(args.get("path", ".")),
    "check_duplicates": lambda args: check_duplicates(args.get("path", ".")),
    "check_sync": lambda args: check_sync(args.get("path", ".")),  # v3.1

    # Debug (v3.2)
    "debug_runtime": lambda args: _wrap_debug_runtime(args),

    # Proactive (v2.0)
    "drift_check": lambda args: _wrap_drift_check(args),
    "pattern_watch": lambda args: _wrap_pattern_watch(args),
    "auto_remind": lambda args: _wrap_auto_remind(args),
    # Meeting (Free, v2.1)
    "meeting": lambda args: meeting(
        context=args.get("context", ""),
        topic=args.get("topic"),
        managers=args.get("managers"),
        project_path=args.get("project_path"),
        include_example=args.get("include_example", True),
    ),
    "meeting_topics": lambda args: meeting_topics(),
    # Meeting Feedback & Tuning (Free, v2.2)
    "rate_meeting": lambda args: rate_meeting(
        project_path=args.get("project_path", ""),
        meeting_id=args.get("meeting_id", ""),
        rating=args.get("rating", 3),
        feedback=args.get("feedback"),
        tags=args.get("tags"),
    ),
    "get_meeting_stats": lambda args: get_meeting_stats(
        project_path=args.get("project_path", ""),
        days=args.get("days", 30),
    ),
    "export_training_data": lambda args: export_training_data(
        project_path=args.get("project_path", ""),
        min_rating=args.get("min_rating", 4),
    ),
    "enable_ab_testing": lambda args: enable_ab_testing(
        project_path=args.get("project_path", ""),
        variants=args.get("variants"),
    ),
    "disable_ab_testing": lambda args: disable_ab_testing(
        project_path=args.get("project_path", ""),
        set_winner=args.get("set_winner"),
    ),
    "get_variant_performance": lambda args: get_variant_performance(
        project_path=args.get("project_path", ""),
    ),
    "list_variants": lambda args: list_variants(),
    # Meeting Personalization (Free, v2.3)
    "configure_meeting": lambda args: configure_meeting(
        project_path=args.get("project_path", ""),
        manager_weights=args.get("manager_weights"),
        default_managers=args.get("default_managers"),
        preferences=args.get("preferences"),
    ),
    "add_persona_override": lambda args: add_persona_override(
        project_path=args.get("project_path", ""),
        manager=args.get("manager", ""),
        overrides=args.get("overrides", {}),
    ),
    "get_meeting_config": lambda args: get_meeting_config(
        project_path=args.get("project_path", ""),
    ),
    "reset_meeting_config": lambda args: reset_meeting_config(
        project_path=args.get("project_path", ""),
    ),
}


def _check_version_once():
    """Check version on first call (lazy initialization)"""
    global _version_check_done
    if not _version_check_done:
        try:
            init_version_check()
        except Exception:
            pass
        _version_check_done = True


async def _wrap_context_save(args: dict) -> list[TextContent]:
    """context_save wrapper — absorbs init_planning, save_finding, handoff."""
    # Build enriched notes from absorbed parameters
    extra_notes = []
    if args.get("task"):
        extra_notes.append(f"## Current Task\n{args['task']}")
    if args.get("goals"):
        goals_str = "\n".join(f"- {g}" for g in args["goals"])
        extra_notes.append(f"## Goals\n{goals_str}")
    if args.get("findings"):
        extra_notes.append(f"## Research Findings\n{args['findings']}")
    if args.get("handoff"):
        extra_notes.append(f"## Handoff Notes\n{args['handoff']}")

    # Merge extra notes into the notes parameter
    notes = args.get("notes", "") or ""
    if extra_notes:
        notes = notes + "\n\n" + "\n\n".join(extra_notes) if notes else "\n\n".join(extra_notes)

    project_path = args.get("path", "")
    return await context_save(
        path=project_path,
        reason=args.get("reason", ""),
        notes=notes,
        active_files=args.get("active_files"),
        decisions_this_session=args.get("decisions_this_session"),
        depth=args.get("depth", "full"),
        is_pro=_is_pro(project_path),
    )


async def _wrap_context_load(args: dict) -> list[TextContent]:
    """context_load wrapper — absorbs refresh_goals."""
    result = await context_load(
        path=args.get("path", ""),
        checkpoint=args.get("checkpoint", "latest"),
    )

    # Append goals reminder if requested (default: true)
    if args.get("show_goals", True):
        try:
            goals_result = await refresh_goals(args.get("path", ""))
            if goals_result and len(goals_result) > 0:
                goals_text = goals_result[0].text if hasattr(goals_result[0], 'text') else str(goals_result[0])
                if result and len(result) > 0:
                    original = result[0].text if hasattr(result[0], 'text') else str(result[0])
                    result[0] = TextContent(type="text", text=original + "\n\n---\n" + goals_text)
        except Exception:
            pass  # Goals not available — that's fine

    return result


async def _wrap_start(args: dict) -> list[TextContent]:
    """start tool wrapper — absorbs init_docs, get_prd_template, init_rules, setup_cli."""
    # Handle rules initialization if requested
    rules_template = args.get("rules")
    rules_msg = None
    if rules_template:
        try:
            rules_result = init_rules(args.get("path", ""), rules_template)
            rules_msg = rules_result.get("message", "Rules initialized.") if isinstance(rules_result, dict) else str(rules_result)
        except Exception as e:
            rules_msg = f"Rules init failed: {e}"

    result = start(
        args.get("path", ""),
        args.get("project_name", ""),
        args.get("project_type", ""),
        args.get("template", ""),
        args.get("layout", "standard"),
        args.get("guide", False),
        args.get("init", False)
    )

    if isinstance(result, dict):
        # Handle special modes (guide, init, template)
        status = result.get("status", "UNKNOWN")

        if status == "GUIDE":
            return [TextContent(type="text", text=result.get("message", ""))]

        if status == "INITIALIZED":
            return [TextContent(type="text", text=result.get("message", ""))]

        if status == "TEMPLATE":
            return [TextContent(type="text", text=result.get("message", ""))]

        # Project type info
        ptype = result.get("project_type", {})
        type_info = f"**Type**: {ptype.get('description', 'N/A')} ({ptype.get('type', 'generic')}) - Confidence {ptype.get('confidence', 0)}%"

        output = f"""# 🚀 Start

**Status**: {status}
**Project**: {result.get('project_name', 'N/A')}
{type_info}

{result.get('message', '')}
"""

        # PRD writing guide (when status is NEED_PRD)
        if result.get("status") == "NEED_PRD" and result.get("prd_guide"):
            guide = result["prd_guide"]
            output += guide.get("instruction", "")

        # Next steps
        output += "\n## Next Steps\n"
        for step in result.get('next_steps', []):
            output += f"- {step}\n"

        # Created files
        if result.get('created_files'):
            output += "\n## Created Files\n"
            for f in result['created_files']:
                output += f"- {f}\n"

        # Append rules result if requested
        if rules_msg:
            output += f"\n## Rules\n{rules_msg}\n"

        return [TextContent(type="text", text=output)]
    return [TextContent(type="text", text=str(result))]


async def _wrap_save_prd(args: dict) -> list[TextContent]:
    """save_prd tool wrapper"""
    result = save_prd(
        args.get("path", ""),
        args.get("content", ""),
        args.get("project_name", ""),
        args.get("project_type", "")
    )

    if isinstance(result, dict):
        output = f"""# 📝 Save PRD

**Status**: {result.get('status', 'UNKNOWN')}
**Path**: {result.get('prd_path', 'N/A')}

{result.get('message', '')}
"""
        if result.get('next_steps'):
            output += "\n## Next Steps\n"
            for step in result['next_steps']:
                output += f"- {step}\n"

        return [TextContent(type="text", text=output)]
    return [TextContent(type="text", text=str(result))]


# === Project Management Wrappers (Free, v3.3) ===

async def _wrap_archive_project(args: dict) -> list[TextContent]:
    """archive_project tool wrapper"""
    from .license_common import archive_project
    result = archive_project(args.get("path", ""))

    if isinstance(result, dict):
        if result.get("success"):
            output = f"""# 📦 Archive Project

{result.get('message', '')}

**Archived at**: {result.get('archived_at', 'N/A')}

Now you can start a new project with `start` tool.
"""
        else:
            output = f"""# ❌ Archive Failed

{result.get('message', '')}
"""
        return [TextContent(type="text", text=output)]
    return [TextContent(type="text", text=str(result))]


async def _wrap_list_projects(args: dict) -> list[TextContent]:
    """list_projects tool wrapper"""
    from .license_common import list_projects
    result = list_projects()

    output = f"""# 📋 Project List

**Active**: {result.get('active_count', 0)}/{result.get('limit', 1)}
**Archived**: {result.get('archived_count', 0)}
**Tier**: {'Pro' if result.get('is_pro') else 'Free'}

## Active Projects
"""
    active = result.get("active", [])
    if active:
        for p in active:
            output += f"- **{p.get('name', 'Unknown')}** ({p.get('path', 'N/A')})\n"
    else:
        output += "_No active projects_\n"

    archived = result.get("archived", [])
    if archived:
        output += "\n## Archived Projects\n"
        for p in archived:
            output += f"- {p.get('name', 'Unknown')} ({p.get('path', 'N/A')})\n"

    if not result.get('is_pro'):
        output += (
            "\n---\n\n"
            "Unlock full error history, 8 managers, and 10 more tools with Pro.\n\n"
            "→ `license_status(action=\"trial\")` (7 days free)\n"
        )

    return [TextContent(type="text", text=output)]


# === Knowledge Base Wrappers (Free, v1.4) ===

async def _wrap_record_decision(args: dict) -> list[TextContent]:
    """record_decision tool wrapper"""
    # v5.0: KB access check — first project gets unlimited KB
    try:
        from .license_common import is_developer, is_kb_trial_active, start_kb_trial, get_project_tier
        project_path = args.get("project_path", ".")
        if not is_developer():
            # v5.0: First project bypasses trial via is_kb_trial_active
            start_kb_trial(project_path)  # Start trial on first use (no-op for first project)
            if not is_kb_trial_active(project_path):
                from .messages.en import CAN_CODE_KB_TRIAL_EXPIRED
                return [TextContent(type="text", text=CAN_CODE_KB_TRIAL_EXPIRED.format(
                    decision_count="N/A"
                ))]
    except ImportError:
        pass

    result = await record_decision(
        category=args.get("category", "general"),
        decision=args.get("decision", ""),
        reasoning=args.get("reasoning"),
        alternatives=args.get("alternatives"),
        project_name=args.get("project_name"),
        project_path=args.get("project_path"),
        locked=args.get("locked", False)
    )

    if result.get("status") == "recorded":
        locked_badge = "🔒 **LOCKED**" if result.get("locked") else ""
        output = f"""# ✅ Decision Recorded {locked_badge}

**ID**: {result.get('decision_id')}
**Category**: {result.get('category')}
**Project**: {result.get('project_id', 'global')}

Decision saved to knowledge base. Use `search_knowledge` to retrieve later.
{"⚠️ This decision is LOCKED. Do not change without explicit user approval." if result.get("locked") else ""}
"""
    else:
        output = f"""# ❌ Error Recording Decision

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_record_location(args: dict) -> list[TextContent]:
    """record_location tool wrapper"""
    # v5.0: KB access check — first project gets unlimited KB
    try:
        from .license_common import is_developer, is_kb_trial_active, start_kb_trial
        project_path = args.get("project_path", ".")
        if not is_developer():
            # v5.0: First project bypasses trial via is_kb_trial_active
            start_kb_trial(project_path)
            if not is_kb_trial_active(project_path):
                from .messages.en import CAN_CODE_KB_TRIAL_EXPIRED
                return [TextContent(type="text", text=CAN_CODE_KB_TRIAL_EXPIRED.format(
                    decision_count="N/A"
                ))]
    except ImportError:
        pass

    result = await record_location(
        name=args.get("name", ""),
        repo=args.get("repo", ""),
        path=args.get("path", ""),
        description=args.get("description"),
        project_name=args.get("project_name"),
        project_path=args.get("project_path")
    )

    if result.get("status") == "recorded":
        output = f"""# ✅ Location Recorded

**ID**: {result.get('location_id')}
**Name**: {result.get('name')}
**Repo**: {result.get('repo')}
**Path**: {result.get('path')}

Location saved to knowledge base.
"""
    else:
        output = f"""# ❌ Error Recording Location

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_search_knowledge(args: dict) -> list[TextContent]:
    """search_knowledge tool wrapper"""
    result = await search_knowledge(
        query=args.get("query", ""),
        project_name=args.get("project_name"),
        project_path=args.get("project_path"),
        limit=args.get("limit", 20)
    )

    if result.get("status") == "success":
        output = f"""# 🔍 Knowledge Search Results

**Query**: {result.get('query')}
**Found**: {result.get('count')} results

"""
        for item in result.get("results", []):
            output += f"""## [{item['type'].upper()}] ID: {item['id']}
{item['content'][:200]}{'...' if len(item['content']) > 200 else ''}

---
"""
        if not result.get("results"):
            output += "_No results found._\n"
    else:
        output = f"""# ❌ Search Error

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_get_context(args: dict) -> list[TextContent]:
    """get_context tool wrapper"""
    result = await get_context(
        project_name=args.get("project_name"),
        project_path=args.get("project_path"),
        include_decisions=args.get("include_decisions", True),
        include_locations=args.get("include_locations", True),
        limit=args.get("limit", 10)
    )

    if result.get("status") == "success":
        output = f"""# 📋 Project Context

**Project ID**: {result.get('project_id', 'global')}

"""
        if result.get("decisions"):
            output += "## Recent Decisions\n\n"
            for d in result["decisions"]:
                output += f"- **[{d.get('category', 'general')}]** {d.get('decision', '')[:100]}\n"
            output += "\n"

        if result.get("locations"):
            output += "## Code Locations\n\n"
            for loc in result["locations"]:
                output += f"- **{loc.get('name', '')}**: `{loc.get('repo', '')}/{loc.get('path', '')}`\n"
            output += "\n"

        if not result.get("decisions") and not result.get("locations"):
            output += "_No context recorded yet. Use `record_decision` and `record_location` to add context._\n"
    else:
        output = f"""# ❌ Error Getting Context

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_init_knowledge(args: dict) -> list[TextContent]:
    """init_knowledge tool wrapper"""
    result = await init_knowledge(
        project_path=args.get("project_path")
    )

    if result.get("status") == "initialized":
        output = f"""# ✅ Knowledge Base Initialized

**Database**: {result.get('db_path')}

{result.get('message', '')}

## Available Commands
- `record_decision` - Record a decision
- `record_location` - Record a code location
- `search_knowledge` - Search past knowledge
- `get_context` - Get recent context
"""
    else:
        output = f"""# ❌ Initialization Error

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_rebuild_index(args: dict) -> list[TextContent]:
    """rebuild_index tool wrapper"""
    result = await rebuild_index(
        project_path=args.get("project_path")
    )

    if result.get("status") == "rebuilt":
        output = f"""# ✅ Search Index Rebuilt

**Indexed Items**: {result.get('indexed_count')}

{result.get('message', '')}
"""
    else:
        output = f"""# ❌ Rebuild Error

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_unlock_decision(args: dict) -> list[TextContent]:
    """unlock_decision tool wrapper"""
    result = await unlock_decision(
        decision_id=args.get("decision_id"),
        reason=args.get("reason"),
        project_path=args.get("project_path")
    )

    if result.get("status") == "unlocked":
        output = f"""# 🔓 Decision Unlocked

**Decision ID**: {result.get('decision_id')}
**Category**: {result.get('category')}
**Decision**: {result.get('decision')}
**Unlock Reason**: {result.get('unlock_reason', 'Not specified')}

This decision can now be modified.
"""
    elif result.get("status") == "pro_required":
        output = f"""# ⚠️ Pro Feature Required

{result.get('error')}

**Purchase**: {result.get('purchase')}
"""
    else:
        output = f"""# ❌ Unlock Error

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


async def _wrap_list_locked_decisions(args: dict) -> list[TextContent]:
    """list_locked_decisions tool wrapper"""
    result = await list_locked_decisions(
        project_name=args.get("project_name"),
        project_path=args.get("project_path")
    )

    if result.get("status") == "success":
        decisions = result.get("decisions", [])
        if not decisions:
            output = "# 🔒 Locked Decisions\n\nNo locked decisions found."
        else:
            lines = ["# 🔒 Locked Decisions\n"]
            for d in decisions:
                lines.append(f"- **[{d['id']}]** [{d['category']}] {d['decision']}")
                if d.get('reasoning'):
                    lines.append(f"  - Reason: {d['reasoning'][:100]}...")
            lines.append(f"\n**Total**: {result.get('count')} locked decisions")
            output = "\n".join(lines)
    elif result.get("status") == "pro_required":
        output = f"""# ⚠️ Pro Feature Required

{result.get('error')}

**Purchase**: {result.get('purchase')}
"""
    else:
        output = f"""# ❌ Error

{result.get('error', 'Unknown error')}
"""
    return [TextContent(type="text", text=output)]


# === Tracking Wrappers (v1.5) ===

async def _wrap_record_file(args: dict) -> list[TextContent]:
    """record_file tool wrapper"""
    return await record_file(
        path=args.get("path", "."),
        file_path=args.get("file_path", ""),
        purpose=args.get("purpose", ""),
        deletable=args.get("deletable", False),
        session=args.get("session", None)
    )


async def _wrap_list_files(args: dict) -> list[TextContent]:
    """list_files tool wrapper"""
    return await list_files(path=args.get("path", "."))


async def _wrap_manager(args: dict) -> list[TextContent]:
    """manager tool wrapper - Worker API 사용 (v1.8)

    아키텍처 결정: 로컬 tools/manager/ 대신 Worker API 호출
    개발자 모드: 로컬 manager 모듈 직접 호출 (use_dynamic 포함)
    """
    context = args.get("context", "")
    topic = args.get("topic", None)
    mode = args.get("mode", "auto")
    managers = args.get("managers", None)
    use_dynamic = args.get("use_dynamic", False)
    include_checklist = args.get("include_checklist", True)

    # Worker API 호출 (개발자 모드면 로컬 실행)
    result = call_manager_api(
        context=context,
        topic=topic,
        mode=mode,
        managers=managers,
        use_dynamic=use_dynamic,
        include_checklist=include_checklist,
    )

    # 응답 처리
    if isinstance(result, dict):
        meeting_output = result.get("formatted_output", "")
        if not meeting_output:
            # error 응답이거나 formatted_output이 없는 경우
            if result.get("error"):
                meeting_output = f"## Manager Error\n\n{result.get('error')}\n\n{result.get('message', '')}"
            else:
                meeting_output = str(result)
        participants = result.get("active_managers", ["PM", "CTO", "QA"])
    else:
        meeting_output = str(result)
        participants = ["PM", "CTO", "QA"]

    # Auto-record meeting to Knowledge Base
    _auto_record_meeting(context, topic, participants, meeting_output)

    # Prepend migration notices (v1.0 pivot + v3.0)
    notices = []
    pivot = get_v1_pivot_notice()
    if pivot:
        notices.append(pivot)
    v3 = get_v3_migration_notice()
    if v3:
        notices.append(v3)
    if notices:
        meeting_output = "\n".join(notices) + "\n" + meeting_output

    return [TextContent(type="text", text=meeting_output)]


def _auto_record_meeting(context: str, topic: str, participants: list, output: str):
    """Automatically record meeting to Knowledge Base."""
    try:
        from .db.knowledge import record_meeting, record_decision, get_or_create_project
        import os

        # Get project from current directory
        project_path = os.getcwd()
        project_name = os.path.basename(project_path)
        project_id = get_or_create_project(project_name, project_path)

        # Record meeting
        contributions = {}
        for p in participants:
            # Extract contribution from output if possible
            contributions[p] = f"Participated in {topic or 'general'} discussion"

        meeting_id = record_meeting(
            topic=topic or "manager_review",
            participants=participants,
            contributions=contributions,
            project_id=project_id
        )

        # Try to extract and record decisions from output
        _extract_and_record_decisions(output, project_id, meeting_id)

    except Exception:
        # Silently fail - don't break manager output
        pass


def _extract_and_record_decisions(output: str, project_id: str, meeting_id: str):
    """Extract decisions from meeting output and record them."""
    try:
        from .db.knowledge import record_decision
        import re

        # Look for action items or decisions in output
        # Pattern: "| # | 담당 | 작업 |" table or "- **[category]** decision" format
        lines = output.split('\n')
        for line in lines:
            # Match action item table rows: "| 1 | PM | Task description |"
            table_match = re.match(r'\|\s*\d+\s*\|\s*[^\|]+\s*\|\s*([^\|]+)\s*\|', line)
            if table_match:
                decision_text = table_match.group(1).strip()
                if decision_text and len(decision_text) > 10:
                    record_decision(
                        category="action_item",
                        decision=decision_text[:200],
                        project_id=project_id,
                        meeting_id=meeting_id
                    )

    except Exception:
        pass


async def _wrap_list_managers() -> list[TextContent]:
    """list_managers tool wrapper"""
    managers_list = list_managers()
    output = "# 👔 Available Managers (8)\n\n"
    for m in managers_list:
        output += f"- **{m['emoji']} {m['key']}** ({m['title']}): {m['focus']}\n"
    return [TextContent(type="text", text=output)]


async def _wrap_quick_perspectives(args: dict) -> list[TextContent]:
    """quick_perspectives tool wrapper — Free: 2 managers, 1 question each."""
    context = args.get("context", "")
    is_pro_user = _is_pro("")  # No project path for this tool

    # Free: 2 managers, 1 question | Pro: up to 4 managers, 2 questions
    free_max_managers = 2
    free_max_questions = 1
    pro_max_managers = args.get("max_managers", 4)
    pro_max_questions = args.get("questions_per_manager", 2)

    max_managers = pro_max_managers if is_pro_user else free_max_managers
    max_questions = pro_max_questions if is_pro_user else free_max_questions

    # Worker API 호출 (manager와 동일)
    result = call_manager_api(
        context=context,
        mode="auto",
    )

    if isinstance(result, dict):
        if result.get("error"):
            return [TextContent(type="text", text=f"## Quick Perspectives Error\n\n{result.get('message', result.get('error'))}")]

        feedback = result.get("feedback", {})
        all_active = result.get("active_managers", [])
        visible = all_active[:max_managers]
        hidden = all_active[max_managers:]

        lines = [f"## Quick Perspectives\n\n_Before: **{context[:80]}{'...' if len(context) > 80 else ''}**_\n"]
        for mgr_key in visible:
            mgr = feedback.get(mgr_key, {})
            emoji = mgr.get("emoji", "")
            title = mgr.get("title", mgr_key)
            questions = mgr.get("questions", [])[:max_questions]
            if questions:
                lines.append(f"**{emoji} {title}**:")
                for q in questions:
                    lines.append(f"  - {q}")
                lines.append("")

        # Free nudge: show hidden managers as teaser
        if not is_pro_user and hidden:
            hidden_names = []
            for mgr_key in hidden:
                mgr = feedback.get(mgr_key, {})
                hidden_names.append(mgr.get("title", mgr_key))
            lines.append("---")
            lines.append(f"**{len(hidden)} more perspectives available** ({', '.join(hidden_names)})")
            # Show first hidden manager's first question as a teaser
            first_hidden = feedback.get(hidden[0], {})
            hint_q = first_hidden.get("questions", [""])[0]
            if hint_q:
                lines.append(f"_Hint: {first_hidden.get('title', '')} asks: \"{hint_q[:60]}...\"_")
            lines.append(f"\nUnlock all managers with Pro → `license_status(action=\"trial\")`")

        return [TextContent(type="text", text="\n".join(lines))]

    return [TextContent(type="text", text=str(result))]


async def _wrap_ship(args: dict) -> list[TextContent]:
    """ship tool wrapper"""
    result = ship(
        path=args.get("path", ""),
        feature=args.get("feature", ""),
        steps=args.get("steps", None),
        generate_evidence=args.get("generate_evidence", True),
        auto_fix=args.get("auto_fix", False)
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _wrap_quick_ship(args: dict) -> list[TextContent]:
    """quick_ship tool wrapper"""
    result = quick_ship(
        path=args.get("path", ""),
        feature=args.get("feature", "")
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _wrap_full_ship(args: dict) -> list[TextContent]:
    """full_ship tool wrapper"""
    result = full_ship(
        path=args.get("path", ""),
        feature=args.get("feature", "")
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


FREE_ERROR_LIMIT = 5


def _apply_free_error_limit(result: list[TextContent], project_path: str) -> list[TextContent]:
    """Limit error_check output for Free users.

    Counts total error entries in error_log.jsonl,
    shows only the last FREE_ERROR_LIMIT entries in output,
    and appends a soft nudge with the total count.
    """
    if not result or len(result) == 0:
        return result

    # Count total errors from log
    total_errors = 0
    try:
        from pathlib import Path as _P
        log_file = _P(project_path) / ".claude" / "errors" / "error_log.jsonl"
        if log_file.exists():
            total_errors = sum(1 for _ in open(log_file, "r", encoding="utf-8"))
    except Exception:
        pass

    if total_errors > FREE_ERROR_LIMIT:
        text = result[0].text if hasattr(result[0], 'text') else str(result[0])
        nudge = (
            f"\n\n---\n"
            f"Checked **{FREE_ERROR_LIMIT} of {total_errors}** error records (Free limit).\n"
            f"Older errors may contain relevant patterns.\n\n"
            f"Unlock full error history with Pro → `license_status(action=\"trial\")`"
        )
        result[0] = TextContent(type="text", text=text + nudge)

    return result


def _append_ghost_data(
    result: list[TextContent], project_path: str, tool_name: str
) -> list[TextContent]:
    """Append ghost data teaser to Free user's error tool output.

    Shows hints about Pro features (pattern learning, memory search)
    to naturally drive conversion from error_record/error_check usage.
    """
    # Only append for non-Pro users
    try:
        if _is_pro(project_path):
            return result
    except Exception:
        return result

    teasers = {
        "error_record": (
            "\n\n---\n"
            "**Pro**: Auto-generate NEVER/ALWAYS rules from your error patterns "
            "→ `license_status(action=\"trial\")`"
        ),
        "error_check": (
            "\n\n---\n"
            "**Pro**: Search all past errors by keyword + share lessons across projects "
            "→ `license_status(action=\"trial\")`"
        ),
    }

    teaser = teasers.get(tool_name)
    if teaser and result and len(result) > 0:
        original = result[0].text if hasattr(result[0], 'text') else str(result[0])
        result[0] = TextContent(type="text", text=original + teaser)

    return result


async def _wrap_error_record(args: dict) -> list[TextContent]:
    """error_record tool wrapper"""
    if not _HAS_ERROR_TOOLS or error_record is None:
        return [TextContent(type="text", text="""
# Clouvel Pro Feature

Error Learning requires **Clouvel Pro**.

Start a free 7-day trial: `license_status(action="trial")`
""")]
    result = await error_record(
        path=args.get("path", ""),
        error_text=args.get("error_text", ""),
        context=args.get("context", ""),
        five_whys=args.get("five_whys", None),
        root_cause=args.get("root_cause", ""),
        solution=args.get("solution", ""),
        prevention=args.get("prevention", "")
    )
    return _append_ghost_data(result, args.get("path", ""), "error_record")


async def _wrap_error_check(args: dict) -> list[TextContent]:
    """error_check tool wrapper — Free: recent 5 errors only."""
    if not _HAS_ERROR_TOOLS or error_check is None:
        return [TextContent(type="text", text="""
# Clouvel Pro Feature

Error Learning requires **Clouvel Pro**.

Start a free 7-day trial: `license_status(action="trial")`
""")]
    result = await error_check(
        path=args.get("path", ""),
        context=args.get("context", ""),
        file_path=args.get("file_path", ""),
        operation=args.get("operation", "")
    )

    # Free limit: cap visible errors and add nudge
    project_path = args.get("path", "")
    if not _is_pro(project_path):
        result = _apply_free_error_limit(result, project_path)

    return _append_ghost_data(result, project_path, "error_check")


async def _wrap_error_learn(args: dict) -> list[TextContent]:
    """error_learn tool wrapper"""
    if not _HAS_ERROR_TOOLS or error_learn is None:
        return [TextContent(type="text", text="""
# Clouvel Pro Feature

Error Learning requires **Clouvel Pro**.

Start a free 7-day trial: `license_status(action="trial")`
""")]
    return await error_learn(
        path=args.get("path", ""),
        auto_update_claude_md=args.get("auto_update_claude_md", True),
        min_count=args.get("min_count", 2)
    )


async def _wrap_memory_status(args: dict) -> list[TextContent]:
    """memory_status tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_status is None:
        return [TextContent(type="text", text="""
# Clouvel Pro Feature

Regression Memory requires **Clouvel Pro**.

Start a free 7-day trial: `license_status(action="trial")`
""")]
    return await memory_status(
        path=args.get("path", ""),
    )


async def _wrap_memory_list(args: dict) -> list[TextContent]:
    """memory_list tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_list is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nRegression Memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_list(
        path=args.get("path", ""),
        category=args.get("category", ""),
        include_archived=args.get("include_archived", False),
        limit=args.get("limit", 20),
    )


async def _wrap_memory_search(args: dict) -> list[TextContent]:
    """memory_search tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_search is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nRegression Memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_search(
        path=args.get("path", ""),
        query=args.get("query", ""),
        category=args.get("category", ""),
    )


async def _wrap_memory_archive(args: dict) -> list[TextContent]:
    """memory_archive tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_archive is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nRegression Memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_archive(
        path=args.get("path", ""),
        memory_id=args.get("memory_id", 0),
        action=args.get("action", "archive"),
    )


async def _wrap_memory_report(args: dict) -> list[TextContent]:
    """memory_report tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_report is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nRegression Memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_report(
        path=args.get("path", ""),
        days=args.get("days", 30),
    )


async def _wrap_memory_promote(args: dict) -> list[TextContent]:
    """memory_promote tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_promote is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nCross-project memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_promote(
        path=args.get("path", ""),
        memory_id=args.get("memory_id", 0),
    )


async def _wrap_memory_global_search(args: dict) -> list[TextContent]:
    """memory_global_search tool wrapper"""
    if not _HAS_ERROR_TOOLS or memory_global_search is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nCross-project memory requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await memory_global_search(
        path=args.get("path", ""),
        query=args.get("query", ""),
        category=args.get("category", ""),
        domain=args.get("domain", ""),
    )


async def _wrap_set_project_domain(args: dict) -> list[TextContent]:
    """set_project_domain tool wrapper"""
    if not _HAS_ERROR_TOOLS or set_project_domain is None:
        return [TextContent(type="text", text="# Clouvel Pro Feature\n\nDomain scoping requires **Clouvel Pro**.\n\nStart a free 7-day trial: `license_status(action=\"trial\")`\n")]
    return await set_project_domain(
        path=args.get("path", ""),
        domain=args.get("domain", ""),
    )


async def _wrap_activate_license(args: dict) -> list[TextContent]:
    """activate_license tool wrapper"""
    license_key = args.get("license_key", "")
    if not license_key:
        return [TextContent(type="text", text="""
# ❌ Please enter license key

## Usage
```
license_status(action="activate", license_key="YOUR-KEY")
```

Or start a free trial: `license_status(action="trial")`
""")]

    result = activate_license_cli(license_key)

    if result.get("success"):
        tier_info = result.get("tier_info", {})
        machine_id = result.get("machine_id", "unknown")
        product = result.get("product", "Clouvel Pro")

        # Test license extra info
        extra_info = ""
        if result.get("test_license"):
            expires_at = result.get("expires_at", "")
            expires_in_days = result.get("expires_in_days", 7)
            extra_info = f"""
## ⚠️ Test License
- **Expires**: {expires_at}
- **Days remaining**: {expires_in_days}
"""

        return [TextContent(type="text", text=f"""
# ✅ License Activated

## Info
- **Tier**: {tier_info.get('name', 'Unknown')}
- **Product**: {product}
- **Machine**: `{machine_id[:8]}...`
{extra_info}
## 🔒 Machine Binding

This license is bound to the current machine.
- Personal: Can only be used on 1 machine
- Team: Can be used on up to 10 machines
- Enterprise: Unlimited machines

To use on another machine, deactivate the existing machine or upgrade to a higher tier.
""")]
    else:
        return [TextContent(type="text", text=f"""
# ❌ License Activation Failed

{result.get('message', 'Unknown error')}

## Checklist
- Verify license key is correct
- Check network connection
- Check activation limit (Personal: 1)

Need a key? `license_status(action="upgrade")`
""")]


async def _wrap_license_status(args: dict = None) -> list[TextContent]:
    """Unified license_status tool wrapper.

    Absorbs: activate_license, start_trial, upgrade_pro.
    Dispatches based on 'action' parameter.
    """
    args = args or {}
    action = args.get("action", "status")

    if action == "activate":
        return await _wrap_activate_license(args)

    if action == "trial":
        return await _wrap_start_trial()

    if action == "upgrade":
        return await _upgrade_pro()

    # Default: status
    result = get_license_status()

    if not result.get("has_license"):
        return [TextContent(type="text", text=f"""
# License Status

**Status**: Not activated

{result.get('message', '')}

## Quick Actions
- **Free trial**: `license_status(action="trial")` — 7 days, no credit card
- **Activate key**: `license_status(action="activate", license_key="YOUR-KEY")`
- **Pricing**: `license_status(action="upgrade")`
""")]

    tier_info = result.get("tier_info", {})
    machine_id = result.get("machine_id", "unknown")
    activated_at = result.get("activated_at", "N/A")
    days = result.get("days_since_activation", 0)
    premium_unlocked = result.get("premium_unlocked", False)
    remaining = result.get("premium_unlock_remaining", 0)

    unlock_status = "Unlocked" if premium_unlocked else f"{remaining} days remaining"

    return [TextContent(type="text", text=f"""
# License Status

**Status**: Active

## Info
- **Tier**: {tier_info.get('name', 'Unknown')} ({tier_info.get('price', '?')})
- **Machine**: `{machine_id[:8]}...`
- **Activated at**: {activated_at[:19] if len(activated_at) > 19 else activated_at}
- **Days since activation**: {days}
- **Premium features**: {unlock_status}
""")]


async def _wrap_start_trial() -> list[TextContent]:
    """start_trial tool wrapper - 7-day Full Pro trial"""
    from .license_common import start_full_trial, get_full_trial_status, is_full_trial_active, load_license_cache

    # Already has a license? No need for trial
    cached = load_license_cache()
    if cached and cached.get("tier"):
        return [TextContent(type="text", text="""
# Pro Trial

You already have an active Pro license. No trial needed!

Use `license_status` to check your current plan.
""")]

    # Already in trial?
    status = get_full_trial_status()
    if status.get("active"):
        remaining = status.get("remaining_days", 0)
        return [TextContent(type="text", text=f"""
# Pro Trial Active

**{remaining} day(s) remaining** | All Pro features unlocked

Included:
- 8 C-Level AI managers (PM, CTO, QA, CDO, CMO, CFO, CSO, ERROR)
- Knowledge Base (decisions preserved across sessions)
- BLOCK mode (enforced spec-first)
- ship (lint -> test -> build -> evidence)
- Unlimited projects

Like it? Keep it:
- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)

→ `license_status(action="upgrade")`
""")]

    # Trial already expired?
    if not status.get("never_started", False) and not status.get("active", False):
        return [TextContent(type="text", text="""
# Pro Trial Expired

Your 7-day trial has ended.

- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)

→ `license_status(action="upgrade")`
""")]

    # Start new trial
    result = start_full_trial()
    remaining = result.get("remaining_days", 7)

    return [TextContent(type="text", text=f"""
# Pro Trial Started!

**{remaining} days of full Pro access** - no credit card required.

You now have:
- 8 C-Level AI managers (PM, CTO, QA, CDO, CMO, CFO, CSO, ERROR)
- Knowledge Base (decisions preserved across sessions)
- BLOCK mode (enforced spec-first coding)
- ship (one-click lint -> test -> build -> evidence)
- Unlimited projects
- All Pro templates (standard + detailed)

## Try these first
1. `manager(context="your current task")` - get 8-manager review
2. `record_decision(category="architecture", decision="...")` - save a decision
3. `ship(path=".")` - run full verification

## After trial
- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)
→ `license_status(action="upgrade")`
""")]


async def _upgrade_pro() -> list[TextContent]:
    """Pro upgrade guide"""
    return [TextContent(type="text", text="""
# Clouvel Pro

10 more tools that make Claude Code reliable.

## What You Get

| Tool | What it does |
|------|-------------|
| `error_learn` | Auto-generate NEVER/ALWAYS rules from error patterns |
| `memory_status` | Error memory dashboard with hit counts |
| `memory_search` | Search past errors by keyword |
| `memory_global_search` | Share error patterns across all projects |
| `drift_check` | Detect when work drifts from goals |
| `plan` | Detailed execution plans with dependencies |
| `meeting` | Full 8-manager C-Level review |
| `ship` | One-click lint+test+build with evidence |
| `record_decision` | Persistent knowledge base for decisions |
| `search_knowledge` | Search past decisions and context |

## Also Unlocked
- Full error history (not just last 5)
- 50 checkpoint slots (not 1)
- 4 managers + 2 questions each (not 2+1)

## Pricing

| Plan | Price |
|------|-------|
| Monthly | **$7.99/mo** |
| Annual | **$49/yr** (Early Adopter Pricing) |

## Purchase

https://polar.sh/clouvel

Or start a free 7-day trial first: `license_status(action="trial")`
""")]


async def _wrap_debug_runtime(args: dict) -> list[TextContent]:
    """Debug MCP runtime environment."""
    import sys
    import clouvel
    from .utils.entitlements import is_developer, is_clouvel_repo, can_use_pro
    from .tools.knowledge import can_use_kb

    project_path = args.get("project_path", "")

    # Gather runtime info
    info = {
        "sys.executable": sys.executable,
        "sys.path[:3]": sys.path[:3],
        "clouvel.__file__": clouvel.__file__,
        "project_path": project_path,
        "is_clouvel_repo": is_clouvel_repo(project_path) if project_path else "N/A (no path)",
        "is_developer": is_developer(project_path) if project_path else is_developer(),
        "can_use_pro": can_use_pro(project_path) if project_path else can_use_pro(),
        "can_use_kb": can_use_kb(project_path) if project_path else can_use_kb(),
        "env.CLOUVEL_DEV": os.getenv("CLOUVEL_DEV", "not set"),
        "env.CLOUVEL_DEV_MODE": os.getenv("CLOUVEL_DEV_MODE", "not set"),
    }

    output = "# 🔧 Debug Runtime\n\n"
    for k, v in info.items():
        output += f"**{k}**: `{v}`\n"

    # Quick diagnosis
    output += "\n## Diagnosis\n"
    if "site-packages" in str(clouvel.__file__):
        output += "⚠️ Using **installed package** (not local source)\n"
    elif "D:" in str(clouvel.__file__) or "clouvel" in str(clouvel.__file__).lower():
        output += "✅ Using **local source**\n"

    if info["is_developer"]:
        output += "✅ Developer mode: **ACTIVE**\n"
    else:
        output += "❌ Developer mode: **INACTIVE** (Pro features blocked)\n"

    return [TextContent(type="text", text=output)]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    global _version_check_done

    # 첫 호출 시 버전 체크 (어떤 도구든)
    if not _version_check_done:
        _check_version_once()

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

    # Analytics 기록
    if name != "get_analytics":
        try:
            log_tool_call(name, success=True, project_path=project_path)
        except Exception:
            pass

    # get_analytics 특별 처리
    if name == "get_analytics":
        return await _get_analytics(arguments.get("path", None), arguments.get("days", 30))

    # get_ab_report 특별 처리 (v3.3)
    if name == "get_ab_report":
        return await _get_ab_report(arguments.get("days", 7), arguments.get("experiment"))

    # get_monthly_report 특별 처리 (v3.3 Week 4)
    if name == "get_monthly_report":
        return await _get_monthly_report(arguments.get("days", 30))

    # decide_winner 특별 처리 (v3.3 Week 4)
    if name == "decide_winner":
        return await _decide_winner(
            arguments.get("experiment", ""),
            arguments.get("min_confidence", "medium")
        )

    # 핸들러 실행
    handler = TOOL_HANDLERS.get(name)
    if handler:
        result = await handler(arguments)

        # 첫 호출이고 업데이트 있으면 배너 추가
        update_info = get_cached_update_info()
        if update_info and update_info.get("update_available"):
            banner = get_update_banner()
            if banner and result and len(result) > 0:
                # 첫 번째 결과에 배너 prepend
                original_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                result[0] = TextContent(type="text", text=banner + "\n" + original_text)
                # 배너는 한 번만 표시
                update_info["update_available"] = False

        return result

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _get_analytics(path: str, days: int) -> list[TextContent]:
    """Tool usage statistics"""
    stats = get_stats(days=days, project_path=path)
    return [TextContent(type="text", text=format_stats(stats))]


async def _get_ab_report(days: int, experiment: str = None) -> list[TextContent]:
    """A/B testing analytics report (v3.3)"""
    from .analytics import get_ab_report, format_ab_report, analyze_ab_experiment

    if experiment:
        # Single experiment analysis
        analysis = analyze_ab_experiment(experiment, days)
        lines = [
            f"# A/B Test: {experiment}",
            f"Period: Last {days} days",
            "",
        ]
        if analysis["variants"]:
            lines.append("| Variant | Impressions | Conversions | Rate |")
            lines.append("|---------|-------------|-------------|------|")
            for variant, data in analysis["variants"].items():
                winner = " *" if variant == analysis.get("winner") else ""
                lines.append(
                    f"| {variant}{winner} | {data['impressions']} | "
                    f"{data['conversions']} | {data['rate']}% |"
                )
            lines.append("")
            lines.append(f"**Uplift:** {analysis['uplift']:+.1f}%")
            lines.append(f"**Confidence:** {analysis['confidence']}")
        else:
            lines.append("_No data collected yet_")
        return [TextContent(type="text", text="\n".join(lines))]
    else:
        # Full report
        report = get_ab_report(days)
        return [TextContent(type="text", text=format_ab_report(report))]


async def _get_monthly_report(days: int) -> list[TextContent]:
    """Monthly KPI dashboard (v3.3 Week 4)"""
    from .analytics import get_monthly_kpis, format_monthly_report

    kpis = get_monthly_kpis(days)
    return [TextContent(type="text", text=format_monthly_report(kpis))]


async def _decide_winner(experiment: str, min_confidence: str) -> list[TextContent]:
    """Decide if experiment winner can be promoted (v3.3 Week 4)"""
    from .analytics import decide_experiment_winner, promote_winning_variant

    if not experiment:
        return [TextContent(type="text", text="Error: experiment name is required")]

    decision = decide_experiment_winner(experiment, min_confidence)
    promotion = promote_winning_variant(experiment)

    lines = [
        f"# Experiment Decision: {experiment}",
        "",
        f"## Analysis",
        f"- Decision: **{decision['decision'].upper()}**",
        f"- Reason: {decision['reason']}",
        "",
    ]

    if decision["ready_for_rollout"]:
        lines.extend([
            f"## Ready for Promotion",
            f"- Winner: **{decision['winner']}**",
            f"- Winner value: `{promotion.get('winner_value')}`",
            f"- Previous rollout: {promotion.get('previous_rollout')}%",
            f"- New rollout: {promotion.get('new_rollout')}%",
            "",
            "### Code Change Required:",
            "```python",
            promotion.get("code_change", "").strip(),
            "```",
        ])
    else:
        lines.extend([
            f"## Action Required",
            f"- {promotion.get('action_required', 'Continue collecting data')}",
        ])

    return [TextContent(type="text", text="\n".join(lines))]


# ============================================================
# Server Entry Points
# ============================================================

async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _run_setup(global_only: bool = False, hooks: bool = False) -> str:
    """B0: clouvel setup - install forced invocation mechanism"""
    import subprocess
    import os
    from pathlib import Path

    results = []

    # --hooks: Install pre-commit hooks in current project
    if hooks:
        git_hooks_dir = Path(".git/hooks")
        if git_hooks_dir.exists():
            pre_commit = git_hooks_dir / "pre-commit"
            pre_commit_content = '''#!/bin/bash
# Clouvel pre-commit hook (v1.6)
# 1. PRD check
# 2. Record files check (files/created.md, status/current.md)
# 3. New files tracking check
# 4. Sensitive files check

# === PRD Check ===
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    echo "Please create docs/PRD.md first."
    exit 1
fi

# === Record Files Check (v1.5) ===
if [ ! -f ".claude/files/created.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: files/created.md missing"
    echo "========================================"
    echo ""
    echo "No file creation record found."
    echo "Fix: Create .claude/files/created.md before commit"
    echo ""
    exit 1
fi

if [ ! -f ".claude/status/current.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: status/current.md missing"
    echo "========================================"
    echo ""
    echo "No work status record found."
    echo "Fix: Create .claude/status/current.md before commit"
    echo ""
    exit 1
fi

# === New Files Tracking Check (v1.6) ===
# Check if newly added files are recorded in created.md
CREATED_MD=".claude/files/created.md"
NEW_FILES=$(git diff --cached --name-only --diff-filter=A 2>/dev/null)

# Skip certain files/patterns from tracking requirement
SKIP_PATTERNS="(\\.md$|\\.txt$|\\.json$|\\.yml$|\\.yaml$|\\.gitignore|\\.env|__pycache__|\\.pyc$|node_modules|\\.git)"

if [ -n "$NEW_FILES" ] && [ -f "$CREATED_MD" ]; then
    UNTRACKED=""
    while IFS= read -r file; do
        # Skip files matching skip patterns
        if echo "$file" | grep -qE "$SKIP_PATTERNS"; then
            continue
        fi
        # Check if file is recorded in created.md
        if ! grep -qF "$file" "$CREATED_MD" 2>/dev/null; then
            UNTRACKED="$UNTRACKED$file\n"
        fi
    done <<< "$NEW_FILES"

    if [ -n "$UNTRACKED" ]; then
        echo ""
        echo "========================================"
        echo "[Clouvel] WARNING: Untracked new files"
        echo "========================================"
        echo ""
        echo "These files are not recorded in .claude/files/created.md:"
        echo -e "$UNTRACKED" | while read -r file; do
            [ -n "$file" ] && echo "  📁 $file"
        done
        echo ""
        echo "To record these files, copy & run in Claude:"
        echo "────────────────────────────────────────"
        echo -e "$UNTRACKED" | while read -r file; do
            [ -n "$file" ] && echo 'record_file(path=".", file_path="'"$file"'", purpose="...")'
        done
        echo "────────────────────────────────────────"
        echo ""
        echo "Continuing commit... (this is a warning, not a block)"
        echo ""
    fi
fi

# === Security Check (sensitive files) ===
SENSITIVE_PATTERNS="(marketing|strategy|pricing|server_pro|_pro\\.py|\\.key$|\\.secret$|credentials|password)"

SENSITIVE_FILES=$(git diff --cached --name-only | grep -iE "$SENSITIVE_PATTERNS" 2>/dev/null)

if [ -n "$SENSITIVE_FILES" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] SECURITY BLOCK: Sensitive files detected!"
    echo "========================================"
    echo ""
    echo "Cannot commit these files:"
    echo "$SENSITIVE_FILES" | while read -r file; do
        echo "  ❌ $file"
    done
    echo ""
    echo "Fix: git reset HEAD <filename>"
    echo "Skip: git commit --no-verify (not recommended)"
    echo ""
    exit 1
fi

echo "[Clouvel] All checks passed. ✓"
'''
            pre_commit.write_text(pre_commit_content, encoding='utf-8')
            try:
                os.chmod(pre_commit, 0o755)
            except:
                pass
            results.append(f"[OK] Pre-commit hook installed: {pre_commit}")
            return "\n".join(results)
        else:
            return "[ERROR] .git/hooks not found. Run from git repository root."

    # 1. Add rules to global CLAUDE.md
    if os.name == 'nt':  # Windows
        claude_dir = Path.home() / ".claude"
    else:  # Mac/Linux
        claude_dir = Path.home() / ".claude"

    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_md_path = claude_dir / "CLAUDE.md"

    clouvel_rule = """
## Clouvel Rules (Auto-generated)

**Must call clouvel's `can_code` tool before writing code.**

- Always call `can_code` tool before writing code (Edit/Write)
- Pass the project's docs folder path as the path argument
- If BLOCK appears, do not write code, guide user to write documentation
- If PASS appears, proceed with coding
- WARN is a recommendation, can proceed but suggest adding recommended docs

**Must call `record_file` after creating important files.**

- After creating a new file with Write tool, call `record_file` to track it
- Required fields: path (project root), file_path (relative), purpose (what it does)
- Skip for: temporary files, test data, config files (.json, .yml, .env)
- This enables file tracking and prevents accidental deletion

"""

    marker = "## Clouvel Rules"
    marker_ko = "## Clouvel 규칙"

    if claude_md_path.exists():
        content = claude_md_path.read_text(encoding='utf-8')
        if marker in content or marker_ko in content:
            results.append("[OK] Global CLAUDE.md: Clouvel rules already exist")
        else:
            # Append to existing content
            new_content = content.rstrip() + "\n\n---\n" + clouvel_rule
            claude_md_path.write_text(new_content, encoding='utf-8')
            results.append(f"[OK] Global CLAUDE.md: Rules added ({claude_md_path})")
    else:
        # Create new
        initial_content = f"# Claude Code Global Settings\n\n> Auto-generated by clouvel setup\n\n---\n{clouvel_rule}"
        claude_md_path.write_text(initial_content, encoding='utf-8')
        results.append(f"[OK] Global CLAUDE.md: Created ({claude_md_path})")

    # 2. Register MCP server (only when not global_only)
    if not global_only:
        try:
            # First check existing registration
            check_result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "clouvel" in check_result.stdout:
                results.append("[OK] MCP Server: Already registered")
            else:
                # Register
                add_result = subprocess.run(
                    ["claude", "mcp", "add", "clouvel", "-s", "user", "--", "clouvel"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if add_result.returncode == 0:
                    results.append("[OK] MCP Server: Registration complete")
                else:
                    results.append(f"[WARN] MCP Server: Registration failed - {add_result.stderr.strip()}")
                    results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")
        except FileNotFoundError:
            results.append("[WARN] MCP Server: claude command not found")
            results.append("   Please install Claude Code and try again")
        except subprocess.TimeoutExpired:
            results.append("[WARN] MCP Server: Timeout")
            results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")
        except Exception as e:
            results.append(f"[WARN] MCP Server: Error - {str(e)}")
            results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")

    # Output results
    output = """
================================================================
                    Clouvel Setup Complete
================================================================

"""
    output += "\n".join(results)
    output += """

----------------------------------------------------------------

## How It Works

1. Run Claude Code
2. Request "Build a login feature"
3. Claude automatically calls can_code first
4. No PRD -> [BLOCK] BLOCK (coding blocked)
5. PRD exists -> [OK] PASS (proceed with coding)

## Test

```bash
# Test in a folder without PRD
mkdir test-project && cd test-project
claude
> "Write some code"
# -> Verify BLOCK message
```

----------------------------------------------------------------
"""

    return output


def main():
    import sys
    import asyncio
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Clouvel - Vibe coding process enforcement tool")
    subparsers = parser.add_subparsers(dest="command")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("-p", "--path", default=".", help="Project path")
    init_parser.add_argument("-l", "--level", choices=["remind", "strict", "full"], default="strict")

    # setup command (B0) - legacy, install recommended
    setup_parser = subparsers.add_parser("setup", help="Install Clouvel forced invocation mechanism (global)")
    setup_parser.add_argument("--global-only", action="store_true", help="Configure CLAUDE.md only (exclude MCP registration)")
    setup_parser.add_argument("--hooks", action="store_true", help="Install pre-commit hooks for record enforcement")
    setup_parser.add_argument("--proactive", choices=["free", "pro"], help="Setup proactive hooks (v2.0) - auto PRD check, drift detection")
    setup_parser.add_argument("--path", "-p", default=".", help="Project root path")

    # install command (new, recommended)
    install_parser = subparsers.add_parser("install", help="Install Clouvel MCP server (recommended)")
    install_parser.add_argument("--platform", choices=["auto", "code", "desktop", "cursor", "all"], default="auto", help="Target platform for installation")
    install_parser.add_argument("--force", action="store_true", help="Reinstall even if already installed")

    # can_code command (for hooks integration)
    can_code_parser = subparsers.add_parser("can_code", help="Check if coding is allowed (for hooks)")
    can_code_parser.add_argument("--path", "-p", default=".", help="Project docs path")
    can_code_parser.add_argument("--silent", "-s", action="store_true", help="Silent mode - exit code only")

    # drift_check command (for hooks integration)
    drift_parser = subparsers.add_parser("drift_check", help="Check for context drift (Pro)")
    drift_parser.add_argument("--path", "-p", default=".", help="Project root path")
    drift_parser.add_argument("--silent", "-s", action="store_true", help="Silent mode - minimal output")

    # activate command (license activation)
    activate_parser = subparsers.add_parser("activate", help="Activate license")
    activate_parser.add_argument("license_key", help="License key")

    # status command (license status)
    status_parser = subparsers.add_parser("status", help="Check license status")

    # gate_check command (lightweight hook check)
    gate_check_parser = subparsers.add_parser("gate_check", help="Lightweight gate check for PreToolUse hooks")

    # deactivate command (license deactivation)
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate license (delete local cache)")

    args = parser.parse_args()

    if args.command == "init":
        from .tools.setup import setup_cli as sync_setup
        import asyncio
        result = asyncio.run(sync_setup(args.path, args.level))
        print(result[0].text)
    elif args.command == "setup":
        # Handle --proactive option
        if hasattr(args, 'proactive') and args.proactive:
            from .tools.setup import setup_cli as sync_setup
            result = asyncio.run(sync_setup(
                path=args.path if hasattr(args, 'path') else ".",
                proactive=args.proactive
            ))
            print(result[0].text)
        else:
            result = _run_setup(
                global_only=args.global_only if hasattr(args, 'global_only') else False,
                hooks=args.hooks if hasattr(args, 'hooks') else False
            )
            print(result)
    elif args.command == "install":
        from .tools.install import run_install
        result = run_install(
            platform=args.platform if hasattr(args, 'platform') else "auto",
            force=args.force if hasattr(args, 'force') else False
        )
        print(result)
    elif args.command == "can_code":
        # CLI for hooks integration
        from .tools.core import can_code as sync_can_code
        result = asyncio.run(sync_can_code(args.path))

        # Parse result to determine exit code
        result_text = result[0].text if result else ""
        is_block = "BLOCK" in result_text
        is_warn = "WARN" in result_text

        if args.silent:
            # Silent mode: just exit code
            if is_block:
                sys.exit(1)  # BLOCK = fail
            else:
                sys.exit(0)  # PASS or WARN = ok
        else:
            # Normal mode: print result
            print(result_text)
            if is_block:
                sys.exit(1)
    elif args.command == "drift_check":
        # CLI for hooks integration
        from .tools.proactive import drift_check as sync_drift_check
        result = asyncio.run(sync_drift_check(args.path, silent=args.silent))

        result_text = result[0].text if result else ""

        if args.silent:
            print(result_text)  # Short status like "OK:0" or "DRIFT:75"
            if "DRIFT" in result_text:
                sys.exit(1)
            sys.exit(0)
        else:
            print(result_text)
            if "DRIFT" in result_text or "🚨" in result_text:
                sys.exit(1)
    elif args.command == "activate":
        try:
            from .license import activate_license_cli
        except ImportError:
            from .license_free import activate_license_cli
        result = activate_license_cli(args.license_key)
        if result["success"]:
            print(f"""
================================================================
              Clouvel Pro License Activated
================================================================

{result['message']}

Tier: {result.get('tier_info', {}).get('name', 'Unknown')}
Machine: {result.get('machine_id', 'Unknown')[:8]}...
Product: {result.get('product', 'Clouvel Pro')}

----------------------------------------------------------------
Premium features will be available 7 days after activation.
Check status with 'clouvel status'.
================================================================
""")
        else:
            print(result["message"])
            sys.exit(1)
    elif args.command == "status":
        try:
            from .license import get_license_status
        except ImportError:
            from .license_free import get_license_status
        result = get_license_status()
        if result.get("has_license"):
            tier_info = result.get("tier_info", {})
            unlock_status = "[OK] Unlocked" if result.get("premium_unlocked") else f"[...] {result.get('premium_unlock_remaining', '?')} days remaining"
            print(f"""
================================================================
                   Clouvel License Status
================================================================

Status: [OK] Activated
Tier: {tier_info.get('name', 'Unknown')} ({tier_info.get('price', '?')})
Machine: {result.get('machine_id', 'Unknown')[:8]}...

Activated at: {result.get('activated_at', 'N/A')[:19]}
Days since activation: {result.get('days_since_activation', 0)}
Premium features: {unlock_status}

================================================================
""")
        else:
            print(f"""
================================================================
                   Clouvel License Status
================================================================

Status: [X] Not activated

{result.get('message', '')}

Start trial: clouvel activate --trial
Purchase:    https://polar.sh/clouvel
================================================================
""")
    elif args.command == "gate_check":
        # Lightweight gate check — calls main() directly
        from .gate_check import main as gate_main
        sys.exit(gate_main())
    elif args.command == "deactivate":
        try:
            from .license import deactivate_license_cli
        except ImportError:
            from .license_free import deactivate_license_cli
        result = deactivate_license_cli()
        print(result["message"])
        if not result["success"]:
            sys.exit(1)
    else:
        asyncio.run(run_server())


# ============================================================
# Proactive Tool Wrappers (v2.0)
# ============================================================

async def _wrap_drift_check(args: dict) -> list[TextContent]:
    """drift_check tool wrapper"""
    return await drift_check(
        path=args.get("path", "."),
        silent=args.get("silent", False)
    )


async def _wrap_pattern_watch(args: dict) -> list[TextContent]:
    """pattern_watch tool wrapper"""
    return await pattern_watch(
        path=args.get("path", "."),
        threshold=args.get("threshold", 3),
        check_only=args.get("check_only", False)
    )


async def _wrap_auto_remind(args: dict) -> list[TextContent]:
    """auto_remind tool wrapper"""
    return await auto_remind(
        path=args.get("path", "."),
        interval=args.get("interval", 30),
        enabled=args.get("enabled", True)
    )


if __name__ == "__main__":
    main()
