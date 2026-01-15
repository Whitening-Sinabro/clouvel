# Clouvel PRD v2.0

> **Claude + Shovel = Clouvel**
> 바이브코딩 프로세스를 강제해서 초보자도 후반부에 안 터지게 해주는 도구

---

## 메타 정보

| 항목 | 내용 |
|------|------|
| **버전** | 2.0 |
| **작성일** | 2026-01-15 |
| **상태** | Draft |
| **작성자** | Shovel + Claude |
| **이전 버전** | v1.1 (docs 빨리 읽기 → 폐기) |

---

## 버전 변경 이유

### v1.1의 문제점

| 항목 | v1.1 | 문제 |
|------|------|------|
| 한 줄 정의 | docs 빨리 읽기 (view 20번→1번) | 52초 → 전체 작업의 2% |
| ROI | 48시간 개발 / 1시간 월간 절약 | 회수 기간 48개월 |
| 진짜 병목 | docs 읽기 | ❌ 아님 |

### v2.0 전환 계기

PM 인터뷰를 통해 **진짜 문제** 발견:

```
1. PRD/검증 없이 바로 코딩 시작
2. 압축으로 맥락 소실
3. 문서-코드 불일치
4. 에러 학습 안 됨
        ↓
   후반부에 터짐 💥
```

---

# Part A: 제품

## A1. 개요

### 한 줄 정의

> **바이브코딩 베스트 프랙티스를 도구로 강제해서, 초보자도 빠짐없이 따라할 수 있게 해주는 시스템**

### 고객 문제

```
핵심 문제:
바이브코딩 초보자들이 PRD/검증/계획 없이 바로 코딩 시작
→ 처음엔 잘 됨
→ 중반부터 꼬이기 시작
→ 후반에 전부 터짐

세부 문제:
1. 체계적인 계획 없이 코드에 끌려다님
2. 문서 업데이트 안 함 → 코드-문서 불일치
3. 압축으로 맥락 소실 → 같은 말 반복
4. 에러 학습 안 됨 → 같은 실수 반복
5. PROGRESS 업데이트 안 됨 → 진행 상황 불명확
6. git log 안 봄 → 변경 이력 파악 안 됨
```

### 고객 검증

#### 1차 검증: 본인 경험 (Shovel)

```yaml
검증 방법: 직접 경험

겪은 문제:
  - 작업 중 Claude가 컨텍스트 압축/잊어버림
  - "다시 읽어볼게요" 반복
  - 지시 무시 / 같은 말 반복 입력
  - 문서-코드 불일치로 충돌 발생
  - /verify, /gate 실패 → 수정 → 재실패 루프

결론: 본인이 쓰면서 개선 (Dog Fooding)
```

#### 2차 검증: 웹 리서치 (2026-01-15)

| 출처 | 문제점 |
|------|--------|
| **Medium** | "처음은 쉽고, 끝은 어렵다" |
| **한국 maily.so** | "체계적인 계획 없이 시작 → 코드에 끌려다님" |
| **Stack Overflow** | "거의 맞는데 안 맞음 → 수정 시간 > 절약 시간" |
| **ZenCoder** | "기술 부채 누적 → 후반부에 터짐" |
| **CIO 한국** | "5개 도구 평가 → 69개 보안 취약점 발견" |
| **바이라인네트워크** | "AI가 거짓말/은폐 → DB 날아감 사례" |
| **Wikipedia** | "'vibe coding hangover' - 개발 지옥" |

#### 핵심 인용구

> "체계적인 계획이 없기 때문에 화면에 나타나는 코드에 이끌려 가게 됩니다" — maily.so

> "두 명의 엔지니어가 이제 50명의 기술 부채를 만들 수 있다" — 업계 평가

> "초반에 아낀 시간은 나중에 원래 의도했던 대로 코드를 다시 작성하는 데 사용해야 합니다" — ZenCoder

### 우리 솔루션

