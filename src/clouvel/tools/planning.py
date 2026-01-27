# -*- coding: utf-8 -*-
"""Planning tools (v0.6): init_planning, save_finding, refresh_goals, update_progress"""

from pathlib import Path
from datetime import datetime
from mcp.types import TextContent


async def init_planning(path: str, task: str, goals: list) -> list[TextContent]:
    """Initialize persistent context."""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"Path does not exist: {path}")]

    planning_dir = project_path / ".claude" / "planning"
    planning_dir.mkdir(parents=True, exist_ok=True)

    # Create task_plan.md
    goals_md = "\n".join(f"- [ ] {g}" for g in goals) if goals else "- [ ] (Goals need to be defined)"

    task_plan_content = f"""# Task Plan

> Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Current Task

{task}

---

## Goals

{goals_md}

---

## Approach

(Write plan before starting work)

---

## Constraints

- Work only within scope specified in PRD
- No deployment without tests

---

> Use `refresh_goals` tool to remind yourself of current goals.
"""

    # Create findings.md
    findings_content = f"""# Findings

> Investigation results record
> Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 2-Action Rule

> Record here after every 2 view/browser actions!

---

(No records yet)
"""

    # Create progress.md
    progress_content = f"""# Progress

> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Completed

*(None yet)*

---

## In Progress

*(None)*

---

## Blockers

*(None)*

---

## Next

*(To be decided)*

---

> Update with `update_progress` tool
"""

    # Create files
    (planning_dir / "task_plan.md").write_text(task_plan_content, encoding='utf-8')
    (planning_dir / "findings.md").write_text(findings_content, encoding='utf-8')
    (planning_dir / "progress.md").write_text(progress_content, encoding='utf-8')

    return [TextContent(type="text", text=f"""# Persistent Context Initialized

## Created Files

| File | Purpose |
|------|---------|
| `task_plan.md` | Task plan + goals |
| `findings.md` | Investigation results |
| `progress.md` | Progress tracking |

## Path
`{planning_dir}`

## Next Steps

1. Check goals: `refresh_goals`
2. Record findings: `save_finding`
3. Update progress: `update_progress`

**Don't lose sight of your goals during long sessions!**
""")]


async def save_finding(path: str, topic: str, question: str, findings: str, source: str, conclusion: str) -> list[TextContent]:
    """Save investigation results."""
    project_path = Path(path)
    findings_file = project_path / ".claude" / "planning" / "findings.md"

    if not findings_file.exists():
        return [TextContent(type="text", text="findings.md not found. Initialize with `init_planning` tool first.")]

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    finding_entry = f"""
---

## [{timestamp}] {topic}

### Question
{question if question else '(Not specified)'}

### Findings
{findings}

### Source
{source if source else '(None)'}

### Conclusion
{conclusion if conclusion else '(Further investigation needed)'}

"""

    existing = findings_file.read_text(encoding='utf-8')
    findings_file.write_text(existing + finding_entry, encoding='utf-8')

    return [TextContent(type="text", text=f"""# Finding Saved

## Summary

| Field | Content |
|-------|---------|
| Topic | {topic} |
| Question | {question or 'None'} |
| Source | {source or 'None'} |

## Saved Location
`{findings_file}`

---

**2-Action Rule followed!**
""")]


async def refresh_goals(path: str) -> list[TextContent]:
    """Remind goals."""
    project_path = Path(path)
    task_plan_file = project_path / ".claude" / "planning" / "task_plan.md"
    progress_file = project_path / ".claude" / "planning" / "progress.md"

    if not task_plan_file.exists():
        return [TextContent(type="text", text="task_plan.md not found. Initialize with `init_planning` tool first.")]

    task_plan = task_plan_file.read_text(encoding='utf-8')
    progress = progress_file.read_text(encoding='utf-8') if progress_file.exists() else "(None)"

    # Extract goals
    goals = []
    in_goals_section = False
    for line in task_plan.split("\n"):
        if "## Goals" in line:
            in_goals_section = True
        elif line.startswith("## "):
            in_goals_section = False
        elif in_goals_section and line.strip().startswith("- "):
            goals.append(line.strip())

    goals_md = "\n".join(goals) if goals else "*(No goals)*"

    return [TextContent(type="text", text=f"""# Goal Reminder

## Current Task

(See task_plan.md)

## Goals

{goals_md}

---

## Current Progress

{progress[:500]}{'...' if len(progress) > 500 else ''}

---

## Next Actions

1. Select one of the goals above
2. Focus on that goal
3. Record with `update_progress` when complete

**"What was I doing?" → Check the goals above!**
""")]


