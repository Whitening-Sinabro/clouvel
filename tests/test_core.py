# -*- coding: utf-8 -*-
"""Core tools comprehensive tests - targeting 80%+ coverage"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.core import (
    can_code,
    scan_docs,
    analyze_docs,
    init_docs,
    _find_prd_file,
    _check_prd_sections,
    _check_tests,
    _check_file_tracking,
    REQUIRED_DOCS,
    REQUIRED_PRD_SECTIONS,
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


class TestFindPrdFile:
    """_find_prd_file function tests"""

    def test_find_prd_lowercase(self, docs_dir):
        """Find PRD.md file"""
        (docs_dir / "prd.md").write_text("# PRD", encoding="utf-8")
        result = _find_prd_file(docs_dir)
        assert result is not None
        assert result.name == "prd.md"

    def test_find_prd_uppercase(self, docs_dir):
        """Find PRD.MD file"""
        (docs_dir / "PRD.MD").write_text("# PRD", encoding="utf-8")
        result = _find_prd_file(docs_dir)
        assert result is not None

    def test_find_product_requirements(self, docs_dir):
        """Find product-requirements.md"""
        (docs_dir / "product-requirements.md").write_text("# PRD", encoding="utf-8")
        result = _find_prd_file(docs_dir)
        assert result is not None

    def test_find_product_requirement_doc(self, docs_dir):
        """Find ProductRequirement.md"""
        (docs_dir / "ProductRequirement.md").write_text("# PRD", encoding="utf-8")
        result = _find_prd_file(docs_dir)
        assert result is not None

    def test_no_prd_found(self, docs_dir):
        """No PRD file exists"""
        (docs_dir / "README.md").write_text("# README", encoding="utf-8")
        result = _find_prd_file(docs_dir)
        assert result is None

    def test_empty_docs_dir(self, docs_dir):
        """Empty docs directory"""
        result = _find_prd_file(docs_dir)
        assert result is None


class TestCheckPrdSections:
    """_check_prd_sections function tests"""

    def test_all_sections_present(self, docs_dir):
        """PRD with all required sections"""
        prd_content = """# PRD

## Scope
Project scope here.

## Non-Goals
What we won't do.

## Acceptance Criteria
- [ ] Feature works
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in found
        assert len(missing_crit) == 0

    def test_missing_acceptance_section(self, docs_dir):
        """PRD without acceptance criteria (critical)"""
        prd_content = """# PRD

## Overview
Something here.
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in missing_crit

    def test_korean_acceptance_section(self, docs_dir):
        """PRD with Korean acceptance criteria"""
        prd_content = """# PRD

## 완료 기준
- [ ] 기능 동작
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in found

    def test_dod_section(self, docs_dir):
        """PRD with Definition of Done section"""
        prd_content = """# PRD

## Definition of Done
- [ ] Tests pass
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in found

    def test_done_when_section(self, docs_dir):
        """PRD with 'Done when' section"""
        prd_content = """# PRD

## Done When
- [ ] All tests pass
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in found

    def test_file_read_error(self, docs_dir):
        """Handle file read error gracefully"""
        prd_path = docs_dir / "nonexistent.md"
        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert "acceptance" in missing_crit

    def test_missing_warn_sections(self, docs_dir):
        """PRD missing warning-level sections"""
        prd_content = """# PRD

## Acceptance Criteria
- [ ] Feature works
"""
        prd_path = docs_dir / "PRD.md"
        prd_path.write_text(prd_content, encoding="utf-8")

        found, missing_crit, missing_warn = _check_prd_sections(prd_path)
        assert len(missing_crit) == 0
        assert "scope" in missing_warn or "non_goals" in missing_warn


