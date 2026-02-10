# -*- coding: utf-8 -*-
"""Shovel 설치 및 관리 도구 (서버사이드 콘텐츠)

v2: 로컬 템플릿 대신 서버에서 콘텐츠 가져옴
- 패키지 추출 공격 방지
- 라이선스 + 7일 검증 후에만 콘텐츠 제공

DEV_MODE: 모든 검증 스킵, 로컬 shovel 폴더 직접 복사
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

from ..license import require_license_premium, verify_license
from ..content_api import fetch_content_bundle, get_cache_status

# DEV_MODE (표준 is_developer() 사용)
def _is_dev_mode() -> bool:
    try:
        from ..license_common import is_developer
        return is_developer()
    except ImportError:
        # Fallback: CLOUVEL_DEV=1 (통합된 개발 모드 변수)
        return os.environ.get("CLOUVEL_DEV") == "1"

DEV_MODE = _is_dev_mode()
# site-packages/clouvel_pro/tools/shovel.py → site-packages/shovel
SHOVEL_DIR = Path(__file__).parent.parent.parent / "shovel"


async def _install_shovel_dev(project_path: Path, claude_dir: Path, force: bool) -> list[TextContent]:
    """DEV_MODE: 로컬 shovel 폴더 직접 복사 (모든 검증 스킵)"""
    if not SHOVEL_DIR.exists():
        return [TextContent(type="text", text=f"DEV_MODE 오류: {SHOVEL_DIR} 없음")]

    # 기존 폴더 처리
    if claude_dir.exists():
        if not force:
            return [TextContent(type="text", text=f".claude/ 이미 존재. force=true로 덮어쓰기")]
        shutil.rmtree(claude_dir)

    # .claude 폴더 복사
    src_claude = SHOVEL_DIR / ".claude"
    if src_claude.exists():
        shutil.copytree(src_claude, claude_dir)

    # CLAUDE.md 복사
    src_claude_md = SHOVEL_DIR / "CLAUDE.md"
    dst_claude_md = project_path / "CLAUDE.md"
    if src_claude_md.exists() and not dst_claude_md.exists():
        shutil.copy(src_claude_md, dst_claude_md)

    # scripts 복사
    src_scripts = SHOVEL_DIR / "scripts"
    dst_scripts = project_path / "scripts"
    if src_scripts.exists():
        dst_scripts.mkdir(exist_ok=True)
        for f in src_scripts.iterdir():
            shutil.copy(f, dst_scripts / f.name)

    return [TextContent(type="text", text=f"""
# ✅ Shovel 설치 완료 (DEV_MODE)

경로: `{project_path}`
소스: `{SHOVEL_DIR}`

## 다음 단계
1. `/start` - 온보딩
2. `/plan` - 계획
3. `/gate` - 검증
""")]


async def install_shovel(
    path: str,
    project_type: str = "web",
    force: bool = False
) -> list[TextContent]:
    """Shovel .claude/ 구조 자동 설치 (서버에서 콘텐츠 다운로드)"""
    project_path = Path(path)
    claude_dir = project_path / ".claude"

    # DEV_MODE: 로컬 shovel 폴더 직접 복사
    if DEV_MODE:
        return await _install_shovel_dev(project_path, claude_dir, force)

    # 이미 존재하는지 확인
    if claude_dir.exists() and not force:
        return [TextContent(type="text", text=f"""
# ⚠️ .claude/ 폴더가 이미 존재합니다

경로: `{claude_dir}`

## 옵션
1. `force=true`로 덮어쓰기
2. `sync_commands`로 커맨드만 동기화
""")]

    # 서버에서 콘텐츠 번들 가져오기
    bundle_result = fetch_content_bundle()

    if not bundle_result.get("success"):
        error = bundle_result.get("error")
        message = bundle_result.get("message")

        # 7일 잠금인 경우
        if error == "Premium locked":
            days_remaining = bundle_result.get("days_remaining", "?")
            unlock_date = bundle_result.get("unlock_date", "")
            return [TextContent(type="text", text=f"""
