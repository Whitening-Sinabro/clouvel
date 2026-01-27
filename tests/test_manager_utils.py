# -*- coding: utf-8 -*-
"""Manager utils tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.utils import (
    _topological_sort,
    _group_by_phase,
    _analyze_context,
    RELEVANCE_THRESHOLD,
)


class TestTopologicalSort:
    """_topological_sort function tests"""

    def test_empty_list(self):
        """Sort empty list"""
        result = _topological_sort([])
        assert result == []

    def test_no_dependencies(self):
        """Sort items with no dependencies"""
        items = [
            {"id": "1", "phase": "Prepare", "action": "Task 1"},
            {"id": "2", "phase": "Design", "action": "Task 2"},
            {"id": "3", "phase": "Implement", "action": "Task 3"},
        ]
        result = _topological_sort(items)
        assert len(result) == 3

    def test_with_dependencies(self):
        """Sort items with dependencies"""
        items = [
            {"id": "1", "phase": "Prepare", "action": "Task 1"},
            {"id": "2", "phase": "Design", "action": "Task 2", "depends": ["1"]},
            {"id": "3", "phase": "Implement", "action": "Task 3", "depends": ["2"]},
        ]
        result = _topological_sort(items)
        # Task 1 should come before Task 2, Task 2 before Task 3
        ids = [item["id"] for item in result]
        assert ids.index("1") < ids.index("2")
        assert ids.index("2") < ids.index("3")

    def test_multiple_dependencies(self):
        """Sort items with multiple dependencies"""
        items = [
            {"id": "1", "phase": "Prepare", "action": "Task 1"},
            {"id": "2", "phase": "Prepare", "action": "Task 2"},
            {"id": "3", "phase": "Design", "action": "Task 3", "depends": ["1", "2"]},
        ]
        result = _topological_sort(items)
        ids = [item["id"] for item in result]
        # Task 3 should come after both Task 1 and Task 2
        assert ids.index("1") < ids.index("3")
        assert ids.index("2") < ids.index("3")


class TestGroupByPhase:
    """_group_by_phase function tests"""

    def test_empty_list(self):
        """Group empty list"""
        result = _group_by_phase([])
        assert result == {"Prepare": [], "Design": [], "Implement": [], "Verify": []}

    def test_group_items(self):
        """Group items by phase"""
        items = [
            {"id": "1", "phase": "Prepare", "action": "Task 1"},
            {"id": "2", "phase": "Design", "action": "Task 2"},
            {"id": "3", "phase": "Implement", "action": "Task 3"},
            {"id": "4", "phase": "Verify", "action": "Task 4"},
        ]
        result = _group_by_phase(items)
        assert len(result["Prepare"]) == 1
        assert len(result["Design"]) == 1
        assert len(result["Implement"]) == 1
        assert len(result["Verify"]) == 1

    def test_multiple_items_per_phase(self):
        """Multiple items in same phase"""
        items = [
            {"id": "1", "phase": "Design", "action": "Task 1"},
            {"id": "2", "phase": "Design", "action": "Task 2"},
            {"id": "3", "phase": "Design", "action": "Task 3"},
        ]
        result = _group_by_phase(items)
        assert len(result["Design"]) == 3

    def test_unknown_phase_goes_to_verify(self):
        """Unknown phase items go to Verify"""
        items = [
            {"id": "1", "phase": "Unknown", "action": "Task 1"},
        ]
        result = _group_by_phase(items)
        assert len(result["Verify"]) == 1

    def test_missing_phase_goes_to_verify(self):
        """Items without phase go to Verify"""
        items = [
            {"id": "1", "action": "Task 1"},
        ]
        result = _group_by_phase(items)
        assert len(result["Verify"]) == 1


class TestAnalyzeContext:
    """_analyze_context function tests"""

    def test_detect_auth_topic(self):
        """Detect auth topic"""
        result = _analyze_context("Implement user login with JWT authentication")
        assert "auth" in result

    def test_detect_payment_topic(self):
        """Detect payment topic"""
        result = _analyze_context("Add Stripe payment integration for subscriptions")
        assert "payment" in result

    def test_detect_api_topic(self):
        """Detect API topic"""
        result = _analyze_context("Create REST API endpoints for user management")
        assert "api" in result

    def test_detect_security_topic(self):
        """Detect security topic"""
        result = _analyze_context("Fix XSS vulnerability in user input handling")
        assert "security" in result

    def test_detect_performance_topic(self):
        """Detect performance topic"""
        result = _analyze_context("Optimize database queries for better performance")
        assert "performance" in result

    def test_detect_error_topic(self):
        """Detect error topic"""
        result = _analyze_context("Fix crash when user submits invalid data")
        assert "error" in result

    def test_detect_database_topic(self):
        """Detect database topic"""
        result = _analyze_context("Run database migration for new schema")
        assert "database" in result

    def test_detect_feature_topic(self):
        """Detect feature topic"""
        result = _analyze_context("Implement new feature for file upload")
        assert "feature" in result

    def test_detect_launch_topic(self):
        """Detect launch topic"""
        result = _analyze_context("Deploy application to production")
        assert "launch" in result

    def test_detect_korean_keywords(self):
        """Detect Korean keywords"""
        result = _analyze_context("사용자 로그인 인증 기능 구현")
        assert "auth" in result

    def test_detect_multiple_topics(self):
        """Detect multiple topics"""
        result = _analyze_context("Implement secure API endpoints with authentication and performance optimization")
        assert len(result) >= 2

    def test_empty_context(self):
        """Empty context returns list (may include default topics)"""
        result = _analyze_context("")
        # May include default topics based on implementation
        assert isinstance(result, list)

    def test_unrelated_context(self):
        """Unrelated context may return few topics"""
        result = _analyze_context("Hello world")
        # Should return empty or very few topics
        assert len(result) <= 1


class TestRelevanceThreshold:
    """RELEVANCE_THRESHOLD constant tests"""

    def test_threshold_value(self):
        """Threshold is reasonable value"""
        assert RELEVANCE_THRESHOLD > 0
        assert RELEVANCE_THRESHOLD < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
