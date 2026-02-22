# -*- coding: utf-8 -*-
"""Tests for Proactive MCP tools (v2.0)"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions to test
from src.clouvel.tools.proactive import (
    drift_check,
    pattern_watch,
    auto_remind,
    _extract_goals,
    _extract_current_task,
    _extract_recent_actions,
    _calculate_drift_score,
    _analyze_error_patterns,
)


class TestExtractGoals:
    """Test _extract_goals helper function"""

    def test_extract_simple_goals(self):
        content = """## Goals

- [ ] Implement login feature
- [ ] Add password reset
- [x] Setup project
"""
        goals = _extract_goals(content)
        assert len(goals) == 3
        assert "Implement login feature" in goals
        assert "Add password reset" in goals

    def test_extract_no_goals(self):
        content = """## Other Section

Some content here
"""
        goals = _extract_goals(content)
        assert len(goals) == 0

    def test_extract_goals_stops_at_next_section(self):
        content = """## Goals

- [ ] Goal 1
- [ ] Goal 2

## Approach

This is the approach
"""
        goals = _extract_goals(content)
        assert len(goals) == 2


class TestExtractCurrentTask:
    """Test _extract_current_task helper function"""

    def test_extract_current_task(self):
        content = """## Current Task

Implement user authentication with JWT tokens

---

## Goals
"""
        task = _extract_current_task(content)
        assert task == "Implement user authentication with JWT tokens"

    def test_no_current_task(self):
        content = """## Goals

- [ ] Goal 1
"""
        task = _extract_current_task(content)
        assert task is None


class TestExtractRecentActions:
    """Test _extract_recent_actions helper function"""

    def test_extract_recent_actions(self):
        content = """## In Progress

- [ ] Working on feature X
- [ ] Debugging issue Y

## Completed

- [x] Setup project
- [x] Write tests
"""
        actions = _extract_recent_actions(content)
        assert len(actions) >= 2

    def test_limit_to_10_actions(self):
        # Create content with more than 10 actions
        lines = ["## Completed\n"]
        for i in range(15):
            lines.append(f"- [x] Action {i}\n")
        content = "".join(lines)

        actions = _extract_recent_actions(content)
        assert len(actions) <= 10


class TestCalculateDriftScore:
    """Test _calculate_drift_score function"""

    def test_perfect_alignment(self):
        goals = ["implement login", "add authentication"]
        current_task = "implement login feature"
        recent_actions = ["working on login", "testing authentication"]

        score, reasons = _calculate_drift_score(goals, current_task, recent_actions)
        assert score < 50  # Should be low (good alignment)

    def test_complete_drift(self):
        goals = ["implement login"]
        current_task = "implement login feature"
        recent_actions = ["fixing CSS", "updating colors", "changing fonts"]

        score, reasons = _calculate_drift_score(goals, current_task, recent_actions)
        assert score > 50  # Should be high (drift detected)

    def test_no_goals(self):
        score, reasons = _calculate_drift_score([], None, ["some action"])
        assert score == 0

    def test_no_recent_actions(self):
        score, reasons = _calculate_drift_score(["goal"], "task", [])
        assert score == 0


class TestAnalyzeErrorPatterns:
    """Test _analyze_error_patterns function"""

    def test_detect_patterns(self):
        content = """## Error History

Error: TypeError: undefined
Error: TypeError: null
Error: ValueError: invalid input
TypeError: another one
"""
        patterns = _analyze_error_patterns(content)
        assert patterns.get("typeerror", 0) >= 2

    def test_no_patterns(self):
        content = """## Error History

No errors recorded
"""
        patterns = _analyze_error_patterns(content)
        assert len(patterns) == 0


class TestDriftCheck:
    """Test drift_check function"""

    @pytest.mark.asyncio
    async def test_drift_check_no_plan(self, tmp_path):
        """Test drift_check when no task plan exists"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await drift_check(str(tmp_path))
            assert len(result) == 1
            assert "No task plan found" in result[0].text or "init_planning" in result[0].text

    @pytest.mark.asyncio
    async def test_drift_check_path_not_exists(self):
        """Test drift_check with non-existent path"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await drift_check("/non/existent/path")
            assert len(result) == 1
            assert "not exist" in result[0].text.lower() or "PATH_NOT_FOUND" in result[0].text

    @pytest.mark.asyncio
    async def test_drift_check_pro_required(self):
        """Test drift_check requires Pro license"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=False):
            result = await drift_check(".")
            assert len(result) == 1
            assert "Pro feature" in result[0].text

    @pytest.mark.asyncio
    async def test_drift_check_silent_mode(self, tmp_path):
        """Test drift_check silent mode returns minimal output"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await drift_check(str(tmp_path), silent=True)
            assert len(result) == 1
            # Silent mode returns short status
            assert ":" in result[0].text or "OK" in result[0].text


class TestPatternWatch:
    """Test pattern_watch function"""

    @pytest.mark.asyncio
    async def test_pattern_watch_no_history(self, tmp_path):
        """Test pattern_watch when no error history exists"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await pattern_watch(str(tmp_path))
            assert len(result) == 1
            assert "No error history" in result[0].text

    @pytest.mark.asyncio
    async def test_pattern_watch_pro_required(self):
        """Test pattern_watch requires Pro license"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=False):
            result = await pattern_watch(".")
            assert len(result) == 1
            assert "Pro feature" in result[0].text

    @pytest.mark.asyncio
    async def test_pattern_watch_detects_patterns(self, tmp_path):
        """Test pattern_watch detects repeated errors"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            # Create error history
            errors_dir = tmp_path / ".claude" / "errors"
            errors_dir.mkdir(parents=True)

            history_file = errors_dir / "history.md"
            history_file.write_text("""## Error History

Error: TypeError: undefined
Error: TypeError: null
Error: TypeError: missing
Error: TypeError: wrong type
""")

            result = await pattern_watch(str(tmp_path), threshold=3)
            assert len(result) == 1
            # Should detect TypeError pattern


class TestAutoRemind:
    """Test auto_remind function"""

    @pytest.mark.asyncio
    async def test_auto_remind_creates_config(self, tmp_path):
        """Test auto_remind creates config file"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await auto_remind(str(tmp_path), interval=30, enabled=True)
            assert len(result) == 1
            assert "Configured" in result[0].text

            # Check config file was created
            config_path = tmp_path / ".clouvel" / "config.yaml"
            assert config_path.exists()

    @pytest.mark.asyncio
    async def test_auto_remind_pro_required(self):
        """Test auto_remind requires Pro license"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=False):
            result = await auto_remind(".")
            assert len(result) == 1
            assert "Pro feature" in result[0].text

    @pytest.mark.asyncio
    async def test_auto_remind_custom_interval(self, tmp_path):
        """Test auto_remind with custom interval"""
        with patch("src.clouvel.tools.proactive._can_use_pro", return_value=True):
            result = await auto_remind(str(tmp_path), interval=60, enabled=True)
            assert len(result) == 1
            assert "60" in result[0].text


class TestCanUsePro:
    """Test _can_use_pro function (v5.2: delegates to services.tier.can_use_pro)"""

    def test_developer_mode(self):
        """Test Pro access in developer mode"""
        with patch("src.clouvel.services.tier.can_use_pro", return_value=True):
            from src.clouvel.tools.proactive import _can_use_pro
            assert _can_use_pro("/some/path") is True

    def test_no_license(self):
        """Test no Pro access without license"""
        with patch("src.clouvel.services.tier.can_use_pro", return_value=False):
            from src.clouvel.tools.proactive import _can_use_pro
            assert _can_use_pro("/some/path") is False
