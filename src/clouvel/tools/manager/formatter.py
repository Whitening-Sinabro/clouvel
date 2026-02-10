# Manager Formatter
# Output formatting functions

from typing import Dict, List, Any

from .data import MANAGERS

# Rich UI (optional)
try:
    from clouvel.ui import (
        render_manager_meeting,
        render_manager_panel,
        HAS_RICH,
        THEME,
    )
except ImportError:
    HAS_RICH = False
    render_manager_meeting = None
    render_manager_panel = None
    THEME = {}


def _format_output(result: Dict) -> str:
    """Formats results into a readable format.

    v1.5: Optimized for LLM attention patterns (U-shaped curve).
    - Critical issues at beginning AND end (bookending)
    - XML tags for better Claude parsing
    - Compressed, essential-first structure

    v1.9.1: Rich UI support for terminal output.
    """
    # Use Rich UI if available
    if HAS_RICH and render_manager_meeting:
        return _format_output_rich(result)

    # Fallback to plain text
    return _format_output_plain(result)


def _format_output_rich(result: Dict) -> str:
    """Rich UI version of manager output."""
    # Build title from detected topics
    topics = result['context_analysis']['detected_topics']
    title = f"Review: {', '.join(topics[:3])}" if topics else "Manager Review"

    # Map overall status
    overall_status = result.get("overall_status", "REVIEW_NEEDED")
    status_map = {
        "APPROVED": "APPROVED",
        "NEEDS_REVISION": "NEEDS_REVISION",
        "BLOCKED": "BLOCKED",
        "REVIEW_NEEDED": "NEEDS_REVISION",
    }
    status = status_map.get(overall_status, "NEEDS_REVISION")

    # Build feedbacks dict for render_manager_meeting
    feedbacks = {}
    for manager in result["active_managers"]:
        feedback = result["feedback"][manager]
        feedbacks[manager] = {
            "opinions": feedback.get("opinions", []),
            "warnings": feedback.get("warnings", []),
            "critical_issues": feedback.get("critical_issues", []),
            "questions": feedback.get("questions", []),
            "concerns": feedback.get("concerns", []),
        }

    # Build summary dict
    summary = {}
    for manager in result["active_managers"][:5]:
        feedback = result["feedback"][manager]
        if feedback.get("critical_issues"):
            status_icon = "🚫 BLOCKED"
        elif feedback.get("warnings"):
            status_icon = "🚨 Risk"
        elif feedback.get("missing_items"):
            status_icon = "📋 Missing"
        elif feedback.get("concerns"):
            status_icon = "⚠️ Caution"
        else:
            status_icon = "✅ Good"

        # Get note
        if feedback.get("critical_issues"):
            note = feedback["critical_issues"][0]
        elif feedback.get("opinions"):
            note = feedback["opinions"][0]
        elif feedback.get("warnings"):
            note = feedback["warnings"][0]
        else:
            note = "-"

        summary[manager] = {"status": status_icon, "note": note[:40] if len(note) > 40 else note}

    return render_manager_meeting(title, status, feedbacks, summary)


