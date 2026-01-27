# MCP Standardization Plan

> 마지막 업데이트: 2026-01-26
> 상태: **v1.9 구현 완료** (Phase 1-2 Done, Phase 3 대기)

---

## Executive Summary

52개 MCP 도구를 9개 그룹으로 분류 후 표준화:

| Action | Count | Tools |
|--------|-------|-------|
| **Standard** | 12 | 각 그룹의 표준 도구 |
| **Keep** | 18 | 용도가 명확히 다른 도구 |
| **Merge** | 8 | 표준에 통합 |
| **Deprecate** | 6 | 단계적 폐기 |
| **Utility** | 8 | 보조 도구 (유지) |

---

## Group 1: Documentation Check

### Standard: `can_code`

| 항목 | 내용 |
|------|------|
| **When to Use** | 코딩 시작 전, Edit/Write 호출 전 |
| **Evidence** | `server.py:767` |
| **Input** | `path`: docs 폴더 경로 |
| **Output** | PASS/BLOCK + KB context |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `scan_docs` | **Deprecate** | v2.0에서 제거 | `can_code`가 내부적으로 호출 |
| `analyze_docs` | **Deprecate** | v2.0에서 제거 | `can_code`가 내부적으로 호출 |

### Next Action
> `scan_docs`, `analyze_docs`를 `can_code` 내부 helper로 이동, public API에서 제거

---

## Group 2: PRD/Template

### Standard: `start` + `save_prd`

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `start` | 새 프로젝트 온보딩, PRD 가이드 | `server.py:810` |
| `save_prd` | PRD 내용 저장 | `server.py:811` |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `get_prd_template` | **Merge** | `start`에 통합 | `start --template web-app` |
| `write_prd_section` | **Keep** | 섹션별 가이드 용도 | - |
| `get_prd_guide` | **Merge** | `start`에 통합 | `start --guide` |
| `list_templates` | **Keep** | 정보 조회용 | - |
| `init_docs` | **Merge** | `start`에 통합 | `start --init` |

### Next Action
> `start`가 `--template`, `--guide`, `--init` 옵션 지원하도록 확장

---

## Group 3: Context/Planning

### Standard: `record_decision` + `update_progress`

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `record_decision` | 아키텍처/설계 결정 기록 | `server.py:814` |
| `update_progress` | 현재 세션 진행 상태 | `server.py:799` |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `init_planning` | **Keep** | 세션 시작용 | - |
| `save_finding` | **Keep** | 리서치 결과 저장 | - |
| `refresh_goals` | **Keep** | 목표 리마인드 | - |
| `handoff` | **Deprecate** | v2.0에서 제거 | `record_decision` + `update_progress` 조합 |
| `record_location` | **Keep** | 코드 위치 추적 (용도 다름) | - |

### Next Action
> `handoff` 호출 시 deprecation warning + `record_decision` 자동 호출로 마이그레이션

---

## Group 4: Verification

### Standard: `ship`

| 항목 | 내용 |
|------|------|
| **When to Use** | 코드 완성 후 검증, 커밋 전 |
| **Evidence** | `server.py:835`, `tools/ship.py:50-131` |
| **Input** | `path`, `steps[]`, `auto_fix`, `feature` |
| **Output** | lint/typecheck/test/build 결과 + EVIDENCE.md |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `verify` | **Deprecate** | v2.0에서 제거 | `ship --steps=["lint"]` |
| `gate` | **Deprecate** | v2.0에서 제거 | `ship` |
| `quick_ship` | **Keep** | `ship` alias (편의성) | - |
| `full_ship` | **Keep** | `ship` alias (편의성) | - |

### Next Action
> `verify`, `gate` 호출 시 deprecation warning + `ship`으로 redirect

---

## Group 5: Manager/Feedback

### Standard: `manager` + `quick_perspectives`

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `manager` | 상세 검토, 전체 매니저 피드백 | `server.py:831` |
| `quick_perspectives` | 코딩 전 빠른 체크 (Free) | `server.py:833` |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `list_managers` | **Keep** | 정보 조회용 | - |

### Next Action
> 변경 없음. 두 도구 모두 용도가 명확히 다름 (상세 vs 빠른)

---

## Group 6: Setup/Config

### Standard: `setup_cli`

| 항목 | 내용 |
|------|------|
| **When to Use** | 프로젝트 초기 설정, hook 설치 |
| **Evidence** | `server.py:782` |
| **Input** | `path`, `level` |
| **Output** | CLAUDE.md, pre-commit hook |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `init_clouvel` | **Keep** | 전역 온보딩 (용도 다름) | - |
| `init_rules` | **Merge** | `setup_cli`에 통합 | `setup_cli --rules` |
| `hook_design` | **Merge** | `setup_cli`에 통합 | `setup_cli --hook=design` |
| `hook_verify` | **Merge** | `setup_cli`에 통합 | `setup_cli --hook=verify` |

### Next Action
> `setup_cli`가 `--rules`, `--hook` 옵션 지원하도록 확장

---

## Group 7: Search/Query

### Standard: 용도별 분리 유지

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `search_knowledge` | KB 검색 (과거 결정) | `server.py:817` |
| `get_context` | 세션 시작 시 컨텍스트 로드 | `server.py:819` |
| `spawn_explore` | 코드베이스 탐색 | `server.py:802` |
| `spawn_librarian` | 외부 라이브러리 조사 | `server.py:803` |

### Alternatives

