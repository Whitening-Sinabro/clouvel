# Clouvel Start Tool - Project Type Detection
# Auto-detect project type from file structure and dependencies

import json
from pathlib import Path
from typing import Dict, Any


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
        except (OSError, json.JSONDecodeError, ValueError):
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
        except (OSError, UnicodeDecodeError):
            pass

    requirements = project_path / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text(encoding="utf-8").split("\n"):
                dep = line.split(">=")[0].split("==")[0].split("[")[0].strip()
                if dep and not dep.startswith("#"):
                    dependencies.add(dep.lower())
        except (OSError, UnicodeDecodeError):
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
                    except (OSError, UnicodeDecodeError):
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
