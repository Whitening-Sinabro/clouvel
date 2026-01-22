# MCP 플랫폼 확장 계획

> 현재 Claude 특화 → 범용 MCP 도구 지원

---

## 현재 상태

Clouvel은 Claude 생태계에 특화되어 있음:

| 기능 | Claude 특화 이유 |
|------|------------------|
| `CLAUDE.md` 규칙 | Claude만 읽음 |
| `.claude/` 디렉토리 | Claude 워크플로 구조 |
| `clouvel setup` | `claude mcp add` 명령어 사용 |
| "코딩 전 can_code 자동 호출" | CLAUDE.md 규칙 기반 |

---

## 지원 대상 플랫폼

### 현재 지원 (Claude 생태계)

- [x] Claude Code (CLI)
- [x] Claude Desktop
- [x] VS Code (Claude 확장)
- [x] Cursor

### 확장 예정

- [ ] Windsurf
- [ ] Zed
- [ ] 기타 MCP 지원 IDE

---

## 확장 계획

### Phase 1: 조사 (우선순위 높음)

1. **Windsurf MCP 지원 현황 조사**
   - MCP 서버 연결 방식
   - 설정 파일 위치/형식
   - 규칙 파일 시스템 (CLAUDE.md 대안)

2. **Zed MCP 지원 현황 조사**
   - MCP 지원 여부 확인
   - 설정 방식

### Phase 2: 범용 설정 시스템 (우선순위 중간)

1. **범용 규칙 파일 지원**
   ```
   현재: CLAUDE.md만 지원
   목표: .clouvel/rules.md 또는 clouvel.config.json
   ```

2. **플랫폼 감지 로직**
   ```python
   def detect_platform():
       # Claude Code CLI 감지
       # Windsurf 감지
       # Cursor 감지
       # 등등
   ```

3. **플랫폼별 setup 로직**
   ```bash
   clouvel setup              # 자동 감지
   clouvel setup --platform windsurf
   clouvel setup --platform zed
   ```

### Phase 3: 자동 차단 기능 (우선순위 낮음)

각 플랫폼별 "코딩 전 can_code 자동 호출" 구현:

| 플랫폼 | 방법 |
|--------|------|
| Claude | CLAUDE.md 규칙 |
| Windsurf | TBD (조사 필요) |
| Cursor | TBD (rules 파일?) |
| Zed | TBD |

---

## 기술적 고려사항

### MCP 서버 자체는 범용

```python
# can_code 도구는 어떤 MCP 클라이언트에서도 호출 가능
@server.tool()
async def can_code(path: str):
    # PRD 체크 로직은 플랫폼 무관
    ...
```

### 플랫폼별 차이점

1. **설정 파일 위치**
   - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windsurf: TBD
   - Cursor: TBD

2. **규칙 파일**
   - Claude: `CLAUDE.md`, `.claude/`
   - 다른 도구: 각자의 시스템

3. **자동 호출 트리거**
   - Claude: CLAUDE.md에 "코딩 전 can_code 호출" 규칙
   - 다른 도구: 각 플랫폼의 hook/규칙 시스템 활용

---

## 마일스톤

| 버전 | 내용 |
|------|------|
| v1.4 | Windsurf 지원 조사 완료 |
| v1.5 | 범용 설정 파일 지원 |
| v2.0 | 멀티 플랫폼 정식 지원 |

---

## 참고

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Windsurf MCP 문서](TBD)
- [Cursor MCP 문서](TBD)
