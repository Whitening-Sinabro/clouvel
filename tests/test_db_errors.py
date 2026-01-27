# -*- coding: utf-8 -*-
"""Database errors module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.schema import init_db
from clouvel.db.errors import (
    generate_error_id,
    record_error,
    get_error,
    list_errors,
    resolve_error,
    search_errors_by_type,
    get_error_stats,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory with initialized DB"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    init_db(str(temp_path))
    yield temp_path
    shutil.rmtree(temp_dir)


class TestGenerateErrorId:
    """generate_error_id function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = generate_error_id()
        assert isinstance(result, str)

    def test_starts_with_err(self):
        """ID starts with err_"""
        result = generate_error_id()
        assert result.startswith("err_")

    def test_unique_ids(self):
        """Generates unique IDs"""
        ids = [generate_error_id() for _ in range(10)]
        assert len(set(ids)) == 10

    def test_contains_timestamp(self):
        """Contains timestamp component"""
        result = generate_error_id()
        # Format: err_YYYYMMDD_HHMMSS_uuid
        parts = result.split("_")
        assert len(parts) >= 3
        # Check date part looks like YYYYMMDD
        assert len(parts[1]) == 8
        assert parts[1].isdigit()


class TestRecordError:
    """record_error function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = record_error("Test error", project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_returns_id(self, temp_project):
        """Returns error ID"""
        result = record_error("Test error", project_path=str(temp_project))
        assert "id" in result
        assert result["id"].startswith("err_")

    def test_returns_status(self, temp_project):
        """Returns status"""
        result = record_error("Test error", project_path=str(temp_project))
        assert result["status"] == "recorded"

    def test_records_error_type(self, temp_project):
        """Records error type"""
        result = record_error(
            "Test error",
            error_type="type_error",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["error_type"] == "type_error"

    def test_records_stack_trace(self, temp_project):
        """Records stack trace"""
        result = record_error(
            "Test error",
            stack_trace="File test.py, line 1",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["stack_trace"] == "File test.py, line 1"

    def test_records_context(self, temp_project):
        """Records context"""
        result = record_error(
            "Test error",
            context="During API call",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["context"] == "During API call"

    def test_records_file_path(self, temp_project):
        """Records file path"""
        result = record_error(
            "Test error",
            file_path="/path/to/file.py",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["file_path"] == "/path/to/file.py"

    def test_records_five_whys(self, temp_project):
        """Records five whys as JSON"""
        whys = ["Why 1", "Why 2", "Why 3"]
        result = record_error(
            "Test error",
            five_whys=whys,
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["five_whys"] == whys

    def test_records_root_cause(self, temp_project):
        """Records root cause"""
        result = record_error(
            "Test error",
            root_cause="Missing null check",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["root_cause"] == "Missing null check"

    def test_records_solution(self, temp_project):
        """Records solution"""
        result = record_error(
            "Test error",
            solution="Add null check",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["solution"] == "Add null check"

    def test_records_prevention(self, temp_project):
        """Records prevention"""
        result = record_error(
            "Test error",
            prevention="Enable TypeScript strict mode",
            project_path=str(temp_project)
        )
        error = get_error(result["id"], str(temp_project))
        assert error["prevention"] == "Enable TypeScript strict mode"


class TestGetError:
    """get_error function tests"""

    def test_returns_none_for_nonexistent(self, temp_project):
        """Returns None for nonexistent error"""
        result = get_error("nonexistent_id", str(temp_project))
        assert result is None

    def test_returns_dict(self, temp_project):
        """Returns dictionary for existing error"""
        record = record_error("Test error", project_path=str(temp_project))
        result = get_error(record["id"], str(temp_project))
        assert isinstance(result, dict)

    def test_returns_error_message(self, temp_project):
        """Returns error message"""
        record = record_error("Test error message", project_path=str(temp_project))
        result = get_error(record["id"], str(temp_project))
        assert result["error_message"] == "Test error message"

    def test_parses_five_whys_json(self, temp_project):
        """Parses five whys JSON"""
        whys = ["Why 1", "Why 2"]
        record = record_error(
            "Test",
            five_whys=whys,
            project_path=str(temp_project)
        )
        result = get_error(record["id"], str(temp_project))
        assert result["five_whys"] == whys
        assert isinstance(result["five_whys"], list)


class TestListErrors:
    """list_errors function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        result = list_errors(project_path=str(temp_project))
        assert isinstance(result, list)

    def test_empty_for_no_errors(self, temp_project):
        """Empty list when no errors"""
        result = list_errors(project_path=str(temp_project))
        assert result == []

    def test_returns_recorded_errors(self, temp_project):
        """Returns recorded errors"""
        record_error("Error 1", project_path=str(temp_project))
        record_error("Error 2", project_path=str(temp_project))

        result = list_errors(project_path=str(temp_project))
        assert len(result) == 2

    def test_respects_limit(self, temp_project):
        """Respects limit parameter"""
        for i in range(5):
            record_error(f"Error {i}", project_path=str(temp_project))

        result = list_errors(limit=3, project_path=str(temp_project))
        assert len(result) == 3

    def test_filters_by_error_type(self, temp_project):
        """Filters by error type"""
        record_error("Error 1", error_type="type_a", project_path=str(temp_project))
        record_error("Error 2", error_type="type_b", project_path=str(temp_project))

        result = list_errors(error_type="type_a", project_path=str(temp_project))
        assert len(result) == 1
        assert result[0]["error_type"] == "type_a"


