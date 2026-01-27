# Clouvel PRD

> PRD 없으면 코딩 없다.

## 한 줄 정의

바이브코딩 프로세스를 강제하는 MCP 서버

## 핵심 기능

### Free (v1.3)

| 도구              | 설명                                               |
| ----------------- | -------------------------------------------------- |
| `can_code`        | 문서 검사 후 코딩 허용/차단                        |
| `start`           | 프로젝트 온보딩                                    |
| `plan`            | **[NEW]** 상세 실행 계획 생성 (매니저 피드백 기반) |
| `init_planning`   | 영속적 컨텍스트 초기화                             |
| `update_progress` | 진행 상황 업데이트                                 |
| `refresh_goals`   | 목표 리마인드                                      |

### Pro

| 도구         | 설명                              |
| ------------ | --------------------------------- |
| `manager`    | 8명 C-Level 매니저 협업 피드백    |
| `ship`       | 원클릭 검증 (lint → test → build) |
| `quick_ship` | 빠른 검증 (lint + test)           |
| `full_ship`  | 전체 검증 + 자동 수정             |

## 타겟

Claude Code 사용자 중 바이브코딩 초보자

## Acceptance (완료 기준)

### Core

- [x] `can_code` 호출 시 PRD 없으면 BLOCK
- [x] `can_code` 호출 시 acceptance 섹션 없으면 BLOCK
- [x] `can_code` 호출 시 권장 문서 없으면 WARN (진행 가능)
- [x] `clouvel setup` 실행 시 글로벌 CLAUDE.md에 규칙 추가
- [x] `clouvel setup` 실행 시 MCP 서버 자동 등록
- [x] Claude가 코드 작성 전 자동으로 `can_code` 호출

### v1.3 Plan Tool

- [x] `plan` 호출 시 manager 피드백 자동 수집
- [x] 액션 아이템을 Phase별(준비/설계/구현/검증)로 그룹화
- [x] 의존성 기반 토폴로지 정렬
- [x] task_plan.md에 상세 계획 저장
- [x] 검증 포인트 및 완료 조건 포함

---

## v1.5 기록 강화 + Manager 개선

> **모토**: "기록을 잃지 않는다" - 약속 이행
> **원칙**: "강제되지 않는 룰은 장식이다"

### 배경 (왜 필요한가)

실제 사용 시 발생한 문제:
- `files/created.md` 안 만듦 → 파일 추적 불가
- 테스트 0개인데 "✅ 완료" 처리 → 거짓 완료
- Mock인데 "✅ 완료" 처리 → DoD 무시
- Manager가 generic 피드백만 줌 → context 무시

**근본 원인**: 규칙만 있고 강제 포인트가 없음

### A. 기록 기능 강화 (Free)

| # | 기능 | 설명 | 우선순위 |
|---|------|------|----------|
| A1 | `can_code` 테스트 체크 | `src/**/*.test.*` 존재 여부 확인, 없으면 WARN | P0 |
| A2 | `can_code` DoD 체크 | PRD에 DoD/Acceptance 섹션 있는지 확인 | P0 |
| A3 | pre-commit hook 강화 | `files/created.md` 존재 확인, 없으면 커밋 차단 | P0 |
| A4 | `record_file` 도구 | 파일 생성 시 자동 기록 (Pro) | P1 |

#### A1. can_code 테스트 체크

```python
def can_code():
    check_prd()           # 기존
    check_tests_exist()   # 신규: src/**/*.test.* 존재?
    # 없으면 WARN: "테스트 파일이 없습니다. 작성 후 진행하세요."
```

**완료 기준:**
- [x] `src/` 또는 `tests/` 폴더에 `*.test.*` 또는 `*.spec.*` 파일 존재 확인
- [x] 없으면 WARN (BLOCK 아님 - 초기 개발 허용)
- [x] 테스트 개수 표시 (예: "3 tests found")

#### A2. can_code DoD 체크

```python
def can_code():
    check_prd()
    check_dod_section()   # 신규: PRD에 DoD 섹션 있는지?
    # 없으면 WARN: "DoD(완료 기준)가 없습니다."
```

