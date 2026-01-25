# -*- coding: utf-8 -*-
"""Clouvel v1.1.0 도구 테스트 (Pro 포함)"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools import (
    # core
    can_code, scan_docs, analyze_docs, init_docs, REQUIRED_DOCS,
    # docs
    get_prd_template, write_prd_section, get_prd_guide, get_verify_checklist, get_setup_guide,
    # setup
    init_clouvel, setup_cli,
    # rules (v0.5)
    init_rules, get_rule, add_rule,
    # verify (v0.5)
    verify, gate, handoff,
    # planning (v0.6)
    init_planning, save_finding, refresh_goals, update_progress,
    # agents (v0.7)
    spawn_explore, spawn_librarian,
    # hooks (v0.8)
    hook_design, hook_verify,
)


@pytest.fixture
def temp_project():
    """임시 프로젝트 디렉토리 생성"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_with_docs(temp_project):
    """docs 폴더가 있는 프로젝트"""
    docs_dir = Path(temp_project) / "docs"
    docs_dir.mkdir()
    # PRD must have acceptance section
    (docs_dir / "PRD.md").write_text("# PRD\n\n## Acceptance Criteria\n- [ ] Test", encoding='utf-8')
    (docs_dir / "ARCHITECTURE.md").write_text("# Arch", encoding='utf-8')
    (docs_dir / "API.md").write_text("# API", encoding='utf-8')
    (docs_dir / "DATABASE.md").write_text("# DB", encoding='utf-8')
    (docs_dir / "VERIFICATION.md").write_text("# Verify", encoding='utf-8')
    return temp_project


class TestCore:
    """Core 도구 테스트"""

    @pytest.mark.asyncio
    async def test_can_code_no_docs(self, temp_project):
        """docs 없으면 코딩 금지"""
        result = await can_code(f"{temp_project}/docs")
        assert "BLOCK" in result[0].text

    @pytest.mark.asyncio
    async def test_can_code_with_docs(self, project_with_docs):
        """docs 있으면 코딩 허용"""
        result = await can_code(f"{project_with_docs}/docs")
        assert "PASS" in result[0].text

    @pytest.mark.asyncio
    async def test_scan_docs(self, project_with_docs):
        """docs 스캔"""
        result = await scan_docs(f"{project_with_docs}/docs")
        assert "5 files" in result[0].text or "Total 5" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_docs(self, project_with_docs):
        """docs 분석"""
        result = await analyze_docs(f"{project_with_docs}/docs")
        assert "100%" in result[0].text

    @pytest.mark.asyncio
    async def test_init_docs(self, temp_project):
        """docs 초기화"""
        result = await init_docs(temp_project, "TestProject")
        assert "initialized" in result[0].text
        assert (Path(temp_project) / "docs" / "PRD.md").exists()


class TestDocs:
    """Docs 도구 테스트"""

    @pytest.mark.asyncio
    async def test_get_prd_template(self):
        """PRD 템플릿"""
        result = await get_prd_template("TestProject", "/tmp/prd.md")
        assert "TestProject" in result[0].text
        assert "Summary" in result[0].text or "PRD" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prd_guide(self):
        """PRD 가이드"""
        result = await get_prd_guide()
        assert "PRD" in result[0].text or "Guide" in result[0].text

    @pytest.mark.asyncio
    async def test_get_verify_checklist(self):
        """검증 체크리스트"""
        result = await get_verify_checklist()
        assert "checklist" in result[0].text.lower() or "verify" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_setup_guide(self):
        """설정 가이드"""
        result = await get_setup_guide("desktop")
        assert "Desktop" in result[0].text or "desktop" in result[0].text.lower()


class TestSetup:
    """Setup 도구 테스트"""

    @pytest.mark.asyncio
    async def test_init_clouvel_ask(self):
        """온보딩 ask"""
        result = await init_clouvel("ask")
        assert "온보딩" in result[0].text or "환경" in result[0].text

    @pytest.mark.asyncio
    async def test_setup_cli(self, temp_project):
        """CLI 설정"""
        result = await setup_cli(temp_project, "remind")
        assert "설정 완료" in result[0].text


class TestRules:
    """Rules 도구 테스트 (v0.5)"""

    @pytest.mark.asyncio
    async def test_init_rules(self, temp_project):
        """규칙 초기화"""
        result = await init_rules(temp_project, "api")
        assert "모듈화 완료" in result[0].text
        assert (Path(temp_project) / ".claude" / "rules" / "global.md").exists()

    @pytest.mark.asyncio
    async def test_get_rule(self, temp_project):
        """규칙 로딩"""
        await init_rules(temp_project, "minimal")
        result = await get_rule(temp_project, "coding")
        assert "규칙" in result[0].text

    @pytest.mark.asyncio
    async def test_add_rule(self, temp_project):
        """규칙 추가"""
        await init_rules(temp_project, "minimal")
        result = await add_rule(temp_project, "never", "테스트 규칙", "general")
        assert "추가 완료" in result[0].text