async def update_progress(path: str, completed: list, in_progress: str, blockers: list, next_item: str) -> list[TextContent]:
    """Update progress."""
    project_path = Path(path)
    progress_file = project_path / ".claude" / "planning" / "progress.md"

    if not progress_file.exists():
        return [TextContent(type="text", text="progress.md not found. Initialize with `init_planning` tool first.")]

    existing = progress_file.read_text(encoding='utf-8')

    # Parse existing completed items
    existing_completed = []
    in_completed_section = False

    for line in existing.split("\n"):
        if "## Completed" in line:
            in_completed_section = True
        elif line.startswith("## "):
            in_completed_section = False
        elif in_completed_section and line.strip().startswith("- "):
            item = line.strip()[2:]
            if item and item != "*(None yet)*":
                existing_completed.append(item)

    # Add new completed items
    all_completed = existing_completed + list(completed)
    completed_md = "\n".join(f"- {c}" for c in all_completed) if all_completed else "*(None yet)*"
    blockers_md = "\n".join(f"- {b}" for b in blockers) if blockers else "*(None)*"

    # Create new progress.md
    new_progress = f"""# Progress

> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Completed

{completed_md}

---

## In Progress

{f"- {in_progress}" if in_progress else "*(None)*"}

---

## Blockers

{blockers_md}

---

## Next

{next_item if next_item else "*(To be decided)*"}

---

> Update with `update_progress` tool
"""

    progress_file.write_text(new_progress, encoding='utf-8')

    return [TextContent(type="text", text=f"""# Progress Updated

## Summary

| Field | Count/Content |
|-------|---------------|
| Completed | {len(all_completed)} |
| In Progress | {in_progress if in_progress else 'None'} |
| Blockers | {len(blockers)} |
| Next | {next_item if next_item else 'TBD'} |

## Saved Location
`{progress_file}`

---

**Progress recorded!**
""")]


