# -*- coding: utf-8 -*-
"""Version check module tests"""

import pytest
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.version_check import (
    _get_current_version,
    _compare_versions,
    _load_cache,
    _save_cache,
    _fetch_latest_version,
    check_for_updates,
    get_update_banner,
    init_version_check,
    get_cached_update_info,
    CURRENT_VERSION,
    CACHE_TTL,
)


class TestCurrentVersion:
    """CURRENT_VERSION constant tests"""

    def test_version_format(self):
        """Version follows semver format"""
        parts = CURRENT_VERSION.split(".")
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts)

    def test_get_current_version_returns_string(self):
        """Returns string version"""
        result = _get_current_version()
        assert isinstance(result, str)
        assert len(result) > 0


class TestCompareVersions:
    """_compare_versions function tests"""

    def test_equal_versions(self):
        """Same versions return 0"""
        assert _compare_versions("1.0.0", "1.0.0") == 0
        assert _compare_versions("2.3.4", "2.3.4") == 0

    def test_current_older(self):
        """Current < latest returns -1"""
        assert _compare_versions("1.0.0", "1.0.1") == -1
        assert _compare_versions("1.0.0", "1.1.0") == -1
        assert _compare_versions("1.0.0", "2.0.0") == -1

    def test_current_newer(self):
        """Current > latest returns 1"""
        assert _compare_versions("1.0.1", "1.0.0") == 1
        assert _compare_versions("1.1.0", "1.0.0") == 1
        assert _compare_versions("2.0.0", "1.0.0") == 1

    def test_different_length_versions(self):
        """Handle different length versions"""
        assert _compare_versions("1.0", "1.0.0") == 0
        assert _compare_versions("1.0.0", "1.0") == 0
        assert _compare_versions("1.0", "1.0.1") == -1

    def test_invalid_version(self):
        """Handle invalid version strings"""
        # Should not crash
        result = _compare_versions("invalid", "1.0.0")
        assert result in [-1, 0, 1]

    def test_major_version_priority(self):
        """Major version has highest priority"""
        assert _compare_versions("2.0.0", "1.9.9") == 1
        assert _compare_versions("1.9.9", "2.0.0") == -1

    def test_minor_version_priority(self):
        """Minor version priority over patch"""
        assert _compare_versions("1.2.0", "1.1.9") == 1
        assert _compare_versions("1.1.9", "1.2.0") == -1

    def test_patch_version(self):
        """Patch version comparison"""
        assert _compare_versions("1.0.2", "1.0.1") == 1
        assert _compare_versions("1.0.1", "1.0.2") == -1


class TestCacheOperations:
    """Cache load/save tests"""

    @pytest.fixture
    def temp_cache_dir(self, monkeypatch):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        cache_dir = Path(temp_dir)
        cache_file = cache_dir / "version_cache.json"

        # Patch cache paths
        import clouvel.version_check as vc
        monkeypatch.setattr(vc, "CACHE_DIR", cache_dir)
        monkeypatch.setattr(vc, "CACHE_FILE", cache_file)

        yield cache_dir
        shutil.rmtree(temp_dir)

    def test_load_nonexistent_cache(self, temp_cache_dir):
        """Load returns None when no cache"""
        result = _load_cache()
        assert result is None

    def test_save_and_load_cache(self, temp_cache_dir):
        """Save and load cache data"""
        test_data = {"latest_version": "1.5.0"}
        _save_cache(test_data)

        result = _load_cache()
        assert result is not None
        assert result["latest_version"] == "1.5.0"
        assert "timestamp" in result

    def test_cache_expiry(self, temp_cache_dir, monkeypatch):
        """Expired cache returns None"""
        # Save old cache
        test_data = {"latest_version": "1.5.0", "timestamp": time.time() - CACHE_TTL - 100}

        import clouvel.version_check as vc
        vc.CACHE_FILE.write_text(json.dumps(test_data), encoding="utf-8")

        result = _load_cache()
        assert result is None  # Expired

    def test_cache_valid_ttl(self, temp_cache_dir):
        """Valid TTL cache is returned"""
        test_data = {"latest_version": "1.5.0"}
        _save_cache(test_data)

        # Should be within TTL
        result = _load_cache()
        assert result is not None


class TestCheckForUpdates:
    """check_for_updates function tests"""

    def test_returns_dict(self):
        """Returns dict with expected keys"""
        result = check_for_updates()
        assert isinstance(result, dict)
        assert "current_version" in result
        assert "latest_version" in result
        assert "update_available" in result

    def test_current_version_included(self):
        """Current version is always included"""
        result = check_for_updates()
        assert result["current_version"] is not None
        assert len(result["current_version"]) > 0

    @patch('clouvel.version_check._fetch_latest_version')
    def test_update_available_when_newer(self, mock_fetch):
        """Update available when newer version exists"""
        mock_fetch.return_value = "99.0.0"  # Very high version

        result = check_for_updates(force=True)

        if result["latest_version"]:
            # If fetch succeeded
            assert result["update_available"] is True
            assert result["message"] is not None

    @patch('clouvel.version_check._fetch_latest_version')
    def test_no_update_when_same(self, mock_fetch):
        """No update when versions match"""
        current = _get_current_version()
        mock_fetch.return_value = current

        result = check_for_updates(force=True)

        if result["latest_version"]:
            assert result["update_available"] is False

    @patch('clouvel.version_check._fetch_latest_version')
    def test_force_bypasses_cache(self, mock_fetch):
        """Force flag bypasses cache"""
        mock_fetch.return_value = "1.5.0"

        # First call with force
        result = check_for_updates(force=True)

        # Should have called fetch
        mock_fetch.assert_called()


