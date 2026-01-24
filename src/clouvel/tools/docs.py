# -*- coding: utf-8 -*-
"""Docs tools: PRD templates, guides, etc."""

import os
from datetime import datetime
from pathlib import Path
from mcp.types import TextContent


# Available templates
TEMPLATES = {
    "web-app": {
        "name": "Web Application",
        "layouts": ["lite", "standard", "detailed"],
        "description": "Web application (React, Vue, Next.js, etc.)"
    },
    "api": {
        "name": "API Server",
        "layouts": ["lite", "standard"],
        "description": "REST/GraphQL API server"
    },
    "cli": {
        "name": "CLI Tool",
        "layouts": ["lite", "standard"],
        "description": "Command-line tool"
    },
    "chrome-ext": {
        "name": "Chrome Extension",
        "layouts": ["lite", "standard"],
        "description": "Chrome extension (MV3)"
    },
    "discord-bot": {
        "name": "Discord Bot",
        "layouts": ["lite", "standard"],
        "description": "Discord bot (discord.js/discord.py)"
    },
    "landing-page": {
        "name": "Landing Page",
        "layouts": ["lite", "standard"],
        "description": "Landing page / Marketing page"
    },
    "saas": {
        "name": "SaaS MVP",
        "layouts": ["lite", "standard"],
        "description": "SaaS MVP (Auth + Payment + Subscription)"
    },
    "generic": {
        "name": "Generic",
        "layouts": ["standard"],
        "description": "Generic template"
    }
}


def _get_template_path(template: str, layout: str) -> Path:
    """Return template file path"""
    # Templates folder inside package
    base_path = Path(__file__).parent.parent / "templates"
    return base_path / template / f"{layout}.md"


def _load_template(template: str, layout: str) -> str:
    """Load template file"""
    template_path = _get_template_path(template, layout)

    if template_path.exists():
        return template_path.read_text(encoding="utf-8")

    # Return None if file doesn't exist
    return None


async def get_prd_template(project_name: str, output_path: str, template: str = "generic", layout: str = "standard") -> list[TextContent]:
    """Generate PRD template

    Args:
        project_name: Project name
        output_path: Output path
        template: Template type (web-app, api, cli, generic)
        layout: Layout (lite, standard, detailed)
    """
    # Try loading template
    content = _load_template(template, layout)

    if content:
        # Replace placeholders
        now = datetime.now().strftime('%Y-%m-%d')
        content = content.replace("{PROJECT_NAME}", project_name)
        content = content.replace("{DATE}", now)

        return [TextContent(type="text", text=f"""# {template}/{layout} Template

```markdown
{content}
```

---

**Save path**: `{output_path}`

**Next steps**:
1. Save the above content to `{output_path}`
2. Fill in sections marked with [ ]
3. Start coding after completion

**Tip**: Don't try to fill everything at once. Start with core sections (1-4) first.
""")]

    # generic fallback
    template_content = f"""# {project_name} PRD

> This document is law. If it's not here, don't build it.
> Created: {datetime.now().strftime('%Y-%m-%d')}

---

## 1. One-line Summary
<!-- Describe the project in one sentence. If you can't, it's not clear yet. -->

[Write here]

---

## 2. Core Principles

> Things that never change. Use these to judge features.

1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

---

## 3. Terminology

| Term | Description |
|------|-------------|
| [Term1] | [Description] |

---

## 4. Input Spec

> Things coming from outside. User input, API requests, etc.

### 4.1 [Input Type 1]
- Format:
- Required fields:
- Constraints:

---

## 5. Output Spec

> Things going outside. UI, API responses, files, etc.

### 5.1 [Output Type 1]
- Format:
- Fields:
- Example:

---

## 6. Error Cases

> Every situation that could fail. Missing one = bug.

| Situation | Handling | Error Code |
|-----------|----------|------------|
| [Situation1] | [Method] | [Code] |

---

## 7. Verification Plan

- [ ] [Test case 1]
- [ ] [Test case 2]

---

## Change Log

| Date | Changes | Author |
|------|---------|--------|
| {datetime.now().strftime('%Y-%m-%d')} | Initial draft | |

"""
    return [TextContent(type="text", text=f"```markdown\n{template_content}\n```\n\nSave to: `{output_path}`")]


