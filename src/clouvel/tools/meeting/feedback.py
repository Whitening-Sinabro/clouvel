# -*- coding: utf-8 -*-
"""Meeting Feedback System

Collects and stores meeting quality feedback for continuous improvement.
- Save meeting outputs with metadata
- Collect user ratings (1-5)
- Track prompt versions for A/B testing

Phase 2: Feedback loop for meeting quality improvement
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, asdict

from mcp.types import TextContent


@dataclass
class MeetingRecord:
    """Single meeting record with metadata."""
    id: str
    timestamp: str
    context: str
    topic: str
    managers: List[str]
    prompt_version: str
    prompt_length: int
    output: Optional[str] = None
    output_length: Optional[int] = None
    rating: Optional[int] = None  # 1-5
    feedback: Optional[str] = None
    tags: Optional[List[str]] = None


def _get_feedback_dir(project_path: str) -> Path:
    """Get feedback storage directory."""
    path = Path(project_path) / ".clouvel" / "meetings"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_history_file(project_path: str) -> Path:
    """Get history JSONL file path."""
    return _get_feedback_dir(project_path) / "history.jsonl"


def _generate_meeting_id() -> str:
    """Generate unique meeting ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


async def save_meeting(
    project_path: str,
    context: str,
    topic: str,
    managers: List[str],
    prompt: str,
    output: Optional[str] = None,
    prompt_version: str = "v1.0.0",
) -> List[TextContent]:
    """
    Save meeting record for later feedback.

    Args:
        project_path: Project root path
        context: Meeting context/topic
        topic: Detected topic
        managers: List of participating managers
        prompt: Generated prompt
        output: Meeting output (if available)
        prompt_version: Prompt version for A/B testing

    Returns:
        Meeting ID for rating submission
    """
    meeting_id = _generate_meeting_id()

    record = MeetingRecord(
        id=meeting_id,
        timestamp=datetime.now().isoformat(),
        context=context[:500],  # Truncate for storage
        topic=topic,
        managers=managers,
        prompt_version=prompt_version,
        prompt_length=len(prompt),
        output=output[:2000] if output else None,  # Truncate output
        output_length=len(output) if output else None,
    )

    # Append to history file
    history_file = _get_history_file(project_path)
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    return [TextContent(
        type="text",
        text=f"""## Meeting Saved

**ID**: {meeting_id}
**Topic**: {topic}
**Managers**: {', '.join(managers)}

회의 후 평가를 남겨주세요:
```
rate_meeting("{meeting_id}", rating=4, feedback="구체적이고 유용했음")
```
"""
    )]


