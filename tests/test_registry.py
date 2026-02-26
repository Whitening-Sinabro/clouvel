# -*- coding: utf-8 -*-
"""Registry module tests (v6.0: all tools visible)"""

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
        """v6.0: 21 CORE tools (10 original + 10 formerly PRO + audit_rules)."""
        core = [k for k, v in TOOL_TIERS.items() if v == ToolTier.CORE]
        assert len(core) == 21, f"Expected 21 core tools, got {len(core)}: {core}"

    def test_no_pro_tools(self):
        """v6.0: No PRO tier tools — all moved to CORE."""
        pro = [k for k, v in TOOL_TIERS.items() if v == ToolTier.PRO]
        assert len(pro) == 0, f"Expected 0 pro tools, got {len(pro)}: {pro}"

    def test_core_tools_list(self):
        expected_core = {
            "can_code", "start", "save_prd", "error_check", "error_record",
            "context_save", "context_load", "quick_perspectives", "gate",
            "license_status",
            # Formerly PRO:
            "error_learn", "memory_status", "memory_search",
            "memory_global_search", "drift_check", "record_decision",
            "search_knowledge", "plan", "meeting", "ship",
            "audit_rules",
        }
        actual_core = {k for k, v in TOOL_TIERS.items() if v == ToolTier.CORE}
        assert actual_core == expected_core

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

    def test_all_core_tools_visible(self, mock_tools):
        """v6.0: All CORE tools visible regardless of tier."""
        result = filter_tools_by_tier(mock_tools, "free")
        names = [t.name for t in result]
        assert "can_code" in names
        assert "gate" in names
        assert "error_learn" in names  # v6.0: now CORE
        assert "plan" in names  # v6.0: now CORE
        assert "scan_docs" not in names  # Still INTERNAL

    def test_pro_tier_shows_same(self, mock_tools):
        result = filter_tools_by_tier(mock_tools, "pro")
        names = [t.name for t in result]
        assert "can_code" in names
        assert "gate" in names
        assert "error_learn" in names
        assert "plan" in names
        assert "scan_docs" not in names  # INTERNAL

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
    def test_always_allowed(self):
        """v6.0: All tools allowed for all tiers."""
        for tier in ["pro", "first", "additional", "free"]:
            assert is_tool_allowed("can_code", tier) is True
            assert is_tool_allowed("error_learn", tier) is True
            assert is_tool_allowed("meeting", tier) is True
            assert is_tool_allowed("scan_docs", tier) is True


# ── Stats Tests ──


class TestTierStats:
    def test_stats_sum(self):
        stats = get_tier_stats()
        assert stats["core"] == 21
        assert stats.get("pro", 0) == 0
        assert stats["deprecated"] >= 4
        total = sum(stats.values())
        assert total == len(TOOL_TIERS)
