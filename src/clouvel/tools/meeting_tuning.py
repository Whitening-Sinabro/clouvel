# -*- coding: utf-8 -*-
"""Meeting Prompt Tuning System

A/B testing and prompt variant management for continuous improvement.
- Manage prompt versions
- Track variant performance
- Auto-select best performing variant

Phase 2: Automated prompt improvement
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

from mcp.types import TextContent


# Prompt Variants for A/B Testing
PROMPT_VARIANTS = {
    "v1.0.0": {
        "name": "baseline",
        "description": "Original prompt with full personas and examples",
        "config": {
            "include_example": True,
            "include_probing_questions": True,
            "persona_detail": "full",  # full, summary, minimal
            "example_count": 1,
        }
    },
    "v1.1.0": {
        "name": "concise",
        "description": "Shorter prompt with summarized personas",
        "config": {
            "include_example": True,
            "include_probing_questions": False,
            "persona_detail": "summary",
            "example_count": 1,
        }
    },
    "v1.2.0": {
        "name": "rich_examples",
        "description": "Two examples for better few-shot learning",
        "config": {
            "include_example": True,
            "include_probing_questions": True,
            "persona_detail": "full",
            "example_count": 2,
        }
    },
    "v1.3.0": {
        "name": "minimal",
        "description": "Minimal prompt for faster response",
        "config": {
            "include_example": False,
            "include_probing_questions": False,
            "persona_detail": "minimal",
            "example_count": 0,
        }
    },
}

# Default active variant
ACTIVE_VARIANT = "v1.0.0"


@dataclass
class VariantStats:
    """Statistics for a prompt variant."""
    version: str
    name: str
    total_uses: int
    rated_count: int
    total_rating: int
    avg_rating: float
    tags: Dict[str, int]  # tag -> count


def _get_tuning_dir(project_path: str) -> Path:
    """Get tuning data directory."""
    path = Path(project_path) / ".clouvel" / "meetings" / "tuning"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_config_file(project_path: str) -> Path:
    """Get tuning config file."""
    return _get_tuning_dir(project_path) / "config.json"


def get_active_variant(project_path: Optional[str] = None) -> str:
    """Get currently active prompt variant."""
    if project_path:
        config_file = _get_config_file(project_path)
        if config_file.exists():
            config = json.loads(config_file.read_text(encoding="utf-8"))
            return config.get("active_variant", ACTIVE_VARIANT)
    return ACTIVE_VARIANT


def get_variant_config(version: str) -> Dict[str, Any]:
    """Get configuration for a specific variant."""
    variant = PROMPT_VARIANTS.get(version, PROMPT_VARIANTS[ACTIVE_VARIANT])
    return variant["config"]


def select_variant_for_ab_test(project_path: Optional[str] = None) -> str:
    """
    Select a variant for A/B testing.

    Uses weighted random selection based on performance.
    New variants get more exposure, proven variants get more weight.
    """
    if project_path:
        config_file = _get_config_file(project_path)
        if config_file.exists():
            config = json.loads(config_file.read_text(encoding="utf-8"))

            # Check if A/B testing is enabled
            if not config.get("ab_testing_enabled", False):
                return config.get("active_variant", ACTIVE_VARIANT)

            # Use weights from config
            weights = config.get("variant_weights", {})
            if weights:
                versions = list(weights.keys())
                probs = list(weights.values())
                return random.choices(versions, weights=probs)[0]

    # Default: uniform distribution
    return random.choice(list(PROMPT_VARIANTS.keys()))


async def enable_ab_testing(
    project_path: str,
    variants: Optional[List[str]] = None,
) -> List[TextContent]:
    """
    Enable A/B testing for prompt variants.

    Args:
        project_path: Project root path
        variants: List of variants to test (default: all)

    Returns:
        Confirmation message
    """
    config_file = _get_config_file(project_path)

    # Load or create config
    if config_file.exists():
        config = json.loads(config_file.read_text(encoding="utf-8"))
    else:
        config = {}

    # Set up A/B testing
    test_variants = variants or list(PROMPT_VARIANTS.keys())

    # Validate variants
    invalid = [v for v in test_variants if v not in PROMPT_VARIANTS]
    if invalid:
        return [TextContent(
            type="text",
            text=f"Invalid variants: {invalid}\nAvailable: {list(PROMPT_VARIANTS.keys())}"
        )]

    # Initial uniform weights
    weights = {v: 1.0 / len(test_variants) for v in test_variants}

    config["ab_testing_enabled"] = True
    config["test_variants"] = test_variants
    config["variant_weights"] = weights
    config["updated_at"] = datetime.now().isoformat()

    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Build output
    lines = [
        "## A/B Testing Enabled",
        "",
        "**Variants**:",
    ]

    for v in test_variants:
        info = PROMPT_VARIANTS[v]
        lines.append(f"- {v} ({info['name']}): {info['description']}")

    lines.extend([
        "",
        "**Initial Weights**: Equal distribution",
        "",
        "Weights will auto-adjust based on ratings.",
        "Run `get_variant_performance` to see results.",
    ])

    return [TextContent(type="text", text="\n".join(lines))]


async def disable_ab_testing(
    project_path: str,
    set_winner: Optional[str] = None,
) -> List[TextContent]:
    """
    Disable A/B testing and optionally set winner.

    Args:
        project_path: Project root path
        set_winner: Variant to set as active (optional)

    Returns:
        Confirmation message
    """
    config_file = _get_config_file(project_path)

    if not config_file.exists():
        return [TextContent(type="text", text="A/B testing not configured")]

    config = json.loads(config_file.read_text(encoding="utf-8"))
    config["ab_testing_enabled"] = False

    if set_winner:
        if set_winner not in PROMPT_VARIANTS:
            return [TextContent(
                type="text",
                text=f"Invalid variant: {set_winner}"
            )]
        config["active_variant"] = set_winner

    config["updated_at"] = datetime.now().isoformat()
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

    winner_msg = f"\n**Active Variant**: {set_winner}" if set_winner else ""

    return [TextContent(
        type="text",
        text=f"## A/B Testing Disabled{winner_msg}"
    )]


async def get_variant_performance(
    project_path: str,
) -> List[TextContent]:
    """
    Get performance metrics for all variants.

    Args:
        project_path: Project root path

    Returns:
        Performance comparison
    """
    history_file = Path(project_path) / ".clouvel" / "meetings" / "history.jsonl"

    if not history_file.exists():
        return [TextContent(type="text", text="No meeting history found")]

    # Read all records
    records = []
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Aggregate by variant
    variant_stats: Dict[str, VariantStats] = {}

    for r in records:
        version = r.get("prompt_version", "v1.0.0")

        if version not in variant_stats:
            variant_info = PROMPT_VARIANTS.get(version, {"name": "unknown"})
            variant_stats[version] = VariantStats(
                version=version,
                name=variant_info.get("name", "unknown"),
                total_uses=0,
                rated_count=0,
                total_rating=0,
                avg_rating=0.0,
                tags={},
            )

        stats = variant_stats[version]
        stats.total_uses += 1

        if r.get("rating"):
            stats.rated_count += 1
            stats.total_rating += r["rating"]
            stats.avg_rating = stats.total_rating / stats.rated_count

        for tag in r.get("tags", []):
            stats.tags[tag] = stats.tags.get(tag, 0) + 1

    if not variant_stats:
        return [TextContent(type="text", text="No variant data yet")]

    # Build output
    lines = [
        "## Variant Performance",
        "",
        "| Version | Name | Uses | Rated | Avg Rating |",
        "|---------|------|------|-------|------------|",
    ]

    # Sort by average rating (descending)
    sorted_stats = sorted(
        variant_stats.values(),
        key=lambda x: (x.avg_rating, x.rated_count),
        reverse=True
    )

    for stats in sorted_stats:
        stars = "⭐" * round(stats.avg_rating) if stats.avg_rating > 0 else "-"
        lines.append(
            f"| {stats.version} | {stats.name} | {stats.total_uses} | "
            f"{stats.rated_count} | {stars} ({stats.avg_rating:.1f}) |"
        )

    # Winner recommendation
    if sorted_stats and sorted_stats[0].rated_count >= 5:
        winner = sorted_stats[0]
        lines.extend([
            "",
            f"**Recommended Winner**: {winner.version} ({winner.name})",
            f"  - Avg Rating: {winner.avg_rating:.1f}/5",
            f"  - Sample Size: {winner.rated_count}",
            "",
            f"To set as default: `disable_ab_testing(\"{winner.version}\")`"
        ])
    else:
        lines.extend([
            "",
            "**Status**: Need more data (min 5 ratings per variant)",
        ])

    return [TextContent(type="text", text="\n".join(lines))]


async def list_variants() -> List[TextContent]:
    """
    List all available prompt variants.

    Returns:
        Variant list with descriptions
    """
    lines = [
        "## Available Prompt Variants",
        "",
    ]

    for version, info in PROMPT_VARIANTS.items():
        config = info["config"]
        lines.append(f"### {version} - {info['name']}")
        lines.append(f"_{info['description']}_")
        lines.append("")
        lines.append("Config:")
        lines.append(f"- Examples: {config['example_count']}")
        lines.append(f"- Probing Questions: {config['include_probing_questions']}")
        lines.append(f"- Persona Detail: {config['persona_detail']}")
        lines.append("")

    return [TextContent(type="text", text="\n".join(lines))]


def update_variant_weights(project_path: str) -> None:
    """
    Auto-update variant weights based on performance.

    Called internally after each rating.
    Uses Thompson Sampling-like approach:
    - Higher rated variants get more weight
    - New variants get exploration bonus
    """
    config_file = _get_config_file(project_path)

    if not config_file.exists():
        return

    config = json.loads(config_file.read_text(encoding="utf-8"))

    if not config.get("ab_testing_enabled"):
        return

    history_file = Path(project_path) / ".clouvel" / "meetings" / "history.jsonl"

    if not history_file.exists():
        return

    # Read rated records
    records = []
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r.get("rating"):
                    records.append(r)

    if len(records) < 10:  # Need minimum data
        return

    # Calculate scores
    test_variants = config.get("test_variants", [])
    scores = {}

    for version in test_variants:
        variant_records = [r for r in records if r.get("prompt_version") == version]

        if not variant_records:
            # Exploration bonus for untested variants
            scores[version] = 3.5
        else:
            # Average rating + exploration bonus for low sample size
            avg = sum(r["rating"] for r in variant_records) / len(variant_records)
            exploration = 0.5 / (1 + len(variant_records) / 10)
            scores[version] = avg + exploration

    # Convert to weights (softmax-like)
    total = sum(scores.values())
    weights = {v: s / total for v, s in scores.items()}

    config["variant_weights"] = weights
    config["weights_updated_at"] = datetime.now().isoformat()

    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
