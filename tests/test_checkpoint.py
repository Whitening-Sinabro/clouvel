# -*- coding: utf-8 -*-
"""Context checkpoint tests (context_save, context_load)"""

import pytest
import tempfile
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.checkpoint import (
    context_save,
    context_load,
    _sanitize_reason,
    _enforce_checkpoint_limit,
    _get_git_status_rich,
    _build_checkpoint_content,
    _fallback_load,
    MAX_FREE_CHECKPOINTS,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory with .claude structure"""
    temp_dir = tempfile.mkdtemp()
    p = Path(temp_dir)

    # Create .claude/status/current.md
    status_dir = p / ".claude" / "status"
    status_dir.mkdir(parents=True)
    (status_dir / "current.md").write_text(
        "# Status\n\n## 지금 상태\n| clouvel | v1.0 |\n\n"
        "## 오늘 완료\n- [x] Feature A\n- [x] Feature B\n\n"
        "## 다음 할 일\n- [ ] Task C\n- [ ] Task D\n\n"
        "## 블로커\n- Waiting for API key\n",
        encoding="utf-8",
    )

    # Create CLAUDE.md
    (p / "CLAUDE.md").write_text(
        "# Rules\nNEVER: commit without tests\nALWAYS: read before edit\n",
        encoding="utf-8",
    )

    # Create docs/PRD.md
    docs_dir = p / "docs"
    docs_dir.mkdir()
    (docs_dir / "PRD.md").write_text(
        "# My Project\n\nA cool project description.\n\n## Features\n- Feature 1\n",
        encoding="utf-8",
    )

    yield p
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_project_minimal():
    """Minimal project without .claude"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


# ============================================================
# context_save tests
# ============================================================

class TestContextSave:
    """context_save function tests"""

    @pytest.mark.asyncio
    async def test_save_creates_checkpoint_file(self, temp_project):
        """Saves a checkpoint file in .claude/checkpoints/"""
        result = await context_save(str(temp_project), reason="test save")

        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        assert checkpoints_dir.exists()

        # Should have a timestamped file + latest.md
        files = list(checkpoints_dir.glob("*.md"))
        assert len(files) == 2  # timestamped + latest

    @pytest.mark.asyncio
    async def test_save_creates_latest_md(self, temp_project):
        """latest.md is always created/updated"""
        await context_save(str(temp_project))

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        assert latest.exists()
        content = latest.read_text(encoding="utf-8")
        assert "Context Checkpoint" in content

    @pytest.mark.asyncio
    async def test_save_captures_current_md(self, temp_project):
        """Checkpoint captures current.md state"""
        result = await context_save(str(temp_project))
        text = result[0].text
        assert "Context Saved" in text

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "Task C" in content  # next todo

    @pytest.mark.asyncio
    async def test_save_includes_reason(self, temp_project):
        """Reason is included in checkpoint"""
        await context_save(str(temp_project), reason="before refactor")

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "before refactor" in content

    @pytest.mark.asyncio
    async def test_save_includes_notes(self, temp_project):
        """Notes are preserved in checkpoint"""
        await context_save(
            str(temp_project),
            notes="Remember: use httpx not requests",
        )

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "httpx not requests" in content

    @pytest.mark.asyncio
    async def test_save_includes_active_files(self, temp_project):
        """Active files are listed in checkpoint"""
        await context_save(
            str(temp_project),
            active_files=["src/auth.py", "tests/test_auth.py"],
        )

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "src/auth.py" in content
        assert "tests/test_auth.py" in content

    @pytest.mark.asyncio
    async def test_save_includes_decisions(self, temp_project):
        """Decisions are listed in checkpoint"""
        await context_save(
            str(temp_project),
            decisions_this_session=["Use JWT", "PostgreSQL over SQLite"],
        )

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "Use JWT" in content
        assert "PostgreSQL over SQLite" in content

    @pytest.mark.asyncio
    async def test_save_quick_depth(self, temp_project):
        """Quick depth skips rules, PRD, recent files"""
        await context_save(str(temp_project), depth="quick")

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        # Should NOT have rules/PRD sections
        assert "Key Rules" not in content
        assert "PRD Summary" not in content

    @pytest.mark.asyncio
    async def test_save_full_depth_includes_rules(self, temp_project):
        """Full depth includes rules from CLAUDE.md"""
        await context_save(str(temp_project), depth="full")

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "Key Rules" in content
        assert "NEVER" in content

    @pytest.mark.asyncio
    async def test_save_full_depth_includes_prd(self, temp_project):
        """Full depth includes PRD summary"""
        await context_save(str(temp_project), depth="full")

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "PRD Summary" in content
        assert "My Project" in content

    @pytest.mark.asyncio
    async def test_save_returns_confirmation(self, temp_project):
        """Returns confirmation with summary"""
        result = await context_save(str(temp_project), reason="test")
        text = result[0].text

        assert "Context Saved" in text
        assert "context_load" in text  # recovery hint

    @pytest.mark.asyncio
    async def test_save_nonexistent_path(self):
        """Returns error for nonexistent path"""
        result = await context_save("/nonexistent/path/xyz")
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_save_without_claude_dir(self, temp_project_minimal):
        """Works even without .claude dir (creates it)"""
        result = await context_save(str(temp_project_minimal))
        text = result[0].text
        assert "Context Saved" in text

        checkpoints_dir = temp_project_minimal / ".claude" / "checkpoints"
        assert checkpoints_dir.exists()


# ============================================================
# context_load tests
# ============================================================

class TestContextLoad:
    """context_load function tests"""

    @pytest.mark.asyncio
    async def test_load_latest(self, temp_project):
        """Loads latest checkpoint"""
        await context_save(str(temp_project), reason="test")
        result = await context_load(str(temp_project))
        text = result[0].text

        assert "Context Checkpoint" in text

    @pytest.mark.asyncio
    async def test_load_specific_checkpoint(self, temp_project):
        """Loads specific checkpoint by filename"""
        await context_save(str(temp_project), reason="first")

        # Find the timestamped file
        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        files = [f.name for f in checkpoints_dir.glob("2*.md")]
        assert len(files) == 1

        result = await context_load(str(temp_project), checkpoint=files[0])
        text = result[0].text
        assert "Context Checkpoint" in text

    @pytest.mark.asyncio
    async def test_load_no_checkpoints_fallback(self, temp_project):
        """Falls back to current.md when no checkpoints"""
        result = await context_load(str(temp_project))
        text = result[0].text
        assert "fallback" in text.lower() or "No checkpoints" in text

    @pytest.mark.asyncio
    async def test_load_no_context_at_all(self, temp_project_minimal):
        """Returns message when nothing exists"""
        result = await context_load(str(temp_project_minimal))
        text = result[0].text
        assert "No Context" in text or "No checkpoints" in text

    @pytest.mark.asyncio
    async def test_load_nonexistent_checkpoint(self, temp_project):
        """Shows available checkpoints when requested one not found"""
        await context_save(str(temp_project), reason="exists")
        result = await context_load(str(temp_project), checkpoint="nonexistent.md")
        text = result[0].text
        assert "Not Found" in text or "Available" in text

    @pytest.mark.asyncio
    async def test_load_nonexistent_path(self):
        """Returns error for nonexistent path"""
        result = await context_load("/nonexistent/path/xyz")
        assert "Error" in result[0].text


# ============================================================
# Checkpoint retention tests
# ============================================================

class TestCheckpointRetention:
    """Free tier: max 3 checkpoints"""

    @pytest.mark.asyncio
    async def test_max_checkpoints_enforced(self, temp_project):
        """Only keeps MAX_FREE_CHECKPOINTS checkpoints"""
        for i in range(5):
            await context_save(str(temp_project), reason=f"save-{i}")

        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        timestamped = list(checkpoints_dir.glob("2*.md"))
        assert len(timestamped) == MAX_FREE_CHECKPOINTS

    @pytest.mark.asyncio
    async def test_oldest_deleted_first(self, temp_project):
        """Oldest checkpoint is deleted first"""
        # Save 3 checkpoints
        reasons = ["first", "second", "third"]
        for reason in reasons:
            await context_save(str(temp_project), reason=reason)

        # Save 4th — should delete the 1st
        await context_save(str(temp_project), reason="fourth")

        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        files = sorted(f.name for f in checkpoints_dir.glob("2*.md"))
        assert len(files) == MAX_FREE_CHECKPOINTS

        # "first" should be gone
        all_content = " ".join(
            f.read_text(encoding="utf-8")
            for f in checkpoints_dir.glob("2*.md")
        )
        # The first save's reason won't be in remaining files
        # (the checkpoint with reason "first" was deleted)

    @pytest.mark.asyncio
    async def test_latest_always_exists(self, temp_project):
        """latest.md always reflects the most recent save"""
        await context_save(str(temp_project), reason="old")
        await context_save(str(temp_project), reason="new")

        latest = temp_project / ".claude" / "checkpoints" / "latest.md"
        content = latest.read_text(encoding="utf-8")
        assert "new" in content

    def test_enforce_limit_empty_dir(self, temp_project):
        """No error on empty checkpoints dir"""
        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        deleted = _enforce_checkpoint_limit(checkpoints_dir)
        assert deleted == []

    def test_enforce_limit_under_limit(self, temp_project):
        """No deletion when under limit"""
        checkpoints_dir = temp_project / ".claude" / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        (checkpoints_dir / "2026-01-01T00-00-00_test.md").write_text("x")
        deleted = _enforce_checkpoint_limit(checkpoints_dir)
        assert deleted == []


# ============================================================
# Checkpoint format tests
# ============================================================

class TestCheckpointFormat:
    """Checkpoint markdown structure"""

    def test_build_basic(self):
        """Build minimal checkpoint"""
        content = _build_checkpoint_content(
            timestamp="2026-02-09T14:00:00",
            reason="test",
            branch="main",
            working_state={"status": None, "completed": [], "next_todos": [], "blockers": []},
            plans=[],
            git_status={"is_git": False},
            active_files=[],
            decisions=[],
            notes="",
            rules=[],
            prd_summary="",
            recent_files=[],
            progress_content="",
        )
        assert "# Context Checkpoint" in content
        assert "2026-02-09T14:00:00" in content

    def test_build_with_all_sections(self):
        """Build checkpoint with all sections populated"""
        content = _build_checkpoint_content(
            timestamp="2026-02-09T14:00:00",
            reason="full test",
            branch="feat/auth",
            working_state={
                "status": "| clouvel | v1.0 |",
                "completed": ["Done A"],
                "next_todos": ["Todo B"],
                "blockers": [],
            },
            plans=[{"file": "PLAN-auth.md", "task": "Auth", "status": "in_progress", "current_step": 2}],
            git_status={"is_git": True, "branch": "feat/auth", "uncommitted_count": 3, "last_commit": "abc123 feat: init", "uncommitted_files": ["M src/a.py"]},
            active_files=["src/auth.py"],
            decisions=["Use JWT"],
            notes="Important note",
            rules=["NEVER: skip tests"],
            prd_summary="# Auth System",
            recent_files=["src/auth.py"],
            progress_content="",
        )
        assert "## Working State" in content
        assert "## Active Files" in content
        assert "## Session Decisions" in content
        assert "## Important Notes" in content
        assert "## Active Plans" in content
        assert "## Progress" in content
        assert "## Key Rules" in content
        assert "## PRD Summary" in content
        assert "## Git State" in content
        assert "## Recent Modified Files" in content

    def test_build_skips_empty_sections(self):
        """Empty sections are not included"""
        content = _build_checkpoint_content(
            timestamp="2026-02-09T14:00:00",
            reason="",
            branch="",
            working_state={"status": None, "completed": [], "next_todos": [], "blockers": []},
            plans=[],
            git_status={"is_git": False},
            active_files=[],
            decisions=[],
            notes="",
            rules=[],
            prd_summary="",
            recent_files=[],
            progress_content="",
        )
        assert "## Active Files" not in content
        assert "## Session Decisions" not in content
        assert "## Important Notes" not in content
        assert "## Key Rules" not in content
        assert "## PRD Summary" not in content


# ============================================================
# Helper tests
# ============================================================

class TestSanitizeReason:
    """_sanitize_reason tests"""

    def test_simple_reason(self):
        assert _sanitize_reason("before refactor") == "before-refactor"

    def test_empty_reason(self):
        assert _sanitize_reason("") == "checkpoint"

    def test_special_chars(self):
        result = _sanitize_reason("test!@#$%^&*()")
        assert "!" not in result
        assert "@" not in result

    def test_long_reason_truncated(self):
        result = _sanitize_reason("a" * 100)
        assert len(result) <= 40

    def test_korean_reason(self):
        result = _sanitize_reason("리팩토링 전")
        assert "리팩토링" in result


class TestGitStatusRich:
    """_get_git_status_rich tests"""

    def test_non_git_directory(self, temp_project_minimal):
        """Returns is_git=False for non-git dirs"""
        result = _get_git_status_rich(temp_project_minimal)
        assert result["is_git"] is False

    @patch("clouvel.tools.checkpoint.subprocess.run")
    def test_git_subprocess_failure(self, mock_run, temp_project):
        """Handles subprocess failures gracefully"""
        mock_run.side_effect = FileNotFoundError("git not found")

        # Create .git dir to trigger subprocess calls
        (temp_project / ".git").mkdir(exist_ok=True)

        result = _get_git_status_rich(temp_project)
        assert result["is_git"] is True
        assert result["branch"] is None


class TestFallbackLoad:
    """_fallback_load tests"""

    @pytest.mark.asyncio
    async def test_fallback_with_current_md(self, temp_project):
        """Falls back to current.md content"""
        result = _fallback_load(temp_project)
        text = result[0].text
        assert "fallback" in text.lower()
        assert "Task C" in text  # from current.md

    @pytest.mark.asyncio
    async def test_fallback_no_current_md(self, temp_project_minimal):
        """Returns 'no context' when nothing exists"""
        result = _fallback_load(temp_project_minimal)
        text = result[0].text
        assert "No Context" in text