```
핵심:
바이브코딩 베스트 프랙티스 (PRD, Boris 검증, Todo 등)를
도구로 강제해서 초보자도 빠짐없이 실행하게 함

방법:
1. 프로젝트 연결 → 자동 스캔
2. 빠진 것 감지 → "PRD 없네요" 알림
3. 가이드 제공 → PRD 작성 인터뷰
4. 검증 체크리스트 → Boris 방식 강제
5. 문서-코드 Sync 감지 → 불일치 경고
```

---

## A2. 타겟 사용자

### Primary Persona

```yaml
이름: 초보 바이브코더
특징:
  - AI와 협업하여 개발 (Cursor, Claude 웹 등)
  - 코딩 경험 적음 또는 없음
  - PRD, 검증 프로세스 모름
  - "일단 만들어보자"로 시작

고통:
  - "처음엔 잘 되다가 갑자기 안 됨"
  - "뭐가 잘못된 건지 모르겠음"
  - "Claude가 자꾸 까먹음"
  - "코드가 점점 꼬여감"

현재 해결책:
  - 없음 (문제인지도 모름)
  - 또는 포기

우리 제품 사용 시 변화:
  - PRD 먼저 작성 → 목표 명확
  - 검증 프로세스 따름 → 품질 향상
  - 문서-코드 Sync → 일관성 유지
  - 결과: 후반부에 안 터짐
```

### Secondary Persona

```yaml
이름: Shovel (본인)
특징:
  - 코딩 인스트럭터
  - 여러 프로젝트 동시 진행
  - Boris Cherny 방식 사용 중
  - PM 역할도 겸함

용도:
  - Dog Fooding (본인이 먼저 사용)
  - 학생들에게 가르칠 도구
```

---

## A3. 기능 요구사항

### MVP (v2.0)

| ID | 기능 | 설명 | 우선순위 |
|----|------|------|----------|
| F001 | `/docs/scan` | 프로젝트 docs 폴더 스캔 | P0 |
| F002 | `/docs/analyze` | 빠진 것 감지 (PRD, 검증 등) | P0 |
| F003 | `/docs/sync` | 문서-코드 불일치 감지 | P0 |
| F004 | `/guide/prd` | PRD 작성 가이드 (인터뷰 형식) | P0 |
| F005 | `/guide/verify` | Boris 검증 체크리스트 | P0 |
| F006 | 웹 대시보드 | 시각적 현황 표시 | P0 |
| F007 | 후원 페이지 | Buy me a coffee 링크 | P0 |

### v2.1+ (추후)

| ID | 기능 | 설명 | 우선순위 |
|----|------|------|----------|
| F008 | MCP 서버 | Cursor/Claude Code 연동 | P1 |
| F009 | 에러 매니저 | 에러 학습/기록 시스템 | P1 |
| F010 | PROGRESS 자동화 | 진행 상황 자동 업데이트 | P1 |
| F011 | git log 분석 | 변경 이력 기반 분석 | P2 |
| F012 | 튜토리얼 | "바이브코딩 제대로 하는 법" | P2 |

---

## A4. 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────┐
│  Clouvel API (FastAPI Backend)              │
│  Port: 8000                                 │
│                                             │
│  ├── /docs/scan      - 프로젝트 스캔        │
│  ├── /docs/analyze   - 빠진 것 감지         │
│  ├── /docs/sync      - 문서-코드 Sync       │
│  ├── /guide/prd      - PRD 가이드           │
│  └── /guide/verify   - 검증 체크리스트      │
└─────────────────────────────────────────────┘
              ↑
              │ API 호출
              ↓
┌─────────────────────────────────────────────┐
│  Agent Layer (Claude가 수행)                │
│                                             │
│  ├── API 결과 해석                          │
│  ├── "PRD 없네, 만들자" 제안                │
│  ├── 체크리스트 가이드                      │
│  └── 진행 상황 리마인드                     │
└─────────────────────────────────────────────┘
              ↑
              │ 사용자 환경에 따라
              ↓
