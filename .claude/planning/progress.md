# Progress

> 마지막 업데이트: 2026-01-23

---

## 완료 (Completed)

- **Polar.sh 마이그레이션 완료**
  - Lemon Squeezy → Polar.sh 전환
  - 상품 6종 생성 (월간/연간)
  - Worker 라이선스 검증 Polar.sh API 연동
  - 랜딩페이지 가격/체크아웃 링크 업데이트
  - 코드베이스 Lemon Squeezy 참조 제거
- PRD 설명 섹션 추가 (index.html)
- ROADMAP.md에서 크몽 관련 내용 전체 제거
- v1.4 목표 현실적으로 수정 (안정화 + 크로스플랫폼)
- KmongMCP 프로젝트 분리 완료
- .gitignore 정리
- FAQ 페이지 추가
- **ship.py Pro 코드 stub 전환** (417줄 → 70줄 stub)
- **S3 Pro 배포 인프라 구축**
  - S3 버킷: `clouvel-pro-dist` (ap-southeast-1)
  - Cloudflare Worker: `clouvel-pro-download.vnddns999.workers.dev`
  - IAM 사용자: `clouvel-s3-worker`
  - Pro 코드 9개 모듈 S3 업로드 완료 (v1.3.8)
  - 다운로드 테스트 완료 ✅
- **PyPI v1.3.9 배포**
  - Pro 활성화 플로우 구현
  - 에러 처리 강화 (재시도, 지수 백오프)
  - 테스트 라이선스 만료 로직 (2026-01-28)
  - README 문서화
- **MCP 스키마 캐시 및 라이선스 문제 해결**
  - 근본 원인: Claude AI가 도구 설명의 `(Pro)` 텍스트를 해석해 도구 호출 자체를 거부
  - 해결: server.py의 모든 도구 설명에서 `(Pro)` 제거
  - 추가 수정: 환경변수 이름 통일 (`CLOUVEL_DEV`, `CLOUVEL_DEV_MODE` 둘 다 지원)
  - 문서화: `.clouvel/errors/2026-01-23_mcp-schema-cache.md`
  - 디버깅 방법론 정리: `.clouvel/errors/debugging-methodology.md`

---

## 완료 (Recent)

- **Error System v2.0 전체 구현 완료** ✅
  - Phase 1: SQLite 스키마 + CRUD (`src/clouvel/db/`)
  - Phase 2: 벡터 검색 (ChromaDB optional, fallback 텍스트)
  - Phase 3: 신규 MCP 도구 4종 (`error_search`, `error_resolve`, `error_get`, `error_stats`)
  - Phase 4: MCP Resources 3종 (`error://recent`, `error://stats`, `error://rules`)
  - Optional dependencies: `pip install clouvel[vector]`

## 진행중 (In Progress)

- v1.4 안정화
  - 코드 점검 + 버그 수정
  - 리팩토링
  - 템플릿 문서 작성

---

## 블로커 (Blockers)

- Polar.sh Payout 계정 인증 대기 중

---

## 다음 할 일 (Next)

- 코드 점검 + 버그 수정
- 리팩토링
- 템플릿 8종 문서 작성

---

> 💡 업데이트: `update_progress` 도구 호출
