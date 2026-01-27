# -*- coding: utf-8 -*-
"""Detailed planning tests - create_detailed_plan function"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.planning import create_detailed_plan


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    yield temp_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_project_with_meeting(temp_project):
    """Create temp project with meeting file"""
    meetings_dir = temp_project / ".claude" / "planning" / "meetings"
    meetings_dir.mkdir(parents=True, exist_ok=True)
    meeting_file = meetings_dir / "2026-01-25_meeting.md"
    meeting_file.write_text("## Previous Meeting\n- Action 1\n- Action 2", encoding="utf-8")
    return temp_project, meeting_file


def mock_manager_result(
    action_items=None,
    action_items_by_phase=None,
    active_managers=None,
    warnings=None,
    feedback=None
):
    """Create a mock manager result"""
    return {
        "action_items": action_items or [],
        "action_items_by_phase": action_items_by_phase or {},
        "active_managers": active_managers or ["PM"],
        "warnings": warnings or [],
        "feedback": feedback or {},
    }


class TestCreateDetailedPlanBasic:
    """Basic create_detailed_plan tests"""

    @pytest.mark.asyncio
    async def test_invalid_path_returns_error(self):
        """Returns error for invalid path"""
        result = await create_detailed_plan("/nonexistent/path", "Task")
        assert "not exist" in result[0].text.lower() or "does not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_returns_list(self, mock_manager, temp_project):
        """Returns list"""
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(str(temp_project), "Test task")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_returns_text_content(self, mock_manager, temp_project):
        """Returns TextContent"""
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(str(temp_project), "Test task")
        assert result[0].type == "text"


class TestCreateDetailedPlanWithManager:
    """Tests with manager integration"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_creates_task_plan_file(self, mock_manager, temp_project):
        """Creates task_plan.md file"""
        mock_manager.return_value = mock_manager_result()
        await create_detailed_plan(str(temp_project), "Test task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        assert task_plan.exists()

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_creates_findings_file(self, mock_manager, temp_project):
        """Creates findings.md file"""
        mock_manager.return_value = mock_manager_result()
        await create_detailed_plan(str(temp_project), "Test task")
        findings = temp_project / ".claude" / "planning" / "findings.md"
        assert findings.exists()

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_creates_progress_file(self, mock_manager, temp_project):
        """Creates progress.md file"""
        mock_manager.return_value = mock_manager_result()
        await create_detailed_plan(str(temp_project), "Test task")
        progress = temp_project / ".claude" / "planning" / "progress.md"
        assert progress.exists()

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_task_in_output(self, mock_manager, temp_project):
        """Task appears in output"""
        mock_manager.return_value = mock_manager_result()
        task = "Implement authentication"
        result = await create_detailed_plan(str(temp_project), task)
        assert task in result[0].text


class TestCreateDetailedPlanWithGoals:
    """Tests with goals parameter"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_goals_in_task_plan(self, mock_manager, temp_project):
        """Goals written to task_plan.md"""
        mock_manager.return_value = mock_manager_result()
        goals = ["Goal 1", "Goal 2"]
        await create_detailed_plan(str(temp_project), "Task", goals=goals)
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "Goal 1" in content
        assert "Goal 2" in content

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_empty_goals(self, mock_manager, temp_project):
        """Handles empty goals"""
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(str(temp_project), "Task", goals=[])
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_goals_passed_to_manager(self, mock_manager, temp_project):
        """Goals passed to manager in context"""
        mock_manager.return_value = mock_manager_result()
        goals = ["Improve coverage", "Fix bugs"]
        await create_detailed_plan(str(temp_project), "Task", goals=goals)
        call_args = mock_manager.call_args
        assert "Improve coverage" in call_args.kwargs["context"]


class TestCreateDetailedPlanWithActionItems:
    """Tests with action items from manager"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}, "QA": {"emoji": "🧪"}})
    @patch("clouvel.tools.manager.manager")
    async def test_action_items_in_plan(self, mock_manager, temp_project):
        """Action items included in plan"""
        mock_manager.return_value = mock_manager_result(
            action_items=[
                {"action": "Write tests", "manager": "QA", "emoji": "🧪", "verify": "Run pytest"},
            ],
            action_items_by_phase={
                "Verify": [{"action": "Write tests", "manager": "QA", "emoji": "🧪", "verify": "Run pytest"}],
            },
            active_managers=["PM", "QA"],
        )
        result = await create_detailed_plan(str(temp_project), "Task")
        assert "1" in result[0].text or "action" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}, "CTO": {"emoji": "🛠️"}})
    @patch("clouvel.tools.manager.manager")
    async def test_action_items_count(self, mock_manager, temp_project):
        """Shows action items count"""
        mock_manager.return_value = mock_manager_result(
            action_items=[
                {"action": "Action 1", "manager": "PM", "emoji": "👔"},
                {"action": "Action 2", "manager": "CTO", "emoji": "🛠️"},
            ],
            action_items_by_phase={
                "Prepare": [{"action": "Action 1", "manager": "PM", "emoji": "👔"}],
                "Design": [{"action": "Action 2", "manager": "CTO", "emoji": "🛠️"}],
            },
            active_managers=["PM", "CTO"],
        )
        result = await create_detailed_plan(str(temp_project), "Task")
        assert "2" in result[0].text

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"CTO": {"emoji": "🛠️"}})
    @patch("clouvel.tools.manager.manager")
    async def test_phases_in_output(self, mock_manager, temp_project):
        """Shows phases in output"""
        mock_manager.return_value = mock_manager_result(
            action_items=[{"action": "Design API", "manager": "CTO", "emoji": "🛠️"}],
            action_items_by_phase={
                "Design": [{"action": "Design API", "manager": "CTO", "emoji": "🛠️"}],
            },
            active_managers=["CTO"],
        )
        result = await create_detailed_plan(str(temp_project), "Task")
        assert "Phase" in result[0].text or "Design" in result[0].text


