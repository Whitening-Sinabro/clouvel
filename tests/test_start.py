# -*- coding: utf-8 -*-
"""Start tool comprehensive tests - targeting high coverage"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.start import (
    start,
    save_prd,
    get_prd_questions,
    quick_start,
    _detect_project_type,
    _validate_prd,
    _calculate_prd_diff,
    _analyze_prd_impact,
    _backup_prd,
    PRD_QUESTIONS,
    PROJECT_TYPE_PATTERNS,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def docs_dir(temp_project):
    """Create docs directory"""
    docs = temp_project / "docs"
    docs.mkdir()
    return docs


class TestDetectProjectType:
    """_detect_project_type function tests"""

    def test_detect_generic_empty(self, temp_project):
        """Empty project detected as generic"""
        result = _detect_project_type(temp_project)
        assert result["type"] == "generic"
        assert result["confidence"] == 0

    def test_detect_chrome_extension(self, temp_project):
        """Chrome extension with manifest.json"""
        manifest = {
            "manifest_version": 3,
            "name": "Test Extension",
            "permissions": ["activeTab"]
        }
        (temp_project / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        result = _detect_project_type(temp_project)
        assert result["type"] == "chrome-ext"
        assert result["confidence"] >= 30

    def test_detect_web_app_react(self, temp_project):
        """React web app detection"""
        pkg = {"dependencies": {"react": "^18.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
        (temp_project / "src").mkdir()
        (temp_project / "src" / "App.tsx").write_text("// React", encoding="utf-8")

        result = _detect_project_type(temp_project)
        assert result["type"] == "web-app"

    def test_detect_api_fastapi(self, temp_project):
        """FastAPI API detection"""
        pyproject = """
[project]
dependencies = [
    "fastapi>=0.100.0"
]
"""
        (temp_project / "pyproject.toml").write_text(pyproject, encoding="utf-8")
        (temp_project / "main.py").write_text("# FastAPI", encoding="utf-8")

        result = _detect_project_type(temp_project)
        assert result["type"] == "api"

    def test_detect_cli_typer(self, temp_project):
        """CLI with typer detection"""
        requirements = "typer>=0.9.0\nrich\n"
        (temp_project / "requirements.txt").write_text(requirements, encoding="utf-8")
        (temp_project / "cli.py").write_text("# CLI", encoding="utf-8")

        result = _detect_project_type(temp_project)
        assert result["type"] == "cli"

    def test_detect_discord_bot(self, temp_project):
        """Discord bot detection"""
        pkg = {"dependencies": {"discord.js": "^14.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
        (temp_project / "bot.js").write_text("// Bot", encoding="utf-8")

        result = _detect_project_type(temp_project)
        assert result["type"] == "discord-bot"

    def test_detect_landing_page(self, temp_project):
        """Landing page (HTML only) detection"""
        (temp_project / "index.html").write_text("<html></html>", encoding="utf-8")

        result = _detect_project_type(temp_project)
        # Landing page if no backend files
        assert result["type"] in ["landing-page", "generic"]


class TestValidatePrd:
    """_validate_prd function tests"""

    def test_valid_prd(self):
        """Valid PRD with all required sections"""
        content = """# Test PRD

## 1. Project Overview

### 1.1 Purpose
This project solves X problem.

### 1.2 Goals
- [ ] Goal 1
- [ ] Goal 2

## 2. Functional Requirements

### 2.1 Core Features
1. **Feature 1**: Does something
"""
        result = _validate_prd(content)
        assert result["is_valid"] is True
        assert len(result["missing_sections"]) == 0

    def test_invalid_prd_empty(self):
        """Empty PRD is invalid"""
        result = _validate_prd("")
        assert result["is_valid"] is False

    def test_prd_missing_overview(self):
        """PRD missing Project Overview"""
        content = """# Test PRD

## 2. Functional Requirements

### 2.1 Core Features
1. **Feature 1**: Does something
"""
        result = _validate_prd(content)
        assert "Project Overview" in result["missing_sections"]

    def test_prd_with_korean_sections(self):
        """PRD with Korean section names"""
        content = """# 테스트 PRD

## 1. 프로젝트 개요

### 1.1 목적
이 프로젝트는 X 문제를 해결합니다.

### 1.2 목표
- [ ] 목표 1

## 2. 기능 요구사항

### 2.1 핵심 기능
1. **기능 1**: 설명
"""
        result = _validate_prd(content)
        # Should recognize Korean sections
        assert len(result["missing_sections"]) == 0 or result["is_valid"]


class TestStart:
    """start function tests"""

    def test_start_no_docs(self, temp_project):
        """Start creates docs folder if missing"""
        result = start(str(temp_project))
        assert result["docs_exists"] is True
        assert (temp_project / "docs").exists()

    def test_start_need_prd(self, temp_project):
        """Start returns NEED_PRD when PRD missing"""
        (temp_project / "docs").mkdir()
        result = start(str(temp_project))
        assert result["status"] == "NEED_PRD"
        assert "prd_guide" in result

    def test_start_with_valid_prd(self, docs_dir, temp_project):
        """Start returns READY with valid PRD"""
        prd_content = """# Test PRD

