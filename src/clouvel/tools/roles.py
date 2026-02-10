# -*- coding: utf-8 -*-
"""Role tools: C-Level 역할 시스템

컨텍스트 기반 자동 역할 감지 + 다중 관점 답변 시스템
- PM: 제품/비즈니스
- CTO: 기술/아키텍처
- CDO: 디자인/UX
- CFO: 비용/ROI
- CMO: 마케팅/성장
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

import yaml

from ..license import require_license_premium, require_team_license, get_cached_license
from ..content_api import fetch_content_bundle

# 로컬 역할 설정 저장 경로
CLOUVEL_DIR = Path.home() / ".clouvel"
CONFIG_FILE = CLOUVEL_DIR / "config.json"

# 유효한 역할 목록
VALID_ROLES = ["pm", "cto", "cdo", "cfo", "cmo"]


def _load_config() -> dict:
    """로컬 설정 로드"""
    if not CONFIG_FILE.exists():
        return {"active_roles": [], "mode": "manual"}

    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"active_roles": [], "mode": "manual"}


def _save_config(config: dict):
    """로컬 설정 저장"""
    CLOUVEL_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def _load_roles_content() -> dict:
    """역할 yaml 콘텐츠 로드 (서버 또는 캐시)"""
    bundle = fetch_content_bundle()
    if not bundle.get("success"):
        return {}

    content = bundle.get("content", {})
    return content.get("roles", {})


def _load_triggers() -> dict:
    """역할 트리거 로드"""
    bundle = fetch_content_bundle()
    if not bundle.get("success"):
        return {}

    content = bundle.get("content", {})
    triggers_yaml = content.get("role_triggers", "")

    if not triggers_yaml:
        return {}

    try:
        return yaml.safe_load(triggers_yaml)
    except Exception:
        return {}


def _parse_role_yaml(role_yaml: str) -> dict:
    """역할 yaml 파싱"""
    try:
        return yaml.safe_load(role_yaml)
    except Exception:
        return {}


def _generate_role_prompt(role_data: dict) -> str:
    """역할 데이터에서 프롬프트 생성"""
    if not role_data:
        return ""

    name = role_data.get("name", "Unknown")
    icon = role_data.get("icon", "")
    perspective = role_data.get("perspective", "")
    persona = role_data.get("persona", "")
    philosophy = role_data.get("philosophy", "")

    lines = [f"# {icon} {name} 모드", ""]

    if persona:
        lines.append(f"> **페르소나**: {persona}")
    if philosophy:
        lines.append(f"> **철학**: {philosophy}")
    if perspective:
        lines.append(f"> **관점**: {perspective}")
    lines.append("")

    # 원칙
    principles = role_data.get("principles", {})
    if principles:
        lines.append("## 핵심 원칙")
        lines.append("")
        for wrong in principles.get("wrong", []):
            lines.append(f"❌ {wrong}")
        for right in principles.get("right", []):
            lines.append(f"✅ {right}")
        lines.append("")

    # 체크리스트
    checklist = role_data.get("checklist", {})
    if checklist:
        lines.append("## 체크리스트")
        lines.append("")
        for category, items in checklist.items():
            lines.append(f"### {category}")
            for item in items:
                lines.append(f"- [ ] {item}")
            lines.append("")

    # 절대 금지
    never = role_data.get("never", [])
    if never:
        lines.append("## 절대 금지")
        lines.append("")
        for item in never:
            lines.append(f"- {item}")
        lines.append("")

    # 조언
    advice = role_data.get("advice", "")
    if advice:
        lines.append("---")
        lines.append("")
        lines.append(f"> {advice.strip()}")

    return "\n".join(lines)


# ============================================================
# 역할 도구 (Pro 이상)
# ============================================================

@require_license_premium
async def set_role(roles: list, mode: str = "manual") -> list[TextContent]:
    """역할 설정

    Args:
        roles: 활성화할 역할 목록 (예: ["pm", "cto"])
        mode: "manual" (수동) | "auto" (자동 감지 허용)
    """
    # 유효성 검사
    invalid = [r for r in roles if r.lower() not in VALID_ROLES]
    if invalid:
        return [TextContent(type="text", text=f"""
# ❌ 유효하지 않은 역할

**잘못된 역할**: {", ".join(invalid)}