async def rate_meeting(
    project_path: str,
    meeting_id: str,
    rating: int,
    feedback: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[TextContent]:
    """
    Rate a meeting for quality feedback.

    Args:
        project_path: Project root path
        meeting_id: Meeting ID from save_meeting
        rating: Quality rating (1-5)
            1: 전혀 도움 안 됨
            2: 별로임
            3: 보통
            4: 유용함
            5: 매우 유용함
        feedback: Optional text feedback
        tags: Optional tags (e.g., ["natural", "actionable", "specific"])

    Returns:
        Confirmation message
    """
    if not 1 <= rating <= 5:
        return [TextContent(type="text", text="Rating must be 1-5")]

    history_file = _get_history_file(project_path)

    if not history_file.exists():
        return [TextContent(type="text", text="No meeting history found")]

    # Read all records
    records = []
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Find and update the meeting
    found = False
    for record in records:
        if record.get("id") == meeting_id:
            record["rating"] = rating
            record["feedback"] = feedback
            record["tags"] = tags or []
            found = True
            break

    if not found:
        return [TextContent(type="text", text=f"Meeting {meeting_id} not found")]

    # Write back all records
    with open(history_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Check if high quality (candidate for EXAMPLES)
    quality_msg = ""
    if rating >= 4:
        quality_msg = "\n\n**Note**: High-quality meeting! Consider adding to EXAMPLES for training."

    return [TextContent(
        type="text",
        text=f"""## Rating Saved

**Meeting**: {meeting_id}
**Rating**: {"⭐" * rating} ({rating}/5)
**Feedback**: {feedback or "(none)"}
**Tags**: {', '.join(tags) if tags else "(none)"}
{quality_msg}
"""
    )]


async def get_meeting_stats(
    project_path: str,
    days: int = 30,
) -> List[TextContent]:
    """
    Get meeting quality statistics.

    Args:
        project_path: Project root path
        days: Number of days to analyze

    Returns:
        Statistics summary
    """
    history_file = _get_history_file(project_path)

    if not history_file.exists():
        return [TextContent(type="text", text="No meeting history found")]

    # Read all records
    records = []
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    if not records:
        return [TextContent(type="text", text="No meetings recorded yet")]

    # Calculate stats
    total = len(records)
    rated = [r for r in records if r.get("rating") is not None]
    rated_count = len(rated)

    if rated_count == 0:
        avg_rating = 0
    else:
        avg_rating = sum(r["rating"] for r in rated) / rated_count

    # Topic distribution
    topics = {}
    for r in records:
        topic = r.get("topic", "unknown")
        topics[topic] = topics.get(topic, 0) + 1

    # Version distribution (for A/B testing)
    versions = {}
    version_ratings = {}
    for r in records:
        ver = r.get("prompt_version", "unknown")
        versions[ver] = versions.get(ver, 0) + 1
        if r.get("rating"):
            if ver not in version_ratings:
                version_ratings[ver] = []
            version_ratings[ver].append(r["rating"])

    # High quality candidates
    high_quality = [r for r in records if r.get("rating", 0) >= 4]

    # Build output
    lines = [
        "## Meeting Statistics",
        "",
        f"**Total Meetings**: {total}",
        f"**Rated**: {rated_count} ({rated_count/total*100:.0f}%)" if total > 0 else "",
        f"**Average Rating**: {'⭐' * round(avg_rating)} ({avg_rating:.1f}/5)" if avg_rating > 0 else "**Average Rating**: (no ratings yet)",
        "",
        "### Topic Distribution",
    ]

    for topic, count in sorted(topics.items(), key=lambda x: -x[1]):
        lines.append(f"- {topic}: {count}")

    if version_ratings:
        lines.append("")
        lines.append("### Prompt Version Performance (A/B)")
        for ver, ratings in version_ratings.items():
            avg = sum(ratings) / len(ratings)
            lines.append(f"- {ver}: {avg:.1f}/5 (n={len(ratings)})")

    if high_quality:
        lines.append("")
        lines.append(f"### High Quality Candidates: {len(high_quality)}")
        lines.append("Run `export_training_data` to extract for EXAMPLES")

    return [TextContent(type="text", text="\n".join(lines))]


async def export_training_data(
    project_path: str,
    min_rating: int = 4,
) -> List[TextContent]:
    """
    Export high-quality meetings for training data.

    Args:
        project_path: Project root path
        min_rating: Minimum rating to include

    Returns:
        Exported data summary
    """
    history_file = _get_history_file(project_path)

    if not history_file.exists():
        return [TextContent(type="text", text="No meeting history found")]

    # Read all records
    records = []
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Filter high quality
    high_quality = [r for r in records if r.get("rating", 0) >= min_rating]

    if not high_quality:
        return [TextContent(
            type="text",
            text=f"No meetings with rating >= {min_rating} found"
        )]

    # Export to training file
    training_dir = _get_feedback_dir(project_path) / "training"
    training_dir.mkdir(exist_ok=True)

    export_file = training_dir / f"export_{datetime.now().strftime('%Y%m%d')}.json"

    training_data = []
    for r in high_quality:
        if r.get("output"):
            training_data.append({
                "context": r["context"],
                "topic": r["topic"],
                "output": r["output"],
                "rating": r["rating"],
                "feedback": r.get("feedback"),
            })

    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    # Generate EXAMPLES format suggestion
    suggestions = []
    for i, data in enumerate(training_data[:3]):
        suggestions.append(f"""
### Candidate {i+1} (Rating: {data['rating']})
**Context**: {data['context'][:100]}...
**Topic**: {data['topic']}

Add to `examples.py`:
```python
"{data['topic']}": [
    {{
        "context": "{data['context'][:100]}...",
        "output": \"\"\"...{data['output'][:200]}...\"\"\"
    }}
]
```
""")

    return [TextContent(
        type="text",
        text=f"""## Training Data Exported

**File**: {export_file}
**Count**: {len(training_data)} high-quality meetings

---

## EXAMPLES Candidates

{chr(10).join(suggestions)}

---

Review and manually add the best ones to `prompts/examples.py`
"""
    )]
