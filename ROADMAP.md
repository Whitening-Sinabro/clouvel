# Clouvel 로드맵

## 현재 버전
- MCP 서버: PyPI v0.3.2
- VS Code 확장: v0.10.2
- Cursor 확장: v0.10.2

---

## 완료된 기능

### MCP 서버
- [x] docs 폴더 스캔
- [x] 필수 문서 분석 (PRD, 아키텍처, API, DB, 검증)
- [x] PRD 작성 가이드
- [x] 검증 체크리스트
- [x] **코딩 차단 기능** (can_code) - 문서 없으면 코딩 금지
- [x] **PRD 상세 템플릿** (get_prd_template) - 11개 섹션
- [x] **섹션별 PRD 작성** (write_prd_section)
- [x] **docs 폴더 초기화** (init_docs) - 템플릿 자동 생성
- [x] **설정 가이드** (get_setup_guide) - Claude Desktop/Code/VS Code 설정법

### VS Code/Cursor 확장
- [x] MCP 서버 원클릭 설정
- [x] Claude Desktop 지원
- [x] Claude Code 지원 (.mcp.json)
- [x] 문서 상태 표시 (상태바 + 사이드바)
- [x] uvx 자동 설치
- [x] clouvel 자동 설치 (fallback)
- [x] Python 미설치 시 안내

### CLI
- [x] setup.sh (macOS/Linux/WSL)
- [x] setup.bat (Windows)

---

## 버전별 로드맵

### v0.1.0 ✅ (현재)
**MVP - 9개 도구**
- [x] can_code - 코딩 시작 가능 여부 확인
- [x] scan_docs - 프로젝트 문서 스캔
- [x] init_docs - 문서 구조 초기화
- [x] get_prd_template - PRD 상세 템플릿
- [x] write_prd_section - 섹션별 PRD 작성
- [x] get_setup_guide - 설정 가이드

### v0.2.0
**문서 상태 추적**
- [ ] Freshness 체크 (문서 최신성 검증)
- [ ] PROGRESS.md 자동화

### v0.3.0
**문서-코드 동기화**
- [ ] Git 커밋 후 문서 미수정 감지
- [ ] 코드 변경과 문서 불일치 알림

### v0.4.0
**컨텍스트 유지**
- [ ] 세션 요약 저장/복원
- [ ] Handoff 문서 자동 생성

### v0.5.0
**에러 학습**
- [ ] 에러 패턴 기록
- [ ] 유사 에러 검색 및 해결책 제안

### v1.0.0
**안정화 + 확장**
- [ ] 웹 대시보드
- [ ] Boris 검증 통합
- [ ] API 안정화

### v2.0.0 (미정)
**통합**
- [ ] shovel-setup 통합

---

## 기술 부채

### 확장
- [ ] ESLint 설정 추가
- [ ] 유닛 테스트 추가
- [ ] CI/CD (GitHub Actions)

### MCP 서버
- [ ] 테스트 코드 작성
- [ ] 로깅 개선
- [ ] 에러 핸들링 강화

---

## 아이디어 (검토 필요)

1. **AI 문서 생성**: Claude가 코드 보고 PRD 초안 작성
2. **문서 품질 점수**: 내용 기반 품질 평가 (0~100)
3. **변경 추적**: 문서 버전 히스토리
4. **협업 기능**: 실시간 문서 편집

---

## 버전 히스토리

### MCP 서버 (PyPI)

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 0.3.2 | 2026-01-16 | GitHub Actions 추가 (CI/CD 자동화) |
| 0.3.1 | 2026-01-16 | wheel 패키징 버그 수정 (모듈 누락 문제) |
| 0.3.0 | 2026-01-15 | init_docs, get_setup_guide 추가 |
| 0.2.0 | 2026-01-15 | can_code (코딩 차단), get_prd_template, write_prd_section 추가 |
| 0.1.0 | 2026-01-15 | 초기 릴리스 |

### VS Code/Cursor 확장

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 0.10.2 | 2026-01-16 | 마켓플레이스 아이콘 추가 |
| 0.10.0 | 2026-01-15 | Diagnostic으로 변경 (빨간 밑줄 + Problems 탭) |
| 0.9.0 | 2026-01-15 | "--1-- 시작하기.md" 안내 파일 추가 |
| 0.8.0 | 2026-01-15 | 프로젝트 유형별 PRD 템플릿 (수익화/개인/사내) |
| 0.7.0 | 2026-01-15 | 코드 파일 상단 경고 배너 (CodeLens) |
| 0.6.0 | 2026-01-15 | init_docs 명령 추가, docs 없으면 자동 안내 |
| 0.5.0 | 2026-01-15 | MCP 서버 0.3.0 동기화 |
| 0.4.0 | 2026-01-15 | Python 미설치 안내 추가 |
| 0.3.0 | 2026-01-15 | uvx/clouvel 자동 설치 |
| 0.2.0 | 2026-01-15 | Claude Code 지원 (.mcp.json) |
| 0.1.0 | 2026-01-15 | 초기 릴리스 |