┌──────────────┬──────────────┬───────────────┐
│ Claude 웹    │ Cursor       │ Claude Code   │
│ (Artifact)   │ (MCP 서버)   │ (MCP 서버)    │
│              │              │               │
│ MVP 타겟 ⭐  │ v2.1+        │ v2.1+         │
└──────────────┴──────────────┴───────────────┘
```

### 프로젝트 구조

```
Clouvel/
├── docs/
│   └── 01-PRD-v2.0.md          # 이 문서
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱
│   ├── api/
│   │   ├── __init__.py
│   │   ├── docs.py              # /docs 라우터
│   │   └── guide.py             # /guide 라우터
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scanner.py           # 폴더 스캔
│   │   ├── analyzer.py          # 빠진 것 감지
│   │   ├── sync_checker.py      # 문서-코드 Sync
│   │   └── guide_generator.py   # 가이드 생성
│   └── models/
│       ├── __init__.py
│       └── schemas.py           # Pydantic 모델
├── web/                         # 웹 대시보드 (추후)
├── tests/
├── requirements.txt
├── README.md
└── CLAUDE.md
```

---

## A5. API 명세

### POST /docs/scan

**Request**
```json
{
  "path": "/path/to/project/docs",
  "recursive": true
}
```

**Response**
```json
{
  "project_name": "vivorbis",
  "scanned_at": "2026-01-15T12:00:00Z",
  "total_files": 29,
  "documents": [
    {
      "filename": "01-PRD-v4.0.md",
      "category": "core",
      "type": "PRD",
      "version": "4.0",
      "modified_at": "2026-01-13T14:00:00Z",
      "age_days": 2
    }
  ]
}
```

### POST /docs/analyze

**Request**
```json
{
  "path": "/path/to/project/docs"
}
```

**Response**
```json
{
  "project_name": "vivorbis",
  "analysis": {
    "missing": [
      {"type": "CHANGELOG", "severity": "medium"},
      {"type": "TESTING_PLAN", "severity": "high"}
    ],
    "outdated": [
      {"file": "PRD.md", "age_days": 30, "suggestion": "업데이트 필요"}
    ],
    "recommendations": [
      "PRD가 30일 이상 지났습니다. 현재 코드와 일치하는지 확인하세요.",
      "테스트 계획 문서가 없습니다. 검증 프로세스 추가를 권장합니다."
    ]
  },
  "health_score": 65
}
```

### POST /docs/sync

**Request**
```json
{
  "project_path": "/path/to/project",
  "docs_path": "/path/to/project/docs"
}
```

**Response**
```json
{
  "sync_issues": [
    {
      "file": "01-PRD-v4.0.md",
      "issue": "outdated",
      "last_modified": "2026-01-08",
      "days_old": 7,
      "code_commits_since": 5,
      "suggestion": "코드가 5번 커밋됐는데 문서 업데이트 없음"
    },
    {
      "file": "PROGRESS.md",
      "issue": "stale",
      "last_modified": "2026-01-01",
      "suggestion": "진행 상황 업데이트 필요"
    }
  ],
  "sync_score": 45
}
```

### GET /guide/prd

**Response**
```json
{
  "guide_type": "prd",
  "title": "PRD 작성 가이드",
  "steps": [
    {
      "step": 1,
      "question": "이 프로젝트를 한 문장으로 설명하면?",
      "purpose": "핵심 정의",
      "example": "카드뉴스를 AI로 쉽게 만드는 웹 에디터"
    },
    {
      "step": 2,
      "question": "누가 쓰나요? (구체적 페르소나)",
      "purpose": "타겟 정의"
    }
  ],
  "template_url": "/templates/prd.md"
}
```

### GET /guide/verify

**Response**
```json
{
  "guide_type": "verify",
  "title": "Boris Cherny 검증 프로토콜",
  "source": "Anthropic 공식 방식",
  "workflow": [
    {"step": 1, "action": "/handoff", "description": "의도 기록"},
    {"step": 2, "action": "/clear", "description": "Context Bias 제거"},
    {"step": 3, "action": "/verify", "description": "새로운 눈으로 검증"},
    {"step": 4, "action": "/gate", "description": "typecheck/lint/test/build"}
  ],
  "checklist": {
    "before_commit": [
      "기능 검증 완료?",
      "엣지 케이스 처리?",
      "에러 핸들링?",
      "typecheck 통과?",
      "lint 통과?",
      "test 통과?"
    ]
  }
}
```

---

## A6. 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 스캔 정확도 | 100% | Vivorbis 테스트 |
| 빠진 것 감지율 | 95%+ | 수동 검증 |
| 사용자 수 (스레드) | 관심 표명 10명+ | 댓글 수 |
| 실제 사용자 | 5명+ (베타) | 후원/피드백 |
| 후원 | 1건+ | Buy me a coffee |

---

# Part B: 비즈니스

## B1. 포지셔닝

### 경쟁 분석

| 대안 | 설명 | 한계 | Clouvel 차별점 |
|------|------|------|----------------|
| **없음** | 그냥 바이브코딩 | 후반부에 터짐 | 프로세스 강제 |
| **블로그/가이드** | "이렇게 해라" 글 | 읽고 안 함, 빼먹음 | 도구로 강제 |
| **BMAD** | 복잡한 워크플로우 | 설정 어려움, 불안정 | 단순, 실전 검증 |
| **본인 경험** | 시행착오로 배움 | 시간 오래 걸림 | 즉시 적용 가능 |

### 차별화

```
다른 것들: "이렇게 해야 해" (정보 제공)
Clouvel: "이렇게 해" (도구로 강제)

