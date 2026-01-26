# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-26 (v1.7.3 배포)

---

## 지금 상태

| 항목              | 상태                              |
| ----------------- | --------------------------------- |
| **clouvel**       | v1.7.3 PyPI 배포 완료             |
| **아키텍처**      | ⚠️ Manager 실행 경로 불일치 발견   |
| **Knowledge Base**| ✅ 아키텍처 결정 기록 완료        |
| **라이선스 서버** | ✅ 동작 중 (Polar.sh + Worker API) |
| **결제**          | ✅ Polar.sh 연동 완료             |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화     |

---

## 결론 (2026-01-26)

**Manager 실행 경로 불일치 문제 발견 및 문서화 완료**

- `server.py`가 `call_manager_api()` 대신 로컬 `tools/manager/` 모듈 사용
- `tools/manager/`는 PyPI 빌드에서 제외됨 → 설치 시 ImportError
- 문서: `docs/architecture/flow_manager.md`, `data_contracts.md`, `decision_log_manager.md`

**다음 액션 (택1)**:
1. 옵션1: `_wrap_manager()`가 `call_manager_api()` 호출하도록 수정 (권장)
2. 옵션2: `tools/manager/`를 PyPI 빌드에 포함

---

## 오늘 완료 (2026-01-26)

### 아키텍처 분석 및 기록 📋

**문제**: manager 도구 충돌로 다른 작업 불가

**근본 원인 분석**:
1. Import 규칙 미정의 → 두 곳에서 같은 함수 정의
2. 아키텍처 결정 미기록 → 왜 이렇게 되었는지 알 수 없음
3. 규칙이 부정형 → 역효과 발생

**Knowledge Base 기록 완료** (11개 결정, 10개 위치):

| ID | 카테고리 | 내용 | 상태 |
|----|----------|------|------|
| #30 | architecture | server.py Import 규칙 | 🔒 LOCKED |
| #31 | architecture | Pro 기능 패턴 (ship 표준) | 🔒 LOCKED |
| #32 | architecture | Manager 충돌 (미해결) | ⚠️ OPEN |
| #33 | architecture | 라이센스 모듈 구조 | 🔒 LOCKED |
| #34 | architecture | Trial 관리 (API 우선) | 🔒 LOCKED |
| #35 | architecture | Optional 의존성 | 🔒 LOCKED |
| #36 | architecture | 개발자 감지 | 🔒 LOCKED |
| #37 | architecture | 파일 구조 규칙 | 🔒 LOCKED |
| #38 | design | 긍정적 프레이밍 원칙 | 🔒 LOCKED |
| #39 | process | 기록 트리거 | 🔒 LOCKED |
| #40 | process | 코드 추가 전 확인 | 🔒 LOCKED |

**CLAUDE.md 업데이트**:
- 아키텍처 규칙 섹션 추가
- 기록 규칙 섹션 추가
- 긍정적 프레이밍 원칙 추가

**findings.md 업데이트**:
- Manager 충돌 분석 기록
- 기록된 결정/위치 목록

---

## 다음 할 일

### P0: Manager 충돌 해결 (#32)

**해결 방향**: ship 패턴으로 통일
1. `tools/manager.py` 생성 (진입점: API 권한 → 로컬 실행)
2. `tools/manager/` → `tools/manager_impl/` 이름 변경
3. `tools/__init__.py`의 중복 manager 제거
4. `server.py` import 정리

### P1: 테스트

- `pytest tests/` 실행
- uvx 환경 테스트

---

## 이전 완료 (2026-01-25)

### v1.6.6 배포 ✅ (Locked Decisions 완성)

**신규 기능**: Decision Lock 시스템 완성

| 도구 | 설명 |
|------|------|
| `record_decision(locked=True)` | 결정 잠금 (컨텍스트 드리프트 방지) |
| `unlock_decision(id, reason)` | 잠긴 결정 해제 (사유 필수) |
| `list_locked_decisions()` | 잠긴 결정 목록 조회 |
| can_code 🔒 표시 | 잠긴 결정은 `🔒 LOCKED` 배지로 표시 |

