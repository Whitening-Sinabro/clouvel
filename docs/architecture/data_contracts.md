# Manager API 데이터 계약

> 작성일: 2026-01-26
> 버전: v1.7.3 기준
> 근거: `api_client.py:48-124`, `api_client.py:195-242`

---

## (A) /api/manager 요청/응답 스키마

### 엔드포인트

```
POST https://clouvel-api.vnddns999.workers.dev/api/manager
```

### 요청 (Request)

```json
{
  "context": "string",      // 필수. 검토할 내용
  "mode": "string",         // 선택. "auto" | "all" | "specific" (기본값: "auto")
  "topic": "string",        // 선택. "auth" | "api" | "payment" | "ui" | "feature" | "launch" | "error" | "security" | "performance" | "maintenance" | "design"
  "managers": ["string"],   // 선택. mode="specific"일 때 매니저 목록 ["PM", "CTO", ...]
  "licenseKey": "string"    // 선택. 라이선스 키 (있으면 Pro 권한)
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `context` | string | O | 검토할 내용 (PRD, 계획, 코드 등) |
| `mode` | string | X | 매니저 선택 모드 |
| `topic` | string | X | 토픽 힌트 (자동 매니저 선택에 사용) |
| `managers` | string[] | X | 특정 매니저 지정 (mode=specific) |
| `licenseKey` | string | X | 라이선스 키 |

### 응답 (Response) - 성공

```json
{
  "topic": "string",
  "active_managers": ["PM", "CTO", "QA"],
  "feedback": {
    "PM": {
      "emoji": "👔",
      "title": "Product Manager",
      "questions": ["string", "string"]
    },
    "CTO": {
      "emoji": "🛠️",
      "title": "CTO",
      "questions": ["string", "string"]
    }
  },
  "formatted_output": "string",
  "offline": false
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `topic` | string | 감지된 토픽 |
| `active_managers` | string[] | 참여한 매니저 목록 |
| `feedback` | object | 매니저별 피드백 |
| `feedback[].emoji` | string | 매니저 이모지 |
| `feedback[].title` | string | 매니저 타이틀 |
| `feedback[].questions` | string[] | 질문/피드백 목록 |
| `formatted_output` | string | 마크다운 포맷 출력 |
| `offline` | boolean | 오프라인 모드 여부 |

---

## (B) 인증/라이선스 흐름

### 헤더

```http
Content-Type: application/json
X-Clouvel-Client: {client_id}
```

| 헤더 | 생성 위치 | 용도 |
|------|----------|------|
| `X-Clouvel-Client` | `api_client.py:20-24` `_get_client_id()` | Trial 추적용 클라이언트 식별자 |

### Client ID 생성 로직

```python
# api_client.py:20-24
def _get_client_id() -> str:
    machine_info = f"{platform.node()}-{platform.machine()}-{os.getlogin()}"
    return hashlib.sha256(machine_info.encode()).hexdigest()[:32]
```

### 라이선스 키 조회 순서

```python
# api_client.py:27-45
def _get_license_key() -> Optional[str]:
    # 1. 환경변수
    license_key = os.environ.get("CLOUVEL_LICENSE_KEY")
    if license_key:
        return license_key

    # 2. 파일
    license_file = Path.home() / ".clouvel" / "license.json"
    if license_file.exists():
        data = json.loads(license_file.read_text())
        return data.get("key")

    return None
```

### 인증 흐름 다이어그램

```
[클라이언트]                              [Worker API]
     │                                        │
     │──1. X-Clouvel-Client 헤더 생성─────────│
     │   (machine hash)                       │
     │                                        │
     │──2. licenseKey 조회───────────────────│
     │   환경변수 → 파일 → None              │
     │                                        │
     │──3. POST /api/manager─────────────────▶│
     │   {context, licenseKey, ...}           │
     │                                        │──4. Trial/License 체크
     │                                        │    KV에서 client_id 조회
     │                                        │
     │◀─5a. 200 OK (성공)────────────────────│
     │   또는                                 │
     │◀─5b. 402 Payment Required──────────────│
     │   (Trial 소진)                         │
```

---

## (C) 에러 응답 포맷

### 402 Payment Required (Trial 소진)

```json
{
  "message": "Trial exhausted. You have used all 3 free uses.",
  "upgrade_url": "https://polar.sh/clouvel"
}
```

**클라이언트 측 처리** (`api_client.py:92-111`):

```python
if response.status_code == 402:
    data = response.json()
    return {
        "error": "trial_exhausted",
        "message": data.get("message", "Trial exhausted"),
        "upgrade_url": data.get("upgrade_url", "https://polar.sh/clouvel"),
        "formatted_output": "==== TRIAL EXHAUSTED ==== ..."
    }
```

### 네트워크 에러

| 에러 | 조건 | 클라이언트 처리 |
|------|------|----------------|
| Timeout | 30초 초과 | `_fallback_response("API timeout...")` |
| ConnectionError | 네트워크 불가 | `_fallback_response("Cannot connect...")` |
| 기타 Exception | 예상치 못한 에러 | `_fallback_response(f"API error: {e}")` |

### Fallback 응답 구조

```json
{
  "topic": "feature",
  "active_managers": ["PM", "CTO", "QA"],
  "feedback": { ... },
  "formatted_output": "## 💡 C-Level Perspectives (Offline Mode)\n\n> ⚠️ {error_message}\n\n...",
  "offline": true
}
```

---

## 참조 코드 라인

| 항목 | 파일 | 라인 |
|------|------|------|
| API Base URL | `api_client.py` | 16 |
| call_manager_api 정의 | `api_client.py` | 48-123 |
| Client ID 생성 | `api_client.py` | 20-24 |
| License Key 조회 | `api_client.py` | 27-45 |
| 402 처리 | `api_client.py` | 92-111 |
| Fallback 응답 | `api_client.py` | 195-242 |
