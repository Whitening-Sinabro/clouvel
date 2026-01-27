# MCP Tool Catalog

> 마지막 업데이트: 2026-01-26
> 총 MCP 수: 52개
> Evidence: `server.py:79-753` (TOOL_DEFINITIONS), `server.py:765-852` (TOOL_HANDLERS)

---

## Summary

| Category | Count | Pro Required |
|----------|-------|--------------|
| Core (문서 체크) | 4 | No |
| Docs (PRD/템플릿) | 7 | No |
| Setup (환경 설정) | 2 | No |
| Rules (규칙 관리) | 3 | No |
| Verify (검증) | 3 | No |
| Planning (컨텍스트) | 5 | No |
| Agent (탐색) | 2 | No |
| Hook (자동화) | 2 | No |
| Start (온보딩) | 2 | No |
| Knowledge (KB) | 8 | Yes (Free stub) |
| Tracking (파일) | 2 | No |
| Manager (피드백) | 3 | Yes (API) |
| Ship (배포) | 3 | Yes (API) |
| Error (학습) | 3 | Yes |
| License (라이선스) | 3 | No |
| Architecture (가드) | 3 | No |

---

## (A) Core Tools (4개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `can_code` | `server.py:82-92`, `tools/core.py:137-250` | 코딩 전 문서 체크 (필수) | MCP Tool | `path`, `mode` | PASS/BLOCK/WARN | File read (docs/), DB read (KB) | None | Local, Sync | **Gate keeper** |
| `scan_docs` | `server.py:93-101`, `tools/core.py:253-280` | docs 폴더 스캔 | MCP Tool | `path` | File list | File read | None | Local, Sync | |
| `analyze_docs` | `server.py:102-110`, `tools/core.py:283-350` | 문서 분석 | MCP Tool | `path` | Analysis result | File read | None | Local, Sync | |
| `init_docs` | `server.py:111-122`, `tools/core.py:353-420` | docs 폴더 초기화 | MCP Tool | `path`, `project_name` | Created files | File write (docs/) | None | Local, Sync | |

---

## (B) Docs Tools (7개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `get_prd_template` | `server.py:125-138`, `tools/docs.py` | PRD 템플릿 생성 | MCP Tool | `project_name`, `output_path`, `template`, `layout` | Template content | File write | None | Local, Sync | |
| `list_templates` | `server.py:139-143`, `tools/docs.py` | 템플릿 목록 | MCP Tool | None | Template list | None | None | Local, Sync | Pure |
| `write_prd_section` | `server.py:144-155`, `tools/docs.py` | PRD 섹션 가이드 | MCP Tool | `section`, `content` | Guide text | None | None | Local, Sync | Pure |
| `get_prd_guide` | `server.py:156`, `tools/docs.py` | PRD 작성 가이드 | MCP Tool | None | Guide text | None | None | Local, Sync | Pure |
| `get_verify_checklist` | `server.py:157`, `tools/docs.py` | 검증 체크리스트 | MCP Tool | None | Checklist | None | None | Local, Sync | Pure |
| `get_setup_guide` | `server.py:158-165`, `tools/docs.py` | 설치 가이드 | MCP Tool | `platform` | Guide text | None | None | Local, Sync | Pure |
| `get_analytics` | `server.py:166-176`, `analytics.py` | 도구 사용 통계 | MCP Tool | `path`, `days` | Stats | File read (~/.clouvel/) | None | Local, Sync | |

---

## (C) Setup Tools (2개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `init_clouvel` | `server.py:179-186`, `tools/setup.py` | Clouvel 온보딩 | MCP Tool | `platform` | Setup guide | None | None | Local, Sync | |
| `setup_cli` | `server.py:187-198`, `tools/setup.py` | CLI 환경 설정 | MCP Tool | `path`, `level` | Config files | File write (.git/hooks, CLAUDE.md) | None | Local, Sync | Pre-commit hook |

---

## (D) Rules Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `init_rules` | `server.py:201-212`, `tools/rules.py` | 규칙 초기화 | MCP Tool | `path`, `template` | Created files | File write (.claude/rules/) | None | Local, Sync | |
| `get_rule` | `server.py:213-224`, `tools/rules.py` | 규칙 로드 | MCP Tool | `path`, `context` | Rules | File read | None | Local, Sync | |
| `add_rule` | `server.py:225-238`, `tools/rules.py` | 규칙 추가 | MCP Tool | `path`, `rule_type`, `content`, `category` | Updated rules | File write | None | Local, Sync | |

---

## (E) Verify Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `verify` | `server.py:241-253`, `tools/verify.py:9-67` | Context Bias 검증 | MCP Tool | `path`, `scope`, `checklist` | Checklist | None | None | Local, Sync | Pure |
| `gate` | `server.py:254-266`, `tools/verify.py:70-135` | lint→test→build 자동화 | MCP Tool | `path`, `steps`, `fix` | EVIDENCE.md | File write (EVIDENCE.md) | None | Local, Sync | |
| `handoff` | `server.py:267-281`, `tools/verify.py:138-200` | 의도 기록 | MCP Tool | `path`, `feature`, `decisions`, `warnings`, `next_steps` | Handoff file | File write (.claude/handoffs/) | None | Local, Sync | |