class TestResolveError:
    """resolve_error function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        record = record_error("Test error", project_path=str(temp_project))
        result = resolve_error(record["id"], project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_returns_resolved_status(self, temp_project):
        """Returns resolved status"""
        record = record_error("Test error", project_path=str(temp_project))
        result = resolve_error(record["id"], project_path=str(temp_project))
        assert result["status"] == "resolved"
        assert result["id"] == record["id"]

    def test_returns_not_found_for_invalid(self, temp_project):
        """Returns not_found for invalid ID"""
        result = resolve_error("invalid_id", project_path=str(temp_project))
        assert result["status"] == "not_found"

    def test_marks_effective(self, temp_project):
        """Marks resolution as effective"""
        record = record_error("Test error", project_path=str(temp_project))
        result = resolve_error(record["id"], effective=True, project_path=str(temp_project))
        assert result["effective"] is True

    def test_marks_ineffective(self, temp_project):
        """Marks resolution as ineffective"""
        record = record_error("Test error", project_path=str(temp_project))
        result = resolve_error(record["id"], effective=False, project_path=str(temp_project))
        assert result["effective"] is False

    def test_updates_solution(self, temp_project):
        """Updates solution on resolve"""
        record = record_error("Test error", project_path=str(temp_project))
        resolve_error(
            record["id"],
            solution="Fixed by updating config",
            project_path=str(temp_project)
        )
        error = get_error(record["id"], str(temp_project))
        assert error["solution"] == "Fixed by updating config"

    def test_updates_prevention(self, temp_project):
        """Updates prevention on resolve"""
        record = record_error("Test error", project_path=str(temp_project))
        resolve_error(
            record["id"],
            prevention="Add validation",
            project_path=str(temp_project)
        )
        error = get_error(record["id"], str(temp_project))
        assert error["prevention"] == "Add validation"

    def test_sets_resolved_at(self, temp_project):
        """Sets resolved_at timestamp"""
        record = record_error("Test error", project_path=str(temp_project))
        resolve_error(record["id"], project_path=str(temp_project))
        error = get_error(record["id"], str(temp_project))
        assert error["resolved_at"] is not None


class TestSearchErrorsByType:
    """search_errors_by_type function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        result = search_errors_by_type("type_error", project_path=str(temp_project))
        assert isinstance(result, list)

    def test_empty_for_no_matches(self, temp_project):
        """Empty list for no matches"""
        result = search_errors_by_type("nonexistent_type", project_path=str(temp_project))
        assert result == []

    def test_finds_matching_errors(self, temp_project):
        """Finds matching errors"""
        record_error("Error 1", error_type="import_error", project_path=str(temp_project))
        record_error("Error 2", error_type="import_error", project_path=str(temp_project))
        record_error("Error 3", error_type="type_error", project_path=str(temp_project))

        result = search_errors_by_type("import_error", project_path=str(temp_project))
        assert len(result) == 2

    def test_respects_limit(self, temp_project):
        """Respects limit parameter"""
        for i in range(5):
            record_error(f"Error {i}", error_type="test_type", project_path=str(temp_project))

        result = search_errors_by_type("test_type", limit=3, project_path=str(temp_project))
        assert len(result) == 3

    def test_returns_error_fields(self, temp_project):
        """Returns expected fields"""
        record_error(
            "Test error",
            error_type="test_type",
            solution="Test solution",
            prevention="Test prevention",
            project_path=str(temp_project)
        )

        result = search_errors_by_type("test_type", project_path=str(temp_project))
        assert len(result) == 1
        assert "id" in result[0]
        assert "error_message" in result[0]
        assert "solution" in result[0]
        assert "prevention" in result[0]


