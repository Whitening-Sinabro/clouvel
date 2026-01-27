# -*- coding: utf-8 -*-
"""Docs tools comprehensive tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.docs import (
    get_prd_template,
    list_templates,
    write_prd_section,
    get_prd_guide,
    get_verify_checklist,
    get_setup_guide,
    TEMPLATES,
    _get_template_path,
    _load_template,
)


class TestTemplates:
    """TEMPLATES constant tests"""

    def test_templates_exist(self):
        """Templates dictionary exists"""
        assert len(TEMPLATES) > 0

    def test_all_templates_have_required_keys(self):
        """All templates have name, layouts, description"""
        for key, template in TEMPLATES.items():
            assert "name" in template
            assert "layouts" in template
            assert "description" in template

    def test_all_templates_have_standard_layout(self):
        """All templates support standard layout"""
        for key, template in TEMPLATES.items():
            assert "standard" in template["layouts"]


class TestGetTemplatePath:
    """_get_template_path function tests"""

    def test_get_path_returns_path(self):
        """Returns Path object"""
        result = _get_template_path("web-app", "standard")
        assert isinstance(result, Path)

    def test_get_path_includes_template_name(self):
        """Path includes template name"""
        result = _get_template_path("api", "lite")
        assert "api" in str(result)
        assert "lite" in str(result)


class TestLoadTemplate:
    """_load_template function tests"""

    def test_load_nonexistent(self):
        """Loading nonexistent template returns None"""
        result = _load_template("nonexistent-template", "nonexistent-layout")
        assert result is None

    def test_load_existing_if_available(self):
        """Loading existing template returns content or None"""
        result = _load_template("generic", "standard")
        # Either returns content string or None
        assert result is None or isinstance(result, str)


class TestGetPrdTemplate:
    """get_prd_template function tests"""

    @pytest.mark.asyncio
    async def test_get_template_generic(self):
        """Get generic template"""
        result = await get_prd_template("TestProject", "/tmp/prd.md")
        assert "TestProject" in result[0].text
        assert "DEPRECATED" in result[0].text

    @pytest.mark.asyncio
    async def test_get_template_with_template_type(self):
        """Get template with specific type"""
        result = await get_prd_template("Test", "/tmp/prd.md", template="api")
        # Should return some content
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_get_template_with_layout(self):
        """Get template with specific layout"""
        result = await get_prd_template("Test", "/tmp/prd.md", layout="lite")
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_get_template_includes_date(self):
        """Get template includes current date"""
        result = await get_prd_template("Test", "/tmp/prd.md")
        # Should contain date in some format
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", result[0].text)


class TestListTemplates:
    """list_templates function tests"""

    @pytest.mark.asyncio
    async def test_list_returns_content(self):
        """List returns template content"""
        result = await list_templates()
        assert "Template" in result[0].text

    @pytest.mark.asyncio
    async def test_list_includes_all_templates(self):
        """List includes all template types"""
        result = await list_templates()
        for key in TEMPLATES.keys():
            assert key in result[0].text


class TestWritePrdSection:
    """write_prd_section function tests"""

    @pytest.mark.asyncio
    async def test_write_summary_section(self):
        """Write summary section"""
        result = await write_prd_section("summary", "Test content")
        assert "summary" in result[0].text.lower()
        assert "Test content" in result[0].text

    @pytest.mark.asyncio
    async def test_write_principles_section(self):
        """Write principles section"""
        result = await write_prd_section("principles", "Core principle 1")
        assert "principle" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_write_input_spec_section(self):
        """Write input_spec section"""
        result = await write_prd_section("input_spec", "User input")
        assert "input" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_write_output_spec_section(self):
        """Write output_spec section"""
        result = await write_prd_section("output_spec", "API response")
        assert "output" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_write_errors_section(self):
        """Write errors section"""
        result = await write_prd_section("errors", "Error handling")
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_write_unknown_section(self):
        """Write unknown section returns unknown message"""
        result = await write_prd_section("nonexistent", "Content")
        assert "unknown" in result[0].text.lower() or "Unknown" in result[0].text

    @pytest.mark.asyncio
    async def test_write_empty_content(self):
        """Write section with empty content"""
        result = await write_prd_section("summary", "")
        assert "required" in result[0].text.lower() or "(Input required)" in result[0].text


class TestGetPrdGuide:
    """get_prd_guide function tests"""

    @pytest.mark.asyncio
    async def test_get_guide_returns_content(self):
        """Get guide returns guide content"""
        result = await get_prd_guide()
        assert "PRD" in result[0].text
        assert "DEPRECATED" in result[0].text

    @pytest.mark.asyncio
    async def test_get_guide_includes_steps(self):
        """Get guide includes writing steps"""
        result = await get_prd_guide()
        assert "Step" in result[0].text or "step" in result[0].text


class TestGetVerifyChecklist:
    """get_verify_checklist function tests"""

    @pytest.mark.asyncio
    async def test_get_checklist_returns_content(self):
        """Get checklist returns content"""
        result = await get_verify_checklist()
        assert "Checklist" in result[0].text or "checklist" in result[0].text

    @pytest.mark.asyncio
    async def test_get_checklist_includes_items(self):
        """Get checklist includes checkbox items"""
        result = await get_verify_checklist()
        assert "[ ]" in result[0].text


class TestGetSetupGuide:
    """get_setup_guide function tests"""

    @pytest.mark.asyncio
    async def test_get_desktop_guide(self):
        """Get desktop setup guide"""
        result = await get_setup_guide("desktop")
        assert "Desktop" in result[0].text or "desktop" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_code_guide(self):
        """Get code (CLI) setup guide"""
        result = await get_setup_guide("code")
        assert "Code" in result[0].text or "CLI" in result[0].text

    @pytest.mark.asyncio
    async def test_get_vscode_guide(self):
        """Get VS Code setup guide"""
        result = await get_setup_guide("vscode")
        assert "VS Code" in result[0].text or "vscode" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_cursor_guide(self):
        """Get Cursor setup guide"""
        result = await get_setup_guide("cursor")
        assert "Cursor" in result[0].text or "cursor" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_all_guides(self):
        """Get all setup guides"""
        result = await get_setup_guide("all")
        assert "Desktop" in result[0].text
        assert "VS Code" in result[0].text or "Code" in result[0].text

    @pytest.mark.asyncio
    async def test_get_unknown_platform(self):
        """Get unknown platform returns error"""
        result = await get_setup_guide("unknown-platform")
        assert "Unknown" in result[0].text or "unknown" in result[0].text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
