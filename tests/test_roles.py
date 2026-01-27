# -*- coding: utf-8 -*-
"""Roles module tests"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.roles import (
    VALID_ROLES,
    CLOUVEL_DIR,
    _load_config,
    _save_config,
    _parse_role_yaml,
    _generate_role_prompt,
)


@pytest.fixture
def temp_clouvel_dir(monkeypatch):
    """Create temporary clouvel directory"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / ".clouvel"
    temp_path.mkdir(parents=True)

    # Patch CLOUVEL_DIR and CONFIG_FILE
    import clouvel.tools.roles as roles_module
    monkeypatch.setattr(roles_module, "CLOUVEL_DIR", temp_path)
    monkeypatch.setattr(roles_module, "CONFIG_FILE", temp_path / "config.json")

    yield temp_path
    shutil.rmtree(temp_dir)


class TestValidRoles:
    """VALID_ROLES constant tests"""

    def test_roles_exist(self):
        """Roles list exists"""
        assert isinstance(VALID_ROLES, list)
        assert len(VALID_ROLES) > 0

    def test_contains_pm(self):
        """Contains PM role"""
        assert "pm" in VALID_ROLES

    def test_contains_cto(self):
        """Contains CTO role"""
        assert "cto" in VALID_ROLES

    def test_contains_cdo(self):
        """Contains CDO role"""
        assert "cdo" in VALID_ROLES

    def test_contains_cfo(self):
        """Contains CFO role"""
        assert "cfo" in VALID_ROLES

    def test_contains_cmo(self):
        """Contains CMO role"""
        assert "cmo" in VALID_ROLES

    def test_all_lowercase(self):
        """All roles are lowercase"""
        for role in VALID_ROLES:
            assert role == role.lower()


class TestLoadConfig:
    """_load_config function tests"""

    def test_returns_dict(self, temp_clouvel_dir):
        """Returns dictionary"""
        result = _load_config()
        assert isinstance(result, dict)

    def test_default_active_roles(self, temp_clouvel_dir):
        """Default has empty active_roles"""
        result = _load_config()
        assert "active_roles" in result
        assert result["active_roles"] == []

    def test_default_mode(self, temp_clouvel_dir):
        """Default mode is manual"""
        result = _load_config()
        assert "mode" in result
        assert result["mode"] == "manual"

    def test_loads_existing_config(self, temp_clouvel_dir):
        """Loads existing config file"""
        config_file = temp_clouvel_dir / "config.json"
        test_config = {"active_roles": ["pm", "cto"], "mode": "auto"}
        config_file.write_text(json.dumps(test_config), encoding="utf-8")

        result = _load_config()
        assert result["active_roles"] == ["pm", "cto"]
        assert result["mode"] == "auto"

    def test_handles_invalid_json(self, temp_clouvel_dir):
        """Returns default for invalid JSON"""
        config_file = temp_clouvel_dir / "config.json"
        config_file.write_text("invalid json{{{", encoding="utf-8")

        result = _load_config()
        assert result == {"active_roles": [], "mode": "manual"}


class TestSaveConfig:
    """_save_config function tests"""

    def test_saves_config(self, temp_clouvel_dir):
        """Saves config to file"""
        test_config = {"active_roles": ["pm"], "mode": "auto"}
        _save_config(test_config)

        config_file = temp_clouvel_dir / "config.json"
        assert config_file.exists()

        loaded = json.loads(config_file.read_text(encoding="utf-8"))
        assert loaded["active_roles"] == ["pm"]

    def test_creates_directory(self, temp_clouvel_dir):
        """Creates directory if not exists"""
        # Remove the directory
        shutil.rmtree(temp_clouvel_dir)

        test_config = {"active_roles": [], "mode": "manual"}
        _save_config(test_config)

        assert temp_clouvel_dir.exists()


class TestParseRoleYaml:
    """_parse_role_yaml function tests"""

    def test_parses_valid_yaml(self):
        """Parses valid YAML"""
        yaml_str = """
name: PM
icon: 📊
perspective: Product
"""
        result = _parse_role_yaml(yaml_str)
        assert result["name"] == "PM"
        assert result["icon"] == "📊"

    def test_returns_empty_for_invalid(self):
        """Returns empty dict for invalid YAML"""
        result = _parse_role_yaml("invalid: yaml: content: [[[")
        assert result == {}

    def test_parses_nested_structure(self):
        """Parses nested YAML structure"""
        yaml_str = """
name: CTO
principles:
  wrong:
    - Bad practice
  right:
    - Good practice
"""
        result = _parse_role_yaml(yaml_str)
        assert result["name"] == "CTO"
        assert "principles" in result
        assert result["principles"]["wrong"] == ["Bad practice"]


