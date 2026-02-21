# -*- coding: utf-8 -*-
"""Proactive tools (v2.0): drift_check, auto_remind, pattern_watch

Free: auto PRD check (via hooks)
Pro: drift_check, pattern_watch, auto_remind
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
from mcp.types import TextContent

# v3.0.0: Use runtime entitlements check (supports first project tier)
from ..utils.entitlements import can_use_pro as _entitlements_can_use_pro


def _can_use_pro(project_path: str | None = None) -> bool:
    """Check if Pro features are available (runtime, supports first project)."""
    return _entitlements_can_use_pro(project_path)


async def drift_check(
    path: str,
    silent: bool = False
) -> list[TextContent]:
    """
    Detect context drift - check if current work deviates from original goals.

    Pro feature: Compares recent actions against original task plan.

    Args:
        path: Project root path
        silent: If True, return minimal output (for hooks)

    Returns:
        DRIFT status with score and suggestions, or OK if aligned
    """
    project_path = Path(path)

    # Pro check
    if not _can_use_pro(str(project_path)):
        return [TextContent(
            type="text",
            text="[Pro] drift_check is a Pro feature. Upgrade at https://clouvels.com/"
        )]

    if not project_path.exists():
        if silent:
            return [TextContent(type="text", text="DRIFT:PATH_NOT_FOUND")]
        return [TextContent(type="text", text=f"[ERROR] Path does not exist: {path}")]

    # Load original goals from task_plan.md
    task_plan_path = project_path / ".claude" / "planning" / "task_plan.md"

    if not task_plan_path.exists():
        if silent:
            return [TextContent(type="text", text="OK:NO_PLAN")]
        return [TextContent(
            type="text",
            text="[INFO] No task plan found. Use `init_planning` to set goals first."
        )]

    try:
        task_plan_content = task_plan_path.read_text(encoding="utf-8")
    except Exception as e:
        if silent:
            return [TextContent(type="text", text=f"DRIFT:READ_ERROR:{e}")]
        return [TextContent(type="text", text=f"[ERROR] Failed to read task plan: {e}")]

    # Extract goals
    goals = _extract_goals(task_plan_content)
    current_task = _extract_current_task(task_plan_content)

    if not goals and not current_task:
        if silent:
            return [TextContent(type="text", text="OK:NO_GOALS")]
        return [TextContent(
            type="text",
            text="[INFO] No goals defined in task plan. Add goals to enable drift detection."
        )]

    # Load recent progress from progress.md
    progress_path = project_path / ".claude" / "planning" / "progress.md"
    recent_actions = []

    if progress_path.exists():
        try:
            progress_content = progress_path.read_text(encoding="utf-8")
            recent_actions = _extract_recent_actions(progress_content)
        except Exception:
            pass

    # Calculate drift score
    drift_score, drift_reasons = _calculate_drift_score(
        goals=goals,
        current_task=current_task,
        recent_actions=recent_actions
    )

    # Build response
    if drift_score < 30:
        status = "OK"
        prefix = "[OK]"
        message = "Aligned with goals"
    elif drift_score < 60:
        status = "WARN"
        prefix = "[WARN]"
        message = "Minor drift detected"
    else:
        status = "DRIFT"
        prefix = "[DRIFT]"
        message = "Significant drift from goals"

    if silent:
        return [TextContent(type="text", text=f"{status}:{drift_score}")]

    # Detailed output
    output_lines = [
        f"{prefix} **Drift Check**: {message}",
        "",
        f"**Score**: {drift_score}/100 (lower is better)",
        "",
        "**Original Goal**:",
        f"  {current_task or '(not set)'}",
        "",
        "**Goals**:",
    ]

    for goal in goals[:5]:  # Limit to 5
        output_lines.append(f"  - {goal}")

    if drift_reasons:
        output_lines.append("")
        output_lines.append("**Drift Reasons**:")
        for reason in drift_reasons:
            output_lines.append(f"  - {reason}")

    if drift_score >= 30:
        output_lines.append("")
        output_lines.append("**Suggestion**: Review your goals and refocus on the original task.")

    return [TextContent(type="text", text="\n".join(output_lines))]


async def pattern_watch(
    path: str,
    threshold: int = 3,
    check_only: bool = False
) -> list[TextContent]:
    """
    Watch for repeated error patterns.

    Pro feature: Detects when same error occurs multiple times.

    Args:
        path: Project root path
        threshold: Number of occurrences to trigger alert (default: 3)
        check_only: If True, only check without recording

    Returns:
        Alert if pattern detected, otherwise OK
    """
    project_path = Path(path)

    # Pro check
    if not _can_use_pro(str(project_path)):
        return [TextContent(
            type="text",
            text="[Pro] pattern_watch is a Pro feature. Upgrade at https://clouvels.com/"
        )]

    if not project_path.exists():
        return [TextContent(type="text", text=f"[ERROR] Path does not exist: {path}")]

    # Load error history
    errors_path = project_path / ".claude" / "errors" / "history.md"

    if not errors_path.exists():
        return [TextContent(
            type="text",
            text="[INFO] No error history found. Errors will be tracked automatically."
        )]

    try:
        errors_content = errors_path.read_text(encoding="utf-8")
    except Exception as e:
        return [TextContent(type="text", text=f"[ERROR] Failed to read error history: {e}")]

    # Analyze patterns
    patterns = _analyze_error_patterns(errors_content)

    # Find patterns exceeding threshold
    alerts = []
    for pattern, count in patterns.items():
        if count >= threshold:
            alerts.append(f"- **{pattern}**: {count} occurrences")

    if not alerts:
        return [TextContent(
            type="text",
            text=f"[OK] No repeated error patterns detected (threshold: {threshold})"
        )]

    output_lines = [
        f"[ALERT] **Error Pattern Alert** (threshold: {threshold})",
        "",
        "**Repeated Patterns**:",
    ] + alerts + [
        "",
        "**Suggestion**: Use `error_record` to analyze root cause with 5 Whys.",
    ]

    return [TextContent(type="text", text="\n".join(output_lines))]


async def auto_remind(
    path: str,
    interval: int = 30,
    enabled: bool = True
) -> list[TextContent]:
    """
    Configure automatic progress reminders.

    Pro feature: Reminds to update current.md periodically.

    Args:
        path: Project root path
        interval: Reminder interval in minutes (default: 30)
        enabled: Enable or disable reminders

    Returns:
        Configuration status
    """
    project_path = Path(path)

    # Pro check
    if not _can_use_pro(str(project_path)):
        return [TextContent(
            type="text",
            text="[Pro] auto_remind is a Pro feature. Upgrade at https://clouvels.com/"
        )]

    if not project_path.exists():
        return [TextContent(type="text", text=f"[ERROR] Path does not exist: {path}")]

    # Save config
    config_dir = project_path / ".clouvel"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.yaml"

    config_content = f"""# Clouvel Proactive Config
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