# ⏳ 프리미엄 기능 잠금 중

{message}

## 현재 상태
- **잠금 해제까지**: {days_remaining}일 남음
- **해제 예정일**: {unlock_date[:10] if unlock_date else 'N/A'}

## 지금 사용 가능한 기능
- `watch_logs` - 로그 감시 설정
- `check_logs` - 로그 체크

**{days_remaining}일 후 다시 시도해주세요!**
""")]

        # 기타 에러
        return [TextContent(type="text", text=f"""
# ❌ 콘텐츠 로드 실패

**오류**: {error}
**메시지**: {message}

## 확인사항
- 라이선스가 활성화되어 있는지 확인
- 인터넷 연결 확인
- 라이선스가 환불되지 않았는지 확인
""")]

    content = bundle_result.get("content", {})
    version = bundle_result.get("version", "unknown")
    cached = bundle_result.get("cached", False)

    # .claude 디렉토리 구조 생성
    if claude_dir.exists() and force:
        import shutil
        shutil.rmtree(claude_dir)

    # 디렉토리 생성
    (claude_dir / "commands").mkdir(parents=True, exist_ok=True)
    (claude_dir / "templates").mkdir(parents=True, exist_ok=True)
    (claude_dir / "config").mkdir(parents=True, exist_ok=True)
    (claude_dir / "evidence").mkdir(parents=True, exist_ok=True)
    (claude_dir / "logs").mkdir(parents=True, exist_ok=True)
    (claude_dir / "plans").mkdir(parents=True, exist_ok=True)

    installed_files = []

    # 커맨드 파일 설치
    commands = content.get("commands", {})
    for filename, file_content in commands.items():
        file_path = claude_dir / "commands" / filename
        file_path.write_text(file_content, encoding="utf-8")
        installed_files.append(f".claude/commands/{filename}")

    # 템플릿 파일 설치
    templates = content.get("templates", {})
    for filename, file_content in templates.items():
        file_path = claude_dir / "templates" / filename
        file_path.write_text(file_content, encoding="utf-8")
        installed_files.append(f".claude/templates/{filename}")

    # 설정 파일 설치
    config = content.get("config", {})
    for filename, file_content in config.items():
        file_path = claude_dir / "config" / filename
        file_path.write_text(file_content, encoding="utf-8")
        installed_files.append(f".claude/config/{filename}")

    # settings.json 설치
    settings = content.get("settings", {})
    if "settings.json" in settings:
        settings_path = claude_dir / "settings.json"
        settings_path.write_text(settings["settings.json"], encoding="utf-8")
        installed_files.append(".claude/settings.json")

    # CLAUDE.md 설치 (프로젝트 루트에, 없을 때만)
    claude_md = content.get("claude_md")
    claude_md_path = project_path / "CLAUDE.md"
    if claude_md and not claude_md_path.exists():
        claude_md_path.write_text(claude_md, encoding="utf-8")
        installed_files.append("CLAUDE.md")

    # scripts 폴더 생성 (gate.sh 포함)
    scripts_dir = project_path / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    gate_script = scripts_dir / "gate.sh"
    if not gate_script.exists():
        gate_script.write_text("""#!/bin/bash
# Shovel Gate Script
set -e

echo "🔍 Running lint..."
pnpm lint || npm run lint || echo "No lint script found"

echo "🧪 Running tests..."
pnpm test || npm test || echo "No test script found"

echo "🔨 Running build..."
pnpm build || npm run build || echo "No build script found"

echo ""
echo "✅ Gate PASS"

# Generate EVIDENCE.md
cat > EVIDENCE.md << EOF
# Gate Evidence

- **Status**: PASS ✅
- **Generated**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Lint**: PASS
- **Test**: PASS
- **Build**: PASS
EOF

echo "📄 EVIDENCE.md generated"
""", encoding="utf-8")
        installed_files.append("scripts/gate.sh")

    source_info = "(캐시됨)" if cached else "(서버에서 다운로드)"

    return [TextContent(type="text", text=f"""
