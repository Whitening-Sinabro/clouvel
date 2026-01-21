# Clouvel PRD

> PRD 없으면 코딩 없다.

## 한 줄 정의

바이브코딩 프로세스를 강제하는 MCP 서버

## 핵심 기능

### Free (v1.3)

| 도구              | 설명                                               |
| ----------------- | -------------------------------------------------- |
| `can_code`        | 문서 검사 후 코딩 허용/차단                        |
| `start`           | 프로젝트 온보딩                                    |
| `plan`            | **[NEW]** 상세 실행 계획 생성 (매니저 피드백 기반) |
| `init_planning`   | 영속적 컨텍스트 초기화                             |
| `update_progress` | 진행 상황 업데이트                                 |
| `refresh_goals`   | 목표 리마인드                                      |

### Pro

| 도구         | 설명                              |
| ------------ | --------------------------------- |
| `manager`    | 8명 C-Level 매니저 협업 피드백    |
| `ship`       | 원클릭 검증 (lint → test → build) |
| `quick_ship` | 빠른 검증 (lint + test)           |
| `full_ship`  | 전체 검증 + 자동 수정             |

## 타겟

Claude Code 사용자 중 바이브코딩 초보자

## Acceptance (완료 기준)

### Core

- [x] `can_code` 호출 시 PRD 없으면 BLOCK
- [x] `can_code` 호출 시 acceptance 섹션 없으면 BLOCK
- [x] `can_code` 호출 시 권장 문서 없으면 WARN (진행 가능)
- [x] `clouvel setup` 실행 시 글로벌 CLAUDE.md에 규칙 추가
- [x] `clouvel setup` 실행 시 MCP 서버 자동 등록
- [x] Claude가 코드 작성 전 자동으로 `can_code` 호출

### v1.3 Plan Tool

- [x] `plan` 호출 시 manager 피드백 자동 수집
- [x] 액션 아이템을 Phase별(준비/설계/구현/검증)로 그룹화
- [x] 의존성 기반 토폴로지 정렬
- [x] task_plan.md에 상세 계획 저장
- [x] 검증 포인트 및 완료 조건 포함