**테스트 통과** (2026-01-25 22:00):
- record → list → unlock → verify 전체 플로우 ✅
- 커밋: c81c3e4, PyPI 배포 완료, GitHub push 완료

### v1.6.4-5 배포 ✅ (File Tracking 강화)

**P0-P3 구현 완료**:

| 우선순위 | 내용 | 상태 |
|----------|------|------|
| P0 | pre-commit hook에 file tracking 체크 | ✅ |
| P1 | 경고에 복붙 가능 명령어 포함 | ✅ |
| P2 | CLAUDE.md에 record_file 규칙 | ✅ |
| P3 | can_code(mode="post") 후검증 | ✅ |

### v1.6.3 배포 ✅

**해결된 문제**: `license_status`가 "Unknown" 표시 → tier_info 정상 반환

| 항목 | 내용 |
|------|------|
| **커밋 1** | 697f16d - license_common + record_file |
| **커밋 2** | 4b54b3a - version bump |
| **PyPI** | v1.6.3 배포 완료 |
| **테스트** | uvx 환경 테스트 통과 |

### 변경 파일

| 파일 | 설명 |
|------|------|
| `license_common.py` | 공통 라이선스 로직 (신규) |
| `license_free.py` | common 모듈 사용하도록 수정 |
| `server.py` | record_file, list_files 추가 |
| `tools/tracking.py` | 파일 추적 도구 (신규) |
| `messages/en.py` | i18n 메시지 (신규) |
| `test_record_file.py` | 테스트 100개 (신규) |

### 제외된 파일 (보안)

- `.claude/planning/*` (마케팅/내부 전략)
- `docs/marketing/`
- `docs/PRD.md`, `CLAUDE.md`

---

## v1.5 계획 (2026-01-25 추가)

> **모토 이행**: "기록을 잃지 않는다"
> 상세: `docs/PRD.md` v1.5 섹션 참조

### 발견된 문제 (7개)

| # | 문제 | 카테고리 |
|---|------|----------|
| 1 | 파일 생성 자동 추적 없음 | 기록 |
| 2 | current.md 자동 업데이트 없음 | 기록 |
| 3 | DoD 체크 강제 없음 | can_code |
| 4 | 테스트 존재 확인 없음 | can_code |
| 5 | Manager context 분석이 얕음 | manager |
| 6 | Clouvel/MCP 토픽 없음 | manager |
| 7 | 동적 피드백이 generic | manager |

### 구현 순서

| Phase | 항목 | 상태 |
|-------|------|------|
| 1 | can_code 강화 (테스트/DoD 체크) | ✅ 완료 (2026-01-25) |
| 2 | pre-commit hook 강화 | ✅ 완료 (2026-01-25) |
| 3 | Manager 토픽 확장 | ✅ 완료 (2026-01-25) |
| 4 | Manager context 분석 개선 | ✅ 완료 (2026-01-25) |
| 5 | record_file 도구 | ✅ 완료 (2026-01-25) |

### Phase 1 완료 내용

**A2: DoD 패턴 추가** (`core.py:61-67`)
- `## DoD`, `## Definition of Done`, `## 완료 정의` 패턴 추가
- `## Criteria`, `## 기준` 패턴 추가

**A1: 테스트 메시지 개선** (`messages/en.py:70-71`)
- 테스트 없을 때 경고: `No Tests (⚠️ write tests before marking complete)`

### Phase 2 완료 내용

**A3: pre-commit hook 강화** (`server.py`, `setup.py`)
- `clouvel setup --hooks` 명령 추가
- PRD 체크 + 기록 파일 체크 + 보안 체크
- `files/created.md` 없으면 커밋 차단
- `status/current.md` 없으면 커밋 차단

### Phase 3 완료 내용

**B1: 토픽 확장** (`utils.py`, `data/__init__.py`)
- topic_keywords에 4개 토픽 추가: `mcp`, `internal`, `tracking`, `maintenance`
- CONTEXT_GROUPS에 매니저 매핑 추가
- 테스트: "Clouvel 기능 개선" → `['mcp', 'internal']` ✓

