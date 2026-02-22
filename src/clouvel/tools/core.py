# -*- coding: utf-8 -*-
"""Core tools: can_code, scan_docs, analyze_docs, init_docs"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

# Rich UI (optional)
try:
    from clouvel.ui import render_can_code, HAS_RICH
except ImportError:
    HAS_RICH = False
    render_can_code = None

# v3.0: License tier checking
from clouvel.license_common import is_feature_available, register_project, increment_warn_count
# v3.2: Full Pro trial
from clouvel.license_common import get_full_trial_status

# v3.0: Migration notice

# Knowledge Base integration (optional - graceful fallback if not available)
try:
    from clouvel.db.knowledge import (
        get_recent_decisions,
        get_recent_locations,
        get_or_create_project,
        KNOWLEDGE_DB_PATH,
    )
    _HAS_KNOWLEDGE = KNOWLEDGE_DB_PATH.exists()
except ImportError:
    _HAS_KNOWLEDGE = False

# PRD Quality Scoring (Phase 1 — informational only)
from clouvel.tools.prd_scoring import score_prd, format_score_report

from clouvel.messages import (
    DOC_NAMES,
    CAN_CODE_BLOCK_NO_DOCS,
    CAN_CODE_BLOCK_MISSING_DOCS,
    CAN_CODE_PASS_WITH_WARN,
    CAN_CODE_PASS,
    PRD_RULE_WARNING,
    TEST_COUNT,
    NO_TESTS,
    PRD_SECTION_PREFIX,
    SCAN_PATH_NOT_FOUND,
    SCAN_NOT_DIRECTORY,
    SCAN_RESULT,
    ANALYZE_PATH_NOT_FOUND,
    ANALYZE_RESULT_HEADER,
    ANALYZE_FOUND_HEADER,
    ANALYZE_MISSING_HEADER,
    ANALYZE_COMPLETE,
    ANALYZE_INCOMPLETE,
    INIT_RESULT_HEADER,
    INIT_CREATED_HEADER,
    INIT_ALREADY_EXISTS,
    INIT_NEXT_STEPS,
    TEMPLATE_PRD,
    TEMPLATE_ARCHITECTURE,
    TEMPLATE_API,
    TEMPLATE_DATABASE,
    TEMPLATE_VERIFICATION,
    # v3.0: FREE tier messages
    CAN_CODE_PROJECT_LIMIT,
    CAN_CODE_WARN_NO_DOCS_FREE,
    CAN_CODE_WARN_NO_PRD_FREE,
    CAN_CODE_PASS_FREE,
    CAN_CODE_WARN_ACCUMULATED,
    # v3.2: Trial messages
    CAN_CODE_TRIAL_ACTIVE,
    CAN_CODE_TRIAL_EXPIRED,
    CAN_CODE_TRIAL_NUDGE_5,
    CAN_CODE_TRIAL_NUDGE_7,
)

# Required documents definition
REQUIRED_DOCS = [
    {"type": "prd", "name": DOC_NAMES["prd"], "patterns": [r"prd", r"product.?requirement"], "priority": "critical"},
    {"type": "architecture", "name": DOC_NAMES["architecture"], "patterns": [r"architect", r"arch", r"module"], "priority": "warn"},
    {"type": "api_spec", "name": DOC_NAMES["api_spec"], "patterns": [r"api", r"swagger", r"openapi"], "priority": "warn"},
    {"type": "db_schema", "name": DOC_NAMES["db_schema"], "patterns": [r"schema", r"database", r"db"], "priority": "warn"},
    {"type": "verification", "name": DOC_NAMES["verification"], "patterns": [r"verif", r"test.?plan"], "priority": "warn"},
]

# PRD required sections (acceptance/DoD is critical)
REQUIRED_PRD_SECTIONS = [
    {"name": "acceptance", "patterns": [
        r"##\s*(acceptance|완료\s*기준|수락\s*조건|done\s*when)",
        r"##\s*(dod|definition\s*of\s*done|완료\s*정의)",
        r"##\s*(criteria|기준)",
    ], "priority": "critical"},
    {"name": "scope", "patterns": [r"##\s*(scope|범위|목표)"], "priority": "warn"},
    {"name": "non_goals", "patterns": [r"##\s*(non.?goals?|하지\s*않을|제외|out\s*of\s*scope)"], "priority": "warn"},
]


def _get_context_summary(project_path: Path) -> str:
    """Get recent context from Knowledge Base for session recovery."""
    if not _HAS_KNOWLEDGE:
        return ""

    try:
        # Get or create project
        project_name = project_path.name
        project_id = get_or_create_project(project_name, str(project_path))

        decisions = get_recent_decisions(project_id=project_id, limit=5)
        locations = get_recent_locations(project_id=project_id, limit=5)

        if not decisions and not locations:
            return ""

        lines = ["\n---\n## 📋 Recent Context (auto-loaded)\n"]

        if decisions:
            lines.append("### Decisions")
            for d in decisions:
                category = d.get('category', 'general')
                decision_text = d.get('decision', '')[:80]
                # Check if locked (category starts with "locked:")
                if category.startswith("locked:"):
                    actual_category = category[7:]  # Remove "locked:" prefix
                    lines.append(f"- 🔒 **[{actual_category}]** {decision_text} *(LOCKED - do not change)*")
                else:
                    lines.append(f"- **[{category}]** {decision_text}")
            lines.append("")

        if locations:
            lines.append("### Code Locations")
            for loc in locations:
                lines.append(f"- **{loc.get('name', '')}**: `{loc.get('repo', '')}/{loc.get('path', '')}`")
            lines.append("")

        lines.append("_Use `search_knowledge` for more context._")
        return "\n".join(lines)

    except Exception:
        return ""


def _find_prd_file(docs_path: Path) -> Path | None:
    """Find PRD file"""
    for f in docs_path.iterdir():
        if f.is_file():
            name_lower = f.name.lower()
            if "prd" in name_lower or "product" in name_lower and "requirement" in name_lower:
                return f
    return None


def _check_prd_sections(prd_path: Path) -> tuple[list[str], list[str], list[str]]:
    """Check required sections in PRD file
    Returns: (found_critical, missing_critical, missing_warn)
    """
    try:
        content = prd_path.read_text(encoding='utf-8')
    except Exception:
        return [], ["acceptance"], []

    found_critical = []
    missing_critical = []
    missing_warn = []

    for section in REQUIRED_PRD_SECTIONS:
        found = False
        for pattern in section["patterns"]:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                found = True
                break

        if found:
            if section["priority"] == "critical":
                found_critical.append(section["name"])
        else:
            if section["priority"] == "critical":
                missing_critical.append(section["name"])
            else:
                missing_warn.append(section["name"])

    return found_critical, missing_critical, missing_warn


def _check_tests(project_path: Path) -> tuple[int, list[str]]:
    """Check for test files
    Returns: (test_count, test_files)
    """
    test_patterns = [r"test_.*\.py$", r".*_test\.py$", r".*\.test\.(ts|js)$", r".*\.spec\.(ts|js)$"]
    test_files = []

    # Search for test files in project root and subdirectories
    search_paths = [project_path]
    for subdir in ["tests", "test", "src", "__tests__"]:
        subpath = project_path / subdir
        if subpath.exists():
            search_paths.append(subpath)

    for search_path in search_paths:
        if not search_path.exists():
            continue
        try:
            for f in search_path.rglob("*"):
                try:
                    if f.is_file():
                        for pattern in test_patterns:
                            if re.match(pattern, f.name, re.IGNORECASE):
                                test_files.append(str(f.relative_to(project_path)))
                                break
                except (OSError, PermissionError):
                    # Ignore broken symlinks, permission denied, etc.
                    continue
        except (OSError, PermissionError):
            continue

    return len(test_files), test_files[:5]  # 최대 5개만 반환


def _write_gate_status(project_path: Path, status: str, reason: str = ""):
    """Write gate status for PreToolUse hook enforcement.

    The PreToolUse hook (gate_check.py) reads this file to decide
    whether to allow Edit/Write tool execution at the runtime level.
    """
    gate_dir = project_path / ".clouvel"
    gate_dir.mkdir(parents=True, exist_ok=True)
    gate_file = gate_dir / "gate.json"
    gate_file.write_text(json.dumps({
        "status": status,       # "PASS" or "BLOCK"
        "reason": reason,
        "timestamp": time.time(),
        "ttl": 600,             # 10 minutes
    }), encoding="utf-8")


async def _check_file_tracking(project_path: Path) -> list[TextContent]:
    """Check if new files are tracked in created.md (post-coding check)"""
    import subprocess

    created_md = project_path / ".claude" / "files" / "created.md"

    # Get new files from git (uncommitted + staged)
    try:
        # New files (untracked + staged new)
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", "HEAD"],
            capture_output=True, text=True, cwd=project_path, timeout=10
        )
        new_files_staged = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()

        # Untracked files
        result2 = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=project_path, timeout=10
        )
        new_files_untracked = set(result2.stdout.strip().split("\n")) if result2.stdout.strip() else set()

        new_files = new_files_staged | new_files_untracked
        new_files.discard("")  # Remove empty string
    except Exception:
        return [TextContent(type="text", text="⚠️ POST CHECK: Could not run git commands")]

    if not new_files:
        return [TextContent(type="text", text="✅ POST CHECK: No new files detected")]

    # Skip patterns (config, docs, etc.)
    skip_patterns = {".md", ".txt", ".json", ".yml", ".yaml", ".gitignore", ".env", "__pycache__", ".pyc"}
    filtered_files = []
    for f in new_files:
        if not any(f.endswith(ext) or ext in f for ext in skip_patterns):
            filtered_files.append(f)

    if not filtered_files:
        return [TextContent(type="text", text="✅ POST CHECK: No trackable new files (all config/docs)")]

    # Check created.md
    tracked_files = set()
    if created_md.exists():
        content = created_md.read_text(encoding="utf-8")
        for f in filtered_files:
            if f in content:
                tracked_files.add(f)

    untracked = [f for f in filtered_files if f not in tracked_files]

    if not untracked:
        return [TextContent(type="text", text=f"✅ POST CHECK: All {len(filtered_files)} new files are tracked")]

    # Generate warning with copy-paste commands
    commands = []
    for f in untracked[:10]:  # Max 10
        commands.append(f'record_file(path=".", file_path="{f}", purpose="<describe>")')

    output = f"""⚠️ POST CHECK: {len(untracked)} untracked new files