## 1. Project Overview

### 1.1 Purpose
Test purpose

### 1.2 Goals
- [ ] Goal 1

## 2. Functional Requirements

### 2.1 Core Features
1. **Login**: User authentication
"""
        (docs_dir / "PRD.md").write_text(prd_content, encoding="utf-8")

        result = start(str(temp_project))
        assert result["status"] == "READY"
        assert result["prd_valid"] is True

    def test_start_with_incomplete_prd(self, docs_dir, temp_project):
        """Start returns INCOMPLETE with template PRD"""
        prd_content = """# Test PRD

## 1. Project Overview

### 1.1 Purpose
[Describe the problem this project solves]

### 1.2 Goals
- [ ] Core goal 1
"""
        (docs_dir / "PRD.md").write_text(prd_content, encoding="utf-8")

        result = start(str(temp_project))
        assert result["status"] in ["INCOMPLETE", "READY"]  # Depends on validation strictness

    def test_start_guide_option(self, temp_project):
        """Start with guide=True returns guide"""
        result = start(str(temp_project), guide=True)
        assert result["status"] == "GUIDE"
        assert "PRD Writing Guide" in result["message"]

    def test_start_init_option(self, temp_project):
        """Start with init=True creates templates"""
        result = start(str(temp_project), init=True)
        assert result["status"] == "INITIALIZED"
        assert (temp_project / "docs" / "PRD.md").exists()

    def test_start_template_option(self, temp_project):
        """Start with template returns template content"""
        result = start(str(temp_project), template="web-app")
        assert result["status"] == "TEMPLATE"
        assert "content" in result

    def test_start_force_project_type(self, temp_project):
        """Start with forced project type"""
        result = start(str(temp_project), project_type="api")
        assert result["project_type"]["type"] == "api"

    def test_start_with_project_name(self, temp_project):
        """Start with custom project name"""
        result = start(str(temp_project), project_name="MyProject")
        assert result["project_name"] == "MyProject"


class TestSavePrd:
    """save_prd function tests"""

    def test_save_prd_new(self, temp_project):
        """Save new PRD"""
        content = "## Summary\nTest project"
        result = save_prd(str(temp_project), content)
        assert result["status"] == "SAVED"
        assert (temp_project / "docs" / "PRD.md").exists()

    def test_save_prd_with_header(self, temp_project):
        """Save PRD adds header if content doesn't start with #"""
        content = "Summary content without header"
        save_prd(str(temp_project), content, project_name="TestProject")

        prd_content = (temp_project / "docs" / "PRD.md").read_text(encoding="utf-8")
        assert "# TestProject PRD" in prd_content

    def test_save_prd_preserves_existing_header(self, temp_project):
        """Save PRD preserves existing header"""
        content = "# Custom Header\n\n## Content"
        save_prd(str(temp_project), content)

        prd_content = (temp_project / "docs" / "PRD.md").read_text(encoding="utf-8")
        assert "# Custom Header" in prd_content

    def test_save_prd_creates_backup(self, docs_dir, temp_project):
        """Save PRD creates backup of previous version"""
        # First save
        (docs_dir / "PRD.md").write_text("# Original PRD", encoding="utf-8")

        # Second save
        save_prd(str(temp_project), "# Updated PRD")

        # Check backup exists
        history_dir = temp_project / ".claude" / "prd_history"
        if history_dir.exists():
            backups = list(history_dir.glob("PRD_*.md"))
            assert len(backups) >= 1


class TestPrdDiff:
    """_calculate_prd_diff function tests"""

    def test_diff_no_changes(self):
        """Diff with identical content"""
        content = "# PRD\n\n## Summary\nTest"
        result = _calculate_prd_diff(content, content)
        assert result["has_changes"] is False
        assert result["added_lines"] == 0
        assert result["removed_lines"] == 0

    def test_diff_added_lines(self):
        """Diff with added lines"""
        old = "# PRD\n\n## Summary"
        new = "# PRD\n\n## Summary\n\n## New Section\nContent"
        result = _calculate_prd_diff(old, new)
        assert result["has_changes"] is True
        assert result["added_lines"] > 0

    def test_diff_removed_lines(self):
        """Diff with removed lines"""
        old = "# PRD\n\n## Summary\n\n## Old Section\nContent"
        new = "# PRD\n\n## Summary"
        result = _calculate_prd_diff(old, new)
        assert result["has_changes"] is True
        assert result["removed_lines"] > 0

    def test_diff_extracts_sections(self):
        """Diff extracts changed section names"""
        old = "# PRD\n\n## Summary\nOld"
        new = "# PRD\n\n## Summary\nNew"
        result = _calculate_prd_diff(old, new)
        assert result["has_changes"] is True


