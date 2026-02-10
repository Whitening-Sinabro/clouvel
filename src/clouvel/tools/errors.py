# -*- coding: utf-8 -*-
"""Error learning tools: log_error, analyze_error, watch_logs, add_prevention_rule

v2.0: SQLite + ChromaDB vector search integration
"""

import re
import json
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

# License module import (use Free stub if Pro version unavailable)
try:
    from ..license import require_license, require_license_premium
except ImportError:
    from ..license_free import require_license, require_license_premium

# New DB module import (v2.0)
try:
    from ..db import (
        init_db,
        record_error as db_record_error,
        get_error as db_get_error,
        list_errors as db_list_errors,
        resolve_error as db_resolve_error,
        get_error_stats as db_get_error_stats,
        add_rule as db_add_rule,
        get_rules as db_get_rules,
        search_similar_errors as db_search_similar,
        is_vector_search_available,
        add_error_embedding,
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Regression Memory import (v4.0)
try:
    from ..db.regression import (
        normalize_error_signature,
        create_memory,
        match_all_levels,
        increment_hit_count,
        get_memory_stats as db_get_memory_stats,
        # v4.0 Phase 2
        list_memories as db_list_memories_reg,
        search_memories as db_search_memories,
        archive_memory as db_archive_memory,
        unarchive_memory as db_unarchive_memory,
        mark_stale_memories as db_mark_stale_memories,
        get_memory_report as db_get_memory_report,
        # v5.0: Cross-Project Memory Transfer
        get_memory as db_get_memory,
        get_memory_for_promote as db_get_memory_for_promote,
    )
    REGRESSION_AVAILABLE = True
except ImportError:
    REGRESSION_AVAILABLE = False

# Global Memory import (v5.0)
try:
    from ..db.knowledge import (
        promote_memory as kb_promote_memory,
        search_global_memories as kb_search_global_memories,
        get_or_create_project as kb_get_or_create_project,
        increment_global_hit as kb_increment_global_hit,
        get_project_domain as kb_get_project_domain,
        set_project_domain as kb_set_project_domain,
    )
    GLOBAL_MEMORY_AVAILABLE = True
except ImportError:
    GLOBAL_MEMORY_AVAILABLE = False

# Error pattern definitions
ERROR_PATTERNS = {
    "type_error": {
        "patterns": [r"TypeError:", r"type\s+error", r"is not a function", r"undefined is not"],
        "category": "Type Error",
        "prevention": "Strengthen type checking, enable TypeScript strict mode"
    },
    "null_error": {
        "patterns": [r"null|undefined", r"Cannot read propert", r"is null", r"is undefined"],
        "category": "Null Reference",
        "prevention": "Use optional chaining, add null checks"
    },
    "import_error": {
        "patterns": [r"Cannot find module", r"Module not found", r"ImportError", r"ModuleNotFoundError"],
        "category": "Import Error",
        "prevention": "Verify dependencies, validate paths"
    },
    "syntax_error": {
        "patterns": [r"SyntaxError", r"Unexpected token", r"Parse error"],
        "category": "Syntax Error",
        "prevention": "Enable linter, format on save"
    },
    "network_error": {
        "patterns": [r"ECONNREFUSED", r"fetch failed", r"NetworkError", r"timeout", r"ETIMEDOUT"],
        "category": "Network Error",
        "prevention": "Implement retry logic, configure timeouts"
    },
    "permission_error": {
        "patterns": [r"EACCES", r"Permission denied", r"PermissionError", r"403"],
        "category": "Permission Error",
        "prevention": "Check permissions, proper error handling"
    },
    "database_error": {
        "patterns": [r"SQLITE", r"PostgreSQL", r"MySQL", r"duplicate key", r"constraint violation"],
        "category": "Database Error",
        "prevention": "Use transactions, validate constraints"
    },
}


def _get_error_log_path(project_path: str) -> Path:
    """Get error log path."""
    return Path(project_path) / ".clouvel" / "errors"


def _classify_error(error_text: str) -> dict:
    """Classify error."""
    error_lower = error_text.lower()

    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, error_text, re.IGNORECASE):
                return {
                    "type": error_type,
                    "category": config["category"],
                    "prevention": config["prevention"]
                }

    return {
        "type": "unknown",
        "category": "Other Error",
        "prevention": "Analyze logs and add pattern"
    }


def _extract_stack_info(error_text: str) -> dict:
    """Extract information from stack trace."""
    info = {
        "file": None,
        "line": None,
        "function": None
    }

    # JavaScript/TypeScript 패턴
    js_match = re.search(r'at\s+(\S+)\s+\(([^:]+):(\d+):', error_text)
    if js_match:
        info["function"] = js_match.group(1)
        info["file"] = js_match.group(2)
        info["line"] = js_match.group(3)
        return info

    # Python 패턴
    py_match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\S+)', error_text)
    if py_match:
        info["file"] = py_match.group(1)
        info["line"] = py_match.group(2)
        info["function"] = py_match.group(3)
        return info

    return info


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


# ============================================================
# Error Learning Tools (v1.4)
# ============================================================

