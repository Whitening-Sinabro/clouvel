# MCP Tool Groups (Similarity Analysis)

> 마지막 업데이트: 2026-01-26
> 유사 판정 기준: 5개 중 3개 이상 일치 시 같은 그룹

---

## Similarity Criteria

| # | Criterion | Description |
|---|-----------|-------------|
| 1 | Purpose | 해결하는 문제 |
| 2 | Interface | IO 스키마/엔드포인트/커맨드 |
| 3 | Side Effects | Network/FS/ENV/DB/Process/Time-Random |
| 4 | Runtime Context | Local vs Worker, CLI vs Server, Sync vs Async |
| 5 | Dependencies | API 키/스토리지/라이브러리 |

---

## Group 1: Documentation Check (문서 체크)

### Members

| Tool | Evidence |
|------|----------|
| `can_code` | `server.py:82-92` |
| `scan_docs` | `server.py:93-101` |
| `analyze_docs` | `server.py:102-110` |

### Similarity Analysis

| Criterion | can_code | scan_docs | analyze_docs | Match? |
|-----------|----------|-----------|--------------|--------|
| Purpose | 코딩 가능 여부 | 폴더 스캔 | 문서 분석 | **YES** (문서 상태 파악) |
| Interface | path → PASS/BLOCK | path → list | path → analysis | **YES** (path 기반) |
| Side Effects | File read | File read | File read | **YES** |
| Runtime | Local, Sync | Local, Sync | Local, Sync | **YES** |
| Dependencies | None | None | None | **YES** |

**Match: 5/5** - 완전 동일 그룹

### Commonalities

- 모두 docs 폴더의 상태를 파악하는 도구
- File read만 수행 (부작용 최소)
- `path` 입력만 받음

### Differences

| Tool | Unique Aspect |
|------|---------------|
| `can_code` | Gate keeper - PASS/BLOCK 반환, KB 연동 |
| `scan_docs` | 단순 파일 목록 |
| `analyze_docs` | 필수 문서 체크 |

### Standard Candidate

**`can_code`** - 이유:
1. Gate keeper 역할로 가장 중요
2. scan_docs + analyze_docs 기능을 포함
3. KB 연동으로 컨텍스트 제공
4. 이미 워크플로우의 핵심

---

## Group 2: PRD/Template (PRD 작성)

### Members

| Tool | Evidence |
|------|----------|
| `get_prd_template` | `server.py:125-138` |
| `write_prd_section` | `server.py:144-155` |
| `get_prd_guide` | `server.py:156` |
| `save_prd` | `server.py:427-440` |
| `init_docs` | `server.py:111-122` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - PRD/문서 생성 |
| Interface | **YES** - path + content/template |
| Side Effects | **PARTIAL** - File write (일부만) |
| Runtime | **YES** - Local, Sync |
| Dependencies | **YES** - None |

**Match: 4/5**

### Commonalities

- PRD 작성/템플릿 관련
- 로컬 실행, 동기

### Differences

| Tool | Output | Write? |
|------|--------|--------|
| `get_prd_template` | Template text | Optional |
| `write_prd_section` | Guide text | No |
| `get_prd_guide` | Guide text | No |
| `save_prd` | Saved file | **Yes** |
| `init_docs` | Created files | **Yes** |

### Standard Candidate

**`start` + `save_prd`** 조합 - 이유:
1. `start`가 프로젝트 온보딩의 표준
2. `save_prd`가 실제 저장 담당
3. 나머지는 `start` 내부에서 가이드로 활용

---

## Group 3: Context/Planning (컨텍스트 관리)

### Members

| Tool | Evidence |
|------|----------|
| `init_planning` | `server.py:284-296` |
| `save_finding` | `server.py:311-326` |
| `refresh_goals` | `server.py:327-335` |
| `update_progress` | `server.py:336-350` |
| `handoff` | `server.py:267-281` |
| `record_decision` | `server.py:443-458` |
| `record_location` | `server.py:460-474` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 작업 상태/결정 기록 |
| Interface | **YES** - path + data |
| Side Effects | **YES** - File/DB write |
| Runtime | **YES** - Local, Sync |
| Dependencies | **PARTIAL** - KB는 SQLite 필요 |

**Match: 4/5**

### Sub-groups

#### 3A: File-based Planning

