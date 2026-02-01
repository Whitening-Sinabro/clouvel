# Clouvel UI Module
# Rich-based terminal UI with fallback to plain text

import os
from typing import Optional, List, Dict, Any

# Check if Rich UI is disabled via environment variable
# Useful for testing or when plain text output is preferred
_RICH_DISABLED = os.environ.get("CLOUVEL_NO_RICH", "").lower() in ("1", "true", "yes")

# Try to import Rich, fallback to plain text if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.style import Style
    from rich import box
    HAS_RICH = True and not _RICH_DISABLED
except ImportError:
    HAS_RICH = False

# =============================================================================
# Theme Configuration
# =============================================================================

THEME = {
    # Status colors
    "block": "red",
    "warn": "yellow",
    "pass": "green",

    # Manager colors
    "PM": "blue",
    "CTO": "cyan",
    "QA": "green",
    "CSO": "red",
    "CDO": "magenta",
    "CMO": "yellow",
    "CFO": "green",
    "ERROR": "red",

    # Manager emojis
    "PM_emoji": "👔",
    "CTO_emoji": "🛠️",
    "QA_emoji": "🧪",
    "CSO_emoji": "🔒",
    "CDO_emoji": "🎨",
    "CMO_emoji": "📢",
    "CFO_emoji": "💰",
    "ERROR_emoji": "🔥",

    # General
    "title": "bold white",
    "subtitle": "dim",
    "muted": "dim white",
}

# Manager full names
MANAGER_NAMES = {
    "PM": "Product Manager",
    "CTO": "Chief Technology Officer",
    "QA": "Quality Assurance",
    "CSO": "Chief Security Officer",
    "CDO": "Chief Design Officer",
    "CMO": "Chief Marketing Officer",
    "CFO": "Chief Financial Officer",
    "ERROR": "Error Manager",
}

# =============================================================================
# Console Singleton
# =============================================================================

_console: Optional["Console"] = None

def get_console() -> Optional["Console"]:
    """Get or create Rich console instance."""
    global _console
    if HAS_RICH and _console is None:
        _console = Console()
    return _console

# =============================================================================
# can_code Output
# =============================================================================

def render_can_code(
    status: str,  # "BLOCK", "WARN", "PASS"
    title: str,
    found: List[str],
    missing: List[str],
    test_count: int = 0,
    next_action: Optional[str] = None,
    pro_hint: Optional[str] = None,
) -> str:
    """Render can_code output with Rich panels or plain text."""

    if HAS_RICH:
        return _render_can_code_rich(status, title, found, missing, test_count, next_action, pro_hint)
    else:
        return _render_can_code_plain(status, title, found, missing, test_count, next_action, pro_hint)


