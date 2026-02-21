# -*- coding: utf-8 -*-
"""call_tool integration tests — deprecated redirect, defense-in-depth, ghost data."""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.registry import get_redirect_message, is_tool_allowed
from clouvel.server import (
    _is_pro,
    _get_list_tools_tier,
    _get_call_tool_tier,
    _apply_free_error_limit,
    _append_ghost_data,
    FREE_ERROR_LIMIT,
)
from mcp.types import TextContent


# ── Deprecated Redirect Tests ──


class TestDeprecatedRedirect:
    def test_spawn_explore_redirects(self):
        msg = get_redirect_message("spawn_explore")
        assert msg is not None
        assert "Task tool" in msg

    def test_hook_design_redirects(self):
        msg = get_redirect_message("hook_design")
        assert msg is not None
        assert "hooks" in msg.lower()

    def test_active_tool_no_redirect(self):
        assert get_redirect_message("can_code") is None
        assert get_redirect_message("error_check") is None
        assert get_redirect_message("meeting") is None


# ── Defense-in-Depth (is_tool_allowed) Tests ──


class TestDefenseInDepth:
    def test_core_tool_always_allowed(self):
        """Core tools pass for any tier."""
        for tier in ["pro", "free", "first", "unknown"]:
            assert is_tool_allowed("can_code", tier) is True
            assert is_tool_allowed("gate", tier) is True
            assert is_tool_allowed("error_check", tier) is True

    def test_pro_tool_only_pro_allowed(self):
        """Pro tools require exactly 'pro' tier."""
        assert is_tool_allowed("error_learn", "pro") is True
        assert is_tool_allowed("meeting", "pro") is True
        assert is_tool_allowed("ship", "pro") is True

    def test_pro_tool_blocked_for_free(self):
        assert is_tool_allowed("error_learn", "free") is False
        assert is_tool_allowed("meeting", "free") is False

    def test_pro_tool_blocked_for_first(self):
        """'first' is NOT pro — Pro tools blocked."""
        assert is_tool_allowed("error_learn", "first") is False
        assert is_tool_allowed("ship", "first") is False

    def test_internal_tool_always_allowed(self):
        """Internal tools pass (backward compat)."""
        assert is_tool_allowed("scan_docs", "free") is True
        assert is_tool_allowed("init_rules", "free") is True


# ── Tier Detection Tests ──


class TestTierDetection:
    def test_is_pro_developer(self):
        with patch("clouvel.license_common.is_developer", return_value=True):
            assert _is_pro("") is True

    def test_is_pro_license(self):
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value={"tier": "personal"}):
            assert _is_pro("") is True

    def test_is_pro_trial(self):
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=True):
            assert _is_pro("") is True

    def test_is_not_pro_free_user(self):
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=False):
            assert _is_pro("") is False

    def test_list_tools_tier_free_for_normal_user(self):
        """Normal user (no license, no trial) gets 'free' tier."""
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=False):
            assert _get_list_tools_tier() == "free"

    def test_list_tools_tier_pro_for_licensed(self):
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value={"tier": "personal"}):
            assert _get_list_tools_tier() == "pro"

    def test_call_tool_tier_matches_is_pro(self):
        """_get_call_tool_tier uses _is_pro internally — should be consistent."""
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=False):
            assert _get_call_tool_tier("/some/path") == "free"

        with patch("clouvel.license_common.is_developer", return_value=True):
            assert _get_call_tool_tier("/some/path") == "pro"


# ── Ghost Data Tests ──


class TestGhostData:
    def test_ghost_data_appended_for_free_user(self):
        """Free users get Pro teaser appended to error tools."""
        result = [TextContent(type="text", text="Error recorded.")]
        with patch("clouvel.server._is_pro", return_value=False):
            output = _append_ghost_data(result, "/path", "error_record")
            assert "Pro" in output[0].text
            assert 'license_status(action="trial")' in output[0].text

    def test_ghost_data_not_appended_for_pro_user(self):
        """Pro users don't see teasers."""
        result = [TextContent(type="text", text="Error recorded.")]
        with patch("clouvel.server._is_pro", return_value=True):
            output = _append_ghost_data(result, "/path", "error_record")
            assert output[0].text == "Error recorded."

    def test_ghost_data_only_for_error_tools(self):
        """Ghost data only for error_record and error_check."""
        result = [TextContent(type="text", text="Some output")]
        with patch("clouvel.server._is_pro", return_value=False):
            output = _append_ghost_data(result, "/path", "gate")
            assert output[0].text == "Some output"

    def test_ghost_data_empty_result_safe(self):
        with patch("clouvel.server._is_pro", return_value=False):
            output = _append_ghost_data([], "/path", "error_record")
            assert output == []


# ── Free Error Limit Tests ──


class TestFreeErrorLimit:
    def test_nudge_when_over_limit(self):
        temp_dir = tempfile.mkdtemp()
        try:
            errors_dir = Path(temp_dir) / ".claude" / "errors"
            errors_dir.mkdir(parents=True)
            log_file = errors_dir / "error_log.jsonl"
            log_file.write_text("\n".join([f'{{"id": {i}}}' for i in range(10)]))

            result = [TextContent(type="text", text="Warning")]
            output = _apply_free_error_limit(result, temp_dir)

            assert "5 of 10" in output[0].text
            assert "Free limit" in output[0].text
            assert 'license_status(action="trial")' in output[0].text
        finally:
            shutil.rmtree(temp_dir)

    def test_no_nudge_under_limit(self):
        temp_dir = tempfile.mkdtemp()
        try:
            errors_dir = Path(temp_dir) / ".claude" / "errors"
            errors_dir.mkdir(parents=True)
            log_file = errors_dir / "error_log.jsonl"
            log_file.write_text("\n".join([f'{{"id": {i}}}' for i in range(3)]))

            result = [TextContent(type="text", text="Warning")]
            output = _apply_free_error_limit(result, temp_dir)
            assert "Free limit" not in output[0].text
        finally:
            shutil.rmtree(temp_dir)

    def test_no_error_log_no_nudge(self):
        result = [TextContent(type="text", text="No risk.")]
        output = _apply_free_error_limit(result, "/nonexistent/path")
        assert "Free limit" not in output[0].text


# ── CTA Consistency Tests ──


class TestCTAConsistency:
    """Verify all Pro-related messages use the unified CTA."""

    def test_ghost_data_cta(self):
        result = [TextContent(type="text", text="test")]
        with patch("clouvel.server._is_pro", return_value=False):
            output = _append_ghost_data(result, "/p", "error_record")
            assert 'license_status(action="trial")' in output[0].text

    def test_error_limit_cta(self):
        temp_dir = tempfile.mkdtemp()
        try:
            errors_dir = Path(temp_dir) / ".claude" / "errors"
            errors_dir.mkdir(parents=True)
            (errors_dir / "error_log.jsonl").write_text(
                "\n".join([f'{{"id": {i}}}' for i in range(10)])
            )
            result = [TextContent(type="text", text="test")]
            output = _apply_free_error_limit(result, temp_dir)
            assert 'license_status(action="trial")' in output[0].text
            assert "polar.sh" not in output[0].text
        finally:
            shutil.rmtree(temp_dir)
