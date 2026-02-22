# -*- coding: utf-8 -*-
"""Context checkpoint: pre-emptive save before context compression.

Saves full working state as a markdown checkpoint file.
Free tier: max 3 checkpoints (oldest auto-deleted).
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

from .context import (
    _extract_summary,
    _find_active_plans,
    _extract_rules,
    _extract_prd_summary,
    _get_recent_modified_files,
)

MAX_FREE_CHECKPOINTS = 1
MAX_PRO_CHECKPOINTS = 50


def _get_git_status_rich(project_path: Path) -> dict:
    """Git status via subprocess (richer than context.py's file-based approach)."""
    result = {
        "is_git": False,
        "branch": None,
        "uncommitted_count": 0,
        "uncommitted_files": [],
        "last_commit": None,
    }

    git_dir = project_path / ".git"
    if not git_dir.exists():
        return result

    result["is_git"] = True

    try:
        # Branch name
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(project_path), timeout=5,
        )
        if branch.returncode == 0:
            result["branch"] = branch.stdout.strip()

        # Uncommitted files
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(project_path), timeout=5,
        )
        if status.returncode == 0:
            files = [line.strip() for line in status.stdout.strip().split("\n") if line.strip()]
            result["uncommitted_count"] = len(files)
            result["uncommitted_files"] = files[:10]  # max 10

        # Last commit
        log = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, cwd=str(project_path), timeout=5,
        )
        if log.returncode == 0:
            result["last_commit"] = log.stdout.strip()

    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return result


def _sanitize_reason(reason: str) -> str:
    """Sanitize reason string for use in filename."""
    if not reason:
        return "checkpoint"
    # Keep only alphanumeric, hyphens, underscores
    sanitized = re.sub(r"[^a-zA-Z0-9가-힣_\-\s]", "", reason)
    sanitized = re.sub(r"\s+", "-", sanitized.strip())
    return sanitized[:40] or "checkpoint"


def _enforce_checkpoint_limit(checkpoints_dir: Path, is_pro: bool = False) -> list[str]:
    """Delete oldest checkpoints if over limit. Returns list of deleted files."""
    limit = MAX_PRO_CHECKPOINTS if is_pro else MAX_FREE_CHECKPOINTS
    deleted = []
    # Get timestamped checkpoint files (exclude latest.md)
    checkpoint_files = sorted(
        [f for f in checkpoints_dir.glob("2*.md") if f.name != "latest.md"],
        key=lambda f: f.name,
    )

    while len(checkpoint_files) >= limit:
        oldest = checkpoint_files.pop(0)
        oldest.unlink()
        deleted.append(oldest.name)

    return deleted


def _build_checkpoint_content(
    *,
    timestamp: str,
    reason: str,
    branch: str,
    working_state: dict,
    plans: list[dict],
    git_status: dict,
    active_files: list[str],
    decisions: list[str],
    notes: str,
    rules: list[str],
    prd_summary: str,
    recent_files: list[str],
    progress_content: str,
) -> str:
    """Build checkpoint markdown content."""
    parts = []

    parts.append("# Context Checkpoint")
    parts.append(f"> **Saved**: {timestamp}")
    if reason:
        parts.append(f"> **Reason**: {reason}")
    if branch:
        parts.append(f"> **Branch**: {branch}")
    parts.append("")

    # Working State
    parts.append("## Working State")
    if working_state.get("next_todos"):
        parts.append(f"**Current Task**: {working_state['next_todos'][0]}")
    if working_state.get("status"):
        parts.append(f"**Status**: {working_state['status']}")
    parts.append("")

    # Active Files
    if active_files:
        parts.append("## Active Files")
        for f in active_files:
            parts.append(f"- `{f}`")
        parts.append("")

    # Session Decisions
    if decisions:
        parts.append("## Session Decisions")
        for i, d in enumerate(decisions, 1):
            parts.append(f"{i}. {d}")
        parts.append("")

    # Important Notes
    if notes:
        parts.append("## Important Notes")
        parts.append(notes)
        parts.append("")

    # Active Plans
    if plans:
        parts.append("## Active Plans")
        for plan in plans:
            status_emoji = {
                "locked": "🔒", "in_progress": "🔄",
                "complete": "✅", "unknown": "❓",
            }.get(plan["status"], "❓")
            step_info = f" (Step {plan['current_step']})" if plan.get("current_step") else ""
            parts.append(f"- {status_emoji} **{plan['task']}**{step_info} — `{plan['file']}`")
        parts.append("")

    # Progress
    if working_state.get("completed") or working_state.get("next_todos"):
        parts.append("## Progress")
        if working_state.get("completed"):
            parts.append("### Completed")
            for item in working_state["completed"][-5:]:
                parts.append(f"- [x] {item}")
        if working_state.get("next_todos"):
            parts.append("### Next")
            for item in working_state["next_todos"][:5]:
                parts.append(f"- [ ] {item}")
        parts.append("")

    # Key Rules (full only)
    if rules:
        parts.append("## Key Rules")
        for rule in rules:
            parts.append(f"- {rule}")
        parts.append("")

    # PRD Summary (full only)
    if prd_summary:
        parts.append("## PRD Summary")
        parts.append(prd_summary)
        parts.append("")

    # Recent Files (full only)
    if recent_files:
        parts.append("## Recent Modified Files")
        for f in recent_files:
            parts.append(f"- `{f}`")
        parts.append("")

    # Git State
    if git_status.get("is_git"):
        parts.append("## Git State")
        parts.append(f"- Branch: `{git_status.get('branch', 'unknown')}`")
        parts.append(f"- Uncommitted: {git_status.get('uncommitted_count', 0)} files")
        if git_status.get("last_commit"):
            parts.append(f"- Last commit: `{git_status['last_commit']}`")
        if git_status.get("uncommitted_files"):
            parts.append("- Changed files:")
            for f in git_status["uncommitted_files"][:5]:
                parts.append(f"  - `{f}`")
        parts.append("")

    return "\n".join(parts)