없음. 모든 도구가 고유한 용도.

### Next Action
> 변경 없음. 검색 대상이 다름 (KB vs Codebase vs External)

---

## Group 8: Error Handling

### Standard: 워크플로우별 전체 유지

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `error_record` | 에러 발생 시 5 Whys 기록 | `server.py:837` |
| `error_check` | 코딩 전 과거 에러 패턴 확인 | `server.py:839` |
| `error_learn` | 세션 종료 시 CLAUDE.md 자동 업데이트 | `server.py:841` |

### Alternatives

없음. 워크플로우: `error_check` → (코딩) → `error_record` → `error_learn`

### Next Action
> 변경 없음. 에러 학습 사이클의 각 단계

---

## Group 9: File Tracking

### Standard: `record_file` + `record_location`

| Tool | When to Use | Evidence |
|------|-------------|----------|
| `record_file` | 프로젝트 내 파일 추적 | `server.py:827` |
| `record_location` | KB에 코드 위치 기록 | `server.py:815` |

### Alternatives

| Tool | Status | Action | Migration Path |
|------|--------|--------|----------------|
| `list_files` | **Keep** | 조회용 | - |

### Next Action
> 변경 없음. 기록 vs 조회 용도

---

## Utility Tools (그룹 외)

| Tool | Status | Reason |
|------|--------|--------|
| `get_rule` | **Keep** | Rules 조회 |
| `add_rule` | **Keep** | Rules 추가 |
| `get_analytics` | **Keep** | 통계 조회 |
| `get_verify_checklist` | **Keep** | 체크리스트 조회 |
| `get_setup_guide` | **Keep** | 가이드 조회 |
| `plan` | **Keep** | 상세 계획 생성 |
| `init_knowledge` | **Keep** | KB 초기화 |
| `rebuild_index` | **Keep** | KB 인덱스 재구축 |

---

## License Tools (별도 관리)

| Tool | Status | Reason |
|------|--------|--------|
| `activate_license` | **Keep** | 라이선스 활성화 |
| `license_status` | **Keep** | 라이선스 상태 조회 |
| `upgrade_pro` | **Keep** | Pro 업그레이드 가이드 |
| `unlock_decision` | **Keep** | LOCKED 결정 해제 |
| `list_locked_decisions` | **Keep** | LOCKED 결정 조회 |
| `arch_check` | **Keep** | 아키텍처 체크 |
| `check_imports` | **Keep** | Import 검증 |
| `check_duplicates` | **Keep** | 중복 검사 |

---

## Implementation Roadmap

### Phase 1: Deprecation Warnings (v1.9) ✅ DONE

```python
# 패턴: deprecated 도구 호출 시 warning
deprecation_warning = """⚠️ **DEPRECATED**: `scan_docs` will be removed in v2.0.
Use `can_code` instead...
"""
return [TextContent(type="text", text=deprecation_warning + result)]
```

**대상 (11개)**: `scan_docs`, `analyze_docs`, `verify`, `gate`, `handoff`, `get_prd_template`, `get_prd_guide`, `init_docs`, `init_rules`, `hook_design`, `hook_verify`

### Phase 2: Option Extensions (v1.9) ✅ DONE

**`start` 확장**:
- `--template`: get_prd_template 기능
- `--layout`: template layout (lite/standard/detailed)
- `--guide`: get_prd_guide 기능
- `--init`: init_docs 기능

**`setup_cli` 확장**:
- `--rules`: init_rules 기능 (web/api/fullstack/minimal)
- `--hook`: hook_design/hook_verify 기능 (design/verify)
- `--hook_trigger`: hook trigger 지정

### Phase 3: Removal (v2.0)

| Tool | Removal Date | Replacement |
|------|--------------|-------------|
| `scan_docs` | v2.0 | `can_code` |
| `analyze_docs` | v2.0 | `can_code` |
| `verify` | v2.0 | `ship` |
| `gate` | v2.0 | `ship` |
| `handoff` | v2.0 | `record_decision` + `update_progress` |
| `get_prd_template` | v2.0 | `start --template` |
| `get_prd_guide` | v2.0 | `start --guide` |
| `init_docs` | v2.0 | `start --init` |

---

## Summary Table

| Group | Standard | Deprecate | Merge | Keep |
|-------|----------|-----------|-------|------|
| 1. Doc Check | `can_code` | 2 | 0 | 0 |
| 2. PRD | `start`, `save_prd` | 0 | 3 | 2 |
| 3. Context | `record_decision`, `update_progress` | 1 | 0 | 4 |
| 4. Verify | `ship` | 2 | 0 | 2 |
| 5. Manager | `manager`, `quick_perspectives` | 0 | 0 | 1 |
| 6. Setup | `setup_cli` | 0 | 3 | 1 |
| 7. Search | All 4 | 0 | 0 | 4 |
| 8. Error | All 3 | 0 | 0 | 3 |
| 9. Tracking | `record_file`, `record_location` | 0 | 0 | 1 |
| **Total** | **12** | **5** | **6** | **18** |

---

## Do Next (Red Volkswagen)

| 상황 | 행동 |
|------|------|
| 새 MCP 추가 시 | 먼저 이 문서에서 유사 도구 확인, 그룹에 맞게 배치 |
| Deprecate 도구 사용 시 | warning 출력 후 replacement 도구 안내 |
| 표준 도구 수정 시 | 해당 그룹의 Merge 대상도 함께 고려 |

