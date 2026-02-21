# -*- coding: utf-8 -*-
"""Setup tools: init_clouvel, setup_cli"""

import json
from pathlib import Path
from mcp.types import TextContent


async def init_clouvel(platform: str) -> list[TextContent]:
    """Clouvel 온보딩"""
    if platform == "ask":
        return [TextContent(type="text", text="""# Clouvel 온보딩

어떤 환경에서 사용하시나요?

1. **Claude Desktop** - GUI 앱
2. **VS Code / Cursor** - IDE 확장
3. **Claude Code (CLI)** - 터미널

선택해 주시면 맞춤 설정을 안내해 드립니다.

예: "Claude Code에서 사용할 거야" 또는 "1번"
""")]

    guides = {
        "desktop": """# Claude Desktop 설정 완료!

MCP 서버가 이미 연결되어 있습니다.

## 사용법
대화에서 "코딩해도 돼?" 또는 "can_code로 확인해줘" 라고 말하세요.

## 주요 도구
- `can_code` - 코딩 가능 여부 확인
- `init_docs` - 문서 템플릿 생성
- `get_prd_guide` - PRD 작성 가이드
""",
        "vscode": """# VS Code / Cursor 설정 안내

## 설치 방법
1. 확장 탭에서 "Clouvel" 검색
2. 설치
3. Command Palette (Ctrl+Shift+P)
4. "Clouvel: Setup MCP Server" 실행

## CLI도 설정하시겠어요?
"CLI도 설정해줘" 라고 말씀하시면 추가 설정을 진행합니다.
""",
        "cli": """# Claude Code (CLI) 설정 안내

## 자동 설정
```bash
clouvel init
```

## 수동 설정
```bash
clouvel init -p /path/to/project -l strict
```

## 강제 수준
- `remind` - 경고만
- `strict` - 커밋 차단 (추천)
- `full` - Hooks + 커밋 차단

어떤 수준으로 설정할까요?
""",
    }

    return [TextContent(type="text", text=guides.get(platform, guides["cli"]))]