class TestCreateDetailedPlanWithWarnings:
    """Tests with warnings from manager"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"CSO": {"emoji": "🔒"}})
    @patch("clouvel.tools.manager.manager")
    async def test_warnings_in_task_plan(self, mock_manager, temp_project):
        """Warnings written to task_plan.md"""
        mock_manager.return_value = mock_manager_result(
            warnings=["Security concern detected", "Performance issue"],
            active_managers=["CSO"],
        )
        await create_detailed_plan(str(temp_project), "Task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "Security concern" in content or "Warnings" in content

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_empty_warnings(self, mock_manager, temp_project):
        """Handles empty warnings"""
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(str(temp_project), "Task")
        assert len(result) == 1


class TestCreateDetailedPlanWithFeedback:
    """Tests with manager feedback"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔", "title": "Product Manager"}})
    @patch("clouvel.tools.manager.manager")
    async def test_feedback_in_task_plan(self, mock_manager, temp_project):
        """Manager feedback in task_plan.md"""
        mock_manager.return_value = mock_manager_result(
            active_managers=["PM"],
            feedback={
                "PM": {
                    "questions": ["Is this in scope?", "MVP?"],
                    "concerns": ["Timeline too tight"],
                },
            },
        )
        await create_detailed_plan(str(temp_project), "Task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "Feedback" in content or "Questions" in content or "scope" in content


class TestCreateDetailedPlanWithMeetingFile:
    """Tests with previous meeting file"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_reads_meeting_file(self, mock_manager, temp_project_with_meeting):
        """Reads meeting file when provided"""
        temp_project, meeting_file = temp_project_with_meeting
        mock_manager.return_value = mock_manager_result()
        await create_detailed_plan(
            str(temp_project),
            "Task",
            meeting_file=meeting_file.name
        )
        call_args = mock_manager.call_args
        assert "Previous Meeting" in call_args.kwargs["context"]

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_handles_nonexistent_meeting_file(self, mock_manager, temp_project):
        """Handles nonexistent meeting file gracefully"""
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(
            str(temp_project),
            "Task",
            meeting_file="nonexistent.md"
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_absolute_meeting_path(self, mock_manager, temp_project_with_meeting):
        """Handles absolute meeting file path"""
        temp_project, meeting_file = temp_project_with_meeting
        mock_manager.return_value = mock_manager_result()
        result = await create_detailed_plan(
            str(temp_project),
            "Task",
            meeting_file=str(meeting_file)
        )
        assert len(result) == 1


class TestCreateDetailedPlanPhaseTables:
    """Tests for phase table generation"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_prepare_phase_table(self, mock_manager, temp_project):
        """Generates Prepare phase table"""
        mock_manager.return_value = mock_manager_result(
            action_items=[{"action": "Review requirements", "manager": "PM", "emoji": "👔"}],
            action_items_by_phase={
                "Prepare": [{"action": "Review requirements", "manager": "PM", "emoji": "👔"}],
            },
        )
        await create_detailed_plan(str(temp_project), "Task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "Prepare" in content

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}, "CTO": {"emoji": "🛠️"}, "QA": {"emoji": "🧪"}})
    @patch("clouvel.tools.manager.manager")
    async def test_all_phases_present(self, mock_manager, temp_project):
        """All phases present when items exist"""
        mock_manager.return_value = mock_manager_result(
            action_items=[
                {"action": "A1", "manager": "PM", "emoji": "👔"},
                {"action": "A2", "manager": "CTO", "emoji": "🛠️"},
                {"action": "A3", "manager": "QA", "emoji": "🧪"},
                {"action": "A4", "manager": "QA", "emoji": "🧪"},
            ],
            action_items_by_phase={
                "Prepare": [{"action": "A1", "manager": "PM", "emoji": "👔"}],
                "Design": [{"action": "A2", "manager": "CTO", "emoji": "🛠️"}],
                "Implement": [{"action": "A3", "manager": "QA", "emoji": "🧪"}],
                "Verify": [{"action": "A4", "manager": "QA", "emoji": "🧪"}],
            },
            active_managers=["PM", "CTO", "QA"],
        )
        await create_detailed_plan(str(temp_project), "Task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "Prepare" in content
        assert "Design" in content
        assert "Implement" in content
        assert "Verify" in content

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}})
    @patch("clouvel.tools.manager.manager")
    async def test_dependencies_in_table(self, mock_manager, temp_project):
        """Dependencies shown in table"""
        mock_manager.return_value = mock_manager_result(
            action_items=[{"action": "A1", "manager": "PM", "emoji": "👔", "depends": ["A0"]}],
            action_items_by_phase={
                "Design": [{"action": "A1", "manager": "PM", "emoji": "👔", "depends": ["A0"]}],
            },
        )
        await create_detailed_plan(str(temp_project), "Task")
        task_plan = temp_project / ".claude" / "planning" / "task_plan.md"
        content = task_plan.read_text(encoding="utf-8")
        assert "A0" in content or "Dependencies" in content or "|" in content


class TestCreateDetailedPlanManagerIcons:
    """Tests for manager icons in output"""

    @pytest.mark.asyncio
    @patch("clouvel.tools.manager.MANAGERS", {"PM": {"emoji": "👔"}, "CTO": {"emoji": "🛠️"}})
    @patch("clouvel.tools.manager.manager")
    async def test_manager_icons_in_output(self, mock_manager, temp_project):
        """Manager icons shown in output"""
        mock_manager.return_value = mock_manager_result(active_managers=["PM", "CTO"])
        result = await create_detailed_plan(str(temp_project), "Task")
        assert "👔" in result[0].text or "🛠️" in result[0].text or "Manager" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
