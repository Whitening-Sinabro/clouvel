# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-21

---

## 지금 상태

| 항목              | 상태                               |
| ----------------- | ---------------------------------- |
| **clouvel**       | v1.2.0 개발 중 (신규 도구 추가)    |
| **clouvel-pro**   | ⚠️ Deprecated (clouvel에 통합됨)   |
| **랜딩 페이지**   | 배포 완료 + 결제 "문의하기"로 변경 |
| **라이선스 서버** | ✅ 동작 중                         |
| **결제**          | ⏳ 일시 중단 (문의 형태로 전환)    |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화      |

---

## 완료된 기능 (v1.4.2)

### Free (clouvel)

- [x] can_code - 문서 강제
- [x] get_progress - 진행 상황
- [x] get_goal - 목표 리마인드

### Pro (clouvel-pro) - $49 (Early Bird)

- [x] activate_license - Lemon Squeezy 연동
- [x] check_license - 라이선스 상태
- [x] install_shovel - 24개 슬래시 커맨드
- [x] sync_commands - 커맨드 동기화
- [x] log_error - 에러 기록
- [x] analyze_error - 에러 분석
- [x] get_error_summary - 에러 요약
- [x] add_prevention_rule - NEVER/ALWAYS 규칙
- [x] watch_logs - 로그 감시
- [x] check_logs - 로그 상태
- [x] recover_context - 컨텍스트 복구 (핵심!)

### Team (clouvel-pro) - $149 (Early Bird)

- [x] team_invite - 팀원 초대
- [x] team_members - 팀원 목록
- [x] team_remove - 팀원 제거
- [x] team_settings - C-Level 설정
- [x] team_toggle_role - 역할 토글
- [x] sync_team_errors - 에러 팀 동기화
- [x] get_team_rules - 팀 규칙 조회
- [x] apply_team_rules - 팀 규칙 적용
- [x] sync_project_context - 컨텍스트 업로드
- [x] get_project_context - 컨텍스트 조회

---

## 오늘 완료 (2026-01-21)

### v1.2.0 신규 도구 구현

#### /start (Free)
- [x] 프로젝트 온보딩 + PRD 강제
- [x] PRD 템플릿 자동 생성
- [x] PRD 검증 (필수 섹션 체크)
- [x] 다음 단계 안내

#### /manager (Pro) - 8명 C-Level 매니저
- [x] 컨텍스트 기반 매니저 자동 선택
- [x] 관련 매니저 그룹 출력 (예: 로그인 → CSO+CTO+QA+Error)
- [x] 매니저별 질문/체크리스트/경고
- [x] 8명 매니저 구현:
  - 👔 PM: PRD, 기능, 우선순위, 스코프
  - 🛠️ CTO: 아키텍처, 기술스택, 성능, 확장성
  - 🧪 QA: 테스트, 엣지케이스, 검증, 커버리지
  - 🎨 CDO: UI/UX, AI패턴방지, 접근성
  - 📢 CMO: GTM, 포지셔닝, 경쟁사, 메시징
  - 💰 CFO: 비용, 수익화, 가격, ROI
  - 🔒 CSO: 보안, 인증, 권한, 취약점
  - 🔥 Error: 에러패턴, 5 Whys, NEVER/ALWAYS

#### /ship (Pro)
- [x] 원클릭 테스트→검증→증거 생성
- [x] lint → typecheck → test → build 순차 실행
- [x] 프로젝트 타입 자동 감지 (python/node/bun)
- [x] 증거 파일 자동 생성 (.claude/evidence/)
- [x] quick_ship (lint+test만)
- [x] full_ship (전체+자동수정)

### 파일 생성
- [x] `src/clouvel/tools/start.py`
- [x] `src/clouvel/tools/manager.py`
- [x] `src/clouvel/tools/ship.py`
- [x] `src/clouvel/tools/__init__.py` 업데이트
- [x] `src/clouvel/server.py` 도구 등록

---

## 이전 완료 (2026-01-19)

### clouvel install 명령 추가

- [x] `clouvel install` CLI 명령 구현
  - 플랫폼 자동 감지 (Claude Code / Desktop)
  - `--platform` 옵션으로 대상 지정 (auto, code, desktop, all)
  - `--force` 옵션으로 재설치 지원
  - 글로벌 CLAUDE.md 규칙 자동 추가
  - 설치 검증 및 다음 단계 안내

### v1.1.0 릴리즈

- [x] **setup_cli 보안 hook 추가** (Free)
  - 민감 파일 커밋 자동 차단 (marketing, pricing, credentials 등)
  - PRD 체크 + 보안 체크 통합
- [x] **setup_security 도구** (Pro, 로컬만)
  - 커스텀 패턴 추가
  - 차단 로그 기록
  - 팀 동기화 옵션

### 보안 강화

- [x] 마케팅 문서 Git 히스토리에서 완전 삭제 (filter-branch)
- [x] .gitignore 강화 (마케팅/전략/가격/Pro코드 패턴)
- [x] CLAUDE.md에 보안 체크리스트 추가
- [x] pre-commit hook 자동 설치 (setup_cli)
- [x] GitHub 검증 완료 (민감 파일 없음)

### 배포

- [x] v1.1.0 PyPI 배포 완료
- [x] `pip install clouvel==1.1.0` 테스트 완료

---

## 이전 완료 (2026-01-18)

### clouvel (Free) v0.6.x