**Untracked files:**
{chr(10).join(f"  📁 {f}" for f in untracked[:10])}
{f"  ... and {len(untracked) - 10} more" if len(untracked) > 10 else ""}

**To track, copy & run:**
```
{chr(10).join(commands)}
```
"""
    return [TextContent(type="text", text=output)]


async def can_code(path: str, mode: str = "pre") -> list[TextContent]:
    """Check if coding is allowed - core feature (B4: quality gate extension)

    v3.0: FREE tier = WARN (can proceed), PRO tier = BLOCK (must fix first)

    Args:
        path: docs folder path
        mode: "pre" (default) - check before coding
              "post" - check after coding (verify file tracking)
    """
    docs_path = Path(path)

    # Early path validation — exit fast on completely invalid paths
    # Only triggers when the PARENT directory doesn't exist (clearly wrong path)
    # If parent exists but docs_path doesn't, fall through to normal BLOCK/WARN logic
    if not docs_path.exists() and not docs_path.parent.exists():
        suggestions = []
        # Walk up to find nearest existing ancestor
        ancestor = docs_path.parent
        while not ancestor.exists() and ancestor != ancestor.parent:
            ancestor = ancestor.parent
        if ancestor.exists():
            candidates = [d for d in ancestor.iterdir() if d.is_dir()][:5]
            suggestions.extend(str(c) for c in candidates[:3])

        msg = f"PATH NOT FOUND: {path}\n\n"
        msg += "The path does not exist. can_code needs a valid project or docs folder path.\n\n"
        if suggestions:
            msg += "Did you mean:\n"
            for s in suggestions[:3]:
                msg += f"  -> can_code(path=\"{s}\")\n"
        else:
            msg += "Usage:\n"
            msg += "  can_code(path=\"/your/project\")        # project root\n"
            msg += "  can_code(path=\"/your/project/docs\")   # docs folder\n"
        return [TextContent(type="text", text=msg)]

    project_path = docs_path.parent if docs_path.name == "docs" else docs_path

    # POST mode: check file tracking
    if mode == "post":
        return await _check_file_tracking(project_path)

    # v3.0: Check license tier for behavior
    validation_check = is_feature_available("full_prd_validation")
    is_pro = validation_check["available"]
    is_trial = validation_check.get("reason") == "trial"
    trial_remaining = validation_check.get("remaining_days", 0)

    blocking_check = is_feature_available("code_blocking")
    can_block = blocking_check["available"]

    # v3.0.0: First Project Unlimited override
    if not is_pro:
        from clouvel.license_common import get_project_tier
        tier = get_project_tier(str(project_path))
        if tier == "first":
            is_pro = True
            can_block = True
            # Don't set is_trial — this is permanent, not trial

    # v3.2: Trial expired check (for FREE path messaging)
    trial_status = get_full_trial_status()
    trial_expired = (not trial_status.get("never_started", False)
                     and not trial_status.get("active", False)
                     and not is_trial)

    # v3.0: Project limit check (FREE = 1 project, first project unlimited)
    project_check = register_project(str(project_path))
    if not project_check.get("allowed", True):
        # v3.3: Track A/B conversion event
        try:
            from ..license_common import track_conversion_event
            track_conversion_event("project_limit", "limit_hit", {
                "count": project_check["count"],
                "limit": project_check["limit"],
            })
        except Exception:
            pass
        _write_gate_status(project_path, "BLOCK", "Project limit reached")
        return [TextContent(type="text", text=CAN_CODE_PROJECT_LIMIT)]

    # v3.0: No docs folder - BLOCK for Pro, WARN for Free
    if not docs_path.exists():
        # v3.3: Track A/B conversion event
        try:
            from ..license_common import track_conversion_event
            track_conversion_event("pain_point_message", "no_docs_warn", {"path": str(path)})
        except Exception:
            pass
        if can_block:
            _write_gate_status(project_path, "BLOCK", "No docs folder")
            return [TextContent(type="text", text=CAN_CODE_BLOCK_NO_DOCS.format(path=path))]
        else:
            _write_gate_status(project_path, "PASS", "WARN - no docs (free)")
            return [TextContent(type="text", text=CAN_CODE_WARN_NO_DOCS_FREE.format(
                path=path, upgrade_hint="$49/yr"
            ))]

    files = [f for f in docs_path.iterdir() if f.is_file()]
    file_names = [f.name.lower() for f in files]

    detected_critical = []
    detected_warn = []
    missing_critical = []
    missing_warn = []

    for req in REQUIRED_DOCS:
        found = False
        for filename in file_names:
            for pattern in req["patterns"]:
                if re.search(pattern, filename, re.IGNORECASE):
                    if req["priority"] == "critical":
                        detected_critical.append(req["name"])
                    else:
                        detected_warn.append(req["name"])
                    found = True
                    break
            if found:
                break
        if not found:
            if req["priority"] == "critical":
                missing_critical.append(req["name"])
            else:
                missing_warn.append(req["name"])

    # B4: Check PRD content (acceptance section required)
    prd_file = _find_prd_file(docs_path)
    prd_sections_found = []
    prd_sections_missing_critical = []
    prd_sections_missing_warn = []

    if prd_file:
        prd_sections_found, prd_sections_missing_critical, prd_sections_missing_warn = _check_prd_sections(prd_file)

    # B4: Check test files
    test_count, test_files = _check_tests(project_path)

    # v3.0: FREE tier - existence check only, never block
    if not is_pro:
        prd_exists = prd_file is not None
        if prd_exists:
            base_msg = CAN_CODE_PASS_FREE.format(
                test_count=test_count,
            )
            # Phase 1: PRD Quality Score (informational — does not change gate behavior)
            try:
                prd_content = prd_file.read_text(encoding="utf-8")
                scoring_result = score_prd(prd_content, level="lite")
                base_msg += format_score_report(scoring_result)
            except Exception:
                pass  # Scoring failure should never block coding
            # v3.2: Show trial expired message if applicable
            if trial_expired:
                base_msg += CAN_CODE_TRIAL_EXPIRED
            # v3.1: Track WARN count and show accumulated message
            warn_count = increment_warn_count(str(project_path))
            if warn_count >= 3:
                base_msg += CAN_CODE_WARN_ACCUMULATED.format(count=warn_count)
                try:
                    from clouvel.analytics import log_event
                    log_event("warn_accumulated", {"count": warn_count, "project": str(project_path)})
                except Exception:
                    pass
            _write_gate_status(project_path, "PASS", "")
            return [TextContent(type="text", text=base_msg)]
        else:
            # v3.1: Track WARN count for no-PRD case too
            warn_count = increment_warn_count(str(project_path))
            base_msg = CAN_CODE_WARN_NO_PRD_FREE.format(upgrade_hint="$49/yr")
            if warn_count >= 3:
                base_msg += CAN_CODE_WARN_ACCUMULATED.format(count=warn_count)
            _write_gate_status(project_path, "PASS", "WARN - no PRD (free)")
            return [TextContent(type="text", text=base_msg)]

    # PRO tier: BLOCK condition - No PRD OR no acceptance section
    if missing_critical or prd_sections_missing_critical:
        all_missing_critical = missing_critical + [PRD_SECTION_PREFIX.format(section=s) for s in prd_sections_missing_critical]
        found_list = detected_critical + detected_warn

        # Use Rich UI if available
        if HAS_RICH and render_can_code:
            output = render_can_code(
                status="BLOCK",
                title=f"Missing: {', '.join(all_missing_critical)}",
                found=found_list,
                missing=all_missing_critical,
                test_count=test_count,
                next_action=f"Fix: start(path=\"{path}\")",
                pro_hint="manager 10, ship 5",
            )
            _write_gate_status(project_path, "BLOCK", "Missing critical docs")
            return [TextContent(type="text", text=output)]

        # Fallback to plain text
        detected_list = "\n".join(f"- {d}" for d in found_list) if found_list else "None"
        _write_gate_status(project_path, "BLOCK", "Missing critical docs")
        return [TextContent(type="text", text=CAN_CODE_BLOCK_MISSING_DOCS.format(
            detected_list=detected_list,
            missing_list=chr(10).join(f'- {m}' for m in all_missing_critical),
            missing_items=', '.join(all_missing_critical)
        ))]

    # WARN condition: No architecture, 0 tests, etc.
    warn_count = len(missing_warn) + len(prd_sections_missing_warn) + (1 if test_count == 0 else 0)

    # Short summary format
    found_docs = detected_critical if detected_critical else []
    warn_items = missing_warn + [f"PRD.{s}" for s in prd_sections_missing_warn]
    if test_count == 0:
        warn_items.append(NO_TESTS)

    # PRD edit rule
    prd_rule = PRD_RULE_WARNING

    # Phase 1: PRD Quality Score (informational — does not change gate behavior)
    prd_quality_report = ""
    if prd_file:
        try:
            prd_content = prd_file.read_text(encoding="utf-8")
            scoring_result = score_prd(prd_content, level="standard")
            prd_quality_report = format_score_report(scoring_result)
        except Exception:
            pass  # Scoring failure should never block coding

    # Get context from Knowledge Base (session recovery)
    context_summary = _get_context_summary(project_path)

    # Use Rich UI if available
    if HAS_RICH and render_can_code:
        if warn_count > 0:
            output = render_can_code(
                status="WARN",
                title=f"Required: PRD ✓ | {test_count} tests",
                found=found_docs,
                missing=warn_items,
                test_count=test_count,
                next_action=None,
                pro_hint="ship auto-generates evidence & completion report",
            )
        else:
            output = render_can_code(
                status="PASS",
                title=f"Required: PRD ✓ | {test_count} tests | Ready to code",
                found=found_docs,
                missing=[],
                test_count=test_count,
                next_action=None,
                pro_hint=None,
            )
        _write_gate_status(project_path, "PASS", "")
        return [TextContent(type="text", text=output + "\n" + prd_rule + prd_quality_report + context_summary)]

    # Fallback to plain text
    found_docs_str = ", ".join(found_docs) if found_docs else "None"
    warn_summary = ", ".join(warn_items) if warn_items else "None"
    test_info = f" | {TEST_COUNT.format(count=test_count)}" if test_count > 0 else ""

    if warn_count > 0:
        _write_gate_status(project_path, "PASS", "")
        return [TextContent(type="text", text=CAN_CODE_PASS_WITH_WARN.format(
            warn_count=warn_count,
            found_docs=found_docs_str,
            test_info=test_info,
            warn_summary=warn_summary,
            prd_rule=prd_rule
        ) + prd_quality_report + context_summary)]
    else:
        base = CAN_CODE_PASS.format(
            found_docs=found_docs_str,
            test_info=test_info,
            prd_rule=prd_rule
        ) + prd_quality_report + context_summary
        # v3.2: Trial nudge for Pro-via-trial users
        if is_trial:
            if trial_remaining <= 1:
                base += CAN_CODE_TRIAL_NUDGE_7.format(remaining_days=trial_remaining)
            elif trial_remaining <= 3:
                base += CAN_CODE_TRIAL_NUDGE_5.format(remaining_days=trial_remaining)
            else:
                base += CAN_CODE_TRIAL_ACTIVE.format(remaining_days=trial_remaining)
        _write_gate_status(project_path, "PASS", "")
        return [TextContent(type="text", text=base)]


async def scan_docs(path: str) -> list[TextContent]:
    """Scan docs folder

    DEPRECATED: Use `can_code` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `scan_docs` will be removed in v2.0.
