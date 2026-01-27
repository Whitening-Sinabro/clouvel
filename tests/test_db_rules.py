# -*- coding: utf-8 -*-
"""Database rules module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.schema import init_db
from clouvel.db.rules import (
    generate_rule_id,
    add_rule,
    get_rules,
    apply_rule,
    get_rules_for_error,
    export_rules_to_markdown,
)
from clouvel.db.errors import record_error


@pytest.fixture
def temp_project():
    """Create temporary project directory with initialized DB"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    init_db(str(temp_path))
    yield temp_path
    shutil.rmtree(temp_dir)


class TestGenerateRuleId:
    """generate_rule_id function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = generate_rule_id()
        assert isinstance(result, str)

    def test_starts_with_rule(self):
        """ID starts with rule_"""
        result = generate_rule_id()
        assert result.startswith("rule_")

    def test_unique_ids(self):
        """Generates unique IDs"""
        ids = [generate_rule_id() for _ in range(10)]
        assert len(set(ids)) == 10

    def test_contains_timestamp(self):
        """Contains timestamp component"""
        result = generate_rule_id()
        parts = result.split("_")
        assert len(parts) >= 3
        # Check date part looks like YYYYMMDD
        assert len(parts[1]) == 8
        assert parts[1].isdigit()


class TestAddRule:
    """add_rule function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_returns_status_created(self, temp_project):
        """Returns status created"""
        result = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        assert result["status"] == "created"

    def test_returns_id(self, temp_project):
        """Returns rule ID"""
        result = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        assert "id" in result
        assert result["id"].startswith("rule_")

    def test_adds_never_rule(self, temp_project):
        """Adds NEVER rule"""
        add_rule("NEVER", "Test NEVER rule", project_path=str(temp_project))
        rules = get_rules(rule_type="NEVER", project_path=str(temp_project))
        assert len(rules) == 1
        assert rules[0]["rule_type"] == "NEVER"

    def test_adds_always_rule(self, temp_project):
        """Adds ALWAYS rule"""
        add_rule("ALWAYS", "Test ALWAYS rule", project_path=str(temp_project))
        rules = get_rules(rule_type="ALWAYS", project_path=str(temp_project))
        assert len(rules) == 1
        assert rules[0]["rule_type"] == "ALWAYS"

    def test_adds_prefer_rule(self, temp_project):
        """Adds PREFER rule"""
        add_rule("PREFER", "Test PREFER rule", project_path=str(temp_project))
        rules = get_rules(rule_type="PREFER", project_path=str(temp_project))
        assert len(rules) == 1
        assert rules[0]["rule_type"] == "PREFER"

    def test_adds_with_category(self, temp_project):
        """Adds rule with category"""
        add_rule(
            "NEVER",
            "Test rule",
            category="security",
            project_path=str(temp_project)
        )
        rules = get_rules(category="security", project_path=str(temp_project))
        assert len(rules) == 1
        assert rules[0]["category"] == "security"

    def test_detects_duplicate(self, temp_project):
        """Detects duplicate rule"""
        add_rule("NEVER", "Same content", project_path=str(temp_project))
        result = add_rule("NEVER", "Same content", project_path=str(temp_project))

        assert result["status"] == "duplicate"
        assert "existing_id" in result


