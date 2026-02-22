# -*- coding: utf-8 -*-
"""Project-related formatters (start, save_prd, archive, list_projects).

Extracted from tool_dispatch.py.
"""


def format_start(result: dict, rules_msg: str = None) -> str:
    """Format start tool result."""
    status = result.get("status", "UNKNOWN")

    if status in ("GUIDE", "INITIALIZED", "TEMPLATE"):
        return result.get("message", "")

    ptype = result.get("project_type", {})
    type_info = (
        f"**Type**: {ptype.get('description', 'N/A')} "
        f"({ptype.get('type', 'generic')}) - "
        f"Confidence {ptype.get('confidence', 0)}%"
    )

    output = f"""# 🚀 Start

**Status**: {status}
**Project**: {result.get('project_name', 'N/A')}
{type_info}

{result.get('message', '')}
"""

    if result.get("status") == "NEED_PRD" and result.get("prd_guide"):
        guide = result["prd_guide"]
        output += guide.get("instruction", "")

    output += "\n## Next Steps\n"
    for step in result.get('next_steps', []):
        output += f"- {step}\n"

    if result.get('created_files'):
        output += "\n## Created Files\n"
        for f in result['created_files']:
            output += f"- {f}\n"

    if rules_msg:
        output += f"\n## Rules\n{rules_msg}\n"

    return output


def format_save_prd(result: dict) -> str:
    output = f"""# 📝 Save PRD

**Status**: {result.get('status', 'UNKNOWN')}
**Path**: {result.get('prd_path', 'N/A')}

{result.get('message', '')}
"""
    if result.get('next_steps'):
        output += "\n## Next Steps\n"
        for step in result['next_steps']:
            output += f"- {step}\n"
    return output


def format_archive_project(result: dict) -> str:
    if result.get("success"):
        return f"""# 📦 Archive Project

{result.get('message', '')}

**Archived at**: {result.get('archived_at', 'N/A')}

Now you can start a new project with `start` tool.
"""
    return f"""# ❌ Archive Failed

{result.get('message', '')}
"""


def format_list_projects(result: dict) -> str:
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

    return output