Use `can_code` instead - it includes all scan_docs functionality plus:
- PRD section validation
- Test file detection
- Knowledge Base context

**Migration**: Replace `scan_docs(path)` with `can_code(path)`

---

"""
    docs_path = Path(path)

    if not docs_path.exists():
        return [TextContent(type="text", text=SCAN_PATH_NOT_FOUND.format(path=path))]

    if not docs_path.is_dir():
        return [TextContent(type="text", text=SCAN_NOT_DIRECTORY.format(path=path))]

    files = []
    for f in sorted(docs_path.iterdir()):
        if f.is_file():
            stat = f.stat()
            files.append(f"{f.name} ({stat.st_size:,} bytes)")

    result = SCAN_RESULT.format(path=path, count=len(files))
    result += "\n".join(files)

    return [TextContent(type="text", text=deprecation_warning + result)]


async def analyze_docs(path: str) -> list[TextContent]:
    """Analyze docs folder

    DEPRECATED: Use `can_code` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `analyze_docs` will be removed in v2.0.
Use `can_code` instead - it includes all analyze_docs functionality plus:
- PRD section validation (acceptance criteria check)
- Test file detection
- Knowledge Base context loading

**Migration**: Replace `analyze_docs(path)` with `can_code(path)`

---

"""
    docs_path = Path(path)

    if not docs_path.exists():
        return [TextContent(type="text", text=ANALYZE_PATH_NOT_FOUND.format(path=path))]

    files = [f.name.lower() for f in docs_path.iterdir() if f.is_file()]
    detected = []
    missing = []

    for req in REQUIRED_DOCS:
        found = False
        for filename in files:
            for pattern in req["patterns"]:
                if re.search(pattern, filename, re.IGNORECASE):
                    detected.append(req["name"])
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(req["name"])

    critical_total = len([r for r in REQUIRED_DOCS if r["priority"] == "critical"])
    critical_found = len([r for r in REQUIRED_DOCS if r["priority"] == "critical" and r["name"] in detected])
    coverage = critical_found / critical_total if critical_total > 0 else 1.0

    result = ANALYZE_RESULT_HEADER.format(path=path, coverage=coverage)

    if detected:
        result += ANALYZE_FOUND_HEADER + "\n".join(f"- {d}" for d in detected) + "\n\n"

    if missing:
        result += ANALYZE_MISSING_HEADER + "\n".join(f"- {m}" for m in missing) + "\n\n"

    if not missing:
        result += ANALYZE_COMPLETE
    else:
        result += ANALYZE_INCOMPLETE.format(count=len(missing))

    return [TextContent(type="text", text=deprecation_warning + result)]


async def init_docs(path: str, project_name: str) -> list[TextContent]:
    """Initialize docs folder + generate templates

    DEPRECATED: Use `start(init=True)` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `init_docs` will be removed in v2.0.
Use `start` with init option instead:

**Migration**: `start(path, init=True)`

---

"""
    project_path = Path(path)
    docs_path = project_path / "docs"

    docs_path.mkdir(parents=True, exist_ok=True)

    templates = {
        "PRD.md": TEMPLATE_PRD.format(project_name=project_name, date=datetime.now().strftime('%Y-%m-%d')),
        "ARCHITECTURE.md": TEMPLATE_ARCHITECTURE.format(project_name=project_name),
        "API.md": TEMPLATE_API.format(project_name=project_name),
        "DATABASE.md": TEMPLATE_DATABASE.format(project_name=project_name),
        "VERIFICATION.md": TEMPLATE_VERIFICATION.format(project_name=project_name),
    }

    created = []
    for filename, content in templates.items():
        file_path = docs_path / filename
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
            created.append(filename)

    result = INIT_RESULT_HEADER.format(path=docs_path)
    if created:
        result += INIT_CREATED_HEADER + "\n".join(f"- {f}" for f in created) + "\n\n"
    else:
        result += INIT_ALREADY_EXISTS

    result += INIT_NEXT_STEPS

    return [TextContent(type="text", text=deprecation_warning + result)]
