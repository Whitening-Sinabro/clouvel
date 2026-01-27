# -*- coding: utf-8 -*-
"""Security tools tests"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.security import (
    setup_security,
    add_security_pattern,
    get_security_log,
    DEFAULT_PATTERNS,
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


class TestSetupSecurity:
    """setup_security function tests"""

    @pytest.mark.asyncio
    async def test_setup_creates_config(self, temp_project):
        """Setup creates security.json"""
        result = await setup_security(str(temp_project))
        config_file = temp_project / ".clouvel" / "security.json"
        assert config_file.exists()
        assert "완료" in result[0].text or "setup" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_setup_config_contents(self, temp_project):
        """Setup creates valid JSON config"""
        await setup_security(str(temp_project))
        config_file = temp_project / ".clouvel" / "security.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))

        assert "patterns" in config
        assert "logging" in config
        assert "team_sync" in config
        assert config["logging"] is True  # default

    @pytest.mark.asyncio
    async def test_setup_with_custom_patterns(self, temp_project):
        """Setup includes custom patterns"""
        custom = ["secret_file", "private_key"]
        await setup_security(str(temp_project), custom_patterns=custom)

        config_file = temp_project / ".clouvel" / "security.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))

        assert "secret_file" in config["patterns"]
        assert "private_key" in config["patterns"]

    @pytest.mark.asyncio
    async def test_setup_logging_disabled(self, temp_project):
        """Setup with logging disabled"""
        await setup_security(str(temp_project), enable_logging=False)

        config_file = temp_project / ".clouvel" / "security.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))

        assert config["logging"] is False

    @pytest.mark.asyncio
    async def test_setup_team_sync_enabled(self, temp_project):
        """Setup with team sync enabled"""
        await setup_security(str(temp_project), team_sync=True)

        config_file = temp_project / ".clouvel" / "security.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))

        assert config["team_sync"] is True

    @pytest.mark.asyncio
    async def test_setup_creates_git_hook(self, git_project):
        """Setup creates pre-commit hook"""
        await setup_security(str(git_project))
        hook_file = git_project / ".git" / "hooks" / "pre-commit"
        assert hook_file.exists()
        content = hook_file.read_text(encoding="utf-8")
        assert "Clouvel" in content

    @pytest.mark.asyncio
    async def test_setup_nonexistent_path(self):
        """Setup fails with nonexistent path"""
        result = await setup_security("/nonexistent/path/123")
        assert "존재하지 않" in result[0].text or "not exist" in result[0].text.lower()


class TestAddSecurityPattern:
    """add_security_pattern function tests"""

    @pytest.mark.asyncio
    async def test_add_pattern_no_setup(self, temp_project):
        """Add pattern fails without setup"""
        result = await add_security_pattern(str(temp_project), "test_pattern")
        assert "setup_security" in result[0].text

    @pytest.mark.asyncio
    async def test_add_pattern_success(self, temp_project):
        """Add pattern succeeds after setup"""
        await setup_security(str(temp_project))
        result = await add_security_pattern(str(temp_project), "new_secret")

        config_file = temp_project / ".clouvel" / "security.json"
        config = json.loads(config_file.read_text(encoding="utf-8"))

        assert "new_secret" in config["patterns"]
        assert "추가" in result[0].text or "added" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_add_duplicate_pattern(self, temp_project):
        """Add duplicate pattern shows info"""
        await setup_security(str(temp_project), custom_patterns=["existing"])
        result = await add_security_pattern(str(temp_project), "existing")
        assert "이미" in result[0].text or "already" in result[0].text.lower()


class TestGetSecurityLog:
    """get_security_log function tests"""

    @pytest.mark.asyncio
    async def test_get_log_no_file(self, temp_project):
        """Get log when no log file exists"""
        result = await get_security_log(str(temp_project))
        assert "없" in result[0].text or "no" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_log_with_content(self, temp_project):
        """Get log with existing content"""
        clouvel_dir = temp_project / ".clouvel"
        clouvel_dir.mkdir(parents=True)

        log_file = clouvel_dir / "security.log"
        log_file.write_text("[2025-01-01] BLOCKED: secret.py\n[2025-01-02] BLOCKED: private.key", encoding="utf-8")

        result = await get_security_log(str(temp_project))
        assert "BLOCKED" in result[0].text
        assert "secret.py" in result[0].text

    @pytest.mark.asyncio
    async def test_get_log_limited_lines(self, temp_project):
        """Get log with limited lines"""
        clouvel_dir = temp_project / ".clouvel"
        clouvel_dir.mkdir(parents=True)

        log_file = clouvel_dir / "security.log"
        lines = "\n".join([f"[2025-01-{i:02d}] BLOCKED: file{i}.py" for i in range(1, 31)])
        log_file.write_text(lines, encoding="utf-8")

        result = await get_security_log(str(temp_project), lines=5)
        # Should show last 5 lines
        assert "file30.py" in result[0].text or "file2" in result[0].text


class TestDefaultPatterns:
    """DEFAULT_PATTERNS tests"""

    def test_default_patterns_exist(self):
        """Default patterns list exists"""
        assert len(DEFAULT_PATTERNS) > 0

    def test_default_patterns_include_sensitive(self):
        """Default patterns include common sensitive files"""
        assert any("marketing" in p.lower() for p in DEFAULT_PATTERNS)
        assert any("credential" in p.lower() for p in DEFAULT_PATTERNS)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