@require_license_premium
async def error_record(
    path: str,
    error_text: str,
    context: str = "",
    five_whys: list[str] = None,
    root_cause: str = "",
    solution: str = "",
    prevention: str = "",
    check_duplicates: bool = True
) -> list[TextContent]:
    """
    5 Whys structured error recording + MD file generation + SQLite storage

    Args:
        path: Project root path
        error_text: Error message
        context: Error occurrence context description
        five_whys: 5 Whys analysis results list
        root_cause: Root cause
        solution: Solution
        prevention: Recurrence prevention measures
        check_duplicates: Check for similar error duplicates (v2.0)
    """
    # v2.0: Duplicate check
    if check_duplicates and DB_AVAILABLE:
        init_db(path)
        similar = db_search_similar(error_text, n_results=3, threshold=0.9, project_path=path)
        if similar.get("highly_similar"):
            existing = similar["highly_similar"][0]
            return [TextContent(type="text", text=f"""
# Similar Error Already Exists

## Existing Error
- **ID**: {existing['id']}
- **Similarity**: {existing['similarity']}

## Check Existing Solution
Use `error_get` tool to check the existing solution.

## To Record as New
Call `error_record` again with `check_duplicates=false`.
""")]

    log_path = _get_error_log_path(path)
    log_path.mkdir(parents=True, exist_ok=True)

    # Classify error
    classification = _classify_error(error_text)
    stack_info = _extract_stack_info(error_text)

    # Timestamp
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H:%M:%S")

    # Generate error ID
    error_id = f"ERR-{timestamp.strftime('%Y%m%d-%H%M%S')}"

    # 5 Whys defaults
    if not five_whys:
        five_whys = [
            "Why did this error occur? → (Analysis required)",
            "Why did that situation happen? → (Analysis required)",
            "Why wasn't it detected? → (Analysis required)",
            "Why wasn't there a prevention measure? → (Analysis required)",
            "Why was there a gap in the process? → (Analysis required)"
        ]

    # Generate MD file
    md_content = f"""# {error_id}: {classification['category']}

> Created: {date_str} {time_str}

## Error Information

| Field | Value |
|-------|-------|
| **Category** | {classification['category']} |
| **Type** | `{classification['type']}` |
| **File** | {stack_info['file'] or 'Unknown'} |
| **Line** | {stack_info['line'] or 'Unknown'} |
| **Function** | {stack_info['function'] or 'Unknown'} |

## Error Message

```
{error_text[:1000]}
```

## Context

{context or '(Context description needed)'}

## 5 Whys Analysis

"""

    for i, why in enumerate(five_whys[:5], 1):
        md_content += f"### Why {i}\n{why}\n\n"

    md_content += f"""## Root Cause

{root_cause or '(Root cause analysis needed)'}

## Solution

{solution or '(Solution documentation needed)'}

## Prevention

{prevention or classification['prevention']}

---

## Learning Points

- [ ] Add NEVER rule to CLAUDE.md
- [ ] Add test case
- [ ] Add to code review checklist
"""

    # Save MD file
    errors_dir = log_path / "records"
    errors_dir.mkdir(parents=True, exist_ok=True)
    md_file = errors_dir / f"{error_id}.md"
    md_file.write_text(md_content, encoding="utf-8")

    # Also record in JSON log
    error_entry = {
        "error_id": error_id,
        "timestamp": timestamp.isoformat(),
        "error_text": error_text[:2000],
        "context": context,
        "classification": classification,
        "stack_info": stack_info,
        "five_whys": five_whys,
        "root_cause": root_cause,
        "solution": solution,
        "prevention": prevention,
        "md_file": str(md_file)
    }

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
        patterns[error_type] = {"count": 0, "last_seen": None, "examples": [], "root_causes": []}

    patterns[error_type]["count"] += 1
    patterns[error_type]["last_seen"] = timestamp.isoformat()
    if root_cause and root_cause not in patterns[error_type].get("root_causes", []):
        patterns[error_type].setdefault("root_causes", []).append(root_cause)

    pattern_file.write_text(json.dumps(patterns, ensure_ascii=False, indent=2), encoding="utf-8")

    # v2.0: SQLite DB storage
    db_error_id = None
    if DB_AVAILABLE:
        try:
            init_db(path)
            db_result = db_record_error(
                error_message=error_text,
                error_type=classification["type"],
                stack_trace=stack_info.get("file", ""),
                context=context,
                file_path=stack_info.get("file"),
                five_whys=five_whys,
                root_cause=root_cause,
                solution=solution,
                prevention=prevention or classification["prevention"],
                project_path=path,
            )
            db_error_id = db_result.get("id")

            # Add vector embedding (if available)
            if is_vector_search_available().get("available"):
                add_error_embedding(
                    db_error_id,
                    error_text,
                    metadata={"error_type": classification["type"]},
                    project_path=path,
                )
        except Exception:
            pass  # MD file saved even if DB storage fails

    # v4.0: Auto-create regression memory when root_cause is provided
    regression_id = None
    if root_cause and REGRESSION_AVAILABLE and DB_AVAILABLE:
        try:
            init_db(path)
            sig = normalize_error_signature(error_text)
            mem_tags = [classification["type"]]
            if stack_info.get("file"):
                mem_tags.append(Path(stack_info["file"]).name if "/" in str(stack_info["file"]) or "\\" in str(stack_info["file"]) else stack_info["file"])
            mem_result = create_memory(
                error_signature=sig,
                root_cause=root_cause,
                project_name=Path(path).name if path else "",
                error_category=classification["type"],
                file_paths=[stack_info["file"]] if stack_info.get("file") else [],
                tags=mem_tags,
                task_description=context or "",
                prevention_rule=prevention or classification["prevention"],
                severity=3,
                source_error_id=db_error_id or "",
                project_path=path,
            )
            regression_id = mem_result.get("id")
        except Exception:
            pass

    return [TextContent(type="text", text=f"""
# Error Recorded

## {error_id}

**Category**: {classification['category']}
**File**: {md_file}
{f"**DB ID**: {db_error_id}" if db_error_id else ""}
{f"**Regression Memory**: #{regression_id}" if regression_id else ""}

## 5 Whys Analysis

{"Analysis complete" if root_cause else "Analysis needed - please complete the 5 Whys"}

## Next Steps

1. Open MD file and complete 5 Whys: `{md_file}`
2. Use `error_learn` tool to auto-update CLAUDE.md
3. Add test cases
{f"4. Use `error_search` to find similar errors" if DB_AVAILABLE else ""}

## Tip

Proper error analysis prevents repeating the same mistakes.
Make sure to complete the 5 Whys!
""")]


