# -*- coding: utf-8 -*-
"""Core tools: can_code, scan_docs, analyze_docs, init_docs"""

import re
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

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
                lines.append(f"- **[{d.get('category', 'general')}]** {d.get('decision', '')[:80]}")
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


async def can_code(path: str) -> list[TextContent]:
    """Check if coding is allowed - core feature (B4: quality gate extension)"""
    docs_path = Path(path)
    project_path = docs_path.parent if docs_path.name == "docs" else docs_path

    if not docs_path.exists():
        return [TextContent(type="text", text=CAN_CODE_BLOCK_NO_DOCS.format(path=path))]

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

    # BLOCK condition: No PRD OR no acceptance section
    if missing_critical or prd_sections_missing_critical:
        all_missing_critical = missing_critical + [PRD_SECTION_PREFIX.format(section=s) for s in prd_sections_missing_critical]
        detected_list = "\n".join(f"- {d}" for d in detected_critical + detected_warn) if (detected_critical or detected_warn) else "None"

        return [TextContent(type="text", text=CAN_CODE_BLOCK_MISSING_DOCS.format(
            detected_list=detected_list,
            missing_list=chr(10).join(f'- {m}' for m in all_missing_critical),
            missing_items=', '.join(all_missing_critical)
        ))]

    # WARN condition: No architecture, 0 tests, etc.
    warn_count = len(missing_warn) + len(prd_sections_missing_warn) + (1 if test_count == 0 else 0)

    # Short summary format
    found_docs = ", ".join(detected_critical) if detected_critical else "None"
    warn_items = missing_warn + [f"PRD.{s}" for s in prd_sections_missing_warn]
    if test_count == 0:
        warn_items.append(NO_TESTS)
    warn_summary = ", ".join(warn_items) if warn_items else "None"

    test_info = f" | {TEST_COUNT.format(count=test_count)}" if test_count > 0 else ""

    # PRD edit rule
    prd_rule = PRD_RULE_WARNING

    # Get context from Knowledge Base (session recovery)
    context_summary = _get_context_summary(project_path)

    if warn_count > 0:
        return [TextContent(type="text", text=CAN_CODE_PASS_WITH_WARN.format(
            warn_count=warn_count,
            found_docs=found_docs,
            test_info=test_info,
            warn_summary=warn_summary,
            prd_rule=prd_rule
        ) + context_summary)]
    else:
        return [TextContent(type="text", text=CAN_CODE_PASS.format(
            found_docs=found_docs,
            test_info=test_info,
            prd_rule=prd_rule
        ) + context_summary)]


async def scan_docs(path: str) -> list[TextContent]:
    """Scan docs folder"""
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

    return [TextContent(type="text", text=result)]


async def analyze_docs(path: str) -> list[TextContent]:
    """Analyze docs folder"""
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

    return [TextContent(type="text", text=result)]


async def init_docs(path: str, project_name: str) -> list[TextContent]:
    """Initialize docs folder + generate templates"""
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

    return [TextContent(type="text", text=result)]
