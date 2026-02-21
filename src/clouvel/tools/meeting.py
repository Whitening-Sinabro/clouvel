# -*- coding: utf-8 -*-
"""Meeting Tool - C-Level Meeting Simulation

MCP tool that returns a prompt for Claude to simulate C-Level meetings.
No additional API calls needed - uses the host Claude to generate.

v5.0: First project = all 8 managers (unlimited)
      Additional projects (Free) = monthly quota + PM only
      Pro = all 8 managers (unlimited)
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

# v3.0: Manager data import with fallback for Free tier (PyPI)
# manager/ folder is Pro-only and excluded from PyPI distribution
try:
    from .manager.data import FREE_MANAGERS, PRO_ONLY_MANAGERS, PRO_ONLY_DESCRIPTIONS
except ImportError:
    # Fallback for Free tier - PM only
    FREE_MANAGERS = ["PM"]
    PRO_ONLY_MANAGERS = ["CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]
    PRO_ONLY_DESCRIPTIONS = {
        "CTO": "기술 아키텍처, 확장성, 기술 부채 관점",
        "QA": "품질 보증, 테스트 커버리지, 엣지 케이스 관점",
        "CSO": "보안 취약점, 컴플라이언스, 위험 관리 관점",
        "CDO": "데이터 구조, 분석 파이프라인, 개인정보 관점",
        "CMO": "사용자 경험, 시장 포지셔닝, 브랜딩 관점",
        "CFO": "비용 효율성, ROI, 리소스 배분 관점",
        "ERROR": "장애 대응, 롤백 전략, 모니터링 관점",
    }

# v3.1: Topic-specific Pro upsell messages
TOPIC_UPSELL = {
    "security": "CSO can review auth tokens, XSS/SQL injection, and compliance gaps",
    "auth": "CSO audits auth flow security + CTO reviews session management architecture",
    "performance": "CTO advises on DB indexing/caching + QA creates load test scenarios",
    "api": "CTO reviews API versioning strategy + CSO checks rate limiting",
    "payment": "CFO optimizes payment fees + CSO ensures PCI DSS compliance",
    "error": "ERROR creates incident runbooks + QA covers edge case scenarios",
    "launch": "CMO reviews go-to-market + CFO validates unit economics",
    "ui": "CDO reviews data-driven UX + CMO checks brand consistency",
    "feature": "CTO evaluates technical debt + QA plans regression testing",
    "design": "CDO reviews information architecture + CMO aligns with brand",
    "cost": "CFO analyzes cost structure + CTO identifies optimization opportunities",
    "maintenance": "CTO plans technical debt reduction + ERROR reviews monitoring gaps",
}


# License check
def _can_use_pro(project_path: str = None) -> bool:
    """Check if user can use Pro features."""
    try:
        from ..utils.entitlements import can_use_pro
        return can_use_pro(project_path)
    except ImportError:
        return False



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

    별도 API 호출 없이 Claude가 직접 회의록을 생성합니다.

    **v3.0 티어 구분**:
    - Free (추가 프로젝트): PM만 참여. 첫 프로젝트: 8명 전체
    - Pro: 8명 전체 (PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR)

    Args:
        context: 회의 주제/상황 설명
        topic: 토픽 힌트 (미지정시 자동 감지)
               지원: auth, api, payment, ui, feature, launch, error,
                     security, performance, design, cost, maintenance
        managers: 참여 매니저 목록 (미지정시 토픽에 따라 자동 선택)
                  Free 추가 프로젝트는 PM만 사용 가능 (첫 프로젝트는 전체)
        project_path: 프로젝트 경로 (Knowledge Base 연동 + 피드백 저장용)
        include_example: few-shot 예시 포함 여부
        variant: 프롬프트 버전 (A/B 테스팅용, 미지정시 자동 선택)

    Returns:
        회의 시뮬레이션 프롬프트 (Claude가 회의록 생성)

    Example:
        meeting("로그인 기능 추가. OAuth + 이메일 로그인 지원 예정")
        meeting("결제 시스템 도입", topic="payment")
        meeting("보안 감사 결과 리뷰", managers=["PM", "CTO", "CSO", "QA"])  # Pro only
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

    # v3.0: Filter managers based on license tier
    is_pro = _can_use_pro(project_path)
    missed_perspectives = []
    weekly_trial_used = False

    if not is_pro:
        # v3.3: Monthly meeting quota (3 times per month)
        monthly_quota_ok = False
        quota_notice = None

        try:
            from ..license_common import check_meeting_quota, consume_meeting_quota
            quota = check_meeting_quota(project_path)

            if quota["allowed"]:
                # Consume one meeting from quota
                consume_result = consume_meeting_quota(project_path)
                monthly_quota_ok = True
                quota_notice = consume_result.get("notice")
            else:
                # v3.3: Track A/B conversion event
                try:
                    from ..license_common import track_conversion_event
                    track_conversion_event("meeting_quota", "quota_exhausted", {
                        "used": quota.get("used", 0),
                        "limit": quota.get("limit", 3),
                    })
                except Exception:
                    pass
                # Quota exhausted - return error message
                return [TextContent(type="text", text=quota.get("message", "월별 Meeting 할당량을 모두 사용했습니다."))]
        except ImportError:
            # Fallback: allow if import fails
            monthly_quota_ok = True

        if monthly_quota_ok:
            # Full meeting allowed - no filtering
            missed_perspectives = []
        else:
            # Track Pro-only managers that were requested but filtered
            missed_perspectives = [m for m in managers if m in PRO_ONLY_MANAGERS]
            # Filter to Free tier only (PM only)
            managers = [m for m in managers if m in FREE_MANAGERS]
            # Ensure at least PM is included
            if not managers:
                managers = FREE_MANAGERS.copy()

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

    # v3.1: Add topic-specific Pro hint for Free users
    pro_hint = ""
    if missed_perspectives:
        # Topic-specific contextual upsell
        detected = topic or detect_topic(context)
        topic_specific = TOPIC_UPSELL.get(detected, "")

        missed_descriptions = [
            f"- {m}: {PRO_ONLY_DESCRIPTIONS.get(m, '')}"
            for m in missed_perspectives
        ]

        if topic_specific:
            pro_hint = f"""

