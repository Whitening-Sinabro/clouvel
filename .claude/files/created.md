# Created Files (Clouvel)

> 삭제하면 안 되는 핵심 파일만 기록

---

## 프로젝트 설정

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `src/clouvel/tools/architecture.py` | 아키텍처 가드 도구 (arch_check, check_imports, check_duplicates) | ❌ |
| `src/clouvel/trial.py` | Pro 기능 Trial 시스템 - 횟수 제한 방식 | ❌ |
| `pyproject.toml` | Python 패키지 설정 | ❌ |
| `setup.py` | 설치 스크립트 | ❌ |
| `CLAUDE.md` | Claude 규칙 | ❌ |

## 문서

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `docs/PRD.md` | 제품 요구사항 | ❌ |
| `docs/landing/index.html` | 랜딩 페이지 | ❌ |
| `docs/landing/i18n/*.json` | 다국어 번역 | ❌ |
| `README.md` | 프로젝트 소개 | ❌ |
| `CHANGELOG.md` | 변경 이력 | ❌ |

## 아키텍처 문서

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `docs/architecture/flow_manager.md` | Manager 코드 플로우 (엔트리포인트, 호출그래프, 시퀀스) | ❌ |
| `docs/architecture/data_contracts.md` | Manager API 요청/응답 스키마, 인증 흐름 | ❌ |
| `docs/architecture/decision_log_manager.md` | Manager 아키텍처 결정 로그 (옵션 비교) | ❌ |

## 핵심 소스 코드

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `src/clouvel/server.py` | MCP 서버 메인 | ❌ |
| `src/clouvel/tools/core.py` | can_code 등 핵심 도구 | ❌ |
| `src/clouvel/tools/docs.py` | 문서 도구 | ❌ |
| `src/clouvel/tools/start.py` | 프로젝트 온보딩 | ❌ |
| `src/clouvel/tools/planning.py` | 계획 도구 | ❌ |
| `src/clouvel/tools/ship.py` | 검증 도구 (Pro) | ❌ |
| `src/clouvel/tools/knowledge.py` | Knowledge Base 도구 | ❌ |
| `src/clouvel/tools/tracking.py` | 파일 추적 도구 (v1.5) | ❌ |
| `src/clouvel/tools/setup.py` | CLI 설정 도구 | ❌ |

## Manager 모듈

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `src/clouvel/tools/manager/core.py` | Manager 핵심 로직 | ❌ |
| `src/clouvel/tools/manager/utils.py` | 유틸리티 (토픽 감지 등) | ❌ |
| `src/clouvel/tools/manager/formatter.py` | 출력 포맷터 | ❌ |
| `src/clouvel/tools/manager/data/` | 매니저 데이터 | ❌ |

## DB 모듈

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `src/clouvel/db/knowledge.py` | Knowledge Base SQLite | ❌ |
| `src/clouvel/db/errors.py` | 에러 DB | ❌ |

## .claude 추적

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `.claude/status/current.md` | 현재 작업 상태 | ❌ |
| `.claude/files/created.md` | 생성 파일 목록 (이 파일) | ❌ |
| `.claude/planning/*.md` | 계획/회의 기록 | ❌ |

---

## 생성 기록

| 날짜 | 세션 | 생성/수정 파일 |
|------|------|----------------|
| 2026-01-26 | auto | `src/clouvel/tools/architecture.py` |
| 2026-01-25 | auto | `src/clouvel/trial.py` |
| 2026-01-25 | v1.5 PRD 추가 | `docs/PRD.md` (v1.5 섹션 추가) |
| 2026-01-25 | files 기록 시작 | `.claude/files/created.md` (신규) |
| 2026-01-25 | Phase 1: can_code 강화 | `src/clouvel/tools/core.py` (DoD 패턴 추가) |
| 2026-01-25 | Phase 1: can_code 강화 | `src/clouvel/messages/en.py` (테스트 메시지 개선) |
| 2026-01-25 | Phase 1: 테스트 수정 | `tests/test_tools.py` (import 오류 수정) |
| 2026-01-25 | Phase 2: hook 강화 | `src/clouvel/server.py` (--hooks 옵션 추가) |
| 2026-01-25 | Phase 2: hook 강화 | `src/clouvel/tools/setup.py` (기록 파일 체크 추가) |
| 2026-01-25 | Phase 3: 토픽 확장 | `src/clouvel/tools/manager/utils.py` (mcp, internal, tracking 토픽) |
| 2026-01-25 | Phase 3: 토픽 확장 | `src/clouvel/tools/manager/data/__init__.py` (CONTEXT_GROUPS 확장) |
| 2026-01-25 | Phase 4: context 분석 | `src/clouvel/tools/manager/utils.py` (패턴 감지 추가) |
| 2026-01-25 | Phase 4: LLM 최적화 | `src/clouvel/tools/manager/formatter.py` (XML + bookending) |
| 2026-01-25 | Phase 5: record_file | `src/clouvel/tools/tracking.py` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/flow_manager.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/data_contracts.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/decision_log_manager.md` (신규) |
