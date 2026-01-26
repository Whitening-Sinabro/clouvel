# Clouvel Start Tool (Free)
# Project onboarding + PRD enforcement + interactive guide

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


def _get_trial_info() -> Optional[Dict[str, Any]]:
    """Get Trial status for Pro features via API."""
    try:
        from ..api_client import get_trial_status

        status = get_trial_status()

        if "error" in status:
            # API unavailable, show trial info anyway
            return {
                "has_trial": True,
                "message": """
---

💡 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test→verify→evidence |

→ Try now: `manager(context="your plan", topic="feature")`
→ Upgrade: https://polar.sh/clouvel
"""
            }

        features = status.get("features", {})

        # Check if any trial remaining
        has_trial = any(f.get("remaining", 0) > 0 for f in features.values())

        if has_trial:
            return {
                "has_trial": True,
                "features": features,
                "message": """
---

💡 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test→verify→evidence |

→ Try now: `manager(context="your plan", topic="feature")`
→ Upgrade: https://polar.sh/clouvel
"""
            }
        else:
            return {
                "has_trial": False,
                "message": "Trial exhausted. Upgrade to Pro: https://polar.sh/clouvel"
            }
    except Exception:
        # Fallback - show trial info
        return {
            "has_trial": True,
            "message": """
---

💡 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test→verify→evidence |

→ Try now: `manager(context="your plan", topic="feature")`
→ Upgrade: https://polar.sh/clouvel
"""
        }

# Project type detection patterns
PROJECT_TYPE_PATTERNS = {
    "chrome-ext": {
        "files": ["manifest.json"],
        "content_check": {"manifest.json": ["manifest_version", "permissions"]},
        "description": "Chrome Extension"
    },
    "discord-bot": {
        "dependencies": ["discord.js", "discord.py", "discordpy", "nextcord", "pycord"],
        "files": ["bot.py", "bot.js", "cogs/"],
        "description": "Discord Bot"
    },
    "cli": {
        "files": ["bin/", "cli.py", "cli.js", "__main__.py"],
        "dependencies": ["commander", "yargs", "click", "typer", "argparse"],
        "pyproject_check": ["[project.scripts]"],
        "description": "CLI Tool"
    },
    "landing-page": {
        "files": ["index.html"],
        "no_backend": True,
        "description": "Landing Page"
    },
    "api": {
        "files": ["server.py", "server.js", "app.py", "main.py", "index.js"],
        "dependencies": ["express", "fastapi", "flask", "django", "koa", "hono", "gin"],
        "description": "API Server"
    },
    "web-app": {
        "files": ["src/App.tsx", "src/App.jsx", "src/main.tsx", "pages/", "app/"],
        "dependencies": ["react", "vue", "svelte", "next", "nuxt", "angular"],
        "description": "Web Application"
    },
    "saas": {
        "files": ["src/App.tsx", "pages/pricing", "app/pricing", "stripe.ts", "checkout"],
        "dependencies": ["stripe", "@stripe/stripe-js", "polar-sh", "paddle"],
        "description": "SaaS MVP"
    }
}

