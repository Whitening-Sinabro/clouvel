# -*- coding: utf-8 -*-
"""call_tool integration tests — v6.0: no Pro gating."""

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
)
from clouvel.tool_dispatch import (
    _get_list_tools_tier,
    _get_call_tool_tier,
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
    def test_all_tools_always_allowed(self):
        """v6.0: All tools allowed for any tier."""
        for tier in ["pro", "free", "first", "unknown"]:
            assert is_tool_allowed("can_code", tier) is True
            assert is_tool_allowed("gate", tier) is True
            assert is_tool_allowed("error_check", tier) is True
            assert is_tool_allowed("error_learn", tier) is True
            assert is_tool_allowed("meeting", tier) is True
            assert is_tool_allowed("ship", tier) is True

    def test_internal_tool_always_allowed(self):
        assert is_tool_allowed("scan_docs", "free") is True
        assert is_tool_allowed("init_rules", "free") is True


# ── Tier Detection Tests ──


class TestTierDetection:
    def test_is_pro_always_true(self):
        """v6.0: _is_pro always returns True."""
        assert _is_pro("") is True
        assert _is_pro("/any/path") is True

    def test_list_tools_tier_always_pro(self):
        """v6.0: list tools tier is always 'pro'."""
        assert _get_list_tools_tier() == "pro"

    def test_call_tool_tier_always_pro(self):
        """v6.0: call tool tier is always 'pro'."""
        assert _get_call_tool_tier("/some/path") == "pro"


# ── PRD Heading Extraction Tests ──


class TestPrdHeadingExtraction:
    """Test _extract_prd_headings and _format_prd_toc."""

    def setup_method(self):
        from clouvel.tools.core import _extract_prd_headings, _format_prd_toc
        self._extract = _extract_prd_headings
        self._format = _format_prd_toc

    def test_basic_headings(self, tmp_path):
        prd = tmp_path / "PRD.md"
        prd.write_text("# Title\n## Summary\n### Details\n## Acceptance Criteria\ntext\n", encoding="utf-8")
        headings = self._extract(prd)
        assert "## Summary" in headings
        assert "### Details" in headings
        assert "## Acceptance Criteria" in headings
        # # Title is h1 — should NOT be extracted
        assert "# Title" not in headings

    def test_empty_file(self, tmp_path):
        prd = tmp_path / "PRD.md"
        prd.write_text("", encoding="utf-8")
        assert self._extract(prd) == []

    def test_nonexistent_file(self, tmp_path):
        prd = tmp_path / "NOPE.md"
        assert self._extract(prd) == []

    def test_many_headings(self, tmp_path):
        prd = tmp_path / "PRD.md"
        lines = [f"## Section {i}" for i in range(35)]
        prd.write_text("\n".join(lines), encoding="utf-8")
        headings = self._extract(prd)
        assert len(headings) == 35

    def test_format_toc_with_headings(self):
        headings = ["## Summary", "### Details", "## Acceptance Criteria"]
        toc = self._format(headings)
        assert "- ## Summary" in toc
        assert "- ### Details" in toc
        assert "- ## Acceptance Criteria" in toc

    def test_format_toc_empty(self):
        assert "_No headings" in self._format([])


# ── can_code TOC Integration Tests ──


class TestCanCodeTocIntegration:
    """Test that can_code PASS responses include PRD TOC and session rules."""

    @pytest.fixture
    def project_with_prd(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        prd = docs / "PRD.md"
        prd.write_text(
            "# My PRD\n\n## Summary\nBuild a thing\n\n"
            "## Acceptance Criteria\n- [ ] It works\n\n"
            "## Non-Goals\nNot this\n",
            encoding="utf-8",
        )
        return tmp_path

    @pytest.mark.asyncio
    async def test_pass_includes_toc(self, project_with_prd):
        from clouvel.tools.core import can_code
        result = await can_code(str(project_with_prd / "docs"))
        text = result[0].text
        assert "PRD Table of Contents" in text
        assert "## Summary" in text
        assert "## Acceptance Criteria" in text

    @pytest.mark.asyncio
    async def test_pass_includes_session_rules(self, project_with_prd):
        from clouvel.tools.core import can_code
        result = await can_code(str(project_with_prd / "docs"))
        text = result[0].text
        assert "Rules for This Session" in text
        assert "Build ONLY what is listed" in text


# ── Start Mode Tests ──


class TestStartMode:
    """Test start tool mode parameter."""

    def test_mode_auto_default(self, tmp_path):
        from clouvel.tools.start.core import start
        result = start(str(tmp_path))
        # auto mode = existing behavior (NEED_PRD or READY)
        assert result["status"] in ("NEED_PRD", "READY", "INCOMPLETE")

    def test_mode_existing(self, tmp_path):
        from clouvel.tools.start.core import start
        result = start(str(tmp_path), mode="existing")
        assert result["status"] == "MODE_GUIDE"
        assert result["mode"] == "existing"
        assert "Place PRD" in result["next_steps"][0]

    def test_mode_write(self, tmp_path):
        from clouvel.tools.start.core import start
        result = start(str(tmp_path), mode="write")
        assert result["status"] == "MODE_GUIDE"
        assert "Acceptance Criteria" in result["next_steps"][1]

    def test_mode_hybrid(self, tmp_path):
        from clouvel.tools.start.core import start
        result = start(str(tmp_path), mode="hybrid")
        assert result["status"] == "MODE_GUIDE"
        assert result["mode"] == "hybrid"

    def test_mode_ai_falls_through(self, tmp_path):
        from clouvel.tools.start.core import start
        result = start(str(tmp_path), mode="ai")
        # ai mode falls through to normal flow (NEED_PRD)
        assert result["status"] in ("NEED_PRD", "READY", "INCOMPLETE")
