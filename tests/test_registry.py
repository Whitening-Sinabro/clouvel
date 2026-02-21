# -*- coding: utf-8 -*-
"""Registry module tests (v5.0 tool visibility filtering)"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.registry import (
    ToolTier,
    TOOL_TIERS,
    TOOL_REDIRECTS,
    get_tool_tier,
    filter_tools_by_tier,
    get_redirect_message,
    is_tool_allowed,
    get_tier_stats,
)


# ── Tier Mapping Tests ──


class TestToolTiers:
    def test_core_tools_count(self):
        core = [k for k, v in TOOL_TIERS.items() if v == ToolTier.CORE]
        assert len(core) == 10, f"Expected 10 core tools, got {len(core)}: {core}"

    def test_pro_tools_count(self):
        pro = [k for k, v in TOOL_TIERS.items() if v == ToolTier.PRO]
        assert len(pro) == 10, f"Expected 10 pro tools, got {len(pro)}: {pro}"

    def test_core_tools_list(self):
        expected_core = {
            "can_code", "start", "save_prd", "error_check", "error_record",
            "context_save", "context_load", "quick_perspectives", "gate",
            "license_status",
        }
        actual_core = {k for k, v in TOOL_TIERS.items() if v == ToolTier.CORE}
        assert actual_core == expected_core

    def test_pro_tools_list(self):
        expected_pro = {
            "error_learn", "memory_status", "memory_search",
            "memory_global_search", "drift_check", "record_decision",
            "search_knowledge", "plan", "meeting", "ship",
        }
        actual_pro = {k for k, v in TOOL_TIERS.items() if v == ToolTier.PRO}
        assert actual_pro == expected_pro

    def test_deprecated_tools(self):
        deprecated = {k for k, v in TOOL_TIERS.items() if v == ToolTier.DEPRECATED}
        assert "spawn_explore" in deprecated
        assert "hook_design" in deprecated

    def test_unmapped_defaults_to_internal(self):
        assert get_tool_tier("nonexistent_tool_xyz") == ToolTier.INTERNAL


# ── Filter Tests ──


class TestFilterToolsByTier:
    @pytest.fixture
    def mock_tools(self):
        """Create mock Tool objects."""
        tools = []
        for name in ["can_code", "gate", "error_learn", "plan", "scan_docs", "spawn_explore"]:
            t = MagicMock()
            t.name = name
            tools.append(t)
        return tools

    def test_free_tier_shows_core_only(self, mock_tools):
        result = filter_tools_by_tier(mock_tools, "free")
        names = [t.name for t in result]
        assert "can_code" in names
        assert "gate" in names
        assert "error_learn" not in names
        assert "plan" not in names
        assert "scan_docs" not in names

    def test_pro_tier_shows_core_and_pro(self, mock_tools):
        result = filter_tools_by_tier(mock_tools, "pro")
        names = [t.name for t in result]
        assert "can_code" in names
        assert "gate" in names
        assert "error_learn" in names
        assert "plan" in names
        assert "scan_docs" not in names  # INTERNAL

    def test_first_tier_shows_core_only(self, mock_tools):
        """'first' tier is treated same as 'free' — no Pro tools."""
        result = filter_tools_by_tier(mock_tools, "first")
        names = [t.name for t in result]
        assert "can_code" in names
        assert "error_learn" not in names
        assert "plan" not in names

    def test_internal_tools_never_shown(self, mock_tools):
        for tier in ["free", "pro"]:
            result = filter_tools_by_tier(mock_tools, tier)
            names = [t.name for t in result]
            assert "scan_docs" not in names

    def test_deprecated_tools_never_shown(self, mock_tools):
        for tier in ["free", "pro"]:
            result = filter_tools_by_tier(mock_tools, tier)
            names = [t.name for t in result]
            assert "spawn_explore" not in names


# ── Redirect Tests ──


class TestRedirects:
    def test_deprecated_tool_has_redirect(self):
        msg = get_redirect_message("spawn_explore")
        assert msg is not None
        assert "Task tool" in msg

    def test_active_tool_has_no_redirect(self):
        assert get_redirect_message("can_code") is None
        assert get_redirect_message("error_learn") is None

    def test_all_deprecated_have_redirects(self):
        deprecated = {k for k, v in TOOL_TIERS.items() if v == ToolTier.DEPRECATED}
        for name in deprecated:
            assert get_redirect_message(name) is not None, f"{name} missing redirect"


# ── Access Control Tests ──


class TestIsToolAllowed:
    def test_core_allowed_for_all(self):
        for tier in ["pro", "first", "additional", "free"]:
            assert is_tool_allowed("can_code", tier) is True

    def test_pro_allowed_for_pro(self):
        assert is_tool_allowed("error_learn", "pro") is True

    def test_pro_blocked_for_first(self):
        """'first' tier cannot access Pro tools — only 'pro' can."""
        assert is_tool_allowed("error_learn", "first") is False

    def test_pro_blocked_for_free(self):
        assert is_tool_allowed("error_learn", "free") is False

    def test_internal_always_allowed(self):
        """Internal tools are callable (backward compat) even if not listed."""
        assert is_tool_allowed("scan_docs", "free") is True
        assert is_tool_allowed("scan_docs", "additional") is True


# ── Stats Tests ──


class TestTierStats:
    def test_stats_sum(self):
        stats = get_tier_stats()
        assert stats["core"] == 10
        assert stats["pro"] == 10
        assert stats["deprecated"] >= 4
        total = sum(stats.values())
        assert total == len(TOOL_TIERS)
