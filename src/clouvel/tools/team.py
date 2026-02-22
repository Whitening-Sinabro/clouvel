# -*- coding: utf-8 -*-
"""Team tools: 팀 멤버 관리, 에러 패턴 공유, 프로젝트 컨텍스트 동기화"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

from ..license import require_team_license, get_cached_license

# Team API URL
TEAM_API_URL = os.environ.get(
    "CLOUVEL_TEAM_API_URL",
    "https://clouvel-api.vnddns999.workers.dev"
)


def _get_license_key() -> str:
    """저장된 라이선스 키 조회"""
    cached = get_cached_license()
    if cached and cached.get("license_key"):
        return cached["license_key"]
    return None


def _get_user_email() -> str:
    """사용자 이메일 조회 (라이선스 정보에서)"""
    cached = get_cached_license()
    if cached and cached.get("email"):
        return cached["email"]
    # 환경변수에서 시도
    return os.environ.get("CLOUVEL_USER_EMAIL", "user@example.com")


def _api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Team API 요청"""
    url = f"{TEAM_API_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, params=data, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid API response"}


# ============================================================
# 멤버 관리 도구
# ============================================================

@require_team_license
async def team_invite(email: str, role: str = "member") -> list[TextContent]:
    """팀에 새 멤버 초대

    Args:
        email: 초대할 멤버 이메일
        role: 역할 (admin 또는 member, 기본값: member)
    """
    license_key = _get_license_key()
    requester_email = _get_user_email()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/invite", "POST", {
        "license_key": license_key,
        "requester_email": requester_email,
        "invite_email": email,
        "role": role
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 멤버 초대 실패

**오류**: {result['error']}
""")]

    return [TextContent(type="text", text=f"""
# ✅ 멤버 초대 완료

**초대 대상**: {email}
**역할**: {role}

## 팀 현황
- **현재 멤버**: {result.get('members_count', '?')}명
- **남은 시트**: {result.get('seats_remaining', '?')}개
""")]


@require_team_license
async def team_members() -> list[TextContent]:
    """팀 멤버 목록 조회"""
    license_key = _get_license_key()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/members", "GET", {"license_key": license_key})

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 멤버 조회 실패

**오류**: {result['error']}
""")]

    members = result.get("members", [])
    seats = result.get("seats", {})

    member_list = "\n".join([
        f"| {m['email']} | {m['role']} | {m.get('joined_at', 'N/A')[:10]} |"
        for m in members
    ])

    return [TextContent(type="text", text=f"""
# 팀 멤버 목록

**오너**: {result.get('owner', 'N/A')}

## 멤버 ({seats.get('used', 0)}/{seats.get('max', 10)})

| 이메일 | 역할 | 가입일 |
|--------|------|--------|
{member_list}

**남은 시트**: {seats.get('remaining', 0)}개
""")]


@require_team_license
async def team_remove(email: str) -> list[TextContent]:
    """팀에서 멤버 제거

    Args:
        email: 제거할 멤버 이메일
    """
    license_key = _get_license_key()
    requester_email = _get_user_email()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/remove", "POST", {
        "license_key": license_key,
        "requester_email": requester_email,
        "target_email": email
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 멤버 제거 실패

**오류**: {result['error']}
""")]

    return [TextContent(type="text", text=f"""
# ✅ 멤버 제거 완료

**제거된 멤버**: {email}
**현재 멤버 수**: {result.get('members_count', '?')}명
""")]


# ============================================================
# C-Level 역할 설정 도구
# ============================================================

@require_team_license
async def team_settings() -> list[TextContent]:
    """팀 설정 조회 (C-Level 역할 활성화 상태)"""
    license_key = _get_license_key()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/settings", "GET", {"license_key": license_key})

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 설정 조회 실패

**오류**: {result['error']}
""")]

    settings = result.get("settings", {})
    enabled_roles = settings.get("enabled_roles", {})

    role_status = "\n".join([
        f"| {role.upper()} | {'✅ 활성화' if enabled else '❌ 비활성화'} |"
        for role, enabled in enabled_roles.items()
    ])

    return [TextContent(type="text", text=f"""
# 팀 C-Level 역할 설정

| 역할 | 상태 |
|------|------|
{role_status}

## 설정 변경
`team_toggle_role` 도구를 사용하세요.
""")]


