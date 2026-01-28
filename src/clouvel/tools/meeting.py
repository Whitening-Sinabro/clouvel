# -*- coding: utf-8 -*-
"""Meeting Tool - C-Level Meeting Simulation

MCP tool that returns a prompt for Claude to simulate C-Level meetings.
No additional API calls needed - uses the host Claude to generate.

Free feature: Works on all environments (Claude Desktop, CLI, VS Code)

v2.1: Basic meeting simulation
v2.2: Feedback loop + A/B testing integration
"""

from typing import Optional, List, Dict, Any
from mcp.types import TextContent

from .meeting_prompt import build_meeting_prompt, detect_topic, get_available_topics
from .meeting_tuning import (
    get_active_variant,
    get_variant_config,
    select_variant_for_ab_test,
    PROMPT_VARIANTS,
)
from .meeting_kb import get_enriched_kb_context, get_recommended_managers
from .meeting_personalization import apply_personalization, load_meeting_config



async def meeting(
    context: str,
    topic: Optional[str] = None,
    managers: Optional[List[str]] = None,
    project_path: Optional[str] = None,
    include_example: bool = True,
    variant: Optional[str] = None,
) -> List[TextContent]:
    """
    C-Level 회의 시뮬레이션.

    8명의 C-Level 매니저가 참여하는 회의를 시뮬레이션합니다.
    별도 API 호출 없이 Claude가 직접 회의록을 생성합니다.

    Args:
        context: 회의 주제/상황 설명
        topic: 토픽 힌트 (미지정시 자동 감지)
               지원: auth, api, payment, ui, feature, launch, error,
                     security, performance, design, cost, maintenance
        managers: 참여 매니저 목록 (미지정시 토픽에 따라 자동 선택)
                  지원: PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR
        project_path: 프로젝트 경로 (Knowledge Base 연동 + 피드백 저장용)
        include_example: few-shot 예시 포함 여부
        variant: 프롬프트 버전 (A/B 테스팅용, 미지정시 자동 선택)

    Returns:
        회의 시뮬레이션 프롬프트 (Claude가 회의록 생성)

    Example:
        meeting("로그인 기능 추가. OAuth + 이메일 로그인 지원 예정")
        meeting("결제 시스템 도입", topic="payment")
        meeting("보안 감사 결과 리뷰", managers=["PM", "CTO", "CSO", "QA"])
    """
    # Auto-detect topic if not provided
    if topic is None:
        topic = detect_topic(context)

    # Select variant for A/B testing
    if variant is None:
        variant = select_variant_for_ab_test(project_path)

    # Get variant configuration
    variant_config = get_variant_config(variant)

    # Override include_example if variant specifies
    if "include_example" in variant_config:
        include_example = variant_config["include_example"]

    # Apply project personalization (Phase 3)
    personalization = {}
    if project_path:
        personalization = apply_personalization(project_path, managers or [], topic)

        # Apply personalized managers if not explicitly provided
        if managers is None and personalization.get("managers"):
            managers = personalization["managers"]

        # Apply persona overrides to variant_config
        if personalization.get("persona_overrides"):
            variant_config["persona_overrides"] = personalization["persona_overrides"]

        # Apply preferences
        if personalization.get("preferences"):
            variant_config["preferences"] = personalization["preferences"]

    # Get recommended managers based on topic + project patterns (Phase 3)
    if managers is None:
        managers = get_recommended_managers(topic, project_path)

    # Get enriched KB context (Phase 3)
    kb_context = get_enriched_kb_context(context, topic, project_path)

    # Build prompt with variant config
    prompt = build_meeting_prompt(
        context=context,
        topic=topic,
        managers=managers,
        include_example=include_example,
        kb_context=kb_context,
        variant_config=variant_config,
    )

    # Add variant info footer for tracking
    footer = f"\n\n<!-- meeting_variant: {variant} -->"

    # Auto-save meeting for feedback (if project_path provided)
    meeting_id = None
    if project_path:
        try:
            from .meeting_feedback import _generate_meeting_id, _get_history_file
            import json
            from datetime import datetime

            meeting_id = _generate_meeting_id()
            history_file = _get_history_file(project_path)

            # Get actual managers used
            from .manager.prompts import get_topic_guide
            if managers is None:
                guide = get_topic_guide(topic)
                managers = guide.get("participants", ["PM", "CTO", "QA"])
                if "PM" not in managers:
                    managers = ["PM"] + managers
                managers = managers[:5]

            record = {
                "id": meeting_id,
                "timestamp": datetime.now().isoformat(),
                "context": context[:500],
                "topic": topic,
                "managers": managers,
                "prompt_version": variant,
                "prompt_length": len(prompt),
            }

            with open(history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        except Exception:
            pass  # Don't fail meeting on tracking error

    # Add rating prompt if meeting_id generated
    rating_prompt = ""
    if meeting_id:
        rating_prompt = f"""

---

회의가 끝나면 평가를 남겨주세요:
```
rate_meeting(project_path="{project_path}", meeting_id="{meeting_id}", rating=4, feedback="유용했음")
```
"""

    return [TextContent(type="text", text=prompt + footer + rating_prompt)]


async def meeting_topics() -> List[TextContent]:
    """
    사용 가능한 회의 토픽 목록 반환.

    Returns:
        토픽 목록과 설명
    """
    topics = get_available_topics()

    topic_descriptions = {
        "auth": "인증/로그인 관련",
        "api": "API 설계/구현",
        "payment": "결제 시스템",
        "ui": "UI/UX 디자인",
        "feature": "일반 기능 구현",
        "launch": "출시/배포 준비",
        "error": "에러/장애 대응",
        "security": "보안 이슈",
        "performance": "성능 최적화",
        "design": "디자인 시스템",
        "cost": "비용 관리",
        "maintenance": "유지보수",
    }

    lines = ["## 지원 토픽\n"]
    for topic in topics:
        desc = topic_descriptions.get(topic, "")
        lines.append(f"- **{topic}**: {desc}")

    lines.append("\n---\n")
    lines.append("토픽을 지정하지 않으면 컨텍스트에서 자동 감지합니다.")

    return [TextContent(type="text", text="\n".join(lines))]