@require_license_premium
async def error_check(
    path: str,
    context: str,
    file_path: str = "",
    operation: str = ""
) -> list[TextContent]:
    """
    Context-based proactive warning - check past error patterns before code changes

    Args:
        path: Project root path
        context: Current work context (code, plan, etc.)
        file_path: File path to modify
        operation: Operation to perform (edit, create, delete, etc.)
    """
    log_path = _get_error_log_path(path)

    warnings = []
    suggestions = []

    # 1. Check past error patterns
    pattern_file = log_path / "patterns.json"
    if pattern_file.exists():
        patterns = json.loads(pattern_file.read_text(encoding="utf-8"))

        context_lower = context.lower()

        for error_type, data in patterns.items():
            error_info = ERROR_PATTERNS.get(error_type, {})

            # Detect related patterns in context
            for pattern in error_info.get("patterns", []):
                if re.search(pattern, context, re.IGNORECASE):
                    count = data.get("count", 0)
                    if count >= 2:
                        warnings.append({
                            "type": error_type,
                            "category": error_info.get("category", error_type),
                            "count": count,
                            "prevention": error_info.get("prevention", ""),
                            "root_causes": data.get("root_causes", [])[:3]
                        })

    # 2. Check prevention rules
    rules_file = log_path / "prevention_rules.json"
    if rules_file.exists():
        rules = json.loads(rules_file.read_text(encoding="utf-8"))

        for error_type, rule_data in rules.items():
            for rule in rule_data.get("rules", []):
                if any(word.lower() in context.lower() for word in rule.split()[:3]):
                    suggestions.append({
                        "error_type": error_type,
                        "rule": rule
                    })

    # 3. Check file-specific error history
    file_warnings = []
    if file_path:
        log_file = log_path / "error_log.jsonl"
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        stack_info = entry.get("stack_info", {})
                        if stack_info.get("file") and file_path in stack_info["file"]:
                            file_warnings.append({
                                "error_id": entry.get("error_id", "?"),
                                "category": entry.get("classification", {}).get("category", "?"),
                                "root_cause": entry.get("root_cause", "")
                            })
                    except json.JSONDecodeError:
                        continue

    # 4. Regression Memory matching (v4.0)
    regression_matches = []
    if REGRESSION_AVAILABLE and DB_AVAILABLE:
        try:
            init_db(path)
            matches = match_all_levels(
                error_text=context,
                file_paths=[file_path] if file_path else None,
                error_category="",
                context=context,
                top_n=3,
                project_path=path,
            )
            for m in matches:
                increment_hit_count(m["id"], project_path=path)
                regression_matches.append(m)
        except Exception:
            pass

    # 5. Global Memory matching (cross-project)
    global_matches = []
    if GLOBAL_MEMORY_AVAILABLE:
        try:
            project_name = Path(path).name if path else "unknown"
            project_id = kb_get_or_create_project(name=project_name, path=path)
            current_domain = kb_get_project_domain(project_id) or "personal"

            search_query = context[:200] if context else ""
            if search_query:
                global_results = kb_search_global_memories(
                    query=search_query,
                    project_id_exclude=project_id,
                    domain=current_domain,
                    limit=3,
                )
                for gm in global_results:
                    kb_increment_global_hit(gm["id"])
                    global_matches.append(gm)
        except Exception:
            pass

    # Output results
    if not warnings and not suggestions and not file_warnings and not regression_matches and not global_matches:
        return [TextContent(type="text", text=f"""
# Proactive Check Complete

No risk factors matching past error patterns found.

**You may proceed**

---
*But stay alert! This could be a new type of error.*
""")]

    result = "# Proactive Warning\n\n"

    if regression_matches:
        result += "## Regression Memory Matches\n\n"
        for m in regression_matches:
            level_label = {1: "Exact", 2: "Similar", 3: "Related"}.get(m.get("match_level", 3), "Related")
            result += f"### [{level_label}] {m.get('error_category', 'unknown')} (Memory #{m['id']})\n"
            if m.get("root_cause"):
                result += f"- **Root Cause**: {m['root_cause'][:150]}\n"
            if m.get("prevention_rule"):
                result += f"- **Prevention**: {m['prevention_rule'][:150]}\n"
            if m.get("negative_constraint"):
                result += f"- **Constraint**: {m['negative_constraint'][:150]}\n"
            result += f"- **Hit Count**: {m.get('hit_count', 0)} | **Times Saved**: {m.get('times_saved', 0)}\n\n"

    if global_matches:
        result += "## Global Memory Matches (Cross-Project)\n\n"
        for gm in global_matches:
            result += f"### Global #{gm['id']} — {gm.get('error_category', 'unknown')}\n"
            result += f"- **Origin Project**: {gm.get('origin_project_name', 'unknown')}\n"
            if gm.get("root_cause"):
                result += f"- **Root Cause**: {gm['root_cause'][:150]}\n"
            if gm.get("prevention_rule"):
                result += f"- **Prevention**: {gm['prevention_rule'][:150]}\n"
            result += f"- **Global Hits**: {gm.get('hit_count', 0)} | **Times Saved**: {gm.get('times_saved', 0)}\n\n"

    if warnings:
        result += "## Past Error Patterns Detected\n\n"
        for w in warnings:
            result += f"### {w['category']} ({w['count']} occurrences)\n"
            result += f"- **Prevention**: {w['prevention']}\n"
            if w['root_causes']:
                result += f"- **Past Root Causes**:\n"
                for rc in w['root_causes']:
                    result += f"  - {rc}\n"
            result += "\n"

    if file_warnings:
        result += f"## File Error History\n\n"
        result += f"**{file_path}** has {len(file_warnings)} error(s) in history\n\n"
        for fw in file_warnings[:5]:
            result += f"- [{fw['error_id']}] {fw['category']}"
            if fw['root_cause']:
                result += f" - {fw['root_cause'][:50]}..."
            result += "\n"

    if suggestions:
        result += "## Recommended Rules to Apply\n\n"
        for s in suggestions:
            result += f"- {s['rule']}\n"

    result += """
---

## Recommended Actions

1. Review the warnings above
2. Check root causes of past errors
3. Apply prevention measures before proceeding
"""

    return [TextContent(type="text", text=result)]


