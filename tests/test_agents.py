# -*- coding: utf-8 -*-
"""Agent tools module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.agents import (
    spawn_explore,
    spawn_librarian,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    # Create planning directory structure
    planning_dir = temp_path / ".claude" / "planning"
    planning_dir.mkdir(parents=True, exist_ok=True)
    (planning_dir / "findings.md").write_text("# Findings\n", encoding="utf-8")
    yield temp_path
    shutil.rmtree(temp_dir)


class TestSpawnExplore:
    """spawn_explore function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        result = await spawn_explore(
            str(temp_project),
            "Find main entry point",
            "project",
            False
        )
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_returns_text_content(self, temp_project):
        """Returns TextContent"""
        result = await spawn_explore(
            str(temp_project),
            "Find tests",
            "project",
            False
        )
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_includes_query_in_prompt(self, temp_project):
        """Includes query in prompt"""
        query = "Find the database module"
        result = await spawn_explore(
            str(temp_project),
            query,
            "project",
            False
        )
        assert query in result[0].text

    @pytest.mark.asyncio
    async def test_includes_scope_in_prompt(self, temp_project):
        """Includes scope in prompt"""
        result = await spawn_explore(
            str(temp_project),
            "Find tests",
            "folder",
            False
        )
        assert "folder" in result[0].text

    @pytest.mark.asyncio
    async def test_file_scope(self, temp_project):
        """File scope works"""
        result = await spawn_explore(
            str(temp_project),
            "Analyze this file",
            "file",
            False
        )
        assert "단일 파일" in result[0].text or "file" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_folder_scope(self, temp_project):
        """Folder scope works"""
        result = await spawn_explore(
            str(temp_project),
            "Scan folder",
            "folder",
            False
        )
        assert "폴더" in result[0].text or "folder" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_project_scope(self, temp_project):
        """Project scope works"""
        result = await spawn_explore(
            str(temp_project),
            "Explore project",
            "project",
            False
        )
        assert "프로젝트" in result[0].text or "project" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_deep_scope(self, temp_project):
        """Deep scope works"""
        result = await spawn_explore(
            str(temp_project),
            "Deep analysis",
            "deep",
            False
        )
        assert "심층" in result[0].text or "deep" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_invalid_path(self):
        """Returns error for invalid path"""
        result = await spawn_explore(
            "/nonexistent/path",
            "Query",
            "project",
            False
        )
        assert "존재하지 않습니다" in result[0].text or "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_save_findings_true(self, temp_project):
        """Saves findings when save_findings is True"""
        result = await spawn_explore(
            str(temp_project),
            "Test query",
            "project",
            True
        )
        # Should still return prompt
        assert len(result) == 1

        # Check findings file was updated
        findings_file = temp_project / ".claude" / "planning" / "findings.md"
        content = findings_file.read_text(encoding="utf-8")
        assert "탐색: Test query" in content or "Test query" in content

    @pytest.mark.asyncio
    async def test_save_findings_without_file(self):
        """Handles missing findings file gracefully"""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)

        try:
            result = await spawn_explore(
                str(temp_path),
                "Query",
                "project",
                True  # save_findings but no findings.md
            )
            # Should still return prompt without error
            assert len(result) == 1
        finally:
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_default_scope_for_unknown(self, temp_project):
        """Uses project scope for unknown scope value"""
        result = await spawn_explore(
            str(temp_project),
            "Query",
            "unknown_scope",
            False
        )
        # Should default to project strategy
        assert "탐색" in result[0].text or "explore" in result[0].text.lower()