**유효한 역할**:
- `pm` - 제품/비즈니스
- `cto` - 기술/아키텍처
- `cdo` - 디자인/UX
- `cfo` - 비용/ROI
- `cmo` - 마케팅/성장
""")]

    # 소문자로 정규화
    normalized_roles = [r.lower() for r in roles]

    # 최대 3개 제한
    if len(normalized_roles) > 3:
        normalized_roles = normalized_roles[:3]

    # 설정 저장
    config = _load_config()
    config["active_roles"] = normalized_roles
    config["mode"] = mode
    config["updated_at"] = datetime.now().isoformat()
    _save_config(config)

    # 역할 정보 로드
    roles_content = _load_roles_content()
    role_info = []
    for role in normalized_roles:
        if role in roles_content:
            data = _parse_role_yaml(roles_content[role])
            icon = data.get("icon", "")
            name = data.get("name", role.upper())
            perspective = data.get("perspective", "")
            role_info.append(f"- {icon} **{name}**: {perspective}")

    return [TextContent(type="text", text=f"""
# ✅ 역할 설정 완료

**활성 역할**: {", ".join([r.upper() for r in normalized_roles])}
**모드**: {mode} ({'자동 감지 허용' if mode == 'auto' else '수동 설정'})

## 활성화된 역할 관점
{chr(10).join(role_info) if role_info else "역할 정보를 로드할 수 없습니다."}

---

이제 모든 작업에서 위 역할 관점이 적용됩니다.
- `get_role_prompt` - 역할 프롬프트 확인
- `multi_perspective` - 다중 관점 분석
""")]


@require_license_premium
async def get_role() -> list[TextContent]:
    """현재 활성 역할 조회"""
    config = _load_config()
    active_roles = config.get("active_roles", [])
    mode = config.get("mode", "manual")
    updated_at = config.get("updated_at", "N/A")

    if not active_roles:
        return [TextContent(type="text", text="""
# 활성 역할 없음

현재 설정된 역할이 없습니다.

`set_role`로 역할을 설정하세요:
```
set_role(roles=["pm", "cto"])
```

**유효한 역할**: pm, cto, cdo, cfo, cmo
""")]

    # 역할 정보 로드
    roles_content = _load_roles_content()
    role_details = []
    for role in active_roles:
        if role in roles_content:
            data = _parse_role_yaml(roles_content[role])
            icon = data.get("icon", "")
            name = data.get("name", role.upper())
            perspective = data.get("perspective", "")
            philosophy = data.get("philosophy", "")
            role_details.append(f"""
### {icon} {name}
- **관점**: {perspective}
- **철학**: {philosophy}
""")

    return [TextContent(type="text", text=f"""
# 현재 활성 역할

**역할**: {", ".join([r.upper() for r in active_roles])}
**모드**: {mode}
**설정 시각**: {updated_at[:19] if len(updated_at) > 19 else updated_at}

{"".join(role_details)}
""")]


@require_license_premium
async def get_role_prompt(roles: list = None) -> list[TextContent]:
    """역할 프롬프트 반환

    Args:
        roles: 역할 목록 (없으면 현재 활성 역할 사용)
    """
    # 역할 결정
    if not roles:
        config = _load_config()
        roles = config.get("active_roles", [])

    if not roles:
        return [TextContent(type="text", text="""
# ⚠️ 활성 역할 없음

역할이 지정되지 않았습니다.

`set_role`로 역할을 설정하거나, `roles` 파라미터를 지정하세요.
""")]

    # 역할 프롬프트 생성
    roles_content = _load_roles_content()
    prompts = []

    for role in roles:
        role_lower = role.lower()
        if role_lower in roles_content:
            data = _parse_role_yaml(roles_content[role_lower])
            prompt = _generate_role_prompt(data)
            if prompt:
                prompts.append(prompt)

    if not prompts:
        return [TextContent(type="text", text="# ⚠️ 역할 프롬프트를 로드할 수 없습니다.")]

    combined = "\n\n---\n\n".join(prompts)

    return [TextContent(type="text", text=f"""
# 역할 프롬프트

**활성 역할**: {", ".join([r.upper() for r in roles])}

---

{combined}
""")]


@require_license_premium
async def detect_roles(context: str) -> list[TextContent]:
    """컨텍스트에서 관련 역할 자동 감지

    Args:
        context: 사용자 입력 또는 현재 작업 설명
    """
    triggers_config = _load_triggers()
    if not triggers_config:
        return [TextContent(type="text", text="""
# ⚠️ 역할 트리거를 로드할 수 없습니다.

