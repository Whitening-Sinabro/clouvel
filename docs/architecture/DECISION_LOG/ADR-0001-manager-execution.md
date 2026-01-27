# ADR-0001: Manager Execution Architecture

> 작성일: 2026-01-26
> 최종 업데이트: 2026-01-26 (v1.8.0 구현 완료)
> 상태: **RESOLVED - 옵션 1 (Worker API) 선택 및 구현됨**

---

## (A) 결론

### 최종 결정

**옵션 1: Worker API 사용** - v1.8.0에서 구현 완료

### 구현 상태

| 항목 | 상태 | Evidence |
|------|------|----------|
| `server.py:_wrap_manager()` | `call_manager_api()` 호출 | `server.py:1193-1225` |
| `server.py:_wrap_quick_perspectives()` | Worker API 사용 | `server.py:1275-1305` |
| 로컬 manager import | 제거됨 | `server.py:44` 라인 삭제 |
| PyPI 설치 테스트 | 통과 | uvx 환경에서 검증 |

### 변경 이력 요약

| 버전 | 상태 |
|------|------|
| v1.7.x | 로컬 실행 시도 → ImportError |
| v1.8.0 | Worker API 전환 완료 |

---

## (B) 결론 근거

### 로컬 실행 경로 (현재 구현)

| # | 파일:라인 | 코드/설명 |
|---|-----------|----------|
| 1 | `server.py:44` | `manager, ... generate_meeting_sync,` import from `.tools` |
| 2 | `server.py:826` | `"manager": lambda args: _wrap_manager(args)` |
| 3 | `server.py:1209` | `meeting_output = generate_meeting_sync(...)` |
| 4 | `server.py:1224` | `result = manager(...)` |
| 5 | `tools/__init__.py:89` | `from .manager import (manager, ...)` |
| 6 | `tools/__init__.py:105` | fallback: `return {"error": f"Manager module not available: {_err}"}` |
| 7 | `pyproject.toml:79` | `"src/clouvel/tools/manager/",` (빌드 제외) |

### Worker 실행 경로 (미사용)

| # | 파일:라인 | 코드/설명 |
|---|-----------|----------|
| 1 | `api_client.py:48` | `def call_manager_api(...)` 정의 |
| 2 | `api_client.py:82-89` | `requests.post(f"{API_BASE_URL}/api/manager", ...)` |
| 3 | (없음) | **`call_manager_api()`를 호출하는 코드가 없음** |

### 검증 명령어

```bash
# call_manager_api 사용처 검색
grep -rn "call_manager_api" src/clouvel/
# 결과: api_client.py:48 (정의만 있음, 호출 없음)
```

---

## (C) 수정안

### 옵션 1: server.py가 call_manager_api()만 쓰게 변경

**개요**: 로컬 모듈 의존성 제거, Worker API만 사용

#### 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `server.py` | `_wrap_manager()`에서 `call_manager_api()` 호출 |
| `server.py` | `from .api_client import call_manager_api` 추가 |
| `tools/__init__.py` | manager 관련 import/fallback 제거 가능 (선택) |

#### 장점

- PyPI 빌드에서 `tools/manager/` 제외해도 문제 없음
- 로컬에 anthropic 패키지 불필요
- Trial/License 체크가 서버에서 일관되게 처리됨
- 코드 단순화

#### 단점

- 네트워크 필수 (오프라인 불가)
- API 응답 지연 (로컬보다 느림)
- Worker 비용 증가 (Claude API 호출이 서버에서 발생)
- use_dynamic 모드 제거 필요 (서버에서 처리해야 함)

#### 리스크

- Worker API가 manager 로직을 완전히 구현했는지 확인 필요
- 기존 use_dynamic 사용자에게 breaking change

#### 코드 변경 예시

