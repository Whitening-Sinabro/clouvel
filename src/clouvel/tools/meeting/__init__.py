# -*- coding: utf-8 -*-
"""Meeting Subpackage

Consolidates all meeting-related tools:
- core: meeting(), meeting_topics()
- data: Standalone persona/example data (PyPI Free fallback)
- feedback: save_meeting(), rate_meeting(), get_meeting_stats(), export_training_data()
- kb: Knowledge Base integration for meeting context enrichment
- personalization: Project-specific meeting customization
- prompt: Prompt building for meeting simulation
- tuning: A/B testing and variant management
"""

from .core import meeting, meeting_topics
from .feedback import (
    save_meeting,
    rate_meeting,
    get_meeting_stats,
    export_training_data,
    _generate_meeting_id,
    _get_history_file,
)
from .tuning import (
    enable_ab_testing,
    disable_ab_testing,
    get_variant_performance,
    list_variants,
    get_active_variant,
    get_variant_config,
    select_variant_for_ab_test,
    PROMPT_VARIANTS,
)
from .personalization import (
    configure_meeting,
    add_persona_override,
    add_custom_prompt,
    get_meeting_config,
    reset_meeting_config,
    load_meeting_config,
    apply_personalization,
)
from .kb import (
    get_enriched_kb_context,
    get_recommended_managers,
    analyze_project_patterns,
)
from .prompt import (
    build_meeting_prompt,
    get_available_topics,
    detect_topic,
)
from .data import (
    PERSONAS,
    TOPIC_GUIDES,
    EXAMPLES,
    TOPIC_KEYWORDS,
    get_persona,
    get_topic_guide,
    get_examples_for_topic,
    format_examples_for_prompt,
    analyze_context,
)

__all__ = [
    # core
    "meeting", "meeting_topics",
    # feedback
    "save_meeting", "rate_meeting", "get_meeting_stats", "export_training_data",
    "_generate_meeting_id", "_get_history_file",
    # tuning
    "enable_ab_testing", "disable_ab_testing", "get_variant_performance", "list_variants",
    "get_active_variant", "get_variant_config", "select_variant_for_ab_test", "PROMPT_VARIANTS",
    # personalization
    "configure_meeting", "add_persona_override", "add_custom_prompt",
    "get_meeting_config", "reset_meeting_config",
    "load_meeting_config", "apply_personalization",
    # kb
    "get_enriched_kb_context", "get_recommended_managers", "analyze_project_patterns",
    # prompt
    "build_meeting_prompt", "get_available_topics", "detect_topic",
    # data
    "PERSONAS", "TOPIC_GUIDES", "EXAMPLES", "TOPIC_KEYWORDS",
    "get_persona", "get_topic_guide", "get_examples_for_topic",
    "format_examples_for_prompt", "analyze_context",
]
