# Created Files (Clouvel)

> 삭제하면 안 되는 핵심 파일만 기록

---

## 프로젝트 설정

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `src/clouvel/gate_check.py` | Lightweight PreToolUse hook gate checker — reads .clouvel/gate.json, exits 0/1. No clouvel imports for speed. | ❌ |
| `tests/test_prd_scoring.py` | PRD quality scoring engine tests (58 tests) | ❌ |
| `tests/test_checkpoint.py` | context_save/context_load tests (36 tests) | ❌ |
| `src/clouvel/tools/prd_scoring.py` | DEAD framework PRD quality scoring engine | ❌ |
| `src/clouvel/tools/checkpoint.py` | context_save/context_load — pre-emptive context checkpoint before compression | ❌ |
| `src/clouvel/templates/landing-page/detailed.md` | Pro Landing Page PRD template with conversion funnel, A/B testing, performance | ❌ |
| `src/clouvel/templates/discord-bot/detailed.md` | Pro Discord Bot PRD template with command spec, permissions, error handling | ❌ |
| `src/clouvel/templates/chrome-ext/detailed.md` | Pro Chrome Extension PRD template with Input/Output spec, error cases, security | ❌ |
| `src/clouvel/templates/cli/detailed.md` | Pro CLI PRD 템플릿 - 명령어별 I/O Spec, 인터랙티브 플로우, Shell Completion, Man Page | ❌ |
| `src/clouvel/templates/api/detailed.md` | Pro API PRD 템플릿 - 엔드포인트별 I/O Spec, 에러케이스, 테스트 시나리오, OpenAPI 예시 | ❌ |
| `src/clouvel/templates/guides/documentation-guide.md` | Pro 문서 가이드라인 - AI를 위한 13종 문서 작성법 (PRD, CLAUDE.md, ADR 등) | ❌ |
| `src/clouvel/templates/saas/detailed.md` | Pro SaaS PRD 템플릿 - 정량적 AC, 에러케이스, State Machine, SaaS 메트릭 포함 | ❌ |
| `infra/api/worker.js` | Clouvel API Worker code - version check, FREE/PRO tier logic | ❌ |
| `infra/api/wrangler.toml` | Clouvel API Worker configuration (v3.0) | ❌ |
| `docs/roadmap-meeting.md` | Meeting 시스템 로드맵 - Phase 1-4 계획 | ⚠️ |
| `src/clouvel/tools/meeting_personalization.py` | Project personalization - 매니저 비중, 페르소나 커스터마이징 | ❌ |
| `src/clouvel/tools/meeting_kb.py` | Enhanced KB integration - 풍부한 컨텍스트, 프로젝트 패턴 분석 | ❌ |
| `src/clouvel/tools/meeting_tuning.py` | A/B testing system - 프롬프트 버전 관리, 성능 비교 | ❌ |
| `src/clouvel/tools/meeting_feedback.py` | Meeting feedback system - 평가 수집, 통계, training data 추출 | ❌ |
| `src/clouvel/tools/meeting_prompt.py` | Meeting prompt builder - PERSONAS + EXAMPLES 조합 | ❌ |
| `src/clouvel/tools/meeting.py` | MCP meeting tool - C-Level 회의 시뮬레이션 | ❌ |
| `docs/landing/assets/manager_feedback.png` | 랜딩페이지 Manager 리뷰 스크린샷 | ❌ |
| `docs/landing/assets/can_code_pass.png` | 랜딩페이지 PASS 스크린샷 | ❌ |
| `docs/landing/assets/can_code_block.png` | 랜딩페이지 BLOCK 스크린샷 | ❌ |
| `tests/test_ship.py` | Ship 도구 테스트 (23개 테스트) | ❌ |
| `tests/test_knowledge.py` | Knowledge Base 도구 테스트 (35개 테스트) | ❌ |
| `.env.example` | 환경 변수 템플릿 (신규 개발자 온보딩용) | ❌ |
| `docs/mcp/MCP_STANDARDIZATION_PLAN.md` | MCP 도구 표준화 계획 - 그룹별 표준/Deprecate/Merge/Keep 결정 | ❌ |
| `docs/architecture/SMOKE_LOGS.md` | 실행 검증 기록 템플릿 (문서-코드 일치 검증) | ❌ |
| `docs/architecture/SIDE_EFFECTS.md` | 외부 부작용 매트릭스 (네트워크, 파일, 환경변수, 프로세스) | ❌ |
| `docs/architecture/ENTRYPOINTS.md` | CLI, MCP, Packaging 진입점 문서 (Evidence 기반) | ❌ |
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
| `docs/architecture/CALL_FLOWS/flow_index.md` | 플로우 문서 인덱스 | ❌ |
| `docs/architecture/CALL_FLOWS/flow_manager.md` | Manager 코드 플로우 (Worker API, v1.8.0) | ❌ |
| `docs/architecture/CALL_FLOWS/flow_activate.md` | 라이선스 활성화 플로우 | ❌ |
| `docs/architecture/CALL_FLOWS/flow_webhook.md` | Worker API 통신 플로우 | ❌ |
| `docs/architecture/DATA_CONTRACTS.md` | API 데이터 계약 (AUTO-GEN 포함) | ❌ |
| `docs/architecture/MODULE_MAP.md` | 모듈 구조 (AUTO-GEN) | ❌ |
| `docs/architecture/RUNTIME_PATHS.md` | 런타임 조건 분기 (AUTO-GEN) | ❌ |
| `docs/architecture/DECISION_LOG/ADR-0001-manager-execution.md` | Manager 실행 아키텍처 결정 | ❌ |

