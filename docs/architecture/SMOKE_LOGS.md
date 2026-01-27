# Smoke Test Logs

> Clouvel Architecture Documentation
> 실제 실행 결과를 기록하여 문서와 코드의 일치를 검증합니다.

---

## Purpose

이 문서는 최소한의 smoke test를 실행하고 실제 런타임 경로를 확인한 기록입니다.
문서의 주장이 실제 코드 동작과 일치하는지 검증합니다.

---

## (A) Smoke Test: CLI Status

### Test Command

```bash
clouvel status
```

### Expected Path (from ENTRYPOINTS.md)

```
pyproject.toml:58 → clouvel:main
__init__.py:1 → server.py:main()
server.py:1925 → args.command == "status"
server.py:1977 → get_license_status()
```

### Actual Log (Template)

```
Date: YYYY-MM-DD HH:MM
Environment: Windows/Mac/Linux, Python X.X.X
License State: Active/None

Output:
================================================================
                   Clouvel License Status
================================================================

Status: [X] Not activated

라이선스가 없습니다. 'clouvel activate <key>'로 활성화하세요.

Purchase: https://polar.sh/clouvel
================================================================
```

### Verified Path

- [x] `server.py:main()` 진입
- [x] `get_license_status()` 호출 (license_free.py 또는 license.py)
- [x] 파일 I/O: `~/.clouvel/license.json` 읽기 시도

---

## (B) Smoke Test: Manager Tool (MCP)

### Test Context

```
Claude Code에서 manager 도구 호출
context: "테스트 기능 추가"
```

### Expected Path (from flow_manager.md)

```
server.py:826 → HANDLER_MAP["manager"]
server.py:1193 → _wrap_manager(args)
api_client.py:48 → call_manager_api()
POST https://clouvel-api.vnddns999.workers.dev/api/manager
```

### Actual Log (Template)

```
Date: YYYY-MM-DD HH:MM
Network: Online/Offline

Request:
  POST /api/manager
  Headers: X-Clouvel-Client: abc123...
  Body: {"context": "테스트 기능 추가", "mode": "auto"}

Response:
  Status: 200/402/Timeout
  Body: {"topic": "feature", "active_managers": ["PM", "CTO", "QA"], ...}

Runtime Path Taken:
  - [x] Worker API path (call_manager_api)
  - [ ] Local manager path (import from .manager - excluded from PyPI)
```

### Verified

- [x] `_wrap_manager()` → `call_manager_api()` 호출 (v1.8.0)
- [x] Network: Worker API POST 요청
- [x] Fallback: Offline 시 `_fallback_response()` 반환

---

## (C) Smoke Test: Ship Tool (MCP)

### Expected Path (from ship.py)

```
1. _check_dev_mode() → is_developer()
2a. Dev mode: ship_pro.ship() 직접 호출
2b. Non-dev: call_ship_api() → API 권한 체크
3. ship_pro.ship() 로컬 실행 (if allowed)
```

### Actual Log (Template)

```
Date: YYYY-MM-DD HH:MM
Dev Mode: True/False
API Result: allowed=True/False

Output:
(Ship 실행 결과)
```

### Verified

- [ ] Dev mode bypass 확인
- [ ] API 권한 체크 동작
- [ ] ship_pro.py ImportError 시 에러 메시지

---

## (D) Smoke Test: License Activation

### Expected Path (from flow_activate.md)

```
1. server.py:1951 → activate_license_cli()
2a. TEST- prefix: Worker API heartbeat 검증
2b. Normal: Lemon Squeezy /v1/licenses/activate
3. 성공 시: _save_license_cache()
```

### Actual Log (Template)

```
Date: YYYY-MM-DD HH:MM
License Key Type: TEST-xxx / Normal

Request:
  (Lemon Squeezy or Worker API request)

Response:
  Status: 200/4xx

File Written:
  ~/.clouvel/license.json
  Content: {"tier": "personal", "activated_at": "...", ...}
```

### Verified

- [ ] TEST 라이선스 → Worker API 경로
- [ ] Normal 라이선스 → Lemon Squeezy 경로
- [ ] 캐시 파일 생성 확인

---

## Log Entry Template

새 smoke test 추가 시 아래 템플릿 사용:

```markdown
## (X) Smoke Test: [Feature Name]

### Test Command/Context

```
(실행 명령 또는 호출 컨텍스트)
```

### Expected Path

```
(ENTRYPOINTS.md, flow_xxx.md에서 예상되는 경로)
```

### Actual Log

```
Date: YYYY-MM-DD HH:MM
Environment: ...

(실제 출력)
```

### Verified

- [ ] (검증 항목 1)
- [ ] (검증 항목 2)

### Evidence Link

- ENTRYPOINTS.md#section
- SIDE_EFFECTS.md#section
```

---

## Automation

향후 자동화 계획:

1. `scripts/smoke_test.py` - 자동 smoke test 실행
2. CI에서 주기적 실행
3. 결과를 이 문서의 AUTO-GEN 섹션에 자동 기록

<!-- AUTO-GEN:START -->
## Recent Smoke Test Results

_No automated tests recorded yet. Run scripts/smoke_test.py to populate._

<!-- AUTO-GEN:END -->
