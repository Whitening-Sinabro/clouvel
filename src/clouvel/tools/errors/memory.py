# -*- coding: utf-8 -*-
"""Memory tools (v4.0, v5.0): memory_status, memory_list, memory_search,
memory_archive, memory_report, memory_promote, memory_global_search,
set_project_domain"""

from pathlib import Path
from mcp.types import TextContent

from ._shared import (
    require_license_premium,
    DB_AVAILABLE,
    REGRESSION_AVAILABLE,
    GLOBAL_MEMORY_AVAILABLE,
)

# Conditional imports from _shared (only available when flags are True)
if DB_AVAILABLE:
    from ._shared import init_db

if REGRESSION_AVAILABLE:
    from ._shared import (
        db_get_memory_stats,
        db_list_memories_reg,
        db_search_memories,
        db_archive_memory,
        db_unarchive_memory,
        db_mark_stale_memories,
        db_get_memory_report,
        db_get_memory,
        db_get_memory_for_promote,
    )

if GLOBAL_MEMORY_AVAILABLE:
    from ._shared import (
        kb_promote_memory,
        kb_search_global_memories,
        kb_get_or_create_project,
        kb_get_project_domain,
        kb_set_project_domain,
    )


# ============================================================
# Regression Memory Status (v4.0)
# ============================================================

@require_license_premium
async def memory_status(
    path: str,
) -> list[TextContent]:
    """
    Regression Memory status and statistics.

    Args:
        path: Project root path
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    stats = db_get_memory_stats(project_path=path)

    result = "# Regression Memory Status\n\n"

    # One-line summary
    result += f"**{stats['active']} active memories** | "
    result += f"{stats['total_hits']} hits | "
    result += f"{stats['total_saves']} saves | "
    result += f"{stats['save_rate']}% save rate\n\n"

    # Top memories
    if stats.get("top_memories"):
        result += "## Top Memories (by hit count)\n\n"
        result += "| # | Category | Signature | Hits | Saves |\n"
        result += "|---|----------|-----------|------|-------|\n"
        for m in stats["top_memories"]:
            sig_short = m["error_signature"][:40] + "..." if len(m["error_signature"]) > 40 else m["error_signature"]
            result += f"| {m['id']} | {m['error_category']} | {sig_short} | {m['hit_count']} | {m['times_saved']} |\n"
        result += "\n"

    # Category breakdown
    if stats.get("categories"):
        result += "## Categories\n\n"
        for cat, count in stats["categories"].items():
            result += f"- **{cat}**: {count}\n"
        result += "\n"

    # Summary
    if stats["archived"] > 0:
        result += f"*{stats['archived']} archived memories not shown*\n"

    # Auto-stale: archive memories with 0 hits older than 60 days
    try:
        stale_result = db_mark_stale_memories(days_threshold=60, project_path=path)
        if stale_result["archived_count"] > 0:
            result += f"\n*{stale_result['archived_count']} stale memories auto-archived (0 hits, >60 days)*\n"
    except Exception:
        pass

    return [TextContent(type="text", text=result)]


# ============================================================
# Regression Memory Management (v4.0 Phase 2)
# ============================================================

@require_license_premium
async def memory_list(
    path: str,
    category: str = "",
    include_archived: bool = False,
    limit: int = 20,
) -> list[TextContent]:
    """
    List regression memories with optional category filter.

    Args:
        path: Project root path
        category: Filter by error category (optional)
        include_archived: Include archived memories (default false)
        limit: Max results (default 20)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    memories = db_list_memories_reg(
        include_archived=include_archived,
        limit=limit,
        project_path=path,
    )

    # Apply category filter if provided
    if category:
        memories = [m for m in memories if m.get("error_category") == category]

    if not memories:
        return [TextContent(type="text", text="# Regression Memories\n\nNo memories found.")]

    result = f"# Regression Memories ({len(memories)} results)\n\n"
    result += "| ID | Category | Signature | Hits | Saves | Date |\n"
    result += "|----|----------|-----------|------|-------|------|\n"

    for m in memories:
        sig_short = m["error_signature"][:40] + "..." if len(m["error_signature"]) > 40 else m["error_signature"]
        date = m.get("timestamp", "")[:10] if m.get("timestamp") else "-"
        archived_tag = " [A]" if m.get("archived") else ""
        result += f"| {m['id']}{archived_tag} | {m.get('error_category', '-')} | {sig_short} | {m.get('hit_count', 0)} | {m.get('times_saved', 0)} | {date} |\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def memory_search(
    path: str,
    query: str,
    category: str = "",
) -> list[TextContent]:
    """
    Search regression memories by keyword (FTS5).

    Args:
        path: Project root path
        query: Search keyword
        category: Filter by category (optional)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    memories = db_search_memories(
        query=query,
        category=category,
        project_path=path,
    )

    if not memories:
        return [TextContent(type="text", text=f'# Memory Search: "{query}"\n\nNo matching memories found.')]

    result = f'# Memory Search: "{query}" ({len(memories)} results)\n\n'

    for m in memories:
        result += f"## Memory #{m['id']} — {m.get('error_category', 'unknown')}\n\n"
        result += f"**Signature**: {m['error_signature'][:80]}\n"
        if m.get("root_cause"):
            result += f"**Root Cause**: {m['root_cause'][:150]}\n"
        if m.get("prevention_rule"):
            result += f"**Prevention**: {m['prevention_rule'][:150]}\n"
        result += f"**Hits**: {m.get('hit_count', 0)} | **Saves**: {m.get('times_saved', 0)}\n\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def memory_archive(
    path: str,
    memory_id: int,
    action: str = "archive",
) -> list[TextContent]:
    """
    Archive or unarchive a regression memory.

    Args:
        path: Project root path
        memory_id: Memory ID to archive/unarchive
        action: "archive" or "unarchive" (default: archive)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)

    if action == "unarchive":
        res = db_unarchive_memory(memory_id, project_path=path)
    else:
        res = db_archive_memory(memory_id, project_path=path)

    if res.get("status") == "not_found":
        return [TextContent(type="text", text=f"# Memory Not Found\n\nMemory #{memory_id} does not exist.")]

    return [TextContent(type="text", text=f"# Memory #{memory_id} {res['status'].title()}\n\nAction completed successfully.")]


