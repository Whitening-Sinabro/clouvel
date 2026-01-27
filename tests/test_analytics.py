# -*- coding: utf-8 -*-
"""Analytics module tests"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.analytics import (
    get_analytics_path,
    load_analytics,
    save_analytics,
    log_tool_call,
    get_stats,
    format_stats,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestGetAnalyticsPath:
    """get_analytics_path function tests"""

    def test_returns_path(self, temp_project):
        """Returns Path object"""
        result = get_analytics_path(str(temp_project))
        assert isinstance(result, Path)

    def test_path_includes_clouvel(self, temp_project):
        """Path includes .clouvel directory"""
        result = get_analytics_path(str(temp_project))
        assert ".clouvel" in str(result)

    def test_path_ends_with_json(self, temp_project):
        """Path ends with analytics.json"""
        result = get_analytics_path(str(temp_project))
        assert result.name == "analytics.json"

    def test_creates_clouvel_dir(self, temp_project):
        """Creates .clouvel directory"""
        clouvel_dir = temp_project / ".clouvel"
        assert not clouvel_dir.exists()

        get_analytics_path(str(temp_project))
        assert clouvel_dir.exists()


class TestLoadAnalytics:
    """load_analytics function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = load_analytics(str(temp_project))
        assert isinstance(result, dict)

    def test_default_has_events(self, temp_project):
        """Default has empty events list"""
        result = load_analytics(str(temp_project))
        assert "events" in result
        assert result["events"] == []

    def test_default_has_version(self, temp_project):
        """Default has version field"""
        result = load_analytics(str(temp_project))
        assert "version" in result

    def test_loads_existing_data(self, temp_project):
        """Loads existing analytics data"""
        clouvel_dir = temp_project / ".clouvel"
        clouvel_dir.mkdir()
        analytics_file = clouvel_dir / "analytics.json"

        test_data = {
            "events": [{"tool": "can_code", "ts": "2024-01-01T00:00:00"}],
            "version": "1.0"
        }
        analytics_file.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_analytics(str(temp_project))
        assert len(result["events"]) == 1
        assert result["events"][0]["tool"] == "can_code"

    def test_handles_invalid_json(self, temp_project):
        """Returns default for invalid JSON"""
        clouvel_dir = temp_project / ".clouvel"
        clouvel_dir.mkdir()
        analytics_file = clouvel_dir / "analytics.json"
        analytics_file.write_text("invalid json{{{", encoding="utf-8")

        result = load_analytics(str(temp_project))
        assert result["events"] == []


class TestSaveAnalytics:
    """save_analytics function tests"""

    def test_saves_data(self, temp_project):
        """Saves data to file"""
        test_data = {
            "events": [{"tool": "can_code", "ts": "2024-01-01T00:00:00"}],
            "version": "1.0"
        }
        save_analytics(test_data, str(temp_project))

        analytics_file = temp_project / ".clouvel" / "analytics.json"
        assert analytics_file.exists()

        loaded = json.loads(analytics_file.read_text(encoding="utf-8"))
        assert loaded["events"][0]["tool"] == "can_code"

    def test_overwrites_existing(self, temp_project):
        """Overwrites existing file"""
        save_analytics({"events": [{"tool": "old"}], "version": "1.0"}, str(temp_project))
        save_analytics({"events": [{"tool": "new"}], "version": "1.0"}, str(temp_project))

        result = load_analytics(str(temp_project))
        assert result["events"][0]["tool"] == "new"


class TestLogToolCall:
    """log_tool_call function tests"""

    def test_logs_success(self, temp_project):
        """Logs successful tool call"""
        log_tool_call("can_code", success=True, project_path=str(temp_project))

        result = load_analytics(str(temp_project))
        assert len(result["events"]) == 1
        assert result["events"][0]["tool"] == "can_code"
        assert result["events"][0]["success"] is True

    def test_logs_failure(self, temp_project):
        """Logs failed tool call"""
        log_tool_call("can_code", success=False, project_path=str(temp_project))

        result = load_analytics(str(temp_project))
        assert result["events"][0]["success"] is False

    def test_multiple_logs(self, temp_project):
        """Multiple log calls accumulate"""
        log_tool_call("can_code", project_path=str(temp_project))
        log_tool_call("scan_docs", project_path=str(temp_project))
        log_tool_call("init_docs", project_path=str(temp_project))

        result = load_analytics(str(temp_project))
        assert len(result["events"]) == 3

    def test_includes_timestamp(self, temp_project):
        """Log includes timestamp"""
        log_tool_call("can_code", project_path=str(temp_project))

        result = load_analytics(str(temp_project))
        assert "ts" in result["events"][0]
        # Should be ISO format
        datetime.fromisoformat(result["events"][0]["ts"])

    def test_limits_to_1000_events(self, temp_project):
        """Limits events to 1000"""
        # Pre-fill with 1005 events
        data = {
            "events": [{"tool": f"tool_{i}", "ts": datetime.now().isoformat(), "success": True}
                       for i in range(1005)],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))

        # Add one more
        log_tool_call("new_tool", project_path=str(temp_project))

        result = load_analytics(str(temp_project))
        assert len(result["events"]) == 1000


