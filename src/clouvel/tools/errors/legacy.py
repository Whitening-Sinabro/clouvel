# -*- coding: utf-8 -*-
"""Legacy error tools: log_error, analyze_error, watch_logs, check_logs,
add_prevention_rule, get_error_summary"""

import re
import json
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

from ._shared import (
    require_license,
    require_license_premium,
    ERROR_PATTERNS,
    _get_error_log_path,
    _classify_error,
    _extract_stack_info,
)


@require_license_premium
async def log_error(
    path: str,
    error_text: str,
    context: str = "",
    source: str = "terminal"
) -> list[TextContent]:
    """Log and classify error."""
    log_path = _get_error_log_path(path)
    log_path.mkdir(parents=True, exist_ok=True)

    # Classify error
    classification = _classify_error(error_text)
    stack_info = _extract_stack_info(error_text)

    # Record error
    timestamp = datetime.now().isoformat()
    error_entry = {
        "timestamp": timestamp,
        "source": source,
        "context": context,
        "error_text": error_text[:2000],  # Truncate if too long
        "classification": classification,
        "stack_info": stack_info
    }

    # Append to log file
    log_file = log_path / "error_log.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")

    # Update pattern count
    pattern_file = log_path / "patterns.json"
    patterns = {}
    if pattern_file.exists():
        patterns = json.loads(pattern_file.read_text(encoding="utf-8"))

    error_type = classification["type"]
    if error_type not in patterns:
        patterns[error_type] = {"count": 0, "last_seen": None, "examples": []}

    patterns[error_type]["count"] += 1
    patterns[error_type]["last_seen"] = timestamp
    if len(patterns[error_type]["examples"]) < 3:
        patterns[error_type]["examples"].append(error_text[:200])

    pattern_file.write_text(json.dumps(patterns, ensure_ascii=False, indent=2), encoding="utf-8")

    return [TextContent(type="text", text=f"""
# Error Recorded

## Classification
- **Type**: {classification['category']}
- **Source**: {source}
- **Time**: {timestamp}

## Location
- File: {stack_info['file'] or 'Unknown'}
- Line: {stack_info['line'] or 'Unknown'}
- Function: {stack_info['function'] or 'Unknown'}

## Prevention
{classification['prevention']}

## Next Steps
1. Use `analyze_error` tool for detailed analysis
2. Use `add_prevention_rule` tool to add prevention rules
""")]


@require_license_premium
async def analyze_error(
    path: str,
    error_text: str = "",
    include_history: bool = True
) -> list[TextContent]:
    """Detailed error analysis."""
    log_path = _get_error_log_path(path)

    result = "# Error Analysis\n\n"

    # Analyze input error
    if error_text:
        classification = _classify_error(error_text)
        stack_info = _extract_stack_info(error_text)

        result += f"""## Current Error

### Classification
- **Type**: {classification['category']}
- **Code**: {classification['type']}

### Location
- File: {stack_info['file'] or 'Unknown'}
- Line: {stack_info['line'] or 'Unknown'}
- Function: {stack_info['function'] or 'Unknown'}

### Recommended Actions
{classification['prevention']}

### Error Message
```
{error_text[:500]}
```

"""

    # History analysis
    if include_history:
        pattern_file = log_path / "patterns.json"
        if pattern_file.exists():
            patterns = json.loads(pattern_file.read_text(encoding="utf-8"))

            if patterns:
                result += "## Error History\n\n"
                result += "| Type | Count | Last Seen |\n"
                result += "|------|-------|----------|\n"

                sorted_patterns = sorted(
                    patterns.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )

                for error_type, data in sorted_patterns[:10]:
                    category = ERROR_PATTERNS.get(error_type, {}).get("category", error_type)
                    last_seen = data["last_seen"][:10] if data["last_seen"] else "-"
                    result += f"| {category} | {data['count']} | {last_seen} |\n"

                # Most frequent error type
                if sorted_patterns:
                    top_error = sorted_patterns[0]
                    top_type = top_error[0]
                    top_count = top_error[1]["count"]

                    prevention = ERROR_PATTERNS.get(top_type, {}).get("prevention", "Analysis required")

                    result += f"""
### Most Frequent Error
- **Type**: {ERROR_PATTERNS.get(top_type, {}).get('category', top_type)}
- **Count**: {top_count} times
- **Recommended Actions**: {prevention}
"""
        else:
            result += "## Error History\n\nNo errors recorded yet.\n"

    if not error_text and not include_history:
        result += "No errors to analyze. Provide error_text or set include_history=true.\n"

    return [TextContent(type="text", text=result)]


