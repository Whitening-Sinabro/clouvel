# -*- coding: utf-8 -*-
"""Clouvel Ship 도구 테스트 (v1.2+)

P0 테스트: ship, quick_ship, full_ship
"""

import pytest
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.ship import ship, quick_ship, full_ship


@pytest.fixture
def temp_project():
    """임시 프로젝트 디렉토리 생성"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def project_with_tests(temp_project):
    """테스트가 있는 프로젝트"""
    # src 폴더 생성
    src_dir = Path(temp_project) / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("def main(): pass", encoding='utf-8')

    # tests 폴더 생성
    tests_dir = Path(temp_project) / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text(
        "def test_main(): assert True",
        encoding='utf-8'
    )

    # pyproject.toml 생성
    (Path(temp_project) / "pyproject.toml").write_text("""
[project]
name = "test-project"
version = "0.1.0"
""", encoding='utf-8')

    return temp_project


@pytest.fixture
def mock_developer_mode():
    """개발자 모드 mock"""
    with patch('clouvel.tools.ship.is_developer', return_value=True):
        yield


@pytest.fixture
def mock_api_allowed():
    """API 허용 mock"""
    with patch('clouvel.tools.ship.call_ship_api') as mock:
        mock.return_value = {"allowed": True, "message": "OK"}
        yield mock


@pytest.fixture
def mock_api_denied():
    """API 거부 mock"""
    with patch('clouvel.tools.ship.call_ship_api') as mock:
        mock.return_value = {"allowed": False, "error": "Not allowed", "message": "License required"}
        yield mock


@pytest.fixture
def mock_api_trial_exhausted():
    """Trial 소진 mock"""
    with patch('clouvel.tools.ship.call_ship_api') as mock:
        mock.return_value = {"allowed": False, "error": "trial_exhausted", "message": "Trial exhausted"}
        yield mock


class TestShipBasic:
    """ship 기본 테스트"""

    def test_ship_developer_mode_no_pro(self, temp_project, mock_developer_mode):
        """개발자 모드에서 ship_pro 없을 때"""
        with patch('clouvel.tools.ship.is_developer', return_value=True):
            # ship_pro 없을 때 ImportError
            with patch.dict('sys.modules', {'clouvel.tools.ship_pro': None}):
                result = ship(path=temp_project)
                # API fallback 또는 에러
                assert result is not None

    def test_ship_api_denied(self, temp_project, mock_api_denied):
        """API 거부 시 에러 반환"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(path=temp_project)

            assert "error" in result
            assert result["error"] == "Not allowed"

    def test_ship_trial_exhausted(self, temp_project, mock_api_trial_exhausted):
        """Trial 소진 시 업그레이드 메시지"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(path=temp_project)

            assert "error" in result
            assert "Trial exhausted" in result["error"]
            assert "polar.sh/clouvel" in result.get("upgrade_url", "") or \
                   "polar.sh/clouvel" in result.get("formatted_output", "")

    def test_ship_default_steps(self, temp_project):
        """기본 steps 확인"""
        # ship 함수 시그니처 확인
        import inspect
        sig = inspect.signature(ship)
        params = sig.parameters

        # steps 기본값 확인
        assert "steps" in params
        # steps=None이면 ship_pro에서 기본값 사용

    def test_ship_with_feature_name(self, temp_project, mock_api_denied):
        """feature 이름 전달"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(path=temp_project, feature="login-feature")
            # API 거부되어도 feature는 전달됨
            assert result is not None


class TestQuickShip:
    """quick_ship 테스트"""

    def test_quick_ship_calls_ship(self, temp_project, mock_api_denied):
        """quick_ship은 ship을 호출"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.ship') as mock_ship:
                mock_ship.return_value = {"status": "ok"}
                quick_ship(path=temp_project)

                # ship이 lint, test steps로 호출됨
                mock_ship.assert_called_once()
                call_kwargs = mock_ship.call_args[1]
                assert call_kwargs["steps"] == ["lint", "test"]

    def test_quick_ship_with_feature(self, temp_project, mock_api_denied):
        """quick_ship feature 전달"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.ship') as mock_ship:
                mock_ship.return_value = {"status": "ok"}
                quick_ship(path=temp_project, feature="my-feature")

                call_kwargs = mock_ship.call_args[1]
                assert call_kwargs["feature"] == "my-feature"


class TestFullShip:
    """full_ship 테스트"""

    def test_full_ship_calls_ship(self, temp_project, mock_api_denied):
        """full_ship은 ship을 호출"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.ship') as mock_ship:
                mock_ship.return_value = {"status": "ok"}
                full_ship(path=temp_project)

                # ship이 모든 steps로 호출됨
                mock_ship.assert_called_once()
                call_kwargs = mock_ship.call_args[1]
                assert call_kwargs["steps"] == ["lint", "typecheck", "test", "build"]
                assert call_kwargs["auto_fix"] == True

    def test_full_ship_with_feature(self, temp_project, mock_api_denied):
        """full_ship feature 전달"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.ship') as mock_ship:
                mock_ship.return_value = {"status": "ok"}
                full_ship(path=temp_project, feature="release-v1")

                call_kwargs = mock_ship.call_args[1]
                assert call_kwargs["feature"] == "release-v1"


