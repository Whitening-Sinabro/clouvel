# Shovel 명령어 상세 가이드 v7

> **대상**: Claude Code CLI 중심 + 웹 보조 사용자  
> **시작 루틴**: PRD 완성 → /start → /plan
> **v7 신규**: 에러 학습 시스템, 서버 검증

**Version**: 2.0  
**Last Updated**: 2026-01-15

---

## 📚 목차

1. [워크플로우별 명령어](#1-워크플로우별-명령어)
2. [상황별 명령어](#2-상황별-명령어)
3. [자주 헷갈리는 구분](#3-자주-헷갈리는-구분)
4. [CLI vs 웹 사용법](#4-cli-vs-웹-사용법)
5. [명령어 전체 목록](#5-명령어-전체-목록)

---

## 1. 워크플로우별 명령어

### Phase 0: 프로젝트 준비 (최초 1회)

#### `/start` - 프로젝트 온보딩

**언제**: 
- 새 프로젝트 시작
- 기존 프로젝트에 Shovel 도입

**왜**: 
- 프로젝트 타입 감지 (Web/Desktop/API)
- CLAUDE.md 자동 생성
- docs/ 폴더 구조 생성

**CLI**:
```bash
# 프로젝트 폴더에서
/start
```

**웹**:
```
"이 프로젝트에 Shovel Setup을 적용하려고 해.
프로젝트 구조를 분석하고 CLAUDE.md를 생성해줘."
```

**동작**:
1. package.json, 폴더 구조 분석
2. 프로젝트 타입 판단 (Next.js → Web)
3. 적절한 템플릿으로 CLAUDE.md 생성
4. docs/ 폴더 생성 (PRD, PLAN, BACKLOG)

**주의**:
- ⚠️ 기존 CLAUDE.md 있으면 백업 먼저
- ⚠️ git commit 권장 (복구 가능하게)

**예제**:
```bash
cd ~/projects/pathcraft-ai
/start

→ "Next.js 프로젝트 감지"
→ "CLAUDE.md 생성 완료"
→ "docs/PRD.template.md 생성"
```

---

### Phase 1: 프로젝트 재개/정리

#### `/sync` - 전체 동기화 🆕

**언제**:
- 프로젝트 재개 시 (오래 안 건드림)
- 문서 혼돈 시 (수정 많음)
- 방향성 재정립 필요 시
- 주간 정리 (매주 월요일 권장)

**왜**:
- docs 전체 파악
- 우선순위 재계산
- 중복/모순 제거
- 실행 계획 업데이트

**CLI**:
```bash
/sync
```

**웹**:
```
"프로젝트 문서들을 전체 분석하고 정리해줘.
docs 폴더의 모든 파일을 읽고:
1. 현황 파악
2. 우선순위 재계산
3. PLAN.md, TODO.md 업데이트"
```

**동작**:
1. docs/ 전체 파일 읽기
2. 현황 분석 리포트
3. 사용자 질문 (4-5개)
4. 우선순위 재계산 (RICE)
5. PLAN.md 업데이트
6. TODO.md 생성
7. IMPROVEMENTS.md 생성

**주의**:
- ⏱️ 5-10분 소요 (문서 많으면)
- 💬 중간에 질문 받음 (답변 필요)
- 📝 변경사항 확인 후 승인

**예제**:
```bash
# 2주 만에 PathcraftAI 재개
/sync

→ "F-002가 2주째 진행 중이네요. 막힌 부분이 있나요?"
→ "YouTube API 인증에서 막혔어요"
→ "F-003을 먼저 하는 게 좋겠어요. RICE 점수가 더 높아요"
→ "PLAN.md 업데이트 완료"
```

---

### Phase 2: 기능 개발

#### `/plan` - 계획 수립

**언제**:
- 새 기능 시작 전 (매번!)
- 복잡한 작업 전

**왜**:
- PRD 확인
- 구현 방법 계획
- 함정 미리 파악
- Boris: "좋은 계획이 문제 예방"

**CLI**:
```bash
/plan YouTube API 연동
```

**웹**:
```
"YouTube API 연동 기능을 계획해줘.
PRD F-003을 확인하고 구현 계획 세워줘."
```

**동작**:
1. PRD에서 해당 기능 찾기
2. AC (Acceptance Criteria) 확인
3. 구현 단계 제시
4. 주의사항 / 함정 경고
5. 사용자 승인 대기

**주의**:
- ⚠️ 계획 승인 전에 구현 시작 금지
- ⚠️ PRD 없는 기능 → BACKLOG로
- ⚠️ 손코딩 vs AI 활용 구분

**예제**:
```bash
/plan YouTube 빌드 수집

→ "PRD F-003 확인"
→ "구현 단계:
    1. YouTube Data API 키 설정
    2. 검색 엔드포인트 구현
    3. POB 링크 추출
    4. DB 저장"
→ "주의: API 할당량 제한 (10,000/day)"
→ "계획 승인하시면 /implement 실행"
```

---

#### `/implement` - 계획 실행

**언제**:
- /plan 승인 후

**왜**:
- 계획대로 구현
- 단계별 진행
- 자동 체크포인트

**CLI**:
```bash
/implement
```

**웹**:
```
"계획대로 구현해줘."
```

**동작**:
1. /plan의 단계 확인
2. 순서대로 구현
3. 각 단계 완료 시 확인
4. /check-complete 자동 실행

**주의**:
- ⚠️ /plan 없이 실행 금지
- ⚠️ 중간에 스펙 변경 금지
- ⚠️ 완료 시 자동으로 /check-complete

**예제**:
```bash
/implement

→ "Step 1: API 키 설정 중..."
→ "Step 1 완료"
→ "Step 2: 검색 엔드포인트 구현 중..."
→ "전체 구현 완료"
→ "/check-complete 실행합니다"
```

---

#### `/check-complete` - 껍데기/미연결 검사 🆕

**언제**:
- 기능 구현 직후 (자동)
- "완료" 선언 전 (필수!)

**왜**:
- 가장 흔한 실수 방지
  1. 기능 구현만 하고 미연결
  2. 껍데기만 만듦 (TODO)
  3. AI가 스펙 무시

**CLI**:
```bash
/check-complete
```

**웹**:
```
"방금 구현한 기능을 체크해줘:
1. 껍데기 없음?
2. 연결됨?
3. 동작함?"
```

**동작**:
```markdown
체크리스트 실행:
□ TODO, placeholder 없음?
□ import/export 연결됨?
□ 라우팅 등록됨?
□ UI에서 접근 가능?
□ 실제로 동작함?

→ 전체 통과: "/gate로 진행"
→ 실패: "수정 필요 항목 안내"
```

**주의**:
- 🚨 이거 건너뛰면 2-3일 디버깅
- ⚠️ 통과해도 /gate는 별도

**예제**:
```bash
/check-complete

→ "체크 1: TODO 검사... ✅"
→ "체크 2: import 검사... ❌"
→ "문제: YouTubeService가 컴포넌트에서 import 안 됨"
→ "수정 후 다시 실행하세요"
```

---

### Phase 3: 검증

#### `/handoff` - 의도 기록

**언제**:
- 기능 완료 시
- /clear 전 (필수!)

**왜**:
- Context Bias 제거 준비
- 다음 세션에서 검증용

**CLI**:
```bash
/handoff
```

**웹**:
```
"이 기능의 의도와 주의사항을 정리해줘."
```

**동작**:
```markdown
기록 내용:
1. 구현한 기능
2. 핵심 결정사항
3. 주의사항
4. 다음 검증 포인트
```

**주의**:
- ⚠️ /clear 전에 반드시
- ⚠️ 기록 복사해두기 (웹 환경)

**예제**:
```bash
/handoff

→ "YouTube API 연동 완료
   
   핵심 결정:
   - Quota 절약 위해 캐싱 추가
   - POB 링크만 추출 (전체 데이터 아님)
   
   주의사항:
   - API 키 .env에만
   - 하루 10,000 요청 제한
   
   검증 포인트:
   - 실제 검색 동작
   - 캐시 작동
   - 에러 핸들링"
```

---

#### `/clear` - Context Bias 제거

**언제**:
- /handoff 직후
- 검증 전 (필수!)

**왜**:
- Boris: "같은 세션에서 검증하면 자기 코드라 문제 못 봄"
- 품질 2-3배 향상

**CLI**:
```bash
/clear
```

**웹**:
```
[새 대화 시작]
```

**동작**:
- CLI: 대화 기록 삭제
- 웹: 새 대화창 열기

**주의**:
- ⚠️ /handoff 없이 하면 정보 손실
- ⚠️ 웹: /handoff 내용 복사해두기

---

#### `/verify` - 새로운 눈으로 검증

**언제**:
- /clear 직후
- 새 세션에서

**왜**:
- 객관적 검증
- Context Bias 없이

**CLI**:
```bash
/verify
```

**웹**:
```
[새 대화에서]
"/handoff 내용: [붙여넣기]

이 기능을 검증해줘:
- AC 충족?
- 엣지 케이스?
- 에러 핸들링?"
```

**동작**:
```markdown
검증 항목:
□ AC 전체 통과?
□ 엣지 케이스 처리?
□ 에러 핸들링?
□ 코드 품질?
□ 보안 이슈?

→ 통과: "/gate 진행"
→ 실패: "수정 후 /handoff부터 재시작"
```

**주의**:
- ⚠️ 웹에서는 /handoff 내용 필요
- ⚠️ 실패하면 처음부터 다시

**예제**:
```bash
# 새 세션에서
/verify

→ "handoff 내용 확인"
→ "검증 시작..."
→ "AC 전체 통과 ✅"
→ "엣지 케이스: API 실패 시 처리 ❌"
→ "수정 필요: 에러 핸들링 추가하세요"
```

---

#### `/gate` - 최종 관문

**언제**:
- /verify 통과 후
- 커밋 전 (필수!)

**왜**:
- 유일한 "완료" 정의
- lint → test → build → audit

**CLI**:
```bash
/gate
```

**웹**:
```
"Gate 검증 실행해줘:
pnpm lint && pnpm test && pnpm build"
```

**동작**:
```bash
1. pnpm lint   → ✅ / ❌
2. pnpm test   → ✅ / ❌
3. pnpm build  → ✅ / ❌
4. pnpm audit  → ✅ / ⚠️

→ 전체 통과: EVIDENCE.md 생성
→ 실패: 즉시 중단
```

**주의**:
- 🚨 하나라도 실패하면 0점
- ⚠️ 통과해야만 "완료"
- ⚠️ EVIDENCE.md가 증거

**예제**:
```bash
/gate

→ "Lint... ✅"
→ "Test... ✅ 12 passed"
→ "Build... ✅"
→ "Audit... ⚠️ 2 moderate"
→ "Gate PASS!"
→ "EVIDENCE.md 생성 완료"
```

---

### Phase 4: 마무리

#### `/review` - 코드 리뷰 + 학습

**언제**:
- Gate 통과 후
- 커밋 전

**왜**:
- 배운 점 기록
- 개선점 파악
- Compounding Rules 추가

**CLI**:
```bash
/review
```

**웹**:
```
"이번 작업을 리뷰해줘:
- 잘한 점
- 개선점
- 배운 점
- CLAUDE.md에 추가할 규칙"
```

**동작**:
```markdown
리뷰 내용:
1. Keep (잘한 것)
2. Problem (문제)
3. Try (시도할 것)
4. Compounding Rules 추가

→ ERROR_LOG 업데이트
→ CLAUDE.md 규칙 추가
```

**주의**:
- 📝 매번 하면 좋지만 선택
- 🎓 학습 목적

**예제**:
```bash
/review

→ "Keep: /plan으로 함정 미리 파악"
→ "Problem: API 할당량 고려 안 함"
→ "Try: 다음엔 외부 API 제약 먼저 확인"
→ "Rule: NEVER 외부 API 조사 생략"
```

---

#### `/commit` - 스마트 커밋

**언제**:
- /gate PASS 후
- (선택) /review 후

**왜**:
- 적절한 커밋 메시지 자동 생성
- 변경사항 요약

**CLI**:
```bash
/commit
```

**웹**:
```
"git status 확인하고 적절한 커밋 메시지 작성해줘."
```

**동작**:
```bash
1. git status 확인
2. 변경 파일 분석
3. 커밋 메시지 생성
   - feat: 새 기능
   - fix: 버그 수정
   - docs: 문서
4. 사용자 승인 후 커밋
```

---

## 2. 상황별 명령어

### 문제 발생 시

#### `/error-log` - 에러 분석 및 기록

**언제**:
- Gate 실패
- 2시간+ 같은 버그
- 디버깅 늪

**왜**:
- 체계적 분석 (5 Whys)
- 패턴 일반화
- 재발 방지 규칙

**CLI**:
```bash
/error-log
```

**동작**:
```markdown
5 Whys 분석:
1. 문제: [현상]
2. Why 1: [1차 원인]
3. Why 2: [2차 원인]
4. Why 3: [근본 원인]

→ 해결 방법
→ 예방 규칙 (NEVER/ALWAYS)
→ ERROR_LOG 기록
```

**예제**:
```bash
/error-log

→ "문제: YouTube API 500 에러"
→ "Why 1: API 키 유효하지 않음"
→ "Why 2: .env 파일 누락"
→ "Why 3: .env.example 문서화 안 함"
→ "규칙: ALWAYS .env.example 문서화"
```

---

### PM 관점 필요 시

#### `/pm` - PM 모드 가이드

**언제**:
- 기능 우선순위 결정
- 비즈니스 관점 필요
- 경쟁 분석 필요

**왜**:
- 제품 50% + 비즈니스 50%
- 수익화 고려

**CLI**:
```bash
/pm
```

**동작**:
- PM 체크리스트 제공
- RICE 계산 도움
- 경쟁 분석 가이드

---

#### `/interview` - 스펙 인터뷰

**언제**:
- 복잡한 기능 시작 전
- 요구사항 불명확

**왜**:
- Thariq 방식 인터뷰
- 구체적 스펙 도출

**CLI**:
```bash
/interview
```

**동작**:
- 질문 10개
- 답변 기반 스펙 작성
- PRD 초안 생성

---

#### `/design` - AI 패턴 탈피 가이드 🆕

**언제**:
- UI/디자인 작업 시 (자동 트리거)
- 랜딩페이지, 대시보드, 컴포넌트 제작

**왜**:
- AI가 만든 UI가 "뻔한 느낌" 방지
- Inter/Roboto, 보라 그라데이션, 3열 카드 그리드 탈피

**트리거 키워드** (자동 실행):
- 랜딩페이지, landing page, 대시보드, dashboard
- UI, 화면, 페이지, 컴포넌트, component
- 디자인, design, 레이아웃, layout

**CLI**:
```bash
/design
```

**동작**:
1. 요청 분석 (타입, 플랫폼)
2. AI 패턴 위험 체크
3. 개선된 프롬프트 생성

**출력 예시**:
```markdown
🎨 디자인 검사 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 요청: "랜딩페이지 만들어줘"

⚠️ 감지된 AI 패턴 위험:
  • 폰트 미지정 → Inter 기본값 위험
  • 색상 미지정 → 보라 그라데이션 위험
  • 레이아웃 미지정 → 3열 카드 그리드 위험

✅ 개선된 프롬프트:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build a SaaS landing page.
Font: Space Grotesk + Lato
Colors: #2C3E50 + #E74C3C + #FDFBF7
Layout: Asymmetric (60/40)
Avoid: Inter, purple gradients, uniform grids
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 v0/Lovable/Cursor에 복사해서 사용
```

**추천 대안**:
- **폰트**: Space Grotesk, Neue Montreal, Ogg, Instrument Serif
- **색상**: 따뜻한 대지색, 차분한 블루/그린, 기업용 따뜻함
- **레이아웃**: 비대칭(60/40), 매거진 스타일, 단일 열 내러티브

---

### 설정 확인 시

#### `/ssot-check` - SSOT 위반 검사

**언제**:
- 설정 파일 수정 후
- 타입 변경 후
- 분산 의심 시

**왜**:
- SSOT (Single Source of Truth) 유지
- 중복 설정 방지

**CLI**:
```bash
/ssot-check
```

**동작**:
```markdown
검사 항목:
□ .env vs 코드 하드코딩
□ 타입 정의 중복
□ 설정 파일 분산

→ 위반 발견 시 경고
```

---

## 3. 자주 헷갈리는 구분

### `/handoff` vs `/step-done`

| 구분 | /handoff | /step-done |
|------|----------|------------|
| **목적** | 의도 기록 | 자동 검증 트리거 |
| **타이밍** | 기능 완료 시 | 단계 완료 시 |
| **동작** | 기록만 | /handoff + /clear + /verify |
| **사용** | CLI: 수동 | CLI: 자동 |

**추천**: CLI는 /step-done만 쓰면 됨 (자동으로 /handoff 포함)

---

### `/verify` vs `/gate`

| 구분 | /verify | /gate |
|------|---------|-------|
| **검증 대상** | 기능 로직 | 코드 품질 |
| **방법** | AC, 엣지 케이스 | lint, test, build |
| **타이밍** | /clear 직후 | /verify 통과 후 |
| **실패 시** | 수정 후 재검증 | 0점, 즉시 중단 |

**둘 다 필수**: /verify (기능) → /gate (품질)

---

### `/clear` 타이밍

```
❌ 잘못된 순서:
구현 → /verify → /clear

✅ 올바른 순서:
구현 → /handoff → /clear → /verify

이유: Context Bias 제거가 목적
```

---

## 4. CLI vs 웹 사용법

### CLI (Claude Code)

**장점**:
- `/명령어` 바로 실행
- 자동화 (hooks)
- 병렬 세션 (tmux)

**단점**:
- 초기 설정 필요
- Windows 제약

**주 작업 환경**: CLI 권장

---

### 웹 (Claude.ai)

**장점**:
- 설정 불필요
- 어디서나 접근
- 자기 전 가벼운 작업

**단점**:
- 명령어 직접 타이핑 불가
- 자동화 없음

**보조 환경**: 잠들기 전, 이동 중

---

### 웹에서 명령어 사용법

**방법 1: 프롬프트로 요청**
```
"/plan YouTube API 연동 기능을 계획해줘"
```

**방법 2: 설명 형식**
```
"YouTube API 연동 기능을 시작하려고 해.
PRD를 확인하고 구현 계획을 세워줘."
```

**방법 3: 체크리스트 제공**
```
"기능 구현 완료했어. 체크해줘:
□ 껍데기 없음?
□ 연결됨?
□ 동작함?"
```

---

## 5. 명령어 전체 목록

### 필수 명령어 (빈도 높음)

| 명령어 | 사용 시점 | 빈도 |
|--------|-----------|------|
| `/sync` | 프로젝트 재개, 주간 정리 | 주 1회 |
| `/plan` | 기능 시작 전 | 기능당 1회 |
| `/implement` | 계획 승인 후 | 기능당 1회 |
| `/check-complete` | 구현 직후 | 기능당 1회 |
| `/gate` | 검증 완료 후 | 기능당 1회 |

### 검증 명령어

| 명령어 | 사용 시점 | 빈도 |
|--------|-----------|------|
| `/handoff` | 기능 완료 시 | 기능당 1회 |
| `/clear` | /handoff 직후 | 기능당 1회 |
| `/verify` | 새 세션에서 | 기능당 1회 |

### 선택 명령어

| 명령어 | 사용 시점 | 빈도 |
|--------|-----------|------|
| `/review` | 커밋 전 | 선택 |
| `/commit` | /gate 후 | 기능당 1회 |
| `/error-log` | 버그/막힘 | 필요 시 |
| `/pm` | 우선순위 결정 | 필요 시 |
| `/interview` | 스펙 불명확 | 필요 시 |
| `/ssot-check` | 설정 변경 후 | 필요 시 |
| `/design` | UI/디자인 작업 시 | 자동 트리거 🆕 |

### v7 신규 명령어 🆕

| 명령어 | 사용 시점 | 빈도 |
|--------|-----------|------|
| `/verify-server` | 서버 기능 완료 시 | 서버 기능당 1회 |
| `/learn-error` | 에러 쌓였을 때 | 주 1회 권장 |
| `/deep-debug` | 3회 반복 에러 | 자동 트리거 |

### 초기 설정 (1회)

| 명령어 | 사용 시점 |
|--------|-----------|
| `/start` | 프로젝트 시작 시 |

---

## 📋 실전 워크플로우 요약

### 일반적인 기능 개발 (클라이언트)

```bash
1. /sync              # 주간 정리 (월요일)
2. /plan [기능]       # 계획
3. /implement         # 구현
4. /check-complete    # 껍데기 체크
5. /handoff           # 의도 기록
6. /clear             # Context Bias 제거
7. /verify            # 새 세션 검증
8. /gate              # 최종 관문
9. /review            # 학습 (선택)
10. /commit           # 커밋
```

### 서버 기능 개발 🆕

```bash
1. /sync              # 주간 정리
2. /plan [기능]       # 계획
3. /implement         # 구현
4. /check-complete    # 껍데기 체크
5. /verify-server     # 🆕 서버 검증
6. /handoff           # 의도 기록
7. /clear             # Context Bias 제거
8. /verify            # 새 세션 검증
9. /gate              # 최종 관문
10. /commit           # 커밋
```

### 문제 발생 시

```bash
# 일반 에러
1. 에러 발생 → ERROR_LOG.md 자동 기록
2. 작업 계속

# 2시간+ 막힘
1. /error-log         # 분석
2. 해결
3. CLAUDE.md 규칙 추가

# 3회 반복 에러 🆕
1. 🚨 자동 /deep-debug 트리거
2. 작업 중단
3. 근본 원인 분석
4. 구조적 수정
5. 테스트 추가
6. 규칙화
```

### 에러 학습 사이클 🆕

```bash
# 매주 또는 에러 쌓였을 때
1. /learn-error       # 패턴 분석
2. CLAUDE.md 규칙 추가 확인
3. ERROR_LOG.md 자동 비움
```

### 프로젝트 재개 시

```bash
1. /sync              # 전체 정리
2. TODO.md 확인
3. /plan [다음 기능]
4. 작업 시작
```

---

## 🆕 v7 명령어 상세

### `/verify-server` - 서버 검증

**언제**:
- 서버/API 기능 완료 시
- /gate 전 (서버 기능인 경우)

**왜**:
- 환경변수 누락 방지
- API 에러 핸들링 검증
- 외부 의존성 안전성 확인

**CLI**:
```bash
/verify-server              # 전체 서버 검증
/verify-server --env        # 환경변수만
/verify-server --api        # API 라우트만
```

**동작**:
1. .env.example vs .env 비교
2. 하드코딩 시크릿 검사
3. API 라우트 에러 핸들링 검사
4. 외부 API timeout/rate limit 검사
5. 결과 리포트

---

### `/learn-error` - 에러 학습

**언제**:
- ERROR_LOG.md에 에러 쌓였을 때
- 주간 정리 시
- 시간 여유 있을 때

**왜**:
- 에러 패턴 → 규칙화
- 재발 방지
- Compounding Engineering

**CLI**:
```bash
/learn-error           # 전체 학습
/learn-error --preview # 미리보기만
```

**동작**:
1. ERROR_LOG.md 읽기
2. 패턴 분석 (유형별 그룹화)
3. NEVER/ALWAYS 규칙 생성
4. CLAUDE.md 업데이트
5. ERROR_LOG.md 비움

---

### `/deep-debug` - 근본 원인 분석

**언제**:
- 같은 에러 3회 반복 시 (자동 트리거)
- 복잡한 버그 (수동 실행)

**왜**:
- 땜빵 방지
- 근본 원인 해결
- 테스트로 재발 방지

**CLI**:
```bash
/deep-debug                        # 가장 빈번한 반복 에러
/deep-debug "TypeError-undefined"  # 특정 에러
```

**동작**:
1. 작업 중단 선언
2. 에러 컨텍스트 수집
3. 관련 코드 전체 분석
4. 데이터 플로우 추적
5. 근본 원인 분류
6. 구조적 수정 제안
7. 테스트 케이스 추가
8. CLAUDE.md 규칙 추가

**⚠️ 주의**:
- 땜빵(`if (!x) return;`) 금지
- 반드시 구조적 수정
- 테스트 없이 완료 금지

---

**Version**: 2.0  
**Last Updated**: 2026-01-15  
**For**: 수익화 목표 솔로 개발자