def _render_can_code_rich(
    status: str,
    title: str,
    found: List[str],
    missing: List[str],
    test_count: int,
    next_action: Optional[str],
    pro_hint: Optional[str],
) -> str:
    """Rich version of can_code output."""
    console = get_console()

    # Determine style based on status
    if status == "BLOCK":
        border_style = THEME["block"]
        status_emoji = "🚫"
        status_text = "BLOCK"
    elif status == "WARN":
        border_style = THEME["warn"]
        status_emoji = "⚠️"
        status_text = "WARN"
    else:  # PASS
        border_style = THEME["pass"]
        status_emoji = "✅"
        status_text = "PASS"

    # Build content
    lines = []

    # Status line
    lines.append(f"{status_emoji}  {status_text} | {title}")
    lines.append("")

    # Found items
    if found:
        lines.append("[dim]Found:[/dim]")
        for item in found:
            lines.append(f"  ✓ {item}")
        lines.append("")

    # Missing items
    if missing:
        lines.append("[dim]Missing:[/dim]")
        for item in missing:
            lines.append(f"  ✗ {item}")
        lines.append("")

    # Test count
    if test_count > 0:
        lines.append(f"[dim]Tests:[/dim] {test_count} files")
        lines.append("")

    # Next action
    if next_action:
        lines.append(f"[bold]Next:[/bold] {next_action}")
        lines.append("")

    # Pro hint
    if pro_hint:
        lines.append(f"[dim]💎 Pro: {pro_hint}[/dim]")

    content = "\n".join(lines)

    # Create panel
    panel = Panel(
        content,
        border_style=border_style,
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # Render to string
    with console.capture() as capture:
        console.print(panel)

    return capture.get()


def _render_can_code_plain(
    status: str,
    title: str,
    found: List[str],
    missing: List[str],
    test_count: int,
    next_action: Optional[str],
    pro_hint: Optional[str],
) -> str:
    """Plain text fallback for can_code output."""
    lines = []

    # Status line
    if status == "BLOCK":
        lines.append(f"🚫 BLOCK | {title}")
    elif status == "WARN":
        lines.append(f"⚠️ WARN | {title}")
    else:
        lines.append(f"✅ PASS | {title}")

    lines.append("")

    # Found/Missing
    if found:
        lines.append(f"Found: {', '.join(found)}")
    if missing:
        lines.append(f"Missing: {', '.join(missing)}")

    if test_count > 0:
        lines.append(f"Tests: {test_count} files")

    if next_action:
        lines.append(f"Next: {next_action}")

    if pro_hint:
        lines.append(f"💎 Pro: {pro_hint}")

    return "\n".join(lines)

# =============================================================================
# Manager Output
# =============================================================================

def render_manager_panel(
    manager: str,  # "PM", "CTO", etc.
    content: List[str],  # List of feedback lines
    status: Optional[str] = None,  # "approved", "warning", "critical"
) -> str:
    """Render a single manager's feedback as a panel."""

    if HAS_RICH:
        return _render_manager_panel_rich(manager, content, status)
    else:
        return _render_manager_panel_plain(manager, content, status)


def _render_manager_panel_rich(
    manager: str,
    content: List[str],
    status: Optional[str],
) -> str:
    """Rich version of manager panel."""
    console = get_console()

    # Get manager info
    color = THEME.get(manager, "white")
    emoji = THEME.get(f"{manager}_emoji", "👤")
    full_name = MANAGER_NAMES.get(manager, manager)

    # Build title
    title = f"{emoji} {manager} ({full_name})"

    # Build content
    content_text = "\n".join(content)

    # Create panel
    panel = Panel(
        content_text,
        title=title,
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1),
    )

    # Render to string
    with console.capture() as capture:
        console.print(panel)

    return capture.get()


def _render_manager_panel_plain(
    manager: str,
    content: List[str],
    status: Optional[str],
) -> str:
    """Plain text fallback for manager panel."""
    emoji = THEME.get(f"{manager}_emoji", "👤")
    full_name = MANAGER_NAMES.get(manager, manager)

    lines = [f"--- {emoji} {manager} ({full_name}) ---"]
    lines.extend(content)
    lines.append("")

    return "\n".join(lines)


def render_manager_meeting(
    title: str,
    status: str,  # "APPROVED", "NEEDS_REVISION", "BLOCKED"
    feedbacks: Dict[str, Dict[str, Any]],  # manager -> {content, warnings, etc.}
    summary: Optional[Dict[str, Any]] = None,
) -> str:
    """Render full manager meeting output."""

    if HAS_RICH:
        return _render_manager_meeting_rich(title, status, feedbacks, summary)
    else:
        return _render_manager_meeting_plain(title, status, feedbacks, summary)