**완료 기준:**
- [x] PRD에서 `## Acceptance`, `## DoD`, `## 완료 기준` 섹션 검색
- [x] 없으면 BLOCK (critical이므로 WARN → BLOCK)
- [ ] 체크리스트 (`- [ ]`) 개수 표시 (미구현 - 향후 추가)

#### A3. pre-commit hook 강화

```bash
# .claude/hooks/pre-commit
if [ ! -f ".claude/files/created.md" ]; then
  echo "❌ .claude/files/created.md가 없습니다."
  echo "파일 생성 기록을 먼저 작성하세요."
  exit 1
fi
```

**완료 기준:**
- [x] `clouvel setup --hooks` 실행 시 pre-commit hook 설치
- [x] `files/created.md` 없으면 커밋 차단
- [x] `current.md` 없으면 커밋 차단

### B. Manager 개선 (Pro)

| # | 기능 | 설명 | 우선순위 |
|---|------|------|----------|
| B1 | 토픽 확장 | mcp, clouvel, internal 토픽 추가 | P1 |
| B2 | Context 분석 강화 | 키워드 + 문장 구조 분석 | P1 |
| B3 | 동적 피드백 개선 | 템플릿 → context 반영 피드백 | P2 |

#### B1. 토픽 확장

```python
# utils.py - topic_keywords 확장
topic_keywords = {
    # 기존...
    "mcp": ["mcp", "server", "tool", "clouvel", "claude", "anthropic"],
    "internal": ["우리", "자체", "개선", "보강", "누락", "약속"],
    "tracking": ["기록", "추적", "files", "created", "current"],
}
```

**완료 기준:**
- [x] "Clouvel 기능 개선" context → "mcp" + "internal" 토픽 감지
- [x] 해당 토픽에 맞는 매니저 피드백 생성 (CONTEXT_GROUPS에 mcp, internal, tracking, maintenance 추가)

#### B2. Context 분석 강화

```python
def _analyze_context(context: str) -> List[str]:
    # 1. 키워드 매칭 (기존)
    detected = _keyword_matching(context)

    # 2. 문장 패턴 분석 (신규)
    if "~가 없다" in context or "누락" in context:
        detected.append("missing")
    if "강제" in context or "체크" in context:
        detected.append("enforcement")

    return detected
```

**완료 기준:**
- [x] 문제 상황 패턴 감지 ("없다", "안 됨", "누락", "느려", "취약")
- [x] 요청 패턴 감지 ("추가", "구현", "수정", "테스트")
- [x] 감지된 패턴에 맞는 피드백 생성 (CONTEXT_GROUPS 매핑)

#### B3. 동적 피드백 개선

**현재 문제:**
```
context: "Clouvel 파일 추적 기능이 없어서 문제"
→ 감지: api, feature
→ 출력: "API 엔드포인트를 PRD에 명시하세요" (관련 없음)
```

**개선 후:**
```
context: "Clouvel 파일 추적 기능이 없어서 문제"
→ 감지: mcp, internal, tracking, missing
→ 출력: "파일 추적 기능 구현 시 고려사항..." (관련 있음)
```

**완료 기준:**
- [x] context 내용이 피드백에 반영됨 (패턴 감지 → 토픽 → 매니저 매핑)
- [x] generic 템플릿 대신 맞춤 피드백 (XML 구조화 + bookending)
- [x] LLM 주의력 최적화 (U-shaped curve: 처음+끝에 critical issues)
- [ ] 이전 결정(Knowledge Base) 참조

---

### 구현 순서

| Phase | 항목 | 예상 |
|-------|------|------|
| 1 | A1, A2 (can_code 강화) | 1일 |
| 2 | A3 (pre-commit hook) | 0.5일 |
| 3 | B1 (토픽 확장) | 0.5일 |
| 4 | B2, B3 (Manager 개선) | 2일 |
| 5 | A4 (record_file) | 1일 |

**총 예상**: 5일

---

### 하위 호환성

- 기존 사용자: 새 체크는 WARN만 (BLOCK 아님)
- 신규 사용자: strict 모드 옵션 제공
- `clouvel setup --strict`: 모든 체크 BLOCK으로 전환