def _format_output_plain(result: Dict) -> str:
    """Plain text version of manager output (original implementation)."""
    lines = []

    # Collect critical items for bookending (will repeat at end)
    all_critical = result.get("critical_issues", [])
    all_warnings = result.get("warnings", [])

    # === BEGINNING: Critical issues first (primacy bias) ===
    if all_critical or all_warnings:
        lines.append("<critical_summary>")
        lines.append("🚨 CRITICAL ISSUES (Resolve before proceeding):")
        for issue in all_critical:
            lines.append(f"  • {issue}")
        for warning in all_warnings[:2]:
            lines.append(f"  ⚠️ {warning}")
        lines.append("</critical_summary>")
        lines.append("")

    # Claude instruction (compressed)
    lines.append("<instruction>")
    lines.append("Restructure RAW data below into natural meeting conversation.")
    lines.append("Rules: (1) Conversational tone (2) Be specific (3) Actionable items")
    lines.append("</instruction>")
    lines.append("")

    # 1. Situation analysis (with XML structure)
    lines.append("<situation_analysis>")
    topics = result['context_analysis']['detected_topics']
    lines.append(f"Topics: {', '.join(topics)}")

    overall_status = result.get("overall_status", "REVIEW_NEEDED")
    status_map = {"APPROVED": "✅", "NEEDS_REVISION": "⚠️", "BLOCKED": "🚫"}
    lines.append(f"Status: {status_map.get(overall_status, '🔍')} {overall_status}")

    lines.append(f"Managers: {', '.join(result['active_managers'])}")
    lines.append("</situation_analysis>")
    lines.append("")

    # Missing items (if any)
    if result.get("missing_items"):
        lines.append("<missing_items>")
        for item in result["missing_items"]:
            lines.append(f"- {item}")
        lines.append("</missing_items>")
        lines.append("")

    # 2. Meeting notes
    lines.append("<meeting_notes>")

    conversation = _generate_conversation(result)
    for line in conversation:
        lines.append(line)
    lines.append("</meeting_notes>")
    lines.append("")

    # 3. Final summary (with XML structure)
    lines.append("<final_summary>")

    lines.append("### Current Status")
    lines.append("")
    lines.append("| Area | Status | Note |")
    lines.append("|------|--------|------|")

    for m in result["active_managers"][:5]:
        feedback = result["feedback"][m]
        # Determine status: critical > warning > missing > concerns > approved
        if feedback.get("critical_issues"):
            status = "🚫 BLOCKED"
        elif feedback.get("warnings"):
            status = "🚨 Risk"
        elif feedback.get("missing_items"):
            status = "📋 Missing"
        elif feedback.get("concerns"):
            status = "⚠️ Caution"
        else:
            status = "✅ Good"

        # Determine note
        if feedback.get("critical_issues"):
            note = feedback["critical_issues"][0]
        elif feedback.get("missing_items"):
            note = feedback["missing_items"][0]
        elif feedback.get("opinions"):
            note = feedback["opinions"][0]
        elif feedback.get("warnings"):
            note = feedback["warnings"][0]
        elif feedback.get("concerns"):
            note = feedback["concerns"][0]
        else:
            note = "-"
        if len(note) > 40:
            note = note[:37] + "..."
        lines.append(f"| {feedback['emoji']} {m} | {status} | {note} |")
    lines.append("")

    # Immediate tasks
    action_items = result.get("action_items", [])
    if action_items:
        lines.append("### Immediate Tasks")
        lines.append("")
        lines.append("| # | Task | Owner | Why? |")
        lines.append("|---|------|-------|------|")
        for i, item in enumerate(action_items[:5], 1):
            lines.append(f"| {i} | {item['action']} | {item['emoji']} {item['manager']} | {item['verify']} |")
        lines.append("")

    # On hold / Later
    if len(action_items) > 5:
        lines.append("### On Hold (Later)")
        lines.append("")
        for item in action_items[5:8]:
            lines.append(f"- {item['action']} ({item['emoji']} {item['manager']})")
        lines.append("")

    # Warnings
    if result["warnings"]:
        lines.append("### Warnings")
        lines.append("")
        lines.append("```")
        for warning in result["warnings"]:
            lines.append(f"❌ NEVER: {warning.replace('⚠️ ', '').replace('Security risk: ', '')}")
        lines.append("```")
        lines.append("")

    # Recommendations
    if result["recommendations"]:
        lines.append("Recommendations:")
        for rec in result["recommendations"]:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("</final_summary>")
    lines.append("")

    # === END: Repeat critical issues (recency bias - bookending) ===
    all_critical = result.get("critical_issues", [])
    all_warnings = result.get("warnings", [])
    if all_critical or all_warnings:
        lines.append("<critical_reminder>")
        lines.append("⚠️ REMINDER - Must resolve before proceeding:")
        for issue in all_critical:
            lines.append(f"  🚫 {issue}")
        for warning in all_warnings[:2]:
            lines.append(f"  ⚠️ {warning}")
        lines.append("</critical_reminder>")
        lines.append("")

    # Compact instruction (at end for recency)
    lines.append("<output_format>")
    lines.append("Format: Meeting conversation → Status table → Action items → Warnings")
    lines.append("Tone: Professional, specific, actionable")
    lines.append("</output_format>")

    return "\n".join(lines)