@require_team_license
async def team_toggle_role(
    cto: bool = None,
    cdo: bool = None,
    cpo: bool = None,
    cfo: bool = None,
    cmo: bool = None
) -> list[TextContent]:
    """C-Level 역할 활성화/비활성화

    Args:
        cto: CTO 역할 (기술)
        cdo: CDO 역할 (디자인)
        cpo: CPO 역할 (제품)
        cfo: CFO 역할 (재무)
        cmo: CMO 역할 (마케팅)
    """
    license_key = _get_license_key()
    requester_email = _get_user_email()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    # 현재 설정 조회
    current = _api_request("/team/settings", "GET", {"license_key": license_key})
    current_roles = current.get("settings", {}).get("enabled_roles", {
        "cto": True, "cdo": True, "cpo": True, "cfo": True, "cmo": True
    })

    # 변경할 값만 업데이트
    enabled_roles = {
        "cto": cto if cto is not None else current_roles.get("cto", True),
        "cdo": cdo if cdo is not None else current_roles.get("cdo", True),
        "cpo": cpo if cpo is not None else current_roles.get("cpo", True),
        "cfo": cfo if cfo is not None else current_roles.get("cfo", True),
        "cmo": cmo if cmo is not None else current_roles.get("cmo", True),
    }

    result = _api_request("/team/settings", "PUT", {
        "license_key": license_key,
        "requester_email": requester_email,
        "settings": {"enabled_roles": enabled_roles}
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 설정 변경 실패

**오류**: {result['error']}
""")]

    new_settings = result.get("settings", {}).get("enabled_roles", {})
    role_status = "\n".join([
        f"| {role.upper()} | {'✅' if enabled else '❌'} |"
        for role, enabled in new_settings.items()
    ])

    return [TextContent(type="text", text=f"""
# ✅ C-Level 역할 설정 변경 완료

| 역할 | 상태 |
|------|------|
{role_status}
""")]


# ============================================================
# 에러 패턴 공유 도구
# ============================================================

@require_team_license
async def sync_team_errors(project_path: str = ".") -> list[TextContent]:
    """로컬 에러 패턴을 팀과 동기화 (업로드)

    Args:
        project_path: 프로젝트 경로 (기본값: 현재 디렉토리)
    """
    license_key = _get_license_key()
    member_email = _get_user_email()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    # 로컬 ERROR_LOG.md 파싱
    error_log_path = Path(project_path) / "ERROR_LOG.md"

    if not error_log_path.exists():
        return [TextContent(type="text", text=f"""
# ❌ ERROR_LOG.md 없음

`{error_log_path}` 파일이 없습니다.

먼저 `/error-log` 또는 `/learn-error`로 에러를 기록하세요.
""")]

    # 간단한 에러 파싱 (실제로는 더 정교한 파싱 필요)
    errors = []
    content = error_log_path.read_text(encoding="utf-8")

    # 에러 블록 추출 (간단한 파싱)
    import re
    error_blocks = re.findall(r'## Error #\d+.*?(?=## Error #|\Z)', content, re.DOTALL)

    for block in error_blocks[:10]:  # 최대 10개
        error_type = re.search(r'타입\s*\|\s*(\w+)', block)
        signature = re.search(r'### 에러 메시지\s*\n(.+)', block)
        never = re.search(r'NEVER:\s*(.+)', block)
        always = re.search(r'ALWAYS:\s*(.+)', block)

        if error_type:
            errors.append({
                "type": error_type.group(1),
                "signature": signature.group(1).strip() if signature else "",
                "never": never.group(1).strip() if never else None,
                "always": always.group(1).strip() if always else None
            })

    if not errors:
        return [TextContent(type="text", text="""
# ⚠️ 동기화할 에러 없음

ERROR_LOG.md에서 에러 패턴을 찾을 수 없습니다.
""")]

    result = _api_request("/team/errors/sync", "POST", {
        "license_key": license_key,
        "member_email": member_email,
        "errors": errors
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 동기화 실패

**오류**: {result['error']}
""")]

    return [TextContent(type="text", text=f"""
# ✅ 에러 패턴 동기화 완료

**동기화된 패턴**: {result.get('synced', 0)}개
**팀 전체 패턴**: {result.get('total_patterns', 0)}개

이제 팀원들이 `get_team_rules`로 공유된 규칙을 가져올 수 있습니다.
""")]


