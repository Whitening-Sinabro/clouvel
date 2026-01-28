# -*- coding: utf-8 -*-
"""Meeting Personalization

Project-specific meeting customization.
- Custom persona overrides
- Manager weight adjustments
- Project-specific prompts

Phase 3: Personalized meetings per project
"""

import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from mcp.types import TextContent


# Default config template
DEFAULT_MEETING_CONFIG = {
    "version": "1.0.0",
    "manager_weights": {
        "PM": 1.0,
        "CTO": 1.0,
        "QA": 1.0,
        "CSO": 1.0,
        "CDO": 1.0,
        "CMO": 1.0,
        "CFO": 1.0,
        "ERROR": 1.0,
    },
    "persona_overrides": {},
    "default_managers_by_topic": {},
    "custom_prompts": {},
    "preferences": {
        "language": "ko",  # ko, en, mixed
        "formality": "casual",  # formal, casual, mixed
        "detail_level": "full",  # full, summary, minimal
    }
}


def _get_config_path(project_path: str) -> Path:
    """Get meeting config file path."""
    return Path(project_path) / ".clouvel" / "meeting_config.json"


def load_meeting_config(project_path: str) -> Dict[str, Any]:
    """
    Load project-specific meeting configuration.

    Args:
        project_path: Project root path

    Returns:
        Meeting configuration dict
    """
    config_path = _get_config_path(project_path)

    if not config_path.exists():
        return DEFAULT_MEETING_CONFIG.copy()

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        # Merge with defaults
        merged = DEFAULT_MEETING_CONFIG.copy()
        merged.update(config)
        return merged
    except Exception:
        return DEFAULT_MEETING_CONFIG.copy()


