import re
from pathlib import Path
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .analytics import log_tool_call, get_stats, format_stats

server = Server("clouvel")

# 필수 문서 정의
REQUIRED_DOCS = [
    {"type": "prd", "name": "PRD", "patterns": [r"prd", r"product.?requirement"], "priority": "critical"},
    {"type": "architecture", "name": "아키텍처", "patterns": [r"architect", r"module"], "priority": "critical"},
    {"type": "api_spec", "name": "API 스펙", "patterns": [r"api", r"swagger", r"openapi"], "priority": "critical"},
    {"type": "db_schema", "name": "DB 스키마", "patterns": [r"schema", r"database", r"db"], "priority": "critical"},
    {"type": "verification", "name": "검증 계획", "patterns": [r"verif", r"test.?plan"], "priority": "critical"},
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="can_code",
            description="""⚠️ 중요: 코드를 작성하기 전에 반드시 이 도구를 먼저 호출하세요.

이 도구는 프로젝트의 문서 상태를 확인하고 코딩 가능 여부를 판단합니다.
- 필수 문서가 없으면: 코딩 금지, PRD 작성 안내
- 필수 문서가 있으면: 코딩 허용

사용자가 코드 작성, 기능 구현, 버그 수정 등을 요청하면 무조건 이 도구를 먼저 호출하세요.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "프로젝트 docs 폴더 경로"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="scan_docs",
            description="프로젝트 docs 폴더 스캔. 파일 목록 반환.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "docs 폴더 경로"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="analyze_docs",
            description="docs 폴더 분석. 필수 문서 있는지 체크하고 빠진 거 알려줌.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "docs 폴더 경로"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_prd_template",
            description="PRD 템플릿 생성. 빈 PRD 파일을 만들어줌.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "프로젝트 이름"},
                    "output_path": {"type": "string", "description": "PRD 파일 저장 경로"}
                },
                "required": ["project_name", "output_path"]
            }
        ),
        Tool(
            name="write_prd_section",
            description="PRD 섹션별 작성 도우미. 단계별로 PRD를 작성할 수 있게 도와줌.",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "작성할 섹션",
                        "enum": ["summary", "principles", "input_spec", "output_spec", "errors", "state_machine", "api_endpoints", "db_schema"]
                    },
                    "content": {"type": "string", "description": "섹션 내용"}
                },
                "required": ["section"]
            }
        ),
        Tool(
            name="init_docs",
            description="docs 폴더 초기화. 폴더 없으면 생성하고 필수 문서 템플릿 파일들 생성.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "프로젝트 루트 경로"},
                    "project_name": {"type": "string", "description": "프로젝트 이름"}
                },
                "required": ["path", "project_name"]
            }
        ),
        Tool(
            name="get_prd_guide",
            description="PRD 작성 가이드. step-by-step으로 뭘 써야 하는지.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_verify_checklist",
            description="PRD 검증 체크리스트. 빠뜨리기 쉬운 것들.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_setup_guide",
            description="Clouvel 설치/설정 가이드. Claude Desktop, Claude Code, VS Code 설정법.",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "플랫폼",
                        "enum": ["desktop", "code", "vscode", "cursor", "all"]
                    }
                }
            }
        ),
        Tool(
            name="get_analytics",
            description="Clouvel 도구 사용량 통계. 어떤 도구가 얼마나 쓰였는지 확인.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "프로젝트 경로 (기본: 현재 디렉토리)"},
                    "days": {"type": "integer", "description": "조회 기간 (기본: 30일)"}
                }
            }
        ),
        Tool(
            name="init_clouvel",
            description="""🚀 Clouvel 온보딩. 처음 사용자에게 플랫폼 선택을 안내하고 맞춤 설정을 도와줌.

사용자가 Clouvel을 처음 사용하거나 설정이 필요할 때 이 도구를 호출하세요.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "사용 환경",
                        "enum": ["desktop", "vscode", "cli", "ask"]
                    }
                }
            }
        ),
        Tool(
            name="setup_cli",
            description="""CLI(Claude Code) 환경 설정. hooks, CLAUDE.md 규칙, pre-commit hook을 자동 생성.

Claude Code에서 "PRD 없으면 코딩 금지"를 강제하기 위한 설정.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "프로젝트 루트 경로"},
                    "level": {
                        "type": "string",
                        "description": "강제 수준",
                        "enum": ["remind", "strict", "full"]
                    }
                },
                "required": ["path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Analytics: 도구 호출 기록 (get_analytics 제외 - 무한 루프 방지)
    project_path = arguments.get("path", None)
    if name != "get_analytics":
        try:
            log_tool_call(name, success=True, project_path=project_path)
        except Exception:
            pass  # analytics 실패해도 도구는 동작해야 함

    if name == "can_code":
        return await _can_code(arguments.get("path", ""))
    elif name == "scan_docs":
        return await _scan_docs(arguments.get("path", ""))
    elif name == "analyze_docs":
        return await _analyze_docs(arguments.get("path", ""))
    elif name == "get_prd_template":
        return await _get_prd_template(
            arguments.get("project_name", ""),
            arguments.get("output_path", "")
        )
    elif name == "write_prd_section":
        return await _write_prd_section(
            arguments.get("section", ""),
            arguments.get("content", "")
        )
    elif name == "init_docs":
        return await _init_docs(
            arguments.get("path", ""),
            arguments.get("project_name", "")
        )
    elif name == "get_prd_guide":
        return await _get_prd_guide()
    elif name == "get_verify_checklist":
        return await _get_verify_checklist()
    elif name == "get_setup_guide":
        return await _get_setup_guide(arguments.get("platform", "all"))
    elif name == "get_analytics":
        return await _get_analytics(
            arguments.get("path", None),
            arguments.get("days", 30)
        )
    elif name == "init_clouvel":
        return await _init_clouvel(arguments.get("platform", "ask"))
    elif name == "setup_cli":
        return await _setup_cli(
            arguments.get("path", ""),
            arguments.get("level", "remind")
        )
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _can_code(path: str) -> list[TextContent]:
    """코딩 가능 여부 확인 - 핵심 기능"""
    docs_path = Path(path)

    # docs 폴더 없음
    if not docs_path.exists():
        return [TextContent(type="text", text=f"""
# ⛔ 코딩 금지

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

    # 필수 문서 부족
    if missing:
        missing_list = "\n".join(f"- {m}" for m in missing)
        detected_list = "\n".join(f"- {d}" for d in detected) if detected else "없음"

        return [TextContent(type="text", text=f"""
# ⛔ 코딩 금지

## 현재 상태
✅ 있음:
{detected_list}

❌ 없음 (필수):
{missing_list}

## 지금 해야 할 것
코드를 작성하지 마세요. 대신:

1. 누락된 문서를 먼저 작성하세요
2. 특히 **PRD**가 가장 중요합니다
3. `get_prd_guide` 도구로 작성법을 확인하세요
4. `get_prd_template` 도구로 템플릿을 생성하세요

## 사용자에게 전달할 메시지
"코드를 작성하기 전에 먼저 문서를 준비해야 합니다.
{len(missing)}개의 필수 문서가 없습니다: {', '.join(missing)}
제가 PRD 작성을 도와드릴까요?"

**절대 코드를 작성하지 마세요. 문서 작성을 도와주세요.**
""")]

    # 모든 필수 문서 있음 → 코딩 허용
    return [TextContent(type="text", text=f"""
# ✅ 코딩 가능

## 문서 상태
모든 필수 문서가 준비되어 있습니다:
{chr(10).join(f'- {d}' for d in detected)}

## 코딩 시작 전 확인사항
1. PRD에 명시된 요구사항을 따르세요
2. API 스펙에 맞게 구현하세요
3. DB 스키마를 참고하세요
4. 검증 계획에 따라 테스트하세요

이제 사용자의 요청에 따라 코드를 작성해도 됩니다.
""")]


async def _scan_docs(path: str) -> list[TextContent]:
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


async def _analyze_docs(path: str) -> list[TextContent]:
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


async def _get_prd_template(project_name: str, output_path: str) -> list[TextContent]:
    """PRD 템플릿 생성"""
    template = f"""# {project_name} PRD

> 이 문서가 법. 여기 없으면 안 만듦.
> 작성일: {datetime.now().strftime('%Y-%m-%d')}

---

## 1. 한 줄 요약
<!-- 프로젝트가 뭔지 한 문장으로. 못 쓰면 정리 안 된 거임. -->

[여기에 작성]

---

## 2. 핵심 원칙

> 절대 안 변하는 것들. 이거 기준으로 기능 판단.

1. [원칙 1]
2. [원칙 2]
3. [원칙 3]

---

## 3. 용어 정의

| 용어 | 설명 |
|------|------|
| [용어1] | [설명] |
| [용어2] | [설명] |

---

## 4. 기능 목록

### 4.1 핵심 기능 (MVP)
- [ ] [기능 1]
- [ ] [기능 2]

### 4.2 추가 기능 (Phase 2)
- [ ] [기능 3]

---

## 5. 입력 스펙

### 5.1 [API/기능명]

| 필드 | 타입 | 필수 | 제한 | 검증 | 예시 |
|------|------|------|------|------|------|
| [필드명] | string | O | 1~100자 | 빈문자열X | "예시값" |
| [필드명] | number | O | 1~9999 | 양수만 | 100 |
| [필드명] | enum | X | - | 목록 내 | "option1" |

#### enum 옵션

| 필드 | 옵션 | 설명 |
|------|------|------|
| [필드명] | option1 | [설명] |
| [필드명] | option2 | [설명] |

---

## 6. 출력 스펙

### 6.1 성공 응답

```json
{{
  "success": true,
  "data": {{
    "id": "abc123",
    "createdAt": "2024-01-01T00:00:00Z",
    "result": {{}}
  }}
}}
```

### 6.2 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| id | string | 고유 식별자 |
| createdAt | datetime | 생성 시각 (ISO 8601) |

---

## 7. 에러 코드

| 상황 | 코드 | HTTP | 메시지 |
|------|------|------|--------|
| 잔액 부족 | INSUFFICIENT_CREDITS | 402 | "크레딧 부족. 필요: {{required}}, 보유: {{available}}" |
| 권한 없음 | UNAUTHORIZED | 401 | "인증이 필요합니다" |
| 잘못된 요청 | INVALID_REQUEST | 400 | "{{field}} 필드가 잘못되었습니다" |
| 서버 오류 | INTERNAL_ERROR | 500 | "서버 오류가 발생했습니다" |

---

## 8. 상태 머신

```
[상태1] --이벤트1--> [상태2] --이벤트2--> [상태3]
                         |
                         +--실패--> [에러상태]
```

### 상태 설명

| 상태 | 설명 | 진입 조건 |
|------|------|----------|
| [상태1] | [설명] | 초기 상태 |
| [상태2] | [설명] | [이벤트] 발생 시 |

---

## 9. API 엔드포인트

### 9.1 [API명]

```
POST /v1/[endpoint]
```

**Request:**
```json
{{
  "field": "value"
}}
```

**Response:**
```json
{{
  "success": true
}}
```

---

## 10. 데이터 정책

| 항목 | 무료 | 유료 |
|------|------|------|
| 보관 기간 | 24시간 | 7일 |
| 용량 제한 | 10MB | 100MB |
| API 호출 | 100/일 | 무제한 |

---

## 11. 검증 계획

### 11.1 단위 테스트
- [ ] [테스트 케이스 1]
- [ ] [테스트 케이스 2]

### 11.2 통합 테스트
- [ ] [테스트 케이스]

### 11.3 엣지 케이스
- [ ] 빈 입력값
- [ ] 최대 길이 초과
- [ ] 특수문자 포함
- [ ] 동시 요청

---

## 부록

### A. 참고 자료
- [링크1]

### B. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| {datetime.now().strftime('%Y-%m-%d')} | 1.0 | 초안 작성 | |
"""

    # 파일 저장
    if output_path:
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(template, encoding='utf-8')
            return [TextContent(type="text", text=f"✅ PRD 템플릿 생성 완료: {output_path}\n\n이제 각 섹션을 채워주세요.")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ 파일 저장 실패: {e}\n\n아래 템플릿을 직접 복사해서 사용하세요:\n\n{template}")]

    return [TextContent(type="text", text=template)]


async def _write_prd_section(section: str, content: str) -> list[TextContent]:
    """PRD 섹션별 작성 가이드"""
    guides = {
        "summary": """## 한 줄 요약 작성법

**목적**: 프로젝트를 한 문장으로 설명

**좋은 예시**:
- "한 번 라이브로 일주일치 콘텐츠 생성"
- "음성만으로 회의록 자동 작성"
- "코드 리뷰를 자동화하는 AI 봇"

**나쁜 예시**:
- "좋은 서비스" (너무 추상적)
- "AI를 활용한 혁신적인..." (마케팅 문구)

**체크리스트**:
- [ ] 10단어 이내인가?
- [ ] 누가 봐도 이해되는가?
- [ ] "그래서 뭘 하는 건데?"에 답이 되는가?

지금 한 줄 요약을 작성해주세요.""",

        "principles": """## 핵심 원칙 작성법

**목적**: 의사결정의 기준이 되는 불변의 원칙

**좋은 예시**:
1. 원가 보호 - 절대 손해 보지 않음
2. 무료 체험 - 결제 전 가치 확인 가능
3. 현금 유입 - 모든 기능은 수익으로 연결

**나쁜 예시**:
- "좋은 UX" (측정 불가)
- "빠르게 개발" (원칙이 아닌 방법)

**체크리스트**:
- [ ] 3개 이하인가?
- [ ] 충돌 시 우선순위가 명확한가?
- [ ] 기능 추가 시 판단 기준이 되는가?

지금 핵심 원칙 3개를 작성해주세요.""",

        "input_spec": """## 입력 스펙 작성법

**목적**: 모든 입력값의 정확한 정의

**필수 항목**:
| 필드 | 타입 | 필수 | 제한 | 검증 | 예시 |
|------|------|------|------|------|------|
| name | string | O | 1~100자 | 빈문자열X | "홍길동" |
| age | number | O | 1~150 | 정수만 | 25 |
| type | enum | X | - | 목록 내 | "premium" |

**체크리스트**:
- [ ] 모든 필드에 타입이 있는가?
- [ ] 문자열에 길이 제한이 있는가?
- [ ] 숫자에 범위가 있는가?
- [ ] enum에 가능한 값 목록이 있는가?
- [ ] 예시가 있는가?

지금 입력 스펙을 작성해주세요.""",

        "output_spec": """## 출력 스펙 작성법

**목적**: API 응답의 정확한 구조

**필수 항목**:
```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "createdAt": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "page": 1,
    "total": 100
  }
}
```

**체크리스트**:
- [ ] 실제 JSON 형태로 작성했는가?
- [ ] 모든 필드 타입이 명확한가?
- [ ] null이 올 수 있는 필드가 표시되어 있는가?
- [ ] 날짜 형식이 명시되어 있는가? (ISO 8601)
- [ ] 페이지네이션이 필요하면 포함했는가?

지금 출력 스펙을 작성해주세요.""",

        "errors": """## 에러 테이블 작성법

**목적**: 모든 에러 상황의 정의

**형식**:
| 상황 | 코드 | HTTP | 메시지 |
|------|------|------|--------|
| 잔액 부족 | INSUFFICIENT_CREDITS | 402 | "크레딧 부족. 필요: {n}" |

**규칙**:
- 코드는 SNAKE_CASE
- 메시지에 동적 값은 {중괄호}로 표시
- HTTP 상태 코드 필수

**체크리스트**:
- [ ] 인증 에러가 있는가?
- [ ] 권한 에러가 있는가?
- [ ] 입력값 검증 에러가 있는가?
- [ ] 비즈니스 로직 에러가 있는가?
- [ ] 서버 에러가 있는가?

지금 에러 테이블을 작성해주세요.""",

        "state_machine": """## 상태 머신 작성법

**목적**: 복잡한 플로우의 시각화

**형식**:
```
[available] --reserve--> [reserved] --capture--> [completed]
                              |
                              +--timeout--> [expired]
                              |
                              +--cancel--> [cancelled]
```

**체크리스트**:
- [ ] 시작 상태가 있는가?
- [ ] 종료 상태가 있는가?
- [ ] 모든 전이에 이벤트명이 있는가?
- [ ] 실패/에러 경로가 있는가?
- [ ] 타임아웃 처리가 있는가?

지금 상태 머신을 작성해주세요.""",

        "api_endpoints": """## API 엔드포인트 작성법

**목적**: REST API 명세

**형식**:
```
POST /v1/orders
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "productId": "abc123",
  "quantity": 1
}

Response (201):
{
  "orderId": "ord_123",
  "status": "created"
}
```

**체크리스트**:
- [ ] /v1/ 버전 prefix가 있는가?
- [ ] HTTP 메서드가 적절한가? (GET=조회, POST=생성, PUT=수정, DELETE=삭제)
- [ ] 인증 방식이 명시되어 있는가?
- [ ] 성공/실패 응답 코드가 있는가?

지금 API 엔드포인트를 작성해주세요.""",

        "db_schema": """## DB 스키마 작성법

**목적**: 데이터 구조 정의

**형식**:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**체크리스트**:
- [ ] 기본키가 있는가?
- [ ] 외래키 관계가 명확한가?
- [ ] 인덱스가 필요한 컬럼에 있는가?
- [ ] NOT NULL 제약이 적절한가?
- [ ] 기본값이 설정되어 있는가?

지금 DB 스키마를 작성해주세요."""
    }

    guide = guides.get(section, "알 수 없는 섹션입니다.")
    return [TextContent(type="text", text=guide)]


async def _init_docs(path: str, project_name: str) -> list[TextContent]:
    """docs 폴더 초기화 - 필수 문서 템플릿 생성"""
    from datetime import datetime

    project_path = Path(path)
    docs_path = project_path / "docs"

    # docs 폴더 생성
    docs_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    # 1. PRD.md
    prd_content = f"""# {project_name} PRD

> 이 문서가 법. 여기 없으면 안 만듦.
> 작성일: {datetime.now().strftime('%Y-%m-%d')}

---

## 1. 한 줄 요약
<!-- 프로젝트가 뭔지 한 문장으로 -->

[여기에 작성]

---

## 2. 핵심 원칙

1. [원칙 1]
2. [원칙 2]
3. [원칙 3]

---

## 3. 기능 목록

### MVP
- [ ] [기능 1]
- [ ] [기능 2]

---

## 4. 입력 스펙

| 필드 | 타입 | 필수 | 제한 | 예시 |
|------|------|------|------|------|
| | | | | |

---

## 5. 출력 스펙

```json
{{
  "success": true,
  "data": {{}}
}}
```

---

## 6. 에러 코드

| 상황 | 코드 | HTTP | 메시지 |
|------|------|------|--------|
| | | | |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| {datetime.now().strftime('%Y-%m-%d')} | 1.0 | 초안 |
"""
    prd_file = docs_path / "PRD.md"
    if not prd_file.exists():
        prd_file.write_text(prd_content, encoding='utf-8')
        created_files.append("PRD.md")

    # 2. ARCHITECTURE.md
    arch_content = f"""# {project_name} 아키텍처

## 시스템 구조

```
[클라이언트] --> [API 서버] --> [데이터베이스]
                    |
                    v
              [외부 서비스]
```

## 기술 스택

| 구분 | 기술 | 이유 |
|------|------|------|
| 언어 | | |
| 프레임워크 | | |
| 데이터베이스 | | |

## 디렉토리 구조

```
src/
├── api/          # API 라우터
├── services/     # 비즈니스 로직
├── models/       # 데이터 모델
└── utils/        # 유틸리티
```

## 주요 모듈

### [모듈명]
- 역할:
- 의존성:
"""
    arch_file = docs_path / "ARCHITECTURE.md"
    if not arch_file.exists():
        arch_file.write_text(arch_content, encoding='utf-8')
        created_files.append("ARCHITECTURE.md")

    # 3. API.md
    api_content = f"""# {project_name} API 스펙

## Base URL
```
https://api.example.com/v1
```

## 인증
```
Authorization: Bearer {{token}}
```

---

## 엔드포인트

### [기능명]

```
POST /v1/endpoint
```

**Request:**
```json
{{
  "field": "value"
}}
```

**Response (200):**
```json
{{
  "success": true,
  "data": {{}}
}}
```

**Errors:**
| 코드 | HTTP | 설명 |
|------|------|------|
| | | |
"""
    api_file = docs_path / "API.md"
    if not api_file.exists():
        api_file.write_text(api_content, encoding='utf-8')
        created_files.append("API.md")

    # 4. DATABASE.md
    db_content = f"""# {project_name} DB 스키마

## ERD

```
[users] 1--* [orders] *--1 [products]
```

## 테이블

### users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### [테이블명]
```sql
-- 여기에 작성
```

## 인덱스

| 테이블 | 인덱스 | 컬럼 | 이유 |
|--------|--------|------|------|
| | | | |
"""
    db_file = docs_path / "DATABASE.md"
    if not db_file.exists():
        db_file.write_text(db_content, encoding='utf-8')
        created_files.append("DATABASE.md")

    # 5. VERIFICATION.md
    verify_content = f"""# {project_name} 검증 계획

## 테스트 전략

| 유형 | 범위 | 도구 |
|------|------|------|
| 단위 테스트 | 함수/메서드 | pytest |
| 통합 테스트 | API 엔드포인트 | pytest |
| E2E 테스트 | 사용자 시나리오 | |

## 테스트 케이스

### 핵심 기능
- [ ] [정상 케이스 1]
- [ ] [정상 케이스 2]

### 엣지 케이스
- [ ] 빈 입력값
- [ ] 최대 길이 초과
- [ ] 특수문자 포함
- [ ] 동시 요청

### 에러 케이스
- [ ] 인증 실패
- [ ] 권한 없음
- [ ] 리소스 없음

## 성능 기준

| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| 응답 시간 | < 200ms | |
| 처리량 | > 100 req/s | |
"""
    verify_file = docs_path / "VERIFICATION.md"
    if not verify_file.exists():
        verify_file.write_text(verify_content, encoding='utf-8')
        created_files.append("VERIFICATION.md")

    if created_files:
        files_list = "\n".join(f"- {f}" for f in created_files)
        return [TextContent(type="text", text=f"""# ✅ docs 폴더 초기화 완료

## 생성된 파일
{files_list}

## 위치
`{docs_path}`

## 다음 단계
1. **PRD.md**부터 작성하세요 - 가장 중요!
2. 한 줄 요약 → 핵심 원칙 → 기능 목록 순으로
3. `get_prd_guide` 도구로 작성법 확인 가능

⚠️ PRD가 완성되기 전까지 코딩은 금지입니다.
""")]
    else:
        return [TextContent(type="text", text=f"""# ℹ️ docs 폴더 이미 존재

## 위치
`{docs_path}`

## 기존 파일 유지됨
이미 있는 파일은 덮어쓰지 않았습니다.

`analyze_docs` 도구로 현재 문서 상태를 확인하세요.
""")]


async def _get_prd_guide() -> list[TextContent]:
    guide = """## PRD 작성법

> 이 문서가 법. 여기 없으면 안 만듦.

### Step 1: 한 줄 요약
프로젝트가 뭔지 한 문장으로. 못 쓰면 정리 안 된 거임.
```
예: "한 번 라이브로 일주일치 콘텐츠"
```

### Step 2: 핵심 원칙 3개
절대 안 변하는 것들. 이거 기준으로 기능 판단.
```
예: 원가 보호 / 무료 체험 / 현금 유입
```

### Step 3: 입력 스펙 테이블
필드 | 타입 | 필수 | 제한 | 검증 | 예시
```
예: productName | string | O | 1~100자 | 빈문자열X | '코코넛오일'
```

### Step 4: 출력 JSON
말로 설명 X. 실제 응답 그대로.
```json
{"id": "abc123", "status": "completed", "result": {...}}
```

### Step 5: 에러 테이블
상황 | 코드 | 메시지. SNAKE_CASE 통일.
```
예: 잔액부족 | INSUFFICIENT_CREDITS | '크레딧 부족. 필요: {n}'
```

### Step 6: 상태 머신
복잡한 플로우는 ASCII로.
```
[available] --reserve--> [reserved] --capture--> [done]
```

---

💡 팁: `get_prd_template` 도구로 빈 템플릿을 생성하세요.
💡 팁: `write_prd_section` 도구로 섹션별 가이드를 받으세요.
"""
    return [TextContent(type="text", text=guide)]


async def _get_verify_checklist() -> list[TextContent]:
    checklist = """## PRD 검증 체크리스트

> 빠뜨리면 나중에 다시 짬

### 스펙
- [ ] 입력 제한값 다 있음? (1~100자, 최대 10개 같은 거)
- [ ] enum 옵션표 있음? (tone: friendly|expert|urgent)
- [ ] 출력 JSON 필드 다 나옴? (metadata, createdAt 빠뜨리기 쉬움)

### 에러
- [ ] 에러코드 SNAKE_CASE? (INSUFFICIENT_CREDITS ⭕)
- [ ] 동적 값 들어감? ('필요: {required}, 보유: {available}')

### 돈
- [ ] 무료/유료 구분표? (Free: 미리보기 / Paid: 다운로드)
- [ ] 크레딧 차감 시점? (reserve -> capture -> release)
- [ ] 실패 시 환불? (작업 실패하면 release)

### API
- [ ] /v1/ 붙어있음? (POST /v1/scripts ⭕)
- [ ] 202 맞게 씀? (비동기는 202 + jobId)

### 데이터
- [ ] 보관 기간? (무료 24시간, 유료 7일)
- [ ] 만료 알림? (24시간 전 푸시)
"""
    return [TextContent(type="text", text=checklist)]


async def _get_setup_guide(platform: str) -> list[TextContent]:
    """Clouvel 설치/설정 가이드"""

    desktop_guide = """## Claude Desktop 설정

### 1. 설정 파일 열기

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\\Claude\\claude_desktop_config.json
```

### 2. MCP 서버 추가

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

### 3. Claude Desktop 재시작

설정 후 Claude Desktop을 완전히 종료했다가 다시 시작하세요.

### 4. 확인

Claude에게 "clouvel 도구 목록 보여줘"라고 말하면 도구들이 보입니다.
"""

    code_guide = """## Claude Code (CLI) 설정

### 1. 프로젝트 루트에 .mcp.json 생성

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

### 2. Claude Code 실행

```bash
claude
```

### 3. 확인

```
> clouvel 도구 목록 보여줘
```
"""

    vscode_guide = """## VS Code 설정

### 1. 확장 설치

1. VS Code 열기
2. 확장(Extensions) 탭 열기 (Ctrl+Shift+X)
3. "Clouvel" 검색
4. "Clouvel" 확장 설치 (whitening.clouvel)

### 2. MCP 서버 설정

1. 명령 팔레트 열기 (Ctrl+Shift+P)
2. "Clouvel: MCP 서버 설정" 선택
3. Claude Desktop 또는 Claude Code 선택

### 3. 사이드바에서 문서 상태 확인

왼쪽 사이드바에 Clouvel 아이콘이 생깁니다.
문서 상태를 실시간으로 확인할 수 있습니다.
"""

    cursor_guide = """## Cursor 설정

### 1. 확장 설치

1. Cursor 열기
2. 확장(Extensions) 탭 열기 (Ctrl+Shift+X)
3. "Clouvel" 검색
4. "Clouvel for Cursor" 확장 설치 (whitening.clouvel-cursor)

### 2. MCP 서버 설정

1. 명령 팔레트 열기 (Ctrl+Shift+P)
2. "Clouvel: MCP 서버 설정" 선택
3. Claude Desktop 또는 Claude Code 선택

### 3. 사이드바에서 문서 상태 확인

왼쪽 사이드바에 Clouvel 아이콘이 생깁니다.
"""

    guides = {
        "desktop": desktop_guide,
        "code": code_guide,
        "vscode": vscode_guide,
        "cursor": cursor_guide,
    }

    if platform == "all":
        result = "# Clouvel 설치/설정 가이드\n\n"
        result += desktop_guide + "\n---\n\n"
        result += code_guide + "\n---\n\n"
        result += vscode_guide + "\n---\n\n"
        result += cursor_guide
    else:
        result = guides.get(platform, "알 수 없는 플랫폼입니다.")

    return [TextContent(type="text", text=result)]


async def _get_analytics(path: str | None, days: int) -> list[TextContent]:
    """사용량 통계 조회"""
    try:
        stats = get_stats(project_path=path, days=days)
        result = format_stats(stats)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"통계 조회 실패: {e}")]


