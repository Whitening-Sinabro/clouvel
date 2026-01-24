# -*- coding: utf-8 -*-
"""Core tools: can_code, scan_docs, analyze_docs, init_docs"""

import re
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

# 필수 문서 정의
REQUIRED_DOCS = [
    {"type": "prd", "name": "PRD", "patterns": [r"prd", r"product.?requirement"], "priority": "critical"},
    {"type": "architecture", "name": "아키텍처", "patterns": [r"architect", r"arch", r"module"], "priority": "warn"},  # B4: WARN으로 변경
    {"type": "api_spec", "name": "API 스펙", "patterns": [r"api", r"swagger", r"openapi"], "priority": "warn"},
    {"type": "db_schema", "name": "DB 스키마", "patterns": [r"schema", r"database", r"db"], "priority": "warn"},
    {"type": "verification", "name": "검증 계획", "patterns": [r"verif", r"test.?plan"], "priority": "warn"},
]

# PRD 필수 섹션 (B4: acceptance 없으면 BLOCK)
REQUIRED_PRD_SECTIONS = [
    {"name": "acceptance", "patterns": [r"##\s*(acceptance|완료\s*기준|수락\s*조건|done\s*when)"], "priority": "critical"},
    {"name": "scope", "patterns": [r"##\s*(scope|범위|목표)"], "priority": "warn"},
    {"name": "non_goals", "patterns": [r"##\s*(non.?goals?|하지\s*않을|제외|out\s*of\s*scope)"], "priority": "warn"},
]


def _find_prd_file(docs_path: Path) -> Path | None:
    """PRD 파일 찾기"""
    for f in docs_path.iterdir():
        if f.is_file():
            name_lower = f.name.lower()
            if "prd" in name_lower or "product" in name_lower and "requirement" in name_lower:
                return f
    return None


def _check_prd_sections(prd_path: Path) -> tuple[list[str], list[str], list[str]]:
    """PRD 파일 내용에서 필수 섹션 확인
    Returns: (found_critical, missing_critical, missing_warn)
    """
    try:
        content = prd_path.read_text(encoding='utf-8')
    except Exception:
        return [], ["acceptance"], []

    found_critical = []
    missing_critical = []
    missing_warn = []

    for section in REQUIRED_PRD_SECTIONS:
        found = False
        for pattern in section["patterns"]:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                found = True
                break

        if found:
            if section["priority"] == "critical":
                found_critical.append(section["name"])
        else:
            if section["priority"] == "critical":
                missing_critical.append(section["name"])
            else:
                missing_warn.append(section["name"])

    return found_critical, missing_critical, missing_warn


def _check_tests(project_path: Path) -> tuple[int, list[str]]:
    """테스트 파일 확인
    Returns: (test_count, test_files)
    """
    test_patterns = [r"test_.*\.py$", r".*_test\.py$", r".*\.test\.(ts|js)$", r".*\.spec\.(ts|js)$"]
    test_files = []

    # 프로젝트 루트와 하위 폴더에서 테스트 파일 검색
    search_paths = [project_path]
    for subdir in ["tests", "test", "src", "__tests__"]:
        subpath = project_path / subdir
        if subpath.exists():
            search_paths.append(subpath)

    for search_path in search_paths:
        if not search_path.exists():
            continue
        try:
            for f in search_path.rglob("*"):
                try:
                    if f.is_file():
                        for pattern in test_patterns:
                            if re.match(pattern, f.name, re.IGNORECASE):
                                test_files.append(str(f.relative_to(project_path)))
                                break
                except (OSError, PermissionError):
                    # 심볼릭 링크 깨짐, 접근 권한 없음 등 무시
                    continue
        except (OSError, PermissionError):
            continue

    return len(test_files), test_files[:5]  # 최대 5개만 반환