# PRD questions by project type
PRD_QUESTIONS = {
    "chrome-ext": [
        {"section": "summary", "question": "What problem does this extension solve?", "example": "e.g., Skipping YouTube ads is tedious"},
        {"section": "target", "question": "Who are the main users?", "example": "e.g., Heavy YouTube users, office workers"},
        {"section": "features", "question": "What are the 3 core features?", "example": "e.g., 1. Auto-skip ads 2. Skip sponsor segments 3. Show stats"},
        {"section": "permissions", "question": "What permissions are required?", "example": "e.g., activeTab, storage"},
        {"section": "side_effects", "question": "What could affect existing features or other extensions?", "example": "e.g., Conflict with other ad blockers, site loading speed impact"},
        {"section": "out_of_scope", "question": "What features are excluded from this version?", "example": "e.g., Firefox support, dark mode"}
    ],
    "discord-bot": [
        {"section": "summary", "question": "What problem does this bot solve?", "example": "e.g., Server management is tedious"},
        {"section": "target", "question": "What type and size of servers will use this?", "example": "e.g., Gaming community, 100-500 members"},
        {"section": "commands", "question": "What are the 3-5 core commands?", "example": "e.g., /warn, /mute, /stats, /match"},
        {"section": "permissions", "question": "What bot permissions are required?", "example": "e.g., Manage Messages, Manage Members"},
        {"section": "side_effects", "question": "What could affect the server or other bots?", "example": "e.g., Permission conflict with other admin bots, log loss on message deletion"},
        {"section": "out_of_scope", "question": "What features are excluded from this version?", "example": "e.g., Voice features, dashboard"}
    ],
    "cli": [
        {"section": "summary", "question": "What problem does this CLI solve?", "example": "e.g., Project initialization is repetitive"},
        {"section": "target", "question": "Who are the main users?", "example": "e.g., Backend developers"},
        {"section": "commands", "question": "What are the 3-5 core commands?", "example": "e.g., init, run, build, deploy"},
        {"section": "options", "question": "What are the main options/flags?", "example": "e.g., --verbose, --config, --dry-run"},
        {"section": "side_effects", "question": "What could affect the system or existing files?", "example": "e.g., Overwriting config files, installing global packages"},
        {"section": "out_of_scope", "question": "What features are excluded from this version?", "example": "e.g., GUI, auto-update"}
    ],
    "landing-page": [
        {"section": "summary", "question": "What is the goal of this landing page?", "example": "e.g., Drive early bird signups for SaaS product"},
        {"section": "target", "question": "Who are the target visitors?", "example": "e.g., Startup founders, developers"},
        {"section": "cta", "question": "What is the primary CTA (conversion goal)?", "example": "e.g., Early bird signup, request demo"},
        {"section": "sections", "question": "What sections are needed?", "example": "e.g., Hero, Problem, Solution, Features, Pricing, FAQ"},
        {"section": "side_effects", "question": "What could affect existing marketing or branding?", "example": "e.g., Design inconsistency with existing homepage, SEO keyword conflict"},
        {"section": "metrics", "question": "What are the target metrics?", "example": "e.g., 5% conversion rate, bounce rate under 40%"}
    ],
    "api": [
        {"section": "summary", "question": "What problem does this API solve?", "example": "e.g., Frontend needs data access"},
        {"section": "clients", "question": "Who are the main API consumers?", "example": "e.g., Web frontend, mobile app"},
        {"section": "endpoints", "question": "What are the 5 core endpoints?", "example": "e.g., POST /auth/login, GET /users, POST /orders"},
        {"section": "auth", "question": "What is the authentication method?", "example": "e.g., JWT Bearer Token"},
        {"section": "side_effects", "question": "What could affect existing systems or data?", "example": "e.g., API version compatibility, DB schema changes, cache invalidation"},
        {"section": "out_of_scope", "question": "What is excluded from this version?", "example": "e.g., GraphQL, WebSocket"}
    ],
    "web-app": [
        {"section": "summary", "question": "What problem does this app solve?", "example": "e.g., Diet management is tedious"},
        {"section": "target", "question": "Who are the main users?", "example": "e.g., Office workers in their 20s-30s, dieters"},
        {"section": "features", "question": "What are the 3-5 core features?", "example": "e.g., 1. Diet logging 2. Calorie calculation 3. Weekly report"},
        {"section": "pages", "question": "What are the main pages/screens?", "example": "e.g., Login, Dashboard, Input, Stats"},
        {"section": "side_effects", "question": "What could affect existing screens or user experience?", "example": "e.g., UI layout changes, loading speed impact, existing data migration"},
        {"section": "out_of_scope", "question": "What features are excluded from this version?", "example": "e.g., Social features, i18n"}
    ],
    "saas": [
        {"section": "summary", "question": "What problem does this SaaS solve?", "example": "e.g., Building landing pages is difficult"},
        {"section": "target", "question": "Who are the target users?", "example": "e.g., Solo founders, small teams"},
        {"section": "features", "question": "What are the 3-5 core features?", "example": "e.g., 1. Drag-and-drop builder 2. Templates 3. Custom domain"},
        {"section": "pricing", "question": "What is the pricing structure? (Free/Pro etc.)", "example": "e.g., Free $0 (3 limit), Pro $15/mo (unlimited)"},
        {"section": "payment", "question": "What is the payment method?", "example": "e.g., Stripe subscription, annual/monthly billing"},
        {"section": "side_effects", "question": "What could affect existing users or payments?", "example": "e.g., Impact on existing plan users, data migration, payment flow changes"},
        {"section": "out_of_scope", "question": "What features are excluded from this version?", "example": "e.g., Team features, mobile app"}
    ],
    "generic": [
        {"section": "summary", "question": "What problem does this project solve?"},
        {"section": "target", "question": "Who are the main users/audience?"},
        {"section": "features", "question": "What are the 3-5 core features?"},
        {"section": "tech", "question": "What tech stack will you use?"},
        {"section": "side_effects", "question": "What could affect existing systems?", "example": "e.g., API compatibility, DB changes, performance impact"},
        {"section": "out_of_scope", "question": "What is excluded from this version?"}
    ]
}

