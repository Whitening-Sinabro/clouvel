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


async def setup_cli(path: str, level: str) -> list[TextContent]:
    """CLI 환경 설정"""
    project_path = Path(path).resolve()

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

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
# 2. 민감 파일 커밋 차단

# === PRD 체크 ===
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    echo "Please create docs/PRD.md first."
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

echo "[Clouvel] Document check passed."
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