async def can_code(path: str) -> list[TextContent]:
    """코딩 가능 여부 확인 - 핵심 기능 (B4: 품질 게이트 확장)"""
    docs_path = Path(path)
    project_path = docs_path.parent if docs_path.name == "docs" else docs_path

    if not docs_path.exists():
        return [TextContent(type="text", text=f"""
# ⛔ BLOCK: 코딩 금지

## 이유
docs 폴더가 없습니다: `{path}`

## 지금 해야 할 것
1. `docs` 폴더를 생성하세요
2. PRD(제품 요구사항 문서)를 먼저 작성하세요
3. `get_prd_template` 도구로 템플릿을 생성할 수 있습니다

## 왜?
PRD 없이 코딩하면:
- 요구사항 불명확 → 재작업
- 예외 케이스 누락 → 버그
- 팀원 간 인식 차이 → 충돌

**문서 먼저, 코딩은 나중에.**

사용자에게 PRD 작성을 도와주겠다고 말하세요.
""")]

    files = [f for f in docs_path.iterdir() if f.is_file()]
    file_names = [f.name.lower() for f in files]

    detected_critical = []
    detected_warn = []
    missing_critical = []
    missing_warn = []

    for req in REQUIRED_DOCS:
        found = False
        for filename in file_names:
            for pattern in req["patterns"]:
                if re.search(pattern, filename, re.IGNORECASE):
                    if req["priority"] == "critical":
                        detected_critical.append(req["name"])
                    else:
                        detected_warn.append(req["name"])
                    found = True
                    break
            if found:
                break
        if not found:
            if req["priority"] == "critical":
                missing_critical.append(req["name"])
            else:
                missing_warn.append(req["name"])

    # B4: PRD 내용 검사 (acceptance 섹션 필수)
    prd_file = _find_prd_file(docs_path)
    prd_sections_found = []
    prd_sections_missing_critical = []
    prd_sections_missing_warn = []

    if prd_file:
        prd_sections_found, prd_sections_missing_critical, prd_sections_missing_warn = _check_prd_sections(prd_file)

    # B4: 테스트 파일 확인
    test_count, test_files = _check_tests(project_path)

    # BLOCK 조건: PRD 없음 OR acceptance 섹션 없음
    if missing_critical or prd_sections_missing_critical:
        all_missing_critical = missing_critical + [f"PRD의 {s} 섹션" for s in prd_sections_missing_critical]
        detected_list = "\n".join(f"- {d}" for d in detected_critical + detected_warn) if (detected_critical or detected_warn) else "없음"

        return [TextContent(type="text", text=f"""
# ⛔ BLOCK: 코딩 금지

## 현재 상태
✅ 있음:
{detected_list}

❌ 없음 (필수 - BLOCK):
{chr(10).join(f'- {m}' for m in all_missing_critical)}

## 지금 해야 할 것
코드를 작성하지 마세요. 대신:

1. 누락된 문서/섹션을 먼저 작성하세요
2. **PRD에 acceptance(완료 기준) 섹션이 필수입니다**
3. `get_prd_guide` 도구로 작성법을 확인하세요
4. `get_prd_template` 도구로 템플릿을 생성하세요

## 사용자에게 전달할 메시지
"코드를 작성하기 전에 먼저 문서를 준비해야 합니다.
필수 항목이 없습니다: {', '.join(all_missing_critical)}
제가 PRD 작성을 도와드릴까요?"

**절대 코드를 작성하지 마세요. 문서 작성을 도와주세요.**
""")]

    # WARN 조건: 아키텍처 없음, 테스트 0개 등
    warn_count = len(missing_warn) + len(prd_sections_missing_warn) + (1 if test_count == 0 else 0)

    # 짧은 요약 형식
    found_docs = ", ".join(detected_critical) if detected_critical else "없음"
    warn_items = missing_warn + [f"PRD.{s}" for s in prd_sections_missing_warn]
    if test_count == 0:
        warn_items.append("테스트")
    warn_summary = ", ".join(warn_items) if warn_items else "없음"

    test_info = f" | 테스트 {test_count}개" if test_count > 0 else ""

    # PRD 수정 관련 지시
    prd_rule = "\n\n⚠️ PRD 수정 규칙: 사용자 명시 요청 없이 PRD 임의 수정 금지. 수정이 필요하다면 (1) 수정 필요 이유 (2) 개선 시 이득 (3) 구체적 변경안을 먼저 제안하고 승인 후 진행."

    if warn_count > 0:
        return [TextContent(type="text", text=f"✅ PASS | ⚠️ WARN {warn_count}개 | 필수: {found_docs} ✓{test_info} | 권장 없음: {warn_summary}{prd_rule}")]
    else:
        return [TextContent(type="text", text=f"✅ PASS | 필수: {found_docs} ✓{test_info} | 코딩 시작 가능{prd_rule}")]