# PRD template (generic fallback)
PRD_TEMPLATE = """# {project_name} PRD

> Created: {date}

---

## 1. Project Overview

### 1.1 Purpose
[Describe the problem this project solves]

### 1.2 Goals
- [ ] Core goal 1
- [ ] Core goal 2
- [ ] Core goal 3

### 1.3 Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| ... | ... | ... |

---

## 2. Functional Requirements

### 2.1 Core Features (Must Have)
1. **Feature 1**: Description
2. **Feature 2**: Description

### 2.2 Additional Features (Nice to Have)
1. **Feature 1**: Description

### 2.3 Out of Scope
- Items excluded from this version

---

## 3. Technical Spec

### 3.1 Tech Stack
- Frontend:
- Backend:
- Database:
- Infra:

### 3.2 Architecture
[Architecture diagram or description]

### 3.3 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/... | ... |

---

## 4. Data Model

### 4.1 Main Entities
```
Entity1:
  - field1: type
  - field2: type

Entity2:
  - field1: type
```

### 4.2 Relationships
[ERD or relationship description]

---

## 5. UI/UX

### 5.1 Main Screens
1. **Screen 1**: Description
2. **Screen 2**: Description

### 5.2 User Flow
1. User does ...
2. System does ...

---

## 6. Error Handling

### 6.1 Expected Error Scenarios
| Scenario | Error Code | User Message |
|----------|------------|--------------|
| ... | ... | ... |

### 6.2 Recovery Strategy
- Strategy 1: ...

---

## 7. Security Requirements

### 7.1 Authentication/Authorization
- Auth method:
- Permission structure:

### 7.2 Data Protection
- Encryption:
- Sensitive data handling:

---

## 8. Test Plan

### 8.1 Test Scope
- [ ] Unit Test
- [ ] Integration Test
- [ ] E2E Test

### 8.2 Test Scenarios
| Scenario | Expected Result | Priority |
|----------|-----------------|----------|
| ... | ... | ... |

---

## 9. Timeline

### 9.1 Milestones
| Phase | Content | Expected Completion |
|-------|---------|---------------------|
| Phase 1 | ... | ... |

---

## 10. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | {date} | ... | Initial draft |
"""


