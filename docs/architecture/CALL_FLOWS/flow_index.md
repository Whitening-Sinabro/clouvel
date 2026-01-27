# Call Flows Index

> Clouvel 주요 기능의 코드 플로우 문서 목록

---

## Architecture Overview

| 문서 | 설명 | 용도 |
|------|------|------|
| [ENTRYPOINTS.md](../ENTRYPOINTS.md) | 진입점 (CLI, MCP, Packaging) | 코드 시작점 파악 |
| [SIDE_EFFECTS.md](../SIDE_EFFECTS.md) | 외부 부작용 매트릭스 | 네트워크/파일/환경변수 추적 |
| [SMOKE_LOGS.md](../SMOKE_LOGS.md) | 실행 검증 기록 | 문서-코드 일치 검증 |
| [RUNTIME_PATHS.md](../RUNTIME_PATHS.md) | 조건 분기 | 런타임 경로 파악 |
| [data_contracts.md](../data_contracts.md) | API 스키마 | 요청/응답 형식 |

---

## 핵심 플로우

| 플로우 | 파일 | 설명 |
|--------|------|------|
| Manager | [flow_manager.md](flow_manager.md) | C-Level 매니저 피드백 (Worker API) |
| Activate | [flow_activate.md](flow_activate.md) | 라이선스 활성화/검증 |
| Webhook | [flow_webhook.md](flow_webhook.md) | Worker API 통신 (인증, 에러처리, 엔드포인트) |

---

## Decision Log

| ADR | 상태 | 설명 |
|-----|------|------|
| [ADR-0001](../DECISION_LOG/ADR-0001-manager-execution.md) | RESOLVED | Manager 실행 아키텍처 (Worker API 선택) |

---

## 문서 규칙

각 플로우 문서는 다음을 포함해야 함:

1. **엔트리포인트**: 어디서 시작되는지 (파일:라인)
2. **호출 그래프**: 함수 호출 순서
3. **시퀀스 다이어그램**: mermaid 포맷
4. **근거 코드**: 파일:라인 리스트
5. **관련 ADR**: 아키텍처 결정 참조

---

## 버전

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.8.0 | 2026-01-26 | Manager Worker API 전환 |
