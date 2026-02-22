# -*- coding: utf-8 -*-
"""
Clouvel Tool Dispatch

TOOL_HANDLERS dict mapping tool names to handler functions,
plus all _wrap_* adapter functions.
Extracted from server.py for maintainability.
"""

import os
from mcp.types import TextContent

from .analytics import get_stats, format_stats
from .api_client import call_manager_api
from .version_check import get_v3_migration_notice, get_v1_pivot_notice
from .version_check import init_version_check

from .tools import (
    # core
    can_code, scan_docs, analyze_docs, init_docs, get_prd_template, list_templates, write_prd_section, get_prd_guide, get_verify_checklist, get_setup_guide,
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
    start, save_prd,
    # tracking (v1.5)
    record_file, list_files,
    # knowledge (Free, v1.4)
    record_decision, record_location, search_knowledge, get_context, init_knowledge, rebuild_index,
    unlock_decision, list_locked_decisions,
    # manager (Pro, v1.2)
    list_managers, ship, quick_ship, full_ship,
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
        memory_list, memory_search, memory_archive, memory_report,
        memory_promote, memory_global_search,
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

# License module import
try:
    from .license import activate_license_cli, get_license_status
except ImportError:
    from .license_free import activate_license_cli, get_license_status


# Version check state (shared with server.py)
_version_check_done = False

# v4.0: Server-side state sync (run once per session)
_sync_done = False


def _ensure_sync_once():
    """Trigger background sync on first tool call."""
    global _sync_done
    if not _sync_done:
        _sync_done = True
        try:
            from .licensing.sync import SyncState
            SyncState.get().sync_async()
        except (ImportError, OSError):
            pass

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
        from .license_common import is_developer, is_kb_trial_active, start_kb_trial
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
        from .db.knowledge import record_meeting, get_or_create_project
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
            lines.append("\nUnlock all managers with Pro → `license_status(action=\"trial\")`")

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
    from .license_common import start_full_trial, get_full_trial_status, load_license_cache

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


# ============================================================
# Analytics Helpers (called by server.call_tool for special tools)
# ============================================================

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
        "## Analysis",
        f"- Decision: **{decision['decision'].upper()}**",
        f"- Reason: {decision['reason']}",
        "",
    ]

    if decision["ready_for_rollout"]:
        lines.extend([
            "## Ready for Promotion",
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
            "## Action Required",
            f"- {promotion.get('action_required', 'Continue collecting data')}",
        ])

    return [TextContent(type="text", text="\n".join(lines))]

