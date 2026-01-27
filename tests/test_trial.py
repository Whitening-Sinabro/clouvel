# -*- coding: utf-8 -*-
"""Trial system tests"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.trial import (
    TRIAL_LIMITS,
    _get_trial_path,
    _load_trial_data,
    _save_trial_data,
    get_trial_usage,
    get_trial_remaining,
    increment_trial_usage,
    check_trial_available,
    get_trial_status,
    reset_trial,
    get_trial_exhausted_message,
)


@pytest.fixture
def temp_trial_dir(monkeypatch):
    """Create temporary trial directory"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Patch _get_trial_path to use temp directory
    def mock_get_trial_path():
        clouvel_dir = temp_path / ".clouvel"
        clouvel_dir.mkdir(parents=True, exist_ok=True)
        return clouvel_dir / "trial.json"

    import clouvel.trial as trial_module
    monkeypatch.setattr(trial_module, "_get_trial_path", mock_get_trial_path)

    yield temp_path
    shutil.rmtree(temp_dir)


class TestTrialLimits:
    """TRIAL_LIMITS constant tests"""

    def test_limits_exist(self):
        """Limits dictionary exists"""
        assert isinstance(TRIAL_LIMITS, dict)

    def test_manager_limit(self):
        """Manager has 10 uses"""
        assert TRIAL_LIMITS.get("manager") == 10

    def test_ship_limit(self):
        """Ship has 5 uses"""
        assert TRIAL_LIMITS.get("ship") == 5

    def test_all_limits_positive(self):
        """All limits are positive integers"""
        for feature, limit in TRIAL_LIMITS.items():
            assert isinstance(limit, int)
            assert limit > 0


class TestGetTrialPath:
    """_get_trial_path function tests"""

    def test_returns_path(self):
        """Returns Path object"""
        result = _get_trial_path()
        assert isinstance(result, Path)

    def test_path_includes_clouvel(self):
        """Path includes .clouvel directory"""
        result = _get_trial_path()
        assert ".clouvel" in str(result)

    def test_path_ends_with_trial_json(self):
        """Path ends with trial.json"""
        result = _get_trial_path()
        assert result.name == "trial.json"


class TestLoadTrialData:
    """_load_trial_data function tests"""

    def test_returns_dict(self, temp_trial_dir):
        """Returns dictionary"""
        result = _load_trial_data()
        assert isinstance(result, dict)

    def test_new_data_has_created_at(self, temp_trial_dir):
        """New data has created_at field"""
        result = _load_trial_data()
        assert "created_at" in result

    def test_new_data_has_usage(self, temp_trial_dir):
        """New data has empty usage dict"""
        result = _load_trial_data()
        assert "usage" in result
        assert result["usage"] == {}

    def test_loads_existing_data(self, temp_trial_dir):
        """Loads existing trial data"""
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)

        test_data = {"created_at": "2024-01-01", "usage": {"manager": 5}}
        trial_path.write_text(json.dumps(test_data), encoding="utf-8")

        result = _load_trial_data()
        assert result["usage"]["manager"] == 5

    def test_handles_invalid_json(self, temp_trial_dir):
        """Returns default for invalid JSON"""
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)
        trial_path.write_text("not valid json {{{", encoding="utf-8")

        result = _load_trial_data()
        # Should return default dict
        assert "created_at" in result
        assert result["usage"] == {}


class TestSaveTrialData:
    """_save_trial_data function tests"""

    def test_saves_data(self, temp_trial_dir):
        """Saves data to file"""
        test_data = {"created_at": "2024-01-01", "usage": {"manager": 3}}
        _save_trial_data(test_data)

        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        assert trial_path.exists()

        loaded = json.loads(trial_path.read_text(encoding="utf-8"))
        assert loaded["usage"]["manager"] == 3


class TestGetTrialUsage:
    """get_trial_usage function tests"""

    def test_returns_zero_for_new(self, temp_trial_dir):
        """Returns 0 for unused feature"""
        result = get_trial_usage("manager")
        assert result == 0

    def test_returns_usage_count(self, temp_trial_dir):
        """Returns actual usage count"""
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)
        trial_path.write_text(json.dumps({
            "created_at": "2024-01-01",
            "usage": {"manager": 7}
        }), encoding="utf-8")

        result = get_trial_usage("manager")
        assert result == 7


class TestGetTrialRemaining:
    """get_trial_remaining function tests"""

    def test_returns_none_for_unlimited(self, temp_trial_dir):
        """Returns None for unlimited feature"""
        result = get_trial_remaining("quick_perspectives")
        assert result is None

    def test_returns_full_limit_for_new(self, temp_trial_dir):
        """Returns full limit for unused feature"""
        result = get_trial_remaining("manager")
        assert result == TRIAL_LIMITS["manager"]

    def test_returns_remaining_count(self, temp_trial_dir):
        """Returns remaining count"""
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)
        trial_path.write_text(json.dumps({
            "created_at": "2024-01-01",
            "usage": {"manager": 3}
        }), encoding="utf-8")

        result = get_trial_remaining("manager")
        assert result == TRIAL_LIMITS["manager"] - 3

    def test_returns_zero_when_exhausted(self, temp_trial_dir):
        """Returns 0 when exhausted"""
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)
        trial_path.write_text(json.dumps({
            "created_at": "2024-01-01",
            "usage": {"manager": 100}  # Over limit
        }), encoding="utf-8")

        result = get_trial_remaining("manager")
        assert result == 0


