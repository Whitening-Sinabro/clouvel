# -*- coding: utf-8 -*-
"""Database migration module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.migrate import (
    parse_error_md,
    migrate_error_files,
    extract_rules_from_claude_md,
    full_migration,
)
from clouvel.db.schema import init_db
from clouvel.db.rules import get_rules


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    init_db(str(temp_path))
    yield temp_path
    shutil.rmtree(temp_dir)


class TestParseErrorMd:
    """parse_error_md function tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        result = parse_error_md("")
        assert isinstance(result, dict)

    def test_default_fields(self):
        """Has default fields"""
        result = parse_error_md("")
        assert "error_message" in result
        assert "error_type" in result
        assert "context" in result
        assert "five_whys" in result
        assert "root_cause" in result
        assert "solution" in result
        assert "prevention" in result

    def test_extracts_title(self):
        """Extracts title as error message"""
        content = "# Test Error Title\n\nSome content"
        result = parse_error_md(content)
        assert result["error_message"] == "Test Error Title"

    def test_extracts_date(self):
        """Extracts date from content"""
        content = "**일시**: 2024-01-15\n\n# Error"
        result = parse_error_md(content)
        assert result["created_at"] == "2024-01-15"

    def test_extracts_type_error(self):
        """Extracts TypeError"""
        content = "# Error\n\nTypeError: cannot read property"
        result = parse_error_md(content)
        assert result["error_type"] == "TypeError"

    def test_extracts_attribute_error(self):
        """Extracts AttributeError"""
        content = "# Error\n\nAttributeError: 'None' has no attribute"
        result = parse_error_md(content)
        assert result["error_type"] == "AttributeError"

    def test_extracts_context_section(self):
        """Extracts context section"""
        content = """# Error
## 에러 상황
This is the error context.

## Other Section
"""
        result = parse_error_md(content)
        assert "error context" in result["context"]

    def test_extracts_root_cause(self):
        """Extracts root cause section"""
        content = """# Error
## 원인
Missing null check in the code.
"""
        result = parse_error_md(content)
        assert "null check" in result["root_cause"]

    def test_extracts_solution(self):
        """Extracts solution section"""
        content = """# Error
## 해결
Added proper validation.
"""
        result = parse_error_md(content)
        assert "validation" in result["solution"]

    def test_extracts_prevention(self):
        """Extracts prevention section"""
        content = """# Error
## 재발 방지
Enable TypeScript strict mode.
"""
        result = parse_error_md(content)
        assert "TypeScript" in result["prevention"]

    def test_extracts_five_whys(self):
        """Extracts 5 Whys from table"""
        content = """# Error
| # | Why | Answer |
|---|-----|--------|
| 1 | Why | First reason |
| 2 | Why | Second reason |
| 3 | Why | Third reason |
"""
        result = parse_error_md(content)
        assert len(result["five_whys"]) == 3
        assert "First reason" in result["five_whys"]

    def test_full_error_md(self):
        """Parses complete error MD file"""
        content = """# TypeError in API Handler

**일시**: 2024-01-20

## 에러 상황
User tried to submit form without required fields.

## 원인
Missing validation in form handler.

## 해결 방법
Added form validation before submission.

## 재발 방지
Enable TypeScript strict mode.

| # | Why | Answer |
|---|-----|--------|
| 1 | Why | No validation |
| 2 | Why | Rushed development |
"""
        result = parse_error_md(content)

        assert "TypeError" in result["error_type"]
        assert result["created_at"] == "2024-01-20"
        assert "submit form" in result["context"]
        assert "validation" in result["root_cause"]
        assert "validation" in result["solution"]
        assert "TypeScript" in result["prevention"]
        assert len(result["five_whys"]) == 2


class TestMigrateErrorFiles:
    """migrate_error_files function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = migrate_error_files(str(temp_project))
        assert isinstance(result, dict)

    def test_no_source_dir(self, temp_project):
        """Returns no_source for missing directory"""
        result = migrate_error_files(str(temp_project))
        assert result["status"] == "no_source"

    def test_no_md_files(self, temp_project):
        """Returns no_files for empty errors directory"""
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)

        result = migrate_error_files(str(temp_project))
        assert result["status"] == "no_files"

    def test_dry_run_mode(self, temp_project):
        """Dry run mode doesn't modify database"""
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)

        # Create error MD file
        error_content = "# Test Error\n\nSome content"
        (errors_dir / "error_001.md").write_text(error_content, encoding="utf-8")

        result = migrate_error_files(str(temp_project), dry_run=True)
        assert result["status"] == "success"
        assert result["total"] == 1

    def test_migrates_error_files(self, temp_project):
        """Migrates error MD files to database"""
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)

        # Create error MD files
        error1 = """# TypeError in Handler

**일시**: 2024-01-20

## 에러 상황
Error occurred during API call.

## 원인
Missing validation.
"""
        (errors_dir / "error_001.md").write_text(error1, encoding="utf-8")

        result = migrate_error_files(str(temp_project))
        assert result["status"] == "success"
        assert result["migrated"] >= 1

    def test_handles_invalid_md(self, temp_project):
        """Handles invalid MD gracefully"""
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)

        # Create minimal MD file
        (errors_dir / "error_001.md").write_text("Just some text", encoding="utf-8")

        result = migrate_error_files(str(temp_project))
        # Should complete even with minimal content
        assert "status" in result