async def scan_docs(path: str) -> list[TextContent]:
    """docs 폴더 스캔"""
    docs_path = Path(path)

    if not docs_path.exists():
        return [TextContent(type="text", text=f"경로 없음: {path}")]

    if not docs_path.is_dir():
        return [TextContent(type="text", text=f"디렉토리 아님: {path}")]

    files = []
    for f in sorted(docs_path.iterdir()):
        if f.is_file():
            stat = f.stat()
            files.append(f"{f.name} ({stat.st_size:,} bytes)")

    result = f"📁 {path}\n총 {len(files)}개 파일\n\n"
    result += "\n".join(files)

    return [TextContent(type="text", text=result)]


async def analyze_docs(path: str) -> list[TextContent]:
    """docs 폴더 분석"""
    docs_path = Path(path)

    if not docs_path.exists():
        return [TextContent(type="text", text=f"경로 없음: {path}")]

    files = [f.name.lower() for f in docs_path.iterdir() if f.is_file()]
    detected = []
    missing = []

    for req in REQUIRED_DOCS:
        found = False
        for filename in files:
            for pattern in req["patterns"]:
                if re.search(pattern, filename, re.IGNORECASE):
                    detected.append(req["name"])
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(req["name"])

    critical_total = len([r for r in REQUIRED_DOCS if r["priority"] == "critical"])
    critical_found = len([r for r in REQUIRED_DOCS if r["priority"] == "critical" and r["name"] in detected])
    coverage = critical_found / critical_total if critical_total > 0 else 1.0

    result = f"## 분석 결과: {path}\n\n"
    result += f"커버리지: {coverage:.0%}\n\n"

    if detected:
        result += "### 있음\n" + "\n".join(f"- {d}" for d in detected) + "\n\n"

    if missing:
        result += "### 없음 (작성 필요)\n" + "\n".join(f"- {m}" for m in missing) + "\n\n"

    if not missing:
        result += "✅ 필수 문서 다 있음. 바이브코딩 시작해도 됨.\n"
    else:
        result += f"⛔ {len(missing)}개 문서 먼저 작성하고 코딩 시작할 것.\n"

    return [TextContent(type="text", text=result)]


async def init_docs(path: str, project_name: str) -> list[TextContent]:
    """docs 폴더 초기화 + 템플릿 생성"""
    project_path = Path(path)
    docs_path = project_path / "docs"

    docs_path.mkdir(parents=True, exist_ok=True)

    templates = {
        "PRD.md": f"# {project_name} PRD\n\n> 작성일: {datetime.now().strftime('%Y-%m-%d')}\n\n## 한 줄 요약\n\n[작성 필요]\n\n## Acceptance (완료 기준)\n\n- [ ] [완료 조건 1]\n- [ ] [완료 조건 2]\n- [ ] [완료 조건 3]\n",
        "ARCHITECTURE.md": f"# {project_name} 아키텍처\n\n## 시스템 구조\n\n[작성 필요]\n",
        "API.md": f"# {project_name} API 스펙\n\n## 엔드포인트\n\n[작성 필요]\n",
        "DATABASE.md": f"# {project_name} DB 스키마\n\n## 테이블\n\n[작성 필요]\n",
        "VERIFICATION.md": f"# {project_name} 검증 계획\n\n## 테스트 케이스\n\n[작성 필요]\n",
    }

    created = []
    for filename, content in templates.items():
        file_path = docs_path / filename
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
            created.append(filename)

    result = f"## docs 폴더 초기화 완료\n\n경로: `{docs_path}`\n\n"
    if created:
        result += "### 생성된 파일\n" + "\n".join(f"- {f}" for f in created) + "\n\n"
    else:
        result += "모든 파일이 이미 존재합니다.\n\n"

    result += "### 다음 단계\n1. PRD.md부터 작성하세요\n2. `get_prd_guide` 도구로 작성법을 확인하세요\n"

    return [TextContent(type="text", text=result)]