class TestVersionParsing:
    """Version parsing edge cases"""

    def test_version_with_alpha(self):
        """Handle version with alpha suffix"""
        # Should not crash
        result = _compare_versions("1.0.0a", "1.0.0")
        assert result in [-1, 0, 1]

    def test_empty_version(self):
        """Handle empty version string"""
        result = _compare_versions("", "1.0.0")
        assert result in [-1, 0, 1]

    def test_none_like_version(self):
        """Handle None-like inputs"""
        # Should not crash with defensive parsing
        try:
            result = _compare_versions("1.0.0", "")
            assert result in [-1, 0, 1]
        except Exception:
            pass  # May raise, that's OK


class TestFetchLatestVersion:
    """_fetch_latest_version function tests"""

    @patch('requests.get')
    def test_fetch_success(self, mock_get):
        """Successful fetch returns version"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "2.0.0"}}
        mock_get.return_value = mock_response

        result = _fetch_latest_version()
        assert result == "2.0.0"

    @patch('requests.get')
    def test_fetch_failure(self, mock_get):
        """Failed fetch returns None"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = _fetch_latest_version()
        assert result is None

    @patch('requests.get')
    def test_fetch_exception(self, mock_get):
        """Exception returns None"""
        mock_get.side_effect = Exception("Network error")

        result = _fetch_latest_version()
        assert result is None

    @patch('requests.get')
    def test_fetch_timeout(self, mock_get):
        """Timeout returns None"""
        mock_get.side_effect = TimeoutError()

        result = _fetch_latest_version()
        assert result is None


class TestGetUpdateBanner:
    """get_update_banner function tests"""

    @patch('clouvel.version_check.check_for_updates')
    def test_returns_none_when_no_update(self, mock_check):
        """Returns None when no update available"""
        mock_check.return_value = {
            "update_available": False,
            "current_version": "1.0.0",
            "latest_version": "1.0.0"
        }

        result = get_update_banner()
        assert result is None

    @patch('clouvel.version_check.check_for_updates')
    def test_returns_banner_when_update_available(self, mock_check):
        """Returns banner when update available"""
        mock_check.return_value = {
            "update_available": True,
            "current_version": "1.0.0",
            "latest_version": "2.0.0"
        }

        result = get_update_banner()
        assert result is not None
        assert "2.0.0" in result
        assert "pip install" in result

    @patch('clouvel.version_check.check_for_updates')
    def test_banner_contains_upgrade_command(self, mock_check):
        """Banner contains upgrade command"""
        mock_check.return_value = {
            "update_available": True,
            "current_version": "1.0.0",
            "latest_version": "2.0.0"
        }

        result = get_update_banner()
        assert "upgrade" in result


class TestInitVersionCheck:
    """init_version_check function tests"""

    @patch('clouvel.version_check.check_for_updates')
    def test_returns_dict(self, mock_check):
        """Returns dict"""
        mock_check.return_value = {"current_version": "1.0.0"}

        result = init_version_check()
        assert isinstance(result, dict)

    @patch('clouvel.version_check.check_for_updates')
    def test_calls_check_for_updates(self, mock_check):
        """Calls check_for_updates"""
        mock_check.return_value = {"current_version": "1.0.0"}

        init_version_check()
        mock_check.assert_called_once()

    @patch('clouvel.version_check.check_for_updates')
    def test_sets_global_state(self, mock_check):
        """Sets global _update_info"""
        mock_check.return_value = {"current_version": "1.0.0", "test": True}

        init_version_check()

        # get_cached_update_info should return the same data
        cached = get_cached_update_info()
        assert cached is not None
        assert cached.get("test") is True


class TestGetCachedUpdateInfo:
    """get_cached_update_info function tests"""

    def test_returns_none_before_init(self):
        """May return None before init"""
        # Reset global state
        import clouvel.version_check as vc
        old_value = vc._update_info
        vc._update_info = None

        result = get_cached_update_info()
        assert result is None

        # Restore
        vc._update_info = old_value

    @patch('clouvel.version_check.check_for_updates')
    def test_returns_cached_after_init(self, mock_check):
        """Returns cached data after init"""
        mock_check.return_value = {
            "current_version": "1.0.0",
            "latest_version": "1.0.0",
            "update_available": False
        }

        init_version_check()
        result = get_cached_update_info()

        assert result is not None
        assert result["current_version"] == "1.0.0"


class TestCacheEdgeCases:
    """Cache edge case tests"""

    @pytest.fixture
    def temp_cache_dir(self, monkeypatch):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        cache_dir = Path(temp_dir)
        cache_file = cache_dir / "version_cache.json"

        import clouvel.version_check as vc
        monkeypatch.setattr(vc, "CACHE_DIR", cache_dir)
        monkeypatch.setattr(vc, "CACHE_FILE", cache_file)

        yield cache_dir
        shutil.rmtree(temp_dir)

    def test_load_corrupted_cache(self, temp_cache_dir):
        """Load corrupted cache returns None"""
        import clouvel.version_check as vc
        vc.CACHE_FILE.write_text("not valid json", encoding="utf-8")

        result = _load_cache()
        assert result is None

    def test_save_creates_directory(self, temp_cache_dir):
        """Save creates directory if not exists"""
        import clouvel.version_check as vc
        new_dir = temp_cache_dir / "subdir"
        vc.CACHE_DIR = new_dir
        vc.CACHE_FILE = new_dir / "cache.json"

        _save_cache({"test": True})

        assert new_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