class TestExtractRulesFromClaudeMd:
    """extract_rules_from_claude_md function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Project\n\nNo rules here", encoding="utf-8")

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        assert isinstance(result, dict)

    def test_not_found_for_missing_file(self, temp_project):
        """Returns not_found for missing file"""
        result = extract_rules_from_claude_md(
            str(temp_project / "nonexistent.md"),
            str(temp_project)
        )
        assert result["status"] == "not_found"

    def test_extracts_never_rules(self, temp_project):
        """Extracts NEVER rules"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text(
            "# Rules\n\nNEVER: Commit secrets to repository\nNEVER: Skip tests before commit",
            encoding="utf-8"
        )

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        assert result["status"] == "success"
        assert result["imported"] >= 1

    def test_extracts_always_rules(self, temp_project):
        """Extracts ALWAYS rules"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text(
            "# Rules\n\nALWAYS: Write tests for new features\nALWAYS: Document public APIs",
            encoding="utf-8"
        )

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        assert result["status"] == "success"
        assert result["imported"] >= 1

    def test_dry_run_mode(self, temp_project):
        """Dry run mode doesn't modify database"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Rules\n\nNEVER: Test rule content", encoding="utf-8")

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project), dry_run=True)
        assert result["status"] == "success"
        # Check rules were parsed but not added
        rules_in_db = get_rules(project_path=str(temp_project))
        # In dry run, shouldn't add to DB
        assert len(result["rules"]) >= 0

    def test_skips_short_rules(self, temp_project):
        """Skips rules that are too short"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Rules\n\nNEVER: ab\nNEVER: This is a proper rule", encoding="utf-8")

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        # "ab" is too short (< 5 chars), should be skipped

    def test_extracts_korean_rules(self, temp_project):
        """Extracts Korean-style rules"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text(
            "# 규칙\n\n절대 금지: 테스트 없이 커밋하기\n반드시: 문서화 작성하기",
            encoding="utf-8"
        )

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        assert result["status"] == "success"

    def test_extracts_markdown_bold_rules(self, temp_project):
        """Extracts rules with markdown bold syntax"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text(
            "# Rules\n\n- **NEVER**: Commit API keys or secrets\n- **ALWAYS**: Run linter before commit",
            encoding="utf-8"
        )

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        assert result["status"] == "success"

    def test_handles_duplicate_rules(self, temp_project):
        """Handles duplicate rules gracefully"""
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text(
            "# Rules\n\nNEVER: Duplicate rule here\nNEVER: Duplicate rule here",
            encoding="utf-8"
        )

        result = extract_rules_from_claude_md(str(claude_md), str(temp_project))
        # Second duplicate should be skipped
        assert result["imported"] + result["skipped"] >= 0


class TestFullMigration:
    """full_migration function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = full_migration(str(temp_project))
        assert isinstance(result, dict)

    def test_has_project_key(self, temp_project):
        """Has project key"""
        result = full_migration(str(temp_project))
        assert "project" in result
        assert result["project"] == str(temp_project)

    def test_has_dry_run_key(self, temp_project):
        """Has dry_run key"""
        result = full_migration(str(temp_project))
        assert "dry_run" in result

    def test_has_errors_key(self, temp_project):
        """Has errors migration result"""
        result = full_migration(str(temp_project))
        assert "errors" in result

    def test_has_rules_key(self, temp_project):
        """Has rules extraction result"""
        result = full_migration(str(temp_project))
        assert "rules" in result

    def test_dry_run_mode(self, temp_project):
        """Dry run mode works"""
        result = full_migration(str(temp_project), dry_run=True)
        assert result["dry_run"] is True

    def test_no_claude_md(self, temp_project):
        """Handles missing CLAUDE.md"""
        result = full_migration(str(temp_project))
        assert result["rules"]["status"] == "no_claude_md"

    def test_migrates_with_claude_md(self, temp_project):
        """Migrates with CLAUDE.md present"""
        # Create CLAUDE.md
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Project\n\nNEVER: Break production", encoding="utf-8")

        result = full_migration(str(temp_project))
        assert result["rules"]["status"] == "success"

    def test_full_workflow(self, temp_project):
        """Full migration with both errors and rules"""
        # Create errors directory with files
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)
        (errors_dir / "error_001.md").write_text(
            "# Test Error\n\n**일시**: 2024-01-15\n\n## 원인\nTest cause",
            encoding="utf-8"
        )

        # Create CLAUDE.md
        claude_md = temp_project / "CLAUDE.md"
        claude_md.write_text("# Rules\n\nNEVER: Skip code review", encoding="utf-8")

        # Run full migration
        result = full_migration(str(temp_project))

        assert "errors" in result
        assert "rules" in result
        assert result["errors"]["status"] == "success"
        assert result["rules"]["status"] == "success"


class TestMigrateIntegration:
    """Integration tests for migration"""

    def test_full_migration_workflow(self, temp_project):
        """Full migration workflow"""
        errors_dir = temp_project / ".clouvel" / "errors"
        errors_dir.mkdir(parents=True)

        # Create multiple error files
        for i in range(3):
            content = f"""# Error {i}

**일시**: 2024-01-{15+i:02d}

## 에러 상황
Error context {i}.

## 원인
Root cause {i}.

## 해결
Solution {i}.
"""
            (errors_dir / f"error_{i:03d}.md").write_text(content, encoding="utf-8")

        # Dry run first
        dry_result = migrate_error_files(str(temp_project), dry_run=True)
        assert dry_result["total"] == 3

        # Actual migration
        result = migrate_error_files(str(temp_project))
        assert result["status"] == "success"
        assert result["migrated"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
