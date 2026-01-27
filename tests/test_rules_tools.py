# -*- coding: utf-8 -*-
"""Rules tools module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.rules import (
    init_rules,
    get_rule,
    add_rule,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestInitRules:
    """init_rules function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        result = await init_rules(str(temp_project), "minimal")
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_path_not_exists(self):
        """Returns error when path doesn't exist"""
        result = await init_rules("/nonexistent/path/xyz", "minimal")
        assert len(result) == 1
        assert "존재하지 않습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_creates_rules_dir(self, temp_project):
        """Creates .claude/rules directory"""
        await init_rules(str(temp_project), "minimal")
        rules_dir = temp_project / ".claude" / "rules"
        assert rules_dir.exists()

    @pytest.mark.asyncio
    async def test_minimal_template(self, temp_project):
        """Minimal template creates global and security"""
        await init_rules(str(temp_project), "minimal")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "global.md").exists()
        assert (rules_dir / "security.md").exists()

    @pytest.mark.asyncio
    async def test_web_template(self, temp_project):
        """Web template creates frontend rules"""
        await init_rules(str(temp_project), "web")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "frontend.md").exists()

    @pytest.mark.asyncio
    async def test_api_template(self, temp_project):
        """API template creates api and database rules"""
        await init_rules(str(temp_project), "api")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "api.md").exists()
        assert (rules_dir / "database.md").exists()

    @pytest.mark.asyncio
    async def test_fullstack_template(self, temp_project):
        """Fullstack template creates all rules"""
        await init_rules(str(temp_project), "fullstack")
        rules_dir = temp_project / ".claude" / "rules"
        assert (rules_dir / "global.md").exists()
        assert (rules_dir / "security.md").exists()
        assert (rules_dir / "frontend.md").exists()
        assert (rules_dir / "api.md").exists()
        assert (rules_dir / "database.md").exists()

    @pytest.mark.asyncio
    async def test_creates_index_file(self, temp_project):
        """Creates rules.index.json"""
        await init_rules(str(temp_project), "minimal")
        index_file = temp_project / ".claude" / "rules" / "rules.index.json"
        assert index_file.exists()

    @pytest.mark.asyncio
    async def test_deprecation_warning(self, temp_project):
        """Includes deprecation warning"""
        result = await init_rules(str(temp_project), "minimal")
        assert "DEPRECATED" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_template_uses_minimal(self, temp_project):
        """Unknown template falls back to minimal"""
        await init_rules(str(temp_project), "unknown")
        rules_dir = temp_project / ".claude" / "rules"
        # Should use minimal template
        assert (rules_dir / "global.md").exists()
        assert (rules_dir / "security.md").exists()


class TestGetRule:
    """get_rule function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        # First init rules
        await init_rules(str(temp_project), "minimal")
        result = await get_rule(str(temp_project), "coding")
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_no_rules_dir(self, temp_project):
        """Returns error when no rules dir"""
        result = await get_rule(str(temp_project), "coding")
        assert "찾을 수 없습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_empty_rules_dir(self, temp_project):
        """Returns error when rules dir is empty"""
        rules_dir = temp_project / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        result = await get_rule(str(temp_project), "coding")
        assert "규칙 파일이 없습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_loads_rules(self, temp_project):
        """Loads rules from files"""
        await init_rules(str(temp_project), "minimal")
        result = await get_rule(str(temp_project), "coding")
        assert "ALWAYS" in result[0].text or "NEVER" in result[0].text

    @pytest.mark.asyncio
    async def test_context_shown(self, temp_project):
        """Shows context in output"""
        await init_rules(str(temp_project), "minimal")
        result = await get_rule(str(temp_project), "review")
        assert "컨텍스트" in result[0].text

    @pytest.mark.asyncio
    async def test_finds_rules_in_parent(self, temp_project):
        """Finds rules in parent directory"""
        await init_rules(str(temp_project), "minimal")
        sub_dir = temp_project / "src" / "components"
        sub_dir.mkdir(parents=True)
        result = await get_rule(str(sub_dir), "coding")
        # Should find rules from parent
        assert "ALWAYS" in result[0].text or "NEVER" in result[0].text


class TestAddRule:
    """add_rule function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        await init_rules(str(temp_project), "minimal")
        result = await add_rule(str(temp_project), "never", "Test rule", "general")
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_no_rules_dir(self, temp_project):
        """Returns error when no rules dir"""
        result = await add_rule(str(temp_project), "never", "Test rule", "general")
        assert "폴더가 없습니다" in result[0].text

    @pytest.mark.asyncio
    async def test_adds_to_existing_file(self, temp_project):
        """Adds rule to existing file"""
        await init_rules(str(temp_project), "minimal")
        await add_rule(str(temp_project), "never", "New test rule", "general")

        rules_file = temp_project / ".claude" / "rules" / "global.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "New test rule" in content

    @pytest.mark.asyncio
    async def test_creates_file_if_not_exists(self, temp_project):
        """Creates category file if not exists"""
        await init_rules(str(temp_project), "minimal")
        # api.md doesn't exist with minimal template
        await add_rule(str(temp_project), "always", "API rule", "api")

        api_file = temp_project / ".claude" / "rules" / "api.md"
        assert api_file.exists()
        assert "API rule" in api_file.read_text(encoding="utf-8")

    @pytest.mark.asyncio
    async def test_adds_to_existing_section(self, temp_project):
        """Adds rule to existing section"""
        await init_rules(str(temp_project), "minimal")
        # global.md has NEVER section
        await add_rule(str(temp_project), "never", "Another never rule", "general")

        rules_file = temp_project / ".claude" / "rules" / "global.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "Another never rule" in content

    @pytest.mark.asyncio
    async def test_adds_new_section(self, temp_project):
        """Adds new section if not exists"""
        await init_rules(str(temp_project), "minimal")
        # PREFER section doesn't exist
        await add_rule(str(temp_project), "prefer", "Prefer this", "general")

        rules_file = temp_project / ".claude" / "rules" / "global.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "PREFER" in content
        assert "Prefer this" in content

    @pytest.mark.asyncio
    async def test_security_category(self, temp_project):
        """Adds to security category"""
        await init_rules(str(temp_project), "minimal")
        await add_rule(str(temp_project), "never", "Security rule", "security")

        rules_file = temp_project / ".claude" / "rules" / "security.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "Security rule" in content

    @pytest.mark.asyncio
    async def test_frontend_category(self, temp_project):
        """Adds to frontend category"""
        await init_rules(str(temp_project), "web")
        await add_rule(str(temp_project), "always", "Frontend rule", "frontend")

        rules_file = temp_project / ".claude" / "rules" / "frontend.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "Frontend rule" in content

    @pytest.mark.asyncio
    async def test_database_category(self, temp_project):
        """Adds to database category"""
        await init_rules(str(temp_project), "api")
        await add_rule(str(temp_project), "never", "Database rule", "database")

        rules_file = temp_project / ".claude" / "rules" / "database.md"
        content = rules_file.read_text(encoding="utf-8")
        assert "Database rule" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