class TestGetStats:
    """get_stats function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = get_stats(str(temp_project))
        assert isinstance(result, dict)

    def test_empty_stats(self, temp_project):
        """Stats for empty analytics"""
        result = get_stats(str(temp_project))
        assert result["total_calls"] == 0
        assert result["by_tool"] == {}
        assert result["success_rate"] == 0

    def test_counts_total_calls(self, temp_project):
        """Counts total calls"""
        log_tool_call("can_code", project_path=str(temp_project))
        log_tool_call("scan_docs", project_path=str(temp_project))

        result = get_stats(str(temp_project))
        assert result["total_calls"] == 2

    def test_groups_by_tool(self, temp_project):
        """Groups calls by tool"""
        log_tool_call("can_code", project_path=str(temp_project))
        log_tool_call("can_code", project_path=str(temp_project))
        log_tool_call("scan_docs", project_path=str(temp_project))

        result = get_stats(str(temp_project))
        assert result["by_tool"]["can_code"] == 2
        assert result["by_tool"]["scan_docs"] == 1

    def test_calculates_success_rate(self, temp_project):
        """Calculates success rate"""
        log_tool_call("tool1", success=True, project_path=str(temp_project))
        log_tool_call("tool2", success=True, project_path=str(temp_project))
        log_tool_call("tool3", success=False, project_path=str(temp_project))

        result = get_stats(str(temp_project))
        # 2 out of 3 = ~66.67%
        assert 65 <= result["success_rate"] <= 68

    def test_filters_by_days(self, temp_project):
        """Filters by days parameter"""
        # Add old event
        old_date = (datetime.now() - timedelta(days=60)).isoformat()
        data = {
            "events": [
                {"tool": "old_tool", "ts": old_date, "success": True},
            ],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))

        # Add recent event
        log_tool_call("new_tool", project_path=str(temp_project))

        # Get stats for last 30 days
        result = get_stats(str(temp_project), days=30)

        # Should only count recent event
        assert result["total_calls"] == 1
        assert "old_tool" not in result["by_tool"]

    def test_groups_by_date(self, temp_project):
        """Groups calls by date"""
        log_tool_call("tool1", project_path=str(temp_project))

        result = get_stats(str(temp_project))
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result["by_date"]


class TestFormatStats:
    """format_stats function tests"""

    def test_returns_string(self):
        """Returns string"""
        stats = {
            "total_calls": 0,
            "by_tool": {},
            "by_date": {},
            "success_rate": 0,
            "period_days": 30
        }
        result = format_stats(stats)
        assert isinstance(result, str)

    def test_includes_title(self):
        """Includes title with period"""
        stats = {
            "total_calls": 10,
            "by_tool": {"can_code": 5},
            "by_date": {},
            "success_rate": 100,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "30" in result
        assert "Clouvel" in result

    def test_includes_total_calls(self):
        """Includes total calls count"""
        stats = {
            "total_calls": 42,
            "by_tool": {},
            "by_date": {},
            "success_rate": 100,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "42" in result

    def test_includes_success_rate(self):
        """Includes success rate"""
        stats = {
            "total_calls": 10,
            "by_tool": {},
            "by_date": {},
            "success_rate": 85.5,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "85.5" in result

    def test_includes_tool_breakdown(self):
        """Includes tool breakdown table"""
        stats = {
            "total_calls": 10,
            "by_tool": {"can_code": 5, "scan_docs": 5},
            "by_date": {},
            "success_rate": 100,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "can_code" in result
        assert "scan_docs" in result

    def test_includes_date_breakdown(self):
        """Includes date breakdown"""
        today = datetime.now().strftime("%Y-%m-%d")
        stats = {
            "total_calls": 10,
            "by_tool": {"can_code": 10},
            "by_date": {today: 10},
            "success_rate": 100,
            "period_days": 30
        }
        result = format_stats(stats)
        assert today in result

    def test_empty_stats_message(self):
        """Shows message for empty stats"""
        stats = {
            "total_calls": 0,
            "by_tool": {},
            "by_date": {},
            "success_rate": 0,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "기록된 사용량이 없습니다" in result

    def test_bar_chart(self):
        """Includes bar chart characters"""
        today = datetime.now().strftime("%Y-%m-%d")
        stats = {
            "total_calls": 10,
            "by_tool": {},
            "by_date": {today: 5},
            "success_rate": 100,
            "period_days": 30
        }
        result = format_stats(stats)
        assert "█" in result


class TestGetStatsEdgeCases:
    """Edge cases for get_stats"""

    def test_invalid_timestamp_format(self, temp_project):
        """Handles invalid timestamp format"""
        data = {
            "events": [
                {"tool": "test", "ts": "not-a-timestamp", "success": True}
            ],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))

        result = get_stats(str(temp_project))
        # Should not crash, invalid events are filtered
        assert "total_calls" in result

    def test_missing_ts_field(self, temp_project):
        """Handles missing ts field"""
        data = {
            "events": [
                {"tool": "test", "success": True}  # No ts field
            ],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))

        result = get_stats(str(temp_project))
        assert "total_calls" in result

    def test_missing_tool_field(self, temp_project):
        """Handles missing tool field"""
        data = {
            "events": [
                {"ts": datetime.now().isoformat(), "success": True}  # No tool field
            ],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))

        result = get_stats(str(temp_project))
        # Uses "unknown" for missing tool
        if result["total_calls"] > 0:
            assert "unknown" in result["by_tool"] or len(result["by_tool"]) == 0


class TestAnalyticsIntegration:
    """Integration tests for analytics"""

    def test_full_workflow(self, temp_project):
        """Full analytics workflow"""
        # Log some calls
        log_tool_call("can_code", success=True, project_path=str(temp_project))
        log_tool_call("scan_docs", success=True, project_path=str(temp_project))
        log_tool_call("init_docs", success=False, project_path=str(temp_project))

        # Get stats
        stats = get_stats(str(temp_project))

        assert stats["total_calls"] == 3
        assert len(stats["by_tool"]) == 3
        assert stats["success_rate"] > 0

    def test_persistence(self, temp_project):
        """Data persists across loads"""
        log_tool_call("tool1", project_path=str(temp_project))

        # Simulate new session
        result = load_analytics(str(temp_project))
        assert len(result["events"]) == 1

    def test_stats_to_formatted(self, temp_project):
        """Stats can be formatted"""
        log_tool_call("can_code", project_path=str(temp_project))
        log_tool_call("scan_docs", project_path=str(temp_project))

        stats = get_stats(str(temp_project))
        formatted = format_stats(stats)

        assert isinstance(formatted, str)
        assert "can_code" in formatted or "2" in formatted


class TestAnalyticsNonePath:
    """Tests for analytics with None project_path"""

    def test_get_analytics_path_no_project(self, temp_project):
        """get_analytics_path with no project uses cwd"""
        import os
        orig_cwd = os.getcwd()
        try:
            os.chdir(str(temp_project))
            result = get_analytics_path()
            assert ".clouvel" in str(result)
        finally:
            os.chdir(orig_cwd)


class TestStatsDateExceptions:
    """Tests for date exception handling in get_stats"""

    def test_missing_ts_field(self, temp_project):
        """Stats handles missing ts field in event"""
        data = {
            "events": [{"tool": "test_tool", "success": True}],  # No ts
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))
        result = get_stats(str(temp_project))
        # Should complete without error
        assert "total_calls" in result

    def test_malformed_date_in_by_date(self, temp_project):
        """Stats handles malformed date when building by_date"""
        data = {
            "events": [
                {"tool": "test", "ts": "2024-01-01T00:00:00", "success": True},
                {"tool": "test2", "success": True},  # No ts, will trigger exception
            ],
            "version": "1.0"
        }
        save_analytics(data, str(temp_project))
        result = get_stats(str(temp_project))
        # Should complete without error
        assert "by_date" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