@require_license_premium
async def error_learn(
    path: str,
    auto_update_claude_md: bool = True,
    min_count: int = 2
) -> list[TextContent]:
    """
    Session analysis + CLAUDE.md auto-update

    Args:
        path: Project root path
        auto_update_claude_md: Whether to auto-update CLAUDE.md
        min_count: Minimum error count to generate NEVER rule
    """
    log_path = _get_error_log_path(path)
    project_path = Path(path)

    if not log_path.exists():
        return [TextContent(type="text", text="No error records found. Record errors with `error_record` first.")]

    result = "# Error Learning Analysis\n\n"

    # 1. Pattern analysis
    pattern_file = log_path / "patterns.json"
    learned_rules = []

    if pattern_file.exists():
        patterns = json.loads(pattern_file.read_text(encoding="utf-8"))

        result += "## Error Pattern Analysis\n\n"
        result += "| Type | Count | Status |\n"
        result += "|------|-------|--------|\n"

        sorted_patterns = sorted(
            patterns.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        for error_type, data in sorted_patterns:
            count = data.get("count", 0)
            category = ERROR_PATTERNS.get(error_type, {}).get("category", error_type)
            status = "Learning needed" if count >= min_count else "Observing"
            result += f"| {category} | {count} | {status} |\n"

            # Extract learning targets
            if count >= min_count:
                prevention = ERROR_PATTERNS.get(error_type, {}).get("prevention", "")
                root_causes = data.get("root_causes", [])

                learned_rules.append({
                    "type": error_type,
                    "category": category,
                    "count": count,
                    "prevention": prevention,
                    "root_causes": root_causes
                })

        result += "\n"

    # 2. Additional learning from error records
    records_dir = log_path / "records"
    analyzed_records = []

    if records_dir.exists():
        for md_file in records_dir.glob("ERR-*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Only those with root cause recorded
            if "## Root Cause" in content and "(Root cause analysis needed)" not in content:
                # Parse
                root_cause_match = re.search(r"## Root Cause\n\n(.+?)(?=\n## |\Z)", content, re.DOTALL)
                prevention_match = re.search(r"## Prevention\n\n(.+?)(?=\n---|\Z)", content, re.DOTALL)

                if root_cause_match:
                    analyzed_records.append({
                        "file": md_file.name,
                        "root_cause": root_cause_match.group(1).strip()[:200],
                        "prevention": prevention_match.group(1).strip()[:200] if prevention_match else ""
                    })

    if analyzed_records:
        result += "## Analyzed Error Records\n\n"
        for rec in analyzed_records[:10]:
            result += f"### {rec['file']}\n"
            result += f"- **Root Cause**: {rec['root_cause'][:100]}...\n"
            if rec['prevention']:
                result += f"- **Prevention**: {rec['prevention'][:100]}...\n"
            result += "\n"

    # 3. Update CLAUDE.md
    claude_md_path = project_path / "CLAUDE.md"
    update_content = ""

    if learned_rules and auto_update_claude_md:
        update_content = "\n## Error Learning Rules (Auto-generated)\n\n"
        update_content += "> These rules were auto-generated from past error analysis.\n\n"

        # Generate NEVER rules
        update_content += "### NEVER\n\n"
        for rule in learned_rules:
            update_content += f"- **{rule['category']}** ({rule['count']} occurrences)\n"
            if rule['root_causes']:
                for rc in rule['root_causes'][:2]:
                    update_content += f"  - NEVER: {rc}\n"
            update_content += f"  - Prevention: {rule['prevention']}\n\n"

        # Generate ALWAYS rules
        update_content += "### ALWAYS\n\n"
        for rule in learned_rules:
            if rule['prevention']:
                update_content += f"- {rule['prevention']} (prevents {rule['category']})\n"

        update_content += "\n---\n"

        # Update CLAUDE.md
        marker = "## Error Learning Rules"

        if claude_md_path.exists():
            existing_content = claude_md_path.read_text(encoding="utf-8")

            if marker in existing_content:
                # Replace existing section
                pattern = r"## Error Learning Rules.*?(?=\n## [^E]|\Z)"
                new_content = re.sub(pattern, update_content.strip() + "\n\n", existing_content, flags=re.DOTALL)
            else:
                # Append to end
                new_content = existing_content.rstrip() + "\n\n" + update_content

            claude_md_path.write_text(new_content, encoding="utf-8")
            result += f"## CLAUDE.md Updated\n\n"
            result += f"**Path**: {claude_md_path}\n\n"
            result += "Added rules:\n"
            for rule in learned_rules:
                result += f"- {rule['category']}: NEVER rule added\n"
        else:
            # Create new
            new_content = f"# {project_path.name} Project Rules\n\n{update_content}"
            claude_md_path.write_text(new_content, encoding="utf-8")
            result += f"## CLAUDE.md Created\n\n**Path**: {claude_md_path}\n\n"

    elif learned_rules and not auto_update_claude_md:
        result += "## CLAUDE.md Update Suggestion\n\n"
        result += "Add the following to CLAUDE.md:\n\n"
        result += "```markdown\n"
        result += update_content
        result += "```\n"

    else:
        result += "## No Rules to Learn\n\n"
        result += f"No error patterns with {min_count}+ occurrences found.\n"
        result += "Record more errors with `error_record` and try again.\n"

    # 4. Statistics summary
    result += "\n## Learning Statistics\n\n"
    result += f"- **Analyzed Error Types**: {len(patterns) if pattern_file.exists() else 0}\n"
    result += f"- **Learned Rules**: {len(learned_rules)}\n"
    result += f"- **Analyzed Records**: {len(analyzed_records)}\n"

    return [TextContent(type="text", text=result)]


# ============================================================
# Error System v2.0 - New Tools
# ============================================================

@require_license_premium
async def error_search(
    path: str,
    query: str,
    error_type: str = "",
    limit: int = 5
) -> list[TextContent]:
    """
    Error similarity search (vector + text hybrid)

    Args:
        path: Project root path
        query: Error text to search
        error_type: Error type filter (optional)
        limit: Maximum number of results
    """
    if not DB_AVAILABLE:
        return [TextContent(type="text", text="""
# Error Search Unavailable

DB module not loaded.
Record errors with `error_record` and try again.
""")]

    init_db(path)

    # Check vector/text search status
    vector_status = is_vector_search_available()

    # Execute search
    results = db_search_similar(
        query,
        error_type=error_type or None,
        n_results=limit,
        threshold=0.7,
        project_path=path,
    )

    method = results.get("method", "unknown")
    highly_similar = results.get("highly_similar", [])
    possibly_related = results.get("possibly_related", results.get("results", []))

    search_result = f"# Error Search Results\n\n"
    search_result += f"**Search Method**: {method}\n"
    search_result += f"**Vector Search**: {'Available' if vector_status['available'] else 'Unavailable (chromadb required)'}\n\n"

    if highly_similar:
        search_result += "## Highly Similar Errors\n\n"
        for e in highly_similar:
            search_result += f"### {e['id']} (Similarity: {e['similarity']})\n"
            doc = e.get('document') or e.get('error_message', '')
            search_result += f"```\n{doc[:200]}...\n```\n"
            if e.get('metadata', {}).get('error_type'):
                search_result += f"**Type**: {e['metadata']['error_type']}\n"
            search_result += "\n"

    if possibly_related:
        search_result += "## Possibly Related Errors\n\n"
        for e in possibly_related[:3]:
            search_result += f"- **{e.get('id', '?')}** (Similarity: {e.get('similarity', '?')})\n"
            doc = e.get('document') or e.get('error_message', '')
            search_result += f"  {doc[:100]}...\n"

    if not highly_similar and not possibly_related:
        search_result += "## No Similar Errors Found\n\n"
        search_result += "Record this error with `error_record`.\n"

    return [TextContent(type="text", text=search_result)]


@require_license_premium
async def error_resolve(
    path: str,
    error_id: str,
    effective: bool = True,
    solution: str = "",
    create_rule: bool = False
) -> list[TextContent]:
    """
    Mark error as resolved + effectiveness feedback

    Args:
        path: Project root path
        error_id: Error ID to resolve
        effective: Whether the solution was effective
        solution: Solution update (optional)
        create_rule: Auto-generate NEVER/ALWAYS rule
    """
    if not DB_AVAILABLE:
        return [TextContent(type="text", text="DB module required.")]

    init_db(path)

    # Mark error as resolved
    result_data = db_resolve_error(
        error_id,
        effective=effective,
        solution=solution or None,
        project_path=path,
    )

    if result_data.get("status") == "not_found":
        return [TextContent(type="text", text=f"# Error Not Found\n\nID: {error_id}")]

    resolve_result = f"# Error Resolved\n\n"
    resolve_result += f"**ID**: {error_id}\n"
    resolve_result += f"**Effective**: {'Yes' if effective else 'No'}\n\n"

    # Create rule
    if create_rule and effective:
        error = db_get_error(error_id, project_path=path)
        if error and error.get("root_cause"):
            rule_result = db_add_rule(
                rule_type="NEVER",
                content=error["root_cause"],
                source_error_id=error_id,
                project_path=path,
            )
            if rule_result.get("status") == "created":
                resolve_result += f"## Rule Created\n\n"
                resolve_result += f"**Type**: NEVER\n"
                resolve_result += f"**Content**: {error['root_cause'][:100]}...\n"

    # Update statistics
    stats = db_get_error_stats(days=30, project_path=path)
    resolve_result += f"\n## Statistics\n\n"
    resolve_result += f"- Total Errors: {stats['total']}\n"
    resolve_result += f"- Resolved: {stats['resolved']}\n"
    resolve_result += f"- Effective: {stats['effective']}\n"

    return [TextContent(type="text", text=resolve_result)]


@require_license
async def error_get(
    path: str,
    error_id: str
) -> list[TextContent]:
    """
    Get error details

    Args:
        path: Project root path
        error_id: Error ID to retrieve
    """
    if not DB_AVAILABLE:
        return [TextContent(type="text", text="DB module required.")]

    init_db(path)
    error = db_get_error(error_id, project_path=path)

    if not error:
        return [TextContent(type="text", text=f"# Error Not Found\n\nID: {error_id}")]

    get_result = f"# Error Details: {error_id}\n\n"

    get_result += "## Basic Information\n\n"
    get_result += f"- **Created**: {error.get('created_at', '?')}\n"
    get_result += f"- **Type**: {error.get('error_type', '?')}\n"
    get_result += f"- **File**: {error.get('file_path', '?')}\n"
    get_result += f"- **Resolved**: {'Yes' if error.get('resolved_at') else 'No'}\n\n"

    get_result += "## Error Message\n\n"
    get_result += f"```\n{error.get('error_message', '')[:500]}\n```\n\n"

    if error.get("context"):
        get_result += f"## Context\n\n{error['context']}\n\n"

    if error.get("five_whys"):
        get_result += "## 5 Whys\n\n"
        for i, why in enumerate(error["five_whys"], 1):
            get_result += f"{i}. {why}\n"
        get_result += "\n"

    if error.get("root_cause"):
        get_result += f"## Root Cause\n\n{error['root_cause']}\n\n"

    if error.get("solution"):
        get_result += f"## Solution\n\n{error['solution']}\n\n"

    if error.get("prevention"):
        get_result += f"## Prevention\n\n{error['prevention']}\n\n"

    return [TextContent(type="text", text=get_result)]


@require_license
async def error_stats(
    path: str,
    days: int = 30
) -> list[TextContent]:
    """
    Get error statistics

    Args:
        path: Project root path
        days: Query period (days)
    """
    if not DB_AVAILABLE:
        return [TextContent(type="text", text="DB module required.")]

    init_db(path)
    stats = db_get_error_stats(days=days, project_path=path)

    stats_result = f"# Error Statistics (Last {days} Days)\n\n"

    stats_result += "## Summary\n\n"
    stats_result += f"- **Total Errors**: {stats['total']}\n"
    stats_result += f"- **Resolved**: {stats['resolved']}\n"
    stats_result += f"- **Effectively Resolved**: {stats['effective']}\n"

    if stats.get("mttr_minutes"):
        stats_result += f"- **Average Resolution Time**: {stats['mttr_minutes']} min\n"

    if stats.get("by_type"):
        stats_result += "\n## Errors by Type\n\n"
        stats_result += "| Type | Count |\n"
        stats_result += "|------|-------|\n"
        for error_type, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
            stats_result += f"| {error_type} | {count} |\n"

    # Vector search status
    vector_status = is_vector_search_available()
    stats_result += f"\n## System Status\n\n"
    stats_result += f"- **DB**: Available\n"
    stats_result += f"- **Vector Search**: {'Available' if vector_status['available'] else 'Unavailable'}\n"

    return [TextContent(type="text", text=stats_result)]


# ============================================================
# Regression Memory Status (v4.0)
# ============================================================

@require_license_premium
async def memory_status(
    path: str,
) -> list[TextContent]:
    """
    Regression Memory status and statistics.

    Args:
        path: Project root path
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    stats = db_get_memory_stats(project_path=path)

    result = "# Regression Memory Status\n\n"

    # One-line summary
    result += f"**{stats['active']} active memories** | "
    result += f"{stats['total_hits']} hits | "
    result += f"{stats['total_saves']} saves | "
    result += f"{stats['save_rate']}% save rate\n\n"

    # Top memories
    if stats.get("top_memories"):
        result += "## Top Memories (by hit count)\n\n"
        result += "| # | Category | Signature | Hits | Saves |\n"
        result += "|---|----------|-----------|------|-------|\n"
        for m in stats["top_memories"]:
            sig_short = m["error_signature"][:40] + "..." if len(m["error_signature"]) > 40 else m["error_signature"]
            result += f"| {m['id']} | {m['error_category']} | {sig_short} | {m['hit_count']} | {m['times_saved']} |\n"
        result += "\n"

    # Category breakdown
    if stats.get("categories"):
        result += "## Categories\n\n"
        for cat, count in stats["categories"].items():
            result += f"- **{cat}**: {count}\n"
        result += "\n"

    # Summary
    if stats["archived"] > 0:
        result += f"*{stats['archived']} archived memories not shown*\n"

    # Auto-stale: archive memories with 0 hits older than 60 days
    try:
        stale_result = db_mark_stale_memories(days_threshold=60, project_path=path)
        if stale_result["archived_count"] > 0:
            result += f"\n*{stale_result['archived_count']} stale memories auto-archived (0 hits, >60 days)*\n"
    except Exception:
        pass

    return [TextContent(type="text", text=result)]


# ============================================================
# Regression Memory Management (v4.0 Phase 2)
# ============================================================

@require_license_premium
async def memory_list(
    path: str,
    category: str = "",
    include_archived: bool = False,
    limit: int = 20,
) -> list[TextContent]:
    """
    List regression memories with optional category filter.

    Args:
        path: Project root path
        category: Filter by error category (optional)
        include_archived: Include archived memories (default false)
        limit: Max results (default 20)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    memories = db_list_memories_reg(
        include_archived=include_archived,
        limit=limit,
        project_path=path,
    )

    # Apply category filter if provided
    if category:
        memories = [m for m in memories if m.get("error_category") == category]

    if not memories:
        return [TextContent(type="text", text="# Regression Memories\n\nNo memories found.")]

    result = f"# Regression Memories ({len(memories)} results)\n\n"
    result += "| ID | Category | Signature | Hits | Saves | Date |\n"
    result += "|----|----------|-----------|------|-------|------|\n"

    for m in memories:
        sig_short = m["error_signature"][:40] + "..." if len(m["error_signature"]) > 40 else m["error_signature"]
        date = m.get("timestamp", "")[:10] if m.get("timestamp") else "-"
        archived_tag = " [A]" if m.get("archived") else ""
        result += f"| {m['id']}{archived_tag} | {m.get('error_category', '-')} | {sig_short} | {m.get('hit_count', 0)} | {m.get('times_saved', 0)} | {date} |\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def memory_search(
    path: str,
    query: str,
    category: str = "",
) -> list[TextContent]:
    """
    Search regression memories by keyword (FTS5).

    Args:
        path: Project root path
        query: Search keyword
        category: Filter by category (optional)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    memories = db_search_memories(
        query=query,
        category=category,
        project_path=path,
    )

    if not memories:
        return [TextContent(type="text", text=f'# Memory Search: "{query}"\n\nNo matching memories found.')]

    result = f'# Memory Search: "{query}" ({len(memories)} results)\n\n'

    for m in memories:
        result += f"## Memory #{m['id']} — {m.get('error_category', 'unknown')}\n\n"
        result += f"**Signature**: {m['error_signature'][:80]}\n"
        if m.get("root_cause"):
            result += f"**Root Cause**: {m['root_cause'][:150]}\n"
        if m.get("prevention_rule"):
            result += f"**Prevention**: {m['prevention_rule'][:150]}\n"
        result += f"**Hits**: {m.get('hit_count', 0)} | **Saves**: {m.get('times_saved', 0)}\n\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def memory_archive(
    path: str,
    memory_id: int,
    action: str = "archive",
) -> list[TextContent]:
    """
    Archive or unarchive a regression memory.

    Args:
        path: Project root path
        memory_id: Memory ID to archive/unarchive
        action: "archive" or "unarchive" (default: archive)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)

    if action == "unarchive":
        res = db_unarchive_memory(memory_id, project_path=path)
    else:
        res = db_archive_memory(memory_id, project_path=path)

    if res.get("status") == "not_found":
        return [TextContent(type="text", text=f"# Memory Not Found\n\nMemory #{memory_id} does not exist.")]

    return [TextContent(type="text", text=f"# Memory #{memory_id} {res['status'].title()}\n\nAction completed successfully.")]


