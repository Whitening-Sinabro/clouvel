# Side Effects Matrix

> Clouvel Architecture Documentation
> 모든 외부 부작용(네트워크, 파일, 환경변수, 프로세스)을 추적합니다.

---

## Summary

Clouvel의 Side Effects를 6개 카테고리로 분류:

| Category | Count | Risk Level |
|----------|-------|------------|
| Network | 7 endpoints | Medium-High |
| File I/O | 4 locations | Low-Medium |
| Environment | 6 variables | Low |
| Process | 2 calls | Low |
| Time/Random | 3 usages | Low |
| License/Credit | 4 checks | Medium |

---

## (A) Network Side Effects

### Worker API Calls

| Trigger | Endpoint | File:Line | Risk | Do Next |
|---------|----------|-----------|------|---------|
| `manager` 도구 호출 | `POST /api/manager` | `api_client.py:82-89` | Medium | 오프라인 시 fallback 응답 반환 |
| `ship` 도구 호출 | `POST /api/ship` | `api_client.py:145-152` | Low | 오프라인 시 로컬 실행 허용 |
| Trial 상태 조회 | `GET /api/trial/status` | `api_client.py:178-186` | Low | 실패 시 빈 객체 반환 |

### License API Calls

| Trigger | Endpoint | File:Line | Risk | Do Next |
|---------|----------|-----------|------|---------|
| 라이선스 검증 | Lemon Squeezy `/v1/licenses/validate` | `license.py:366` | Medium | 캐시 fallback |
| 라이선스 활성화 | Lemon Squeezy `/v1/licenses/activate` | `license.py:616-623` | High | 네트워크 필수 |
| Heartbeat | `POST /heartbeat` | `license.py:165-173` | Medium | 3일 오프라인 유예 |
| 환불 체크 | `GET /check` | `license.py:342-346` | Low | 실패 시 통과 |

### Evidence

```python
# api_client.py:16
API_BASE_URL = os.environ.get("CLOUVEL_API_URL", "https://clouvel-api.vnddns999.workers.dev")

# api_client.py:82-89
response = requests.post(
    f"{API_BASE_URL}/api/manager",
    json=payload,
    headers={"Content-Type": "application/json", "X-Clouvel-Client": _get_client_id()},
    timeout=API_TIMEOUT,  # 30 seconds
)

# license.py:36-44
LEMONSQUEEZY_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"
REVOKE_CHECK_URL = "https://clouvel-license-webhook.vnddns999.workers.dev/check"
HEARTBEAT_URL = "https://clouvel-license-webhook.vnddns999.workers.dev/heartbeat"
```

---

## (B) File I/O Side Effects

### Read Locations

| Location | Purpose | File:Line | Risk |
|----------|---------|-----------|------|
| `~/.clouvel/license.json` | 라이선스 캐시 | `license_common.py:70-82` | Low |
| `~/.clouvel-heartbeat` | Heartbeat 캐시 | `license.py:70` | Low |
| `~/.clouvel/knowledge.db` | Knowledge Base | `db/knowledge.py:~40` | Low |
| `docs/*.md` | PRD/문서 체크 | `tools/core.py:~50` | Low |

### Write Locations

| Location | Purpose | File:Line | Risk | Do Next |
|----------|---------|-----------|------|---------|
| `~/.clouvel/license.json` | 라이선스 저장 | `license_common.py:154-168` | Medium | 파일 권한 확인 |
| `~/.clouvel-heartbeat` | Heartbeat 저장 | `license.py:106-108` | Low | - |
| `~/.clouvel/knowledge.db` | KB 저장 | `db/knowledge.py:~60` | Medium | 50MB 제한 |
| `.git/hooks/pre-commit` | Hook 설치 | `server.py:1654-1772` | Medium | 기존 hook 백업 |
| `~/.claude/CLAUDE.md` | 규칙 추가 | `server.py:1776-1821` | Medium | 기존 내용 보존 |

### Evidence

```python
# license_common.py:70-82
def get_license_path() -> Path:
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:  # Unix
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "license.json"

# license.py:70
HEARTBEAT_FILE = Path.home() / ".clouvel-heartbeat"
```

---

## (C) Environment Variable Side Effects

### Read Variables

