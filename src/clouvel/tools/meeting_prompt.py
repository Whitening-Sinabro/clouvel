# -*- coding: utf-8 -*-
"""Meeting Prompt Builder

Builds high-quality prompts for C-Level meeting simulation.
Uses PERSONAS and EXAMPLES to generate natural meeting transcripts.

Phase 1: Basic prompt building
Phase 2+: Feedback loop, A/B testing, KB integration
"""

from typing import List, Optional, Dict, Any

# Try to import from manager module (full version), fallback to meeting_data (PyPI Free)
try:
    from .manager.prompts.personas import PERSONAS, get_persona
    from .manager.prompts.examples import get_examples_for_topic, format_examples_for_prompt
    from .manager.prompts import get_topic_guide
    from .manager.utils import _analyze_context
except ImportError:
    # Fallback to standalone meeting data
    from .meeting_data import (
        PERSONAS,
        get_persona,
        get_examples_for_topic,
        format_examples_for_prompt,
        get_topic_guide,
        analyze_context as _analyze_context,
    )


def build_meeting_prompt(
    context: str,
    topic: Optional[str] = None,
    managers: Optional[List[str]] = None,
    include_example: bool = True,
    kb_context: Optional[str] = None,
    variant_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build a prompt for C-Level meeting simulation.

    Args:
        context: Meeting topic/situation description
        topic: Topic hint (auto-detected if None)
        managers: List of managers to include (auto-selected if None)
        include_example: Whether to include few-shot example
        kb_context: Knowledge Base context (past decisions)
        variant_config: Prompt variant configuration for A/B testing

    Returns:
        Formatted prompt for Claude to simulate meeting
    """
    # Apply variant config defaults
    if variant_config is None:
        variant_config = {}

    include_probing_questions = variant_config.get("include_probing_questions", True)
    persona_detail = variant_config.get("persona_detail", "full")
    example_count = variant_config.get("example_count", 1)

    # Override include_example if variant specifies
    if "include_example" in variant_config:
        include_example = variant_config["include_example"]

    # 1. Detect topic
    if topic is None:
        detected_topics = _analyze_context(context)
        topic = detected_topics[0] if detected_topics else "feature"

    # 2. Select managers
    if managers is None:
        guide = get_topic_guide(topic)
        managers = guide.get("participants", ["PM", "CTO", "QA"])

    # Always include PM
    if "PM" not in managers:
        managers.insert(0, "PM")

    # Limit to 5 managers for focused discussion
    managers = managers[:5]

    # 3. Build persona summaries (respecting persona_detail setting)
    persona_lines = []
    for mgr_key in managers:
        persona = get_persona(mgr_key)
        if persona:
            # Extract key info for prompt
            emoji = persona.get("emoji", "")
            title = persona.get("title", mgr_key)
            years = persona.get("years", "")

            if persona_detail == "minimal":
                # Minimal: just name and emoji
                persona_lines.append(f"- {emoji} {mgr_key}")
            elif persona_detail == "summary":
                # Summary: name, title, one line
                persona_lines.append(f"- {emoji} {mgr_key} ({title})")
            else:
                # Full: complete persona info
                # Get communication style
                comm = persona.get("communication", {})
                tone = comm.get("tone", "")
                pet_phrases = comm.get("pet_phrases", [])[:2]

                persona_line = f"""
**{emoji} {mgr_key}** ({title}, {years}년 경력)
- 스타일: {tone}
- 자주 하는 말: {', '.join(pet_phrases)}"""

                # Add probing questions only if enabled
                if include_probing_questions:
                    probing = persona.get("probing_questions", {})
                    topic_questions = _get_relevant_questions(probing, topic)
                    persona_line += f"\n- 이번 토픽 관련 질문: {', '.join(topic_questions[:2])}"

                persona_lines.append(persona_line)

    personas_section = "\n".join(persona_lines)

    # 4. Get example (few-shot) - respecting example_count
    example_section = ""
    if include_example and example_count > 0:
        examples = get_examples_for_topic(topic, limit=example_count)
        if examples:
            example_parts = []
            for i, ex in enumerate(examples):
                example_parts.append(f"""
## 예시 회의록 {i + 1 if len(examples) > 1 else ''}

**상황**: {ex['context']}

{ex['output']}
""")
            example_section = f"""
---
{chr(10).join(example_parts)}
---
"""

    # 5. KB context (if available)
    kb_section = ""
    if kb_context:
        kb_section = f"""
---

## 프로젝트 히스토리

{kb_context}

_위 과거 결정사항을 참고하여 회의를 진행하세요._

---
"""

    # 6. Build final prompt
    prompt = f"""## C-Level 회의 시뮬레이션 요청

아래 상황에 대해 C-Level 회의를 시뮬레이션해주세요.

---

### 회의 정보

**토픽**: {topic}
**참여자**: {', '.join([f"{PERSONAS.get(m, {}).get('emoji', '')} {m}" for m in managers])}

---

### 상황/컨텍스트

{context}

---

### 참여 매니저 프로필
{personas_section}

{kb_section}

---

### 회의 규칙

1. **자연스러운 대화**: 매니저들이 서로 대화하듯 진행
2. **구체적 의견**: 일반론이 아닌, 컨텍스트에 맞는 구체적 의견
3. **의견 충돌 허용**: 다른 의견이 있으면 논의 후 합의
4. **솔로 개발자 현실 고려**: 리소스 제약을 감안한 현실적 조언
5. **액션 아이템으로 마무리**: 구체적인 다음 단계 정리

---

### 출력 형식

```
## C-Level 회의록

**[이모지] [매니저]**: [발언 내용]

**[이모지] [매니저]**: [발언 내용]
...

---

## 액션 아이템

| # | 담당 | 작업 | 우선순위 |
|---|------|------|----------|
| 1 | ... | ... | P0/P1/P2 |

## 주의사항
- NEVER: [하면 안 되는 것들]
- ALWAYS: [반드시 해야 하는 것들]
```

{example_section}

---

위 설정으로 회의를 진행해주세요. 매니저들이 실제로 대화하는 것처럼 자연스럽게 시뮬레이션해주세요.
"""

    return prompt


def _get_relevant_questions(probing_questions: Dict[str, List[str]], topic: str) -> List[str]:
    """Get relevant probing questions based on topic."""

    # Topic to question category mapping
    topic_to_category = {
        "auth": ["auth_authz", "attack_surface", "scope"],
        "api": ["architecture", "tradeoffs", "edge_cases"],
        "payment": ["cost_awareness", "attack_surface", "revenue"],
        "ui": ["user_journey", "visual_hierarchy", "states_and_feedback"],
        "feature": ["scope", "user_value", "tradeoffs"],
        "launch": ["target_audience", "distribution", "observability"],
        "error": ["failure_scenarios", "recovery", "learning"],
        "security": ["attack_surface", "auth_authz", "data_protection"],
        "performance": ["architecture", "cost_awareness", "observability"],
        "design": ["visual_hierarchy", "accessibility", "user_journey"],
        "cost": ["cost_awareness", "revenue", "roi"],
        "maintenance": ["maintainability", "dependencies", "observability"],
    }

    categories = topic_to_category.get(topic, ["scope", "tradeoffs"])

    questions = []
    for cat in categories:
        if cat in probing_questions:
            questions.extend(probing_questions[cat][:2])
            if len(questions) >= 3:
                break

    # Fallback: get from any category
    if not questions:
        for cat, qs in probing_questions.items():
            questions.extend(qs[:2])
            if len(questions) >= 3:
                break

    return questions[:3]


def get_available_topics() -> List[str]:
    """Return list of available topics with examples."""
    from .manager.prompts.examples import EXAMPLES
    return list(EXAMPLES.keys())


def detect_topic(context: str) -> str:
    """Detect topic from context."""
    detected = _analyze_context(context)
    return detected[0] if detected else "feature"