---

## v1.7 버그 수정 + 검증 워크플로우

> **발견일**: 2026-01-25
> **근본 원인**: 테스트만 하고 검증 안 함. 사이드이펙트 체크 누락.

### 발견된 문제

| # | 문제 | 원인 | 영향도 | 우선순위 |
|---|------|------|--------|----------|
| 1 | license_status "Unknown" 표시 | license_free.py에 tier_info 미반환 | 높음 | **P0** |
| 2 | manager 동적 회의 작동 안 함 | uvx에 anthropic 없음 + 템플릿만 반환 | 높음 | **P0** |
| 3 | 검증 워크플로우 미정의 | PRD에 handoff→verify→review→gate 없음 | 높음 | **P1** |
| 4 | review 도구 없음 | 구현 안 됨 | 중간 | **P1** |
| 5 | verify/gate 실행 안 함 | 안내만 하고 실제 실행 안 함 | 중간 | **P1** |
| 6 | 사이드이펙트 체크 없음 | 동기화 파일 쌍(license.py↔license_free.py) 체크 안 함 | 높음 | **P1** |
| 7 | 테스트 ≠ 검증 | pytest 통과해도 실제 MCP 작동 확인 안 함 | 높음 | **P0** |

---

### P0: 즉시 수정 (배포 차단)

#### 1. license_free.py 동기화
- [x] tier_info, days_since_activation, premium_unlocked 반환 추가
- [ ] PyPI 배포하여 uvx 환경 반영

#### 2. manager 동적 회의 수정
- [ ] pyproject.toml에 anthropic optional 추가 (완료)
- [ ] MCP 설정 문서에 `--with anthropic` 안내
- [ ] 동적 회의 시 템플릿 대신 실제 피드백 생성 확인
- [ ] 토큰 낭비 없이 관련 있는 피드백만 생성

#### 3. 실제 MCP 검증 절차 추가
- [ ] pytest 후 반드시 MCP 도구 수동 호출 테스트
- [ ] 검증 체크리스트 문서화

---

### P1: 검증 워크플로우 정의 및 구현

#### 검증 워크플로우 (MUST)

```
기능 개발 완료
    ↓
handoff(feature, decisions, warnings, next_steps)
    ↓
/clear (컨텍스트 초기화)
    ↓
verify(path, scope, checklist)  ← 실제 체크 실행
    ↓
review(path)  ← 매니저들이 코드 리뷰 [NEW]
    ↓
gate(path, steps, fix)  ← 실제 lint/test/build 실행
    ↓
완료
```

#### 4. verify 도구 개선
- [ ] 체크리스트 항목 자동 검증 (파일 존재, 함수 구조 등)
- [ ] PASS/FAIL 결과 반환
- [ ] 실패 시 자동으로 수정 제안

#### 5. review 도구 신규 구현
```python
async def review(path: str, scope: str = "feature") -> list[TextContent]:
    """매니저들의 코드 리뷰

    1. 변경된 파일 목록 수집
    2. 각 매니저 관점에서 리뷰
    3. 문제 발견 시 수정 제안
    """
```

#### 6. gate 도구 개선
- [ ] 실제 명령어 실행 (lint, test, build)
- [ ] 결과 수집 및 EVIDENCE.md 자동 업데이트
- [ ] 전체 PASS 시에만 "완료" 허용

#### 7. 사이드이펙트 체크 도구
```python
async def check_sync(path: str) -> list[TextContent]:
    """동기화 필수 파일 쌍 검증

    체크 대상:
    - license.py ↔ license_free.py
    - server.py ↔ server_pro.py (있으면)
    - messages/en.py ↔ messages/ko.py (있으면)

    검증 항목:
    - 함수 시그니처 일치
    - 반환값 구조 일치
    """
```

---

### 완료 기준 (DoD)

#### P0 완료 조건
- [ ] license_status 호출 시 Tier가 "Personal" 표시
- [ ] manager(use_dynamic=true) 호출 시 context 관련 피드백 반환
- [ ] pytest 통과 + MCP 수동 테스트 통과