class TestGetErrorStats:
    """get_error_stats function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = get_error_stats(project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_empty_stats(self, temp_project):
        """Stats for empty database"""
        result = get_error_stats(project_path=str(temp_project))
        assert result["total"] == 0
        assert result["by_type"] == {}
        assert result["resolved"] == 0

    def test_counts_total(self, temp_project):
        """Counts total errors"""
        record_error("Error 1", project_path=str(temp_project))
        record_error("Error 2", project_path=str(temp_project))
        record_error("Error 3", project_path=str(temp_project))

        result = get_error_stats(project_path=str(temp_project))
        assert result["total"] == 3

    def test_groups_by_type(self, temp_project):
        """Groups errors by type"""
        record_error("Error 1", error_type="type_a", project_path=str(temp_project))
        record_error("Error 2", error_type="type_a", project_path=str(temp_project))
        record_error("Error 3", error_type="type_b", project_path=str(temp_project))

        result = get_error_stats(project_path=str(temp_project))
        assert result["by_type"]["type_a"] == 2
        assert result["by_type"]["type_b"] == 1

    def test_counts_resolved(self, temp_project):
        """Counts resolved errors"""
        record1 = record_error("Error 1", project_path=str(temp_project))
        record2 = record_error("Error 2", project_path=str(temp_project))
        record_error("Error 3", project_path=str(temp_project))

        resolve_error(record1["id"], project_path=str(temp_project))
        resolve_error(record2["id"], project_path=str(temp_project))

        result = get_error_stats(project_path=str(temp_project))
        assert result["resolved"] == 2

    def test_counts_effective(self, temp_project):
        """Counts effective resolutions"""
        record1 = record_error("Error 1", project_path=str(temp_project))
        record2 = record_error("Error 2", project_path=str(temp_project))

        resolve_error(record1["id"], effective=True, project_path=str(temp_project))
        resolve_error(record2["id"], effective=False, project_path=str(temp_project))

        result = get_error_stats(project_path=str(temp_project))
        assert result["effective"] == 1

    def test_respects_days_parameter(self, temp_project):
        """Respects days parameter"""
        record_error("Error 1", project_path=str(temp_project))

        result = get_error_stats(days=30, project_path=str(temp_project))
        assert result["period_days"] == 30

    def test_includes_period_days(self, temp_project):
        """Includes period_days in result"""
        result = get_error_stats(days=7, project_path=str(temp_project))
        assert result["period_days"] == 7


class TestListErrorsFilters:
    """Additional list_errors filter tests"""

    def test_filters_resolved_true(self, temp_project):
        """Filters for resolved errors"""
        record1 = record_error("Error 1", project_path=str(temp_project))
        record_error("Error 2", project_path=str(temp_project))

        resolve_error(record1["id"], project_path=str(temp_project))

        result = list_errors(resolved=True, project_path=str(temp_project))
        assert len(result) == 1
        assert result[0]["resolved_at"] is not None

    def test_filters_resolved_false(self, temp_project):
        """Filters for unresolved errors"""
        record1 = record_error("Error 1", project_path=str(temp_project))
        record_error("Error 2", project_path=str(temp_project))

        resolve_error(record1["id"], project_path=str(temp_project))

        result = list_errors(resolved=False, project_path=str(temp_project))
        assert len(result) == 1
        assert result[0]["resolved_at"] is None


class TestDbErrorsIntegration:
    """Integration tests for db errors"""

    def test_full_workflow(self, temp_project):
        """Full error recording workflow"""
        # Record error with all fields
        result = record_error(
            "NullPointerException",
            error_type="null_error",
            stack_trace="at main.py:10",
            context="User login",
            file_path="main.py",
            five_whys=["Why 1", "Why 2", "Why 3"],
            root_cause="Missing check",
            solution="Add check",
            prevention="Use Optional",
            project_path=str(temp_project)
        )

        assert result["status"] == "recorded"

        # Retrieve error
        error = get_error(result["id"], str(temp_project))
        assert error is not None
        assert error["error_message"] == "NullPointerException"
        assert error["error_type"] == "null_error"
        assert len(error["five_whys"]) == 3

        # List errors
        errors = list_errors(project_path=str(temp_project))
        assert len(errors) == 1


class TestDbErrorsEdgeCases:
    """Edge case tests for db errors"""

    def test_record_error_with_all_fields(self, temp_project):
        """Record error with all fields populated"""
        result = record_error(
            "Complete error",
            error_type="CompleteError",
            stack_trace="Full stack trace here",
            context="Full context description",
            file_path="/path/to/file.py",
            five_whys=["Why 1", "Why 2", "Why 3", "Why 4", "Why 5"],
            root_cause="Full root cause analysis",
            solution="Comprehensive solution",
            prevention="Detailed prevention plan",
            project_path=str(temp_project)
        )
        assert result["status"] == "recorded"

        error = get_error(result["id"], str(temp_project))
        assert error["error_type"] == "CompleteError"
        assert len(error["five_whys"]) == 5

    def test_list_errors_with_all_filters(self, temp_project):
        """List errors with all filters combined"""
        record1 = record_error("E1", error_type="TypeError", project_path=str(temp_project))
        resolve_error(record1["id"], project_path=str(temp_project))

        record_error("E2", error_type="TypeError", project_path=str(temp_project))
        record_error("E3", error_type="ValueError", project_path=str(temp_project))

        # Get resolved TypeErrors
        result = list_errors(
            days=7,
            error_type="TypeError",
            resolved=True,
            limit=10,
            project_path=str(temp_project)
        )
        assert len(result) == 1

    def test_resolve_with_both_solution_and_prevention(self, temp_project):
        """Resolve with both solution and prevention"""
        record = record_error("Test", project_path=str(temp_project))

        result = resolve_error(
            record["id"],
            effective=True,
            solution="Solution text",
            prevention="Prevention text",
            project_path=str(temp_project)
        )
        assert result["status"] == "resolved"

        error = get_error(record["id"], str(temp_project))
        assert error["solution"] == "Solution text"
        assert error["prevention"] == "Prevention text"

    def test_search_errors_returns_expected_fields(self, temp_project):
        """Search errors returns expected fields"""
        record_error(
            "Search test error",
            error_type="SearchType",
            solution="Search solution",
            prevention="Search prevention",
            project_path=str(temp_project)
        )

        results = search_errors_by_type("SearchType", project_path=str(temp_project))
        assert len(results) == 1
        assert "id" in results[0]
        assert "error_message" in results[0]
        assert "solution" in results[0]
        assert "prevention" in results[0]
        assert "resolved_at" in results[0]

    def test_error_stats_mttr_calculation(self, temp_project):
        """Error stats includes MTTR calculation"""
        record = record_error("MTTR test", project_path=str(temp_project))
        resolve_error(record["id"], project_path=str(temp_project))

        stats = get_error_stats(project_path=str(temp_project))
        # MTTR may be None if resolution is instant
        assert "mttr_minutes" in stats

    def test_error_stats_unknown_type(self, temp_project):
        """Error stats handles unknown (None) type"""
        record_error("Error without type", project_path=str(temp_project))

        stats = get_error_stats(project_path=str(temp_project))
        # None type should be mapped to "unknown"
        assert stats["total"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