class TestVerify:
    """Verify 도구 테스트 (v0.5)"""

    @pytest.mark.asyncio
    async def test_verify(self, temp_project):
        """검증"""
        result = await verify(temp_project, "file", [])
        assert "검증" in result[0].text

    @pytest.mark.asyncio
    async def test_gate(self, temp_project):
        """Gate"""
        result = await gate(temp_project, ["lint", "test"], False)
        assert "Gate" in result[0].text

    @pytest.mark.asyncio
    async def test_handoff(self, temp_project):
        """Handoff"""
        result = await handoff(temp_project, "테스트 기능", "결정사항", "주의", "다음")
        assert "Handoff" in result[0].text


class TestPlanning:
    """Planning 도구 테스트 (v0.6)"""

    @pytest.mark.asyncio
    async def test_init_planning(self, temp_project):
        """Planning 초기화"""
        result = await init_planning(temp_project, "테스트 작업", ["목표1", "목표2"])
        assert "initialized" in result[0].text.lower() or "complete" in result[0].text.lower()
        assert (Path(temp_project) / ".claude" / "planning" / "task_plan.md").exists()

    @pytest.mark.asyncio
    async def test_save_finding(self, temp_project):
        """Finding 저장"""
        await init_planning(temp_project, "테스트", [])
        result = await save_finding(temp_project, "주제", "질문", "발견", "소스", "결론")
        assert "saved" in result[0].text.lower() or "complete" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_refresh_goals(self, temp_project):
        """목표 리마인드"""
        await init_planning(temp_project, "테스트", ["목표1"])
        result = await refresh_goals(temp_project)
        assert "goal" in result[0].text.lower() or "목표" in result[0].text

    @pytest.mark.asyncio
    async def test_update_progress(self, temp_project):
        """Progress 업데이트"""
        await init_planning(temp_project, "테스트", [])
        result = await update_progress(temp_project, ["완료1"], "진행중", [], "다음")
        assert "updated" in result[0].text.lower() or "complete" in result[0].text.lower()


class TestAgents:
    """Agent 도구 테스트 (v0.7)"""

    @pytest.mark.asyncio
    async def test_spawn_explore(self, temp_project):
        """탐색 에이전트"""
        result = await spawn_explore(temp_project, "인증 로직", "project", False)
        assert "탐색" in result[0].text

    @pytest.mark.asyncio
    async def test_spawn_librarian(self, temp_project):
        """라이브러리언 에이전트"""
        result = await spawn_librarian(temp_project, "FastAPI", "library", "quick")
        assert "라이브러리언" in result[0].text or "조사" in result[0].text


class TestHooks:
    """Hook 도구 테스트 (v0.8)"""

    @pytest.mark.asyncio
    async def test_hook_design(self, temp_project):
        """설계 훅"""
        result = await hook_design(temp_project, "pre_code", [], True)
        assert "훅" in result[0].text

    @pytest.mark.asyncio
    async def test_hook_verify(self, temp_project):
        """검증 훅"""
        result = await hook_verify(temp_project, "pre_commit", [], False, False)
        assert "훅" in result[0].text


class TestPro:
    """Pro 도구 테스트 (v1.1) - Pro 기능은 별도 패키지로 분리됨"""

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_install_shovel_no_license(self, temp_project):
        """라이선스 없이 Shovel 설치 시도"""
        pass

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_install_shovel_with_license(self, temp_project):
        """라이선스로 Shovel 설치"""
        pass

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_sync_commands_no_claude(self, temp_project):
        """sync 시 .claude 없음"""
        pass

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_sync_commands_with_shovel(self, temp_project):
        """Shovel 있을 때 sync"""
        pass

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_activate_license_valid(self):
        """유효한 라이선스 활성화"""
        pass

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_activate_license_invalid(self):
        """잘못된 라이선스"""
        pass


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_project):
        """전체 워크플로우"""
        # 1. docs 없음 확인
        result = await can_code(f"{temp_project}/docs")
        assert "BLOCK" in result[0].text

        # 2. docs 초기화
        await init_docs(temp_project, "TestProject")

        # 3. docs 있음 확인
        result = await can_code(f"{temp_project}/docs")
        assert "PASS" in result[0].text

        # 4. 규칙 초기화
        await init_rules(temp_project, "api")

        # 5. Planning 초기화
        await init_planning(temp_project, "통합 테스트", ["테스트 완료"])

        # 6. Progress 업데이트
        result = await update_progress(temp_project, ["테스트 완료"], "", [], "")
        assert "updated" in result[0].text.lower() or "complete" in result[0].text.lower()

    @pytest.mark.skip(reason="Pro features moved to clouvel-pro package")
    @pytest.mark.asyncio
    async def test_pro_full_workflow(self, temp_project):
        """Pro 전체 워크플로우"""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
