# -*- coding: utf-8 -*-
"""Rules tools (v0.5): init_rules, get_rule, add_rule"""

import json
from pathlib import Path
from mcp.types import TextContent


async def init_rules(path: str, template: str) -> list[TextContent]:
    """규칙 모듈화 초기화

    DEPRECATED: Use `setup_cli(rules=...)` instead. Will be removed in v2.0.
    """
    # Deprecation warning
    deprecation_warning = """⚠️ **DEPRECATED**: `init_rules` will be removed in v2.0.
Use `setup_cli` with rules option instead:

**Migration**: `setup_cli(path, level="strict", rules="web")`

---

"""
    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    rules_dir = project_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    # 템플릿별 규칙 파일
    templates = {
        "minimal": ["global.md", "security.md"],
        "web": ["global.md", "security.md", "frontend.md"],
        "api": ["global.md", "security.md", "api.md", "database.md"],
        "fullstack": ["global.md", "security.md", "frontend.md", "api.md", "database.md"],
    }

    files_to_create = templates.get(template, templates["minimal"])
    created = []

    # 규칙 파일 내용
    rule_contents = {
        "global.md": """# Global Rules

## ALWAYS
- Read before Edit
- Check PRD before implementing
- Update progress after completing

## NEVER
- Skip documentation
- Implement features not in PRD
- Commit without tests
""",
        "security.md": """# Security Rules

## ALWAYS
- Validate user input
- Use parameterized queries
- Escape output for XSS prevention

## NEVER
- Store passwords in plain text
- Expose sensitive data in logs
- Trust client-side validation alone
""",
        "frontend.md": """# Frontend Rules

## ALWAYS
- Use semantic HTML
- Handle loading/error states
- Support keyboard navigation

## NEVER
- Use inline styles for complex CSS
- Mutate props directly
- Skip accessibility attributes
""",
        "api.md": """# API Rules

## ALWAYS
- Return consistent response format
- Include proper HTTP status codes
- Document all endpoints

## NEVER
- Expose internal errors to clients
- Use GET for state-changing operations
- Skip rate limiting
""",
        "database.md": """# Database Rules

## ALWAYS
- Use migrations for schema changes
- Index foreign keys
- Use transactions for multi-step operations

## NEVER
- Store JSON for relational data
- Skip backup before migration
- Use SELECT * in production
""",
    }

    for filename in files_to_create:
        file_path = rules_dir / filename
        if not file_path.exists():
            file_path.write_text(rule_contents.get(filename, f"# {filename}\n\n[규칙 작성]"), encoding='utf-8')
            created.append(filename)

    # rules.index.json 생성
    index_content = {
        "version": "0.5.0",
        "template": template,
        "rules": [
            {"file": f, "scope": "**/*", "priority": 100 - i * 10}
            for i, f in enumerate(files_to_create)
        ]
    }
    index_file = rules_dir / "rules.index.json"
    index_file.write_text(json.dumps(index_content, indent=2, ensure_ascii=False), encoding='utf-8')

    created_list = "\n".join(f"- {f}" for f in created) if created else "없음 (이미 존재)"

    return [TextContent(type="text", text=deprecation_warning + f"""# 규칙 모듈화 완료

## 템플릿
**{template}**

## 생성된 파일
{created_list}

## 경로
`{rules_dir}`

## 사용법
- `get_rule`로 파일별 규칙 로딩
- `add_rule`로 새 규칙 추가

**컨텍스트 절약 50%+ 효과!**
""")]


async def get_rule(path: str, context: str) -> list[TextContent]:
    """경로 기반 규칙 로딩"""
    file_path = Path(path)

    # 프로젝트 루트 찾기
    current = file_path if file_path.is_dir() else file_path.parent
    rules_dir = None

    for _ in range(10):  # 최대 10레벨 상위까지
        potential = current / ".claude" / "rules"
        if potential.exists():
            rules_dir = potential
            break
        if current.parent == current:
            break
        current = current.parent

    if not rules_dir:
        return [TextContent(type="text", text="❌ .claude/rules/ 폴더를 찾을 수 없습니다. `init_rules`로 먼저 생성하세요.")]

    # 규칙 파일 로딩
    rules = []
    for rule_file in rules_dir.glob("*.md"):
        rules.append(f"## {rule_file.stem}\n\n{rule_file.read_text(encoding='utf-8')}")

    if not rules:
        return [TextContent(type="text", text="❌ 규칙 파일이 없습니다.")]

    context_note = f"\n\n> 컨텍스트: {context}" if context != "coding" else ""

    return [TextContent(type="text", text=f"""# 적용 규칙

경로: `{path}`{context_note}

---

{chr(10).join(rules)}
""")]


async def add_rule(path: str, rule_type: str, content: str, category: str) -> list[TextContent]:
    """새 규칙 추가"""
    project_path = Path(path)
    rules_dir = project_path / ".claude" / "rules"

    if not rules_dir.exists():
        return [TextContent(type="text", text="❌ .claude/rules/ 폴더가 없습니다. `init_rules`로 먼저 생성하세요.")]

    # 카테고리 파일 선택
    category_files = {
        "api": "api.md",
        "frontend": "frontend.md",
        "database": "database.md",
        "security": "security.md",
        "general": "global.md",
    }
    target_file = rules_dir / category_files.get(category, "global.md")

    # 파일이 없으면 생성
    if not target_file.exists():
        target_file.write_text(f"# {category.title()} Rules\n\n", encoding='utf-8')

    # 규칙 추가
    existing = target_file.read_text(encoding='utf-8')
    rule_section = f"\n## {rule_type.upper()}\n- {content}\n"

    # 같은 타입 섹션이 있으면 거기에 추가
    if f"## {rule_type.upper()}" in existing:
        existing = existing.replace(f"## {rule_type.upper()}\n", f"## {rule_type.upper()}\n- {content}\n")
        target_file.write_text(existing, encoding='utf-8')
    else:
        target_file.write_text(existing + rule_section, encoding='utf-8')

    return [TextContent(type="text", text=f"""# 규칙 추가 완료

## 상세

| 항목 | 값 |
|------|-----|
| 타입 | {rule_type.upper()} |
| 카테고리 | {category} |
| 파일 | {target_file.name} |

## 내용
{content}

---

규칙이 `{target_file}`에 추가되었습니다.
""")]