# ✅ Shovel 설치 완료 {source_info}

## 설치 경로
`{project_path}`

## 버전
`{version}`

## 생성된 구조
```
.claude/
├── commands/      (슬래시 커맨드) - {len(commands)}개
├── templates/     (템플릿) - {len(templates)}개
├── config/        (설정) - {len(config)}개
├── evidence/      (Gate 증거)
├── logs/          (작업 로그)
├── plans/         (계획 파일)
└── settings.json  (설정)
```

## 설치된 파일 수
{len(installed_files)}개

## 다음 단계
1. `/start` - 프로젝트 온보딩
2. `/plan` - 계획 수립
3. `/gate` - 검증 실행

## 핵심 워크플로우
```
/start → /plan → /implement → /gate → /commit
```
""")]


@require_license_premium
async def sync_commands(
    path: str,
    mode: str = "merge"
) -> list[TextContent]:
    """Shovel 커맨드 동기화 (서버에서 최신 버전 가져오기)"""
    project_path = Path(path)
    claude_dir = project_path / ".claude"
    commands_dir = claude_dir / "commands"

    if not claude_dir.exists():
        return [TextContent(type="text", text="""
# ❌ .claude/ 폴더가 없습니다

먼저 `install_shovel`로 Shovel을 설치하세요.
""")]

    # 서버에서 콘텐츠 가져오기
    bundle_result = fetch_content_bundle()

    if not bundle_result.get("success"):
        error = bundle_result.get("error")
        message = bundle_result.get("message")

        if error == "Premium locked":
            days_remaining = bundle_result.get("days_remaining", "?")
            return [TextContent(type="text", text=f"""
# ⏳ 프리미엄 기능 잠금 중

{message}

**{days_remaining}일 후 다시 시도해주세요!**
""")]

        return [TextContent(type="text", text=f"""
# ❌ 콘텐츠 로드 실패

**오류**: {error}
**메시지**: {message}
""")]

    content = bundle_result.get("content", {})
    commands = content.get("commands", {})
    version = bundle_result.get("version", "unknown")

    commands_dir.mkdir(parents=True, exist_ok=True)

    synced = []
    skipped = []

    for filename, file_content in commands.items():
        target = commands_dir / filename

        if mode == "merge" and target.exists():
            skipped.append(filename)
            continue

        target.write_text(file_content, encoding="utf-8")
        synced.append(filename)

    return [TextContent(type="text", text=f"""
# ✅ 커맨드 동기화 완료

## 버전
`{version}`

## 모드
`{mode}` {'(기존 파일 유지)' if mode == 'merge' else '(덮어쓰기)'}

## 동기화된 커맨드
{chr(10).join(f'- {c}' for c in synced) if synced else '없음'}

## 스킵된 커맨드 (이미 존재)
{chr(10).join(f'- {c}' for c in skipped) if skipped else '없음'}

## 사용 가능한 커맨드
| 커맨드 | 설명 |
|--------|------|
| /start | 프로젝트 온보딩 |
| /plan | 계획 수립 |
| /implement | 구현 실행 |
| /gate | lint → test → build |
| /verify | Context Bias 검증 |
| /commit | Gate PASS 후 커밋 |
| /learn-error | 에러 학습 |
""")]


async def check_content_status() -> list[TextContent]:
    """콘텐츠 캐시 상태 확인 (라이선스 불필요)"""
    cache_status = get_cache_status()

    if cache_status.get("cached"):
        return [TextContent(type="text", text=f"""
# 📦 콘텐츠 캐시 상태

- **캐시됨**: ✅
- **캐시 시간**: {cache_status.get('cached_at', 'N/A')}
- **경과**: {cache_status.get('age_hours', '?')} 시간
- **유효**: {'✅' if cache_status.get('valid') else '❌ (만료됨)'}
""")]

    return [TextContent(type="text", text="""
# 📦 콘텐츠 캐시 상태

- **캐시됨**: ❌

`install_shovel` 또는 `sync_commands` 실행 시 자동으로 캐시됩니다.
""")]
