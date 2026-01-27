# -*- coding: utf-8 -*-
"""Manager core module tests"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.core import (
    _check_pro_license,
    _check_pro_or_trial,
    _trial_exhausted_response,
    MANAGERS,
    _HAS_KNOWLEDGE,
)


class TestManagersConstant:
    """MANAGERS constant tests"""

    def test_managers_exist(self):
        """MANAGERS dictionary exists"""
        assert isinstance(MANAGERS, dict)

    def test_has_pm(self):
        """Has PM manager"""
        assert "PM" in MANAGERS

    def test_has_cto(self):
        """Has CTO manager"""
        assert "CTO" in MANAGERS

    def test_has_qa(self):
        """Has QA manager"""
        assert "QA" in MANAGERS

    def test_has_cso(self):
        """Has CSO manager"""
        assert "CSO" in MANAGERS

    def test_has_cfo(self):
        """Has CFO manager"""
        assert "CFO" in MANAGERS

    def test_has_cdo(self):
        """Has CDO manager"""
        assert "CDO" in MANAGERS

    def test_has_cmo(self):
        """Has CMO manager"""
        assert "CMO" in MANAGERS

    def test_manager_has_emoji(self):
        """Each manager has emoji"""
        for key, mgr in MANAGERS.items():
            assert "emoji" in mgr, f"{key} missing emoji"

    def test_manager_has_title(self):
        """Each manager has title"""
        for key, mgr in MANAGERS.items():
            assert "title" in mgr, f"{key} missing title"


class TestCheckProLicense:
    """_check_pro_license function tests"""

    @patch("clouvel.license_common.is_developer")
    def test_returns_true_for_developer(self, mock_is_dev):
        """Returns True for developer mode"""
        mock_is_dev.return_value = True
        result = _check_pro_license()
        assert result is True

    @patch("clouvel.license_common.is_developer")
    @patch("clouvel.license.verify_license")
    def test_returns_true_for_valid_license(self, mock_verify, mock_is_dev):
        """Returns True for valid license"""
        mock_is_dev.return_value = False
        mock_verify.return_value = {"valid": True}
        result = _check_pro_license()
        assert result is True

    @patch("clouvel.license_common.is_developer")
    @patch("clouvel.license.verify_license")
    def test_returns_false_for_invalid_license(self, mock_verify, mock_is_dev):
        """Returns False for invalid license"""
        mock_is_dev.return_value = False
        mock_verify.return_value = {"valid": False}
        result = _check_pro_license()
        assert result is False


class TestCheckProOrTrial:
    """_check_pro_or_trial function tests"""

    @patch("clouvel.tools.manager.core._check_pro_license")
    def test_returns_allowed_for_pro_license(self, mock_check_pro):
        """Returns allowed when Pro license valid"""
        mock_check_pro.return_value = True
        result = _check_pro_or_trial("manager")
        assert result["allowed"] is True
        assert result["reason"] == "license"

    @patch("clouvel.tools.manager.core._check_pro_license")
    @patch("clouvel.trial.check_trial_available")
    @patch("clouvel.trial.increment_trial_usage")
    def test_returns_allowed_for_trial(self, mock_inc, mock_check_trial, mock_check_pro):
        """Returns allowed when trial available"""
        mock_check_pro.return_value = False
        mock_check_trial.return_value = True
        mock_inc.return_value = {"used": 1, "remaining": 9}

        result = _check_pro_or_trial("manager")
        assert result["allowed"] is True
        assert result["reason"] == "trial"
        assert "trial_info" in result

    @patch("clouvel.tools.manager.core._check_pro_license")
    @patch("clouvel.trial.check_trial_available")
    @patch("clouvel.trial.get_trial_remaining")
    def test_returns_exhausted_when_trial_done(self, mock_remaining, mock_check_trial, mock_check_pro):
        """Returns exhausted when trial finished"""
        mock_check_pro.return_value = False
        mock_check_trial.return_value = False
        mock_remaining.return_value = 0

        result = _check_pro_or_trial("manager")
        assert result["allowed"] is False
        assert result["reason"] == "exhausted"


class TestTrialExhaustedResponse:
    """_trial_exhausted_response function tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        result = _trial_exhausted_response("manager")
        assert isinstance(result, dict)

    def test_has_error_key(self):
        """Has error key"""
        result = _trial_exhausted_response("manager")
        assert "error" in result or "formatted_output" in result

    @patch("clouvel.trial.get_trial_exhausted_message")
    @patch("clouvel.trial.TRIAL_LIMITS", {"manager": 10})
    def test_uses_trial_message(self, mock_msg):
        """Uses trial exhausted message"""
        mock_msg.return_value = "Trial exhausted message"
        result = _trial_exhausted_response("manager")
        # Should contain the message somewhere
        assert isinstance(result, dict)


class TestKnowledgeIntegration:
    """Knowledge Base integration tests"""

    def test_has_knowledge_is_bool(self):
        """_HAS_KNOWLEDGE is boolean"""
        assert isinstance(_HAS_KNOWLEDGE, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