#### P1 완료 조건
- [ ] handoff → verify → review → gate 워크플로우 작동
- [ ] verify가 실제 검증 수행 (체크리스트 자동 확인)
- [ ] review가 매니저 코드 리뷰 수행
- [ ] gate가 실제 lint/test/build 실행
- [ ] check_sync가 동기화 불일치 감지

---

### 예방책 (재발 방지)

1. **Stub 파일 수정 시 동기화 체크 필수**
   - Primary 파일 수정 → Stub 파일도 확인
   - CI에 check_sync 추가

2. **테스트 후 검증 필수**
   - pytest 통과 ≠ 완료
   - MCP 도구 수동 호출 테스트 필수

3. **검증 워크플로우 강제**
   - 기능 완료 시 handoff → verify → review → gate 순서 강제
   - gate 통과 전 커밋 차단 (pre-commit hook)

---

## v1.8 아키텍처 가드 + 긍정적 프레이밍

> **발견일**: 2026-01-26
> **근본 원인**: 아키텍처 결정 미기록 + 부정형 규칙의 역효과
> **연구 기반**: Wegner (1987) 사고 억제, Anthropic/OpenAI 공식 가이드

### 배경 (왜 필요한가)

실제 사용 시 발생한 문제:
- manager 도구 2곳에서 다르게 정의됨 → 충돌로 작업 불가
- 아키텍처 결정이 기록되지 않음 → 왜 이렇게 되었는지 알 수 없음
- "~하지 마라" 규칙 → 인간/AI 모두 역효과 (먼저 금지 대상 활성화)

**근본 원인**:
1. "언제/무엇을" 기록해야 하는지 미정의
2. 기존 코드 확인 없이 새 코드 추가 (수정보다 추가가 인지적으로 쉬움)
3. 규칙이 부정형 → Pink Elephant Problem

### A. 아키텍처 가드 (Pro)

| # | 기능 | 설명 | 우선순위 |
|---|------|------|----------|
| A1 | `arch_check` 도구 | 새 함수/모듈 추가 전 기존 코드 검색 강제 | P0 |
| A2 | Import 규칙 검증 | server.py의 잘못된 import 패턴 감지 | P0 |
| A3 | 중복 정의 감지 | 같은 함수명이 여러 곳에 정의되면 경고 | P1 |
| A4 | 아키텍처 결정 강제 기록 | 특정 파일 수정 시 record_decision 호출 강제 | P1 |

#### A1. arch_check 도구

```python
async def arch_check(
    name: str,           # 추가하려는 함수/클래스명
    purpose: str,        # 목적 설명
    path: str = "."      # 프로젝트 경로
) -> list[TextContent]:
    """새 코드 추가 전 기존 코드 확인

    1. Knowledge Base에서 관련 결정 검색
    2. Grep으로 같은 이름/비슷한 기능 검색
    3. 있으면: "기존 코드 수정 권장" + 위치
    4. 없으면: "추가 가능" + record_location 안내
    """
```

**완료 기준:**
- [ ] `arch_check("manager", "매니저 피드백")` 호출 시 기존 위치 반환
- [ ] 기존 코드 있으면 "수정 권장", 없으면 "추가 가능"
- [ ] 추가 후 record_location 호출 안내

#### A2. Import 규칙 검증

```python
async def check_imports(path: str) -> list[TextContent]:
    """server.py의 import 패턴 검증

    규칙 (LOCKED #30):
    - ✅ from .tools import xxx
    - ❌ from .tools.manager import xxx
    - ❌ from .tools.manager.core import xxx

    위반 시 경고 + 수정 방법 안내
    """
```

**완료 기준:**
- [ ] server.py 분석하여 tools/xxx/ 직접 import 감지
- [ ] 위반 시 WARN + 올바른 import 방법 안내
- [ ] can_code에 통합 (선택적)

#### A3. 중복 정의 감지

```python
async def check_duplicates(path: str) -> list[TextContent]:
    """같은 함수명이 여러 곳에 정의되었는지 확인

    1. __init__.py들에서 export된 함수명 수집
    2. 같은 이름이 2곳 이상이면 경고
    3. "단일 위치에서만 export 규칙" 안내
    """
```