| Tool | Storage |
|------|---------|
| `init_planning` | `.claude/planning/*.md` |
| `save_finding` | `.claude/planning/findings.md` |
| `refresh_goals` | `.claude/planning/task_plan.md` |
| `update_progress` | `.claude/planning/progress.md` |
| `handoff` | `.claude/handoffs/*.md` |

#### 3B: DB-based Knowledge

| Tool | Storage |
|------|---------|
| `record_decision` | `~/.clouvel/knowledge.db` |
| `record_location` | `~/.clouvel/knowledge.db` |

### Differences

| Sub-group | Scope | Persistence |
|-----------|-------|-------------|
| Planning (3A) | 프로젝트별 | 프로젝트 내 |
| Knowledge (3B) | 전역 | 전역 (~/.clouvel/) |

### Standard Candidate

**`record_decision`** for decisions, **`update_progress`** for progress - 이유:
1. record_decision은 KB에 영구 저장 (세션 간 유지)
2. update_progress는 현재 세션 진행 추적
3. 용도가 명확히 다름 (영구 vs 임시)

**통합 권장**: `handoff`를 `record_decision` + `update_progress`로 대체 가능

---

## Group 4: Verification (검증)

### Members

| Tool | Evidence |
|------|----------|
| `verify` | `server.py:241-253` |
| `gate` | `server.py:254-266` |
| `ship` | `server.py:608-622` |
| `quick_ship` | `server.py:623-634` |
| `full_ship` | `server.py:635-646` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 코드 품질 검증 |
| Interface | **YES** - path + steps |
| Side Effects | **YES** - Process (lint/test), File write |
| Runtime | **PARTIAL** - ship은 API 체크 |
| Dependencies | **PARTIAL** - ship은 API 필요 |

**Match: 3/5**

### Commonalities

- lint/test/build 실행
- 검증 결과 생성

### Differences

| Tool | API Check | Auto-fix | Evidence |
|------|-----------|----------|----------|
| `verify` | No | No | Checklist only |
| `gate` | No | Optional | EVIDENCE.md |
| `ship` | **Yes** | Optional | Full |
| `quick_ship` | **Yes** | No | Partial |
| `full_ship` | **Yes** | **Yes** | Full |

### Standard Candidate

**`ship`** - 이유:
1. 가장 완전한 기능 (lint+typecheck+test+build)
2. Trial/License 체크로 비즈니스 모델 지원
3. `quick_ship`, `full_ship`은 alias

**Deprecate 후보**:
- `verify` - `ship`으로 대체 가능 (체크리스트만 출력)
- `gate` - `ship`의 하위 호환

---

## Group 5: Manager/Feedback (피드백)

### Members

| Tool | Evidence |
|------|----------|
| `manager` | `server.py:572-587` |
| `quick_perspectives` | `server.py:593-605` |
| `list_managers` | `server.py:588-592` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 매니저 피드백 |
| Interface | **YES** - context → feedback |
| Side Effects | **YES** - Network (Worker API) |
| Runtime | **YES** - Worker, Async |
| Dependencies | **YES** - Worker API |

**Match: 5/5**

### Differences

| Tool | Depth | Cost | Use Case |
|------|-------|------|----------|
| `manager` | Full meeting | Higher | 상세 검토 |
| `quick_perspectives` | Questions only | Lower | 코딩 전 빠른 체크 |
| `list_managers` | Static list | None | 정보 조회 |

### Standard Candidate

**`manager`** for full review, **`quick_perspectives`** for quick check - 이유:
1. 용도가 명확히 다름
2. quick_perspectives는 Free (진입 장벽 낮음)
3. manager는 Pro (상세 분석)

**Keep both**: 목적이 다르므로 둘 다 유지

---

## Group 6: Setup/Config (환경 설정)

### Members

| Tool | Evidence |
|------|----------|
| `init_clouvel` | `server.py:179-186` |
| `setup_cli` | `server.py:187-198` |
| `init_rules` | `server.py:201-212` |
| `hook_design` | `server.py:383-396` |
| `hook_verify` | `server.py:397-411` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 프로젝트 설정 |
| Interface | **YES** - path + config |
| Side Effects | **YES** - File write |
| Runtime | **YES** - Local, Sync |
| Dependencies | **YES** - None |

**Match: 5/5**

### Differences

