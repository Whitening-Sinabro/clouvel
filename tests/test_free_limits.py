# -*- coding: utf-8 -*-
"""Free/Pro gating tests (v5.0 soft nudge limits)"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from mcp.types import TextContent

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.checkpoint import (
    MAX_FREE_CHECKPOINTS,
    MAX_PRO_CHECKPOINTS,
    _enforce_checkpoint_limit,
)
from clouvel.server import (
    _is_pro,
    _apply_free_error_limit,
    FREE_ERROR_LIMIT,
)


# ── _is_pro Tests ──


class TestIsPro:
    def test_returns_bool(self):
        """_is_pro should always return a boolean."""
        result = _is_pro("")
        assert isinstance(result, bool)

    def test_developer_is_pro(self):
        """Developer mode should be treated as Pro."""
        with patch("clouvel.license_common.is_developer", return_value=True):
            assert _is_pro("") is True

    def test_license_is_pro(self):
        """User with license cache should be Pro."""
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value={"tier": "personal"}):
            assert _is_pro("") is True

    def test_trial_is_pro(self):
        """User with active trial should be Pro."""
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=True):
            assert _is_pro("") is True

    def test_no_license_no_trial_is_not_pro(self):
        """User without license or trial should not be Pro."""
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=False):
            assert _is_pro("") is False


# ── Checkpoint Limit Tests ──


class TestCheckpointLimits:
    def test_free_limit_is_1(self):
        assert MAX_FREE_CHECKPOINTS == 1

    def test_pro_limit_is_50(self):
        assert MAX_PRO_CHECKPOINTS == 50

    def test_enforce_free_limit(self):
        """Free users should only keep 1 checkpoint."""
        temp_dir = tempfile.mkdtemp()
        try:
            d = Path(temp_dir)
            # Create 3 checkpoint files
            (d / "2026-01-01T00-00-00_test1.md").write_text("cp1")
            (d / "2026-01-02T00-00-00_test2.md").write_text("cp2")
            (d / "2026-01-03T00-00-00_test3.md").write_text("cp3")

            deleted = _enforce_checkpoint_limit(d, is_pro=False)
            remaining = list(d.glob("2*.md"))

            # Free limit=1, so with 3 files, 2 should be deleted (leaving room for 1 new)
            assert len(deleted) >= 2
            assert len(remaining) <= MAX_FREE_CHECKPOINTS
        finally:
            shutil.rmtree(temp_dir)

    def test_enforce_pro_limit(self):
        """Pro users should keep up to 50 checkpoints."""
        temp_dir = tempfile.mkdtemp()
        try:
            d = Path(temp_dir)
            # Create 3 checkpoint files — well under Pro limit
            (d / "2026-01-01T00-00-00_test1.md").write_text("cp1")
            (d / "2026-01-02T00-00-00_test2.md").write_text("cp2")
            (d / "2026-01-03T00-00-00_test3.md").write_text("cp3")

            deleted = _enforce_checkpoint_limit(d, is_pro=True)

            # Pro limit=50, so 3 files should all remain
            assert len(deleted) == 0
            assert len(list(d.glob("2*.md"))) == 3
        finally:
            shutil.rmtree(temp_dir)

    def test_latest_md_excluded(self):
        """latest.md should not be counted or deleted."""
        temp_dir = tempfile.mkdtemp()
        try:
            d = Path(temp_dir)
            (d / "latest.md").write_text("latest")
            (d / "2026-01-01T00-00-00_test.md").write_text("cp1")

            deleted = _enforce_checkpoint_limit(d, is_pro=False)

            # latest.md should still exist
            assert (d / "latest.md").exists()
        finally:
            shutil.rmtree(temp_dir)


# ── Error Limit Tests ──


class TestErrorLimit:
    def test_free_error_limit_is_5(self):
        assert FREE_ERROR_LIMIT == 5

    def test_no_errors_no_nudge(self):
        """When there are no error logs, no nudge is added."""
        result = [TextContent(type="text", text="No risk factors found.")]
        limited = _apply_free_error_limit(result, "/nonexistent/path")
        assert "Free limit" not in limited[0].text

    def test_nudge_added_when_over_limit(self):
        """When error count > 5, nudge message is appended."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create error log with 10 entries
            errors_dir = Path(temp_dir) / ".claude" / "errors"
            errors_dir.mkdir(parents=True)
            log_file = errors_dir / "error_log.jsonl"
            log_file.write_text("\n".join(['{"id": %d}' % i for i in range(10)]))

            result = [TextContent(type="text", text="Proactive Warning")]
            limited = _apply_free_error_limit(result, temp_dir)

            assert "5 of 10" in limited[0].text
            assert "Free limit" in limited[0].text
            assert "Pro" in limited[0].text
        finally:
            shutil.rmtree(temp_dir)

    def test_no_nudge_under_limit(self):
        """When error count <= 5, no nudge is added."""
        temp_dir = tempfile.mkdtemp()
        try:
            errors_dir = Path(temp_dir) / ".claude" / "errors"
            errors_dir.mkdir(parents=True)
            log_file = errors_dir / "error_log.jsonl"
            log_file.write_text("\n".join(['{"id": %d}' % i for i in range(3)]))

            result = [TextContent(type="text", text="Proactive Warning")]
            limited = _apply_free_error_limit(result, temp_dir)

            assert "Free limit" not in limited[0].text
        finally:
            shutil.rmtree(temp_dir)

    def test_empty_result_safe(self):
        """Empty result should not crash."""
        result = _apply_free_error_limit([], "/path")
        assert result == []