@require_license_premium
async def memory_report(
    path: str,
    days: int = 30,
) -> list[TextContent]:
    """
    Monthly regression memory report.

    Args:
        path: Project root path
        days: Report period in days (default 30)
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]

    init_db(path)
    report = db_get_memory_report(days=days, project_path=path)

    # One-line summary
    result = f"# Regression Memory Report ({report['period_days']} days)\n\n"
    result += f"> **{report['total_saves']} errors prevented** | "
    result += f"~{report['time_saved_hours']}h saved | "
    result += f"{report['save_rate']}% save rate\n\n"

    # Detailed stats
    result += "## Statistics\n\n"
    result += f"- **New memories**: {report['new_memories']}\n"
    result += f"- **Active memories**: {report['active']}\n"
    result += f"- **Archived**: {report['archived']}\n"
    result += f"- **Total hits**: {report['total_hits']}\n"
    result += f"- **Total saves**: {report['total_saves']}\n"
    result += f"- **Save rate**: {report['save_rate']}%\n\n"

    # Time saved estimate
    result += "## Time Saved Estimate\n\n"
    result += f"- **{report['total_saves']}** errors prevented × **15 min** avg debug time\n"
    result += f"- **= {report['time_saved_minutes']} minutes ({report['time_saved_hours']} hours) saved**\n\n"

    # Top memories
    if report.get("top_memories"):
        result += "## Top Memories (by hit count)\n\n"
        result += "| # | Category | Root Cause | Hits | Saves |\n"
        result += "|---|----------|-----------|------|-------|\n"
        for m in report["top_memories"]:
            rc_short = m["root_cause"][:50] + "..." if len(m["root_cause"]) > 50 else m["root_cause"]
            result += f"| {m['id']} | {m['error_category']} | {rc_short} | {m['hit_count']} | {m['times_saved']} |\n"
        result += "\n"

    # Top categories
    if report.get("top_categories"):
        result += "## Top Categories\n\n"
        for c in report["top_categories"]:
            result += f"- **{c['category']}**: {c['count']} memories\n"

    return [TextContent(type="text", text=result)]


# ============================================================
# Cross-Project Memory Transfer (v5.0)
# ============================================================

@require_license_premium
async def memory_promote(
    path: str,
    memory_id: int,
) -> list[TextContent]:
    """
    Promote a local regression memory to global (cross-project).

    Only root_cause and prevention_rule are promoted (no raw error text).
    Requires hit_count >= 1 to ensure quality.

    Args:
        path: Project root path
        memory_id: Local memory ID to promote
    """
    if not REGRESSION_AVAILABLE or not DB_AVAILABLE:
        return [TextContent(type="text", text="Regression Memory module not available.")]
    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    init_db(path)

    # Get local memory (full data for validation)
    local_mem = db_get_memory(memory_id, project_path=path)
    if local_mem is None:
        return [TextContent(type="text", text=f"# Memory Not Found\n\nLocal memory #{memory_id} does not exist.")]

    # Validate: hit_count >= 1 (zero-hit memories are unproven)
    if local_mem.get("hit_count", 0) < 1:
        return [TextContent(type="text", text=f"""# Cannot Promote Memory #{memory_id}

