# -*- coding: utf-8 -*-
"""Tests for services.quota — v6.0: no quotas."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.services.quota import (
    FREE_PERSPECTIVES_MANAGERS,
    FREE_PERSPECTIVES_QUESTIONS,
    PRO_DEFAULT_PERSPECTIVES_MANAGERS,
    PRO_DEFAULT_PERSPECTIVES_QUESTIONS,
    QuotaResult,
    get_perspectives_limits,
)


class TestConstants:
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


class TestGetPerspectivesLimits:
    def test_always_pro_limits(self):
        """v6.0: Always returns Pro limits."""
        limits = get_perspectives_limits()
        assert limits["max_managers"] == PRO_DEFAULT_PERSPECTIVES_MANAGERS
        assert limits["max_questions"] == PRO_DEFAULT_PERSPECTIVES_QUESTIONS

    def test_with_path(self):
        limits = get_perspectives_limits("/some/path")
        assert limits["max_managers"] == 4
        assert limits["max_questions"] == 2
