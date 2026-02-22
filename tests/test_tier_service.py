# -*- coding: utf-8 -*-
"""Tests for services.tier — unified tier resolution."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.services.tier import Tier, resolve_tier, is_pro, can_use_pro, get_tool_filter_tier


class TestTierEnum:
    def test_pro_equivalent(self):
        assert Tier.PRO.is_pro_equivalent() is True
        assert Tier.TRIAL.is_pro_equivalent() is True
        assert Tier.DEV.is_pro_equivalent() is True
        assert Tier.FIRST.is_pro_equivalent() is False
        assert Tier.FREE.is_pro_equivalent() is False

    def test_first_or_above(self):
        assert Tier.PRO.is_first_or_above() is True
        assert Tier.TRIAL.is_first_or_above() is True
        assert Tier.DEV.is_first_or_above() is True
        assert Tier.FIRST.is_first_or_above() is True
        assert Tier.FREE.is_first_or_above() is False


class TestResolveTier:
    def test_developer_returns_dev(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            assert resolve_tier() == Tier.DEV

    def test_license_returns_pro(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value={"tier": "personal"}):
            assert resolve_tier() == Tier.PRO

    def test_trial_returns_trial(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=True):
            assert resolve_tier() == Tier.TRIAL

    def test_first_project_returns_first(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project.get_project_tier", return_value="first"):
            assert resolve_tier("/some/path") == Tier.FIRST

    def test_free_user_returns_free(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project.get_project_tier", return_value="free"):
            assert resolve_tier("/some/path") == Tier.FREE

    def test_free_without_project_path(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            assert resolve_tier() == Tier.FREE

    def test_priority_dev_over_license(self):
        """Developer mode wins even if license exists."""
        with patch("clouvel.licensing.core.is_developer", return_value=True), \
             patch("clouvel.licensing.validation.load_license_cache", return_value={"tier": "personal"}):
            assert resolve_tier() == Tier.DEV

    def test_priority_license_over_trial(self):
        """License wins over trial."""
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value={"tier": "personal"}), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=True):
            assert resolve_tier() == Tier.PRO


class TestConvenienceFunctions:
    def test_is_pro_for_developer(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            assert is_pro() is True

    def test_is_pro_for_first_project(self):
        """First project is NOT pro-equivalent."""
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project.get_project_tier", return_value="first"):
            assert is_pro("/path") is False

    def test_can_use_pro_for_first_project(self):
        """First project CAN use pro features."""
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project.get_project_tier", return_value="first"):
            assert can_use_pro("/path") is True

    def test_can_use_pro_false_for_free(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            assert can_use_pro() is False

    def test_get_tool_filter_tier_pro(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            assert get_tool_filter_tier() == "pro"

    def test_get_tool_filter_tier_free(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            assert get_tool_filter_tier() == "free"

    def test_get_tool_filter_tier_first_is_free(self):
        """First project tier should filter as 'free' (not show Pro tools)."""
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project.get_project_tier", return_value="first"):
            assert get_tool_filter_tier("/path") == "free"
