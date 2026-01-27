# -*- coding: utf-8 -*-
"""Setup tools comprehensive tests"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.setup import (
    init_clouvel,
    setup_cli,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_project(temp_project):
    """Project with .git directory"""
    git_dir = temp_project / ".git" / "hooks"
    git_dir.mkdir(parents=True)
    return temp_project


class TestInitClouvel:
    """init_clouvel function tests"""

    @pytest.mark.asyncio
    async def test_init_ask(self):
        """Init with ask returns platform selection"""
        result = await init_clouvel("ask")
        assert "환경" in result[0].text or "Desktop" in result[0].text or "CLI" in result[0].text

    @pytest.mark.asyncio
    async def test_init_desktop(self):
        """Init for desktop platform"""
        result = await init_clouvel("desktop")
        assert "Desktop" in result[0].text or "desktop" in result[0].text.lower()
        assert "can_code" in result[0].text

    @pytest.mark.asyncio
    async def test_init_vscode(self):
        """Init for VS Code platform"""
        result = await init_clouvel("vscode")
        assert "VS Code" in result[0].text or "vscode" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_init_cli(self):
        """Init for CLI platform"""
        result = await init_clouvel("cli")
        assert "CLI" in result[0].text or "cli" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_init_unknown_fallback(self):
        """Init with unknown platform falls back to CLI"""
        result = await init_clouvel("unknown")
        # Should return CLI guide as default
        assert len(result[0].text) > 0


class TestSetupCliBasic:
    """setup_cli basic tests"""

    @pytest.mark.asyncio
    async def test_setup_remind_level(self, temp_project):
        """Setup with remind level"""
        result = await setup_cli(str(temp_project), "remind")
        assert "설정 완료" in result[0].text or "remind" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_setup_strict_level(self, git_project):
        """Setup with strict level"""
        result = await setup_cli(str(git_project), "strict")
        assert "설정 완료" in result[0].text or "strict" in result[0].text.lower()
        # Should create pre-commit hook
        hook_file = git_project / ".git" / "hooks" / "pre-commit"
        assert hook_file.exists()

    @pytest.mark.asyncio
    async def test_setup_full_level(self, git_project):
        """Setup with full level"""
        result = await setup_cli(str(git_project), "full")
        assert "설정 완료" in result[0].text
        # Should create hooks.json and pre-commit
        assert (git_project / ".claude" / "hooks.json").exists()

    @pytest.mark.asyncio
    async def test_setup_nonexistent_path(self):
        """Setup fails with nonexistent path"""
        result = await setup_cli("/nonexistent/path/123", "remind")
        assert "존재하지 않" in result[0].text or "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_setup_creates_claude_dir(self, temp_project):
        """Setup creates .claude directory"""
        await setup_cli(str(temp_project), "remind")
        assert (temp_project / ".claude").exists()

    @pytest.mark.asyncio
    async def test_setup_creates_claude_md(self, temp_project):
        """Setup creates CLAUDE.md"""
        await setup_cli(str(temp_project), "remind")
        assert (temp_project / "CLAUDE.md").exists()

    @pytest.mark.asyncio
    async def test_setup_updates_existing_claude_md(self, temp_project):
        """Setup updates existing CLAUDE.md"""
        # Create existing CLAUDE.md
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Existing content\n\nSome rules here.", encoding="utf-8")

        await setup_cli(str(temp_project), "remind")

        content = claude_md.read_text(encoding="utf-8")
        assert "Existing content" in content
        assert "Clouvel 규칙" in content


class TestSetupCliRules:
    """setup_cli rules option tests"""

    @pytest.mark.asyncio
    async def test_setup_rules_minimal(self, temp_project):
        """Setup with minimal rules"""
        result = await setup_cli(str(temp_project), "remind", rules="minimal")
        assert "Rules" in result[0].text or "규칙" in result[0].text

        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "global.md").exists()
        assert (rules_dir / "security.md").exists()

    @pytest.mark.asyncio
    async def test_setup_rules_web(self, temp_project):
        """Setup with web rules"""
        result = await setup_cli(str(temp_project), "remind", rules="web")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "frontend.md").exists()

    @pytest.mark.asyncio
    async def test_setup_rules_api(self, temp_project):
        """Setup with api rules"""
        result = await setup_cli(str(temp_project), "remind", rules="api")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "api.md").exists()
        assert (rules_dir / "database.md").exists()

    @pytest.mark.asyncio
    async def test_setup_rules_fullstack(self, temp_project):
        """Setup with fullstack rules"""
        result = await setup_cli(str(temp_project), "remind", rules="fullstack")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "frontend.md").exists()
        assert (rules_dir / "api.md").exists()
        assert (rules_dir / "database.md").exists()

    @pytest.mark.asyncio
    async def test_setup_rules_unknown_fallback(self, temp_project):
        """Setup with unknown rules falls back to minimal"""
        result = await setup_cli(str(temp_project), "remind", rules="unknown")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "global.md").exists()


class TestSetupCliHooks:
    """setup_cli hook option tests"""

    @pytest.mark.asyncio
    async def test_setup_hook_design(self, temp_project):
        """Setup design hook"""
        result = await setup_cli(str(temp_project), "remind", hook="design")
        assert "Design" in result[0].text or "Hook" in result[0].text

        hooks_dir = temp_project / ".claude" / "hooks"
        assert hooks_dir.exists()

    @pytest.mark.asyncio
    async def test_setup_hook_verify(self, temp_project):
        """Setup verify hook"""
        result = await setup_cli(str(temp_project), "remind", hook="verify")
        assert "Verify" in result[0].text or "Hook" in result[0].text

    @pytest.mark.asyncio
    async def test_setup_hook_with_trigger(self, temp_project):
        """Setup hook with custom trigger"""
        result = await setup_cli(str(temp_project), "remind", hook="design", hook_trigger="pre_feature")
        assert "pre_feature" in result[0].text or "feature" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_setup_hook_unknown(self, temp_project):
        """Setup with unknown hook type"""
        result = await setup_cli(str(temp_project), "remind", hook="unknown")
        assert "Unknown" in result[0].text or "unknown" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_setup_hook_creates_json(self, temp_project):
        """Setup hook creates JSON config"""
        await setup_cli(str(temp_project), "remind", hook="design", hook_trigger="pre_code")

        hook_file = temp_project / ".claude" / "hooks" / "pre_code.json"
        assert hook_file.exists()

        config = json.loads(hook_file.read_text(encoding="utf-8"))
        assert "trigger" in config
        assert config["trigger"] == "pre_code"


class TestSetupCliPreCommit:
    """setup_cli pre-commit hook tests"""

    @pytest.mark.asyncio
    async def test_pre_commit_content(self, git_project):
        """Pre-commit hook has expected content"""
        await setup_cli(str(git_project), "strict")

        hook_file = git_project / ".git" / "hooks" / "pre-commit"
        content = hook_file.read_text(encoding="utf-8")

        assert "PRD" in content
        assert "Clouvel" in content
        assert "BLOCKED" in content

    @pytest.mark.asyncio
    async def test_pre_commit_no_git_dir(self, temp_project):
        """Pre-commit skipped without .git directory"""
        result = await setup_cli(str(temp_project), "strict")
        # Should complete without error
        assert "설정 완료" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