proactive:
  enabled: true

  auto_prd_check:
    enabled: true
    on_block: "stop"  # stop | warn | log

  drift_detection:
    enabled: true
    threshold: 50
    check_interval: 5  # every N tool calls

  error_pattern:
    enabled: true
    threshold: 3

  reminder:
    enabled: {str(enabled).lower()}
    interval: {interval}  # minutes
"""

    try:
        config_path.write_text(config_content, encoding="utf-8")
    except Exception as e:
        return [TextContent(type="text", text=f"[ERROR] Failed to save config: {e}")]

    status = "enabled" if enabled else "disabled"

    return [TextContent(
        type="text",
        text=f"""[OK] **Auto Remind Configured**

**Status**: {status}
**Interval**: {interval} minutes
**Config**: {config_path}

To use with Claude Code hooks, add to `.claude/settings.local.json`:
```json
{{
  "hooks": {{
    "pre_tool_use": [
      {{
        "matcher": "Edit|Write",
        "command": "clouvel can_code --path {path} --silent"
      }}
    ]
  }}
}}
```
"""
    )]


# Helper functions

def _extract_goals(content: str) -> list[str]:
    """Extract goals from task_plan.md content."""
    goals = []
    in_goals_section = False

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("## Goals"):
            in_goals_section = True
            continue

        if in_goals_section:
            if line.startswith("##"):
                break
            if line.startswith("- ["):
                # Extract goal text after checkbox
                goal_text = line.split("]", 1)[-1].strip()
                if goal_text:
                    goals.append(goal_text)

    return goals


def _extract_current_task(content: str) -> Optional[str]:
    """Extract current task from task_plan.md content."""
    in_task_section = False
    task_lines = []

    for line in content.split("\n"):
        if line.startswith("## Current Task"):
            in_task_section = True
            continue

        if in_task_section:
            if line.startswith("##") or line.startswith("---"):
                break
            if line.strip():
                task_lines.append(line.strip())

    return " ".join(task_lines) if task_lines else None


def _extract_recent_actions(content: str) -> list[str]:
    """Extract recent actions from progress.md content."""
    actions = []
    in_progress_section = False

    for line in content.split("\n"):
        line = line.strip()

        if "## In Progress" in line or "## Completed" in line:
            in_progress_section = True
            continue

        if in_progress_section:
            if line.startswith("##"):
                in_progress_section = False
                continue
            if line.startswith("- ["):
                action_text = line.split("]", 1)[-1].strip()
                if action_text:
                    actions.append(action_text)

    return actions[-10:]  # Last 10 actions


def _calculate_drift_score(
    goals: list[str],
    current_task: Optional[str],
    recent_actions: list[str]
) -> tuple[int, list[str]]:
    """
    Calculate drift score based on goals vs recent actions.

    Returns:
        (score 0-100, list of drift reasons)
    """
    if not goals and not current_task:
        return 0, []

    if not recent_actions:
        return 0, ["No recent actions recorded"]

    # Simple keyword matching for now
    # TODO: Use embeddings for semantic similarity

    goal_keywords = set()
    for goal in goals:
        goal_keywords.update(goal.lower().split())

    if current_task:
        goal_keywords.update(current_task.lower().split())

    # Remove common words
    common_words = {"the", "a", "an", "is", "are", "to", "for", "and", "or", "in", "on", "at"}
    goal_keywords -= common_words

    # Check recent actions against goals
    matching_actions = 0
    drift_reasons = []

    for action in recent_actions:
        action_words = set(action.lower().split()) - common_words

        overlap = goal_keywords & action_words
        if overlap:
            matching_actions += 1
        else:
            drift_reasons.append(f"'{action[:50]}...' not related to goals")

    if not recent_actions:
        return 0, []

    # Calculate score (0 = perfect alignment, 100 = complete drift)
    alignment_ratio = matching_actions / len(recent_actions)
    drift_score = int((1 - alignment_ratio) * 100)

    return drift_score, drift_reasons[:3]  # Limit reasons


def _analyze_error_patterns(content: str) -> dict[str, int]:
    """Analyze error history and find patterns."""
    patterns = {}

    # Simple pattern extraction - look for error types
    for line in content.split("\n"):
        line = line.strip().lower()

        # Look for common error patterns
        if "error:" in line or "exception:" in line or "failed:" in line:
            # Extract error type
            for keyword in ["typeerror", "valueerror", "keyerror", "importerror",
                          "attributeerror", "syntaxerror", "nameerror",
                          "connection", "timeout", "permission", "not found"]:
                if keyword in line:
                    patterns[keyword] = patterns.get(keyword, 0) + 1

    return patterns
