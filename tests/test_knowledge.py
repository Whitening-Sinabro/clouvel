# -*- coding: utf-8 -*-
"""Clouvel Knowledge Base 도구 테스트 (v1.4+)

P0 테스트: record_decision, record_location, search_knowledge, get_context 등
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.knowledge import (
    record_decision,
    record_location,
    search_knowledge,
    get_context,
    init_knowledge,
    rebuild_index,
    unlock_decision,
    list_locked_decisions,
    can_use_kb,
    PRO_MESSAGE,
)


@pytest.fixture
def temp_home():
    """임시 홈 디렉토리 (Knowledge DB 격리)"""
    temp_dir = tempfile.mkdtemp()
    old_home = os.environ.get("HOME")
    old_userprofile = os.environ.get("USERPROFILE")

    os.environ["HOME"] = temp_dir
    os.environ["USERPROFILE"] = temp_dir

    # DB 모듈의 경로도 패치
    from clouvel.db import knowledge as kb_module
    old_db_path = kb_module.KNOWLEDGE_DB_PATH
    old_archive_path = kb_module.ARCHIVE_DB_PATH
    kb_module.KNOWLEDGE_DB_PATH = Path(temp_dir) / ".clouvel" / "knowledge.db"
    kb_module.ARCHIVE_DB_PATH = Path(temp_dir) / ".clouvel" / "knowledge_archive.db"

    yield temp_dir

    # Restore
    kb_module.KNOWLEDGE_DB_PATH = old_db_path
    kb_module.ARCHIVE_DB_PATH = old_archive_path

    if old_home:
        os.environ["HOME"] = old_home
    else:
        os.environ.pop("HOME", None)
    if old_userprofile:
        os.environ["USERPROFILE"] = old_userprofile
    else:
        os.environ.pop("USERPROFILE", None)

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_developer_mode():
    """개발자 모드 mock"""
    with patch('clouvel.tools.knowledge.is_developer', return_value=True):
        with patch('clouvel.tools.knowledge.can_use_kb', return_value=True):
            yield


@pytest.fixture
def mock_no_db():
    """DB 없는 Free 버전 mock"""
    with patch('clouvel.tools.knowledge.is_developer', return_value=False):
        with patch('clouvel.tools.knowledge._get_db', return_value=None):
            yield


class TestCanUseKB:
    """can_use_kb 권한 체크 테스트"""

    def test_can_use_kb_developer_mode(self):
        """개발자 모드에서는 항상 True"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            assert can_use_kb() == True

    def test_can_use_kb_with_project_path(self):
        """project_path로 개발자 감지"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            assert can_use_kb("D:\\clouvel") == True

    def test_can_use_kb_no_db_no_dev(self):
        """DB 없고 개발자 아니면 False"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=False):
            with patch('clouvel.tools.knowledge._get_db', return_value=None):
                assert can_use_kb() == False

    def test_can_use_kb_with_db(self):
        """DB 있으면 True (Pro 설치됨)"""
        mock_db = MagicMock()
        with patch('clouvel.tools.knowledge.is_developer', return_value=False):
            with patch('clouvel.tools.knowledge._get_db', return_value=mock_db):
                assert can_use_kb() == True


class TestRecordDecision:
    """record_decision 테스트"""

    @pytest.mark.asyncio
    async def test_record_decision_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await record_decision(
            category="test",
            decision="Test decision"
        )
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_record_decision_basic(self, temp_home):
        """기본 결정 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_decision(
                category="architecture",
                decision="Use SQLite for storage",
                reasoning="Simple and portable",
                project_path=temp_home
            )

            assert result["status"] == "recorded"
            assert "decision_id" in result
            assert result["category"] == "architecture"
            assert result["locked"] == False

    @pytest.mark.asyncio
    async def test_record_decision_with_alternatives(self, temp_home):
        """대안 포함 결정 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_decision(
                category="database",
                decision="Use PostgreSQL",
                reasoning="Scalability",
                alternatives=["MySQL", "MongoDB", "SQLite"],
                project_path=temp_home
            )

            assert result["status"] == "recorded"

    @pytest.mark.asyncio
    async def test_record_decision_locked(self, temp_home):
        """잠긴 결정 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_decision(
                category="security",
                decision="Use JWT for auth",
                locked=True,
                project_path=temp_home
            )

            assert result["status"] == "recorded"
            assert result["locked"] == True

    @pytest.mark.asyncio
    async def test_record_decision_with_project_name(self, temp_home):
        """프로젝트명 포함 결정 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_decision(
                category="feature",
                decision="Add dark mode",
                project_name="clouvel",
                project_path=temp_home
            )

            assert result["status"] == "recorded"
            assert result["project_id"] is not None


