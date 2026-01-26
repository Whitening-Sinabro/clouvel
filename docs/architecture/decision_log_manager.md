# Manager 아키텍처 결정 로그

> 작성일: 2026-01-26
> 버전: v1.7.3 기준
> 상태: **미해결 - 결정 필요**

---

## (A) 결론

### 현재 상태

**"로컬 실행" 구현이지만, 로컬 모듈이 배포에서 제외되어 PyPI 설치 시 작동 불가**

### 의도

**"Worker 실행"** - `api_client.py:call_manager_api()` 함수가 존재함

### 실제

**"로컬 실행 시도 → 실패"** - `server.py:_wrap_manager()`가 `call_manager_api()`를 사용하지 않음

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

## 권장안

**옵션 1 (Worker API 사용)** 권장

이유:
1. `api_client.py:call_manager_api()`가 이미 존재 - 의도된 아키텍처로 보임
2. Pro 기능 보호 - 비즈니스 모델 유지
3. Trial 체크가 서버에서 일관되게 처리됨
4. 로컬 의존성 감소

단, Worker API가 manager 로직을 완전히 구현했는지 먼저 확인 필요.

---

## 다음 액션

1. [ ] Worker API (`clouvel-api.vnddns999.workers.dev/api/manager`) 동작 확인
2. [ ] 옵션 선택 후 구현
3. [ ] 테스트 (PyPI 설치 환경에서)
4. [ ] Knowledge Base에 결정 기록 (`record_decision`)