async def _init_clouvel(platform: str) -> list[TextContent]:
    """Clouvel 온보딩 - 플랫폼별 맞춤 안내"""

    if platform == "ask":
        return [TextContent(type="text", text="""# 🚀 Clouvel 시작하기

어떤 환경에서 사용하시나요?

## 1️⃣ Claude Desktop
- 대화형으로 PRD 작성 도움
- MCP 도구로 문서 체크
- **추천: 바이브코딩 입문자**

## 2️⃣ VS Code / Cursor
- 사이드바에서 문서 상태 확인
- 에디터 내 가이드
- **추천: 에디터 중심 작업**

## 3️⃣ Claude Code (CLI)
- 터미널에서 코딩
- Hooks로 자동 체크
- **추천: 파워 유저**

---

**사용자에게 물어보세요:**
"어떤 환경에서 사용하시나요? (desktop / vscode / cli)"

선택 후 `init_clouvel` 도구를 다시 호출하세요.
예: init_clouvel(platform="cli")
""")]

    elif platform == "desktop":
        return [TextContent(type="text", text="""# ✅ Claude Desktop 설정 완료!

MCP 서버가 이미 연결되어 있습니다.

## 사용법

### 코딩 전 체크
```
"이 프로젝트 코딩해도 돼?" → can_code 도구 자동 호출
```

### PRD 작성 도움
```
"PRD 작성 도와줘" → get_prd_guide + get_prd_template
```

### 문서 분석
```
"docs 폴더 분석해줘" → analyze_docs
```

---

## 다음 단계

1. 프로젝트 docs 폴더 경로를 알려주세요
2. `can_code` 도구로 문서 상태 확인
3. 부족한 문서가 있으면 작성 도움 받기

**시작할까요?** 프로젝트 경로를 알려주세요!
""")]

    elif platform == "vscode":
        return [TextContent(type="text", text="""# 🔧 VS Code / Cursor 설정

## 1단계: 확장 설치

1. VS Code 열기
2. 확장(Extensions) 탭 (Ctrl+Shift+X)
3. "Clouvel" 검색 → 설치

## 2단계: MCP 서버 연결

터미널에서:
```bash
clouvel init
```

또는 명령 팔레트(Ctrl+Shift+P):
```
Clouvel: MCP 서버 설정
```

## 3단계: 사이드바 확인

왼쪽에 Clouvel 아이콘이 생깁니다.
문서 상태를 실시간으로 확인할 수 있습니다.

---

## CLI도 함께 쓴다면?

`setup_cli` 도구로 Hooks 설정을 추가하세요:
```
setup_cli(path="프로젝트경로", level="remind")
```
""")]

    elif platform == "cli":
        return [TextContent(type="text", text="""# 🖥️ Claude Code (CLI) 설정

CLI에서는 **강제**가 핵심입니다.
자동 설정을 위해 `setup_cli` 도구를 사용하세요.

## 강제 수준 선택

| 수준 | 설명 | 추천 |
|------|------|------|
| `remind` | 경고만 출력 | 처음 써보는 분 |
| `strict` | 커밋 차단 | 일반 사용 |
| `full` | Hooks + 커밋 차단 | 확실한 강제 |

## 설정 방법

**사용자에게 물어보세요:**
1. 프로젝트 경로가 어디인가요?
2. 강제 수준은? (remind / strict / full)

그 후 `setup_cli` 도구를 호출하세요:
```
setup_cli(path="프로젝트경로", level="strict")
```

---

## 수동 설정 (참고용)

### .claude/hooks.json
```json
{
  "hooks": {
    "preToolUse": [{
      "matcher": "Edit|Write",
      "hooks": ["clouvel-check"]
    }]
  }
}
```

### CLAUDE.md 규칙
```markdown
## Clouvel 규칙
코드 작성(Edit/Write) 전 반드시 can_code 도구 실행.
```
""")]

    return [TextContent(type="text", text="알 수 없는 플랫폼입니다.")]


