# -*- coding: utf-8 -*-
"""Manager personas module tests"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.prompts.personas import (
    PERSONAS,
    get_persona,
    get_all_personas_summary,
)


class TestPersonasConstant:
    """PERSONAS constant tests"""

    def test_personas_exist(self):
        """Personas dictionary exists"""
        assert isinstance(PERSONAS, dict)
        assert len(PERSONAS) > 0

    def test_has_pm(self):
        """Has PM persona"""
        assert "PM" in PERSONAS

    def test_has_cto(self):
        """Has CTO persona"""
        assert "CTO" in PERSONAS

    def test_has_qa(self):
        """Has QA persona"""
        assert "QA" in PERSONAS

    def test_has_cso(self):
        """Has CSO persona"""
        assert "CSO" in PERSONAS

    def test_has_cdo(self):
        """Has CDO persona"""
        assert "CDO" in PERSONAS

    def test_has_cmo(self):
        """Has CMO persona"""
        assert "CMO" in PERSONAS

    def test_has_cfo(self):
        """Has CFO persona"""
        assert "CFO" in PERSONAS

    def test_has_error(self):
        """Has ERROR persona"""
        assert "ERROR" in PERSONAS

    def test_total_personas(self):
        """Has 8 total personas"""
        assert len(PERSONAS) == 8


class TestPersonaStructure:
    """Persona structure tests"""

    def test_all_have_emoji(self):
        """All personas have emoji"""
        for key, persona in PERSONAS.items():
            assert "emoji" in persona, f"{key} missing emoji"
            assert len(persona["emoji"]) > 0

    def test_all_have_title(self):
        """All personas have title"""
        for key, persona in PERSONAS.items():
            assert "title" in persona, f"{key} missing title"

    def test_all_have_years(self):
        """All personas have years experience"""
        for key, persona in PERSONAS.items():
            assert "years" in persona, f"{key} missing years"
            assert persona["years"] >= 10, f"{key} should have 10+ years"

    def test_all_have_expertise(self):
        """All personas have expertise list"""
        for key, persona in PERSONAS.items():
            assert "expertise" in persona, f"{key} missing expertise"
            assert len(persona["expertise"]) >= 3

    def test_all_have_probing_questions(self):
        """All personas have probing questions"""
        for key, persona in PERSONAS.items():
            assert "probing_questions" in persona, f"{key} missing probing_questions"


class TestGetPersona:
    """get_persona function tests"""

    def test_get_pm(self):
        """Gets PM persona"""
        result = get_persona("PM")
        assert result is not None
        assert result["title"] == "Product Manager"

    def test_get_cto(self):
        """Gets CTO persona"""
        result = get_persona("CTO")
        assert result is not None
        assert result["title"] == "Chief Technology Officer"

    def test_case_insensitive(self):
        """Works case insensitively"""
        pm = get_persona("pm")
        PM = get_persona("PM")
        assert pm == PM

    def test_unknown_returns_empty(self):
        """Unknown key returns empty dict"""
        result = get_persona("UNKNOWN_MANAGER")
        assert result == {}


class TestGetAllPersonasSummary:
    """get_all_personas_summary function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = get_all_personas_summary()
        assert isinstance(result, str)

    def test_includes_all_managers(self):
        """Includes all manager keys"""
        result = get_all_personas_summary()
        for key in PERSONAS:
            assert key in result

    def test_includes_emojis(self):
        """Includes emojis"""
        result = get_all_personas_summary()
        assert "👔" in result  # PM emoji
        assert "🛠️" in result  # CTO emoji

    def test_includes_years(self):
        """Includes years experience"""
        result = get_all_personas_summary()
        assert "years" in result

    def test_includes_expertise(self):
        """Includes expertise"""
        result = get_all_personas_summary()
        assert "Expertise" in result


class TestPersonasIntegration:
    """Integration tests for personas"""

    def test_pm_has_complete_structure(self):
        """PM has complete structure"""
        pm = get_persona("PM")

        assert "emoji" in pm
        assert "title" in pm
        assert "years" in pm
        assert "background" in pm
        assert "expertise" in pm
        assert "ai_perspective" in pm
        assert "personality" in pm
        assert "communication" in pm
        assert "probing_questions" in pm
        assert "interaction_rules" in pm

    def test_probing_questions_categories(self):
        """Each persona has multiple question categories"""
        for key, persona in PERSONAS.items():
            pq = persona["probing_questions"]
            assert len(pq) >= 3, f"{key} should have at least 3 question categories"

    def test_communication_pet_phrases(self):
        """Each persona has pet phrases"""
        for key, persona in PERSONAS.items():
            comm = persona["communication"]
            assert "pet_phrases" in comm, f"{key} missing pet_phrases"
            assert len(comm["pet_phrases"]) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
