# -*- coding: utf-8 -*-
"""Docs tools: PRD 템플릿, 가이드 등"""

import os
from datetime import datetime
from pathlib import Path
from mcp.types import TextContent


# 사용 가능한 템플릿 목록
TEMPLATES = {
    "web-app": {
        "name": "Web Application",
        "layouts": ["lite", "standard", "detailed"],
        "description": "웹 애플리케이션 (React, Vue, Next.js 등)"
    },
    "api": {
        "name": "API Server",
        "layouts": ["lite", "standard"],
        "description": "REST/GraphQL API 서버"
    },
    "cli": {
        "name": "CLI Tool",
        "layouts": ["lite", "standard"],
        "description": "커맨드라인 도구"
    },
    "chrome-ext": {
        "name": "Chrome Extension",
        "layouts": ["lite", "standard"],
        "description": "Chrome 확장프로그램 (MV3)"
    },
    "discord-bot": {
        "name": "Discord Bot",
        "layouts": ["lite", "standard"],
        "description": "디스코드 봇 (discord.js/discord.py)"
    },
    "landing-page": {
        "name": "Landing Page",
        "layouts": ["lite", "standard"],
        "description": "랜딩 페이지 / 마케팅 페이지"
    },
    "saas": {
        "name": "SaaS MVP",
        "layouts": ["lite", "standard"],
        "description": "SaaS MVP (인증 + 결제 + 구독)"
    },
    "generic": {
        "name": "Generic",
        "layouts": ["standard"],
        "description": "범용 템플릿"
    }
}


def _get_template_path(template: str, layout: str) -> Path:
    """템플릿 파일 경로 반환"""
    # 패키지 내부 templates 폴더
    base_path = Path(__file__).parent.parent / "templates"
    return base_path / template / f"{layout}.md"


def _load_template(template: str, layout: str) -> str:
    """템플릿 파일 로드"""
    template_path = _get_template_path(template, layout)

    if template_path.exists():
        return template_path.read_text(encoding="utf-8")

    # 파일이 없으면 generic 템플릿 반환
    return None


async def get_prd_template(project_name: str, output_path: str, template: str = "generic", layout: str = "standard") -> list[TextContent]:
    """PRD 템플릿 생성

    Args:
        project_name: 프로젝트 이름
        output_path: 출력 경로
        template: 템플릿 종류 (web-app, api, cli, generic)
        layout: 레이아웃 (lite, standard, detailed)
    """
    # 템플릿 로드 시도
    content = _load_template(template, layout)

    if content:
        # placeholder 치환
        now = datetime.now().strftime('%Y-%m-%d')
        content = content.replace("{PROJECT_NAME}", project_name)
        content = content.replace("{DATE}", now)

        return [TextContent(type="text", text=f"""# {template}/{layout} 템플릿

```markdown
{content}
```

---

**저장 경로**: `{output_path}`

**다음 단계**:
1. 위 내용을 `{output_path}`에 저장
2. [ ] 로 표시된 부분을 채우기
3. 완료 후 코딩 시작

**팁**: 한 번에 다 채우려 하지 마세요. 핵심(1~4번)부터 채우고 시작해도 됩니다.
""")]

    # generic fallback
    template_content = f"""# {project_name} PRD

> 이 문서가 법. 여기 없으면 안 만듦.
> 작성일: {datetime.now().strftime('%Y-%m-%d')}

---

## 1. 한 줄 요약
<!-- 프로젝트가 뭔지 한 문장으로. 못 쓰면 정리 안 된 거임. -->

[여기에 작성]

---

## 2. 핵심 원칙

> 절대 안 변하는 것들. 이거 기준으로 기능 판단.

1. [원칙 1]
2. [원칙 2]
3. [원칙 3]

---

## 3. 용어 정의

| 용어 | 설명 |
|------|------|
| [용어1] | [설명] |

---

## 4. 입력 스펙

> 외부에서 들어오는 거. 사용자 입력, API 요청 등.

### 4.1 [입력 타입 1]
- 형식:
- 필수 필드:
- 제한사항:

---

## 5. 출력 스펙

> 외부로 나가는 거. UI, API 응답, 파일 등.

### 5.1 [출력 타입 1]
- 형식:
- 필드:
- 예시:

---

## 6. 에러 케이스

> 터질 수 있는 모든 상황. 빠뜨리면 버그됨.

| 상황 | 처리 방법 | 에러 코드 |
|------|----------|-----------|
| [상황1] | [방법] | [코드] |

---

## 7. 검증 계획

- [ ] [테스트 케이스 1]
- [ ] [테스트 케이스 2]

---

## 변경 로그

| 날짜 | 변경 내용 | 작성자 |
|------|----------|--------|
| {datetime.now().strftime('%Y-%m-%d')} | 최초 작성 | |

"""
    return [TextContent(type="text", text=f"```markdown\n{template_content}\n```\n\n출력 경로: `{output_path}`에 저장하세요.")]