class TestSpawnLibrarian:
    """spawn_librarian function tests"""

    @pytest.mark.asyncio
    async def test_returns_list(self, temp_project):
        """Returns list of TextContent"""
        result = await spawn_librarian(
            str(temp_project),
            "React hooks",
            "library",
            "standard"
        )
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_returns_text_content(self, temp_project):
        """Returns TextContent"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "library",
            "standard"
        )
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_includes_topic_in_prompt(self, temp_project):
        """Includes topic in prompt"""
        topic = "Prisma ORM"
        result = await spawn_librarian(
            str(temp_project),
            topic,
            "library",
            "standard"
        )
        assert topic in result[0].text

    @pytest.mark.asyncio
    async def test_library_type(self, temp_project):
        """Library research type works"""
        result = await spawn_librarian(
            str(temp_project),
            "React",
            "library",
            "standard"
        )
        assert "라이브러리" in result[0].text or "library" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_api_type(self, temp_project):
        """API research type works"""
        result = await spawn_librarian(
            str(temp_project),
            "REST API",
            "api",
            "standard"
        )
        assert "API" in result[0].text

    @pytest.mark.asyncio
    async def test_migration_type(self, temp_project):
        """Migration research type works"""
        result = await spawn_librarian(
            str(temp_project),
            "React 18 migration",
            "migration",
            "standard"
        )
        assert "마이그레이션" in result[0].text or "migration" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_best_practice_type(self, temp_project):
        """Best practice research type works"""
        result = await spawn_librarian(
            str(temp_project),
            "Error handling",
            "best_practice",
            "standard"
        )
        assert "프랙티스" in result[0].text or "practice" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_quick_depth(self, temp_project):
        """Quick depth works"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "library",
            "quick"
        )
        assert "QUICK" in result[0].text or "5분" in result[0].text

    @pytest.mark.asyncio
    async def test_standard_depth(self, temp_project):
        """Standard depth works"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "library",
            "standard"
        )
        assert "STANDARD" in result[0].text or "15분" in result[0].text

    @pytest.mark.asyncio
    async def test_thorough_depth(self, temp_project):
        """Thorough depth works"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "library",
            "thorough"
        )
        assert "THOROUGH" in result[0].text or "30분" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_path(self):
        """Returns error for invalid path"""
        result = await spawn_librarian(
            "/nonexistent/path",
            "Topic",
            "library",
            "standard"
        )
        assert "존재하지 않습니다" in result[0].text or "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_saves_to_findings(self, temp_project):
        """Saves research start to findings.md"""
        result = await spawn_librarian(
            str(temp_project),
            "Test Topic",
            "library",
            "standard"
        )
        # Should return prompt
        assert len(result) == 1

        # Check findings file was updated
        findings_file = temp_project / ".claude" / "planning" / "findings.md"
        content = findings_file.read_text(encoding="utf-8")
        assert "조사: Test Topic" in content or "Test Topic" in content

    @pytest.mark.asyncio
    async def test_handles_missing_findings_file(self):
        """Handles missing findings file gracefully"""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)

        try:
            result = await spawn_librarian(
                str(temp_path),
                "Topic",
                "library",
                "standard"
            )
            # Should still return prompt without error
            assert len(result) == 1
        finally:
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_default_type_for_unknown(self, temp_project):
        """Uses library type for unknown type value"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "unknown_type",
            "standard"
        )
        # Should default to library strategy
        assert "라이브러리" in result[0].text or "library" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_default_depth_for_unknown(self, temp_project):
        """Uses standard depth for unknown depth value"""
        result = await spawn_librarian(
            str(temp_project),
            "Topic",
            "library",
            "unknown_depth"
        )
        # Should default to standard depth
        assert "STANDARD" in result[0].text or "15분" in result[0].text


class TestAgentsIntegration:
    """Integration tests for agents"""

    @pytest.mark.asyncio
    async def test_explore_then_librarian(self, temp_project):
        """Can use explore then librarian"""
        explore_result = await spawn_explore(
            str(temp_project),
            "Find modules",
            "project",
            True
        )
        assert len(explore_result) == 1

        librarian_result = await spawn_librarian(
            str(temp_project),
            "Python modules",
            "library",
            "standard"
        )
        assert len(librarian_result) == 1

    @pytest.mark.asyncio
    async def test_all_scopes_work(self, temp_project):
        """All scopes produce valid output"""
        scopes = ["file", "folder", "project", "deep"]
        for scope in scopes:
            result = await spawn_explore(
                str(temp_project),
                f"Test {scope}",
                scope,
                False
            )
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_all_research_types_work(self, temp_project):
        """All research types produce valid output"""
        types = ["library", "api", "migration", "best_practice"]
        for research_type in types:
            result = await spawn_librarian(
                str(temp_project),
                f"Test {research_type}",
                research_type,
                "standard"
            )
            assert len(result) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