| Variable | Default | File:Line | Purpose |
|----------|---------|-----------|---------|
| `CLOUVEL_API_URL` | `https://clouvel-api...workers.dev` | `api_client.py:16` | API 베이스 URL |
| `CLOUVEL_LICENSE_KEY` | None | `api_client.py:30` | 라이선스 키 |
| `CLOUVEL_DEV` | None | `license_common.py:35` | 개발자 모드 |
| `CLOUVEL_REVOKE_CHECK_URL` | workers.dev URL | `license.py:41-44` | 환불 체크 URL |
| `CLOUVEL_HEARTBEAT_URL` | workers.dev URL | `license.py:66-69` | Heartbeat URL |
| `ANTHROPIC_API_KEY` | None | `tools/manager/generator/conversation.py:~20` | Dynamic meeting |

### Evidence

```python
# api_client.py:16
API_BASE_URL = os.environ.get("CLOUVEL_API_URL", "https://clouvel-api.vnddns999.workers.dev")

# license_common.py:35-36
if os.environ.get("CLOUVEL_DEV") == "1":
    return True
```

---

## (D) Process Side Effects

| Trigger | Command | File:Line | Risk | Do Next |
|---------|---------|-----------|------|---------|
| `is_developer()` | `git remote -v` | `license_common.py:42-53` | Low | 5초 timeout |
| `clouvel setup` | `claude mcp list/add` | `server.py:1827-1858` | Medium | FileNotFoundError 처리 |

### Evidence

```python
# license_common.py:42-53
result = subprocess.run(
    ["git", "remote", "-v"],
    capture_output=True,
    text=True,
    timeout=5,
    cwd=str(source_dir)
)

# server.py:1827-1830
check_result = subprocess.run(
    ["claude", "mcp", "list"],
    capture_output=True,
    text=True,
    timeout=10
)
```

---

## (E) Time/Random Side Effects

| Usage | File:Line | Impact |
|-------|-----------|--------|
| `datetime.now()` | `license_common.py:208,280` | 라이선스 활성화 시간 기록 |
| `uuid.getnode()` | `license_common.py:125` | Machine ID 생성 |
| `hashlib.sha256()` | `license_common.py:136`, `api_client.py:24` | ID 해시 |

---

## (F) License/Credit Checks

| Check Point | File:Line | Failure Behavior |
|-------------|-----------|------------------|
| Trial 횟수 체크 | Worker API (402 반환) | TRIAL EXHAUSTED 메시지 |
| 라이선스 유효성 | `license.py:471-591` | 캐시 fallback |
| Machine ID 일치 | `license.py:528-544` | 기기 불일치 에러 |
| 7일 잠금 | `license.py:1038-1060` | 프리미엄 기능 차단 |
| Heartbeat | `license.py:1063-1092` | 3일 유예 후 차단 |

---

<!-- AUTO-GEN:START -->
## Side Effects (Auto-Generated)

_Auto-generated: 2026-01-26 19:44_

### Network Calls

| File | Line | Call |
|------|------|------|
| `src\clouvel\api_client.py` | 82 | `response = requests.post(` |
| `src\clouvel\api_client.py` | 145 | `response = requests.post(` |
| `src\clouvel\api_client.py` | 178 | `response = requests.get(` |
| `src\clouvel\content_api.py` | 248 | `response = requests.post(` |
| `src\clouvel\content_api.py` | 350 | `response = requests.get(` |
| `src\clouvel\license.py` | 165 | `response = requests.post(` |
| `src\clouvel\license.py` | 342 | `response = requests.get(` |
| `src\clouvel\license.py` | 366 | `response = requests.post(` |
| `src\clouvel\license.py` | 616 | `response = requests.post(` |
| `src\clouvel\license.py` | 777 | `response = requests.post(` |
| `src\clouvel\license.py` | 844 | `response = requests.post(` |
| `src\clouvel\pro_downloader.py` | 83 | `response = requests.get(url, stream=True, timeout=60)` |
| `src\clouvel\pro_downloader.py` | 139 | `response = requests.post(` |
| `src\clouvel\version_check.py` | 34 | `response = requests.get(` |
| `src\clouvel\tools\team.py` | 43 | `response = requests.get(url, params=data, timeout=10)` |

### File I/O