**완료 기준:**
- [ ] tools/__init__.py와 tools/xxx/__init__.py의 export 비교
- [ ] 중복 발견 시 경고 + 어느 것을 사용해야 하는지 안내

#### A4. 아키텍처 결정 강제 기록

```python
# 트리거 파일 목록 (CLAUDE.md에도 명시)
ARCH_TRIGGER_FILES = [
    "server.py",
    "tools/__init__.py",
    "**/core.py",
    "license*.py",
    "api_client.py",
]

# 이 파일들 수정 시 can_code가 record_decision 호출 안내
```

**완료 기준:**
- [ ] ARCH_TRIGGER_FILES 수정 시 "아키텍처 결정 기록 필요" 메시지
- [ ] record_decision 호출 예시 제공

---

### B. 긍정적 프레이밍 가이드 (Free)

| # | 기능 | 설명 | 우선순위 |
|---|------|------|----------|
| B1 | 규칙 변환 가이드 | 부정형 → 긍정형 변환 안내 | P1 |
| B2 | CLAUDE.md 검사 | 부정형 규칙 감지 및 변환 제안 | P2 |
| B3 | Manager 피드백 개선 | "~하지 마라" 대신 "~해라"로 출력 | P2 |

#### B1. 규칙 변환 가이드

```python
NEGATIVE_TO_POSITIVE = {
    "금지": "사용: {}",
    "하지 마라": "대신: {}",
    "피하라": "권장: {}",
    "안 됨": "방법: {}",
}

def convert_rule(negative_rule: str) -> str:
    """부정형 규칙을 긍정형으로 변환 제안"""
```

**예시:**
| 부정형 | 긍정형 |
|--------|--------|
| "중복 정의 금지" | "각 함수는 하나의 위치에서만 export" |
| "직접 import 금지" | "server.py는 tools/__init__.py에서 import" |
| "기록 안 하면 안 됨" | "아키텍처 변경 시 record_decision 호출" |

#### B2. CLAUDE.md 검사

```python
async def check_rules_framing(path: str) -> list[TextContent]:
    """CLAUDE.md의 규칙 프레이밍 검사

    1. 부정형 패턴 감지 ("금지", "하지 마", "안 됨", "피하")
    2. 긍정형 변환 제안
    3. 연구 근거 안내 (Wegner, Anthropic)
    """
```

---

### 완료 기준 (DoD)

#### P0 완료 조건
- [ ] arch_check 호출 시 기존 코드 검색 동작
- [ ] check_imports 호출 시 잘못된 import 감지
- [ ] 현재 manager 충돌 감지됨

#### P1 완료 조건
- [ ] check_duplicates로 중복 정의 감지
- [ ] ARCH_TRIGGER_FILES 수정 시 기록 안내
- [ ] 규칙 변환 가이드 제공

#### P2 완료 조건
- [ ] CLAUDE.md 부정형 규칙 감지
- [ ] Manager 피드백이 긍정형으로 출력

---

### 기술 결정 (Knowledge Base 기록됨)

| ID | 결정 | 상태 |
|----|------|------|
| #30 | server.py는 tools/__init__.py에서만 import | 🔒 LOCKED |
| #31 | Pro 기능: API 권한 → 로컬 실행 (ship 패턴) | 🔒 LOCKED |
| #32 | Manager 충돌: 통합 필요 | ⚠️ OPEN |
| #37 | 파일 구조: xxx.py(진입점), xxx_pro.py(구현), xxx/(내부) | 🔒 LOCKED |
| #38 | 규칙은 긍정형으로 작성 | 🔒 LOCKED |
| #39 | 아키텍처 변경 시 record_decision 호출 | 🔒 LOCKED |
| #40 | 새 코드 추가 전 기존 코드 확인 | 🔒 LOCKED |

---

### 연구 근거

**Wegner (1987)**: "하얀 곰 생각 마라" → 더 많이 생각함 (rebound effect, d ≈ 0.30)

**Anthropic 공식 문서**:
> "Tell Claude what to do instead of what not to do."
> ❌ "Do not use markdown"
> ✅ "Use smoothly flowing prose paragraphs"