- [x] **B0: clouvel setup** - 원커맨드 설정 (글로벌 규칙 + MCP 자동 등록)
- [x] **3단계 품질 게이트** - BLOCK / WARN / PASS
- [x] can_code 자동 호출 메커니즘 (글로벌 CLAUDE.md 규칙)

### 패키지 통합

- [x] **clouvel + clouvel-pro 통합** → 단일 패키지 v1.0.0
  - Free 도구: 28개 (라이선스 불필요)
  - Pro 도구: 21개 (라이선스 필요)
  - 총 49개 도구

### 이전 작업

- [x] 랜딩 페이지 인터랙티브 모달 추가
- [x] 기술 문서 페이지 (docs.html) 생성
- [x] recover_context 도구 구현 (컨텍스트 압축 후 자동 복구)
- [x] setup_auto_recovery 도구 구현 (Hook 자동 설치)
- [x] Claude Code Hook 연동 (PreCompact + SessionStart)

---

## 개발 우선순위

```
1. ✅ 개인화 기능 (Pro 10개) - 완료
2. ✅ 팀 기능 (Team 10개) - 완료
3. ✅ 라이선스 서버 배포 - 완료
4. ✅ Lemon Squeezy 결제 연동 - 완료
5. ⏳ Lemon Squeezy Identity 인증 대기 중
6. ⏳ v1.5 Analytics Dashboard
```

---

## 로드맵

> **📄 5개년 로드맵**: `docs/roadmap/` 폴더 참조 (8개 파일로 분리)

### 비전 (2026-2030)

```
2026: "PRD 없으면 코딩 없다" (현재)
2030: "PRD가 곧 제품이다" (AI가 스펙만으로 구현)
```

### 단기 목표 (2026)

| 분기  | 목표                         | 핵심 지표       |
| ----- | ---------------------------- | --------------- |
| Q1-Q2 | Cursor 통합 + 무료 티어 강화 | 1,000 signups   |
| Q3    | 템플릿 라이브러리 v1 (50개)  | Discord 1,000명 |
| Q4    | Pro 티어 활성화              | $10K MRR        |

### 현재 단계 (v1.5)

| 항목               | 상태                         |
| ------------------ | ---------------------------- |
| 라이선스 서버      | ✅ 완료                      |
| Lemon Squeezy 연동 | ✅ 완료                      |
| 가격 확정          | ✅ $49 / $149 (until Feb 15) |
| Identity 인증      | ⏳ 심사 중                   |
| Cursor MCP 통합    | ⏳ 준비 중                   |

### 다음 단계

**v1.6 - 마케팅 + Cursor 통합**

- [ ] Cursor 디렉토리 제출
- [ ] Product Hunt 런칭
- [ ] 기본 템플릿 10개

**v1.7 - 템플릿 라이브러리**

- [ ] 구현 가이드라인 시스템
- [ ] 커뮤니티 기여 시스템
- [ ] 템플릿 50개

**v2.0 - Enterprise (2027)**

- [ ] SSO 통합
- [ ] 감사 로그
- [ ] 오픈소스 코어

---

## 가격 전략

| 단계         | Personal | Team     | 시점           |
| ------------ | -------- | -------- | -------------- |
| Early Bird   | **$49**  | **$149** | ~ Feb 15, 2026 |
| After Launch | $79      | $249     | Feb 16~        |

### 랜딩 페이지 문구 (확정)

```
Early Bird Pricing (until Feb 15)

Personal: $49 (After launch: $79)
Team: $149 (After launch: $249)

✅ Early Bird includes priority support (30 days)
```

### 주의사항

- "First 100" 안 씀 (카운터 없으면 구라로 보임)
- "40% OFF" 안 씀 (계산 불일치 리스크)
- 날짜 박아서 신뢰 확보

---

## 전략 문서

| 문서                 | 설명                                         |
| -------------------- | -------------------------------------------- |
| `docs/ROADMAP_5Y.md` | 5개년 로드맵 (2026-2030)                     |
| (내부) 차별화 전략   | AI Coding Agent 시장 분석 + Clouvel 포지셔닝 |
| (내부) 시장 분석     | 2026 AI 코딩 도구 생태계 전체 분석           |
| (내부) 전략적 기회   | Clouvel의 enforcement gap 기회 분석          |

### 핵심 전략 요약

```
시장 기회: "enforcement" 하는 스펙 도구 없음
차별점: 추천이 아닌 강제 (No PRD, No Code)
장기 Moat: 스펙 템플릿 라이브러리 + 커뮤니티
Exit 목표: 2028-2030, $100-200M M&A 또는 지속 성장
```

---

## BACKLOG

→ `docs/BACKLOG.md` 참조

- api.clouvel.dev 커스텀 도메인 (유저 늘면)
- 문서 자동 생성 스크립트
- ~~**MCP 설치 간소화** (높음) - `clouvel install` 명령 추가~~ ✅ 완료

---

## 다음 할 일

- [x] v1.1.0 릴리즈 ✅ 보안 hook 추가
- [x] 민감 파일 보호 자동화 ✅ pre-commit hook
- [x] `clouvel install` 명령 추가 ✅ MCP 설치 간소화
- [ ] 결제 시스템 재오픈 준비
- [x] 랜딩페이지 v1.2.0 변경사항 반영 ✅ clouvel install
- [ ] Pro setup_security 서버 등록 (라이선스 체크 후)