### Phase 4 완료 내용 (LLM 주의력 최적화 적용)

**B2: Context 분석 강화** (`utils.py`)
- 키워드 매칭 + 패턴 감지 결합
- 문제 패턴: "없다", "안 됨", "느려", "취약" → error/performance/security
- 요청 패턴: "추가", "구현", "수정", "테스트" → feature/maintenance

**B3: 동적 피드백 개선** (`formatter.py`)
- XML 구조화: `<critical_summary>`, `<situation_analysis>`, `<meeting_notes>`
- Bookending: critical issues를 처음과 끝에 반복 (U-shaped attention)
- 압축된 instruction: 장황한 템플릿 → 핵심 규칙만

### Phase 5 완료 내용

**A4: record_file 도구** (`tracking.py`)
- `record_file(path, file_path, purpose, deletable, session)` - 파일 생성 기록
- `list_files(path)` - 기록된 파일 목록 조회
- `.claude/files/created.md`에 자동 추가
- 중복 체크 포함

---

## 오늘 완료 (2026-01-24)

### 동적 회의 4회 진행 📋

> 상세 기록: `.claude/planning/meetings/2026-01-24-decisions.md`

#### 회의 1: 팀 라이선스 아키텍처
- [x] Worker KV 유지 (Supabase 추가 안 함)
- [x] MVP: Phase 1만 (rate limiting, team license validation)
- [x] 연기: PostgreSQL, 대시보드, Linear/Jira

#### 회의 2: 가격 책정
- [x] Personal Pro: $9.99/mo
- [x] Team 10: $129/mo ($12.9/user)
- [x] 프리미엄 근거: 주니어 성장 메트릭 (lock-in)
- [x] LAUNCH70: 70% off → $38.7/10석

#### 회의 3-4: Knowledge Base 설계
- [x] 저장소: SQLite (`~/.clouvel/knowledge.db`)
- [x] 50MB 제한, 40MB 아카이브 트리거
- [x] 5개 테이블 + FTS5 스키마 설계
- [x] 4개 신규 도구 API 설계
- [x] 8주 로드맵 수립

### 마케팅 런칭 🚀

- [x] **Twitter 쓰레드** 7개 올림 (@ShovelMaker91)
- [x] **Threads 포스트** 3개 올림 (@sinabrocoding)
- [x] **Reddit 워밍업** 시작 - r/ClaudeAI, r/SideProject 답글 각 1개
- [x] **LAUNCH70 쿠폰** 생성 (70% off, 50개 한정, Polar.sh)
- [x] **Demo GIF** GitHub Pages 배포 완료

### 마케팅 자동화 설정

- [x] Typefully 가입
- [x] Make.com 가입
- [x] Week 1 콘텐츠 예약 (월/화/수)
- [x] 2주치 콘텐츠 초안 작성 (`.claude/planning/content-drafts.md`)
- [x] 마케팅 일정표 작성 (`.claude/planning/marketing-schedule.md`)
- [x] Reddit 포스트 초안 v3 (`.claude/planning/reddit-posts.md`)

### 테스트 라이선스 발급

- [x] Worker API로 테스트 라이선스 발급 확인
- [x] 내 테스트 키: `TEST-0BM6-E8N6-L0V9` (Personal, 30일)
- [x] 배포용 Personal 키 5개 (14일 만료)
- [x] 배포용 Team 키 2개 (1/30 만료)
  - `TEST-E737-2CG1-I188`
  - `TEST-04Q2-5DY5-MSTH`

### 이전 완료 (v1.3.11~13)

- [x] manager 동적 회의록 생성 (Claude API 연동)
- [x] Windows cp949 인코딩 수정
- [x] manager import 조건부 처리 (Free 버전 호환)
- [x] PyPI 배포 성공 (v1.3.13)

---

## 이전 완료 (2026-01-22)

### v1.3.4 신규 기능