async def create_detailed_plan(
    path: str,
    task: str,
    goals: list = None,
    auto_manager_feedback: bool = True,
    meeting_file: str = None
) -> list[TextContent]:
    """Generate detailed execution plan.

    Calls manager tool to collect action items from each manager,
    and generates a step-by-step plan sorted by dependencies.

    Args:
        path: Project root path
        task: Task to perform
        goals: List of goals to achieve
        auto_manager_feedback: Whether to auto-call manager feedback
        meeting_file: Previous meeting notes file path (if exists, use as basis for plan)

    Returns:
        TextContent containing detailed plan
    """
    from .manager import manager, MANAGERS

    project_path = Path(path)
    if not project_path.exists():
        return [TextContent(type="text", text=f"Path does not exist: {path}")]

    planning_dir = project_path / ".claude" / "planning"
    planning_dir.mkdir(parents=True, exist_ok=True)

    # Read meeting notes file if exists and use as context
    meeting_context = None
    if meeting_file:
        meeting_path = Path(meeting_file)
        if not meeting_path.is_absolute():
            # If relative path, look in planning/meetings folder
            meeting_path = planning_dir / "meetings" / meeting_file
        if meeting_path.exists():
            try:
                meeting_context = meeting_path.read_text(encoding='utf-8')
            except Exception:
                pass

    # Collect manager feedback
    context = f"Task: {task}"
    if goals:
        context += f"\nGoals: {', '.join(goals)}"

    # Add meeting context if exists
    if meeting_context:
        context += f"\n\n## Previous Meeting Results\n\n{meeting_context}"

    manager_result = manager(context=context, mode="auto", include_checklist=True)

    # Extract action items
    action_items = manager_result.get("action_items", [])
    action_items_by_phase = manager_result.get("action_items_by_phase", {})
    active_managers = manager_result.get("active_managers", [])
    warnings = manager_result.get("warnings", [])

    # Goals markdown
    goals_md = "\n".join(f"- [ ] {g}" for g in goals) if goals else "- [ ] (Goals need to be defined)"

    # Create phase tables
    phase_tables = []
    global_idx = 1

    for phase in ["Prepare", "Design", "Implement", "Verify"]:
        items = action_items_by_phase.get(phase, [])
        if items:
            table_lines = [f"### Phase: {phase}"]
            table_lines.append("")
            table_lines.append("| # | Action | Owner | Dependencies | Completion Criteria | Status |")
            table_lines.append("|---|--------|-------|--------------|---------------------|--------|")

            for item in items:
                deps = ", ".join(item.get("depends", [])) if item.get("depends") else "-"
                table_lines.append(
                    f"| {global_idx} | {item['action']} | {item.get('emoji', '')} {item['manager']} | {deps} | {item.get('verify', '')} | [ ] |"
                )
                global_idx += 1

            table_lines.append("")
            phase_tables.append("\n".join(table_lines))

    phases_md = "\n".join(phase_tables) if phase_tables else "(No action items)"

    # Warnings markdown
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "(None)"

    # Manager feedback summary
    feedback_summary = []
    for mgr_key in active_managers:
        mgr_info = MANAGERS.get(mgr_key, {})
        feedback = manager_result.get("feedback", {}).get(mgr_key, {})
        questions = feedback.get("questions", [])[:2]
        concerns = feedback.get("concerns", [])

        if questions or concerns:
            lines = [f"#### {mgr_info.get('emoji', '')} {mgr_info.get('title', mgr_key)}"]
            if questions:
                lines.append("**Questions:**")
                for q in questions:
                    lines.append(f"  - {q}")
            if concerns:
                lines.append("**Concerns:**")
                for c in concerns:
                    lines.append(f"  - {c}")
            lines.append("")
            feedback_summary.append("\n".join(lines))

    feedback_md = "\n".join(feedback_summary) if feedback_summary else "(None)"

    # Create task_plan.md (with detailed plan)
    task_plan_content = f"""# Task Plan

> Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> Tool: create_detailed_plan (v1.3)

---

## Current Task

{task}

---

## Goals

{goals_md}

---

## Detailed Execution Plan

{phases_md}

---

## Verification Points

- [ ] Prepare phase complete → Design phase can start
- [ ] Design phase complete → Implement phase can start
- [ ] Implement phase complete → Verify phase can start
- [ ] All complete → Final verification with `ship` tool

---

## Warnings

{warnings_md}

---

## Manager Feedback Summary

{feedback_md}

---

## Constraints

- Work only within scope specified in PRD
- No deployment without tests

---

> Update progress with `update_progress` tool
"""

    # Create findings.md
    findings_content = f"""# Findings

> Investigation results record
> Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 2-Action Rule

> Record here after every 2 view/browser actions!

---

(No records yet)
"""

    # Create progress.md
    progress_content = f"""# Progress

> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Completed

*(None yet)*

---

## In Progress

*(None)*

---

## Blockers

*(None)*

---

## Next

*(To be decided)*

---

> Update with `update_progress` tool
"""

    # Save files
    (planning_dir / "task_plan.md").write_text(task_plan_content, encoding='utf-8')
    (planning_dir / "findings.md").write_text(findings_content, encoding='utf-8')
    (planning_dir / "progress.md").write_text(progress_content, encoding='utf-8')

    # Active manager icons
    manager_icons = " ".join([MANAGERS[m]["emoji"] for m in active_managers])

    return [TextContent(type="text", text=f"""# Detailed Execution Plan Generated

## Task
{task}

## Active Managers
{manager_icons}

## Generated Plan
Total **{len(action_items)}** action items across **{len([p for p in action_items_by_phase.values() if p])} Phases**

| Phase | Actions |
|-------|---------|
| Prepare | {len(action_items_by_phase.get('Prepare', []))} |
| Design | {len(action_items_by_phase.get('Design', []))} |
| Implement | {len(action_items_by_phase.get('Implement', []))} |
| Verify | {len(action_items_by_phase.get('Verify', []))} |

## Path
`{planning_dir}/task_plan.md`

## Next Steps

1. Review `task_plan.md`
2. Start from Phase 1 (Prepare) in order
3. Call `update_progress` when each phase completes
4. Verify with `ship` tool when all complete

**Start your work with a detailed plan!**

---

💎 **Pro**: `ship` auto-generates PASS evidence & completion report → https://polar.sh/clouvel
""")]