class TestGenerateRolePrompt:
    """_generate_role_prompt function tests"""

    def test_empty_data(self):
        """Returns empty for empty data"""
        result = _generate_role_prompt({})
        assert result == ""

    def test_basic_structure(self):
        """Generates basic structure"""
        role_data = {
            "name": "PM",
            "icon": "📊"
        }
        result = _generate_role_prompt(role_data)
        assert "📊 PM" in result

    def test_includes_persona(self):
        """Includes persona if provided"""
        role_data = {
            "name": "PM",
            "persona": "Product-focused leader"
        }
        result = _generate_role_prompt(role_data)
        assert "페르소나" in result
        assert "Product-focused leader" in result

    def test_includes_philosophy(self):
        """Includes philosophy if provided"""
        role_data = {
            "name": "CTO",
            "philosophy": "Technology excellence"
        }
        result = _generate_role_prompt(role_data)
        assert "철학" in result
        assert "Technology excellence" in result

    def test_includes_perspective(self):
        """Includes perspective if provided"""
        role_data = {
            "name": "CDO",
            "perspective": "User experience"
        }
        result = _generate_role_prompt(role_data)
        assert "관점" in result
        assert "User experience" in result

    def test_includes_principles(self):
        """Includes principles if provided"""
        role_data = {
            "name": "CFO",
            "principles": {
                "wrong": ["Overspend"],
                "right": ["Budget control"]
            }
        }
        result = _generate_role_prompt(role_data)
        assert "핵심 원칙" in result
        assert "❌ Overspend" in result
        assert "✅ Budget control" in result

    def test_includes_checklist(self):
        """Includes checklist if provided"""
        role_data = {
            "name": "PM",
            "checklist": {
                "Launch": ["Check metrics", "Notify users"]
            }
        }
        result = _generate_role_prompt(role_data)
        assert "체크리스트" in result
        assert "Launch" in result
        assert "Check metrics" in result

    def test_includes_never(self):
        """Includes never list if provided"""
        role_data = {
            "name": "PM",
            "never": ["Skip user research", "Ignore feedback"]
        }
        result = _generate_role_prompt(role_data)
        assert "절대 금지" in result
        assert "Skip user research" in result

    def test_includes_advice(self):
        """Includes advice if provided"""
        role_data = {
            "name": "PM",
            "advice": "Always prioritize user value"
        }
        result = _generate_role_prompt(role_data)
        assert "Always prioritize user value" in result

    def test_full_role_prompt(self):
        """Generates complete role prompt"""
        role_data = {
            "name": "PM",
            "icon": "📊",
            "persona": "Product leader",
            "philosophy": "User first",
            "perspective": "Business value",
            "principles": {
                "wrong": ["Ignore metrics"],
                "right": ["Data-driven decisions"]
            },
            "checklist": {
                "Daily": ["Review dashboard"]
            },
            "never": ["Skip testing"],
            "advice": "Stay curious"
        }
        result = _generate_role_prompt(role_data)

        assert "📊 PM" in result
        assert "Product leader" in result
        assert "User first" in result
        assert "Business value" in result
        assert "Ignore metrics" in result
        assert "Data-driven decisions" in result
        assert "Daily" in result
        assert "Skip testing" in result
        assert "Stay curious" in result


class TestRoleIntegration:
    """Integration tests for role functions"""

    def test_save_and_load_config(self, temp_clouvel_dir):
        """Save and load config works together"""
        test_config = {
            "active_roles": ["pm", "cto", "cdo"],
            "mode": "auto",
            "custom_setting": "value"
        }
        _save_config(test_config)

        loaded = _load_config()
        assert loaded["active_roles"] == ["pm", "cto", "cdo"]
        assert loaded["mode"] == "auto"
        assert loaded["custom_setting"] == "value"

    def test_multiple_saves(self, temp_clouvel_dir):
        """Multiple saves work correctly"""
        _save_config({"active_roles": ["pm"], "mode": "manual"})
        _save_config({"active_roles": ["cto", "cfo"], "mode": "auto"})

        loaded = _load_config()
        assert loaded["active_roles"] == ["cto", "cfo"]
        assert loaded["mode"] == "auto"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