@require_license_premium
async def memory_report(
    path: str,
    days: int = 30,
) -> list[TextContent]:
    """
    Monthly regression memory report.

    Args:
        path: Project root path
        days: Report period in days (default 30)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    report = db_get_memory_report(days=days, project_path=path)

    # One-line summary
    result = f"# Regression Memory Report ({report['period_days']} days)\n\n"
    result += f"> **{report['total_saves']} errors prevented** | "
    result += f"~{report['time_saved_hours']}h saved | "
    result += f"{report['save_rate']}% save rate\n\n"

    # Detailed stats
    result += "## Statistics\n\n"
    result += f"- **New memories**: {report['new_memories']}\n"
    result += f"- **Active memories**: {report['active']}\n"
    result += f"- **Archived**: {report['archived']}\n"
    result += f"- **Total hits**: {report['total_hits']}\n"
    result += f"- **Total saves**: {report['total_saves']}\n"
    result += f"- **Save rate**: {report['save_rate']}%\n\n"

    # Time saved estimate
    result += "## Time Saved Estimate\n\n"
    result += f"- **{report['total_saves']}** errors prevented x **15 min** avg debug time\n"
    result += f"- **= {report['time_saved_minutes']} minutes ({report['time_saved_hours']} hours) saved**\n\n"

    # Top memories
    if report.get("top_memories"):
        result += "## Top Memories (by hit count)\n\n"
        result += "| # | Category | Root Cause | Hits | Saves |\n"
        result += "|---|----------|-----------|------|-------|\n"
        for m in report["top_memories"]:
            rc_short = m["root_cause"][:50] + "..." if len(m["root_cause"]) > 50 else m["root_cause"]
            result += f"| {m['id']} | {m['error_category']} | {rc_short} | {m['hit_count']} | {m['times_saved']} |\n"
        result += "\n"

    # Top categories
    if report.get("top_categories"):
        result += "## Top Categories\n\n"
        for c in report["top_categories"]:
            result += f"- **{c['category']}**: {c['count']} memories\n"

    return [TextContent(type="text", text=result)]


# ============================================================
# Cross-Project Memory Transfer (v5.0)
# ============================================================

@require_license_premium
async def memory_promote(
    path: str,
    memory_id: int,
) -> list[TextContent]:
    """
    Promote a local regression memory to global (cross-project).

    Only root_cause and prevention_rule are promoted (no raw error text).
    Requires hit_count >= 1 to ensure quality.

    Args:
        path: Project root path
        memory_id: Local memory ID to promote
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]
    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    init_db(path)

    # Get local memory (full data for validation)
    local_mem = db_get_memory(memory_id, project_path=path)
    if local_mem is None:
        return [TextContent(type="text", text=f"# Memory Not Found\n\nLocal memory #{memory_id} does not exist.")]

    # Validate: hit_count >= 1 (zero-hit memories are unproven)
    if local_mem.get("hit_count", 0) < 1:
        return [TextContent(type="text", text=f"""# Cannot Promote Memory #{memory_id}

**Reason**: Memory has 0 hits. Only memories that have been matched at least once can be promoted to global.

**Tip**: Use this memory in error_check first to build confidence, then promote.
""")]

    # Get promote-safe data (excludes sensitive fields)
    promote_data = db_get_memory_for_promote(memory_id, project_path=path)
    if promote_data is None:
        return [TextContent(type="text", text=f"# Memory Not Found\n\nLocal memory #{memory_id} does not exist.")]

    # Get or create project in knowledge DB
    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    # Auto-inherit domain from project
    project_domain = kb_get_project_domain(project_id) if GLOBAL_MEMORY_AVAILABLE else None

    # Promote to global
    result = kb_promote_memory(promote_data, project_id, project_name, domain=project_domain)

    if result.get("status") == "duplicate":
        return [TextContent(type="text", text=f"""# Already Promoted

Memory #{memory_id} has already been promoted to global (Global ID: #{result.get('existing_id')}).
""")]

    return [TextContent(type="text", text=f"""# Memory #{memory_id} Promoted to Global

**Global ID**: #{result['id']}
**Root Cause**: {promote_data['root_cause'][:150]}
**Prevention**: {promote_data['prevention_rule'][:150]}

This memory is now available across all projects via `memory_global_search`.
""")]


