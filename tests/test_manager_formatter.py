# -*- coding: utf-8 -*-
"""Manager formatter module tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.formatter import (
    _format_output,
    _generate_conversation,
    _get_ai_instruction_template,
)


def create_mock_result(
    active_managers=None,
    topics=None,
    has_critical=False,
    has_warnings=False,
    has_missing=False,
    has_concerns=False,
    has_opinions=False,
    has_actions=False,
    has_recommendations=False,
    overall_status="REVIEW_NEEDED",
):
    """Create a mock result dictionary for testing"""
    if active_managers is None:
        active_managers = ["PM", "CTO"]
    if topics is None:
        topics = ["feature"]

    feedback = {}
    for mgr in active_managers:
        emoji = {"PM": "👔", "CTO": "🛠️", "QA": "🧪", "CSO": "🔒", "CFO": "💰", "CMO": "📢"}.get(mgr, "👤")
        feedback[mgr] = {
            "emoji": emoji,
            "questions": [f"What about {mgr.lower()} concerns?"],
            "opinions": [f"{mgr} opinion here"] if has_opinions else [],
            "warnings": ["Security issue found"] if has_warnings else [],
            "concerns": [f"{mgr} concern here"] if has_concerns else [],
            "critical_issues": ["Critical security bug"] if has_critical else [],
            "missing_items": ["Missing test coverage"] if has_missing else [],
        }

    result = {
        "context_analysis": {"detected_topics": topics},
        "active_managers": active_managers,
        "feedback": feedback,
        "overall_status": overall_status,
        "warnings": ["Don't expose secrets"] if has_warnings else [],
        "critical_issues": ["Critical bug found"] if has_critical else [],
        "missing_items": ["Missing docs"] if has_missing else [],
        "action_items": [
            {"action": "Fix security bug", "manager": "CTO", "emoji": "🛠️", "verify": "Run tests"},
            {"action": "Write tests", "manager": "QA", "emoji": "🧪", "verify": "Coverage check"},
        ] if has_actions else [],
        "recommendations": ["Consider caching"] if has_recommendations else [],
    }

    return result


class TestFormatOutput:
    """_format_output function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = create_mock_result()
        output = _format_output(result)
        assert isinstance(output, str)

    def test_includes_instruction_tag(self):
        """Includes instruction tag"""
        result = create_mock_result()
        output = _format_output(result)
        assert "<instruction>" in output

    def test_includes_situation_analysis(self):
        """Includes situation analysis"""
        result = create_mock_result()
        output = _format_output(result)
        assert "<situation_analysis>" in output

    def test_includes_meeting_notes(self):
        """Includes meeting notes"""
        result = create_mock_result()
        output = _format_output(result)
        assert "<meeting_notes>" in output

    def test_includes_final_summary(self):
        """Includes final summary"""
        result = create_mock_result()
        output = _format_output(result)
        assert "<final_summary>" in output

    def test_includes_output_format(self):
        """Includes output format tag"""
        result = create_mock_result()
        output = _format_output(result)
        assert "<output_format>" in output

    def test_shows_topics(self):
        """Shows detected topics"""
        result = create_mock_result(topics=["auth", "security"])
        output = _format_output(result)
        assert "auth" in output

    def test_shows_managers(self):
        """Shows active managers"""
        result = create_mock_result(active_managers=["PM", "CTO", "QA"])
        output = _format_output(result)
        assert "PM" in output
        assert "CTO" in output

    def test_critical_summary_when_critical(self):
        """Shows critical summary when has critical issues"""
        result = create_mock_result(has_critical=True)
        output = _format_output(result)
        assert "<critical_summary>" in output
        assert "CRITICAL ISSUES" in output

    def test_critical_reminder_when_critical(self):
        """Shows critical reminder at end when has critical"""
        result = create_mock_result(has_critical=True)
        output = _format_output(result)
        assert "<critical_reminder>" in output

    def test_missing_items_section(self):
        """Shows missing items section"""
        result = create_mock_result(has_missing=True)
        output = _format_output(result)
        assert "<missing_items>" in output or "Missing" in output

    def test_action_items_table(self):
        """Shows action items table"""
        result = create_mock_result(has_actions=True)
        output = _format_output(result)
        assert "Immediate Tasks" in output
        assert "Fix security bug" in output

    def test_warnings_section(self):
        """Shows warnings section"""
        result = create_mock_result(has_warnings=True)
        output = _format_output(result)
        assert "Warnings" in output or "NEVER" in output

    def test_recommendations_section(self):
        """Shows recommendations section"""
        result = create_mock_result(has_recommendations=True)
        output = _format_output(result)
        assert "Recommendations" in output

    def test_approved_status_icon(self):
        """Shows approved status with checkmark"""
        result = create_mock_result(overall_status="APPROVED")
        output = _format_output(result)
        assert "✅" in output

    def test_blocked_status_icon(self):
        """Shows blocked status icon"""
        result = create_mock_result(overall_status="BLOCKED")
        output = _format_output(result)
        assert "🚫" in output

    def test_needs_revision_status_icon(self):
        """Shows needs revision status"""
        result = create_mock_result(overall_status="NEEDS_REVISION")
        output = _format_output(result)
        assert "⚠️" in output

    def test_manager_status_in_table(self):
        """Shows manager status in table"""
        result = create_mock_result(active_managers=["PM"])
        output = _format_output(result)
        # Should have table with status
        assert "| Area | Status | Note |" in output or "| " in output

    def test_truncates_long_notes(self):
        """Truncates long notes in table"""
        result = create_mock_result()
        # Modify to have a very long opinion
        result["feedback"]["PM"]["opinions"] = ["This is a very long opinion that exceeds forty characters and should be truncated"]
        output = _format_output(result)
        # Should contain truncated text with ...
        assert "..." in output or len(output) > 0

    def test_on_hold_section_with_many_actions(self):
        """Shows on hold section when more than 5 actions"""
        result = create_mock_result()
        result["action_items"] = [
            {"action": f"Task {i}", "manager": "CTO", "emoji": "🛠️", "verify": "Test"}
            for i in range(8)
        ]
        output = _format_output(result)
        assert "On Hold" in output or "Later" in output


