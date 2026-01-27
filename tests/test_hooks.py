# -*- coding: utf-8 -*-
"""Hooks module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.hooks import (
    hook_design,
    hook_verify,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestHookDesign:
    """hook_design function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=[],
            block_on_fail=True
        )
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_path_not_exists(self):
        """Returns error when path doesn't exist"""
        result = await hook_design(
            "/nonexistent/path/xyz",
            trigger="pre_code",
            checks=[],
            block_on_fail=True
        )
        assert len(result) == 1
        assert "존재하지 않습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_creates_hook_file(self, temp_project):
        """Creates hook config file"""
        await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=["check1", "check2"],
            block_on_fail=True
        )

        hook_file = temp_project / ".claude" / "hooks" / "pre_code.json"
        assert hook_file.exists()

    @pytest.mark.asyncio
    async def test_custom_checks(self, temp_project):
        """Uses custom checks when provided"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=["custom_check"],
            block_on_fail=False
        )
        assert "custom_check" in result[0].text

    @pytest.mark.asyncio
    async def test_default_checks_pre_code(self, temp_project):
        """Uses default checks for pre_code trigger"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=[],
            block_on_fail=True
        )
        # Default pre_code checks include prd_exists
        assert "prd_exists" in result[0].text

    @pytest.mark.asyncio
    async def test_default_checks_pre_feature(self, temp_project):
        """Uses default checks for pre_feature trigger"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_feature",
            checks=[],
            block_on_fail=True
        )
        assert "feature_in_prd" in result[0].text

    @pytest.mark.asyncio
    async def test_block_on_fail_message(self, temp_project):
        """Shows correct message based on block_on_fail"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=[],
            block_on_fail=True
        )
        assert "차단됩니다" in result[0].text

    @pytest.mark.asyncio
    async def test_deprecation_warning(self, temp_project):
        """Includes deprecation warning"""
        result = await hook_design(
            str(temp_project),
            trigger="pre_code",
            checks=[],
            block_on_fail=True
        )
        assert "DEPRECATED" in result[0].text


class TestHookVerify:
    """hook_verify function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=[],
            parallel=False,
            continue_on_error=False
        )
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_path_not_exists(self):
        """Returns error when path doesn't exist"""
        result = await hook_verify(
            "/nonexistent/path/xyz",
            trigger="post_code",
            steps=[],
            parallel=False,
            continue_on_error=False
        )
        assert len(result) == 1
        assert "존재하지 않습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_creates_hook_file(self, temp_project):
        """Creates hook config file"""
        await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=["lint", "test"],
            parallel=True,
            continue_on_error=True
        )

        hook_file = temp_project / ".claude" / "hooks" / "post_code.json"
        assert hook_file.exists()

    @pytest.mark.asyncio
    async def test_custom_steps(self, temp_project):
        """Uses custom steps when provided"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=["custom_step"],
            parallel=False,
            continue_on_error=False
        )
        assert "custom_step" in result[0].text

    @pytest.mark.asyncio
    async def test_default_steps_post_code(self, temp_project):
        """Uses default steps for post_code trigger"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=[],
            parallel=False,
            continue_on_error=False
        )
        # Default post_code steps include lint
        assert "lint" in result[0].text

    @pytest.mark.asyncio
    async def test_default_steps_pre_commit(self, temp_project):
        """Uses default steps for pre_commit trigger"""
        result = await hook_verify(
            str(temp_project),
            trigger="pre_commit",
            steps=[],
            parallel=False,
            continue_on_error=False
        )
        assert "security_scan" in result[0].text

    @pytest.mark.asyncio
    async def test_parallel_mode_message(self, temp_project):
        """Shows parallel mode in output"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=[],
            parallel=True,
            continue_on_error=False
        )
        assert "병렬" in result[0].text

    @pytest.mark.asyncio
    async def test_continue_on_error_message(self, temp_project):
        """Shows error handling in output"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=[],
            parallel=False,
            continue_on_error=True
        )
        assert "계속 진행" in result[0].text

    @pytest.mark.asyncio
    async def test_deprecation_warning(self, temp_project):
        """Includes deprecation warning"""
        result = await hook_verify(
            str(temp_project),
            trigger="post_code",
            steps=[],
            parallel=False,
            continue_on_error=False
        )
        assert "DEPRECATED" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