---

With Pro, {topic_specific}

Missed perspectives:
{chr(10).join(missed_descriptions)}

Pro: $7.99/mo (Annual: $49/yr — Early Adopter Pricing)
-> https://polar.sh/clouvel
"""
        else:
            pro_hint = f"""

---

Missed perspectives:
{chr(10).join(missed_descriptions)}

Pro: $7.99/mo (Annual: $49/yr — Early Adopter Pricing)
-> https://polar.sh/clouvel
"""

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
            if managers is None:
                try:
                    from .manager.prompts import get_topic_guide
                    guide = get_topic_guide(topic)
                    managers = guide.get("participants", ["PM", "CTO", "QA"])
                except ImportError:
                    # Fallback for Free tier
                    managers = ["PM"]
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

    # v3.1: Log upgrade message shown event
    if pro_hint and not is_pro:
        try:
            from ..analytics import log_event
            detected_topic = topic or detect_topic(context)
            log_event("upgrade_message_shown", {"source": "meeting", "topic": detected_topic})
        except Exception:
            pass

    # v3.1: Add weekly trial badge
    weekly_badge = ""
    if not is_pro and weekly_trial_used:
        weekly_badge = "\n\n---\n\nThis week's free Full C-Level Meeting trial. Next week's trial resets automatically.\nPro: Unlimited full meetings -> https://polar.sh/clouvel ($49/yr — Early Adopter Pricing)\n"

    return [TextContent(type="text", text=prompt + footer + pro_hint + weekly_badge + rating_prompt)]


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