def _generate_conversation(result: Dict) -> List[str]:
    """Converts manager feedback into conversation format."""
    lines = []

    active_managers = result["active_managers"]
    feedbacks = result["feedback"]
    action_items = result.get("action_items", [])
    topics = result["context_analysis"].get("detected_topics", ["feature"])

    for i, m in enumerate(active_managers):
        feedback = feedbacks[m]
        emoji = feedback["emoji"]
        role = m

        if feedback.get("opinions"):
            opinion = feedback["opinions"][0]
            lines.append(f"**{emoji} {role}**: {opinion}")
            lines.append("")
        elif feedback["questions"]:
            q = feedback["questions"][0]
            lines.append(f"**{emoji} {role}**: {q}")
            lines.append("")

        if feedback["warnings"]:
            for w in feedback["warnings"]:
                lines.append(f"**{emoji} {role}**: 🚨 {w}")
                lines.append("")

        if feedback["concerns"]:
            c = feedback["concerns"][0]
            lines.append(f"**{emoji} {role}**: {c}")
            lines.append("")

    # PM dynamic wrap-up
    if "PM" in active_managers:
        summary_parts = []

        all_warnings = []
        for m in active_managers:
            all_warnings.extend(feedbacks[m].get("warnings", []))

        if all_warnings:
            summary_parts.append("Resolve security issues first")

        if action_items:
            top_actions = [item["action"].split("(")[0].strip() for item in action_items[:2]]
            summary_parts.extend(top_actions)

        if "auth" in topics:
            summary_parts.append("Finalize auth flow")
        elif "payment" in topics:
            summary_parts.append("Payment testing required")
        elif "api" in topics:
            summary_parts.append("Document API specs")

        summary_parts = summary_parts[:3]

        if summary_parts:
            summary = ", ".join(summary_parts)
            lines.append(f"**👔 PM**: To summarize - 1) {summary}. Let's proceed in order.")
        else:
            lines.append("**👔 PM**: To summarize, let's each review our checklists and proceed.")
        lines.append("")

    return lines


def _get_ai_instruction_template() -> str:
    """Returns the AI restructuring instruction template."""
    return """
---

## 📝 AI Restructuring Instructions

The above data was mechanically generated. Please **restructure it naturally** in the format below:

### Output Format

```
## 🏢 C-Level Meeting Notes

---

**👔 PM**: [Situation explanation - what's the issue]

**🛠️ CTO**: [Technical perspective - reacting to PM]

**🧪 QA**: [Quality perspective - testing/verification issues]

**💰 CFO**: [Cost/financial perspective]

**📢 CMO**: [Marketing perspective]

**🔒 CSO**: [Security perspective] (if applicable)

**🔥 Error**: [Error/risk perspective] (if applicable)

**👔 PM**: [Wrap up with summary]

---

## 📋 Final Summary

### Current Status
| Item | Status | Note |
|------|--------|------|
| ... | ✅/⚠️/🚨 | ... |

### Immediate Tasks (This Week)
| # | Task | Why? |
|---|------|------|
| 1 | ... | ... |

### This Month Tasks
| # | Task | Why? |
|---|------|------|

### On Hold (When conditions met)
| Task | Trigger Condition |
|------|-------------------|

### Warnings
```
❌ NEVER: ...
✅ ALWAYS: ...
```
```

### Writing Rules

1. **Meeting notes in conversational tone**: As if managers are exchanging opinions
2. **Be specific**: "Testing needed" → "Test activate_license_cli() in license.py"
3. **Reflect context**: Connect detected topics with actual situation
4. **Include insights**: Analysis and judgment, not just listing
5. **Make it actionable**: No vague expressions, concrete next steps

### Tone & Manner

- Professional but conversational
- Don't overuse emojis
- Concise, only essentials
- Clear priorities
"""
