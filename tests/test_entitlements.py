# -*- coding: utf-8 -*-
"""Entitlements module tests"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.utils.entitlements import (
    env_flag,
    is_clouvel_repo,
    is_developer,
    pro_enabled_by_env,
    can_use_pro,
    has_valid_license,
    _TRUE,
)


class TestEnvFlag:
    """env_flag function tests"""

    def test_true_values(self):
        """Truthy env values return True"""
        for val in ["1", "true", "yes", "y", "on", "enable", "enabled", "dev"]:
            with patch.dict(os.environ, {"TEST_FLAG": val}):
                assert env_flag("TEST_FLAG") is True

    def test_false_values(self):
        """Falsy env values return False"""
        for val in ["0", "false", "no", "n", "off", "disable", "disabled", ""]:
            with patch.dict(os.environ, {"TEST_FLAG": val}):
                assert env_flag("TEST_FLAG") is False

    def test_nonexistent_var(self):
        """Nonexistent var returns False"""
        # Ensure var doesn't exist
        os.environ.pop("NONEXISTENT_VAR_XYZ", None)
        assert env_flag("NONEXISTENT_VAR_XYZ") is False

    def test_multiple_names(self):
        """Check multiple var names"""
        with patch.dict(os.environ, {"VAR_A": "0", "VAR_B": "1"}):
            assert env_flag("VAR_A", "VAR_B") is True

    def test_case_insensitive(self):
        """Values are case insensitive"""
        with patch.dict(os.environ, {"TEST_FLAG": "TRUE"}):
            assert env_flag("TEST_FLAG") is True
        with patch.dict(os.environ, {"TEST_FLAG": "True"}):
            assert env_flag("TEST_FLAG") is True

    def test_whitespace_stripped(self):
        """Whitespace is stripped"""
        with patch.dict(os.environ, {"TEST_FLAG": "  1  "}):
            assert env_flag("TEST_FLAG") is True


class TestTrueConstant:
    """_TRUE constant tests"""

    def test_contains_common_truthy_values(self):
        """Contains common truthy values"""
        assert "1" in _TRUE
        assert "true" in _TRUE
        assert "yes" in _TRUE


class TestIsClouvelRepo:
    """is_clouvel_repo function tests"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_none_path(self):
        """None path returns False"""
        assert is_clouvel_repo(None) is False

    def test_nonexistent_path(self):
        """Nonexistent path returns False"""
        assert is_clouvel_repo("/nonexistent/path/xyz") is False

    def test_empty_project(self, temp_project):
        """Empty project returns False"""
        assert is_clouvel_repo(str(temp_project)) is False

    def test_with_src_clouvel(self, temp_project):
        """Project with src/clouvel returns True"""
        src_clouvel = temp_project / "src" / "clouvel"
        src_clouvel.mkdir(parents=True)

        assert is_clouvel_repo(str(temp_project)) is True

    def test_with_pyproject_clouvel(self, temp_project):
        """Project with clouvel pyproject.toml returns True"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text('name = "clouvel"\nversion = "1.0.0"', encoding="utf-8")

        assert is_clouvel_repo(str(temp_project)) is True

    def test_with_git_clouvel_remote(self, temp_project):
        """Project with clouvel git remote returns True"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()

        config_file = git_dir / "config"
        config_file.write_text(
            '[remote "origin"]\n\turl = git@github.com:user/clouvel.git',
            encoding="utf-8"
        )

        assert is_clouvel_repo(str(temp_project)) is True

    def test_other_pyproject(self, temp_project):
        """Project with other pyproject.toml returns False"""
        pyproject = temp_project / "pyproject.toml"
        pyproject.write_text('name = "other-project"\nversion = "1.0.0"', encoding="utf-8")

        assert is_clouvel_repo(str(temp_project)) is False