---

## (F) Planning Tools (5개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `init_planning` | `server.py:284-296`, `tools/planning.py:9-132` | 컨텍스트 초기화 | MCP Tool | `path`, `task`, `goals` | Created files | File write (.claude/planning/) | None | Local, Sync | |
| `plan` | `server.py:297-310`, `tools/planning.py` | 실행 계획 생성 | MCP Tool | `path`, `task`, `goals`, `meeting_file` | Plan document | File read/write | None | Local, Sync | v1.3 |
| `save_finding` | `server.py:311-326`, `tools/planning.py:135-190` | 조사 결과 저장 | MCP Tool | `path`, `topic`, `question`, `findings`, `source`, `conclusion` | Updated findings | File write | None | Local, Sync | |
| `refresh_goals` | `server.py:327-335`, `tools/planning.py` | 목표 리마인드 | MCP Tool | `path` | Goals | File read | None | Local, Sync | |
| `update_progress` | `server.py:336-350`, `tools/planning.py` | 진행 상태 업데이트 | MCP Tool | `path`, `completed`, `in_progress`, `blockers`, `next` | Updated progress | File write | None | Local, Sync | |

---

## (G) Agent Tools (2개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `spawn_explore` | `server.py:353-366`, `tools/agents.py` | 탐색 에이전트 | MCP Tool | `path`, `query`, `scope`, `save_findings` | Exploration result | File read/write (optional) | None | Local, Sync | |
| `spawn_librarian` | `server.py:367-380`, `tools/agents.py` | 라이브러리 조사 에이전트 | MCP Tool | `path`, `topic`, `type`, `depth` | Research result | File read/write | None | Local, Sync | |

---

## (H) Hook Tools (2개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `hook_design` | `server.py:383-396`, `tools/hooks.py` | 설계 훅 생성 | MCP Tool | `path`, `trigger`, `checks`, `block_on_fail` | Hook config | File write (.claude/hooks/) | None | Local, Sync | |
| `hook_verify` | `server.py:397-411`, `tools/hooks.py` | 검증 훅 생성 | MCP Tool | `path`, `trigger`, `steps`, `parallel`, `continue_on_error` | Hook config | File write | None | Local, Sync | |

---

## (I) Start Tools (2개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `start` | `server.py:414-426`, `tools/start.py` | 프로젝트 온보딩 | MCP Tool | `path`, `project_name`, `project_type` | PRD guide | File read (project scan) | None | Local, Sync | **Primary onboarding** |
| `save_prd` | `server.py:427-440`, `tools/start.py` | PRD 저장 | MCP Tool | `path`, `content`, `project_name`, `project_type` | Saved PRD | File write (docs/PRD.md) | None | Local, Sync | |

---

## (J) Knowledge Base Tools (8개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `record_decision` | `server.py:443-458`, `tools/knowledge.py:35-95` | 결정 기록 | MCP Tool | `category`, `decision`, `reasoning`, `alternatives`, `project_name`, `project_path`, `locked` | Decision ID | DB write (knowledge.db) | SQLite | Local, Sync | Pro |
| `record_location` | `server.py:460-474`, `tools/knowledge.py:98-150` | 코드 위치 기록 | MCP Tool | `name`, `repo`, `path`, `description`, `project_name`, `project_path` | Location ID | DB write | SQLite | Local, Sync | Pro |
| `search_knowledge` | `server.py:476-487`, `tools/knowledge.py` | KB 검색 | MCP Tool | `query`, `project_name`, `limit` | Search results | DB read | SQLite, FTS5 | Local, Sync | Pro |
| `get_context` | `server.py:489-502`, `tools/knowledge.py` | 최근 컨텍스트 조회 | MCP Tool | `project_name`, `project_path`, `include_decisions`, `include_locations`, `limit` | Context | DB read | SQLite | Local, Sync | Pro |
| `init_knowledge` | `server.py:503-510`, `tools/knowledge.py` | KB 초기화 | MCP Tool | None | Status | DB create (~/.clouvel/knowledge.db) | SQLite | Local, Sync | Pro |
| `rebuild_index` | `server.py:511-518`, `tools/knowledge.py` | 검색 인덱스 재구축 | MCP Tool | None | Status | DB write | SQLite, FTS5 | Local, Sync | Pro |
| `unlock_decision` | `server.py:519-530`, `tools/knowledge.py` | 결정 잠금 해제 | MCP Tool | `decision_id`, `reason` | Status | DB write | SQLite | Local, Sync | Pro |
| `list_locked_decisions` | `server.py:531-541`, `tools/knowledge.py` | 잠긴 결정 목록 | MCP Tool | `project_name`, `project_path` | Decision list | DB read | SQLite | Local, Sync | Pro |

---