**OpenAI Help Center**:
> "Using negative instructions instead of positive framing" - 피해야 할 실수로 명시

**효과 크기**:
- 긍정형 지시 (implementation intentions): medium-to-large effect
- 부정형 지시 (thought suppression): rebound effect (d = 0.30)

---

## v1.9 도구 통합 + Deprecation

> **완료일**: 2026-01-26
> **목표**: 유사 도구 통합, API 단순화

### 배경 (왜 필요한가)

MCP 도구 분석 결과:
- 52개 도구 중 9개 유사 그룹 발견
- 5개 기능 중복 (scan_docs ≈ can_code)
- 6개 통합 가능 (get_prd_template → start --template)

### A. Deprecation Warnings

| Deprecated | 대체 | Migration |
|------------|------|-----------|
| `scan_docs` | `can_code` | `can_code(path)` |
| `analyze_docs` | `can_code` | `can_code(path)` |
| `verify` | `ship` | `ship(path, steps=["lint", "test"])` |
| `gate` | `ship` | `ship(path, steps, auto_fix)` |
| `handoff` | `record_decision` + `update_progress` | 조합 사용 |
| `get_prd_template` | `start` | `start(path, template="web-app")` |
| `get_prd_guide` | `start` | `start(path, guide=True)` |
| `init_docs` | `start` | `start(path, init=True)` |
| `init_rules` | `setup_cli` | `setup_cli(path, rules="web")` |
| `hook_design` | `setup_cli` | `setup_cli(path, hook="design")` |
| `hook_verify` | `setup_cli` | `setup_cli(path, hook="verify")` |

### B. 옵션 확장

#### start 도구 통합

```python
start(
    path: str,
    template: str = None,     # get_prd_template 대체
    layout: str = "standard", # lite | standard | detailed
    guide: bool = False,      # get_prd_guide 대체
    init: bool = False,       # init_docs 대체
    project_type: str = None, # 타입 강제 지정
    project_name: str = None
)
```

#### setup_cli 도구 통합

```python
setup_cli(
    path: str,
    level: str = "remind",
    rules: str = None,        # init_rules 대체: web | api | fullstack | minimal
    hook: str = None,         # hook_design/hook_verify 대체: design | verify
    hook_trigger: str = None  # pre_code | post_code | pre_commit 등
)
```

### C. 신규 도구

| 도구 | 설명 | 버전 |
|------|------|------|
| `debug_runtime` | MCP 런타임 환경 진단 | v3.2 |
| `check_sync` | 파일 쌍 동기화 검증 | v3.1 |

### 완료 기준 (DoD)

- [x] 11개 도구에 deprecation warning 추가
- [x] `start --template/--guide/--init` 옵션 동작
- [x] `setup_cli --rules/--hook` 옵션 동작
- [x] README.md 업데이트
- [x] CLAUDE.md에 migration guide 추가

---

## v3.1 런타임 안전장치

> **완료일**: 2026-01-27
> **목표**: 사이드이펙트 체크, 상업용 안전장치

### A. check_sync 도구

파일 쌍 동기화 검증:
- `license.py` ↔ `license_free.py`: 함수 시그니처
- `messages/en.py` ↔ `messages/ko.py`: 메시지 키

### B. ship 안전장치 (Pro)

```python
_run_safety_checks():
    - 시크릿 파일 탐지 (.env, *.key, *.pem)
    - 시크릿 패턴 탐지 (API key, password)
    - .env.example 존재 확인
    - git 추적 시크릿 → BLOCK
```

### C. PRD Diff + 영향 분석

save_prd 시:
- 이전 PRD 백업 (`.claude/prd_history/`)
- 변경 내용 분석 (추가/삭제 라인)
- 영향받는 파일 검색

### 완료 기준 (DoD)

- [x] check_sync 도구 구현
- [x] ship 안전장치 구현
- [x] save_prd diff 분석 구현

---

## v3.2 MCP 런타임 디버그

> **완료일**: 2026-01-27
> **목표**: MCP 환경 진단 도구

### debug_runtime 도구