**Reason**: Memory has 0 hits. Only memories that have been matched at least once can be promoted to global.

**Tip**: Use this memory in error_check first to build confidence, then promote.
""")]

    # Get promote-safe data (excludes sensitive fields)
    promote_data = db_get_memory_for_promote(memory_id, project_path=path)
    if promote_data is None:
        return [TextContent(type="text", text=f"# Memory Not Found\n\nLocal memory #{memory_id} does not exist.")]

    # Get or create project in knowledge DB
    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    # Auto-inherit domain from project
    project_domain = kb_get_project_domain(project_id) if GLOBAL_MEMORY_AVAILABLE else None

    # Promote to global
    result = kb_promote_memory(promote_data, project_id, project_name, domain=project_domain)

    if result.get("status") == "duplicate":
        return [TextContent(type="text", text=f"""# Already Promoted

Memory #{memory_id} has already been promoted to global (Global ID: #{result.get('existing_id')}).
""")]

    return [TextContent(type="text", text=f"""# Memory #{memory_id} Promoted to Global

**Global ID**: #{result['id']}
**Root Cause**: {promote_data['root_cause'][:150]}
**Prevention**: {promote_data['prevention_rule'][:150]}

This memory is now available across all projects via `memory_global_search`.
""")]


@require_license_premium
async def memory_global_search(
    path: str,
    query: str,
    category: str = "",
    domain: str = "",
) -> list[TextContent]:
    """
    Search global regression memories from all projects.

    Finds patterns learned in other projects. Current project is excluded
    from results (use local memory_search for that).

    Args:
        path: Project root path
        query: Search keyword
        category: Filter by error category (optional)
        domain: Filter by domain (personal/work/client). Auto-detected if not specified.
    """
    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    # Get current project ID to exclude from results
    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    # Auto-detect domain from project if not specified
    effective_domain = domain or None
    if not effective_domain:
        try:
            effective_domain = kb_get_project_domain(project_id) or None
        except Exception:
            pass

    memories = kb_search_global_memories(
        query=query,
        project_id_exclude=project_id,
        category=category or None,
        domain=effective_domain,
    )

    if not memories:
        return [TextContent(type="text", text=f'# Global Memory Search: "{query}"\n\nNo matching memories found in other projects.')]

    result = f'# Global Memory Search: "{query}" ({len(memories)} results)\n\n'

    for m in memories:
        result += f"## Global #{m['id']} — {m.get('error_category', 'unknown')}\n\n"
        result += f"**Origin**: {m.get('origin_project_name', 'unknown')}\n"
        result += f"**Root Cause**: {m.get('root_cause', '')[:150]}\n"
        result += f"**Prevention**: {m.get('prevention_rule', '')[:150]}\n"
        result += f"**Hits**: {m.get('hit_count', 0)} | **Saves**: {m.get('times_saved', 0)}\n\n"

    return [TextContent(type="text", text=result)]


@require_license_premium
async def set_project_domain(
    path: str,
    domain: str,
) -> list[TextContent]:
    """
    Set the domain for the current project. Domains isolate memories.

    Args:
        path: Project root path
        domain: Domain value (personal/work/client)
    """
    valid_domains = ("personal", "work", "client")
    if domain not in valid_domains:
        return [TextContent(type="text", text=f"# Invalid Domain\n\nDomain must be one of: {', '.join(valid_domains)}\n\nGot: `{domain}`")]

    if not GLOBAL_MEMORY_AVAILABLE:
        return [TextContent(type="text", text="Global Memory module not available. Knowledge Base required.")]

    project_name = Path(path).name if path else "unknown"
    project_id = kb_get_or_create_project(name=project_name, path=path)

    result = kb_set_project_domain(project_id, domain)

    if result.get("status") == "not_found":
        return [TextContent(type="text", text=f"# Project Not Found\n\nCould not find project with ID: {project_id}")]

    return [TextContent(type="text", text=f"""# Project Domain Set

**Project**: {project_name}
**Domain**: {domain}

Memories promoted from this project will inherit the `{domain}` domain.
Global memory searches will be scoped to `{domain}` domain by default.
""")]