| Tool | Scope | Output |
|------|-------|--------|
| `init_clouvel` | Global | Guide |
| `setup_cli` | Project | Hooks, CLAUDE.md |
| `init_rules` | Project | Rules files |
| `hook_design` | Project | Design hooks |
| `hook_verify` | Project | Verify hooks |

### Standard Candidate

**`setup_cli`** for initial setup - 이유:
1. Pre-commit hook 설정 포함
2. CLAUDE.md 규칙 설정 포함
3. 가장 포괄적

**Merge 후보**:
- `hook_design` + `hook_verify` → `setup_cli --hooks`에 통합

---

## Group 7: Search/Query (검색)

### Members

| Tool | Evidence |
|------|----------|
| `search_knowledge` | `server.py:476-487` |
| `get_context` | `server.py:489-502` |
| `spawn_explore` | `server.py:353-366` |
| `spawn_librarian` | `server.py:367-380` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 정보 검색 |
| Interface | **YES** - query → results |
| Side Effects | **PARTIAL** - DB read vs File read |
| Runtime | **YES** - Local, Sync |
| Dependencies | **PARTIAL** - KB는 SQLite |

**Match: 3/5**

### Differences

| Tool | Source | Scope |
|------|--------|-------|
| `search_knowledge` | Knowledge DB | Past decisions |
| `get_context` | Knowledge DB | Recent context |
| `spawn_explore` | Codebase | File exploration |
| `spawn_librarian` | Codebase + Web | Library research |

### Standard Candidate

**용도별 분리 유지** - 이유:
1. search_knowledge: KB 전용
2. get_context: 세션 시작용
3. spawn_explore: 코드베이스 탐색
4. spawn_librarian: 외부 라이브러리 조사

---

## Group 8: Error Handling (에러 학습)

### Members

| Tool | Evidence |
|------|----------|
| `error_record` | `server.py:649-665` |
| `error_check` | `server.py:666-679` |
| `error_learn` | `server.py:680-692` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 에러 관리 |
| Interface | **YES** - path + error info |
| Side Effects | **YES** - File read/write |
| Runtime | **YES** - Local, Sync |
| Dependencies | **YES** - None |

**Match: 5/5** - 완전 동일 그룹

### Standard Candidate

**모두 유지** - 이유:
1. error_record: 에러 발생 시 기록
2. error_check: 코딩 전 패턴 체크
3. error_learn: 세션 종료 시 학습

**워크플로우**: record → check → learn (순서대로 사용)

---

## Group 9: File Tracking (파일 추적)

### Members

| Tool | Evidence |
|------|----------|
| `record_file` | `server.py:544-557` |
| `list_files` | `server.py:559-568` |
| `record_location` | `server.py:460-474` |

### Similarity Analysis

| Criterion | Match? |
|-----------|--------|
| Purpose | **YES** - 파일/위치 기록 |
| Interface | **YES** - path + file info |
| Side Effects | **YES** - File/DB write |
| Runtime | **YES** - Local, Sync |
| Dependencies | **PARTIAL** - location은 KB |

**Match: 4/5**

### Differences

| Tool | Storage | Scope |
|------|---------|-------|
| `record_file` | `.claude/files/` | 프로젝트 내 |
| `list_files` | `.claude/files/` | 프로젝트 내 |
| `record_location` | Knowledge DB | 전역 |

### Standard Candidate

**둘 다 유지** - 이유:
1. record_file: 프로젝트 내 파일 추적
2. record_location: 코드베이스 간 위치 추적

---

## Summary: Standard Candidates

| Group | Standard | Alternatives | Action |
|-------|----------|--------------|--------|
| 1. Doc Check | `can_code` | scan_docs, analyze_docs | **Deprecate** scan/analyze |
| 2. PRD | `start` + `save_prd` | get_prd_template, etc. | **Merge** into start |
| 3. Context | `record_decision`, `update_progress` | handoff, etc. | **Deprecate** handoff |
| 4. Verify | `ship` | verify, gate | **Deprecate** verify, gate |
| 5. Manager | `manager`, `quick_perspectives` | list_managers | **Keep** both |
| 6. Setup | `setup_cli` | init_clouvel, hooks | **Merge** hooks into setup |
| 7. Search | All different | - | **Keep** all |
| 8. Error | All needed | - | **Keep** all |
| 9. Tracking | `record_file`, `record_location` | list_files | **Keep** all |