async def list_templates() -> list[TextContent]:
    """List available templates"""
    lines = ["# PRD Template List\n"]

    for key, info in TEMPLATES.items():
        layouts = ", ".join(info["layouts"])
        lines.append(f"## {info['name']} (`{key}`)")
        lines.append(f"- **Description**: {info['description']}")
        lines.append(f"- **Layouts**: {layouts}")
        lines.append("")

    lines.append("---")
    lines.append("**Usage**: Specify `template` and `layout` when calling `get_prd_template`")
    lines.append("```")
    lines.append('e.g., template="web-app", layout="standard"')
    lines.append("```")

    return [TextContent(type="text", text="\n".join(lines))]


async def write_prd_section(section: str, content: str) -> list[TextContent]:
    """PRD section writing guide"""
    guides = {
        "summary": "One-line Summary: Describe the project in one sentence. If you can't, it's not clear yet.",
        "principles": "Core Principles: 3-5 things that never change. Criteria for judging features.",
        "input_spec": "Input Spec: Everything coming from outside. Include format, required fields, constraints.",
        "output_spec": "Output Spec: Everything going outside. Include format, fields, examples.",
        "errors": "Error Cases: Every situation that could fail. Missing one = bug.",
        "state_machine": "State Machine: If there are states, draw them. Make state transitions clear.",
        "api_endpoints": "API Endpoints: Method, Path, Description. Keep it RESTful.",
        "db_schema": "DB Schema: Tables, columns, types, relationships. Consider normalization.",
    }

    guide = guides.get(section, "Unknown section.")
    return [TextContent(type="text", text=f"## {section} Writing Guide\n\n{guide}\n\nContent:\n{content if content else '(Input required)'}")]


async def get_prd_guide() -> list[TextContent]:
    """PRD writing guide"""
    return [TextContent(type="text", text="""# PRD Writing Guide

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
""")]


async def get_verify_checklist() -> list[TextContent]:
    """Verification checklist"""
    return [TextContent(type="text", text="""# Verification Checklist

## PRD Verification
- [ ] Is the one-line summary clear?
- [ ] Are there at least 3 core principles?
- [ ] Are input/output specs specific?
- [ ] Are all error cases covered?

## Code Verification
- [ ] Only features specified in PRD implemented?
- [ ] Error cases handled?
- [ ] Tests written?

## Pre-deployment Verification
- [ ] All tests passing?
- [ ] No lint errors?
- [ ] Build successful?
""")]


async def get_setup_guide(platform: str) -> list[TextContent]:
    """Setup guide"""
    guides = {
        "desktop": """## Claude Desktop Setup

1. Open config file: `%APPDATA%\\Claude\\claude_desktop_config.json`
2. Add the following:

```json
{
  "mcpServers": {
    "clouvel": {
      "command": "uvx",
      "args": ["clouvel"]
    }
  }
}
```

3. Restart Claude Desktop
""",
        "code": """## Claude Code (CLI) Setup

```bash
# Auto setup
clouvel init

# Or manual
clouvel init -p /path/to/project -l strict
```
""",
        "vscode": """## VS Code Setup

1. Search "Clouvel" in Extensions tab
2. Install
3. Command Palette (Ctrl+Shift+P) -> "Clouvel: Setup MCP Server"
""",
        "cursor": """## Cursor Setup

Same as VS Code. Install the "Clouvel" extension.
""",
    }

    if platform == "all":
        result = "# Clouvel Setup Guide\n\n"
        for p, g in guides.items():
            result += g + "\n---\n\n"
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=guides.get(platform, "Unknown platform."))]