```python
debug_runtime(project_path: str = None):
    - sys.executable 출력
    - clouvel.__file__ 출력
    - is_developer() 결과
    - can_use_pro() 결과
    - 환경 변수 (CLOUVEL_DEV 등)
```

### 완료 기준 (DoD)

- [x] debug_runtime 도구 구현
- [x] server.py에 등록
- [x] MCP 재시작 후 테스트 통과

---

## 테스트 커버리지 강화

> **완료일**: 2026-01-27
> **목표**: P0 테스트 파일 작성

### 추가된 테스트 파일

| 파일 | 테스트 수 | 내용 |
|------|----------|------|
| `test_knowledge.py` | 35 | Knowledge Base 전체 |
| `test_ship.py` | 23 | Ship 도구 전체 |

### 전체 테스트 현황

```
234 passed, 7 skipped
```

### 완료 기준 (DoD)

- [x] test_knowledge.py 작성 (20+ 테스트)
- [x] test_ship.py 작성 (15+ 테스트)
- [x] 전체 테스트 통과

---

## v1.10 Review 도구 (Pro)

> **상태**: 설계 완료
> **우선순위**: P1
> **담당**: PM

### 배경

현재 워크플로우: `handoff → verify → gate`

**문제**: 코드 리뷰 단계 누락. ship 전에 매니저 관점 검토가 없음.

### 제안 워크플로우

```
handoff → review → verify → gate → ship
```

### API 설계

```python
@mcp_tool
async def review(
    path: str,
    scope: str = "feature",  # file | feature | full
    managers: list[str] = None,  # 특정 매니저만 (기본: auto)
    base_branch: str = "main"  # diff 기준 브랜치
) -> list[TextContent]:
    """매니저들의 코드 리뷰

    1. git diff로 변경 파일 수집
    2. 변경 코드 분석
    3. 매니저별 관점에서 리뷰
    4. 이슈 및 수정 제안 반환
    """
```

### 응답 형식

```markdown
## 🔍 Code Review

**Scope**: feature (login-auth)
**Files**: 5 changed (+234 -45)

### 👔 PM Review
- ✅ PRD 요구사항 충족
- ⚠️ 에러 메시지 사용자 친화적이지 않음 (line 45)

### 🔧 CTO Review
- ✅ 아키텍처 패턴 준수
- ❌ N+1 쿼리 발견 (user_service.py:78)
  ```suggestion
  # Before
  for user in users:
      profile = get_profile(user.id)

  # After
  profiles = get_profiles_batch([u.id for u in users])
  ```

### 🔒 CSO Review
- ⚠️ 입력 검증 누락 (auth.py:23)
- ❌ SQL 인젝션 위험 (query.py:56)

### 📊 Summary
| Manager | Pass | Warn | Fail |
|---------|------|------|------|
| PM | 3 | 1 | 0 |
| CTO | 2 | 0 | 1 |
| CSO | 1 | 1 | 1 |

**Verdict**: ⚠️ 2 issues must be fixed before ship
```

### 매니저별 리뷰 관점

| 매니저 | 리뷰 관점 |
|--------|----------|
| PM | PRD 충족, 기능 완성도, UX |
| CTO | 아키텍처, 성능, 코드 품질 |
| QA | 테스트 커버리지, 엣지 케이스 |
| CSO | 보안 취약점, 인증/인가 |
| CFO | 비용 영향 (API 호출, 리소스) |
| CDO | UI/UX 일관성 |

### 구현 계획

| Phase | 내용 | 예상 |
|-------|------|------|
| 1 | git diff 파싱 + 파일 수집 | 2h |
| 2 | 매니저별 리뷰 프롬프트 | 3h |
| 3 | Worker API 연동 | 2h |
| 4 | 응답 포맷터 | 2h |
| 5 | 테스트 | 2h |

### 완료 기준 (DoD)

- [ ] `review` 도구 MCP 등록
- [ ] git diff 기반 변경 파일 수집
- [ ] 매니저별 리뷰 프롬프트 작성
- [ ] Worker API 또는 로컬 실행 지원
- [ ] test_review.py 10+ 테스트
- [ ] 문서 업데이트
