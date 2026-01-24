# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-24

---

## 지금 상태

| 항목              | 상태                          |
| ----------------- | ----------------------------- |
| **clouvel**       | v1.3.13 배포 완료             |
| **clouvel-pro**   | clouvel에 통합됨              |
| **랜딩 페이지**   | 배포 완료                     |
| **라이선스 서버** | ✅ 동작 중 (Polar.sh)         |
| **결제**          | ✅ Polar.sh 연동 완료         |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화 |

---

## 오늘 완료 (2026-01-24)

### v1.3.11 ~ v1.3.13 핫픽스

- [x] **v1.3.11**: manager 동적 회의록 생성 (Claude API 연동)
- [x] **v1.3.12**: Windows cp949 인코딩 수정 + 플랫폼별 Python 명령어
- [x] **v1.3.13**: manager import 조건부 처리 (Free 버전 호환)

### 문서 업데이트

- [x] README.md - v1.3.11~13 changelog 추가
- [x] README.md - Windows 완벽 지원 명시 + 플랫폼별 MCP 설정 예시

### 검증 완료

- [x] PyPI 배포 성공 (v1.3.13)
- [x] `pip install clouvel==1.3.13` 테스트 통과
- [x] MCP 재시작 후 도구 정상 작동 확인 (can_code, manager, license_status)

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

- [x] **i18n 완료** ✅
- [ ] i18n 테스트 (`?lang=en` / `?lang=ko`)
- [ ] Threads/X 포스트 올리기
- [ ] Windows CI 추가 (GitHub Actions)
- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] Cursor 디렉토리 제출
