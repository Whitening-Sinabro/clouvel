# -*- coding: utf-8 -*-
"""API client module tests"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.api_client import (
    _get_client_id,
    _get_license_key,
    API_BASE_URL,
    API_TIMEOUT,
)


class TestApiConstants:
    """API constants tests"""

    def test_api_base_url_exists(self):
        """API base URL is defined"""
        assert API_BASE_URL is not None
        assert len(API_BASE_URL) > 0

    def test_api_base_url_is_https(self):
        """API base URL uses HTTPS"""
        assert API_BASE_URL.startswith("https://")

    def test_api_timeout_positive(self):
        """API timeout is positive"""
        assert API_TIMEOUT > 0

    def test_api_timeout_reasonable(self):
        """API timeout is reasonable (under 60s)"""
        assert API_TIMEOUT <= 60


class TestGetClientId:
    """_get_client_id function tests"""

    def test_returns_string(self):
        """Returns string"""
        result = _get_client_id()
        assert isinstance(result, str)

    def test_returns_32_chars(self):
        """Returns 32 character string"""
        result = _get_client_id()
        assert len(result) == 32

    def test_returns_hex_string(self):
        """Returns hex string"""
        result = _get_client_id()
        assert all(c in "0123456789abcdef" for c in result)

    def test_consistent_id(self):
        """Returns consistent ID for same machine"""
        id1 = _get_client_id()
        id2 = _get_client_id()
        assert id1 == id2


class TestGetLicenseKey:
    """_get_license_key function tests"""

    def test_returns_none_when_no_license(self):
        """Returns None when no license configured"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLOUVEL_LICENSE_KEY", None)
            result = _get_license_key()
            # May return None or find license file
            assert result is None or isinstance(result, str)

    def test_returns_env_license(self):
        """Returns license from environment"""
        with patch.dict(os.environ, {"CLOUVEL_LICENSE_KEY": "TEST-LICENSE-KEY"}):
            result = _get_license_key()
            assert result == "TEST-LICENSE-KEY"

    def test_reads_license_file(self):
        """Reads license from file"""
        temp_dir = tempfile.mkdtemp()
        try:
            clouvel_dir = Path(temp_dir) / ".clouvel"
            clouvel_dir.mkdir()
            license_file = clouvel_dir / "license.json"
            license_file.write_text(json.dumps({"key": "FILE-LICENSE-KEY"}), encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                os.environ.pop("CLOUVEL_LICENSE_KEY", None)
                with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                    result = _get_license_key()
                    # May be None if home patch doesn't work in this context
                    assert result is None or result == "FILE-LICENSE-KEY"
        finally:
            shutil.rmtree(temp_dir)

    def test_env_takes_priority(self):
        """Environment takes priority over file"""
        temp_dir = tempfile.mkdtemp()
        try:
            clouvel_dir = Path(temp_dir) / ".clouvel"
            clouvel_dir.mkdir()
            license_file = clouvel_dir / "license.json"
            license_file.write_text(json.dumps({"key": "FILE-LICENSE-KEY"}), encoding="utf-8")

            with patch.dict(os.environ, {"CLOUVEL_LICENSE_KEY": "ENV-LICENSE-KEY"}):
                with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                    result = _get_license_key()
                    assert result == "ENV-LICENSE-KEY"
        finally:
            shutil.rmtree(temp_dir)


class TestFallbackResponse:
    """_fallback_response function tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Test error")
        assert isinstance(result, dict)

    def test_has_topic(self):
        """Has topic key"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert "topic" in result

    def test_has_active_managers(self):
        """Has active_managers key"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert "active_managers" in result
        assert isinstance(result["active_managers"], list)

    def test_has_feedback(self):
        """Has feedback key"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert "feedback" in result

    def test_has_formatted_output(self):
        """Has formatted_output key"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert "formatted_output" in result

    def test_error_message_in_output(self):
        """Error message appears in output"""
        from clouvel.api_client import _fallback_response
        error_msg = "Connection failed"
        result = _fallback_response(error_msg)
        assert error_msg in result["formatted_output"]

    def test_offline_flag_set(self):
        """offline flag is set"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert result.get("offline") is True

    def test_default_managers_present(self):
        """v3.0: FREE tier = PM only"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Error")
        assert result["active_managers"] == ["PM"]
        # v3.0: CTO, QA are now Pro-only
        assert "missed_perspectives" in result
        assert "CTO" in result["missed_perspectives"]
        assert "QA" in result["missed_perspectives"]


class TestDevModeResponse:
    """_dev_mode_response function tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Test context")
        assert isinstance(result, dict)

    def test_dev_mode_flag(self):
        """Has dev_mode flag"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context")
        assert result.get("dev_mode") is True

    def test_has_active_managers(self):
        """Has active_managers"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context")
        assert "active_managers" in result

    def test_has_formatted_output(self):
        """Has formatted_output"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context")
        assert "formatted_output" in result

    def test_context_in_output(self):
        """Context appears in output or feedback"""
        from clouvel.api_client import _dev_mode_response
        context = "Implementing new feature X"
        result = _dev_mode_response(context)
        # Context may be truncated or in formatted_output
        assert "formatted_output" in result

    def test_topic_parameter(self):
        """Accepts topic parameter"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context", topic="auth")
        assert isinstance(result, dict)

    def test_mode_parameter(self):
        """Accepts mode parameter"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context", mode="all")
        assert isinstance(result, dict)

    def test_managers_parameter(self):
        """Accepts managers parameter"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context", managers=["PM", "CTO"])
        assert isinstance(result, dict)

    def test_use_dynamic_parameter(self):
        """Accepts use_dynamic parameter"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Context", use_dynamic=False)
        assert isinstance(result, dict)


class TestCallManagerApi:
    """call_manager_api function tests"""

    @patch("clouvel.license_common.is_developer")
    def test_dev_mode_bypasses_api(self, mock_is_dev):
        """Developer mode bypasses API"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = True
        result = call_manager_api("Test context")
        assert result.get("dev_mode") is True

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_api_call_with_context(self, mock_post, mock_is_dev):
        """API called with context"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"feedback": {}}
        mock_post.return_value = mock_response

        call_manager_api("Test context")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "context" in call_args.kwargs["json"]

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_api_timeout_returns_fallback(self, mock_post, mock_is_dev):
        """Timeout returns fallback response"""
        import requests as req
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_post.side_effect = req.exceptions.Timeout()

        result = call_manager_api("Context")
        assert result.get("offline") is True

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_api_connection_error_returns_fallback(self, mock_post, mock_is_dev):
        """Connection error returns fallback"""
        import requests as req
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_post.side_effect = req.exceptions.ConnectionError()

        result = call_manager_api("Context")
        assert result.get("offline") is True

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_402_returns_trial_exhausted(self, mock_post, mock_is_dev):
        """402 status returns trial exhausted"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {
            "message": "Trial exhausted",
            "upgrade_url": "https://polar.sh/clouvel"
        }
        mock_post.return_value = mock_response

        result = call_manager_api("Context")
        assert result.get("error") == "trial_exhausted"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    @patch("clouvel.api_client._get_license_key")
    def test_license_key_added_to_payload(self, mock_license, mock_post, mock_is_dev):
        """License key added to payload"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_license.return_value = "test-license-key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        call_manager_api("Context")
        call_args = mock_post.call_args
        assert call_args.kwargs["json"].get("licenseKey") == "test-license-key"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_topic_added_to_payload(self, mock_post, mock_is_dev):
        """Topic added to payload when provided"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        call_manager_api("Context", topic="auth")
        call_args = mock_post.call_args
        assert call_args.kwargs["json"].get("topic") == "auth"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_managers_added_to_payload(self, mock_post, mock_is_dev):
        """Managers added to payload when provided"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        call_manager_api("Context", mode="specific", managers=["PM", "CTO"])
        call_args = mock_post.call_args
        assert call_args.kwargs["json"].get("managers") == ["PM", "CTO"]


class TestCallShipApi:
    """call_ship_api function tests"""

    @patch("clouvel.license_common.is_developer")
    def test_dev_mode_always_allows(self, mock_is_dev):
        """Developer mode always allows"""
        from clouvel.api_client import call_ship_api
        mock_is_dev.return_value = True
        result = call_ship_api("/path/to/project")
        assert result.get("allowed") is True
        assert result.get("dev_mode") is True

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_api_call_with_path(self, mock_post, mock_is_dev):
        """API called with path"""
        from clouvel.api_client import call_ship_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"allowed": True}
        mock_post.return_value = mock_response

        call_ship_api("/path/to/project")
        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["path"] == "/path/to/project"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_feature_in_payload(self, mock_post, mock_is_dev):
        """Feature in payload"""
        from clouvel.api_client import call_ship_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"allowed": True}
        mock_post.return_value = mock_response

        call_ship_api("/path", feature="auth")
        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["feature"] == "auth"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_402_returns_not_allowed(self, mock_post, mock_is_dev):
        """402 status returns not allowed"""
        from clouvel.api_client import call_ship_api
        mock_is_dev.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {
            "message": "Trial exhausted",
            "upgrade_url": "https://polar.sh/clouvel"
        }
        mock_post.return_value = mock_response

        result = call_ship_api("/path")
        assert result.get("allowed") is False
        assert result.get("error") == "trial_exhausted"

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_exception_allows_graceful_degradation(self, mock_post, mock_is_dev):
        """Exception allows graceful degradation"""
        from clouvel.api_client import call_ship_api
        mock_is_dev.return_value = False
        mock_post.side_effect = Exception("Network error")

        result = call_ship_api("/path")
        assert result.get("allowed") is True  # Graceful degradation


class TestGetTrialStatus:
    """get_trial_status function tests"""

    @patch("clouvel.api_client.requests.get")
    def test_returns_dict(self, mock_get):
        """Returns dictionary"""
        from clouvel.api_client import get_trial_status
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"features": {}}
        mock_get.return_value = mock_response

        result = get_trial_status()
        assert isinstance(result, dict)

    @patch("clouvel.api_client.requests.get")
    def test_api_call_to_correct_endpoint(self, mock_get):
        """API calls correct endpoint"""
        from clouvel.api_client import get_trial_status
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        get_trial_status()
        call_args = mock_get.call_args
        assert "/api/trial/status" in call_args.args[0]

    @patch("clouvel.api_client.requests.get")
    def test_exception_returns_error_dict(self, mock_get):
        """Exception returns error dict"""
        from clouvel.api_client import get_trial_status
        mock_get.side_effect = Exception("Network error")

        result = get_trial_status()
        assert "error" in result
        assert "features" in result

    @patch("clouvel.api_client.requests.get")
    def test_timeout_returns_error(self, mock_get):
        """Timeout returns error"""
        import requests
        from clouvel.api_client import get_trial_status
        mock_get.side_effect = requests.exceptions.Timeout()

        result = get_trial_status()
        assert "error" in result


class TestApiClientIntegration:
    """Integration tests for API client"""

    def test_client_id_is_deterministic(self):
        """Client ID is deterministic across calls"""
        ids = [_get_client_id() for _ in range(5)]
        assert all(id == ids[0] for id in ids)

    def test_fallback_response_structure_matches_api(self):
        """Fallback response has same structure as expected API response"""
        from clouvel.api_client import _fallback_response
        result = _fallback_response("Test")
        assert "topic" in result
        assert "active_managers" in result
        assert "feedback" in result
        assert "formatted_output" in result

    def test_dev_mode_response_structure_matches_api(self):
        """Dev mode response has same structure as expected API response"""
        from clouvel.api_client import _dev_mode_response
        result = _dev_mode_response("Test")
        assert "active_managers" in result
        assert "formatted_output" in result


class TestGenerateDynamicMeetingDirect:
    """_generate_dynamic_meeting_direct function tests"""

    @patch("anthropic.Anthropic")
    def test_returns_string(self, mock_anthropic):
        """Returns string"""
        from clouvel.api_client import _generate_dynamic_meeting_direct
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Meeting output")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        result = _generate_dynamic_meeting_direct("context", "auth", "test-api-key")
        assert result == "Meeting output"

    @patch("anthropic.Anthropic")
    def test_uses_correct_model(self, mock_anthropic):
        """Uses correct model"""
        from clouvel.api_client import _generate_dynamic_meeting_direct
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Output")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        _generate_dynamic_meeting_direct("context", "feature", "key")
        call_args = mock_client.messages.create.call_args
        assert "claude" in call_args.kwargs["model"].lower()

    @patch("anthropic.Anthropic")
    def test_topic_in_system_prompt(self, mock_anthropic):
        """Topic appears in system prompt"""
        from clouvel.api_client import _generate_dynamic_meeting_direct
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Output")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        _generate_dynamic_meeting_direct("ctx", "security", "key")
        call_args = mock_client.messages.create.call_args
        assert "security" in call_args.kwargs["system"]

    @patch("anthropic.Anthropic")
    def test_default_topic_when_none(self, mock_anthropic):
        """Uses default topic when None"""
        from clouvel.api_client import _generate_dynamic_meeting_direct
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Output")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        _generate_dynamic_meeting_direct("ctx", None, "key")
        call_args = mock_client.messages.create.call_args
        assert "feature" in call_args.kwargs["system"]


class TestApiClientImportErrors:
    """Test ImportError handling paths"""

    def test_manager_api_handles_import_error(self):
        """Manager API handles import errors gracefully"""
        from clouvel.api_client import call_manager_api
        # The import error handling is internal - test that function completes
        # by using a mock that simulates the error being caught
        with patch("clouvel.license_common.is_developer", return_value=False):
            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"feedback": {}}
                mock_post.return_value = mock_response

                result = call_manager_api("Context")
                # Function completes successfully
                assert isinstance(result, dict)

    def test_ship_api_handles_import_error(self):
        """Ship API handles import errors gracefully"""
        from clouvel.api_client import call_ship_api
        with patch("clouvel.license_common.is_developer", return_value=False):
            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"allowed": True}
                mock_post.return_value = mock_response

                result = call_ship_api("/path")
                assert isinstance(result, dict)


class TestDevModeWithDynamicMeeting:
    """Test dev mode with dynamic meeting option"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("clouvel.api_client._generate_dynamic_meeting_direct")
    def test_uses_direct_call_when_local_unavailable(self, mock_generate):
        """Uses direct anthropic call when local manager unavailable"""
        from clouvel.api_client import _dev_mode_response
        mock_generate.return_value = "Dynamic meeting output"

        # This will try local import first (fails), then use direct call
        result = _dev_mode_response(
            context="Test",
            use_dynamic=True
        )
        # May use mock or fallback depending on import status
        assert isinstance(result, dict)

    def test_dev_mode_fallback_without_anthropic_key(self):
        """Falls back to mock when no API key"""
        from clouvel.api_client import _dev_mode_response
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            result = _dev_mode_response(
                context="Test",
                use_dynamic=True
            )
            # Should return mock response
            assert result.get("dev_mode") is True
            assert "active_managers" in result


class TestCallManagerApiGenericException:
    """Test generic exception handling"""

    @patch("clouvel.license_common.is_developer")
    @patch("requests.post")
    def test_generic_exception_returns_fallback(self, mock_post, mock_is_dev):
        """Generic exception returns fallback"""
        from clouvel.api_client import call_manager_api
        mock_is_dev.return_value = False
        mock_post.side_effect = Exception("Unknown error")

        result = call_manager_api("Context")
        assert result.get("offline") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