```python
# server.py

from .api_client import call_manager_api

async def _wrap_manager(args: dict) -> list[TextContent]:
    """manager tool wrapper - Worker API 호출"""
    result = call_manager_api(
        context=args.get("context", ""),
        topic=args.get("topic"),
        mode=args.get("mode", "auto"),
        managers=args.get("managers"),
    )

    output = result.get("formatted_output", str(result))
    return [TextContent(type="text", text=output)]
```

---

### 옵션 2: tools/manager를 PyPI 빌드에 포함

**개요**: 로컬 실행 유지, 빌드 제외 항목에서 제거

#### 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| `pyproject.toml` | `exclude`에서 `"src/clouvel/tools/manager/"` 제거 |
| (없음) | 다른 코드 변경 불필요 |

#### 장점

- 최소 변경 (1줄)
- 오프라인 동작 가능
- use_dynamic 모드 유지
- 빠른 응답 (로컬 실행)

#### 단점

- Pro 기능 코드가 공개됨 (오픈소스화)
- 로컬에 anthropic 패키지 필요 (동적 모드)
- Trial/License 체크 로직이 클라이언트에 있어야 함
- 패키지 크기 증가

#### 리스크

- Pro 기능의 비즈니스 모델 영향 (무료로 사용 가능해짐)
- 라이선스 우회 가능성

#### 코드 변경 예시

```toml
# pyproject.toml

[tool.hatch.build]
exclude = [
    "src/clouvel/license.py",
    "src/clouvel/tools/ship_pro.py",
    # "src/clouvel/tools/manager/",  # 이 줄 제거 또는 주석
]
```

---

## 비교표

| 항목 | 옵션 1 (Worker API) | 옵션 2 (로컬 포함) |
|------|--------------------|--------------------|
| 변경 규모 | 중간 (server.py 수정) | 최소 (pyproject.toml 1줄) |
| 오프라인 | X | O |
| 응답 속도 | 느림 (네트워크) | 빠름 (로컬) |
| Pro 코드 보호 | O (서버에 있음) | X (공개됨) |
| anthropic 의존성 | X (서버에서 처리) | O (로컬 필요) |
| Breaking Change | O (use_dynamic) | X |
| 라이선스 우회 | 어려움 | 쉬움 |

---

## 최종 결정

**옵션 1 (Worker API 사용)** 선택 및 구현 완료

### 결정 근거

1. `api_client.py:call_manager_api()`가 이미 존재 - 의도된 아키텍처
2. Pro 기능 보호 - 비즈니스 모델 유지
3. Trial 체크가 서버에서 일관되게 처리됨
4. 로컬 의존성 감소 (anthropic 패키지 불필요)

### 단점 수용

- 네트워크 필수 → fallback 응답 구현 (`api_client.py:195-242`)
- API 지연 → 30초 timeout 설정 (`api_client.py:17`)

---

## 완료된 액션

1. [x] Worker API 동작 확인 (2026-01-26)
2. [x] 옵션 1 구현 (v1.8.0)
3. [x] PyPI 설치 환경 테스트 통과
4. [x] Knowledge Base에 결정 기록 (decision #30-40)

### 구현 변경사항

```python
# server.py (v1.8.0)

# Line 19: 새 import 추가
from .api_client import call_manager_api

# Line 1193-1225: _wrap_manager() 변경
async def _wrap_manager(args: dict) -> list[TextContent]:
    result = call_manager_api(
        context=args.get("context", ""),
        topic=args.get("topic"),
        mode=args.get("mode", "auto"),
        managers=args.get("managers"),
    )
    # ... formatting
```

### 롤백 계획

옵션 2로 롤백이 필요한 경우:
1. `pyproject.toml` exclude에서 `tools/manager/` 제거
2. `server.py`에서 로컬 import 복원
3. `_wrap_manager()`가 로컬 함수 호출하도록 변경

---

## 참조

- flow_manager.md: [Manager 호출 플로우](../CALL_FLOWS/flow_manager.md)
- Knowledge Base: `search_knowledge("architecture manager")` → decision #30, #32
