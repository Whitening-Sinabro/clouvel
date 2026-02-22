# Clouvel Start Tool - Core Functions (Free)
# Project onboarding + PRD enforcement + interactive guide

from pathlib import Path
from typing import Dict, Any

from .detect import (
    _detect_project_type,
    PROJECT_TYPE_PATTERNS,
    PRD_QUESTIONS,
)
from .prd import (
    _get_trial_info,
    _validate_prd,
)


def start(
    path: str,
    project_name: str = "",
    project_type: str = "",
    template: str = "",
    layout: str = "standard",
    guide: bool = False,
    init: bool = False
) -> Dict[str, Any]:
    """
    Start project onboarding.

    Flow:
    1. Auto-detect project type (or user-specified)
    2. Check/create docs folder
    3. Check if PRD.md exists
    4. If not -> Return type-specific questions (interactive PRD writing guide)
    5. If yes -> Validate structure + guide next steps

    Args:
        path: Project root path
        project_name: Project name (optional)
        project_type: Force project type (optional)
        template: Get PRD template (replaces get_prd_template)
        layout: Template layout - lite, standard, detailed (default: standard)
        guide: Show PRD writing guide (replaces get_prd_guide)
        init: Initialize docs folder with templates (replaces init_docs)

    Returns:
        Onboarding result and next step guide (or PRD writing questions)
    """
    from datetime import datetime

    project_path = Path(path).resolve()
    docs_path = project_path / "docs"
    prd_path = docs_path / "PRD.md"

    # === Option: --guide (PRD writing guide) ===
    if guide:
        return {
            "status": "GUIDE",
            "message": """# PRD Writing Guide

## Why PRD?
- Clarify what to build before coding
- Align understanding between team/AI
- Prevent "why did we do it this way?" later

## Writing Order

### Step 1: Core first
1. **One-line Summary** - If you can't write it, it's not clear
2. **Core Principles** - 3 things that never change

### Step 2: Input/Output
3. **Input Spec** - What comes in
4. **Output Spec** - What goes out

### Step 3: Exception handling
5. **Error Cases** - Everything that could fail

### Step 4: Details
6. **API** - Endpoint list
7. **DB** - Table structure
8. **State Machine** - If applicable

### Step 5: Verification
9. **Test Plan** - How to verify

## Tips
- Don't try to write perfectly. Just write.
- You can update while coding.
- But never build features not in the PRD.
"""
        }

    # === Option: --init (Initialize docs folder) ===
    if init:
        docs_path.mkdir(parents=True, exist_ok=True)
        name = project_name or project_path.name
        today = datetime.now().strftime('%Y-%m-%d')

        templates_to_create = {
            "PRD.md": f"""# {name} PRD

> Created: {today}

---

## 1. Project Overview

### 1.1 Purpose
[Describe the problem this project solves]

### 1.2 Goals
- [ ] Core goal 1
- [ ] Core goal 2

---

## 2. Functional Requirements

### 2.1 Core Features
1. **Feature 1**: Description

### 2.2 Out of Scope
- Items excluded from this version

---

## 3. Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
""",
            "ARCHITECTURE.md": f"# {name} Architecture\n\n[Architecture description]\n",
            "API.md": f"# {name} API\n\n| Method | Endpoint | Description |\n|--------|----------|-------------|\n| GET | /api/... | ... |\n",
        }

        created = []
        for filename, content in templates_to_create.items():
            file_path = docs_path / filename
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
                created.append(filename)

        return {
            "status": "INITIALIZED",
            "docs_path": str(docs_path),
            "created_files": created,
            "message": f"\u2705 Docs folder initialized: {docs_path}\n\nCreated: {', '.join(created) if created else 'None (already exist)'}\n\nNext: Fill in PRD.md sections"
        }

    # === Option: --template (Get PRD template) ===
    if template:
        name = project_name or project_path.name
        today = datetime.now().strftime('%Y-%m-%d')

        # Handle "minimal" template specially - fastest way to unblock
        if template == "minimal" or layout == "minimal":
            docs_path.mkdir(parents=True, exist_ok=True)
            minimal_content = f"""# {name} PRD

> Created: {today}

## Summary

[What are you building? 1-2 sentences]

## Acceptance Criteria

- [ ] User can...
- [ ] System should...
- [ ] Test: ...

---

_Minimal PRD created by Clouvel. Expand sections as needed._
"""
            prd_file = docs_path / "PRD.md"
            if not prd_file.exists():
                prd_file.write_text(minimal_content, encoding='utf-8')
                return {
                    "status": "MINIMAL_CREATED",
                    "prd_path": str(prd_file),
                    "message": f"""\u2705 Minimal PRD created: {prd_file}

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
  PRD is ready! You can now code.

  Next steps:
  1. Fill in Summary (1-2 sentences)
  2. Fill in Acceptance Criteria
  3. Run can_code to verify
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

\U0001f4a1 Tip: Expand PRD with more sections later:
\u2192 start(path=".", template="web-app", layout="standard")
"""
                }
            else:
                return {
                    "status": "PRD_EXISTS",
                    "prd_path": str(prd_file),
                    "message": f"\u26a0\ufe0f PRD already exists: {prd_file}\n\nRun can_code to check if you can proceed."
                }

        # Check layout access (Free=lite+minimal, Pro=all)
        from ...licensing.core import is_developer
        from ...licensing.validation import load_license_cache
        from ...licensing.projects import FREE_LAYOUTS

        is_pro = is_developer()
        if not is_pro:
            cached = load_license_cache()
            is_pro = cached is not None and cached.get("tier") is not None

        requested_layout = layout
        upsell_message = ""

        if not is_pro and layout not in FREE_LAYOUTS:
            # Free user requesting Pro layout -> fallback to lite
            layout = "lite"
            upsell_message = f"""
---

\U0001f48e **Pro Template Requested**

You requested `{requested_layout}` layout, but Free tier only includes `lite` and `minimal`.

**What you're missing in {requested_layout}:**
- Input/Output Specifications (AI\uac00 \uc815\ud655\ud788 \uc774\ud574)
- State Machine diagrams (\ubcf5\uc7a1\ud55c \ud50c\ub85c\uc6b0 \uba85\uc2dc)
- Error Cases \uc804\uccb4 \uc5f4\uac70 (\ud560\ub8e8\uc2dc\ub124\uc774\uc158 \ubc29\uc9c0)
- Test Scenarios (\uac80\uc99d \uae30\uc900)
- Definition of Done (\uc644\ub8cc \uae30\uc900)

\u2192 Upgrade to Pro: https://polar.sh/clouvel
\u2192 Annual: $49/yr \u2014 Early Adopter Pricing

---
"""

        # Try loading from templates folder
        templates_base = Path(__file__).parent.parent.parent / "templates"
        template_path = templates_base / template / f"{layout}.md"

        if template_path.exists():
            content = template_path.read_text(encoding="utf-8")
            content = content.replace("{PROJECT_NAME}", name)
            content = content.replace("{DATE}", today)
        else:
            # Fallback generic template
            content = f"""# {name} PRD

> This document is law. If it's not here, don't build it.
> Created: {today}

---

## 1. One-line Summary
[Write here]

---

## 2. Core Principles
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

---

## 3. Input Spec
### 3.1 [Input Type 1]
- Format:
- Required fields:
- Constraints:

---

## 4. Output Spec
### 4.1 [Output Type 1]
- Format:
- Fields:
- Example:

---

## 5. Error Cases
| Situation | Handling | Error Code |
|-----------|----------|------------|
| [Situation1] | [Method] | [Code] |

---

## 6. Acceptance Criteria
- [ ] [Test case 1]
- [ ] [Test case 2]
"""

        result = {
            "status": "TEMPLATE",
            "template": template,
            "layout": layout,
            "requested_layout": requested_layout,
            "is_pro": is_pro,
            "content": content,
            "message": f"# {template}/{layout} Template\n\n```markdown\n{content}\n```\n\nSave to: `docs/PRD.md`"
        }

        # Add upsell message if Free user requested Pro layout
        if upsell_message:
            result["upsell"] = upsell_message
            result["message"] = upsell_message + result["message"]

        return result

    # === Check project limit (Free = 1 active project) ===
    from ...licensing.projects import register_project

    project_reg = register_project(str(project_path))

    if not project_reg["allowed"]:
        # Use the message from register_project (Pain Point #1)
        custom_message = project_reg.get("message", "")
        active_projects = project_reg.get("active_projects", [])
        active_name = Path(active_projects[0]).name if active_projects else "Unknown"

        return {
            "status": "PROJECT_LIMIT",
            "project_path": str(project_path),
            "count": project_reg["count"],
            "limit": project_reg["limit"],
            "active_projects": active_projects,
            "active_project_name": active_name,
            "needs_archive": project_reg.get("needs_archive", False),
            "message": custom_message or f"""
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
  \U0001f512 Active Project Limit ({project_reg['count']}/{project_reg['limit']})

  Currently active: {active_name}

  Free \ud50c\ub79c\uc740 \ud55c \ubc88\uc5d0 \ud558\ub098\uc758 \ud504\ub85c\uc81d\ud2b8\uc5d0\ub9cc \uc9d1\uc911\ud560 \uc218 \uc788\uc5b4\uc694.

  \uc120\ud0dd\uc9c0:
  1\ufe0f\u20e3 \uae30\uc874 \ud504\ub85c\uc81d\ud2b8 \uc544\uce74\uc774\ube0c \ud6c4 \uc0c8 \ud504\ub85c\uc81d\ud2b8 \uc2dc\uc791
  2\ufe0f\u20e3 Pro\ub85c \uc5c5\uadf8\ub808\uc774\ub4dc\ud558\uc5ec \ubb34\uc81c\ud55c \ud504\ub85c\uc81d\ud2b8

  \U0001f4a1 Pro: $7.99/mo - \ubb34\uc81c\ud55c \ud504\ub85c\uc81d\ud2b8 + 8\uba85 \ub9e4\ub2c8\uc800 + KB
  \u2192 \uccab 7\uc77c \ubb34\ub8cc \uccb4\ud5d8: https://polar.sh/clouvel
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
""",
            "upsell": True,
            "actions": [
                {
                    "label": f"Archive '{active_name}' and start new",
                    "command": "archive_project",
                    "args": {"path": active_projects[0]} if active_projects else {}
                },
                {
                    "label": "Upgrade to Pro",
                    "command": "upgrade_pro",
                    "url": "https://polar.sh/clouvel"
                }
            ]
        }

    result = {
        "status": "UNKNOWN",
        "project_path": str(project_path),
        "docs_exists": False,
        "prd_exists": False,
        "prd_valid": False,
        "created_files": [],
        "next_steps": [],
        "message": "",
        "project_count": project_reg["count"],
        "project_limit": project_reg["limit"],
        "is_new_project": project_reg["is_new"]
    }

    # Infer project name
    if not project_name:
        project_name = project_path.name

    result["project_name"] = project_name

    # Detect project type
    if project_type and project_type in PRD_QUESTIONS:
        detected = {
            "type": project_type,
            "confidence": 100,
            "signals": ["User specified"],
            "description": PROJECT_TYPE_PATTERNS.get(project_type, {}).get("description", project_type)
        }
    else:
        detected = _detect_project_type(project_path)

    result["project_type"] = detected

    # 1. Check/create docs folder
    if not docs_path.exists():
        try:
            docs_path.mkdir(parents=True)
            result["created_files"].append("docs/")
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"Failed to create docs folder: {e}"
            return result

    result["docs_exists"] = True

    # 2. Check PRD.md
    if prd_path.exists():
        result["prd_exists"] = True

        # Validate PRD content
        prd_content = prd_path.read_text(encoding="utf-8")
        validation = _validate_prd(prd_content)

        if validation["is_valid"]:
            result["status"] = "READY"
            result["prd_valid"] = True
            result["message"] = "\u2705 PRD is ready. You can start coding."
            result["next_steps"] = [
                "1. Check coding eligibility with `can_code` tool",
                "2. If needed, create detailed execution plan with `plan` tool",
                "3. Start coding!"
            ]
            result["prd_summary"] = validation["summary"]
        else:
            result["status"] = "INCOMPLETE"
            result["message"] = "\u26a0\ufe0f PRD exists but some sections are empty."
            result["missing_sections"] = validation["missing_sections"]
            result["next_steps"] = [
                f"1. Write the following PRD sections: {', '.join(validation['missing_sections'])}",
                "2. Run `start` again after completion"
            ]
    else:
        # No PRD -> Start interactive PRD writing guide
        result["status"] = "NEED_PRD"
        result["message"] = f"\U0001f4dd PRD is required. Detected as {detected['description']} project."

        # Return type-specific questions
        questions = PRD_QUESTIONS.get(detected["type"], PRD_QUESTIONS["generic"])
        result["prd_guide"] = {
            "detected_type": detected["type"],
            "confidence": detected["confidence"],
            "signals": detected["signals"],
            "template": detected["type"],
            "questions": questions,
            "instruction": f"""
## \U0001f3af PRD Writing Guide

**Detected project type**: {detected['description']} ({detected['type']})
**Confidence**: {detected['confidence']}%

### Instructions for Claude

Ask the user the following questions **interactively**:

{chr(10).join([f"{i+1}. **{q['section']}**: {q['question']}" + (f" ({q.get('example', '')})" if q.get('example') else "") for i, q in enumerate(questions)])}

### How to proceed

1. Ask questions one at a time or group related ones
2. Collect user answers
3. When all answers are collected, save PRD with `save_prd` tool
4. Template: `{detected['type']}` / Layout: `standard` recommended

### Example conversation

"Hello! Looks like a {detected['description']} project.
Let's write the PRD together. I'll ask a few questions.

**{questions[0]['question']}**
{questions[0].get('example', '')}"
"""
        }

        result["next_steps"] = [
            "1. Answer the questions above to write PRD",
            "2. Save with `save_prd` tool when complete",
            "3. Run `start` again to validate"
        ]

        # Add Pro template upsell for specialized project types
        pro_template_types = ["saas", "api", "cli", "chrome-ext", "discord-bot", "landing-page"]
        if detected["type"] in pro_template_types:
            pro_features = {
                "saas": "Pricing tiers, Aha Moment, SaaS metrics, Payment flow state machine",
                "api": "TypeScript interfaces, Rate limits per tier, JWT specs, Error codes",
                "cli": "Signal handling, Shell completion, Config priority, Exit codes",
                "chrome-ext": "MV3 manifest, Permission matrix, CSP, Storage schema",
                "discord-bot": "Slash command specs, Intents, Embed templates, Rate limits",
                "landing-page": "Conversion funnel, A/B testing, SEO meta, Performance budget"
            }
            result["pro_template_hint"] = f"""
---

\U0001f48e **Pro Template Available for {detected['description']}**

Free `lite` template: ~150 lines (basic structure)
Pro `detailed` template: ~700+ lines includes:
- {pro_features.get(detected['type'], 'Advanced specifications')}
- Input/Output Specifications (AI\uac00 \uc815\ud655\ud788 \uc774\ud574)
- Error Cases \uc804\uccb4 \uc5f4\uac70 (\ud560\ub8e8\uc2dc\ub124\uc774\uc158 \ubc29\uc9c0)
- Test Scenarios & Definition of Done

\u2192 Upgrade: https://polar.sh/clouvel ($49/yr \u2014 Early Adopter Pricing)
"""

    # Check additional docs files
    optional_docs = {
        "ARCHITECTURE.md": "Architecture document",
        "API.md": "API document",
        "CHANGELOG.md": "Change history"
    }

    result["optional_docs"] = {}
    for doc, desc in optional_docs.items():
        doc_path = docs_path / doc
        result["optional_docs"][doc] = {
            "exists": doc_path.exists(),
            "description": desc
        }

    # Add Trial info
    trial_info = _get_trial_info()
    if trial_info:
        result["trial_info"] = trial_info

    return result


# Simple version (can be used instead of can_code)
def quick_start(path: str) -> str:
    """
    Quick start - Check PRD existence and return guidance message
    """
    result = start(path)

    if result["status"] == "READY":
        return f"\u2705 {result['project_name']} project ready!\n\nStart coding."
    elif result["status"] == "NEED_PRD":
        guide = result.get("prd_guide", {})
        return f"\U0001f4dd PRD is required.\n\n{guide.get('instruction', '')}"
    elif result["status"] == "INCOMPLETE":
        return f"\u26a0\ufe0f PRD incomplete\n\nMissing sections: {', '.join(result.get('missing_sections', []))}\n\nNext steps:\n" + "\n".join(result["next_steps"])
    else:
        return f"\u274c Error: {result['message']}"
