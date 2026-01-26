# -*- coding: utf-8 -*-
"""Verify tools (v0.5): verify, gate, handoff"""

from pathlib import Path
from datetime import datetime
from mcp.types import TextContent


async def verify(path: str, scope: str, checklist: list) -> list[TextContent]:
    """Context Bias 제거 검증

    DEPRECATED: Use `ship` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `verify` will be removed in v2.0.
Use `ship` instead - it provides:
- Automated lint/typecheck/test/build execution
- EVIDENCE.md generation
- License/Trial verification

**Migration**: Replace `verify(path, scope)` with `ship(path, steps=["lint", "test"])`

---

"""

    # 기본 체크리스트
    default_checklist = {
        "file": [
            "함수가 단일 책임을 가지는가?",
            "에러 처리가 되어 있는가?",
            "타입이 명시되어 있는가?",
        ],
        "feature": [
            "PRD에 명시된 기능인가?",
            "엣지 케이스가 처리되어 있는가?",
            "테스트가 작성되어 있는가?",
        ],
        "full": [
            "모든 필수 문서가 업데이트되었는가?",
            "보안 취약점이 없는가?",
            "성능 이슈가 없는가?",
            "접근성이 고려되었는가?",
        ],
    }

    active_checklist = checklist if checklist else default_checklist.get(scope, default_checklist["file"])
    checklist_md = "\n".join(f"- [ ] {item}" for item in active_checklist)

    result = f"""# Context Bias 제거 검증

## 검증 대상
`{path}`

## 검증 범위
**{scope}**

---

## ⚠️ 중요

**같은 세션에서 작성한 코드를 검증하면 문제를 못 봅니다.**

### 권장 절차
1. `/clear` 실행 (컨텍스트 초기화)
2. 아래 체크리스트로 검증
3. 문제 발견 시 수정

---

## 체크리스트

{checklist_md}

---

## 검증 후

- 모든 항목 통과 → `ship` 도구로 자동 검증
- 실패 항목 있음 → 수정 후 재검증

**"/clear 후 다시 보면 다르게 보인다"**
"""
    return [TextContent(type="text", text=deprecation_warning + result)]


async def gate(path: str, steps: list, fix: bool) -> list[TextContent]:
    """Gate 검증 자동화

    DEPRECATED: Use `ship` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `gate` will be removed in v2.0.
Use `ship` instead - it provides:
- Same lint/test/build execution
- Better EVIDENCE.md format
- License/Trial integration

**Migration**: Replace `gate(path, steps, fix)` with `ship(path, steps=steps, auto_fix=fix)`

---

"""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    # 기본 단계
    default_steps = ["lint", "test", "build"]
    active_steps = steps if steps else default_steps

    # 단계별 명령어 (예시)
    step_commands = {
        "lint": "npm run lint || pylint . || ruff check .",
        "test": "npm test || pytest || go test ./...",
        "build": "npm run build || python -m build || go build",
    }

    steps_md = ""
    for i, step in enumerate(active_steps, 1):
        cmd = step_commands.get(step, step)
        steps_md += f"{i}. **{step}**\n   ```\n   {cmd}\n   ```\n\n"

    # EVIDENCE.md 템플릿
    evidence_template = f"""# Gate 검증 결과

> 검증일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 경로: {path}

## 단계별 결과

| 단계 | 결과 | 비고 |
|------|------|------|
{chr(10).join(f'| {s} | ⏳ | |' for s in active_steps)}

## 자동 수정
{'활성화' if fix else '비활성화'}

---

모든 단계 PASS 시 "완료" 처리
"""

    # EVIDENCE.md 생성
    evidence_file = project_path / "EVIDENCE.md"
    evidence_file.write_text(evidence_template, encoding='utf-8')

    result = f"""# Gate 검증 시작

## 검증 단계

{steps_md}

## EVIDENCE.md
`{evidence_file}` 에 결과가 기록됩니다.

---

## 실행 방법

각 단계를 순서대로 실행하고 결과를 기록하세요.

{'lint 에러는 자동 수정을 시도합니다.' if fix else ''}

**모든 단계 PASS = 완료!**
"""
    return [TextContent(type="text", text=deprecation_warning + result)]


async def handoff(path: str, feature: str, decisions: str, warnings: str, next_steps: str) -> list[TextContent]:
    """의도 기록

    DEPRECATED: Use `record_decision` + `update_progress` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `handoff` will be removed in v2.0.
Use `record_decision` + `update_progress` instead:
- `record_decision`: Saves decisions to Knowledge Base (persists across sessions)
- `update_progress`: Tracks current session progress

**Migration**:
```
# Instead of handoff(path, feature, decisions, warnings, next_steps):
record_decision(category="feature", decision=decisions, reasoning=feature)
update_progress(path, completed=[feature], next=next_steps)
```

---

"""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    handoffs_dir = project_path / ".claude" / "handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime('%Y-%m-%d')
    safe_feature = feature.replace(" ", "-").replace("/", "-")[:30]
    handoff_file = handoffs_dir / f"{timestamp}_{safe_feature}.md"

    content = f"""# Handoff: {feature}

> 작성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 경로: {path}

---

## 완료한 작업

{feature}

---

## 주요 결정사항 (왜 이렇게 했는지)

{decisions if decisions else '(기록 필요)'}

---

## 주의할 점

{warnings if warnings else '(없음)'}

---

## 다음에 해야 할 것

{next_steps if next_steps else '(없음)'}

---

## Context Bias 제거 권장

이 기록을 남긴 후:
1. `/clear` 실행 또는 새 세션 시작
2. `verify` 도구로 검증
3. `gate` 도구로 최종 확인
4. 커밋

"""
    handoff_file.write_text(content, encoding='utf-8')

    result = f"""# Handoff 기록 완료

## 기록 위치
`{handoff_file}`

## 요약

| 항목 | 내용 |
|------|------|
| 기능 | {feature} |
| 결정사항 | {decisions[:50] + '...' if decisions and len(decisions) > 50 else decisions or '없음'} |
| 주의사항 | {warnings[:50] + '...' if warnings and len(warnings) > 50 else warnings or '없음'} |
| 다음 단계 | {next_steps[:50] + '...' if next_steps and len(next_steps) > 50 else next_steps or '없음'} |

---

**다음 작업자(또는 미래의 나)를 위한 기록이 저장되었습니다.**
"""
    return [TextContent(type="text", text=deprecation_warning + result)]
