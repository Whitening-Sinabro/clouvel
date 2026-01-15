# Clouvel 로드맵

## 현재 버전
- MCP 서버: PyPI v0.3.1
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

## 예정된 기능

### 우선순위 높음
- [ ] **Standalone 실행 파일**: PyInstaller로 clouvel.exe 빌드 → Python 불필요
- [ ] **FastAPI 서버 모드**: 웹 UI 제공 (localhost:8000)
- [x] ~~**문서 템플릿 생성**: PRD, 아키텍처 등 빈 템플릿 자동 생성~~ → init_docs로 완료

### 우선순위 중간
- [ ] **문서 내용 검증**: 파일명뿐 아니라 내용도 분석
- [ ] **다국어 지원**: 영어 UI 추가
- [ ] **커스텀 문서 규칙**: 사용자 정의 필수 문서 설정
- [ ] **GitHub Action**: PR 시 자동 문서 체크

### 우선순위 낮음
- [ ] **웹 버전**: 브라우저에서 docs 업로드 → 분석
- [ ] **팀 대시보드**: 여러 프로젝트 문서 현황 한눈에
- [ ] **Slack/Discord 알림**: 문서 누락 시 알림

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