## (K) Tracking Tools (2개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `record_file` | `server.py:544-557`, `tools/tracking.py:13-124` | 파일 생성 기록 | MCP Tool | `path`, `file_path`, `purpose`, `deletable`, `session` | Status | File write (.claude/files/created.md) | None | Local, Sync | |
| `list_files` | `server.py:559-568`, `tools/tracking.py:127-152` | 기록된 파일 목록 | MCP Tool | `path` | File list | File read | None | Local, Sync | |

---

## (L) Manager Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `manager` | `server.py:572-587`, `server.py:1193-1231` | C-Level 매니저 피드백 | MCP Tool | `context`, `mode`, `managers`, `include_checklist`, `use_dynamic`, `topic` | Meeting result | Network (Worker API) | API Key (optional) | **Worker**, Async | Pro, Trial 3회 |
| `list_managers` | `server.py:588-592`, `server.py:1234-1245` | 매니저 목록 | MCP Tool | None | Manager list | None | None | Local, Sync | |
| `quick_perspectives` | `server.py:593-605`, `server.py:1275-1305` | 빠른 관점 체크 | MCP Tool | `context`, `max_managers`, `questions_per_manager` | Questions | Network (Worker API) | None | **Worker**, Async | Free |

---

## (M) Ship Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `ship` | `server.py:608-622`, `tools/ship.py:50-131` | 테스트→검증→증거 자동화 | MCP Tool | `path`, `feature`, `steps`, `generate_evidence`, `auto_fix` | Ship result | Network (API check), Process (lint/test) | API (trial check) | **API+Local**, Sync | Pro, Trial 5회 |
| `quick_ship` | `server.py:623-634`, `tools/ship.py:134-137` | 빠른 ship (lint+test) | MCP Tool | `path`, `feature` | Ship result | Same as ship | Same | API+Local, Sync | Alias |
| `full_ship` | `server.py:635-646`, `tools/ship.py:139-142` | 전체 ship (all+fix) | MCP Tool | `path`, `feature` | Ship result | Same as ship | Same | API+Local, Sync | Alias |

---

## (N) Error Learning Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `error_record` | `server.py:649-665`, `tools/errors.py` | 5 Whys 에러 기록 | MCP Tool | `path`, `error_text`, `context`, `five_whys`, `root_cause`, `solution`, `prevention` | Error record | File write (.claude/errors/) | None | Local, Sync | Pro |
| `error_check` | `server.py:666-679`, `tools/errors.py` | 에러 패턴 체크 | MCP Tool | `path`, `context`, `file_path`, `operation` | Warnings | File read | None | Local, Sync | Pro |
| `error_learn` | `server.py:680-692`, `tools/errors.py` | CLAUDE.md 자동 업데이트 | MCP Tool | `path`, `auto_update_claude_md`, `min_count` | Learned rules | File read/write (CLAUDE.md) | None | Local, Sync | Pro |

---

## (O) License Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `activate_license` | `server.py:695-705`, `server.py:1436-1475` | 라이선스 활성화 | MCP Tool | `license_key` | Activation result | Network (Lemon Squeezy/Worker), File write (~/.clouvel/) | requests | Network, Sync | |
| `license_status` | `server.py:706-710`, `server.py:1478-1505` | 라이선스 상태 | MCP Tool | None | Status | File read | None | Local, Sync | |
| `upgrade_pro` | `server.py:713-717`, `server.py:1508-1550` | Pro 업그레이드 가이드 | MCP Tool | None | Guide | None | None | Local, Sync | Pure |

---

## (P) Architecture Guard Tools (3개)

| Name | Location | Purpose | Entry | Inputs | Outputs | Side Effects | Dependencies | Runtime | Notes |
|------|----------|---------|-------|--------|---------|--------------|--------------|---------|-------|
| `arch_check` | `server.py:720-732`, `tools/architecture.py` | 코드 추가 전 중복 체크 | MCP Tool | `name`, `purpose`, `path` | Check result | Process (grep) | None | Local, Sync | |
| `check_imports` | `server.py:733-742`, `tools/architecture.py` | import 패턴 검증 | MCP Tool | `path` | Violations | Process (grep) | None | Local, Sync | |
| `check_duplicates` | `server.py:743-752`, `tools/architecture.py` | 중복 정의 탐지 | MCP Tool | `path` | Duplicates | Process (grep) | None | Local, Sync | |

---

## Side Effects Legend

| Symbol | Meaning |
|--------|---------|
| File read | 파일 읽기 (로컬 FS) |
| File write | 파일 쓰기 (로컬 FS) |
| DB read/write | SQLite 접근 |
| Network | HTTP 요청 (Worker API, Lemon Squeezy) |
| Process | subprocess 실행 (grep, lint, test) |
| None | 순수 함수 (부작용 없음) |

## Runtime Legend

| Context | Description |
|---------|-------------|
| Local, Sync | 로컬에서 동기 실행 |
| Worker, Async | Worker API로 비동기 실행 |
| API+Local | API 권한 체크 후 로컬 실행 |