@require_team_license
async def get_team_rules() -> list[TextContent]:
    """팀 공유 NEVER/ALWAYS 규칙 조회"""
    license_key = _get_license_key()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/errors/rules", "GET", {"license_key": license_key})

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 규칙 조회 실패

**오류**: {result['error']}
""")]

    rules = result.get("rules", {})
    never_rules = rules.get("never", [])
    always_rules = rules.get("always", [])

    never_list = "\n".join([
        f"- **{r['type']}** ({r['count']}회): {r['rule']}"
        for r in never_rules
    ]) or "없음"

    always_list = "\n".join([
        f"- **{r['type']}** ({r['count']}회): {r['rule']}"
        for r in always_rules
    ]) or "없음"

    return [TextContent(type="text", text=f"""
# 팀 공유 규칙

## 🚫 NEVER (절대 금지)
{never_list}

## ✅ ALWAYS (항상 수행)
{always_list}

---

이 규칙들을 CLAUDE.md에 추가하려면 `apply_team_rules`를 사용하세요.
""")]


@require_team_license
async def apply_team_rules(project_path: str = ".") -> list[TextContent]:
    """팀 규칙을 로컬 CLAUDE.md에 적용

    Args:
        project_path: 프로젝트 경로 (기본값: 현재 디렉토리)
    """
    license_key = _get_license_key()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    # 팀 규칙 조회
    result = _api_request("/team/errors/rules", "GET", {"license_key": license_key})

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 규칙 조회 실패

**오류**: {result['error']}
""")]

    rules = result.get("rules", {})
    never_rules = rules.get("never", [])
    always_rules = rules.get("always", [])

    if not never_rules and not always_rules:
        return [TextContent(type="text", text="# ⚠️ 적용할 팀 규칙이 없습니다.")]

    # CLAUDE.md 경로
    claude_md_path = Path(project_path) / "CLAUDE.md"

    # 팀 규칙 섹션 생성
    team_section = f"""

## 팀 공유 규칙 (자동 동기화됨)

> 마지막 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### NEVER (팀 공통)
"""
    for r in never_rules:
        team_section += f"- {r['rule']} ({r['type']}, {r['count']}회 발생)\n"

    team_section += "\n### ALWAYS (팀 공통)\n"
    for r in always_rules:
        team_section += f"- {r['rule']} ({r['type']}, {r['count']}회 발생)\n"

    # CLAUDE.md에 추가 또는 업데이트
    if claude_md_path.exists():
        content = claude_md_path.read_text(encoding="utf-8")

        # 기존 팀 규칙 섹션 제거
        import re
        content = re.sub(
            r'\n## 팀 공유 규칙 \(자동 동기화됨\).*?(?=\n## |\Z)',
            '',
            content,
            flags=re.DOTALL
        )

        content += team_section
    else:
        content = f"# CLAUDE.md\n{team_section}"

    claude_md_path.write_text(content, encoding="utf-8")

    return [TextContent(type="text", text=f"""
# ✅ 팀 규칙 적용 완료

**파일**: {claude_md_path}
**NEVER 규칙**: {len(never_rules)}개
**ALWAYS 규칙**: {len(always_rules)}개

CLAUDE.md에 팀 공유 규칙이 추가되었습니다.
""")]