def _detect_project_type(project_path: Path) -> Dict[str, Any]:
    """
    Auto-detect project type.
    Analyzes file structure, dependencies, and config files.
    """
    detected = {
        "type": "generic",
        "confidence": 0,
        "signals": [],
        "description": "Generic Project"
    }

    # 의존성 파일 읽기
    dependencies = set()

    # package.json
    pkg_json = project_path / "package.json"
    if pkg_json.exists():
        try:
            pkg_data = json.loads(pkg_json.read_text(encoding="utf-8"))
            deps = pkg_data.get("dependencies", {})
            dev_deps = pkg_data.get("devDependencies", {})
            dependencies.update(deps.keys())
            dependencies.update(dev_deps.keys())
        except:
            pass

    # pyproject.toml / requirements.txt
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # 간단한 파싱 (정확하진 않지만 충분)
            for line in content.split("\n"):
                if ">=" in line or "==" in line:
                    dep = line.split(">=")[0].split("==")[0].strip().strip('"').strip("'")
                    if dep:
                        dependencies.add(dep.lower())
        except:
            pass

    requirements = project_path / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text(encoding="utf-8").split("\n"):
                dep = line.split(">=")[0].split("==")[0].split("[")[0].strip()
                if dep and not dep.startswith("#"):
                    dependencies.add(dep.lower())
        except:
            pass

    # 타입별 점수 계산
    scores = {}

    for ptype, patterns in PROJECT_TYPE_PATTERNS.items():
        score = 0
        signals = []

        # File existence check
        if "files" in patterns:
            for f in patterns["files"]:
                if (project_path / f).exists():
                    score += 30
                    signals.append(f"File found: {f}")

        # Dependency check
        if "dependencies" in patterns:
            for dep in patterns["dependencies"]:
                if dep.lower() in dependencies:
                    score += 40
                    signals.append(f"Dependency found: {dep}")

        # manifest.json content check (Chrome Extension)
        if "content_check" in patterns:
            for file, keywords in patterns["content_check"].items():
                file_path = project_path / file
                if file_path.exists():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        for kw in keywords:
                            if kw in content:
                                score += 25
                                signals.append(f"Found '{kw}' in {file}")
                    except:
                        pass

        # landing-page: no backend check
        if patterns.get("no_backend"):
            has_backend = any((project_path / f).exists() for f in ["server.py", "server.js", "app.py", "main.py"])
            if not has_backend and (project_path / "index.html").exists():
                score += 20
                signals.append("No backend files, only index.html exists")

        if score > 0:
            scores[ptype] = {"score": score, "signals": signals}

    # 최고 점수 타입 선택
    if scores:
        best_type = max(scores, key=lambda x: scores[x]["score"])
        best_score = scores[best_type]

        if best_score["score"] >= 30:  # 최소 신뢰도
            detected["type"] = best_type
            detected["confidence"] = min(best_score["score"], 100)
            detected["signals"] = best_score["signals"]
            detected["description"] = PROJECT_TYPE_PATTERNS[best_type]["description"]

    return detected


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
            "message": f"✅ Docs folder initialized: {docs_path}\n\nCreated: {', '.join(created) if created else 'None (already exist)'}\n\nNext: Fill in PRD.md sections"
        }

    # === Option: --template (Get PRD template) ===
    if template:
        name = project_name or project_path.name
        today = datetime.now().strftime('%Y-%m-%d')

        # Try loading from templates folder
        templates_base = Path(__file__).parent.parent / "templates"
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

        return {
            "status": "TEMPLATE",
            "template": template,
            "layout": layout,
            "content": content,
            "message": f"# {template}/{layout} Template\n\n```markdown\n{content}\n```\n\nSave to: `docs/PRD.md`"
        }

    result = {
        "status": "UNKNOWN",
        "project_path": str(project_path),
        "docs_exists": False,
        "prd_exists": False,
        "prd_valid": False,
        "created_files": [],
        "next_steps": [],
        "message": ""
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
            result["message"] = "✅ PRD is ready. You can start coding."
            result["next_steps"] = [
                "1. Check coding eligibility with `can_code` tool",
                "2. If needed, create detailed execution plan with `plan` tool",
                "3. Start coding!"
            ]
            result["prd_summary"] = validation["summary"]
        else:
            result["status"] = "INCOMPLETE"
            result["message"] = "⚠️ PRD exists but some sections are empty."
            result["missing_sections"] = validation["missing_sections"]
            result["next_steps"] = [
                f"1. Write the following PRD sections: {', '.join(validation['missing_sections'])}",
                "2. Run `start` again after completion"
            ]
    else:
        # No PRD -> Start interactive PRD writing guide
        result["status"] = "NEED_PRD"
        result["message"] = f"📝 PRD is required. Detected as {detected['description']} project."

        # Return type-specific questions
        questions = PRD_QUESTIONS.get(detected["type"], PRD_QUESTIONS["generic"])
        result["prd_guide"] = {
            "detected_type": detected["type"],
            "confidence": detected["confidence"],
            "signals": detected["signals"],
            "template": detected["type"],
            "questions": questions,
            "instruction": f"""
## 🎯 PRD Writing Guide

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


def _validate_prd(content: str) -> Dict[str, Any]:
    """
    Validate PRD content.

    Required sections:
    - Project Overview (Purpose, Goals)
    - Functional Requirements

    Recommended sections:
    - Technical Spec
    - Data Model
    - Test Plan
    """
    # Check for both Korean and English section names
    required_sections = [
        (["Project Overview", "프로젝트 개요"], ["Purpose", "Goals", "목적", "목표"]),
        (["Functional Requirements", "기능 요구사항"], ["Core Features", "핵심 기능"]),
    ]

    recommended_sections = [
        ["Technical Spec", "기술 스펙"],
        ["Data Model", "데이터 모델"],
        ["Test Plan", "테스트 계획"]
    ]

    missing_sections = []
    summary = {
        "sections_found": [],
        "has_goals": False,
        "has_features": False
    }

    # Required section check
    for section_names, subsection_names in required_sections:
        section_found = any(name in content for name in section_names)
        if not section_found:
            missing_sections.append(section_names[0])  # Use English name
        else:
            summary["sections_found"].append(section_names[0])

            # Check if content exists (not just template placeholder)
            for sub in subsection_names:
                if sub in content:
                    # Placeholder check
                    if sub in ["Purpose", "목적"] and ("[Describe the problem" in content or "[이 프로젝트가 해결하려는 문제를 작성하세요]" in content):
                        missing_sections.append(f"{section_names[0]} > {sub}")
                    elif sub in ["Goals", "목표"] and ("Core goal 1" in content or "핵심 목표 1" in content):
                        pass  # Goals exist, OK
                    else:
                        if section_names[0] in ["Project Overview", "프로젝트 개요"]:
                            summary["has_goals"] = True

    # Functional requirements check
    if any(name in content for name in ["Functional Requirements", "기능 요구사항"]):
        if "**Feature 1**: Description" not in content and "**기능 1**: 설명" not in content:
            summary["has_features"] = True

    # Recommended section check
    for section_names in recommended_sections:
        if any(name in content for name in section_names):
            summary["sections_found"].append(section_names[0])

    is_valid = len(missing_sections) == 0 and summary["has_goals"]

    return {
        "is_valid": is_valid,
        "missing_sections": missing_sections,
        "summary": summary
    }


def save_prd(
    path: str,
    content: str,
    project_name: str = "",
    project_type: str = ""
) -> Dict[str, Any]:
    """
    Save PRD content.

    Save PRD written by Claude through conversation with user.

    Args:
        path: Project root path
        content: PRD content (markdown)
        project_name: Project name (optional, used in header)
        project_type: Project type (optional, for metadata)

    Returns:
        Save result
    """
    from datetime import datetime

    project_path = Path(path).resolve()
    docs_path = project_path / "docs"
    prd_path = docs_path / "PRD.md"

    result = {
        "status": "UNKNOWN",
        "prd_path": str(prd_path),
        "message": ""
    }

    # Create docs folder
    if not docs_path.exists():
        try:
            docs_path.mkdir(parents=True)
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"Failed to create docs folder: {e}"
            return result

    # Add PRD header (if missing)
    if not content.strip().startswith("#"):
        today = datetime.now().strftime("%Y-%m-%d")
        name = project_name or project_path.name
        header = f"# {name} PRD\n\n> Created: {today}\n\n---\n\n"
        content = header + content

    # Save
    try:
        prd_path.write_text(content, encoding="utf-8")
        result["status"] = "SAVED"
        result["message"] = f"✅ PRD saved: {prd_path}"

        # Validate
        validation = _validate_prd(content)
        result["validation"] = validation

        if validation["is_valid"]:
            result["next_steps"] = [
                "PRD saved! You can start coding now.",
                "Check with `can_code` tool or start coding directly."
            ]
        else:
            result["next_steps"] = [
                f"PRD saved but some sections are incomplete: {', '.join(validation['missing_sections'])}",
                "Consider completing the PRD if needed."
            ]

    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Failed to save PRD: {e}"

    return result


def get_prd_questions(project_type: str = "generic") -> Dict[str, Any]:
    """
    Return PRD writing questions for a specific project type.

    Args:
        project_type: Project type (web-app, api, cli, chrome-ext, discord-bot, landing-page, generic)

    Returns:
        Questions list and guide
    """
    if project_type not in PRD_QUESTIONS:
        project_type = "generic"

    questions = PRD_QUESTIONS[project_type]
    description = PROJECT_TYPE_PATTERNS.get(project_type, {}).get("description", project_type)

    return {
        "project_type": project_type,
        "description": description,
        "questions": questions,
        "usage": f"""
## PRD Writing Questions ({description})

Ask the user the following questions:

{chr(10).join([f"{i+1}. **{q['section']}**: {q['question']}" for i, q in enumerate(questions)])}

After collecting all answers, write the PRD and save it with `save_prd` tool.
"""
    }


# Simple version (can be used instead of can_code)
def quick_start(path: str) -> str:
    """
    Quick start - Check PRD existence and return guidance message
    """
    result = start(path)

    if result["status"] == "READY":
        return f"✅ {result['project_name']} project ready!\n\nStart coding."
    elif result["status"] == "NEED_PRD":
        guide = result.get("prd_guide", {})
        return f"📝 PRD is required.\n\n{guide.get('instruction', '')}"
    elif result["status"] == "INCOMPLETE":
        return f"⚠️ PRD incomplete\n\nMissing sections: {', '.join(result.get('missing_sections', []))}\n\nNext steps:\n" + "\n".join(result["next_steps"])
    else:
        return f"❌ Error: {result['message']}"