async def setup_cli(
    path: str,
    level: str = "strict",
    rules: str = "",
    hook: str = "",
    hook_trigger: str = "",
    proactive: str = ""
) -> list[TextContent]:
    """CLI 환경 설정

    Args:
        path: Project root path
        level: Enforcement level (remind, strict, full)
        rules: Initialize rules with template (replaces init_rules) - web, api, fullstack, minimal
        hook: Create hook (replaces hook_design, hook_verify) - design or verify
        hook_trigger: Trigger for hook - pre_code, pre_feature, post_code, pre_commit, etc.
        proactive: Setup proactive hooks (v2.0) - free or pro
    """
    project_path = Path(path).resolve()

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    # === Option: --rules (Initialize rules) ===
    if rules:
        rules_dir = project_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        templates = {
            "minimal": ["global.md", "security.md"],
            "web": ["global.md", "security.md", "frontend.md"],
            "api": ["global.md", "security.md", "api.md", "database.md"],
            "fullstack": ["global.md", "security.md", "frontend.md", "api.md", "database.md"],
        }

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

        files_to_create = templates.get(rules, templates["minimal"])
        created = []

        for filename in files_to_create:
            file_path = rules_dir / filename
            if not file_path.exists():
                file_path.write_text(rule_contents.get(filename, f"# {filename}\n"), encoding='utf-8')
                created.append(filename)

        return [TextContent(type="text", text=f"""# Rules Initialized

## Template: {rules}

## Created Files
{chr(10).join(f"- {f}" for f in created) if created else "None (already exist)"}

## Path
`{rules_dir}`

**Context savings 50%+!**
""")]

    # === Option: --hook (Create hook) ===
    if hook:
        hooks_dir = project_path / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime

        if hook == "design":
            default_checks = {
                "pre_code": ["prd_exists", "architecture_review", "scope_defined"],
                "pre_feature": ["feature_in_prd", "api_spec_exists", "db_schema_ready"],
                "pre_refactor": ["test_coverage", "backup_exists", "rollback_plan"],
                "pre_api": ["api_spec_complete", "auth_defined", "error_codes_listed"]
            }
            trigger = hook_trigger or "pre_code"
            checks = default_checks.get(trigger, default_checks["pre_code"])

            hook_config = {
                "name": f"design_{trigger}",
                "trigger": trigger,
                "checks": checks,
                "block_on_fail": True,
                "created": datetime.now().isoformat()
            }
            hook_file = hooks_dir / f"{trigger}.json"
            hook_file.write_text(json.dumps(hook_config, indent=2, ensure_ascii=False), encoding='utf-8')

            return [TextContent(type="text", text=f"""# Design Hook Created

## Trigger: {trigger}
## Checks: {len(checks)}

{chr(10).join(f"- [ ] {c}" for c in checks)}

## Path
`{hook_file}`
""")]

        elif hook == "verify":
            default_steps = {
                "post_code": ["lint", "type_check"],
                "post_feature": ["lint", "test", "build"],
                "pre_commit": ["lint", "test", "security_scan"],
                "pre_push": ["lint", "test", "build", "integration_test"]
            }
            trigger = hook_trigger or "post_code"
            steps = default_steps.get(trigger, default_steps["post_code"])

            hook_config = {
                "name": f"verify_{trigger}",
                "trigger": trigger,
                "steps": steps,
                "parallel": False,
                "continue_on_error": False,
                "created": datetime.now().isoformat()
            }
            hook_file = hooks_dir / f"{trigger}.json"
            hook_file.write_text(json.dumps(hook_config, indent=2, ensure_ascii=False), encoding='utf-8')

            return [TextContent(type="text", text=f"""# Verify Hook Created

## Trigger: {trigger}
## Steps: {len(steps)}

{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(steps))}

## Path
`{hook_file}`
""")]

        else:
            return [TextContent(type="text", text=f"❌ Unknown hook type: {hook}. Use 'design' or 'verify'.")]

    # === Option: --proactive (v2.0 Proactive MCP) ===
    if proactive:
        claude_dir = project_path / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)

        settings_file = claude_dir / "settings.local.json"

        # Determine docs path relative to project
        docs_path = "./docs"
        if (project_path / "docs").exists():
            docs_path = "./docs"
        elif (project_path / "doc").exists():
            docs_path = "./doc"

        if proactive == "free":
            # Free: Auto PRD check only
            settings_content = {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Edit|Write",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "clouvel-gate || python -m clouvel.gate_check"
                                }
                            ]
                        }
                    ]
                }
            }
            tier_msg = "Free"
            features = ["Auto PRD check before Edit/Write (via gate_check)"]

        elif proactive == "pro":
            # Pro: Full proactive features
            settings_content = {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Edit|Write",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "clouvel-gate || python -m clouvel.gate_check"
                                }
                            ]
                        }
                    ],
                    "PostToolUse": [
                        {
                            "matcher": ".*",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "clouvel drift_check --path . --silent"
                                }
                            ]
                        }
                    ]
                }
            }
            tier_msg = "Pro"
            features = [
                "Auto PRD check before Edit/Write",
                "Context drift detection after every action"
            ]

        else:
            return [TextContent(type="text", text=f"❌ Unknown proactive tier: {proactive}. Use 'free' or 'pro'.")]

        # Write settings file
        settings_file.write_text(json.dumps(settings_content, indent=2), encoding='utf-8')

        return [TextContent(type="text", text=f"""# Proactive MCP Configured ({tier_msg})

## Features Enabled
{chr(10).join(f"- {f}" for f in features)}

## Settings File
`{settings_file}`

## How It Works
- **PreToolUse**: Checks PRD before you write code
- **BLOCK** = No coding allowed (PRD missing)
- **PASS** = Coding allowed

## Next Steps
1. Restart Claude Code to apply hooks
2. Try editing a file - PRD check will run automatically

## Docs Path
`{docs_path}` (auto-detected)

---
Tip: Edit `.claude/settings.local.json` to customize.
""")]

    created_files = []

    # 1. .claude 폴더 생성
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # 2. hooks.json (remind, full)
    if level in ["remind", "full"]:
        hooks_content = {
            "hooks": {
                "preToolUse": [
                    {
                        "matcher": "Edit|Write|NotebookEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo '[Clouvel] 코드 작성 전 can_code 도구로 문서 상태를 확인하세요!'"
                            }
                        ]
                    }
                ]
            }
        }
        hooks_file = claude_dir / "hooks.json"
        hooks_file.write_text(json.dumps(hooks_content, indent=2, ensure_ascii=False), encoding='utf-8')
        created_files.append(".claude/hooks.json")

    # 3. CLAUDE.md 규칙
    claude_md = project_path / "CLAUDE.md"
    clouvel_rule = """
## Clouvel 규칙 (자동 생성)

> 이 규칙은 Clouvel이 자동으로 추가했습니다.

### 필수 준수 사항
1. **코드 작성 전 문서 체크**: Edit/Write 도구 사용 전 반드시 `can_code` 도구를 먼저 호출
2. **can_code 실패 시 코딩 금지**: 필수 문서가 없으면 PRD 작성부터
3. **PRD가 법**: docs/PRD.md에 없는 기능은 구현하지 않음
"""

    if claude_md.exists():
        existing = claude_md.read_text(encoding='utf-8')
        if "Clouvel 규칙" not in existing:
            claude_md.write_text(existing + "\n" + clouvel_rule, encoding='utf-8')
            created_files.append("CLAUDE.md (규칙 추가)")
    else:
        claude_md.write_text(f"# {project_path.name}\n" + clouvel_rule, encoding='utf-8')
        created_files.append("CLAUDE.md (생성)")

    # 4. pre-commit hook (strict, full)
    if level in ["strict", "full"]:
        git_hooks_dir = project_path / ".git" / "hooks"
        if git_hooks_dir.exists():
            pre_commit = git_hooks_dir / "pre-commit"
            pre_commit_content = '''#!/bin/bash
# Clouvel pre-commit hook (Free)
# 1. PRD 문서 확인
# 2. 기록 파일 확인 (files/created.md, status/current.md)
# 3. 민감 파일 커밋 차단

# === PRD 체크 ===
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    echo "Please create docs/PRD.md first."
    exit 1
fi

# === 기록 파일 체크 (v1.5) ===
if [ ! -f ".claude/files/created.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: files/created.md 없음"
    echo "========================================"
    echo ""
    echo "생성 파일 기록이 없습니다."
    echo "해결: .claude/files/created.md 생성 후 커밋"
    echo ""
    exit 1
fi

if [ ! -f ".claude/status/current.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: status/current.md 없음"
    echo "========================================"
    echo ""
    echo "작업 상태 기록이 없습니다."
    echo "해결: .claude/status/current.md 생성 후 커밋"
    echo ""
    exit 1
fi

# === 보안 체크 (민감 파일 차단) ===
SENSITIVE_PATTERNS="(marketing|strategy|pricing|가격|마케팅|전략|server_pro|_pro\\.py|\\.key$|\\.secret$|credentials|password)"

SENSITIVE_FILES=$(git diff --cached --name-only | grep -iE "$SENSITIVE_PATTERNS" 2>/dev/null)

if [ -n "$SENSITIVE_FILES" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] SECURITY BLOCK: 민감 파일 감지!"
    echo "========================================"
    echo ""
    echo "다음 파일은 커밋할 수 없습니다:"
    echo "$SENSITIVE_FILES" | while read -r file; do
        echo "  ❌ $file"
    done
    echo ""
    echo "해결: git reset HEAD <파일명>"
    echo "무시: git commit --no-verify (권장하지 않음)"
    echo ""
    exit 1
fi

echo "[Clouvel] All checks passed. ✓"
'''
            pre_commit.write_text(pre_commit_content, encoding='utf-8')
            # chmod +x 처리
            try:
                import os
                os.chmod(pre_commit, 0o755)
            except:
                pass
            created_files.append(".git/hooks/pre-commit")

    files_list = "\n".join(f"- {f}" for f in created_files) if created_files else "없음"

    return [TextContent(type="text", text=f"""# CLI 설정 완료

## 프로젝트
`{project_path}`

## 강제 수준
**{level}**

## 생성/수정된 파일
{files_list}

## 다음 단계
1. `docs/PRD.md` 생성
2. Claude에게 "코딩해도 돼?" 질문
3. PRD 없으면 코딩 차단됨

**PRD 없으면 코딩 없다!**
""")]
