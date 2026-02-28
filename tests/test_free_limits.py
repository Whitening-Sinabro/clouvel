# -*- coding: utf-8 -*-
"""Free/Pro gating tests — v6.0: all features free."""

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
)


# ── _is_pro Tests ──


class TestIsPro:
    def test_returns_bool(self):
        result = _is_pro("")
        assert isinstance(result, bool)

    def test_always_true(self):
        """v6.0: _is_pro always returns True."""
        assert _is_pro("") is True
        assert _is_pro("/any/path") is True


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
            (d / "2026-01-01T00-00-00_test1.md").write_text("cp1")
            (d / "2026-01-02T00-00-00_test2.md").write_text("cp2")
            (d / "2026-01-03T00-00-00_test3.md").write_text("cp3")

            deleted = _enforce_checkpoint_limit(d, is_pro=False)
            remaining = list(d.glob("2*.md"))

            assert len(deleted) >= 2
            assert len(remaining) <= MAX_FREE_CHECKPOINTS
        finally:
            shutil.rmtree(temp_dir)

    def test_enforce_pro_limit(self):
        """Pro users should keep up to 50 checkpoints."""
        temp_dir = tempfile.mkdtemp()
        try:
            d = Path(temp_dir)
            (d / "2026-01-01T00-00-00_test1.md").write_text("cp1")
            (d / "2026-01-02T00-00-00_test2.md").write_text("cp2")
            (d / "2026-01-03T00-00-00_test3.md").write_text("cp3")

            deleted = _enforce_checkpoint_limit(d, is_pro=True)

            assert len(deleted) == 0
            assert len(list(d.glob("2*.md"))) == 3
        finally:
            shutil.rmtree(temp_dir)

    def test_latest_md_excluded(self):
        temp_dir = tempfile.mkdtemp()
        try:
            d = Path(temp_dir)
            (d / "latest.md").write_text("latest")
            (d / "2026-01-01T00-00-00_test.md").write_text("cp1")

            deleted = _enforce_checkpoint_limit(d, is_pro=False)

            assert (d / "latest.md").exists()
        finally:
            shutil.rmtree(temp_dir)


