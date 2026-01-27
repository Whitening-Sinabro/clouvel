# -*- coding: utf-8 -*-
"""Manager examples module tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.prompts.examples import (
    EXAMPLES,
    get_examples_for_topic,
    get_all_examples,
    format_examples_for_prompt,
)


class TestExamplesConstant:
    """EXAMPLES constant tests"""

    def test_examples_exist(self):
        """Examples dictionary exists"""
        assert isinstance(EXAMPLES, dict)
        assert len(EXAMPLES) > 0

    def test_has_auth_examples(self):
        """Has auth examples"""
        assert "auth" in EXAMPLES

    def test_has_api_examples(self):
        """Has api examples"""
        assert "api" in EXAMPLES

    def test_has_maintenance_examples(self):
        """Has maintenance examples"""
        assert "maintenance" in EXAMPLES

    def test_has_error_examples(self):
        """Has error examples"""
        assert "error" in EXAMPLES

    def test_has_cost_examples(self):
        """Has cost examples"""
        assert "cost" in EXAMPLES

    def test_has_feature_examples(self):
        """Has feature examples"""
        assert "feature" in EXAMPLES

    def test_has_payment_examples(self):
        """Has payment examples"""
        assert "payment" in EXAMPLES

    def test_has_ui_examples(self):
        """Has ui examples"""
        assert "ui" in EXAMPLES

    def test_has_launch_examples(self):
        """Has launch examples"""
        assert "launch" in EXAMPLES

    def test_has_security_examples(self):
        """Has security examples"""
        assert "security" in EXAMPLES

    def test_has_performance_examples(self):
        """Has performance examples"""
        assert "performance" in EXAMPLES

    def test_has_design_examples(self):
        """Has design examples"""
        assert "design" in EXAMPLES


class TestExampleStructure:
    """Example structure tests"""

    def test_each_topic_has_list(self):
        """Each topic has a list of examples"""
        for topic, examples in EXAMPLES.items():
            assert isinstance(examples, list), f"{topic} should have list"

    def test_each_example_has_context(self):
        """Each example has context field"""
        for topic, examples in EXAMPLES.items():
            for ex in examples:
                assert "context" in ex, f"{topic} example missing context"

    def test_each_example_has_output(self):
        """Each example has output field"""
        for topic, examples in EXAMPLES.items():
            for ex in examples:
                assert "output" in ex, f"{topic} example missing output"

    def test_output_has_meeting_notes(self):
        """Output contains meeting notes format"""
        for topic, examples in EXAMPLES.items():
            for ex in examples:
                assert "C-Level Meeting" in ex["output"] or "PM" in ex["output"]


class TestGetExamplesForTopic:
    """get_examples_for_topic function tests"""

    def test_returns_list(self):
        """Returns list"""
        result = get_examples_for_topic("auth")
        assert isinstance(result, list)

    def test_returns_auth_examples(self):
        """Returns auth examples"""
        result = get_examples_for_topic("auth")
        assert len(result) >= 1
        assert "context" in result[0]

    def test_returns_api_examples(self):
        """Returns api examples"""
        result = get_examples_for_topic("api")
        assert len(result) >= 1

    def test_respects_limit(self):
        """Respects limit parameter"""
        result = get_examples_for_topic("auth", limit=1)
        assert len(result) <= 1

    def test_fallback_to_feature(self):
        """Falls back to feature for unknown topic"""
        result = get_examples_for_topic("unknown_topic")
        # Should return feature examples as fallback
        assert len(result) >= 1

    def test_default_limit_is_3(self):
        """Default limit is 3"""
        result = get_examples_for_topic("auth")
        assert len(result) <= 3


class TestGetAllExamples:
    """get_all_examples function tests"""

    def test_returns_list(self):
        """Returns list"""
        result = get_all_examples()
        assert isinstance(result, list)

    def test_returns_all_examples(self):
        """Returns all examples from all topics"""
        result = get_all_examples()
        # Should have at least one example per topic
        assert len(result) >= len(EXAMPLES)

    def test_each_has_context(self):
        """Each example has context"""
        result = get_all_examples()
        for ex in result:
            assert "context" in ex

    def test_each_has_output(self):
        """Each example has output"""
        result = get_all_examples()
        for ex in result:
            assert "output" in ex


class TestFormatExamplesForPrompt:
    """format_examples_for_prompt function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = format_examples_for_prompt("auth")
        assert isinstance(result, str)

    def test_includes_examples_header(self):
        """Includes Examples header"""
        result = format_examples_for_prompt("auth")
        assert "## Examples" in result

    def test_includes_context(self):
        """Includes context section"""
        result = format_examples_for_prompt("auth")
        assert "**Context**:" in result

    def test_includes_meeting_notes(self):
        """Includes meeting notes section"""
        result = format_examples_for_prompt("auth")
        assert "**Meeting Notes**:" in result

    def test_respects_limit(self):
        """Respects limit parameter"""
        result = format_examples_for_prompt("auth", limit=1)
        # Should have exactly 1 example
        assert result.count("### Example") == 1

    def test_default_limit_is_2(self):
        """Default limit is 2"""
        result = format_examples_for_prompt("auth")
        # Should have at most 2 examples
        assert result.count("### Example") <= 2

    def test_empty_for_invalid_topic_with_no_feature_fallback(self):
        """Returns empty for unknown topic with no examples"""
        # Actually it falls back to feature, so should return something
        result = format_examples_for_prompt("unknown_topic")
        assert "## Examples" in result


class TestExamplesContent:
    """Tests for example content quality"""

    def test_auth_example_mentions_oauth(self):
        """Auth example mentions OAuth"""
        examples = get_examples_for_topic("auth")
        assert any("OAuth" in ex["output"] for ex in examples)

    def test_api_example_mentions_rest(self):
        """API example mentions REST"""
        examples = get_examples_for_topic("api")
        assert any("REST" in ex["context"] or "API" in ex["context"] for ex in examples)

    def test_security_example_mentions_owasp(self):
        """Security example mentions OWASP"""
        examples = get_examples_for_topic("security")
        assert any("OWASP" in ex["context"] or "SQL" in ex["output"] for ex in examples)

    def test_payment_example_mentions_stripe(self):
        """Payment example mentions Stripe"""
        examples = get_examples_for_topic("payment")
        assert any("Stripe" in ex["context"] or "Stripe" in ex["output"] for ex in examples)

    def test_examples_have_action_items(self):
        """Examples have action items section"""
        examples = get_all_examples()
        for ex in examples:
            assert "Action Items" in ex["output"]

    def test_examples_have_warnings(self):
        """Examples have warnings section"""
        examples = get_all_examples()
        for ex in examples:
            assert "Warnings" in ex["output"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
