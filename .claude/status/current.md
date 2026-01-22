# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-22

---

## 지금 상태

| 항목              | 상태                          |
| ----------------- | ----------------------------- |
| **clouvel**       | v1.3.4 배포 완료              |
| **clouvel-pro**   | clouvel에 통합됨              |
| **랜딩 페이지**   | 배포 완료                     |
| **라이선스 서버** | ✅ 동작 중                    |
| **결제**          | ⏳ 문의 형태로 전환           |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화 |

---

## 오늘 완료 (2026-01-22)

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

## 다음 할 일

- [ ] v1.3.4 PyPI 배포
- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] 결제 시스템 재오픈 준비
- [ ] Cursor 디렉토리 제출