#### 템플릿 확장 (8개 카테고리, 16개 파일)

- [x] web-app (lite, standard, detailed) - 기존
- [x] api (lite, standard) - 신규
- [x] cli (lite, standard) - 신규
- [x] chrome-ext (lite, standard) - 신규
- [x] discord-bot (lite, standard) - 신규
- [x] landing-page (lite, standard) - 신규
- [x] saas (lite, standard) - 신규
- [x] generic (standard) - 기존

#### start 도구 개선 (Free)

- [x] 프로젝트 타입 자동 감지
  - 파일 패턴 분석 (manifest.json → chrome-ext)
  - 의존성 분석 (discord.js → discord-bot, stripe → saas)
- [x] 대화형 PRD 작성 가이드
  - 타입별 5-6개 질문 세트
  - Claude가 질문 → 사용자 답변 수집
- [x] save_prd 도구 추가 (PRD 저장)

#### 버전 체크 기능

- [x] PyPI API로 최신 버전 조회
- [x] 24시간 캐싱 (~/.clouvel/version_cache.json)
- [x] 첫 도구 호출 시 체크 (어떤 도구든)
- [x] 업데이트 있으면 배너 1회 표시

### 파일 변경

- [x] `src/clouvel/tools/start.py` - 타입 감지 + PRD 가이드
- [x] `src/clouvel/tools/docs.py` - TEMPLATES 확장
- [x] `src/clouvel/version_check.py` - 신규
- [x] `src/clouvel/server.py` - save_prd 등록, 버전 체크 연동
- [x] `src/clouvel/templates/*` - 14개 신규 템플릿 파일

---

## 완료된 기능

### Free (clouvel)

- [x] can_code - 문서 강제
- [x] start - 프로젝트 온보딩 + 타입 감지 + PRD 가이드
- [x] save_prd - PRD 저장
- [x] get_progress - 진행 상황
- [x] get_goal - 목표 리마인드
- [x] 템플릿 8종 (web-app, api, cli, chrome-ext, discord-bot, landing-page, saas, generic)
- [x] 버전 체크 (PyPI 최신 버전 알림)

### Pro - $49 (Early Bird)

- [x] manager - 8명 C-Level 매니저 협업 피드백
- [x] ship - 원클릭 테스트→검증→증거 생성
- [x] activate_license - Lemon Squeezy 연동
- [x] recover_context - 컨텍스트 복구
- [x] 기타 Pro 도구들

### Team - $149 (Early Bird)

- [x] 팀 협업 도구 (invite, members, settings 등)
- [x] 팀 규칙 동기화
- [x] 프로젝트 컨텍스트 공유

---

## 이전 완료 (2026-01-21)

### v1.2.0 ~ v1.3.3

- [x] /start 도구 기본 구현
- [x] /manager 도구 (8명 매니저)
- [x] /ship 도구 (lint → test → build)
- [x] clouvel install 명령
- [x] 보안 hook (민감 파일 차단)

---

## 로드맵

> **📄 5개년 로드맵**: `docs/roadmap/` 폴더 참조

### Q1 2026 목표

| 항목   | 목표 | 현재   |
| ------ | ---- | ------ |
| 템플릿 | 10개 | 8개 ✅ |
| 가입자 | 200  | -      |
| MAU    | 50   | -      |

### 다음 단계

**v1.4 - 템플릿 완성 + MCP 확장**

- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] Windsurf/Continue.dev 가이드
- [ ] Cursor 디렉토리 제출

**v1.5 - 다른 LLM 지원 (조건부)**

- [ ] LangChain Tool 패키지
- 전환 조건: 유료 15건+ 또는 요청 5건+

---

## 가격 전략

| 단계         | Personal | Team     | 시점           |
| ------------ | -------- | -------- | -------------- |
| Early Bird   | **$49**  | **$149** | ~ Feb 15, 2026 |
| After Launch | $79      | $249     | Feb 16~        |

---

## ✅ 완료: i18n 랜딩페이지

