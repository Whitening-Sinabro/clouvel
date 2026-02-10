# Clouvel Manager Tool (Pro)
# 8 C-Level managers provide context-based collaborative feedback
#
# v2: Dynamic meeting generation support
# - 15-20 year veteran personas
# - Natural conversational meeting notes
# - Auto-collect tuning data

from .data import (
    MANAGERS,
    CONTEXT_GROUPS,
    PHASE_ORDER,
    FREE_MANAGERS,
    PRO_ONLY_MANAGERS,
    PRO_ONLY_DESCRIPTIONS,
)
from .core import manager, ask_manager, manager_dynamic, get_meeting_prompt, quick_perspectives
from .utils import list_managers

# Dynamic meeting generation module
from .generator import (
    generate_meeting,
    generate_meeting_sync,
    MeetingGenerator,
    MeetingConfig,
    MeetingCollector,
    save_meeting_log,
    get_training_data,
)

# Personas and prompts
from .prompts import (
    PERSONAS,
    get_persona,
    get_system_prompt,
    get_topic_guide,
    EXAMPLES,
    get_examples_for_topic,
)

__all__ = [
    # Core API
    "MANAGERS",
    "CONTEXT_GROUPS",
    "PHASE_ORDER",
    "FREE_MANAGERS",
    "PRO_ONLY_MANAGERS",
    "PRO_ONLY_DESCRIPTIONS",
    "manager",
    "ask_manager",
    "list_managers",
    "quick_perspectives",

    # v2: Dynamic meeting generation
    "manager_dynamic",
    "get_meeting_prompt",
    "generate_meeting",
    "generate_meeting_sync",
    "MeetingGenerator",
    "MeetingConfig",

    # Personas and prompts
    "PERSONAS",
    "get_persona",
    "get_system_prompt",
    "get_topic_guide",
    "EXAMPLES",
    "get_examples_for_topic",

    # Tuning data collection
    "MeetingCollector",
    "save_meeting_log",
    "get_training_data",
]