핵심 차별점:
1. 정보 → 실행으로 전환
2. 초보자도 빠짐없이 따라함
3. Boris Cherny 방식 내장
4. 실시간 문서-코드 Sync 감지
```

---

## B2. 수익 모델

### MVP: 무료 + 후원

```
이유:
1. PMF 검증 전 → 유료화 시기상조
2. 사용자 확보 우선
3. 후원 = 관심도 측정

방법:
- 도구 자체: 무료
- Buy me a coffee 링크
- 스레드/README에 후원 안내
```

### v2.0+: 검토 예정

```
옵션:
A) 계속 무료 + 후원
B) Freemium (기본 무료, 고급 기능 유료)
C) 크레딧 기반 (사용량 과금)

결정 시점: 사용자 100명+ 후
```

---

## B3. GTM (Go-to-Market)

### Phase 1: 씨앗 (현재)

```
목표: 관심 있는 사람 10명

채널:
- 스레드 (글 올림 ✅)
- 트위터
- 개발자 커뮤니티

메시지:
"바이브코딩 하다가 후반에 터진 적 있음?
프롬프트 문제 아니라 프로세스 문제임.
이거 해결하는 도구 만드는 중"
```

### Phase 2: 초기 (사용자 10명)

```
목표: 실제 사용자 + 피드백

방법:
- 관심 표명한 사람에게 DM
- 베타 테스터 모집
- 1:1 온보딩
- 피드백 수집 → 개선
```

### Phase 3: 성장 (사용자 100명+)

```
목표: 입소문 + 자연 성장

방법:
- 성공 사례 공유
- 블로그/튜토리얼 작성
- Product Hunt 런칭
- 수익화 검토
```

---

# Part C: 실행

## C1. 기술 스택

```yaml
Backend:
  언어: Python 3.11+
  프레임워크: FastAPI
  서버: Uvicorn (포트 8000)

Frontend (웹 대시보드):
  프레임워크: Next.js (추후)
  또는: 간단히 HTML + Tailwind

배포:
  MVP: 로컬 실행
  v2.1+: Vercel

의존성:
  - fastapi
  - uvicorn
  - python-frontmatter
  - pydantic
  - python-dateutil