| File | Line | Operation |
|------|------|-----------|
| `src\clouvel\analytics.py` | 22 | `clouvel_dir.mkdir(parents=True, exist_ok=True)` |
| `src\clouvel\analytics.py` | 31 | `return json.loads(path.read_text(encoding='utf-8'))` |
| `src\clouvel\analytics.py` | 40 | `path.write_text(json.dumps(data, ensure_ascii=False, indent=...` |
| `src\clouvel\api_client.py` | 40 | `data = json.loads(license_file.read_text())` |
| `src\clouvel\content_api.py` | 73 | `content["claude_md"] = claude_md_path.read_text(encoding="ut...` |
| `src\clouvel\content_api.py` | 79 | `content["commands"][cmd_file.stem] = cmd_file.read_text(enco...` |
| `src\clouvel\content_api.py` | 85 | `content["templates"][tpl_file.stem] = tpl_file.read_text(enc...` |
| `src\clouvel\content_api.py` | 93 | `content["config"][cfg_file.name] = cfg_file.read_text(encodi...` |
| `src\clouvel\content_api.py` | 101 | `content["settings"] = json.loads(settings_path.read_text(enc...` |
| `src\clouvel\content_api.py` | 110 | `content["roles"][role_file.stem] = role_file.read_text(encod...` |
| `src\clouvel\content_api.py` | 118 | `content["role_triggers"] = triggers_path.read_text(encoding=...` |
| `src\clouvel\content_api.py` | 132 | `return json.loads(license_file.read_text(encoding="utf-8"))` |
| `src\clouvel\content_api.py` | 143 | `data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf...` |
| `src\clouvel\content_api.py` | 163 | `CONTENT_CACHE_FILE.write_text(json.dumps(cache_data, ensure_...` |
| `src\clouvel\content_api.py` | 284 | `data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf...` |

### Environment Variables

| File | Line | Variable |
|------|------|----------|
| `src\clouvel\api_client.py` | 16 | `API_BASE_URL = os.environ.get("CLOUVEL_API_URL", "https://cl...` |
| `src\clouvel\api_client.py` | 30 | `license_key = os.environ.get("CLOUVEL_LICENSE_KEY")` |
| `src\clouvel\content_api.py` | 33 | `return os.environ.get("CLOUVEL_DEV_MODE", "").lower() in ("1...` |
| `src\clouvel\content_api.py` | 41 | `CONTENT_SERVER_URL = os.environ.get(` |
| `src\clouvel\license.py` | 41 | `REVOKE_CHECK_URL = os.environ.get(` |
| `src\clouvel\license.py` | 66 | `HEARTBEAT_URL = os.environ.get(` |
| `src\clouvel\license.py` | 127 | `key = license_key or os.environ.get("CLOUVEL_LICENSE")` |
| `src\clouvel\license.py` | 490 | `key = license_key or os.environ.get("CLOUVEL_LICENSE")` |
| `src\clouvel\license_common.py` | 35 | `if os.environ.get("CLOUVEL_DEV") == "1":` |
| `src\clouvel\license_common.py` | 76 | `base = Path(os.environ.get('USERPROFILE', '~'))` |
| `src\clouvel\license_common.py` | 120 | `computer_name = os.environ.get("COMPUTERNAME") or platform.n...` |
| `src\clouvel\license_common.py` | 131 | `username = os.environ.get("USERNAME") or os.environ.get("USE...` |
| `src\clouvel\pro_downloader.py` | 33 | `DOWNLOAD_API_URL = os.environ.get(` |
| `src\clouvel\pro_downloader.py` | 70 | `return os.environ.get("CLOUVEL_LICENSE")` |
| `src\clouvel\trial.py` | 29 | `base = Path(os.environ.get('USERPROFILE', '~'))` |

### Process Calls

| File | Line | Call |
|------|------|------|
| `src\clouvel\license_common.py` | 42 | `result = subprocess.run(` |
| `src\clouvel\server.py` | 1827 | `check_result = subprocess.run(` |
| `src\clouvel\server.py` | 1838 | `add_result = subprocess.run(` |
| `src\clouvel\tools\architecture.py` | 70 | `grep_result = subprocess.run(` |
| `src\clouvel\tools\architecture.py` | 90 | `grep_result = subprocess.run(` |
| `src\clouvel\tools\core.py` | 201 | `result = subprocess.run(` |
| `src\clouvel\tools\core.py` | 208 | `result2 = subprocess.run(` |
| `src\clouvel\tools\install.py` | 34 | `result = subprocess.run(` |
| `src\clouvel\tools\install.py` | 72 | `check = subprocess.run(` |
| `src\clouvel\tools\install.py` | 91 | `subprocess.run(` |

<!-- AUTO-GEN:END -->

---

## Manual Notes

### Risk Assessment

- **High Risk**: 라이선스 활성화 (네트워크 필수, 실패 시 복구 어려움)
- **Medium Risk**: Worker API 호출 (오프라인 fallback 있음), 파일 쓰기
- **Low Risk**: 환경변수 읽기, 시간/해시 사용

### Do Next (Red Volkswagen)

- **네트워크 호출 추가 시**: timeout 설정 필수, fallback 로직 구현
- **파일 쓰기 추가 시**: 기존 파일 백업 고려, 인코딩 utf-8 명시
- **환경변수 추가 시**: 기본값 제공, 문서화 필수