def _render_manager_meeting_rich(
    title: str,
    status: str,
    feedbacks: Dict[str, Dict[str, Any]],
    summary: Optional[Dict[str, Any]],
) -> str:
    """Rich version of manager meeting."""
    console = get_console()
    output_parts = []

    # Header
    if status == "APPROVED":
        status_style = THEME["pass"]
        status_emoji = "✅"
    elif status == "BLOCKED":
        status_style = THEME["block"]
        status_emoji = "🚫"
    else:
        status_style = THEME["warn"]
        status_emoji = "⚠️"

    header = Panel(
        f"[bold]{title}[/bold]\n\nStatus: {status_emoji} {status}",
        title="🏢 Manager Meeting",
        title_align="left",
        border_style=status_style,
        box=box.DOUBLE,
        padding=(1, 2),
    )

    with console.capture() as capture:
        console.print(header)
    output_parts.append(capture.get())

    # Each manager's feedback
    for manager, feedback in feedbacks.items():
        content_lines = []

        # Opinions/main points
        if feedback.get("opinions"):
            for opinion in feedback["opinions"]:
                content_lines.append(f"✓ {opinion}")

        # Warnings
        if feedback.get("warnings"):
            for warning in feedback["warnings"]:
                content_lines.append(f"⚠️ {warning}")

        # Critical issues
        if feedback.get("critical_issues"):
            for issue in feedback["critical_issues"]:
                content_lines.append(f"✗ CRITICAL: {issue}")

        # Questions
        if feedback.get("questions"):
            for q in feedback["questions"][:2]:
                content_lines.append(f"❓ \"{q}\"")

        if content_lines:
            panel_output = _render_manager_panel_rich(manager, content_lines, None)
            output_parts.append(panel_output)

    # Summary table
    if summary:
        table = Table(
            title="Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
        )
        table.add_column("Area", style="cyan")
        table.add_column("Status")
        table.add_column("Note", style="dim")

        for area, info in summary.items():
            status_icon = info.get("status", "✓")
            note = info.get("note", "-")
            table.add_row(area, status_icon, note[:40])

        with console.capture() as capture:
            console.print(table)
        output_parts.append(capture.get())

    return "\n".join(output_parts)


def _render_manager_meeting_plain(
    title: str,
    status: str,
    feedbacks: Dict[str, Dict[str, Any]],
    summary: Optional[Dict[str, Any]],
) -> str:
    """Plain text fallback for manager meeting."""
    lines = []

    # Header
    lines.append(f"🏢 Manager Meeting - {title}")
    lines.append(f"Status: {status}")
    lines.append("---")
    lines.append("")

    # Each manager
    for manager, feedback in feedbacks.items():
        emoji = THEME.get(f"{manager}_emoji", "👤")
        lines.append(f"**{emoji} {manager}**:")

        if feedback.get("opinions"):
            for opinion in feedback["opinions"]:
                lines.append(f"  ✓ {opinion}")
        if feedback.get("warnings"):
            for warning in feedback["warnings"]:
                lines.append(f"  ⚠️ {warning}")
        if feedback.get("questions"):
            for q in feedback["questions"][:2]:
                lines.append(f"  ❓ \"{q}\"")
        lines.append("")

    # Summary
    if summary:
        lines.append("---")
        lines.append("Summary:")
        lines.append("| Area | Status | Note |")
        lines.append("|------|--------|------|")
        for area, info in summary.items():
            status_icon = info.get("status", "✓")
            note = info.get("note", "-")[:40]
            lines.append(f"| {area} | {status_icon} | {note} |")

    return "\n".join(lines)

# =============================================================================
# Ship Output
# =============================================================================

def render_ship_step(
    step: str,  # "lint", "test", "build"
    status: str,  # "running", "pass", "fail", "skip"
    message: Optional[str] = None,
) -> str:
    """Render a single ship step."""

    if status == "running":
        icon = "⏳"
        style = "yellow" if HAS_RICH else ""
    elif status == "pass":
        icon = "✅"
        style = "green" if HAS_RICH else ""
    elif status == "fail":
        icon = "❌"
        style = "red" if HAS_RICH else ""
    else:  # skip
        icon = "⏭️"
        style = "dim" if HAS_RICH else ""

    if HAS_RICH:
        console = get_console()
        text = f"{icon} {step}"
        if message:
            text += f" - {message}"
        with console.capture() as capture:
            console.print(f"[{style}]{text}[/{style}]")
        return capture.get()
    else:
        text = f"{icon} {step}"
        if message:
            text += f" - {message}"
        return text


