# Findings

> 조사 결과 기록
> 생성일: 2026-01-24 14:15

---

## 2026-01-26: Manager 도구 충돌 분석

### 문제

manager 도구 호출 시 작업 차단. 다른 작업 진행 불가.

### 근본 원인

**2개의 manager 함수가 다른 일을 함:**

| 위치 | 동작 |
|------|------|
| `tools/__init__.py:89-114` | `call_manager_api()` → API가 응답 생성 |
| `tools/manager/core.py:220` | 로컬 Pro/Trial 체크 + 응답 생성 |

`server.py:44`가 `from .tools.manager import manager`로 되어있어 어디서 가져오는지 불명확.

### 분석 과정

1. `server.py` import 확인 → `tools.manager`에서 import
2. `tools/__init__.py` 확인 → 자체 manager 함수 정의 (API 기반)
3. `tools/manager/__init__.py` 확인 → `core.py`에서 manager import
4. `tools/manager/core.py` 확인 → 로컬 기반 manager 정의

### 해결 방향

**ship 패턴으로 통일:**
- `tools/manager.py` (신규) → API 권한 체크
- `tools/manager_impl/` (기존 manager/ 이름변경) → 실제 로직

### 기록된 결정 (Knowledge Base)

- #30: Import 규칙 (LOCKED)
- #31: Pro 기능 패턴 (LOCKED)
- #32: Manager 충돌 (미해결)
- #33: 라이센스 모듈 구조 (LOCKED)
- #34: Trial 관리 (LOCKED)
- #35: Optional 의존성 (LOCKED)
- #36: 개발자 감지 (LOCKED)
- #37: 파일 구조 규칙 (LOCKED)

### 기록된 위치 (Knowledge Base)

- #5: server.py (MCP 서버 메인)
- #6: tools/__init__.py (단일 Export)
- #7: tools/__init__.py:89-114 (Manager 충돌 지점 1)
- #8: tools/manager/core.py:220 (Manager 충돌 지점 2)
- #9: tools/ship.py (표준 패턴)
- #10: api_client.py
- #11: license_common.py
- #12: db/knowledge.py
- #13: trial.py
- #14: manager/generator/conversation.py

---

## 2-Action Rule

> view/browser 작업 2개 후 반드시 여기에 기록!

---
