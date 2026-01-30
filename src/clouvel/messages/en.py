# -*- coding: utf-8 -*-
"""English messages for Clouvel"""

# Document type names
DOC_NAMES = {
    "prd": "PRD",
    "architecture": "Architecture",
    "api_spec": "API Spec",
    "db_schema": "DB Schema",
    "verification": "Verification Plan",
}

# can_code messages
CAN_CODE_BLOCK_NO_DOCS = """⛔ BLOCK | No docs folder: {path} | Fix: start(path=".") | 💎 Pro: manager 10, ship 5

Why spec first? 10 min spec → 2 hours saved (no rework)
Next: Run start(path=".") to create PRD template
"""

CAN_CODE_BLOCK_MISSING_DOCS = """⛔ BLOCK | Missing: {missing_items} | Fix: start(path=".") | 💎 Pro: manager 10, ship 5

Found: {detected_list} | Missing (required): {missing_list}
Next: Write PRD with Acceptance Criteria section first
"""

CAN_CODE_PASS_WITH_WARN = "✅ PASS | ⚠️ WARN {warn_count} | Required: {found_docs} ✓{test_info} | Missing recommended: {warn_summary}{prd_rule}\n\n💎 Pro: `ship` auto-generates evidence & completion report → https://polar.sh/clouvel"

CAN_CODE_PASS = "✅ PASS | Required: {found_docs} ✓{test_info} | Ready to code{prd_rule}"

# v3.0: FREE tier messages (WARN instead of BLOCK)
CAN_CODE_PROJECT_LIMIT = """⚠️ PROJECT LIMIT | FREE tier: 1 project ({count}/{limit}) | 💎 Pro: Unlimited

You're using: {existing_project}

To use another project, upgrade to Pro:
→ https://polar.sh/clouvel (code: {upgrade_hint})

Or continue with your existing project.
"""

CAN_CODE_WARN_NO_DOCS_FREE = """⚠️ WARN | No docs folder: {path} | Recommended: start(path=".")

FREE tier: You can code, but PRD-first is recommended.
Why spec first? 10 min spec → 2 hours saved (no rework)

💎 Pro: Blocks coding until PRD exists (prevents rework)
→ https://polar.sh/clouvel (code: {upgrade_hint})
"""

CAN_CODE_WARN_NO_PRD_FREE = """⚠️ WARN | No PRD found | Recommended: start(path=".")

FREE tier: You can code, but PRD-first is recommended.
Why spec first? 10 min spec → 2 hours saved (no rework)

💎 Pro: Blocks coding + validates PRD sections + 8 managers
→ https://polar.sh/clouvel (code: {upgrade_hint})
"""

CAN_CODE_PASS_FREE = """✅ PASS | PRD exists ✓ | {test_count} tests | Ready to code (FREE tier)

{upgrade_hint}

💎 Pro: Full PRD validation + code blocking + 8 C-Level managers
→ https://polar.sh/clouvel
"""

PRD_RULE_WARNING = "\n\n⚠️ PRD Edit Rule: Do NOT modify PRD without explicit user request. If changes are needed, first propose (1) why changes are needed (2) benefits of improvement (3) specific changes, then proceed after approval."

# Test related
TEST_COUNT = "{count} tests"
NO_TESTS = "No Tests (⚠️ write tests before marking complete)"

# PRD section
PRD_SECTION_PREFIX = "PRD {section} section"

# scan_docs messages
SCAN_PATH_NOT_FOUND = "Path not found: {path}"
SCAN_NOT_DIRECTORY = "Not a directory: {path}"
SCAN_RESULT = "📁 {path}\nTotal {count} files\n\n"

# analyze_docs messages
ANALYZE_PATH_NOT_FOUND = "Path not found: {path}"
ANALYZE_RESULT_HEADER = "## Analysis Result: {path}\n\nCoverage: {coverage:.0%}\n\n"
ANALYZE_FOUND_HEADER = "### Found\n"
ANALYZE_MISSING_HEADER = "### Missing (Need to write)\n"
ANALYZE_COMPLETE = "✅ All required docs present. Ready for vibe coding.\n"
ANALYZE_INCOMPLETE = "⛔ Write {count} documents first, then start coding.\n"

# init_docs messages
INIT_RESULT_HEADER = "## docs folder initialized\n\nPath: `{path}`\n\n"
INIT_CREATED_HEADER = "### Created files\n"
INIT_ALREADY_EXISTS = "All files already exist.\n\n"
INIT_NEXT_STEPS = "### Next steps\n1. Start with PRD.md\n2. Use `get_prd_guide` tool for writing guidelines\n"

# Template contents
TEMPLATE_PRD = """# {project_name} PRD

> Created: {date}

## Summary

[TODO]

## Acceptance Criteria

- [ ] [Acceptance criterion 1]
- [ ] [Acceptance criterion 2]
- [ ] [Acceptance criterion 3]
"""

TEMPLATE_ARCHITECTURE = """# {project_name} Architecture

## System Structure

[TODO]
"""

TEMPLATE_API = """# {project_name} API Spec

## Endpoints

[TODO]
"""

TEMPLATE_DATABASE = """# {project_name} DB Schema

## Tables

[TODO]
"""

TEMPLATE_VERIFICATION = """# {project_name} Verification Plan

## Test Cases

[TODO]
"""