def render_ship_result(
    passed: bool,
    steps_summary: Dict[str, str],  # step -> status
    evidence_path: Optional[str] = None,
) -> str:
    """Render ship final result."""

    if HAS_RICH:
        return _render_ship_result_rich(passed, steps_summary, evidence_path)
    else:
        return _render_ship_result_plain(passed, steps_summary, evidence_path)


def _render_ship_result_rich(
    passed: bool,
    steps_summary: Dict[str, str],
    evidence_path: Optional[str],
) -> str:
    """Rich version of ship result."""
    console = get_console()

    # Status
    if passed:
        border_style = THEME["pass"]
        title = "✅ Ship PASSED"
    else:
        border_style = THEME["block"]
        title = "❌ Ship FAILED"

    # Build content
    lines = []
    for step, status in steps_summary.items():
        if status == "pass":
            lines.append(f"✅ {step}")
        elif status == "fail":
            lines.append(f"❌ {step}")
        else:
            lines.append(f"⏭️ {step} (skipped)")

    if evidence_path:
        lines.append("")
        lines.append(f"📄 Evidence: {evidence_path}")

    content = "\n".join(lines)

    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style=border_style,
        box=box.ROUNDED,
        padding=(1, 2),
    )

    with console.capture() as capture:
        console.print(panel)

    return capture.get()


def _render_ship_result_plain(
    passed: bool,
    steps_summary: Dict[str, str],
    evidence_path: Optional[str],
) -> str:
    """Plain text fallback for ship result."""
    lines = []

    if passed:
        lines.append("✅ Ship PASSED")
    else:
        lines.append("❌ Ship FAILED")

    lines.append("")

    for step, status in steps_summary.items():
        if status == "pass":
            lines.append(f"  ✅ {step}")
        elif status == "fail":
            lines.append(f"  ❌ {step}")
        else:
            lines.append(f"  ⏭️ {step} (skipped)")

    if evidence_path:
        lines.append("")
        lines.append(f"📄 Evidence: {evidence_path}")

    return "\n".join(lines)

# =============================================================================
# Quick Perspectives Output
# =============================================================================

def render_quick_perspectives(
    context: str,
    perspectives: Dict[str, List[str]],  # manager -> questions
) -> str:
    """Render quick perspectives output."""

    if HAS_RICH:
        return _render_quick_perspectives_rich(context, perspectives)
    else:
        return _render_quick_perspectives_plain(context, perspectives)


def _render_quick_perspectives_rich(
    context: str,
    perspectives: Dict[str, List[str]],
) -> str:
    """Rich version of quick perspectives."""
    console = get_console()
    output_parts = []

    # Header
    header = Panel(
        f"[dim]Before building:[/dim] [bold]{context}[/bold]",
        title="💡 Quick Perspectives",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )

    with console.capture() as capture:
        console.print(header)
    output_parts.append(capture.get())

    # Each manager's questions
    for manager, questions in perspectives.items():
        emoji = THEME.get(f"{manager}_emoji", "👤")
        color = THEME.get(manager, "white")

        content_lines = []
        for q in questions:
            content_lines.append(f"• {q}")

        panel = Panel(
            "\n".join(content_lines),
            title=f"{emoji} {manager}",
            title_align="left",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 1),
        )

        with console.capture() as capture:
            console.print(panel)
        output_parts.append(capture.get())

    return "\n".join(output_parts)


def _render_quick_perspectives_plain(
    context: str,
    perspectives: Dict[str, List[str]],
) -> str:
    """Plain text fallback for quick perspectives."""
    lines = []

    lines.append("💡 Quick Perspectives")
    lines.append(f"Before building: {context}")
    lines.append("")

    for manager, questions in perspectives.items():
        emoji = THEME.get(f"{manager}_emoji", "👤")
        lines.append(f"**{emoji} {manager}**:")
        for q in questions:
            lines.append(f"  • {q}")
        lines.append("")

    return "\n".join(lines)
