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

## 2026-01-27: 실전 꿀팁 시스템 아이디어

### 개요

사용자가 PRD 작성하거나 특정 기능 구현할 때 **선배 개발자의 실전 팁**을 자동으로 제공.

### 예시 팁

**Google Play 14일 테스트 우회 전략**:
- 개인 개발자는 14일간 20명 테스터로 클로즈드 테스트 필수 (법인 면제)
- 앱이 "켜지기만 하는" 최소 버전으로 먼저 테스트 시작
- 14일 동안 실제 개발하면서 계속 업데이트
- 완성되면 프로덕션 배포
- **핵심**: 구글은 "14일간 테스트 했냐"만 봄, 내용은 안 봄

### 구현 방향

| 옵션 | 설명 |
|------|------|
| A | Knowledge Base에 `tips` 카테고리 추가 |
| B | Manager 응답에 관련 팁 포함 |
| C | 별도 `tips` 도구 생성 |
| D | PRD 템플릿에 팁 섹션 추가 |

### 트리거 예시

| 컨텍스트 | 제공 팁 |
|----------|---------|
| 앱 PRD 작성 | Google Play 테스트 팁, App Store 심사 팁 |
| 결제 기능 | Stripe/PG 실전 팁, 환불 정책 |
| 배포 준비 | 플랫폼별 주의사항 |
| 인증 기능 | OAuth 실전 경험, 보안 체크리스트 |

### 출처

디스코드 커뮤니티 (팬더/라인프/앱/7년차)

---

## 2-Action Rule

> view/browser 작업 2개 후 반드시 여기에 기록!

---
