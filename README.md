# Clouvel

바이브코딩 프로세스를 강제하는 MCP 서버.

**PRD 없으면 코딩 없다.**

## 현재 버전

- MCP 서버: v0.3.1
- VS Code 확장: v0.10.2
- Cursor 확장: v0.10.2

## 설치

### 방법 1: VS Code/Cursor 확장 (추천)

1. 확장 탭에서 "Clouvel" 검색 → 설치
2. `Ctrl+Shift+P` → "Clouvel: Claude Desktop 설정" 선택
3. 끝!

### 방법 2: 수동 설정

Claude Desktop 설정 (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "clouvel": {
      "command": "uvx",
      "args": ["clouvel"]
    }
  }
}
```

## 핵심 기능

### can_code - 코딩 차단

```
코딩해도 돼? (can_code로 docs 폴더 확인)
```

- docs 폴더 없음 → **코딩 금지**
- 필수 문서 부족 → **코딩 금지**
- 모든 문서 있음 → **코딩 허용**

### init_docs - 문서 초기화

```
init_docs로 docs 폴더 만들어줘
```

5개 템플릿 자동 생성:
- PRD.md
- ARCHITECTURE.md
- API.md
- DATABASE.md
- VERIFICATION.md

## 전체 도구 목록

| 도구 | 설명 |
|------|------|
| `can_code` | **코딩 가능 여부 확인** - 핵심 기능 |
| `init_docs` | docs 폴더 초기화 + 템플릿 생성 |
| `scan_docs` | docs 폴더 파일 목록 |
| `analyze_docs` | 필수 문서 체크, 빠진 거 알려줌 |
| `get_prd_template` | PRD 템플릿 생성 (11개 섹션) |
| `write_prd_section` | 섹션별 PRD 작성 가이드 |
| `get_prd_guide` | PRD 작성 가이드 |
| `get_verify_checklist` | 검증 체크리스트 |
| `get_setup_guide` | 설치/설정 가이드 |

## 사용 플로우

```
1. can_code → "코딩 금지" (문서 없음)
2. init_docs → 빈 템플릿 생성
3. Claude와 함께 PRD 작성
4. can_code → "코딩 허용"
5. 코딩 시작!
```

## 필수 문서

`can_code`가 체크하는 것들:

- **PRD** (제품 요구사항) - 가장 중요
- **아키텍처** 문서
- **API** 스펙
- **DB** 스키마
- **검증** 계획

다 있어야 코딩 허용.

## VS Code/Cursor 확장 기능

- 원클릭 MCP 서버 설정
- 사이드바에서 문서 상태 확인
- 코드 파일에 경고 표시 (Diagnostic)
- 프로젝트 유형별 PRD 템플릿 (수익화/개인/사내)

## 왜?

바이브코딩 = AI가 코드 짬.
근데 PRD 없이 시작하면 = 나중에 다 뜯어고침.

**Clouvel = 문서 없으면 코딩 못 하게 강제.**

## 피드백 / 버그 리포트

[GitHub Issues](https://github.com/JinHyeokPark28/clouvel/issues)에 남겨주세요!

## License

MIT