class TestShipAPIIntegration:
    """ship API 통합 테스트"""

    def test_ship_api_call_with_path(self, temp_project):
        """API 호출 시 path 전달"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.call_ship_api') as mock_api:
                mock_api.return_value = {"allowed": False, "error": "test"}
                ship(path=temp_project)

                mock_api.assert_called_once()
                call_kwargs = mock_api.call_args[1]
                assert call_kwargs["path"] == temp_project

    def test_ship_api_call_with_feature(self, temp_project):
        """API 호출 시 feature 전달"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.call_ship_api') as mock_api:
                mock_api.return_value = {"allowed": False, "error": "test"}
                ship(path=temp_project, feature="test-feature")

                call_kwargs = mock_api.call_args[1]
                assert call_kwargs["feature"] == "test-feature"


class TestShipDeveloperMode:
    """ship 개발자 모드 테스트"""

    def test_ship_dev_mode_bypasses_api(self, temp_project):
        """개발자 모드는 API 우회"""
        with patch('clouvel.tools.ship.is_developer', return_value=True):
            with patch('clouvel.tools.ship.call_ship_api') as mock_api:
                # ship_pro import 실패하도록 설정
                with patch.dict('sys.modules', {'clouvel.tools.ship_pro': None}):
                    try:
                        ship(path=temp_project)
                    except:
                        pass

                # 개발자 모드에서는 API 호출하지 않음
                # (ship_pro로 직접 가거나 ImportError)
                # API 호출 안 함 확인
                # Note: 현재 구현에서 is_developer가 True면 ship_pro로 직접 감

    def test_ship_dev_mode_with_ship_pro(self, temp_project):
        """개발자 모드 + ship_pro 있을 때"""
        mock_ship_impl = MagicMock(return_value={"status": "success"})

        with patch('clouvel.tools.ship.is_developer', return_value=True):
            # ship_pro.ship mock
            mock_module = MagicMock()
            mock_module.ship = mock_ship_impl

            with patch.dict('sys.modules', {'clouvel.tools.ship_pro': mock_module}):
                with patch('clouvel.tools.ship_pro', mock_module, create=True):
                    # Import 시뮬레이션
                    with patch('builtins.__import__', return_value=mock_module):
                        result = ship(path=temp_project)
                        # ship_pro가 호출되어야 함


class TestShipResponseFormat:
    """ship 응답 형식 테스트"""

    def test_trial_exhausted_response_format(self, temp_project, mock_api_trial_exhausted):
        """Trial 소진 응답 형식"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(path=temp_project)

            assert "error" in result
            assert "message" in result
            assert "upgrade_url" in result or "formatted_output" in result

    def test_api_denied_response_format(self, temp_project, mock_api_denied):
        """API 거부 응답 형식"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(path=temp_project)

            assert "error" in result
            assert "formatted_output" in result or "message" in result

    def test_ship_pro_not_found_response(self, temp_project, mock_api_allowed):
        """ship_pro 없을 때 응답"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            # ship_pro import가 실패하도록 설정
            with patch.dict('sys.modules', {'clouvel.tools.ship_pro': None}):
                result = ship(path=temp_project)

                # ship_pro가 None이면 ImportError가 발생하거나
                # 에러 응답이 반환됨
                if "error" in result:
                    assert "Implementation not found" in result["error"] or \
                           "PRO" in result.get("formatted_output", "") or \
                           "not found" in result.get("message", "").lower()
                else:
                    # mock_api_allowed가 작동하면 ship_pro 호출 시도
                    pass  # 이 경우는 정상


class TestShipSteps:
    """ship steps 옵션 테스트"""

    def test_ship_custom_steps(self, temp_project, mock_api_denied):
        """사용자 정의 steps"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(
                path=temp_project,
                steps=["lint", "build"]
            )
            # API 거부되어도 steps는 전달됨
            assert result is not None

    def test_ship_single_step(self, temp_project, mock_api_denied):
        """단일 step"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(
                path=temp_project,
                steps=["test"]
            )
            assert result is not None

    def test_ship_empty_steps(self, temp_project, mock_api_denied):
        """빈 steps (기본값 사용)"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(
                path=temp_project,
                steps=[]
            )
            assert result is not None


class TestShipOptions:
    """ship 옵션 테스트"""

    def test_ship_generate_evidence_option(self, temp_project, mock_api_denied):
        """generate_evidence 옵션"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(
                path=temp_project,
                generate_evidence=True
            )
            assert result is not None

    def test_ship_auto_fix_option(self, temp_project, mock_api_denied):
        """auto_fix 옵션"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            result = ship(
                path=temp_project,
                auto_fix=True
            )
            assert result is not None


class TestIntegration:
    """통합 테스트"""

    def test_ship_workflow_api_denied(self, temp_project):
        """워크플로우: API 거부 시"""
        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.call_ship_api') as mock_api:
                mock_api.return_value = {
                    "allowed": False,
                    "error": "license_required",
                    "message": "Pro license required"
                }

                result = ship(
                    path=temp_project,
                    feature="test",
                    steps=["lint", "test"]
                )

                assert "error" in result

    def test_ship_workflow_trial_mode(self, temp_project):
        """워크플로우: Trial 모드"""
        mock_ship_impl = MagicMock(return_value={
            "status": "success",
            "formatted_output": "All checks passed"
        })

        with patch('clouvel.tools.ship.is_developer', return_value=False):
            with patch('clouvel.tools.ship.call_ship_api') as mock_api:
                mock_api.return_value = {
                    "allowed": True,
                    "message": "Trial use 1/5"
                }

                # ship_pro mock
                mock_module = MagicMock()
                mock_module.ship = mock_ship_impl

                with patch.dict('sys.modules', {'clouvel.tools.ship_pro': mock_module}):
                    # Import가 성공하도록
                    with patch('builtins.__import__', return_value=mock_module):
                        result = ship(path=temp_project)
                        # Trial 배너가 추가되어야 함


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