@require_license_premium
async def memory_global_search(
    path: str,
    query: str,
    category: str = "",
    domain: str = "",
) -> list[TextContent]:
    """
    Search global regression memories from all projects.

    Finds patterns learned in other projects. Current project is excluded
    from results (use local memory_search for that).

    Args:
        path: Project root path
        query: Search keyword
        category: Filter by error category (optional)
        domain: Filter by domain (personal/work/client). Auto-detected if not specified.
    """
    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    # Get current project ID to exclude from results
    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    # Auto-detect domain from project if not specified
    effective_domain = domain or None
    if not effective_domain:
        try:
            effective_domain = kb_get_project_domain(project_id) or None
        except Exception:
            pass

    memories = kb_search_global_memories(
        query=query,
        project_id_exclude=project_id,
        category=category or None,
        domain=effective_domain,
    )

    if not memories:
        return [TextContent(type="text", text=f'# Global Memory Search: "{query}"\n\nNo matching memories found in other projects.')]

    result = f'# Global Memory Search: "{query}" ({len(memories)} results)\n\n'

    for m in memories:
        result += f"## Global #{m['id']} — {m.get('error_category', 'unknown')}\n\n"
        result += f"**Origin**: {m.get('origin_project_name', 'unknown')}\n"
        result += f"**Root Cause**: {m.get('root_cause', '')[:150]}\n"
        result += f"**Prevention**: {m.get('prevention_rule', '')[:150]}\n"
        result += f"**Hits**: {m.get('hit_count', 0)} | **Saves**: {m.get('times_saved', 0)}\n\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def set_project_domain(
    path: str,
    domain: str,
) -> list[TextContent]:
    """
    Set the domain for the current project. Domains isolate memories.

    Args:
        path: Project root path
        domain: Domain value (personal/work/client)
    """
    valid_domains = ("personal", "work", "client")
    if domain not in valid_domains:
        return [TextContent(type="text", text=f"# Invalid Domain\n\nDomain must be one of: {', '.join(valid_domains)}\n\nGot: `{domain}`")]

    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    result = kb_set_project_domain(project_id, domain)

    if result.get("status") == "not_found":
        return [TextContent(type="text", text=f"# Project Not Found\n\nCould not find project with ID: {project_id}")]

    return [TextContent(type="text", text=f"""# Project Domain Set

**Project**: {project_name}
**Domain**: {domain}

Memories promoted from this project will inherit the `{domain}` domain.
Global memory searches will be scoped to `{domain}` domain by default.
""")]