class TestIncrementTrialUsage:
    """increment_trial_usage function tests"""

    def test_unlimited_feature(self, temp_trial_dir):
        """Returns unlimited for non-limited feature"""
        result = increment_trial_usage("quick_perspectives")
        assert result.get("unlimited") is True

    def test_increments_count(self, temp_trial_dir):
        """Increments usage count"""
        result = increment_trial_usage("manager")
        assert result["used"] == 1
        assert result["limit"] == TRIAL_LIMITS["manager"]
        assert result["remaining"] == TRIAL_LIMITS["manager"] - 1
        assert result["exhausted"] is False

    def test_multiple_increments(self, temp_trial_dir):
        """Multiple increments work correctly"""
        increment_trial_usage("manager")
        increment_trial_usage("manager")
        result = increment_trial_usage("manager")

        assert result["used"] == 3
        assert result["remaining"] == TRIAL_LIMITS["manager"] - 3

    def test_exhausted_flag(self, temp_trial_dir):
        """Exhausted flag set correctly"""
        # Fill up the limit
        for _ in range(TRIAL_LIMITS["ship"]):
            result = increment_trial_usage("ship")

        assert result["exhausted"] is True
        assert result["remaining"] == 0

    def test_initializes_usage_dict(self, temp_trial_dir):
        """Initializes usage dict if missing"""
        # Save data without usage field
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        trial_path.parent.mkdir(parents=True, exist_ok=True)
        trial_path.write_text(json.dumps({"created_at": "2024-01-01"}), encoding="utf-8")

        result = increment_trial_usage("manager")
        assert result["used"] == 1


class TestCheckTrialAvailable:
    """check_trial_available function tests"""

    def test_unlimited_always_true(self, temp_trial_dir):
        """Unlimited features always available"""
        assert check_trial_available("quick_perspectives") is True

    def test_new_feature_available(self, temp_trial_dir):
        """New feature is available"""
        assert check_trial_available("manager") is True

    def test_exhausted_feature_unavailable(self, temp_trial_dir):
        """Exhausted feature is unavailable"""
        # Exhaust the limit
        for _ in range(TRIAL_LIMITS["ship"]):
            increment_trial_usage("ship")

        assert check_trial_available("ship") is False


class TestGetTrialStatus:
    """get_trial_status function tests"""

    def test_returns_dict(self, temp_trial_dir):
        """Returns dictionary"""
        result = get_trial_status()
        assert isinstance(result, dict)

    def test_has_features(self, temp_trial_dir):
        """Has features section"""
        result = get_trial_status()
        assert "features" in result

    def test_includes_all_limited_features(self, temp_trial_dir):
        """Includes all limited features"""
        result = get_trial_status()
        for feature in TRIAL_LIMITS:
            assert feature in result["features"]

    def test_feature_status_structure(self, temp_trial_dir):
        """Feature status has expected structure"""
        result = get_trial_status()
        for feature_status in result["features"].values():
            assert "used" in feature_status
            assert "limit" in feature_status
            assert "remaining" in feature_status
            assert "exhausted" in feature_status


class TestResetTrial:
    """reset_trial function tests"""

    def test_removes_trial_file(self, temp_trial_dir):
        """Removes trial file"""
        # Create trial data
        increment_trial_usage("manager")

        # Reset
        reset_trial()

        # Check file removed
        trial_path = temp_trial_dir / ".clouvel" / "trial.json"
        assert not trial_path.exists()

    def test_reset_allows_new_usage(self, temp_trial_dir):
        """Reset allows new usage"""
        # Use some
        increment_trial_usage("manager")
        increment_trial_usage("manager")

        # Reset
        reset_trial()

        # Should be back to 0
        assert get_trial_usage("manager") == 0


class TestGetTrialExhaustedMessage:
    """get_trial_exhausted_message function tests"""

    def test_returns_string(self):
        """Returns string message"""
        result = get_trial_exhausted_message("manager")
        assert isinstance(result, str)

    def test_includes_feature_name(self):
        """Includes feature name"""
        result = get_trial_exhausted_message("manager")
        assert "manager" in result

    def test_includes_limit(self):
        """Includes trial limit"""
        result = get_trial_exhausted_message("manager")
        assert str(TRIAL_LIMITS["manager"]) in result

    def test_includes_upgrade_link(self):
        """Includes upgrade link"""
        result = get_trial_exhausted_message("manager")
        assert "polar.sh" in result or "Pro" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