def save_meeting_config(project_path: str, config: Dict[str, Any]) -> bool:
    """
    Save project-specific meeting configuration.

    Args:
        project_path: Project root path
        config: Configuration dict

    Returns:
        Success status
    """
    config_path = _get_config_path(project_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


async def configure_meeting(
    project_path: str,
    manager_weights: Optional[Dict[str, float]] = None,
    default_managers: Optional[Dict[str, List[str]]] = None,
    preferences: Optional[Dict[str, str]] = None,
) -> List[TextContent]:
    """
    Configure project-specific meeting settings.

    Args:
        project_path: Project root path
        manager_weights: Weight multipliers for each manager (0.0-2.0)
        default_managers: Default managers by topic {"auth": ["PM", "CTO", "CSO"]}
        preferences: Meeting preferences (language, formality, detail_level)

    Returns:
        Configuration status
    """
    config = load_meeting_config(project_path)

    # Update weights
    if manager_weights:
        for mgr, weight in manager_weights.items():
            if mgr in config["manager_weights"]:
                # Clamp to 0.0-2.0
                config["manager_weights"][mgr] = max(0.0, min(2.0, weight))

    # Update default managers by topic
    if default_managers:
        config["default_managers_by_topic"].update(default_managers)

    # Update preferences
    if preferences:
        config["preferences"].update(preferences)

    # Save config
    if save_meeting_config(project_path, config):
        # Build output
        lines = [
            "## Meeting Configuration Saved",
            "",
            "### Manager Weights",
        ]

        for mgr, weight in config["manager_weights"].items():
            bar = "█" * int(weight * 5) + "░" * (10 - int(weight * 5))
            lines.append(f"- {mgr}: {bar} ({weight:.1f})")

        if config["default_managers_by_topic"]:
            lines.append("")
            lines.append("### Default Managers by Topic")
            for topic, managers in config["default_managers_by_topic"].items():
                lines.append(f"- {topic}: {', '.join(managers)}")

        lines.append("")
        lines.append("### Preferences")
        for key, value in config["preferences"].items():
            lines.append(f"- {key}: {value}")

        return [TextContent(type="text", text="\n".join(lines))]
    else:
        return [TextContent(type="text", text="Failed to save configuration")]


async def add_persona_override(
    project_path: str,
    manager: str,
    overrides: Dict[str, Any],
) -> List[TextContent]:
    """
    Add custom persona overrides for a manager.

    Args:
        project_path: Project root path
        manager: Manager key (PM, CTO, etc.)
        overrides: Override dict (pet_phrases, probing_questions, etc.)

    Returns:
        Status message

    Example:
        add_persona_override("D:/myproject", "CTO", {
            "pet_phrases": ["기술 부채 조심하세요", "성능 먼저 측정하세요"],
            "focus_areas": ["scalability", "maintainability"]
        })
    """
    config = load_meeting_config(project_path)

    valid_managers = ["PM", "CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]
    if manager not in valid_managers:
        return [TextContent(
            type="text",
            text=f"Invalid manager: {manager}. Valid: {', '.join(valid_managers)}"
        )]

    # Merge with existing overrides
    if manager not in config["persona_overrides"]:
        config["persona_overrides"][manager] = {}

    config["persona_overrides"][manager].update(overrides)

    if save_meeting_config(project_path, config):
        lines = [
            f"## Persona Override Saved: {manager}",
            "",
            "### Overrides:",
        ]

        for key, value in overrides.items():
            if isinstance(value, list):
                lines.append(f"- {key}:")
                for item in value[:3]:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- {key}: {value}")

        return [TextContent(type="text", text="\n".join(lines))]
    else:
        return [TextContent(type="text", text="Failed to save override")]


async def add_custom_prompt(
    project_path: str,
    topic: str,
    prompt_template: str,
) -> List[TextContent]:
    """
    Add custom prompt template for a topic.

    Args:
        project_path: Project root path
        topic: Topic key
        prompt_template: Custom prompt template with {context}, {managers} placeholders

    Returns:
        Status message
    """
    config = load_meeting_config(project_path)
    config["custom_prompts"][topic] = prompt_template

    if save_meeting_config(project_path, config):
        return [TextContent(
            type="text",
            text=f"## Custom Prompt Saved\n\n**Topic**: {topic}\n**Length**: {len(prompt_template)} chars"
        )]
    else:
        return [TextContent(type="text", text="Failed to save custom prompt")]


async def get_meeting_config(project_path: str) -> List[TextContent]:
    """
    Get current meeting configuration.

    Args:
        project_path: Project root path

    Returns:
        Current configuration
    """
    config = load_meeting_config(project_path)
    config_path = _get_config_path(project_path)

    lines = [
        "## Meeting Configuration",
        "",
        f"**Config File**: {config_path}",
        f"**Exists**: {config_path.exists()}",
        "",
        "### Manager Weights",
    ]

    for mgr, weight in config["manager_weights"].items():
        bar = "█" * int(weight * 5) + "░" * (10 - int(weight * 5))
        lines.append(f"- {mgr}: {bar} ({weight:.1f})")

    if config.get("persona_overrides"):
        lines.append("")
        lines.append("### Persona Overrides")
        for mgr, overrides in config["persona_overrides"].items():
            lines.append(f"- {mgr}: {len(overrides)} overrides")

    if config.get("default_managers_by_topic"):
        lines.append("")
        lines.append("### Default Managers by Topic")
        for topic, managers in config["default_managers_by_topic"].items():
            lines.append(f"- {topic}: {', '.join(managers)}")

    if config.get("custom_prompts"):
        lines.append("")
        lines.append("### Custom Prompts")
        for topic, prompt in config["custom_prompts"].items():
            lines.append(f"- {topic}: {len(prompt)} chars")

    lines.append("")
    lines.append("### Preferences")
    for key, value in config.get("preferences", {}).items():
        lines.append(f"- {key}: {value}")

    return [TextContent(type="text", text="\n".join(lines))]


async def reset_meeting_config(project_path: str) -> List[TextContent]:
    """
    Reset meeting configuration to defaults.

    Args:
        project_path: Project root path

    Returns:
        Status message
    """
    if save_meeting_config(project_path, DEFAULT_MEETING_CONFIG.copy()):
        return [TextContent(
            type="text",
            text="## Configuration Reset\n\nAll meeting settings restored to defaults."
        )]
    else:
        return [TextContent(type="text", text="Failed to reset configuration")]


def apply_personalization(
    project_path: str,
    managers: List[str],
    topic: str,
) -> Dict[str, Any]:
    """
    Apply project personalization to meeting settings.

    Args:
        project_path: Project root path
        managers: Default manager list
        topic: Meeting topic

    Returns:
        Personalized settings dict
    """
    config = load_meeting_config(project_path)

    result = {
        "managers": managers.copy(),
        "persona_overrides": {},
        "preferences": config.get("preferences", {}),
        "custom_prompt": None,
    }

    # Apply default managers by topic
    topic_defaults = config.get("default_managers_by_topic", {})
    if topic in topic_defaults:
        result["managers"] = topic_defaults[topic]

    # Apply manager weights to sort order
    weights = config.get("manager_weights", {})
    if weights:
        # Score each manager
        scored = [(mgr, weights.get(mgr, 1.0)) for mgr in result["managers"]]
        # Sort by weight (descending), keeping PM first
        pm_weight = weights.get("PM", 1.0)
        sorted_managers = sorted(scored, key=lambda x: (-1000 if x[0] == "PM" else 0) - x[1])
        result["managers"] = [mgr for mgr, _ in sorted_managers[:5]]

    # Apply persona overrides
    result["persona_overrides"] = config.get("persona_overrides", {})

    # Apply custom prompt if exists
    if topic in config.get("custom_prompts", {}):
        result["custom_prompt"] = config["custom_prompts"][topic]

    return result