class TestGetRules:
    """get_rules function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        result = get_rules(project_path=str(temp_project))
        assert isinstance(result, list)

    def test_empty_for_no_rules(self, temp_project):
        """Empty list when no rules"""
        result = get_rules(project_path=str(temp_project))
        assert result == []

    def test_returns_added_rules(self, temp_project):
        """Returns added rules"""
        add_rule("NEVER", "Rule 1", project_path=str(temp_project))
        add_rule("ALWAYS", "Rule 2", project_path=str(temp_project))

        result = get_rules(project_path=str(temp_project))
        assert len(result) == 2

    def test_filters_by_rule_type(self, temp_project):
        """Filters by rule type"""
        add_rule("NEVER", "NEVER rule", project_path=str(temp_project))
        add_rule("ALWAYS", "ALWAYS rule", project_path=str(temp_project))

        result = get_rules(rule_type="NEVER", project_path=str(temp_project))
        assert len(result) == 1
        assert result[0]["rule_type"] == "NEVER"

    def test_filters_by_category(self, temp_project):
        """Filters by category"""
        add_rule("NEVER", "Rule 1", category="api", project_path=str(temp_project))
        add_rule("NEVER", "Rule 2", category="security", project_path=str(temp_project))

        result = get_rules(category="api", project_path=str(temp_project))
        assert len(result) == 1
        assert result[0]["category"] == "api"

    def test_respects_limit(self, temp_project):
        """Respects limit parameter"""
        for i in range(10):
            add_rule("NEVER", f"Rule {i}", project_path=str(temp_project))

        result = get_rules(limit=5, project_path=str(temp_project))
        assert len(result) == 5

    def test_combined_filters(self, temp_project):
        """Combined filters work together"""
        add_rule("NEVER", "Rule 1", category="api", project_path=str(temp_project))
        add_rule("NEVER", "Rule 2", category="security", project_path=str(temp_project))
        add_rule("ALWAYS", "Rule 3", category="api", project_path=str(temp_project))

        result = get_rules(
            rule_type="NEVER",
            category="api",
            project_path=str(temp_project)
        )
        assert len(result) == 1


class TestApplyRule:
    """apply_rule function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        result = apply_rule(rule["id"], project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_returns_applied_status(self, temp_project):
        """Returns applied status"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        result = apply_rule(rule["id"], project_path=str(temp_project))
        assert result["status"] == "applied"
        assert result["id"] == rule["id"]

    def test_returns_not_found_for_invalid(self, temp_project):
        """Returns not_found for invalid ID"""
        result = apply_rule("invalid_id", project_path=str(temp_project))
        assert result["status"] == "not_found"

    def test_increments_applied_count(self, temp_project):
        """Increments applied_count"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        apply_rule(rule["id"], project_path=str(temp_project))
        apply_rule(rule["id"], project_path=str(temp_project))
        apply_rule(rule["id"], project_path=str(temp_project))

        rules = get_rules(project_path=str(temp_project))
        assert rules[0]["applied_count"] == 3

    def test_updates_last_applied(self, temp_project):
        """Updates last_applied timestamp"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        apply_rule(rule["id"], project_path=str(temp_project))

        rules = get_rules(project_path=str(temp_project))
        assert rules[0]["last_applied"] is not None

    def test_links_to_error(self, temp_project):
        """Links rule to error"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        error = record_error("Test error", project_path=str(temp_project))

        apply_rule(rule["id"], error_id=error["id"], project_path=str(temp_project))

        linked = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert len(linked) == 1
        assert linked[0]["id"] == rule["id"]

    def test_marks_prevented(self, temp_project):
        """Marks rule as prevented error"""
        rule = add_rule("NEVER", "Test rule", project_path=str(temp_project))
        error = record_error("Test error", project_path=str(temp_project))

        apply_rule(
            rule["id"],
            error_id=error["id"],
            prevented=True,
            project_path=str(temp_project)
        )

        linked = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert linked[0]["prevented"] == 1


class TestGetRulesForError:
    """get_rules_for_error function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        error = record_error("Test error", project_path=str(temp_project))
        result = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert isinstance(result, list)

    def test_empty_for_no_linked_rules(self, temp_project):
        """Empty list when no rules linked"""
        error = record_error("Test error", project_path=str(temp_project))
        result = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert result == []

    def test_returns_linked_rules(self, temp_project):
        """Returns linked rules"""
        error = record_error("Test error", project_path=str(temp_project))
        rule1 = add_rule("NEVER", "Rule 1", project_path=str(temp_project))
        rule2 = add_rule("ALWAYS", "Rule 2", project_path=str(temp_project))

        apply_rule(rule1["id"], error_id=error["id"], project_path=str(temp_project))
        apply_rule(rule2["id"], error_id=error["id"], project_path=str(temp_project))

        result = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert len(result) == 2

    def test_includes_rule_fields(self, temp_project):
        """Includes rule fields"""
        error = record_error("Test error", project_path=str(temp_project))
        rule = add_rule(
            "NEVER",
            "Test content",
            category="security",
            project_path=str(temp_project)
        )
        apply_rule(rule["id"], error_id=error["id"], project_path=str(temp_project))

        result = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert result[0]["rule_type"] == "NEVER"
        assert result[0]["content"] == "Test content"
        assert result[0]["category"] == "security"

    def test_rule_linked_via_source_error_id(self, temp_project):
        """Rule linked via source_error_id"""
        error = record_error("Test error", project_path=str(temp_project))
        add_rule(
            "NEVER",
            "Rule from error",
            source_error_id=error["id"],
            project_path=str(temp_project)
        )

        result = get_rules_for_error(error["id"], project_path=str(temp_project))
        assert len(result) == 1


class TestExportRulesToMarkdown:
    """export_rules_to_markdown function tests"""

    def test_returns_string(self, temp_project):
        """Returns string"""
        result = export_rules_to_markdown(project_path=str(temp_project))
        assert isinstance(result, str)

    def test_empty_for_no_rules(self, temp_project):
        """Empty string when no rules"""
        result = export_rules_to_markdown(project_path=str(temp_project))
        assert result == ""

    def test_includes_header(self, temp_project):
        """Includes header section"""
        add_rule("NEVER", "Test rule", project_path=str(temp_project))
        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "Clouvel" in result
        assert "규칙" in result

    def test_groups_never_rules(self, temp_project):
        """Groups NEVER rules"""
        add_rule("NEVER", "Never do this", project_path=str(temp_project))
        add_rule("NEVER", "Never do that", project_path=str(temp_project))

        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "NEVER" in result
        assert "절대 금지" in result
        assert "Never do this" in result
        assert "Never do that" in result

    def test_groups_always_rules(self, temp_project):
        """Groups ALWAYS rules"""
        add_rule("ALWAYS", "Always do this", project_path=str(temp_project))

        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "ALWAYS" in result
        assert "필수 준수" in result
        assert "Always do this" in result

    def test_groups_prefer_rules(self, temp_project):
        """Groups PREFER rules"""
        add_rule("PREFER", "Prefer this approach", project_path=str(temp_project))

        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "PREFER" in result
        assert "권장" in result
        assert "Prefer this approach" in result

    def test_all_rule_types(self, temp_project):
        """Exports all rule types"""
        add_rule("NEVER", "Never rule", project_path=str(temp_project))
        add_rule("ALWAYS", "Always rule", project_path=str(temp_project))
        add_rule("PREFER", "Prefer rule", project_path=str(temp_project))

        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "Never rule" in result
        assert "Always rule" in result
        assert "Prefer rule" in result

    def test_formats_as_list(self, temp_project):
        """Formats rules as markdown list"""
        add_rule("NEVER", "Test rule", project_path=str(temp_project))

        result = export_rules_to_markdown(project_path=str(temp_project))
        assert "- Test rule" in result


class TestDbRulesIntegration:
    """Integration tests for db rules"""

    def test_full_workflow(self, temp_project):
        """Full rule management workflow"""
        # Add various rules
        add_rule(
            "NEVER",
            "Never commit secrets",
            category="security",
            project_path=str(temp_project)
        )
        add_rule(
            "ALWAYS",
            "Always write tests",
            category="general",
            project_path=str(temp_project)
        )
        add_rule(
            "PREFER",
            "Prefer composition over inheritance",
            category="general",
            project_path=str(temp_project)
        )

        # Query all rules
        all_rules = get_rules(project_path=str(temp_project))
        assert len(all_rules) == 3

        # Query by type
        never_rules = get_rules(rule_type="NEVER", project_path=str(temp_project))
        assert len(never_rules) == 1
        assert "secrets" in never_rules[0]["content"]

        # Query by category
        general_rules = get_rules(category="general", project_path=str(temp_project))
        assert len(general_rules) == 2

    def test_multiple_categories(self, temp_project):
        """Test all categories"""
        categories = ["api", "frontend", "database", "security", "general"]

        for cat in categories:
            add_rule("NEVER", f"Rule for {cat}", category=cat, project_path=str(temp_project))

        for cat in categories:
            rules = get_rules(category=cat, project_path=str(temp_project))
            assert len(rules) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
