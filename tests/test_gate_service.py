# -*- coding: utf-8 -*-
"""Tests for services.gate — feature gating logic."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.services.gate import (
    require_error_tools,
    require_kb_access,
    append_free_nudge,
)
from mcp.types import TextContent


class TestRequireErrorTools:
    def test_available_returns_none(self):
        """When error tools are available, no block message."""
        # In dev environment, error tools are imported
        result = require_error_tools("error_record")
        assert result is None  # tools available in dev

    def test_message_varies_by_feature(self):
        """Different features get different messages."""
        with patch("clouvel.services.gate._HAS_ERROR_TOOLS", False):
            error_msg = require_error_tools("error_record")
            memory_msg = require_error_tools("memory_status")
            cross_msg = require_error_tools("memory_promote")
            domain_msg = require_error_tools("set_project_domain")

            assert "Error Learning" in error_msg[0].text
            assert "Regression Memory" in memory_msg[0].text
            assert "Cross-project" in cross_msg[0].text
            assert "Domain scoping" in domain_msg[0].text


class TestRequireKbAccess:
    def test_developer_allowed(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            result = require_kb_access(".")
            assert result is None  # No block

    def test_expired_trial_blocked(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.quotas.start_kb_trial"), \
             patch("clouvel.licensing.quotas.is_kb_trial_active", return_value=False):
            result = require_kb_access(".")
            assert result is not None
            assert isinstance(result, list)
            assert "KB Write Locked" in result[0].text


class TestAppendFreeNudge:
    def test_pro_user_no_nudge(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            original = [TextContent(type="text", text="result")]
            result = append_free_nudge(original, ".", "error_record")
            assert "Pro" not in result[0].text

    def test_free_user_gets_nudge(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            original = [TextContent(type="text", text="result")]
            result = append_free_nudge(original, ".", "error_record")
            assert "Pro" in result[0].text
            assert "NEVER/ALWAYS" in result[0].text

    def test_unknown_tool_no_nudge(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            original = [TextContent(type="text", text="result")]
            result = append_free_nudge(original, ".", "unknown_tool")
            assert result[0].text == "result"
