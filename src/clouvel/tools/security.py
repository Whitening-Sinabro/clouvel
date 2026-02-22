# -*- coding: utf-8 -*-
"""
Clouvel Pro: Security Tools
커스텀 보안 패턴, 팀 동기화, 로깅
절대 GitHub에 올리지 마세요!
"""

import json
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

# 기본 민감 패턴 (Free와 동일)
DEFAULT_PATTERNS = [
    "marketing", "strategy", "pricing",
    "가격", "마케팅", "전략",
    "server_pro", "_pro\.py",
    "\.key$", "\.secret$",
    "credentials", "password"
]


async def setup_security(
    path: str,
    custom_patterns: list[str] | None = None,
    enable_logging: bool = True,
    team_sync: bool = False
) -> list[TextContent]:
    """
    Pro: 고급 보안 설정
    - 커스텀 패턴 추가
    - 차단 로깅
    - 팀 패턴 동기화
    """
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]
    
    # 패턴 병합
    patterns = DEFAULT_PATTERNS.copy()
    if custom_patterns:
        patterns.extend(custom_patterns)
    
    # .clouvel/security.json 저장
    clouvel_dir = project_path / ".clouvel"
    clouvel_dir.mkdir(exist_ok=True)
    
    security_config = {
        "version": "4.0.0",
        "patterns": patterns,
        "logging": enable_logging,
        "team_sync": team_sync,
        "updated_at": datetime.now().isoformat()
    }
    
    config_file = clouvel_dir / "security.json"
    config_file.write_text(json.dumps(security_config, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # pre-commit hook 생성 (Pro 버전)
    git_hooks_dir = project_path / ".git" / "hooks"
    if git_hooks_dir.exists():
        patterns_regex = "|".join(patterns)
        
        pre_commit_content = f'''#!/bin/bash
# Clouvel Pro pre-commit hook
# 커스텀 보안 패턴 + 로깅

CLOUVEL_DIR=".clouvel"
LOG_FILE="$CLOUVEL_DIR/security.log"

# === PRD 체크 ===
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    exit 1
fi

# === 보안 체크 (Pro: 커스텀 패턴) ===
SENSITIVE_PATTERNS="({patterns_regex})"

SENSITIVE_FILES=$(git diff --cached --name-only | grep -iE "$SENSITIVE_PATTERNS" 2>/dev/null)

if [ -n "$SENSITIVE_FILES" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel Pro] SECURITY BLOCK"
    echo "========================================"
    echo ""
    echo "차단된 파일:"
    echo "$SENSITIVE_FILES" | while read -r file; do
        echo "  ❌ $file"
    done
    
    # 로깅 (Pro 기능)
    if [ "{str(enable_logging).lower()}" = "true" ]; then
        mkdir -p "$CLOUVEL_DIR"
        echo "[$(date -Iseconds)] BLOCKED: $SENSITIVE_FILES" >> "$LOG_FILE"
    fi
    
    echo ""
    echo "해결: git reset HEAD <파일명>"
    exit 1
fi

echo "[Clouvel Pro] Security check passed."
'''
        pre_commit = git_hooks_dir / "pre-commit"
        pre_commit.write_text(pre_commit_content, encoding='utf-8')
        
        try:
            import os
            os.chmod(pre_commit, 0o755)
        except OSError:
            pass
    
    patterns_list = "\n".join(f"  - `{p}`" for p in patterns)
    
    return [TextContent(type="text", text=f"""# Clouvel Pro: 보안 설정 완료

## 프로젝트
`{project_path}`

## 설정
- **커스텀 패턴**: {len(custom_patterns or [])}개 추가
- **로깅**: {'✅ 활성화' if enable_logging else '❌ 비활성화'}
- **팀 동기화**: {'✅ 활성화' if team_sync else '❌ 비활성화'}

## 차단 패턴 ({len(patterns)}개)
{patterns_list}

## 생성된 파일
- `.clouvel/security.json`
- `.git/hooks/pre-commit` (Pro 버전)

## 로그 확인
```bash
cat .clouvel/security.log
```
""")]


async def add_security_pattern(path: str, pattern: str) -> list[TextContent]:
    """Pro: 보안 패턴 추가"""
    project_path = Path(path).resolve()
    config_file = project_path / ".clouvel" / "security.json"
    
    if not config_file.exists():
        return [TextContent(type="text", text="❌ 먼저 `setup_security`를 실행하세요.")]
    
    config = json.loads(config_file.read_text(encoding='utf-8'))
    
    if pattern in config["patterns"]:
        return [TextContent(type="text", text=f"ℹ️ 이미 존재하는 패턴: `{pattern}`")]
    
    config["patterns"].append(pattern)
    config["updated_at"] = datetime.now().isoformat()
    
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # hook 재생성
    await setup_security(path, config["patterns"], config["logging"], config["team_sync"])
    
    return [TextContent(type="text", text=f"✅ 패턴 추가됨: `{pattern}`")]


async def get_security_log(path: str, lines: int = 20) -> list[TextContent]:
    """Pro: 보안 로그 조회"""
    project_path = Path(path).resolve()
    log_file = project_path / ".clouvel" / "security.log"
    
    if not log_file.exists():
        return [TextContent(type="text", text="ℹ️ 보안 로그가 없습니다. (차단된 커밋이 없음)")]
    
    log_content = log_file.read_text(encoding='utf-8')
    log_lines = log_content.strip().split('\n')[-lines:]
    
    return [TextContent(type="text", text=f"""# 보안 로그 (최근 {lines}건)

```
{chr(10).join(log_lines)}
```
""")]