class TestRecordLocation:
    """record_location 테스트"""

    @pytest.mark.asyncio
    async def test_record_location_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await record_location(
            name="Test",
            repo="test-repo",
            path="src/test.py"
        )
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_record_location_basic(self, temp_home):
        """기본 위치 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_location(
                name="License validation",
                repo="clouvel",
                path="src/clouvel/license.py:42",
                description="License validation endpoint",
                project_path=temp_home
            )

            assert result["status"] == "recorded"
            assert "location_id" in result
            assert result["name"] == "License validation"
            assert result["repo"] == "clouvel"

    @pytest.mark.asyncio
    async def test_record_location_with_project(self, temp_home):
        """프로젝트 연결 위치 기록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await record_location(
                name="API endpoint",
                repo="clouvel-workers",
                path="src/index.ts:100",
                project_name="clouvel",
                project_path=temp_home
            )

            assert result["status"] == "recorded"
            assert result["project_id"] is not None


class TestSearchKnowledge:
    """search_knowledge 테스트"""

    @pytest.mark.asyncio
    async def test_search_knowledge_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await search_knowledge(query="test")
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_search_knowledge_empty(self, temp_home):
        """빈 검색 결과"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await search_knowledge(
                query="nonexistent",
                project_path=temp_home
            )

            assert result["status"] == "success"
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_search_knowledge_find_decision(self, temp_home):
        """결정 검색"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 먼저 결정 기록
            await record_decision(
                category="architecture",
                decision="Use SQLite for knowledge base",
                project_path=temp_home
            )

            # 검색
            result = await search_knowledge(
                query="SQLite",
                project_path=temp_home
            )

            assert result["status"] == "success"
            assert result["count"] >= 1

    @pytest.mark.asyncio
    async def test_search_knowledge_find_location(self, temp_home):
        """위치 검색"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 먼저 위치 기록
            await record_location(
                name="Manager core",
                repo="clouvel",
                path="src/clouvel/tools/manager/core.py",
                project_path=temp_home
            )

            # 검색
            result = await search_knowledge(
                query="manager",
                project_path=temp_home
            )

            assert result["status"] == "success"
            assert result["count"] >= 1

    @pytest.mark.asyncio
    async def test_search_knowledge_with_limit(self, temp_home):
        """검색 결과 제한"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 여러 결정 기록
            for i in range(5):
                await record_decision(
                    category="test",
                    decision=f"Test decision {i}",
                    project_path=temp_home
                )

            # limit=2로 검색
            result = await search_knowledge(
                query="Test decision",
                limit=2,
                project_path=temp_home
            )

            assert result["status"] == "success"
            assert result["count"] <= 2


class TestGetContext:
    """get_context 테스트"""

    @pytest.mark.asyncio
    async def test_get_context_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await get_context()
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_get_context_empty(self, temp_home):
        """빈 컨텍스트"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await get_context(project_path=temp_home)

            assert result["status"] == "success"
            assert "decisions" in result
            assert "locations" in result

    @pytest.mark.asyncio
    async def test_get_context_with_data(self, temp_home):
        """데이터 있는 컨텍스트"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 데이터 기록
            await record_decision(
                category="test",
                decision="Test decision",
                project_path=temp_home
            )
            await record_location(
                name="Test location",
                repo="test",
                path="test.py",
                project_path=temp_home
            )

            result = await get_context(project_path=temp_home)

            assert result["status"] == "success"
            assert len(result["decisions"]) >= 1
            assert len(result["locations"]) >= 1

    @pytest.mark.asyncio
    async def test_get_context_decisions_only(self, temp_home):
        """결정만 포함"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await get_context(
                include_decisions=True,
                include_locations=False,
                project_path=temp_home
            )

            assert result["status"] == "success"
            assert "decisions" in result
            assert "locations" not in result


class TestInitKnowledge:
    """init_knowledge 테스트"""

    @pytest.mark.asyncio
    async def test_init_knowledge_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await init_knowledge()
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_init_knowledge_creates_db(self, temp_home):
        """DB 파일 생성"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            result = await init_knowledge(project_path=temp_home)

            assert result["status"] == "initialized"
            assert "db_path" in result
            assert Path(result["db_path"]).exists()


