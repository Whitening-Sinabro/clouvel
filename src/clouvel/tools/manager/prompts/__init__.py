# Manager Prompts
# Tunable prompt system

from .personas import PERSONAS, get_persona, get_all_personas_summary
from .templates import (
    MEETING_TEMPLATE,
    get_system_prompt,
    get_persona_prompt,
    get_topic_guide,
    get_conversation_starter,
    TOPIC_GUIDES,
    CONVERSATION_STARTERS,
)
from .examples import (
    EXAMPLES,
    get_examples_for_topic,
    get_all_examples,
    format_examples_for_prompt,
)

__all__ = [
    # 페르소나
    "PERSONAS",
    "get_persona",
    "get_all_personas_summary",

    # 템플릿
    "MEETING_TEMPLATE",
    "get_system_prompt",
    "get_persona_prompt",
    "get_topic_guide",
    "get_conversation_starter",
    "TOPIC_GUIDES",
    "CONVERSATION_STARTERS",

    # 예시
    "EXAMPLES",
    "get_examples_for_topic",
    "get_all_examples",
    "format_examples_for_prompt",
]