async def _setup_cli(path: str, level: str) -> list[TextContent]:
    """CLI 환경 설정 - hooks, CLAUDE.md, pre-commit"""
    import json

    project_path = Path(path)

    if not project_path.exists():
        return [TextContent(type="text", text=f"❌ 경로가 존재하지 않습니다: {path}")]

    created_files = []

    # 1. .claude 폴더 생성
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # 2. hooks.json 생성 (remind, full 레벨)
    if level in ["remind", "full"]:
        hooks_content = {
            "hooks": {
                "preToolUse": [
                    {
                        "matcher": "Edit|Write|NotebookEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo '⚠️ [Clouvel] 코드 작성 전 can_code 도구로 문서 상태를 확인하세요!'"
                            }
                        ]
                    }
                ]
            }
        }
        hooks_file = claude_dir / "hooks.json"
        hooks_file.write_text(json.dumps(hooks_content, indent=2, ensure_ascii=False), encoding='utf-8')
        created_files.append(".claude/hooks.json")

    # 3. CLAUDE.md 규칙 추가/생성
    claude_md = project_path / "CLAUDE.md"
    clouvel_rule = """
## Clouvel 규칙 (자동 생성)

> 이 규칙은 Clouvel이 자동으로 추가했습니다.

### 필수 준수 사항
1. **코드 작성 전 문서 체크**: Edit/Write 도구 사용 전 반드시 `can_code` 도구를 먼저 호출
2. **can_code 실패 시 코딩 금지**: 필수 문서가 없으면 PRD 작성부터
3. **PRD가 법**: docs/PRD.md에 없는 기능은 구현하지 않음

### 워크플로우
```
사용자 요청 → can_code 호출 →
  ├─ ✅ 통과 → 코딩 시작
  └─ ❌ 실패 → PRD 작성 도움
```
"""

    if claude_md.exists():
        existing = claude_md.read_text(encoding='utf-8')
        if "Clouvel 규칙" not in existing:
            claude_md.write_text(existing + "\n" + clouvel_rule, encoding='utf-8')
            created_files.append("CLAUDE.md (규칙 추가)")
    else:
        claude_md.write_text(f"# {project_path.name}\n" + clouvel_rule, encoding='utf-8')
        created_files.append("CLAUDE.md (생성)")

    # 4. pre-commit hook (strict, full 레벨)
    if level in ["strict", "full"]:
        git_hooks_dir = project_path / ".git" / "hooks"
        if git_hooks_dir.exists():
            pre_commit = git_hooks_dir / "pre-commit"
            pre_commit_content = '''#!/bin/sh
# Clouvel pre-commit hook
# 문서 없이 커밋 방지

DOCS_DIR="./docs"

# PRD 파일 확인
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "❌ [Clouvel] 커밋 차단: PRD 문서가 없습니다."
    echo ""
    echo "먼저 docs/PRD.md를 작성하세요."
    echo "도움: clouvel get_prd_template"
    exit 1
fi

echo "✅ [Clouvel] 문서 체크 통과"
'''
            pre_commit.write_text(pre_commit_content, encoding='utf-8')
            # 실행 권한 (Unix 계열)
            try:
                import os
                os.chmod(pre_commit, 0o755)
            except Exception:
                pass
            created_files.append(".git/hooks/pre-commit")
        else:
            created_files.append("⚠️ .git/hooks 없음 (git init 필요)")

    # 결과 출력
    files_list = "\n".join(f"  - {f}" for f in created_files)

    level_desc = {
        "remind": "리마인드 (경고만)",
        "strict": "엄격 (커밋 차단)",
        "full": "풀옵션 (Hooks + 커밋 차단)"
    }

    return [TextContent(type="text", text=f"""# ✅ CLI 설정 완료!

## 설정 수준
**{level_desc.get(level, level)}**

## 생성/수정된 파일
{files_list}

## 작동 방식

### Hooks (remind, full)
```
Edit/Write 호출 시 → 경고 메시지 출력
```

### CLAUDE.md 규칙
```
Claude가 규칙을 읽고 can_code 먼저 호출
```

### pre-commit (strict, full)
```
PRD 없이 커밋 시도 → 커밋 차단
```

---

## 테스트 해보기

1. `can_code` 도구로 현재 문서 상태 확인:
   ```
   can_code(path="{path}/docs")
   ```

2. PRD 없으면 생성:
   ```
   init_docs(path="{path}", project_name="프로젝트명")
   ```

**이제 PRD 없이는 코딩할 수 없습니다!** 🔒
""")]


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _cli_init(args):
    """CLI init 명령어 - 인터랙티브 설정"""
    import json

    # -p와 -l이 명시적으로 주어졌으면 바로 설정 (non-interactive)
    if args.path and args.path != "." or args.level != "strict":
        print("[Clouvel] Quick setup mode.\n")
        _sync_setup_cli(args.path or ".", args.level)
        return

    print("[Clouvel] Setup started.\n")

    # 플랫폼 선택
    print("Where will you use Clouvel?")
    print("  1) Claude Desktop")
    print("  2) VS Code / Cursor")
    print("  3) Claude Code (CLI)")
    print("  4) All of the above")
    print()

    try:
        choice = input("Select (1-4): ").strip()
    except EOFError:
        # Non-interactive 환경에서는 CLI로 기본 설정
        print("\n[Auto] Non-interactive mode, using CLI defaults.")
        _sync_setup_cli(args.path or ".", args.level)
        return

    platform_map = {"1": "desktop", "2": "vscode", "3": "cli", "4": "all"}
    platform = platform_map.get(choice, "cli")

    if platform in ["cli", "all"]:
        print("\n[Path] Enter project path")
        path = input(f"Path (default: {args.path or '.'}): ").strip() or args.path or "."

        print("\nSelect enforcement level:")
        print("  1) remind - Warning only")
        print("  2) strict - Block commits (Recommended)")
        print("  3) full   - Hooks + Block commits")
        print()

        level_choice = input("Select (1-3, default: 2): ").strip() or "2"
        level_map = {"1": "remind", "2": "strict", "3": "full"}
        level = level_map.get(level_choice, "strict")

        # 동기 버전으로 설정 실행
        _sync_setup_cli(path, level)

    elif platform == "desktop":
        print("\n[OK] Claude Desktop MCP server is already connected.")
        print("Try saying 'show clouvel tools' in your conversation.")

    elif platform == "vscode":
        print("\n[Setup] VS Code:")
        print("1. Search 'Clouvel' in Extensions and install")
        print("2. Command Palette (Ctrl+Shift+P) -> 'Clouvel: Setup MCP Server'")
        print("\nAlso setup CLI? (y/n)")
        if input().strip().lower() == 'y':
            path = input("Project path (default: .): ").strip() or "."
            _sync_setup_cli(path, "strict")