class TestCheckTests:
    """_check_tests function tests"""

    def test_python_test_files(self, temp_project):
        """Find test_*.py files"""
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("# test", encoding="utf-8")
        (tests_dir / "test_utils.py").write_text("# test", encoding="utf-8")

        count, files = _check_tests(temp_project)
        assert count >= 2  # At least our created files

    def test_pytest_style_tests(self, temp_project):
        """Find *_test.py files"""
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "main_test.py").write_text("# test", encoding="utf-8")

        count, files = _check_tests(temp_project)
        assert count >= 1

    def test_js_test_files(self, temp_project):
        """Find *.test.js files"""
        tests_dir = temp_project / "__tests__"
        tests_dir.mkdir()
        (tests_dir / "app.test.js").write_text("// test", encoding="utf-8")

        count, files = _check_tests(temp_project)
        assert count >= 1

    def test_spec_files(self, temp_project):
        """Find *.spec.ts files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "utils.spec.ts").write_text("// test", encoding="utf-8")

        count, files = _check_tests(temp_project)
        assert count >= 1

    def test_no_test_files(self, temp_project):
        """No test files in project - isolated temp dir"""
        # This tests an empty directory with no test subdirs
        count, files = _check_tests(temp_project)
        # Empty temp dir should have 0 tests
        assert count == 0

    def test_max_5_files_returned(self, temp_project):
        """Returns max 5 test files in returned list"""
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        for i in range(10):
            (tests_dir / f"test_{i}.py").write_text("# test", encoding="utf-8")

        count, files = _check_tests(temp_project)
        assert count >= 10  # At least our created files
        assert len(files) <= 5  # Max 5 in returned list


class TestCanCode:
    """can_code function tests"""

    @pytest.mark.asyncio
    async def test_no_docs_folder(self, temp_project):
        """BLOCK when docs folder doesn't exist"""
        result = await can_code(str(temp_project / "docs"))
        assert "BLOCK" in result[0].text

    @pytest.mark.asyncio
    async def test_empty_docs_folder(self, docs_dir, temp_project):
        """BLOCK when docs folder is empty"""
        result = await can_code(str(docs_dir))
        assert "BLOCK" in result[0].text

    @pytest.mark.asyncio
    async def test_prd_without_acceptance(self, docs_dir):
        """BLOCK when PRD exists but no acceptance section"""
        (docs_dir / "PRD.md").write_text("# PRD\n\nJust overview.", encoding="utf-8")
        result = await can_code(str(docs_dir))
        assert "BLOCK" in result[0].text

    @pytest.mark.asyncio
    async def test_prd_with_acceptance(self, docs_dir):
        """PASS when PRD has acceptance section"""
        (docs_dir / "PRD.md").write_text("# PRD\n\n## Acceptance Criteria\n- Test", encoding="utf-8")
        result = await can_code(str(docs_dir))
        assert "PASS" in result[0].text

    @pytest.mark.asyncio
    async def test_pass_with_warnings(self, docs_dir, temp_project):
        """PASS with warnings when optional docs missing"""
        (docs_dir / "PRD.md").write_text("# PRD\n\n## Acceptance Criteria\n- Test", encoding="utf-8")
        result = await can_code(str(docs_dir))
        # Should pass but may have warnings for missing architecture, tests, etc.
        assert "PASS" in result[0].text

    @pytest.mark.asyncio
    async def test_pass_with_tests(self, docs_dir, temp_project):
        """PASS showing test count"""
        (docs_dir / "PRD.md").write_text("# PRD\n\n## Acceptance Criteria\n- Test", encoding="utf-8")
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("# test", encoding="utf-8")

        result = await can_code(str(docs_dir))
        assert "PASS" in result[0].text
        # Check for test count in output
        text = result[0].text
        assert "1 test" in text or "tests" in text.lower()

    @pytest.mark.asyncio
    async def test_post_mode_no_new_files(self, temp_project):
        """POST mode with no new files"""
        result = await can_code(str(temp_project / "docs"), mode="post")
        # Either "No new files" or git error message
        assert "POST CHECK" in result[0].text

    @pytest.mark.asyncio
    async def test_all_docs_present(self, docs_dir, temp_project):
        """PASS with no warnings when all docs present"""
        (docs_dir / "PRD.md").write_text("# PRD\n\n## Acceptance\n- X\n## Scope\n- Y\n## Non-Goals\n- Z", encoding="utf-8")
        (docs_dir / "architecture.md").write_text("# Arch", encoding="utf-8")
        (docs_dir / "api.md").write_text("# API", encoding="utf-8")
        (docs_dir / "database.md").write_text("# DB", encoding="utf-8")
        (docs_dir / "verification.md").write_text("# Verify", encoding="utf-8")

        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("# test", encoding="utf-8")

        result = await can_code(str(docs_dir))
        assert "PASS" in result[0].text