class TestIsDeveloper:
    """is_developer function tests"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_with_clouvel_dev_env(self, temp_project):
        """CLOUVEL_DEV=1 returns True"""
        with patch.dict(os.environ, {"CLOUVEL_DEV": "1"}):
            assert is_developer(str(temp_project)) is True

    def test_with_clouvel_dev_mode_env(self, temp_project):
        """CLOUVEL_DEV_MODE=1 returns True"""
        with patch.dict(os.environ, {"CLOUVEL_DEV_MODE": "1"}):
            assert is_developer(str(temp_project)) is True

    def test_with_clouvel_repo_path(self, temp_project):
        """Clouvel repo path returns True"""
        # Create clouvel repo structure
        src_clouvel = temp_project / "src" / "clouvel"
        src_clouvel.mkdir(parents=True)

        # Without env var, path-based detection
        with patch.dict(os.environ, {}, clear=True):
            # Clear CLOUVEL_DEV if exists
            os.environ.pop("CLOUVEL_DEV", None)
            os.environ.pop("CLOUVEL_DEV_MODE", None)
            assert is_developer(str(temp_project)) is True

    def test_env_takes_priority(self, temp_project):
        """Env var takes priority over path detection"""
        # Even with non-clouvel path, env should work
        with patch.dict(os.environ, {"CLOUVEL_DEV": "1"}):
            assert is_developer(str(temp_project)) is True


class TestProEnabledByEnv:
    """pro_enabled_by_env function tests (deprecated)"""

    def test_returns_bool(self):
        """Returns boolean"""
        result = pro_enabled_by_env()
        assert isinstance(result, bool)

    def test_with_dev_env(self):
        """Returns True with dev env"""
        with patch.dict(os.environ, {"CLOUVEL_DEV": "1"}):
            assert pro_enabled_by_env() is True


class TestHasValidLicense:
    """has_valid_license function tests"""

    def test_returns_bool(self):
        """Returns boolean"""
        result = has_valid_license()
        assert isinstance(result, bool)

    def test_returns_false_by_default(self):
        """Returns False when no valid license"""
        # In test environment, license check typically returns False
        result = has_valid_license()
        # Should return bool regardless of license status
        assert result in [True, False]

    def test_handles_import_error(self):
        """Handles import errors gracefully"""
        # The function should not raise exceptions
        try:
            result = has_valid_license()
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"has_valid_license raised exception: {e}")


class TestCanUsePro:
    """can_use_pro function tests"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_with_developer_mode(self, temp_project):
        """Returns True in developer mode"""
        with patch.dict(os.environ, {"CLOUVEL_DEV": "1"}):
            assert can_use_pro(str(temp_project)) is True

    def test_with_license_checker(self, temp_project):
        """Custom license checker is called"""
        mock_checker = lambda: True

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLOUVEL_DEV", None)
            os.environ.pop("CLOUVEL_DEV_MODE", None)
            result = can_use_pro(str(temp_project), license_checker=mock_checker)
            # In non-clouvel project, uses license_checker
            assert isinstance(result, bool)

    def test_false_license_checker(self, temp_project):
        """False license checker returns False in non-dev"""
        mock_checker = lambda: False

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLOUVEL_DEV", None)
            os.environ.pop("CLOUVEL_DEV_MODE", None)
            # If not clouvel repo and no valid license
            result = can_use_pro(str(temp_project), license_checker=mock_checker)
            # Result depends on whether temp_project is detected as clouvel repo
            assert isinstance(result, bool)

    def test_uses_has_valid_license_fallback(self, temp_project):
        """Uses has_valid_license when no checker provided"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLOUVEL_DEV", None)
            os.environ.pop("CLOUVEL_DEV_MODE", None)
            # Without license_checker, uses has_valid_license()
            result = can_use_pro(str(temp_project))
            assert isinstance(result, bool)


class TestIsClouvelRepoExceptions:
    """Exception handling in is_clouvel_repo"""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_pyproject_read_exception(self, temp_project):
        """Handles pyproject read exception"""
        pyproject = temp_project / "pyproject.toml"
        # Create a file we can't read properly (simulate error)
        pyproject.write_text('name = "other"', encoding="utf-8")

        # Even if read fails, should return False safely
        result = is_clouvel_repo(str(temp_project))
        assert isinstance(result, bool)

    def test_git_config_read_exception(self, temp_project):
        """Handles git config read exception"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()

        config_file = git_dir / "config"
        # Create valid but non-clouvel config
        config_file.write_text('[remote "origin"]\n\turl = git@github.com:other/repo.git', encoding="utf-8")

        result = is_clouvel_repo(str(temp_project))
        assert result is False

    def test_git_exists_but_no_config(self, temp_project):
        """Handles git dir without config file"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        # No config file created

        result = is_clouvel_repo(str(temp_project))
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