## 문서 자동화 스크립트

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|
| `scripts/docs_extract.py` | 아키텍처 문서 자동 생성 | ❌ |
| `scripts/docs_check.py` | 문서 유효성 검증 | ❌ |

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
| 2026-02-21 | auto | `src/clouvel/gate_check.py` |
| 2026-02-09 | auto | `tests/test_prd_scoring.py` |
| 2026-02-09 | auto | `tests/test_checkpoint.py` |
| 2026-02-09 | auto | `src/clouvel/tools/prd_scoring.py` |
| 2026-02-09 | auto | `src/clouvel/tools/checkpoint.py` |
| 2026-02-01 | auto | `src/clouvel/templates/landing-page/detailed.md` |
| 2026-02-01 | auto | `src/clouvel/templates/discord-bot/detailed.md` |
| 2026-02-01 | auto | `src/clouvel/templates/chrome-ext/detailed.md` |
| 2026-02-01 | auto | `src/clouvel/templates/cli/detailed.md` |
| 2026-02-01 | auto | `src/clouvel/templates/api/detailed.md` |
| 2026-02-01 | auto | `src/clouvel/templates/guides/documentation-guide.md` |
| 2026-02-01 | auto | `src/clouvel/templates/saas/detailed.md` |
| 2026-01-30 | auto | `infra/api/worker.js` |
| 2026-01-30 | auto | `infra/api/wrangler.toml` |
| 2026-01-28 | auto | `docs/roadmap-meeting.md` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting_personalization.py` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting_kb.py` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting_tuning.py` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting_feedback.py` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting_prompt.py` |
| 2026-01-28 | auto | `src/clouvel/tools/meeting.py` |
| 2026-01-27 | auto | `docs/landing/assets/manager_feedback.png` |
| 2026-01-27 | auto | `docs/landing/assets/can_code_pass.png` |
| 2026-01-27 | auto | `docs/landing/assets/can_code_block.png` |
| 2026-01-27 | auto | `tests/test_ship.py` |
| 2026-01-27 | auto | `tests/test_knowledge.py` |
| 2026-01-27 | auto | `.env.example` |
| 2026-01-26 | auto | `docs/mcp/MCP_STANDARDIZATION_PLAN.md` |
| 2026-01-26 | SSOT-docs-system | `docs/architecture/SMOKE_LOGS.md` |
| 2026-01-26 | SSOT-docs-system | `docs/architecture/SIDE_EFFECTS.md` |
| 2026-01-26 | SSOT-docs-system | `docs/architecture/ENTRYPOINTS.md` |
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
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/CALL_FLOWS/flow_manager.md` (v1.8.0 업데이트) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/CALL_FLOWS/flow_index.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/CALL_FLOWS/flow_activate.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/CALL_FLOWS/flow_webhook.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/DATA_CONTRACTS.md` (AUTO-GEN 추가) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/MODULE_MAP.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/RUNTIME_PATHS.md` (신규) |
| 2026-01-26 | 아키텍처 문서화 | `docs/architecture/DECISION_LOG/ADR-0001-manager-execution.md` (이동) |
| 2026-01-26 | 문서 자동화 | `scripts/docs_extract.py` (신규) |
| 2026-01-26 | 문서 자동화 | `scripts/docs_check.py` (신규) |
