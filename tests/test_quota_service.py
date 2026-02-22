# -*- coding: utf-8 -*-
"""Tests for services.quota — quota checking logic."""

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.services.quota import (
    FREE_ERROR_LIMIT,
    FREE_PERSPECTIVES_MANAGERS,
    FREE_PERSPECTIVES_QUESTIONS,
    PRO_DEFAULT_PERSPECTIVES_MANAGERS,
    PRO_DEFAULT_PERSPECTIVES_QUESTIONS,
    QuotaResult,
    check_error_view_quota,
    check_kb_access,
    get_perspectives_limits,
)


class TestConstants:
    def test_free_error_limit(self):
        assert FREE_ERROR_LIMIT == 5

    def test_perspectives_limits(self):
        assert FREE_PERSPECTIVES_MANAGERS == 2
        assert FREE_PERSPECTIVES_QUESTIONS == 1
        assert PRO_DEFAULT_PERSPECTIVES_MANAGERS == 4
        assert PRO_DEFAULT_PERSPECTIVES_QUESTIONS == 2


class TestQuotaResult:
    def test_defaults(self):
        r = QuotaResult(allowed=True)
        assert r.allowed is True
        assert r.message == ""
        assert r.remaining == -1


class TestCheckErrorViewQuota:
    def test_no_errors(self):
        result = check_error_view_quota("/nonexistent/path")
        assert result.allowed is True
        assert result.message == ""

    def test_under_limit(self):
        temp_dir = tempfile.mkdtemp()
        try:
            error_dir = Path(temp_dir) / ".claude" / "errors"
            error_dir.mkdir(parents=True)
            log = error_dir / "error_log.jsonl"
            log.write_text("\n".join(['{"e":1}'] * 3), encoding="utf-8")
            result = check_error_view_quota(temp_dir)
            assert result.allowed is True
            assert result.remaining == 3
            assert result.message == ""
        finally:
            shutil.rmtree(temp_dir)

    def test_over_limit_shows_nudge(self):
        temp_dir = tempfile.mkdtemp()
        try:
            error_dir = Path(temp_dir) / ".claude" / "errors"
            error_dir.mkdir(parents=True)
            log = error_dir / "error_log.jsonl"
            log.write_text("\n".join(['{"e":1}'] * 10), encoding="utf-8")
            result = check_error_view_quota(temp_dir)
            assert result.allowed is True
            assert result.remaining == FREE_ERROR_LIMIT
            assert "Free limit" in result.message
            assert "Pro" in result.message
        finally:
            shutil.rmtree(temp_dir)


class TestCheckKbAccess:
    def test_developer_always_allowed(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            result = check_kb_access(".")
            assert result.allowed is True

    def test_active_trial_allowed(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.quotas.start_kb_trial"), \
             patch("clouvel.licensing.quotas.is_kb_trial_active", return_value=True):
            result = check_kb_access(".")
            assert result.allowed is True

    def test_expired_trial_blocked(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.quotas.start_kb_trial"), \
             patch("clouvel.licensing.quotas.is_kb_trial_active", return_value=False):
            result = check_kb_access(".")
            assert result.allowed is False
            assert "KB Write Locked" in result.message


class TestGetPerspectivesLimits:
    def test_free_limits(self):
        with patch("clouvel.licensing.core.is_developer", return_value=False), \
             patch("clouvel.licensing.validation.load_license_cache", return_value=None), \
             patch("clouvel.licensing.trial.is_full_trial_active", return_value=False):
            limits = get_perspectives_limits()
            assert limits["max_managers"] == 2
            assert limits["max_questions"] == 1

    def test_pro_limits(self):
        with patch("clouvel.licensing.core.is_developer", return_value=True):
            limits = get_perspectives_limits()
            assert limits["max_managers"] == 4
            assert limits["max_questions"] == 2