> **완료 시점**: 2026-01-24

### 완료 항목

- [x] `docs/landing/i18n/en.json` - 영문 번역 전체
- [x] `docs/landing/i18n/ko.json` - 한글 번역 전체
- [x] `docs/landing/i18n.js` - 언어 전환 스크립트
- [x] `index.html` - `<html lang="en">` 변경
- [x] `index.html` - i18n.js 스크립트 추가
- [x] `index.html` - 언어 토글 버튼 추가 (nav)
- [x] `index.html` - nav 링크 data-i18n 속성 추가
- [x] Hero 섹션 data-i18n 추가
- [x] Works with 섹션 data-i18n 추가
- [x] PRD 설명 섹션 data-i18n 추가
- [x] Problem 섹션 data-i18n 추가
- [x] How it works 섹션 data-i18n 추가
- [x] Demo 섹션 data-i18n 추가
- [x] Features 섹션 data-i18n 추가
- [x] Getting Started 섹션 data-i18n 추가
- [x] Pricing 섹션 data-i18n 추가
- [x] FAQ 섹션 data-i18n 추가
- [x] Contact 섹션 data-i18n 추가
- [x] Footer data-i18n 추가
- [x] 모바일 메뉴 data-i18n 추가

### 테스트 방법

```
# 영문
file:///D:/Clouvel/docs/landing/index.html?lang=en

# 한글
file:///D:/Clouvel/docs/landing/index.html?lang=ko
```

### 컨텍스트

- **목표**: 국제 indie hackers 타겟 영문 랜딩
- **결정**: 별도 영문 페이지 대신 i18n 단일 페이지
- **Threads/X**: Build in Public, 팀 리드 타겟
- **로드맵**: 18개월 후 $120K ARR, 10K 사용자

---

## 다음 할 일

### ✅ Manager v2: Augmentation 모델 (2026-01-24)

**핵심 변경**: 답변형 → 질문형 전환

| Before | After |
|--------|-------|
| "OAuth 쓰세요" | "유저가 소셜 로그인 선호하나요?" |
| 매니저가 결정 | 개발자가 결정 (매니저는 관점 제시) |
| Action Items | Decisions for YOU |

**구현 내용:**
- 8명 매니저 각각 4개 카테고리 probing questions 추가
- 시스템 프롬프트에 "AUGMENTATION, NOT AUTOMATION" 철학 명시
- 출력 형식: "Decisions for YOU", "Key Questions to Answer" 섹션

**파일 변경:**
- `src/clouvel/tools/manager/prompts/personas.py` - probing_questions 추가
- `src/clouvel/tools/manager/prompts/templates.py` - 질문 중심 템플릿

### ✅ Knowledge Base 연동 강화 (2026-01-24)

**Manager가 과거 결정을 참조:**
- `_get_kb_context()` - 관련 과거 결정 조회
- 토픽 기반 검색 + 최근 결정 포함
- 매니저 프롬프트에 자동 주입

**파일 변경:**
- `src/clouvel/tools/manager/core.py` - `_get_kb_context()` 추가
- `src/clouvel/tools/manager/generator/conversation.py` - KB 컨텍스트 전달

### ✅ Quick Perspectives 도구 추가 (2026-01-24)

**코딩 전 빠른 관점 체크:**
- `quick_perspectives(context)` - 3-4명 매니저가 핵심 질문 제시
- 토픽 기반 자동 매니저 선택 (auth → CSO 포함, UI → CDO 포함)
- 매니저당 2개 probing questions
- KB에서 관련 과거 결정 참조

**출력 예시:**
```
## 💡 Quick Perspectives

_Before building: **Adding user authentication with JWT tokens**_

**👔 PM**:
  - Is this MVP scope or post-launch?
  - What's the ONE thing this feature must do?

**🔒 CSO**:
  - How do you verify the user is who they claim?
  - How do you verify they're allowed to do this action?

💡 _Related past decision: auth Use JWT with refresh token..._
```

