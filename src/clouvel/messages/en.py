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
CAN_CODE_BLOCK_NO_DOCS = """
# ⛔ BLOCK: No coding allowed

## Reason
docs folder not found: `{path}`

## What to do now
1. Create a `docs` folder
2. Write a PRD (Product Requirements Document) first
3. Use `get_prd_template` tool to generate a template

## Why?
Coding without PRD leads to:
- Unclear requirements → Rework
- Missing edge cases → Bugs
- Team misalignment → Conflicts

**Spec first, code later.**

Tell the user you'll help them write a PRD.
"""

CAN_CODE_BLOCK_MISSING_DOCS = """
# ⛔ BLOCK: No coding allowed

## Current Status
✅ Found:
{detected_list}

❌ Missing (Required - BLOCK):
{missing_list}

## What to do now
Do NOT write code. Instead:

1. Write the missing documents/sections first
2. **PRD must have an Acceptance Criteria section**
3. Use `get_prd_guide` tool for writing guidelines
4. Use `get_prd_template` tool to generate a template

## Message for user
"Before writing code, we need to prepare the documentation.
Missing required items: {missing_items}
Would you like me to help you write the PRD?"

**Do NOT write any code. Help with documentation instead.**
"""

CAN_CODE_PASS_WITH_WARN = "✅ PASS | ⚠️ WARN {warn_count} | Required: {found_docs} ✓{test_info} | Missing recommended: {warn_summary}{prd_rule}"

CAN_CODE_PASS = "✅ PASS | Required: {found_docs} ✓{test_info} | Ready to code{prd_rule}"

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
