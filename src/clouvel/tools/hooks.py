# -*- coding: utf-8 -*-
"""Hook tools (v0.8): hook_design, hook_verify"""

import json
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent


async def hook_design(path: str, trigger: str, checks: list, block_on_fail: bool) -> list[TextContent]:
    """설계 훅 - 코드 작성 전 자동 체크포인트"""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    # 트리거별 기본 체크 항목
    default_checks = {
        "pre_code": ["prd_exists", "architecture_review", "scope_defined"],
        "pre_feature": ["feature_in_prd", "api_spec_exists", "db_schema_ready"],
        "pre_refactor": ["test_coverage", "backup_exists", "rollback_plan"],
        "pre_api": ["api_spec_complete", "auth_defined", "error_codes_listed"]
    }

    # 체크 항목 설정 (사용자 지정 또는 기본값)
    active_checks = checks if checks else default_checks.get(trigger, [])

    # 훅 설정 파일 생성
    hooks_dir = project_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_config = {
        "name": f"design_{trigger}",
        "trigger": trigger,
        "checks": active_checks,
        "block_on_fail": block_on_fail,
        "created": datetime.now().isoformat()
    }

    hook_file = hooks_dir / f"{trigger}.json"
    hook_file.write_text(json.dumps(hook_config, indent=2, ensure_ascii=False), encoding='utf-8')

    # 체크리스트 생성
    checklist_md = "\n".join(f"- [ ] {check}" for check in active_checks)

    return [TextContent(type="text", text=f"""# 설계 훅 생성 완료

## 훅 설정

| 항목 | 값 |
|------|-----|
| 트리거 | `{trigger}` |
| 실패 시 차단 | {'예' if block_on_fail else '아니오'} |
| 체크 항목 | {len(active_checks)}개 |

## 체크리스트

{checklist_md}

## 저장 위치

`{hook_file}`

---

## 사용법

이 훅은 **{trigger}** 시점에 자동 트리거됩니다.

```
# 훅 실행 예시
Claude가 코드 작성 전:
1. can_code 확인
2. {trigger} 훅 체크리스트 확인
3. 모든 체크 통과 시 진행
```

**{'체크 실패 시 코드 작성이 차단됩니다.' if block_on_fail else '체크 실패해도 경고만 출력합니다.'}**
""")]


async def hook_verify(path: str, trigger: str, steps: list, parallel: bool, continue_on_error: bool) -> list[TextContent]:
    """검증 훅 - 코드 완료 후 자동 검증 체크포인트"""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    # 트리거별 기본 단계
    default_steps = {
        "post_code": ["lint", "type_check"],
        "post_feature": ["lint", "test", "build"],
        "pre_commit": ["lint", "test", "security_scan"],
        "pre_push": ["lint", "test", "build", "integration_test"]
    }

    # 단계 설정 (사용자 지정 또는 기본값)
    active_steps = steps if steps else default_steps.get(trigger, ["lint", "test", "build"])

    # 단계별 명령어 매핑
    step_commands = {
        "lint": {"cmd": "npm run lint || pylint . || ruff check .", "desc": "코드 스타일 검사"},
        "type_check": {"cmd": "tsc --noEmit || mypy .", "desc": "타입 검사"},
        "test": {"cmd": "npm test || pytest || go test ./...", "desc": "테스트 실행"},
        "build": {"cmd": "npm run build || python -m build || go build", "desc": "빌드"},
        "security_scan": {"cmd": "npm audit || safety check || gosec ./...", "desc": "보안 스캔"},
        "integration_test": {"cmd": "npm run test:e2e || pytest tests/e2e", "desc": "통합 테스트"}
    }

    # 훅 설정 파일 생성
    hooks_dir = project_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_config = {
        "name": f"verify_{trigger}",
        "trigger": trigger,
        "steps": active_steps,
        "parallel": parallel,
        "continue_on_error": continue_on_error,
        "created": datetime.now().isoformat()
    }

    hook_file = hooks_dir / f"{trigger}.json"
    hook_file.write_text(json.dumps(hook_config, indent=2, ensure_ascii=False), encoding='utf-8')

    # 단계 목록 생성
    steps_md = ""
    for i, step in enumerate(active_steps, 1):
        info = step_commands.get(step, {"cmd": step, "desc": "사용자 정의"})
        steps_md += f"{i}. **{step}**: {info['desc']}\n   ```\n   {info['cmd']}\n   ```\n\n"

    execution_mode = "병렬 (동시 실행)" if parallel else "순차 (하나씩 실행)"
    error_handling = "계속 진행" if continue_on_error else "즉시 중단"

    return [TextContent(type="text", text=f"""# 검증 훅 생성 완료

## 훅 설정

| 항목 | 값 |
|------|-----|
| 트리거 | `{trigger}` |
| 실행 모드 | {execution_mode} |
| 에러 처리 | {error_handling} |
| 단계 수 | {len(active_steps)}개 |

## 검증 단계

{steps_md}

## 저장 위치

`{hook_file}`

---

## 실행 흐름

```
{trigger} 트리거 발생
    |
    v
{'병렬 실행' if parallel else '순차 실행'}
{' -> '.join(active_steps)}
    |
    v
결과 리포트 생성
```

**트리거 시점: {trigger}**
""")]