async def context_save(
    path: str,
    reason: str = "",
    notes: str = "",
    active_files: list[str] = None,
    decisions_this_session: list[str] = None,
    depth: str = "full",
    is_pro: bool = False,
) -> list[TextContent]:
    """Pre-emptive context checkpoint. Saves full working state.

    Args:
        path: Project root path
        reason: Why saving (e.g., "before refactor")
        notes: LLM's notes to preserve
        active_files: Files currently being worked on
        decisions_this_session: Decisions made this session
        depth: "quick" (current.md + git only) or "full" (everything)
        is_pro: Whether user has Pro access (affects slot limit)

    Returns:
        Confirmation with checkpoint summary
    """
    project_path = Path(path) if path else Path.cwd()
    if not project_path.exists():
        return [TextContent(type="text", text=f"# Error\n\nPath not found: `{project_path}`")]

    claude_dir = project_path / ".claude"
    active_files = active_files or []
    decisions = decisions_this_session or []

    # ── Auto-gather: current.md ──
    working_state = {"status": None, "completed": [], "next_todos": [], "blockers": []}
    current_md_path = claude_dir / "status" / "current.md"
    if current_md_path.exists():
        try:
            content = current_md_path.read_text(encoding="utf-8")
            working_state = _extract_summary(content)
        except Exception:
            pass

    # ── Auto-gather: active plans ──
    plans = _find_active_plans(claude_dir)

    # ── Auto-gather: git status (subprocess) ──
    git_status = _get_git_status_rich(project_path)
    branch = git_status.get("branch", "")

    # ── Auto-gather: full-depth extras ──
    rules = []
    prd_summary = ""
    recent_files = []

    if depth == "full":
        # CLAUDE.md rules
        claude_md_path = project_path / "CLAUDE.md"
        if claude_md_path.exists():
            try:
                rules = _extract_rules(claude_md_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # PRD summary
        for prd_path in [project_path / "docs" / "PRD.md", project_path / "PRD.md"]:
            if prd_path.exists():
                try:
                    prd_summary = _extract_prd_summary(prd_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
                break

        # Recent modified files
        recent_files = _get_recent_modified_files(project_path, limit=5)

    # ── Progress.md content ──
    progress_content = ""
    progress_path = claude_dir / "status" / "progress.md"
    if progress_path.exists():
        try:
            progress_content = progress_path.read_text(encoding="utf-8")
        except Exception:
            pass

    # ── Build checkpoint content ──
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
    file_timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    safe_reason = _sanitize_reason(reason)

    checkpoint_content = _build_checkpoint_content(
        timestamp=timestamp,
        reason=reason,
        branch=branch,
        working_state=working_state,
        plans=plans,
        git_status=git_status,
        active_files=active_files,
        decisions=decisions,
        notes=notes,
        rules=rules,
        prd_summary=prd_summary,
        recent_files=recent_files,
        progress_content=progress_content,
    )

    # ── Write checkpoint file ──
    checkpoints_dir = claude_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    # Enforce limit (delete oldest before writing new)
    deleted = _enforce_checkpoint_limit(checkpoints_dir, is_pro=is_pro)

    # Write timestamped file
    filename = f"{file_timestamp}_{safe_reason}.md"
    checkpoint_file = checkpoints_dir / filename
    checkpoint_file.write_text(checkpoint_content, encoding="utf-8")

    # Copy to latest.md
    latest_file = checkpoints_dir / "latest.md"
    latest_file.write_text(checkpoint_content, encoding="utf-8")

    # ── Build response ──
    response_parts = []
    response_parts.append("# Context Saved")
    response_parts.append(f"\n> **File**: `.claude/checkpoints/{filename}`")
    response_parts.append(f"> **Depth**: {depth}")
    response_parts.append(f"> **Time**: {timestamp}")
    if reason:
        response_parts.append(f"> **Reason**: {reason}")

    response_parts.append("\n## Captured")
    response_parts.append(f"- Working state: {'yes' if working_state.get('status') or working_state.get('next_todos') else 'basic'}")
    response_parts.append(f"- Active plans: {len(plans)}")
    response_parts.append(f"- Git branch: `{branch or 'N/A'}`")
    response_parts.append(f"- Uncommitted: {git_status.get('uncommitted_count', 0)} files")
    response_parts.append(f"- Active files: {len(active_files)}")
    response_parts.append(f"- Decisions: {len(decisions)}")
    if notes:
        response_parts.append(f"- Notes: included ({len(notes)} chars)")
    if depth == "full":
        response_parts.append(f"- Rules: {len(rules)}")
        response_parts.append(f"- PRD summary: {'yes' if prd_summary else 'no'}")
        response_parts.append(f"- Recent files: {len(recent_files)}")

    if deleted:
        limit = MAX_PRO_CHECKPOINTS if is_pro else MAX_FREE_CHECKPOINTS
        response_parts.append(f"\n**Rotated**: {len(deleted)} old checkpoint(s) removed (max {limit})")

    if not is_pro:
        response_parts.append(
            f"\n**Free plan**: {MAX_FREE_CHECKPOINTS} checkpoint slot(s). "
            f"New saves overwrite older ones.\n"
            f"Pro: {MAX_PRO_CHECKPOINTS} slots + timeline view "
            f"→ `license_status(action=\"trial\")`"
        )

    response_parts.append(f"\n**Recover with**: `context_load(path=\"{path}\")`")

    return [TextContent(type="text", text="\n".join(response_parts))]


async def context_load(
    path: str,
    checkpoint: str = "latest",
) -> list[TextContent]:
    """Load context from checkpoint after compression/new session.

    Args:
        path: Project root path
        checkpoint: "latest" or specific filename

    Returns:
        Checkpoint content for context recovery
    """
    project_path = Path(path) if path else Path.cwd()
    if not project_path.exists():
        return [TextContent(type="text", text=f"# Error\n\nPath not found: `{project_path}`")]

    checkpoints_dir = project_path / ".claude" / "checkpoints"

    if not checkpoints_dir.exists():
        # Fallback: try reading current.md directly
        return _fallback_load(project_path)

    # Determine which file to load
    if checkpoint == "latest":
        target = checkpoints_dir / "latest.md"
    else:
        target = checkpoints_dir / checkpoint
        if not target.exists():
            # Try with .md extension
            target = checkpoints_dir / f"{checkpoint}.md"

    if not target.exists():
        # List available checkpoints
        available = sorted(
            [f.name for f in checkpoints_dir.glob("2*.md")],
            reverse=True,
        )
        if available:
            listing = "\n".join(f"- `{f}`" for f in available)
            return [TextContent(
                type="text",
                text=f"# Checkpoint Not Found\n\n`{checkpoint}` not found.\n\n## Available\n{listing}",
            )]
        return _fallback_load(project_path)

    # Read and return
    content = target.read_text(encoding="utf-8")

    header = f"> Loaded from: `{target.name}`\n> Use this context to resume work.\n\n"
    return [TextContent(type="text", text=header + content)]


def _fallback_load(project_path: Path) -> list[TextContent]:
    """Fallback when no checkpoints exist: read current.md."""
    current_md = project_path / ".claude" / "status" / "current.md"
    if current_md.exists():
        try:
            content = current_md.read_text(encoding="utf-8")
            summary = _extract_summary(content)

            parts = ["# Context Recovery (fallback)"]
            parts.append("\n> No checkpoints found. Loaded from `current.md`.")
            parts.append("> Use `context_save` to create checkpoints for better recovery.\n")

            if summary.get("next_todos"):
                parts.append("## Next Tasks")
                for item in summary["next_todos"][:5]:
                    parts.append(f"- [ ] {item}")

            if summary.get("completed"):
                parts.append("\n## Recently Completed")
                for item in summary["completed"][-5:]:
                    parts.append(f"- [x] {item}")

            return [TextContent(type="text", text="\n".join(parts))]
        except Exception:
            pass

    return [TextContent(
        type="text",
        text="# No Context Available\n\nNo checkpoints or `current.md` found.\nUse `context_save` to create a checkpoint.",
    )]