```

---

## C2. 개발 체크리스트

### Phase 1: 기본 API (3일)

- [x] 프로젝트 구조 생성
- [x] CLAUDE.md 작성
- [x] requirements.txt 작성
- [x] src/main.py 기본 구조
- [ ] /docs/scan 엔드포인트
- [ ] /docs/analyze 엔드포인트
- [ ] Vivorbis로 테스트

### Phase 2: 가이드 API (2일)

- [ ] /guide/prd 엔드포인트
- [ ] /guide/verify 엔드포인트
- [ ] PRD 템플릿 작성
- [ ] Boris 체크리스트 작성

### Phase 3: Sync 감지 (2일)

- [ ] /docs/sync 엔드포인트
- [ ] git log 분석 (기본)
- [ ] 수정일 기반 감지

### Phase 4: 대시보드 (3일)

- [ ] 웹 UI 설계
- [ ] 대시보드 구현
- [ ] 후원 페이지 추가

### Phase 5: 런칭 (2일)

- [ ] README 작성
- [ ] 스크린샷/데모
- [ ] 스레드 업데이트
- [ ] 베타 테스터 모집

---

## C3. Acceptance Criteria

### /docs/scan

```gherkin
Feature: 프로젝트 docs 스캔

  Scenario: 정상 스캔
    Given Vivorbis docs 폴더가 있다
    When POST /docs/scan 호출한다
    Then 29개 파일 정보가 반환된다
    And 각 파일에 category, type, version이 있다

  Scenario: 빈 폴더
    Given 빈 docs 폴더가 있다
    When POST /docs/scan 호출한다
    Then total_files는 0이다
```

### /docs/analyze

```gherkin
Feature: 빠진 것 감지

  Scenario: PRD 없는 프로젝트
    Given docs 폴더에 PRD가 없다
    When POST /docs/analyze 호출한다
    Then missing에 "PRD"가 포함된다
    And severity는 "high"이다

  Scenario: 오래된 문서 감지
    Given PRD가 30일 전에 수정됐다
    When POST /docs/analyze 호출한다
    Then outdated에 PRD가 포함된다
```

---

## C4. 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 관심 없음 | 중 | 높 | 본인이 쓰면 됨 |
| 기능 과다 | 중 | 중 | MVP 집중 |
| 시간 부족 | 높 | 중 | 우선순위 엄격 |
| 경쟁 도구 등장 | 낮 | 중 | 빠른 실행 |

---

## 버전 히스토리

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0 | 2026-01-15 | 초안 (docs 빨리 읽기) |
| 1.1 | 2026-01-15 | 확장성 아키텍처 추가 |
| **2.0** | **2026-01-15** | **완전 재정의 (바이브코딩 프로세스 강제 도구)** |

---

## 참고 자료

### 방법론
- [Boris Cherny Workflow](/mnt/project/Boris_Cherny_Claude_Code_Workflow.md)
- [검증 프로토콜](/mnt/project/Verification_Protocol_Guide.md)
- [Universal PRD Guidelines v4.0](/mnt/project/공용_PRD_지침서_v4.0.md)

### 고객 검증 출처
- Stack Overflow Blog - "A new worst coder has entered the chat"
- Medium - "Vibe-Coding First Impressions: The Beginning Is Easy, The End Is Hard"
- ZenCoder - "5 Vibe Coding Risks"
- maily.so - "'바이브 코딩'의 문제점"
- CIO 한국 - "바이브 코딩 확산, 보안에는 주의 필요"
- 바이라인네트워크 - "바이브코딩의 배신, AI 에이전트 때문에 DB 날린 개발자"

---

> **핵심 기억:**
> 
> "처음은 쉽고, 끝은 어렵다" — 바이브코딩의 현실
> 
> Clouvel은 이 "끝"을 쉽게 만드는 도구다.
> 
> PRD → 계획 → 검증 → 문서 Sync
> 
> 이 프로세스를 강제하면 후반부에 안 터진다.