**파일 변경:**
- `src/clouvel/tools/manager/core.py` - `quick_perspectives()` 함수 추가
- `src/clouvel/tools/manager/__init__.py` - export 추가
- `src/clouvel/server.py` - Tool 정의 및 핸들러 추가

---

### ✅ Knowledge Base 구현 완료 (8주 → 1일)

| 주차 | 목표 | 상태 |
|------|------|------|
| 1-2 | SQLite 기반 구축 | ✅ 완료 |
| 3-4 | 도구 통합 (record_decision, record_location) | ✅ 완료 |
| 5-6 | 자동화 (회의 후 자동 기록) | ✅ 완료 |
| 7-8 | FTS5 검색 + CLI | ✅ FTS5 완료, CLI 미정 |

**v1.4 Knowledge Base MVP 완료** (2026-01-24)
- `~/.clouvel/knowledge.db` SQLite 저장소
- 5개 테이블: projects, meetings, decisions, locations, events
- FTS5 전문 검색 지원 (category 포함)
- 6개 신규 도구: record_decision, record_location, search_knowledge, get_context, init_knowledge, rebuild_index
- **세션 시작 자동 컨텍스트 로딩**: can_code 호출 시 최근 결정/위치 표시
- **50MB 제한 + 자동 아카이브**: 40MB 초과 시 30일 이상 데이터 아카이브
- **API 키 fallback**: ANTHROPIC_API_KEY 없어도 manager 동작 (static mode)
- **회의 자동 기록**: manager 호출 시 결정사항 자동 추출 및 KB 저장
- **SQLite 암호화**: `CLOUVEL_KB_KEY` 환경변수로 선택적 Fernet 암호화

### 랜딩페이지 수정
- [x] "context preserved" → "Progress Tracking" + "Smart recovery coming soon" 변경 완료

---

- [x] **i18n 완료** ✅
- [x] **글로벌 런칭 Phase 1 완료** ✅
  - [x] hreflang 태그 추가 (SEO)
  - [x] Flash 방지 인라인 스크립트
  - [x] SUPPORTED_LANGS 유효성 검증
  - [x] localStorage 에러 핸들링
- [x] **GA4 언어별 전환율 추적 완료** ✅
  - [x] GA4 ID: G-17L1X6CZ4W
  - [x] trackCTA 함수 (CTA 클릭 추적)
  - [x] language_switch 이벤트 (언어 변경 추적)
- [x] **Solo-first 랜딩페이지 전환** ✅
  - [x] Hero 섹션: Solo devs & indie hackers 타겟팅
  - [x] Team 5/Team 10 플랜 숨김 → "Coming Soon"
  - [x] Personal Pro에 "추천" 배지 이동
  - [x] Enterprise 섹션 → "Need team features? Let us know"
  - [x] i18n 파일 업데이트 (en.json, ko.json)
  - [x] 영어 페이지(index-en.html) 동기화
- [x] **Week 1-2: GitHub 프로젝트 정비** ✅
  - [x] README.md 영문 재작성
  - [x] Demo GIF 생성 (docs/assets/demo.gif)
  - [x] CONTRIBUTING.md 확인 (영문 완료)
  - [x] CODE_OF_CONDUCT.md 확인 (영문 완료)
  - [x] Issue 템플릿 3개 확인 (bug, feature, question)
  - [x] PR 템플릿 확인
  - [x] GitHub Discussions 활성화
  - [x] 에러 메시지 영어 전환 (errors.py, planning.py)
  - [x] Reddit 포스트 초안 작성 (.claude/planning/reddit-posts.md)
- [ ] **Week 3: 커뮤니티 활동 시작**
  - [ ] r/ClaudeAI 포스팅
  - [ ] r/SideProject 포스팅
  - [ ] X/Threads 소개 쓰레드
- [ ] i18n 테스트 (`?lang=en` / `?lang=ko` / `?lang=jp` → fallback)
- [ ] Product Hunt 재런칭 준비 (Phase 3)
- [ ] Windows CI 추가 (GitHub Actions)
- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] Cursor 디렉토리 제출
