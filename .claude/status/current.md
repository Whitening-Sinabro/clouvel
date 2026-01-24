# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-24

---

## 지금 상태

| 항목              | 상태                          |
| ----------------- | ----------------------------- |
| **clouvel**       | v1.4.0 배포 준비 (Knowledge Base) |
| **clouvel-pro**   | clouvel에 통합됨              |
| **랜딩 페이지**   | 배포 완료                     |
| **라이선스 서버** | ✅ 동작 중 (Polar.sh + Worker API) |
| **결제**          | ✅ Polar.sh 연동 완료         |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화 |

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