class TestRebuildIndex:
    """rebuild_index 테스트"""

    @pytest.mark.asyncio
    async def test_rebuild_index_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await rebuild_index()
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_rebuild_index_empty(self, temp_home):
        """빈 DB에서 인덱스 재구축"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            await init_knowledge(project_path=temp_home)
            result = await rebuild_index(project_path=temp_home)

            assert result["status"] == "rebuilt"
            # 기존 글로벌 DB에 데이터 있을 수 있으므로 0 이상만 확인
            assert result["indexed_count"] >= 0

    @pytest.mark.asyncio
    async def test_rebuild_index_with_data(self, temp_home):
        """데이터 있는 DB에서 인덱스 재구축"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 데이터 기록
            await record_decision(
                category="test",
                decision="Test",
                project_path=temp_home
            )
            await record_location(
                name="Test",
                repo="test",
                path="test.py",
                project_path=temp_home
            )

            result = await rebuild_index(project_path=temp_home)

            assert result["status"] == "rebuilt"
            assert result["indexed_count"] >= 2


class TestUnlockDecision:
    """unlock_decision 테스트"""

    @pytest.mark.asyncio
    async def test_unlock_decision_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await unlock_decision(decision_id=1, reason="Test")
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_unlock_decision_not_found(self, temp_home):
        """존재하지 않는 결정 unlock"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                await init_knowledge(project_path=temp_home)
                result = await unlock_decision(
                    decision_id=9999,
                    reason="Test",
                    project_path=temp_home
                )

                assert result["status"] == "error"
                assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_unlock_decision_not_locked(self, temp_home):
        """잠기지 않은 결정 unlock 시도"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                # 잠기지 않은 결정 생성
                rec_result = await record_decision(
                    category="test",
                    decision="Unlocked decision",
                    locked=False,
                    project_path=temp_home
                )

                result = await unlock_decision(
                    decision_id=int(rec_result["decision_id"]),
                    reason="Test",
                    project_path=temp_home
                )

                assert result["status"] == "error"
                assert "not locked" in result["error"]

    @pytest.mark.asyncio
    async def test_unlock_decision_success(self, temp_home):
        """잠긴 결정 unlock 성공"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                # 잠긴 결정 생성
                rec_result = await record_decision(
                    category="architecture",
                    decision="Locked architecture decision",
                    locked=True,
                    project_path=temp_home
                )

                # Unlock
                result = await unlock_decision(
                    decision_id=int(rec_result["decision_id"]),
                    reason="No longer needed",
                    project_path=temp_home
                )

                assert result["status"] == "unlocked"
                assert result["category"] == "architecture"
                assert result["unlock_reason"] == "No longer needed"


class TestListLockedDecisions:
    """list_locked_decisions 테스트"""

    @pytest.mark.asyncio
    async def test_list_locked_decisions_pro_required(self, mock_no_db):
        """Pro 없으면 PRO_MESSAGE 반환"""
        result = await list_locked_decisions()
        assert result == PRO_MESSAGE

    @pytest.mark.asyncio
    async def test_list_locked_decisions_empty(self, temp_home):
        """잠긴 결정 없음 (새 프로젝트)"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                await init_knowledge(project_path=temp_home)
                # 새 프로젝트에서 잠긴 결정 확인
                result = await list_locked_decisions(
                    project_name="empty-test-project",
                    project_path=temp_home
                )

                assert result["status"] == "success"
                # 새 프로젝트에는 잠긴 결정 없음
                assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_list_locked_decisions_with_data(self, temp_home):
        """잠긴 결정 목록"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                # 잠긴 결정 2개 생성
                await record_decision(
                    category="arch1",
                    decision="Locked 1",
                    locked=True,
                    project_path=temp_home
                )
                await record_decision(
                    category="arch2",
                    decision="Locked 2",
                    locked=True,
                    project_path=temp_home
                )
                # 잠기지 않은 결정 1개
                await record_decision(
                    category="other",
                    decision="Not locked",
                    locked=False,
                    project_path=temp_home
                )

                result = await list_locked_decisions(project_path=temp_home)

                assert result["status"] == "success"
                assert result["count"] >= 2
                for d in result["decisions"]:
                    assert d["locked"] == True


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_home):
        """전체 워크플로우: 초기화 → 기록 → 검색 → 잠금 → 해제"""
        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            with patch('pathlib.Path.home', return_value=Path(temp_home)):
                # 1. 초기화
                init_result = await init_knowledge(project_path=temp_home)
                assert init_result["status"] == "initialized"

                # 2. 결정 기록 (잠금)
                decision_result = await record_decision(
                    category="architecture",
                    decision="Use SQLite for KB",
                    reasoning="Simple and portable",
                    locked=True,
                    project_path=temp_home
                )
                assert decision_result["status"] == "recorded"
                decision_id = int(decision_result["decision_id"])

                # 3. 위치 기록
                location_result = await record_location(
                    name="KB module",
                    repo="clouvel",
                    path="src/clouvel/db/knowledge.py",
                    project_path=temp_home
                )
                assert location_result["status"] == "recorded"

                # 4. 검색
                search_result = await search_knowledge(
                    query="SQLite",
                    project_path=temp_home
                )
                assert search_result["status"] == "success"
                assert search_result["count"] >= 1

                # 5. 컨텍스트 조회
                context_result = await get_context(project_path=temp_home)
                assert context_result["status"] == "success"
                assert len(context_result["decisions"]) >= 1
                assert len(context_result["locations"]) >= 1

                # 6. 잠긴 결정 목록
                locked_result = await list_locked_decisions(project_path=temp_home)
                assert locked_result["status"] == "success"
                assert locked_result["count"] >= 1

                # 7. 결정 잠금 해제
                unlock_result = await unlock_decision(
                    decision_id=decision_id,
                    reason="Testing unlock",
                    project_path=temp_home
                )
                assert unlock_result["status"] == "unlocked"

                # 8. 잠긴 결정 다시 확인 (감소)
                locked_result2 = await list_locked_decisions(project_path=temp_home)
                assert locked_result2["count"] < locked_result["count"]

    @pytest.mark.asyncio
    async def test_multiple_projects(self, temp_home):
        """여러 프로젝트 분리 (이름 기반)"""
        import uuid
        unique_suffix = uuid.uuid4().hex[:8]

        with patch('clouvel.tools.knowledge.is_developer', return_value=True):
            # 프로젝트 A (이름만 지정, path 없음 → 이름으로 구분)
            project_a_name = f"project-a-{unique_suffix}"
            result_a = await record_decision(
                category="test",
                decision="Project A decision",
                project_name=project_a_name
                # project_path 없음 → 이름으로만 프로젝트 생성
            )

            # 프로젝트 B (다른 이름)
            project_b_name = f"project-b-{unique_suffix}"
            result_b = await record_decision(
                category="test",
                decision="Project B decision",
                project_name=project_b_name
                # project_path 없음 → 이름으로만 프로젝트 생성
            )

            # 각 프로젝트는 다른 project_id 가짐
            assert result_a["project_id"] != result_b["project_id"]

            # 프로젝트 A 컨텍스트
            context_a = await get_context(project_name=project_a_name)
            assert context_a["status"] == "success"

            # 프로젝트 B 컨텍스트
            context_b = await get_context(project_name=project_b_name)
            assert context_b["status"] == "success"

            # 각 프로젝트의 결정은 분리됨
            assert context_a["project_id"] != context_b["project_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