# ============================================================
# 프로젝트 컨텍스트 동기화 도구
# ============================================================

@require_team_license
async def sync_project_context(
    project_path: str = ".",
    project_id: str = None
) -> list[TextContent]:
    """프로젝트 컨텍스트를 팀과 동기화

    Args:
        project_path: 프로젝트 경로
        project_id: 프로젝트 ID (기본값: 폴더명)
    """
    license_key = _get_license_key()
    member_email = _get_user_email()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    project_root = Path(project_path).resolve()
    if not project_id:
        project_id = project_root.name

    context = {}

    # PRD 읽기
    prd_paths = [
        project_root / "docs" / "PRD.md",
        project_root / "PRD.md",
        project_root / "docs" / "prd.md"
    ]
    for prd_path in prd_paths:
        if prd_path.exists():
            context["prd"] = prd_path.read_text(encoding="utf-8")[:5000]  # 5KB 제한
            break

    # CLAUDE.md 읽기
    claude_md_path = project_root / "CLAUDE.md"
    if claude_md_path.exists():
        context["claude_md"] = claude_md_path.read_text(encoding="utf-8")[:3000]

    # 파일 구조 (간단히)
    structure = []
    for f in project_root.glob("**/*.py"):
        if ".venv" not in str(f) and "node_modules" not in str(f):
            structure.append(str(f.relative_to(project_root)))
    for f in project_root.glob("**/*.ts"):
        if "node_modules" not in str(f):
            structure.append(str(f.relative_to(project_root)))
    context["structure"] = "\n".join(structure[:50])  # 최대 50개 파일

    if not context:
        return [TextContent(type="text", text="# ⚠️ 동기화할 컨텍스트가 없습니다.")]

    result = _api_request("/team/project/sync", "POST", {
        "license_key": license_key,
        "member_email": member_email,
        "project_id": project_id,
        "context": context
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 컨텍스트 동기화 실패

**오류**: {result['error']}
""")]

    return [TextContent(type="text", text=f"""
# ✅ 프로젝트 컨텍스트 동기화 완료

**프로젝트 ID**: {project_id}
**PRD**: {'✅' if context.get('prd') else '❌'}
**CLAUDE.md**: {'✅' if context.get('claude_md') else '❌'}
**파일 구조**: {len(structure)}개 파일

팀원들이 이 프로젝트의 컨텍스트를 조회할 수 있습니다.
""")]


@require_team_license
async def get_project_context(project_id: str) -> list[TextContent]:
    """팀 프로젝트 컨텍스트 조회

    Args:
        project_id: 프로젝트 ID
    """
    license_key = _get_license_key()

    if not license_key:
        return [TextContent(type="text", text="# ❌ 라이선스 키를 찾을 수 없습니다.")]

    result = _api_request("/team/project", "GET", {
        "license_key": license_key,
        "project_id": project_id
    })

    if result.get("error"):
        return [TextContent(type="text", text=f"""
# ❌ 컨텍스트 조회 실패

**오류**: {result['error']}
""")]

    context = result.get("context", {})

    if not context:
        return [TextContent(type="text", text=f"""
# ⚠️ 프로젝트 컨텍스트 없음

프로젝트 ID `{project_id}`의 컨텍스트가 없습니다.
먼저 `sync_project_context`로 동기화하세요.
""")]

    decisions = context.get("decisions", [])
    decision_list = "\n".join([
        f"- **{d['what']}**: {d['why']} ({d.get('recorded_by', 'N/A')})"
        for d in decisions
    ]) or "없음"

    return [TextContent(type="text", text=f"""
# 프로젝트 컨텍스트: {project_id}

**마지막 업데이트**: {result.get('updated_at', 'N/A')[:10]}
**업데이트 by**: {result.get('updated_by', 'N/A')}

## PRD 요약
{context.get('prd', '없음')[:500]}{'...' if len(context.get('prd', '')) > 500 else ''}

## 결정사항
{decision_list}

## 파일 구조
```
{context.get('structure', '없음')[:1000]}
```
""")]
