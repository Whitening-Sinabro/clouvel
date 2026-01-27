# -*- coding: utf-8 -*-
"""Planning tools comprehensive tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.planning import (
    init_planning,
    save_finding,
    refresh_goals,
    update_progress,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def initialized_project(temp_project):
    """Project with planning initialized"""
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        init_planning(str(temp_project), "Test task", ["Goal 1", "Goal 2"])
    )
    return temp_project


class TestInitPlanning:
    """init_planning function tests"""

    @pytest.mark.asyncio
    async def test_init_creates_files(self, temp_project):
        """Init creates all planning files"""
        result = await init_planning(str(temp_project), "Test task", ["Goal 1"])

        planning_dir = temp_project / ".claude" / "planning"
        assert planning_dir.exists()
        assert (planning_dir / "task_plan.md").exists()
        assert (planning_dir / "findings.md").exists()
        assert (planning_dir / "progress.md").exists()

    @pytest.mark.asyncio
    async def test_init_with_goals(self, temp_project):
        """Init includes goals in task_plan.md"""
        await init_planning(str(temp_project), "Test", ["Goal A", "Goal B"])

        content = (temp_project / ".claude" / "planning" / "task_plan.md").read_text(encoding="utf-8")
        assert "Goal A" in content
        assert "Goal B" in content

    @pytest.mark.asyncio
    async def test_init_with_task(self, temp_project):
        """Init includes task in task_plan.md"""
        await init_planning(str(temp_project), "Build login page", [])

        content = (temp_project / ".claude" / "planning" / "task_plan.md").read_text(encoding="utf-8")
        assert "Build login page" in content

    @pytest.mark.asyncio
    async def test_init_empty_goals(self, temp_project):
        """Init with empty goals list"""
        await init_planning(str(temp_project), "Task", [])

        content = (temp_project / ".claude" / "planning" / "task_plan.md").read_text(encoding="utf-8")
        assert "Goals need to be defined" in content

    @pytest.mark.asyncio
    async def test_init_nonexistent_path(self):
        """Init fails gracefully with nonexistent path"""
        result = await init_planning("/nonexistent/path/123456", "Task", [])
        assert "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_init_returns_success(self, temp_project):
        """Init returns success message"""
        result = await init_planning(str(temp_project), "Task", ["Goal"])
        assert "Initialized" in result[0].text


class TestSaveFinding:
    """save_finding function tests"""

    @pytest.mark.asyncio
    async def test_save_finding_appends(self, initialized_project):
        """Save finding appends to findings.md"""
        result = await save_finding(
            str(initialized_project),
            "Authentication",
            "How to implement OAuth?",
            "Use OAuth2 library",
            "docs.oauth.io",
            "Implement with library X"
        )

        findings = (initialized_project / ".claude" / "planning" / "findings.md").read_text(encoding="utf-8")
        assert "Authentication" in findings
        assert "OAuth" in findings
        assert "Saved" in result[0].text

    @pytest.mark.asyncio
    async def test_save_finding_no_init(self, temp_project):
        """Save finding fails without init"""
        result = await save_finding(str(temp_project), "Topic", "", "", "", "")
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_save_finding_empty_optional(self, initialized_project):
        """Save finding with empty optional fields"""
        result = await save_finding(
            str(initialized_project),
            "Topic only",
            "",  # no question
            "Found something",
            "",  # no source
            ""   # no conclusion
        )
        assert "Saved" in result[0].text

    @pytest.mark.asyncio
    async def test_save_multiple_findings(self, initialized_project):
        """Save multiple findings"""
        await save_finding(str(initialized_project), "Topic 1", "", "Finding 1", "", "")
        await save_finding(str(initialized_project), "Topic 2", "", "Finding 2", "", "")

        findings = (initialized_project / ".claude" / "planning" / "findings.md").read_text(encoding="utf-8")
        assert "Topic 1" in findings
        assert "Topic 2" in findings


class TestRefreshGoals:
    """refresh_goals function tests"""

    @pytest.mark.asyncio
    async def test_refresh_goals_shows_goals(self, initialized_project):
        """Refresh goals shows current goals"""
        result = await refresh_goals(str(initialized_project))

        assert "Goal 1" in result[0].text or "goal" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_refresh_goals_no_init(self, temp_project):
        """Refresh goals fails without init"""
        result = await refresh_goals(str(temp_project))
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_refresh_goals_extracts_from_plan(self, initialized_project):
        """Refresh goals extracts goals section"""
        result = await refresh_goals(str(initialized_project))
        # Should contain reminder message
        assert "Reminder" in result[0].text or "Goals" in result[0].text


class TestUpdateProgress:
    """update_progress function tests"""

    @pytest.mark.asyncio
    async def test_update_progress_completed(self, initialized_project):
        """Update progress with completed items"""
        result = await update_progress(
            str(initialized_project),
            ["Task 1 done", "Task 2 done"],
            "Working on task 3",
            [],
            "Task 4 next"
        )

        progress = (initialized_project / ".claude" / "planning" / "progress.md").read_text(encoding="utf-8")
        assert "Task 1 done" in progress
        assert "Task 2 done" in progress
        assert "Updated" in result[0].text

    @pytest.mark.asyncio
    async def test_update_progress_in_progress(self, initialized_project):
        """Update progress with in_progress item"""
        await update_progress(
            str(initialized_project),
            [],
            "Currently building feature X",
            [],
            ""
        )

        progress = (initialized_project / ".claude" / "planning" / "progress.md").read_text(encoding="utf-8")
        assert "Currently building feature X" in progress

    @pytest.mark.asyncio
    async def test_update_progress_blockers(self, initialized_project):
        """Update progress with blockers"""
        await update_progress(
            str(initialized_project),
            [],
            "",
            ["Need API access", "Waiting for design"],
            ""
        )

        progress = (initialized_project / ".claude" / "planning" / "progress.md").read_text(encoding="utf-8")
        assert "Need API access" in progress
        assert "Waiting for design" in progress

    @pytest.mark.asyncio
    async def test_update_progress_next(self, initialized_project):
        """Update progress with next item"""
        await update_progress(
            str(initialized_project),
            [],
            "",
            [],
            "Deploy to staging"
        )

        progress = (initialized_project / ".claude" / "planning" / "progress.md").read_text(encoding="utf-8")
        assert "Deploy to staging" in progress

    @pytest.mark.asyncio
    async def test_update_progress_accumulates(self, initialized_project):
        """Update progress accumulates completed items"""
        await update_progress(str(initialized_project), ["Item 1"], "", [], "")
        await update_progress(str(initialized_project), ["Item 2"], "", [], "")

        progress = (initialized_project / ".claude" / "planning" / "progress.md").read_text(encoding="utf-8")
        assert "Item 1" in progress
        assert "Item 2" in progress

    @pytest.mark.asyncio
    async def test_update_progress_no_init(self, temp_project):
        """Update progress fails without init"""
        result = await update_progress(str(temp_project), [], "", [], "")
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_update_progress_empty_all(self, initialized_project):
        """Update progress with all empty"""
        result = await update_progress(
            str(initialized_project),
            [],
            "",
            [],
            ""
        )
        assert "Updated" in result[0].text


class TestPlanningWorkflow:
    """Integration tests for planning workflow"""

    @pytest.mark.asyncio
    async def test_full_planning_workflow(self, temp_project):
        """Test complete planning workflow"""
        # 1. Initialize
        await init_planning(str(temp_project), "Build user auth", ["Login", "Logout", "Register"])

        # 2. Refresh to see goals
        result = await refresh_goals(str(temp_project))
        assert "Login" in result[0].text or "Goals" in result[0].text

        # 3. Record finding
        await save_finding(
            str(temp_project),
            "Auth research",
            "What library to use?",
            "FastAPI Security works well",
            "fastapi.tiangolo.com",
            "Use FastAPI Security"
        )

        # 4. Update progress
        result = await update_progress(
            str(temp_project),
            ["Research done"],
            "Implementing login",
            [],
            "Test login flow"
        )
        assert "Updated" in result[0].text

        # Verify all files exist and have content
        planning_dir = temp_project / ".claude" / "planning"
        assert (planning_dir / "task_plan.md").read_text(encoding="utf-8")
        assert "Auth research" in (planning_dir / "findings.md").read_text(encoding="utf-8")
        assert "Research done" in (planning_dir / "progress.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
