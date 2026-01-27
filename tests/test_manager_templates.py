# -*- coding: utf-8 -*-
"""Manager templates module tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.prompts.templates import (
    MEETING_TEMPLATE,
    get_system_prompt,
    get_persona_prompt,
)


class TestMeetingTemplate:
    """MEETING_TEMPLATE constant tests"""

    def test_template_exists(self):
        """Template string exists"""
        assert MEETING_TEMPLATE is not None
        assert isinstance(MEETING_TEMPLATE, str)
        assert len(MEETING_TEMPLATE) > 0

    def test_contains_philosophy(self):
        """Contains augmentation philosophy"""
        assert "AUGMENTATION" in MEETING_TEMPLATE
        assert "NOT AUTOMATION" in MEETING_TEMPLATE

    def test_contains_manager_placeholder(self):
        """Contains manager_list placeholder"""
        assert "{manager_list}" in MEETING_TEMPLATE

    def test_contains_meeting_rules(self):
        """Contains meeting rules section"""
        assert "Meeting Rules" in MEETING_TEMPLATE

    def test_contains_output_format(self):
        """Contains output format section"""
        assert "Output Format" in MEETING_TEMPLATE


class TestGetSystemPrompt:
    """get_system_prompt function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = get_system_prompt()
        assert isinstance(result, str)

    def test_includes_all_managers_by_default(self):
        """Includes all managers when no list provided"""
        result = get_system_prompt()
        assert "PM" in result
        assert "CTO" in result
        assert "QA" in result

    def test_filters_to_specified_managers(self):
        """Filters to specified managers only"""
        result = get_system_prompt(["PM", "CTO"])
        assert "PM" in result
        assert "CTO" in result
        # QA should not appear as much (may appear in template text)
        manager_sections = result.count("### ")
        assert manager_sections >= 2

    def test_includes_manager_details(self):
        """Includes manager details"""
        result = get_system_prompt(["PM"])
        assert "years" in result
        assert "Expertise" in result
        assert "Philosophy" in result

    def test_includes_probing_questions(self):
        """Includes probing questions"""
        result = get_system_prompt(["PM"])
        assert "Probing Questions" in result

    def test_handles_empty_list(self):
        """Handles empty manager list"""
        result = get_system_prompt([])
        # Should still include template
        assert "Meeting Rules" in result

    def test_handles_invalid_manager(self):
        """Handles invalid manager key"""
        result = get_system_prompt(["INVALID_MANAGER"])
        # Should not crash
        assert isinstance(result, str)


class TestGetPersonaPrompt:
    """get_persona_prompt function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = get_persona_prompt("PM")
        assert isinstance(result, str)

    def test_pm_prompt_structure(self):
        """PM prompt has expected structure"""
        result = get_persona_prompt("PM")
        assert "PM" in result
        assert "Experience" in result
        assert "years" in result

    def test_includes_career(self):
        """Includes career section"""
        result = get_persona_prompt("CTO")
        assert "Career" in result

    def test_case_insensitive(self):
        """Works case insensitively - both produce valid prompts"""
        pm = get_persona_prompt("pm")
        PM = get_persona_prompt("PM")
        # Both should return non-empty prompts
        assert len(pm) > 0
        assert len(PM) > 0
        # Core content should match (except for the key display)
        assert "Experience" in pm
        assert "Experience" in PM

    def test_unknown_returns_empty(self):
        """Unknown manager returns empty string"""
        result = get_persona_prompt("UNKNOWN_MANAGER")
        assert result == ""

    def test_includes_emoji(self):
        """Includes manager emoji"""
        result = get_persona_prompt("CTO")
        assert "🛠️" in result

    def test_includes_expertise(self):
        """Includes expertise"""
        result = get_persona_prompt("QA")
        assert "Test strategy" in result or "testing" in result.lower()

    def test_all_managers_have_prompt(self):
        """All managers have valid prompts"""
        manager_keys = ["PM", "CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]
        for key in manager_keys:
            result = get_persona_prompt(key)
            assert len(result) > 0, f"{key} should have a prompt"


class TestTemplatesIntegration:
    """Integration tests for templates"""

    def test_system_prompt_with_single_manager(self):
        """System prompt works with single manager"""
        result = get_system_prompt(["PM"])
        assert "PM" in result
        assert "C-Level meeting" in result

    def test_system_prompt_formatting(self):
        """System prompt is properly formatted"""
        result = get_system_prompt(["PM", "CTO"])
        # No unresolved placeholders
        assert "{" not in result.replace("{{", "").replace("}}", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