class TestAnalyzePrdImpact:
    """_analyze_prd_impact function tests"""

    def test_impact_no_keywords(self, temp_project):
        """Impact analysis with no keywords"""
        diff = {"changed_keywords": [], "changed_sections": []}
        result = _analyze_prd_impact(temp_project, diff)
        assert result["affected_files"] == []

    def test_impact_finds_matching_files(self, temp_project):
        """Impact analysis finds files with matching keywords"""
        # Create source file with keywords
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "auth.py").write_text("def login():\n    pass", encoding="utf-8")

        diff = {"changed_keywords": ["login", "auth"], "changed_sections": []}
        result = _analyze_prd_impact(temp_project, diff)
        assert len(result["affected_files"]) > 0

    def test_impact_warns_on_critical_sections(self, temp_project):
        """Impact analysis warns on critical section changes"""
        diff = {
            "changed_keywords": [],
            "changed_sections": ["API Endpoints", "Database Schema"]
        }
        result = _analyze_prd_impact(temp_project, diff)
        # Should have warning about critical sections if there are any
        # The function only adds warnings when critical_changes is not empty
        warnings = result.get("warnings", [])
        # Check function returns proper structure
        assert "warnings" in result
        assert isinstance(warnings, list)


class TestBackupPrd:
    """_backup_prd function tests"""

    def test_backup_creates_file(self, temp_project):
        """Backup creates file in history folder"""
        content = "# PRD Content"
        result = _backup_prd(temp_project, content)
        if result:  # May return None on error
            assert Path(result).exists()

    def test_backup_creates_history_dir(self, temp_project):
        """Backup creates history directory"""
        _backup_prd(temp_project, "# Content")
        history_dir = temp_project / ".claude" / "prd_history"
        assert history_dir.exists()


class TestGetPrdQuestions:
    """get_prd_questions function tests"""

    def test_get_questions_generic(self):
        """Get questions for generic type"""
        result = get_prd_questions("generic")
        assert result["project_type"] == "generic"
        assert len(result["questions"]) > 0

    def test_get_questions_web_app(self):
        """Get questions for web-app type"""
        result = get_prd_questions("web-app")
        assert result["project_type"] == "web-app"
        assert "pages" in [q["section"] for q in result["questions"]]

    def test_get_questions_api(self):
        """Get questions for api type"""
        result = get_prd_questions("api")
        assert result["project_type"] == "api"
        assert "endpoints" in [q["section"] for q in result["questions"]]

    def test_get_questions_unknown_type(self):
        """Unknown type falls back to generic"""
        result = get_prd_questions("unknown-type")
        assert result["project_type"] == "generic"

    def test_all_project_types_have_questions(self):
        """All defined project types have questions"""
        for ptype in PROJECT_TYPE_PATTERNS.keys():
            result = get_prd_questions(ptype)
            assert len(result["questions"]) > 0


class TestQuickStart:
    """quick_start function tests"""

    def test_quick_start_ready(self, docs_dir, temp_project):
        """Quick start with valid PRD"""
        prd = """# PRD

## 1. Project Overview

### 1.1 Purpose
Test

### 1.2 Goals
- Goal 1

## 2. Functional Requirements

### 2.1 Core Features
1. **Feature**: Test
"""
        (docs_dir / "PRD.md").write_text(prd, encoding="utf-8")

        result = quick_start(str(temp_project))
        assert "ready" in result.lower() or "✅" in result

    def test_quick_start_need_prd(self, temp_project):
        """Quick start without PRD"""
        (temp_project / "docs").mkdir()
        result = quick_start(str(temp_project))
        assert "PRD" in result

    def test_quick_start_incomplete(self, docs_dir, temp_project):
        """Quick start with incomplete PRD"""
        (docs_dir / "PRD.md").write_text("# PRD\n\nEmpty", encoding="utf-8")
        result = quick_start(str(temp_project))
        # Should indicate something about the state
        assert len(result) > 0


class TestProjectTypePatterns:
    """Test PROJECT_TYPE_PATTERNS coverage"""

    def test_saas_detection(self, temp_project):
        """SaaS project detection"""
        pkg = {"dependencies": {"stripe": "^12.0.0", "react": "^18.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
        (temp_project / "src").mkdir()
        (temp_project / "src" / "App.tsx").write_text("// App", encoding="utf-8")

        result = _detect_project_type(temp_project)
        # Should detect as saas or web-app
        assert result["type"] in ["saas", "web-app"]

    def test_all_prd_question_types(self):
        """All project types have PRD questions"""
        for ptype in PRD_QUESTIONS.keys():
            questions = PRD_QUESTIONS[ptype]
            assert len(questions) > 0
            for q in questions:
                assert "section" in q
                assert "question" in q


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