class TestScanDocs:
    """scan_docs function tests"""

    @pytest.mark.asyncio
    async def test_scan_nonexistent(self, temp_project):
        """Scan nonexistent path"""
        result = await scan_docs(str(temp_project / "nonexistent"))
        assert "not found" in result[0].text.lower() or "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_scan_file_not_dir(self, docs_dir):
        """Scan a file instead of directory"""
        file_path = docs_dir / "test.txt"
        file_path.write_text("test", encoding="utf-8")
        result = await scan_docs(str(file_path))
        assert "not a directory" in result[0].text.lower() or "directory" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_scan_with_files(self, docs_dir):
        """Scan directory with files"""
        (docs_dir / "PRD.md").write_text("# PRD", encoding="utf-8")
        (docs_dir / "README.md").write_text("# README", encoding="utf-8")
        result = await scan_docs(str(docs_dir))
        assert "2" in result[0].text or "PRD" in result[0].text
        # Check deprecation warning
        assert "DEPRECATED" in result[0].text


class TestAnalyzeDocs:
    """analyze_docs function tests"""

    @pytest.mark.asyncio
    async def test_analyze_nonexistent(self, temp_project):
        """Analyze nonexistent path"""
        result = await analyze_docs(str(temp_project / "nonexistent"))
        assert "not found" in result[0].text.lower() or "not exist" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_analyze_with_all_docs(self, docs_dir):
        """Analyze with all required docs"""
        (docs_dir / "PRD.md").write_text("# PRD", encoding="utf-8")
        (docs_dir / "architecture.md").write_text("# Arch", encoding="utf-8")
        (docs_dir / "api.md").write_text("# API", encoding="utf-8")
        (docs_dir / "database.md").write_text("# DB", encoding="utf-8")
        (docs_dir / "verification.md").write_text("# Verify", encoding="utf-8")

        result = await analyze_docs(str(docs_dir))
        assert "100%" in result[0].text
        # Check deprecation warning
        assert "DEPRECATED" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_missing_docs(self, docs_dir):
        """Analyze with missing docs"""
        (docs_dir / "PRD.md").write_text("# PRD", encoding="utf-8")

        result = await analyze_docs(str(docs_dir))
        # Should show missing docs
        assert "missing" in result[0].text.lower() or "Missing" in result[0].text


class TestInitDocs:
    """init_docs function tests"""

    @pytest.mark.asyncio
    async def test_init_creates_all_templates(self, temp_project):
        """Init creates all template files"""
        result = await init_docs(str(temp_project), "TestProject")

        docs_dir = temp_project / "docs"
        assert docs_dir.exists()
        assert (docs_dir / "PRD.md").exists()
        assert (docs_dir / "ARCHITECTURE.md").exists()
        assert (docs_dir / "API.md").exists()
        assert (docs_dir / "DATABASE.md").exists()
        assert (docs_dir / "VERIFICATION.md").exists()
        # Check deprecation warning
        assert "DEPRECATED" in result[0].text

    @pytest.mark.asyncio
    async def test_init_with_project_name(self, temp_project):
        """Init includes project name in templates"""
        await init_docs(str(temp_project), "MyAwesomeProject")

        prd_content = (temp_project / "docs" / "PRD.md").read_text(encoding="utf-8")
        assert "MyAwesomeProject" in prd_content

    @pytest.mark.asyncio
    async def test_init_skips_existing(self, temp_project):
        """Init doesn't overwrite existing files"""
        docs_dir = temp_project / "docs"
        docs_dir.mkdir()
        (docs_dir / "PRD.md").write_text("Custom PRD", encoding="utf-8")

        await init_docs(str(temp_project), "Test")

        # Original content should remain
        content = (docs_dir / "PRD.md").read_text(encoding="utf-8")
        assert content == "Custom PRD"

    @pytest.mark.asyncio
    async def test_init_creates_parent_dirs(self, temp_project):
        """Init creates parent directories if needed"""
        nested = temp_project / "nested" / "project"
        nested.mkdir(parents=True)

        result = await init_docs(str(nested), "Test")
        assert (nested / "docs" / "PRD.md").exists()


class TestRequiredDocsPatterns:
    """Test REQUIRED_DOCS patterns work correctly"""

    def test_prd_patterns(self, docs_dir):
        """PRD detection patterns"""
        test_cases = [
            ("prd.md", True),
            ("PRD.md", True),
            ("product-requirements.md", True),
            ("ProductRequirement.md", True),
            ("readme.md", False),
            ("architecture.md", False),
        ]

        for filename, should_match in test_cases:
            # Clear and create single file
            for f in docs_dir.iterdir():
                f.unlink()
            (docs_dir / filename).write_text("# Doc", encoding="utf-8")

            result = _find_prd_file(docs_dir)
            if should_match:
                assert result is not None, f"{filename} should be detected as PRD"
            else:
                assert result is None, f"{filename} should not be detected as PRD"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
