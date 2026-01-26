# Manager 기능 코드 플로우

> 작성일: 2026-01-26
> 버전: v1.7.3 기준

---

## (A) 엔트리포인트 목록

| 엔트리포인트 | 파일:라인 | 설명 |
|-------------|-----------|------|
| MCP Tool `manager` | `server.py:571` | Tool 정의 |
| MCP Handler | `server.py:826` | `"manager": lambda args: _wrap_manager(args)` |
| Wrapper 함수 | `server.py:1192` | `async def _wrap_manager(args)` |

---

## (B) 호출 그래프

```
[Claude Code MCP 호출]
        │
        ▼
server.py:826 ─── HANDLER_MAP["manager"]
        │
        ▼
server.py:1192 ─── _wrap_manager(args)
        │
        ├─── use_dynamic=True ───▶ generate_meeting_sync() [server.py:1209]
        │                                   │
        │                                   ▼
        │                          tools/__init__.py:95에서 import
        │                                   │
        │                          ┌────────┴────────┐
        │                          │                 │
        │                    [성공 시]           [ImportError]
        │                          │                 │
        │              tools/manager/          fallback 함수
        │              generator/              "Manager module
        │              conversation.py         not available"
        │
        └─── fallback ───▶ manager() [server.py:1224]
                                │
                                ▼
                       tools/__init__.py:89에서 import
                                │
                       ┌────────┴────────┐
                       │                 │
                  [성공 시]          [ImportError]
                       │                 │
               tools/manager/       fallback 함수
               core.py:manager()    {"error": "..."}
```

### 사용되지 않는 코드 경로

```
api_client.py:48 ─── call_manager_api()
        │
        ▼
    [DEAD CODE - 어디서도 호출 안 됨]
        │
        ▼
    POST https://clouvel-api.vnddns999.workers.dev/api/manager
```

---

## (C) 시퀀스 다이어그램

### 현재 구현 (로컬 실행)

```
사용자          Claude Code       server.py        tools/__init__    tools/manager/
  │                 │                │                  │                 │
  │──"manager"────▶│                │                  │                 │
  │                 │──MCP call────▶│                  │                 │
  │                 │                │                  │                 │
  │                 │                │──import─────────▶│                 │
  │                 │                │                  │──import────────▶│
  │                 │                │                  │                 │
  │                 │                │                  │◀─[ImportError]──│ (PyPI 빌드 제외)
  │                 │                │                  │                 │
  │                 │                │◀─fallback 함수───│                 │
  │                 │                │                  │                 │
  │                 │◀─{"error":...}│                  │                 │
  │◀─에러 표시─────│                │                  │                 │
```

### 의도된 구현 (Worker 호출)

```
사용자          Claude Code       server.py       api_client.py      Worker API
  │                 │                │                 │                 │
  │──"manager"────▶│                │                 │                 │
  │                 │──MCP call────▶│                 │                 │
  │                 │                │                 │                 │
  │                 │                │──call_manager──▶│                 │
  │                 │                │    _api()       │──POST /api/────▶│
  │                 │                │                 │    manager      │
  │                 │                │                 │                 │──AI 처리
  │                 │                │                 │◀─JSON response──│
  │                 │◀─결과─────────│◀────────────────│                 │
  │◀─피드백 표시───│                │                 │                 │
```

---

## (D) 현재 구현 vs 의도 아키텍처 비교

| 항목 | 현재 구현 | 의도된 아키텍처 |
|------|----------|----------------|
| 실행 위치 | 로컬 (tools/manager/) | Worker API (workers.dev) |
| 호출 방식 | 직접 import | HTTP POST via api_client.py |
| 라이선스 체크 | import 시점에 실패 | API에서 체크 |
| PyPI 패키지 | tools/manager/ 제외 | 제외해도 무관 (API 호출) |
| 의존성 | anthropic, 로컬 모듈 | requests만 필요 |

### 핵심 모순 (1줄 요약)

**`api_client.py:call_manager_api()`가 존재하지만, `server.py:_wrap_manager()`는 이를 호출하지 않고 로컬 `tools/manager/` 모듈을 직접 import하여 실행하려 함. 그런데 `pyproject.toml:79`에서 해당 모듈이 빌드에서 제외되어 PyPI 설치 시 ImportError 발생.**

---

## (E) 실패 재현 조건

### 환경

```
설치 방식: pip install clouvel (또는 uvx clouvel)
Python: 3.10+
clouvel 버전: 1.7.3 이하 (PyPI)
```

### 재현 단계

1. `pip install clouvel` (PyPI에서 설치)
2. Claude Code에서 manager MCP 도구 호출
3. `use_dynamic=False` (기본값)

### 에러 발생 경로

```
server.py:1224 ─── manager() 호출
        │
        ▼
tools/__init__.py:105 ─── fallback 함수 실행
        │
        ▼
반환값: {"error": "Manager module not available: No module named 'clouvel.tools.manager'"}
```

### 에러 메시지

```json
{"error": "Manager module not available: No module named 'clouvel.tools.manager'"}
```

### 근거 코드 라인

| 파일 | 라인 | 내용 |
|------|------|------|
| `pyproject.toml` | 79 | `"src/clouvel/tools/manager/",` (빌드 제외) |
| `tools/__init__.py` | 88-98 | `try: from .manager import ...` |
| `tools/__init__.py` | 105 | `return {"error": f"Manager module not available: {_err}"}` |
| `server.py` | 1224 | `result = manager(...)` |

---

## 파일 구조 참조

### tools/manager/ 디렉토리 (PyPI 빌드에서 제외됨)

```
tools/manager/
├── __init__.py          # manager, quick_perspectives 등 export
├── core.py              # manager() 함수 정의
├── formatter.py         # 출력 포맷팅
├── utils.py             # 유틸리티
├── data/                # 매니저 데이터 (PM, CTO, QA 등)
│   ├── __init__.py
│   ├── pm.py
│   ├── cto.py
│   └── ...
├── prompts/             # 프롬프트 템플릿
│   ├── __init__.py
│   ├── personas.py
│   └── templates.py
└── generator/           # 동적 회의 생성
    ├── __init__.py
    ├── collector.py
    └── conversation.py  # generate_meeting_sync()
```

### 관련 파일 (PyPI 빌드에 포함됨)

```
api_client.py            # call_manager_api() 정의 (사용 안 됨)
server.py                # _wrap_manager() 정의
tools/__init__.py        # manager import 시도 + fallback
```