라이선스가 활성화되어 있는지 확인하세요.
""")]

    triggers = triggers_config.get("triggers", [])
    default_roles = triggers_config.get("default_roles", ["pm"])
    max_roles = triggers_config.get("max_roles", 3)

    detected = {}  # role -> (priority, reason)
    context_lower = context.lower()

    for trigger in triggers:
        keywords = trigger.get("keywords", [])
        roles = trigger.get("roles", [])
        reason = trigger.get("reason", "")
        priority = trigger.get("priority", 5)

        for keyword in keywords:
            if keyword.lower() in context_lower:
                for role in roles:
                    if role not in detected or detected[role][0] > priority:
                        detected[role] = (priority, reason)
                break  # 하나의 키워드만 매칭되면 충분

    if not detected:
        detected_roles = default_roles
        reason = "기본 역할 (매칭되는 키워드 없음)"
    else:
        # 우선순위 순으로 정렬
        sorted_roles = sorted(detected.items(), key=lambda x: x[1][0])
        detected_roles = [r for r, _ in sorted_roles[:max_roles]]
        reasons = [f"- **{r.upper()}**: {detected[r][1]}" for r in detected_roles]
        reason = "\n".join(reasons)

    # 역할 정보 로드
    roles_content = _load_roles_content()
    role_info = []
    for role in detected_roles:
        if role in roles_content:
            data = _parse_role_yaml(roles_content[role])
            icon = data.get("icon", "")
            name = data.get("name", role.upper())
            role_info.append(f"{icon} {name}")

    return [TextContent(type="text", text=f"""
# 🔍 역할 자동 감지 결과

**입력**: "{context[:100]}{'...' if len(context) > 100 else ''}"

**감지된 역할**: {", ".join(role_info) if role_info else ", ".join([r.upper() for r in detected_roles])}

## 감지 이유
{reason}

---

이 역할들을 활성화하려면:
```
set_role(roles={detected_roles})
```
""")]


@require_license_premium
async def multi_perspective(query: str, roles: list = None) -> list[TextContent]:
    """다중 관점 분석

    Args:
        query: 분석할 주제/질문
        roles: 역할 목록 (없으면 현재 활성 역할 또는 자동 감지)
    """
    # 역할 결정
    if not roles:
        config = _load_config()
        roles = config.get("active_roles", [])

        # 자동 모드면 감지 시도
        if config.get("mode") == "auto" or not roles:
            triggers_config = _load_triggers()
            if triggers_config:
                triggers = triggers_config.get("triggers", [])
                query_lower = query.lower()
                detected = set()

                for trigger in triggers:
                    keywords = trigger.get("keywords", [])
                    trigger_roles = trigger.get("roles", [])

                    for keyword in keywords:
                        if keyword.lower() in query_lower:
                            detected.update(trigger_roles)
                            break

                if detected:
                    roles = list(detected)[:3]

    if not roles:
        roles = ["pm"]  # 기본값

    # 역할 프롬프트 로드
    roles_content = _load_roles_content()
    perspectives = []

    for role in roles:
        role_lower = role.lower()
        if role_lower not in roles_content:
            continue

        data = _parse_role_yaml(roles_content[role_lower])
        if not data:
            continue

        icon = data.get("icon", "")
        name = data.get("name", role.upper())
        perspective = data.get("perspective", "")

        # 핵심 질문 추출
        questions = data.get("questions", {})
        key_questions = []
        if isinstance(questions, dict):
            for category, qs in questions.items():
                if isinstance(qs, list):
                    key_questions.extend(qs[:2])  # 카테고리당 2개
        elif isinstance(questions, list):
            key_questions = questions[:3]

        # 체크리스트 추출
        checklist = data.get("checklist", {})
        key_checks = []
        if isinstance(checklist, dict):
            for category, checks in checklist.items():
                if isinstance(checks, list):
                    key_checks.extend(checks[:2])

        perspectives.append({
            "icon": icon,
            "name": name,
            "perspective": perspective,
            "questions": key_questions[:3],
            "checks": key_checks[:3]
        })

    # 결과 포맷팅
    sections = []
    for p in perspectives:
        section = f"""## {p['icon']} {p['name']} 관점

**관점**: {p['perspective']}

### 핵심 질문
"""
        for q in p['questions']:
            section += f"- {q}\n"

        section += "\n### 체크리스트\n"
        for c in p['checks']:
            section += f"- [ ] {c}\n"

        sections.append(section)

    combined = "\n---\n\n".join(sections)

    return [TextContent(type="text", text=f"""
# 📊 다중 관점 분석

**주제**: {query}
**분석 역할**: {", ".join([p['name'] for p in perspectives])}

---

{combined}

---

## ⚖️ 종합 분석 시 고려사항

각 역할의 관점을 종합하여:
1. 상충되는 부분 식별
2. 공통 우려사항 도출
3. 균형잡힌 의사결정

**다음 단계**: 각 관점의 체크리스트를 기반으로 구체적 분석 진행
""")]


# ============================================================
# 팀 전용 도구
# ============================================================

@require_team_license
async def sync_roles() -> list[TextContent]:
    """팀과 역할 설정 동기화"""
    # TODO: 팀 API와 동기화
    return [TextContent(type="text", text="""
# 🔄 역할 동기화

팀 역할 동기화 기능은 준비 중입니다.

현재는 로컬 설정만 사용됩니다.
""")]