async def list_templates() -> list[TextContent]:
    """사용 가능한 템플릿 목록"""
    lines = ["# PRD 템플릿 목록\n"]

    for key, info in TEMPLATES.items():
        layouts = ", ".join(info["layouts"])
        lines.append(f"## {info['name']} (`{key}`)")
        lines.append(f"- **설명**: {info['description']}")
        lines.append(f"- **레이아웃**: {layouts}")
        lines.append("")

    lines.append("---")
    lines.append("**사용법**: `get_prd_template` 호출 시 `template`과 `layout` 지정")
    lines.append("```")
    lines.append('예: template="web-app", layout="standard"')
    lines.append("```")

    return [TextContent(type="text", text="\n".join(lines))]


async def write_prd_section(section: str, content: str) -> list[TextContent]:
    """PRD 섹션별 작성 가이드"""
    guides = {
        "summary": "한 줄 요약: 프로젝트가 뭔지 한 문장으로. 못 쓰면 정리 안 된 거임.",
        "principles": "핵심 원칙: 절대 안 변하는 것들 3-5개. 기능 판단의 기준.",
        "input_spec": "입력 스펙: 외부에서 들어오는 모든 것. 형식, 필수 필드, 제한사항 포함.",
        "output_spec": "출력 스펙: 외부로 나가는 모든 것. 형식, 필드, 예시 포함.",
        "errors": "에러 케이스: 터질 수 있는 모든 상황. 하나라도 빠뜨리면 버그됨.",
        "state_machine": "상태 머신: 상태가 있으면 그림으로. 상태 전이 명확하게.",
        "api_endpoints": "API 엔드포인트: Method, Path, 설명. RESTful하게.",
        "db_schema": "DB 스키마: 테이블, 컬럼, 타입, 관계. 정규화 고려.",
    }

    guide = guides.get(section, "알 수 없는 섹션입니다.")
    return [TextContent(type="text", text=f"## {section} 작성 가이드\n\n{guide}\n\n내용:\n{content if content else '(입력 필요)'}")]


async def get_prd_guide() -> list[TextContent]:
    """PRD 작성 가이드"""
    return [TextContent(type="text", text="""# PRD 작성 가이드

## 왜 PRD?
- 코딩 전에 뭘 만들지 정리
- 팀원/AI 간 인식 통일
- 나중에 "이거 왜 이렇게 했지?" 방지

## 작성 순서

### 1단계: 핵심부터
1. **한 줄 요약** - 못 쓰면 정리 안 된 거
2. **핵심 원칙** - 절대 안 변하는 3가지

### 2단계: 입출력
3. **입력 스펙** - 뭐가 들어오나
4. **출력 스펙** - 뭐가 나가나

### 3단계: 예외처리
5. **에러 케이스** - 터질 수 있는 거 다

### 4단계: 상세
6. **API** - 엔드포인트 목록
7. **DB** - 테이블 구조
8. **상태 머신** - 있으면

### 5단계: 검증
9. **테스트 계획** - 어떻게 확인할 건지

## 팁
- 완벽하게 쓰려고 하지 마. 일단 써.
- 코딩하면서 업데이트해도 됨.
- 근데 PRD에 없는 기능은 절대 안 만듦.
""")]


async def get_verify_checklist() -> list[TextContent]:
    """검증 체크리스트"""
    return [TextContent(type="text", text="""# 검증 체크리스트

## PRD 검증
- [ ] 한 줄 요약이 명확한가?
- [ ] 핵심 원칙이 3개 이상인가?
- [ ] 입력/출력 스펙이 구체적인가?
- [ ] 에러 케이스가 빠짐없이 있는가?

## 코드 검증
- [ ] PRD에 명시된 기능만 구현했는가?
- [ ] 에러 케이스 처리가 되어 있는가?
- [ ] 테스트가 작성되어 있는가?

## 배포 전 검증
- [ ] 모든 테스트가 통과하는가?
- [ ] lint 에러가 없는가?
- [ ] 빌드가 성공하는가?
""")]


async def get_setup_guide(platform: str) -> list[TextContent]:
    """설정 가이드"""
    guides = {
        "desktop": """## Claude Desktop 설정

1. 설정 파일 열기: `%APPDATA%\\Claude\\claude_desktop_config.json`
2. 아래 내용 추가:

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

3. Claude Desktop 재시작
""",
        "code": """## Claude Code (CLI) 설정

```bash
# 자동 설정
clouvel init

# 또는 수동
clouvel init -p /path/to/project -l strict
```
""",
        "vscode": """## VS Code 설정

1. 확장 탭에서 "Clouvel" 검색
2. 설치
3. Command Palette (Ctrl+Shift+P) → "Clouvel: Setup MCP Server"
""",
        "cursor": """## Cursor 설정

VS Code와 동일합니다. "Clouvel" 확장을 설치하세요.
""",
    }

    if platform == "all":
        result = "# Clouvel 설정 가이드\n\n"
        for p, g in guides.items():
            result += g + "\n---\n\n"
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=guides.get(platform, "알 수 없는 플랫폼입니다."))]
