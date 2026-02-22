# -*- coding: utf-8 -*-
"""Knowledge Base result formatters.

Extracted from tool_dispatch.py _wrap_record_decision/location/search/context etc.
"""


def format_record_decision(result: dict) -> str:
    if result.get("status") == "recorded":
        locked_badge = "🔒 **LOCKED**" if result.get("locked") else ""
        return f"""# ✅ Decision Recorded {locked_badge}

**ID**: {result.get('decision_id')}
**Category**: {result.get('category')}
**Project**: {result.get('project_id', 'global')}

Decision saved to knowledge base. Use `search_knowledge` to retrieve later.
{"⚠️ This decision is LOCKED. Do not change without explicit user approval." if result.get("locked") else ""}
"""
    return f"""# ❌ Error Recording Decision

{result.get('error', 'Unknown error')}
"""


def format_record_location(result: dict) -> str:
    if result.get("status") == "recorded":
        return f"""# ✅ Location Recorded

**ID**: {result.get('location_id')}
**Name**: {result.get('name')}
**Repo**: {result.get('repo')}
**Path**: {result.get('path')}

Location saved to knowledge base.
"""
    return f"""# ❌ Error Recording Location

{result.get('error', 'Unknown error')}
"""


def format_search_knowledge(result: dict) -> str:
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
        return output
    return f"""# ❌ Search Error

{result.get('error', 'Unknown error')}
"""


def format_get_context(result: dict) -> str:
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
        return output
    return f"""# ❌ Error Getting Context

{result.get('error', 'Unknown error')}
"""


def format_init_knowledge(result: dict) -> str:
    if result.get("status") == "initialized":
        return f"""# ✅ Knowledge Base Initialized

**Database**: {result.get('db_path')}

{result.get('message', '')}

## Available Commands
- `record_decision` - Record a decision
- `record_location` - Record a code location
- `search_knowledge` - Search past knowledge
- `get_context` - Get recent context
"""
    return f"""# ❌ Initialization Error

{result.get('error', 'Unknown error')}
"""


def format_rebuild_index(result: dict) -> str:
    if result.get("status") == "rebuilt":
        return f"""# ✅ Search Index Rebuilt

**Indexed Items**: {result.get('indexed_count')}

{result.get('message', '')}
"""
    return f"""# ❌ Rebuild Error

{result.get('error', 'Unknown error')}
"""


def format_unlock_decision(result: dict) -> str:
    if result.get("status") == "unlocked":
        return f"""# 🔓 Decision Unlocked

**Decision ID**: {result.get('decision_id')}
**Category**: {result.get('category')}
**Decision**: {result.get('decision')}
**Unlock Reason**: {result.get('unlock_reason', 'Not specified')}

This decision can now be modified.
"""
    elif result.get("status") == "pro_required":
        return f"""# ⚠️ Pro Feature Required

{result.get('error')}

**Purchase**: {result.get('purchase')}
"""
    return f"""# ❌ Unlock Error

{result.get('error', 'Unknown error')}
"""


def format_list_locked_decisions(result: dict) -> str:
    if result.get("status") == "success":
        decisions = result.get("decisions", [])
        if not decisions:
            return "# 🔒 Locked Decisions\n\nNo locked decisions found."
        lines = ["# 🔒 Locked Decisions\n"]
        for d in decisions:
            lines.append(f"- **[{d['id']}]** [{d['category']}] {d['decision']}")
            if d.get('reasoning'):
                lines.append(f"  - Reason: {d['reasoning'][:100]}...")
        lines.append(f"\n**Total**: {result.get('count')} locked decisions")
        return "\n".join(lines)
    elif result.get("status") == "pro_required":
        return f"""# ⚠️ Pro Feature Required

{result.get('error')}

**Purchase**: {result.get('purchase')}
"""
    return f"""# ❌ Error

{result.get('error', 'Unknown error')}
"""