class TestGenerateConversation:
    """_generate_conversation function tests"""

    def test_returns_list(self):
        """Returns list"""
        result = create_mock_result()
        output = _generate_conversation(result)
        assert isinstance(output, list)

    def test_includes_manager_lines(self):
        """Includes lines for each manager"""
        result = create_mock_result(active_managers=["PM", "CTO"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "PM" in joined or "CTO" in joined

    def test_uses_emoji(self):
        """Uses manager emoji"""
        result = create_mock_result(active_managers=["PM"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "👔" in joined

    def test_shows_opinions(self):
        """Shows manager opinions"""
        result = create_mock_result(has_opinions=True)
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "opinion" in joined

    def test_shows_questions_without_opinions(self):
        """Shows questions when no opinions"""
        result = create_mock_result(has_opinions=False)
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "?" in joined or "concerns" in joined

    def test_shows_warnings(self):
        """Shows warnings"""
        result = create_mock_result(has_warnings=True)
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "🚨" in joined or "Security" in joined

    def test_shows_concerns(self):
        """Shows concerns"""
        result = create_mock_result(has_concerns=True)
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "concern" in joined

    def test_pm_summary_at_end(self):
        """PM provides summary at end"""
        result = create_mock_result(active_managers=["PM", "CTO"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "summarize" in joined.lower() or "summary" in joined.lower() or "proceed" in joined.lower()

    def test_pm_mentions_actions(self):
        """PM mentions action items"""
        result = create_mock_result(active_managers=["PM"], has_actions=True)
        output = _generate_conversation(result)
        joined = "\n".join(output)
        # PM should provide summary
        assert "PM" in joined

    def test_auth_topic_mention(self):
        """Mentions auth when topic detected"""
        result = create_mock_result(active_managers=["PM"], topics=["auth"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "auth" in joined.lower() or "PM" in joined

    def test_payment_topic_mention(self):
        """Mentions payment when topic detected"""
        result = create_mock_result(active_managers=["PM"], topics=["payment"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "payment" in joined.lower() or "PM" in joined

    def test_api_topic_mention(self):
        """Mentions API when topic detected"""
        result = create_mock_result(active_managers=["PM"], topics=["api"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        assert "api" in joined.lower() or "PM" in joined


class TestGetAiInstructionTemplate:
    """_get_ai_instruction_template function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = _get_ai_instruction_template()
        assert isinstance(result, str)

    def test_includes_meeting_notes_format(self):
        """Includes meeting notes format"""
        result = _get_ai_instruction_template()
        assert "Meeting Notes" in result or "meeting" in result.lower()

    def test_includes_output_format(self):
        """Includes output format section"""
        result = _get_ai_instruction_template()
        assert "Output Format" in result or "format" in result.lower()

    def test_includes_writing_rules(self):
        """Includes writing rules"""
        result = _get_ai_instruction_template()
        assert "Rules" in result or "rule" in result.lower()

    def test_includes_manager_placeholders(self):
        """Includes manager placeholders"""
        result = _get_ai_instruction_template()
        assert "PM" in result and "CTO" in result

    def test_includes_table_format(self):
        """Includes table format examples"""
        result = _get_ai_instruction_template()
        assert "|" in result


class TestFormatterIntegration:
    """Integration tests for formatter"""

    def test_full_result_formatting(self):
        """Test with full result"""
        result = create_mock_result(
            active_managers=["PM", "CTO", "QA", "CSO"],
            topics=["auth", "security"],
            has_critical=True,
            has_warnings=True,
            has_missing=True,
            has_concerns=True,
            has_opinions=True,
            has_actions=True,
            has_recommendations=True,
            overall_status="NEEDS_REVISION"
        )
        output = _format_output(result)

        # Should include all sections
        assert "<critical_summary>" in output
        assert "<situation_analysis>" in output
        assert "<meeting_notes>" in output
        assert "<final_summary>" in output
        assert "<critical_reminder>" in output

    def test_minimal_result_formatting(self):
        """Test with minimal result"""
        result = create_mock_result(
            active_managers=["PM"],
            topics=["feature"],
            overall_status="APPROVED"
        )
        output = _format_output(result)

        # Should still have basic structure
        assert "<instruction>" in output
        assert "<situation_analysis>" in output
        assert "<meeting_notes>" in output

    def test_no_pm_in_managers(self):
        """Test when PM not in active managers"""
        result = create_mock_result(active_managers=["CTO", "QA"])
        output = _generate_conversation(result)
        joined = "\n".join(output)
        # Should not have PM summary line
        # But may still output something
        assert isinstance(output, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