def _sync_setup_cli(path: str, level: str):
    """동기 버전 CLI 설정"""
    import json

    project_path = Path(path).resolve()

    if not project_path.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return

    print(f"\n[Setting up...] {project_path}")

    created_files = []

    # 1. .claude 폴더 생성
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # 2. hooks.json
    if level in ["remind", "full"]:
        hooks_content = {
            "hooks": {
                "preToolUse": [
                    {
                        "matcher": "Edit|Write|NotebookEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo '⚠️ [Clouvel] 코드 작성 전 can_code 도구로 문서 상태를 확인하세요!'"
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
            print("  - CLAUDE.md: 이미 Clouvel 규칙 있음")
    else:
        claude_md.write_text(f"# {project_path.name}\n" + clouvel_rule, encoding='utf-8')
        created_files.append("CLAUDE.md (생성)")

    # 4. pre-commit hook
    if level in ["strict", "full"]:
        git_hooks_dir = project_path / ".git" / "hooks"
        if git_hooks_dir.exists():
            pre_commit = git_hooks_dir / "pre-commit"
            pre_commit_content = '''#!/bin/sh
# Clouvel pre-commit hook
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    echo "Please create docs/PRD.md first."
    exit 1
fi
echo "[Clouvel] Document check passed."
'''
            pre_commit.write_text(pre_commit_content, encoding='utf-8')
            try:
                import os
                os.chmod(pre_commit, 0o755)
            except Exception:
                pass
            created_files.append(".git/hooks/pre-commit")
        else:
            print("  [WARN] .git/hooks not found (run git init first)")

    # 결과 출력
    print("\n[OK] Setup complete!\n")
    print("Created/modified files:")
    for f in created_files:
        print(f"  - {f}")

    print("\nNext steps:")
    print("1. Create docs/PRD.md")
    print("2. Ask Claude 'Can I code this project?'")
    print("\n[LOCKED] No coding without PRD!")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Clouvel - 바이브코딩 프로세스 강제 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  clouvel              MCP 서버 실행 (Claude가 사용)
  clouvel init         인터랙티브 설정
  clouvel init -p .    현재 폴더에 설정
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # init 서브커맨드
    init_parser = subparsers.add_parser("init", help="프로젝트 초기화")
    init_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")
    init_parser.add_argument("-l", "--level", choices=["remind", "strict", "full"], default="strict", help="강제 수준")

    args = parser.parse_args()

    if args.command == "init":
        _cli_init(args)
    else:
        # 기본: MCP 서버 실행
        import asyncio
        asyncio.run(run_server())


if __name__ == "__main__":
    main()