@require_license
async def watch_logs(
    path: str,
    log_paths: list[str] = None,
    patterns: list[str] = None
) -> list[TextContent]:
    """Configure log file monitoring."""
    config_path = _get_error_log_path(path)
    config_path.mkdir(parents=True, exist_ok=True)

    # Default log paths
    default_paths = [
        "logs/*.log",
        "*.log",
        "npm-debug.log",
        "yarn-error.log",
        ".next/server/pages-errors.log"
    ]

    # Default error patterns
    default_patterns = [
        r"Error:",
        r"ERROR",
        r"Exception:",
        r"FATAL",
        r"Failed",
        r"Traceback"
    ]

    watch_config = {
        "log_paths": log_paths or default_paths,
        "error_patterns": patterns or default_patterns,
        "enabled": True,
        "last_check": None
    }

    config_file = config_path / "watch_config.json"
    config_file.write_text(json.dumps(watch_config, ensure_ascii=False, indent=2), encoding="utf-8")

    return [TextContent(type="text", text=f"""
# Log Monitoring Configured

## Watch Targets
```
{chr(10).join(watch_config['log_paths'])}
```

## Error Patterns
```
{chr(10).join(watch_config['error_patterns'])}
```

## Usage
When errors are found in log files:
1. Record with `log_error` tool
2. Analyze with `analyze_error` tool
3. Add prevention rules with `add_prevention_rule` tool

## Tips
- Add custom log paths: use log_paths parameter
- Add custom patterns: use patterns parameter
""")]


@require_license
async def check_logs(path: str) -> list[TextContent]:
    """Scan log files (manual check)."""
    config_path = _get_error_log_path(path)
    config_file = config_path / "watch_config.json"

    if not config_file.exists():
        return [TextContent(type="text", text="Log monitoring not configured. Run `watch_logs` tool first.")]

    config = json.loads(config_file.read_text(encoding="utf-8"))
    project_path = Path(path)

    found_errors = []

    for log_pattern in config["log_paths"]:
        for log_file in project_path.glob(log_pattern):
            if not log_file.is_file():
                continue

            try:
                content = log_file.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")

                for i, line in enumerate(lines[-100:]):  # Last 100 lines only
                    for pattern in config["error_patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            found_errors.append({
                                "file": str(log_file),
                                "line_num": len(lines) - 100 + i + 1,
                                "content": line[:200]
                            })
                            break
            except Exception:
                continue

    if not found_errors:
        return [TextContent(type="text", text="# Log Check Complete\n\nNo errors found.")]

    result = f"# Log Check Results\n\n{len(found_errors)} errors found\n\n"

    for i, error in enumerate(found_errors[:20], 1):
        result += f"## {i}. {error['file']}:{error['line_num']}\n"
        result += f"```\n{error['content']}\n```\n\n"

    if len(found_errors) > 20:
        result += f"\n... and {len(found_errors) - 20} more\n"

    result += "\n## Next Steps\nRecord important errors with `log_error` tool.\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def add_prevention_rule(
    path: str,
    error_type: str,
    rule: str,
    scope: str = "project"
) -> list[TextContent]:
    """Add error prevention rule."""
    log_path = _get_error_log_path(path)
    log_path.mkdir(parents=True, exist_ok=True)

    rules_file = log_path / "prevention_rules.json"
    rules = {}
    if rules_file.exists():
        rules = json.loads(rules_file.read_text(encoding="utf-8"))

    if error_type not in rules:
        rules[error_type] = {
            "rules": [],
            "scope": scope,
            "added": datetime.now().isoformat()
        }

    if rule not in rules[error_type]["rules"]:
        rules[error_type]["rules"].append(rule)

    rules_file.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")

    # Suggest adding rule to CLAUDE.md
    claude_md_path = Path(path) / "CLAUDE.md"
    suggestion = ""

    if claude_md_path.exists():
        suggestion = f"""
## CLAUDE.md Update Suggestion

Add the following to CLAUDE.md:

```markdown
## Error Prevention Rules

### {ERROR_PATTERNS.get(error_type, {}).get('category', error_type)}
- {rule}
```
"""

    return [TextContent(type="text", text=f"""
# Prevention Rule Added

## Rule
- **Error Type**: {error_type}
- **Rule**: {rule}
- **Scope**: {scope}

## Currently Registered Rules
{json.dumps(rules, ensure_ascii=False, indent=2)}
{suggestion}
""")]


@require_license_premium
async def get_error_summary(path: str, days: int = 30) -> list[TextContent]:
    """Error summary report."""
    log_path = _get_error_log_path(path)

    if not log_path.exists():
        return [TextContent(type="text", text="No error records found.")]

    result = f"# Error Summary (Last {days} Days)\n\n"

    # Pattern statistics
    pattern_file = log_path / "patterns.json"
    if pattern_file.exists():
        patterns = json.loads(pattern_file.read_text(encoding="utf-8"))

        total_errors = sum(p["count"] for p in patterns.values())
        result += f"**Total Errors**: {total_errors}\n\n"

        if patterns:
            result += "## Error Statistics by Type\n\n"
            result += "| Type | Count | Ratio |\n"
            result += "|------|-------|-------|\n"

            sorted_patterns = sorted(
                patterns.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )

            for error_type, data in sorted_patterns:
                category = ERROR_PATTERNS.get(error_type, {}).get("category", error_type)
                ratio = (data["count"] / total_errors * 100) if total_errors > 0 else 0
                result += f"| {category} | {data['count']} | {ratio:.1f}% |\n"

    # Prevention rules
    rules_file = log_path / "prevention_rules.json"
    if rules_file.exists():
        rules = json.loads(rules_file.read_text(encoding="utf-8"))

        if rules:
            result += "\n## Registered Prevention Rules\n\n"
            for error_type, data in rules.items():
                category = ERROR_PATTERNS.get(error_type, {}).get("category", error_type)
                result += f"### {category}\n"
                for rule in data["rules"]:
                    result += f"- {rule}\n"
                result += "\n"

    return [TextContent(type="text", text=result)]
