# -*- coding: utf-8 -*-
"""
Clouvel MCP Server v1.2.0
바이브코딩 프로세스를 강제하는 MCP 서버

v1.2 신규 도구:
- start: 프로젝트 온보딩 + PRD 강제 (Free)
- manager: 8명 C-Level 매니저 협업 피드백 (Pro)
- ship: 원클릭 테스트→검증→증거 생성 (Pro)

Free 버전 - Pro 기능은 clouvel-pro 패키지 참조
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .analytics import log_tool_call, get_stats, format_stats
from .tools import (
    # core
    can_code, scan_docs, analyze_docs, init_docs, REQUIRED_DOCS,
    # docs
    get_prd_template, list_templates, write_prd_section, get_prd_guide, get_verify_checklist, get_setup_guide,
    # setup
    init_clouvel, setup_cli,
    # rules (v0.5)
    init_rules, get_rule, add_rule,
    # verify (v0.5)
    verify, gate, handoff,
    # planning (v0.6)
    init_planning, save_finding, refresh_goals, update_progress,
    # agents (v0.7)
    spawn_explore, spawn_librarian,
    # hooks (v0.8)
    hook_design, hook_verify,
    # start (Free, v1.2)
    start, quick_start,
    # manager (Pro, v1.2)
    manager, ask_manager, list_managers, MANAGERS,
    # ship (Pro, v1.2)
    ship, quick_ship, full_ship,
)

server = Server("clouvel")


# ============================================================
# Tool Definitions (Free - v0.8까지)
# ============================================================

TOOL_DEFINITIONS = [
    # === Core Tools ===
    Tool(
        name="can_code",
        description="코드 작성 전 반드시 호출. 문서 상태 확인 후 코딩 가능 여부 판단.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "프로젝트 docs 폴더 경로"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="scan_docs",
        description="프로젝트 docs 폴더 스캔. 파일 목록 반환.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs 폴더 경로"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="analyze_docs",
        description="docs 폴더 분석. 필수 문서 체크.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs 폴더 경로"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="init_docs",
        description="docs 폴더 초기화 + 템플릿 생성.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "project_name": {"type": "string", "description": "프로젝트 이름"}
            },
            "required": ["path", "project_name"]
        }
    ),

    # === Docs Tools ===
    Tool(
        name="get_prd_template",
        description="PRD 템플릿 생성. 템플릿과 레이아웃 선택 가능.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "프로젝트 이름"},
                "output_path": {"type": "string", "description": "출력 경로"},
                "template": {"type": "string", "enum": ["web-app", "api", "cli", "generic"], "description": "템플릿 종류"},
                "layout": {"type": "string", "enum": ["lite", "standard", "detailed"], "description": "레이아웃 (분량)"}
            },
            "required": ["project_name", "output_path"]
        }
    ),
    Tool(
        name="list_templates",
        description="사용 가능한 PRD 템플릿 목록 조회.",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="write_prd_section",
        description="PRD 섹션별 작성 가이드.",
        inputSchema={
            "type": "object",
            "properties": {
                "section": {"type": "string", "enum": ["summary", "principles", "input_spec", "output_spec", "errors", "state_machine", "api_endpoints", "db_schema"]},
                "content": {"type": "string", "description": "섹션 내용"}
            },
            "required": ["section"]
        }
    ),
    Tool(name="get_prd_guide", description="PRD 작성 가이드.", inputSchema={"type": "object", "properties": {}}),
    Tool(name="get_verify_checklist", description="검증 체크리스트.", inputSchema={"type": "object", "properties": {}}),
    Tool(
        name="get_setup_guide",
        description="설치/설정 가이드.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "code", "vscode", "cursor", "all"]}}
        }
    ),
    Tool(
        name="get_analytics",
        description="도구 사용량 통계.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 경로"},
                "days": {"type": "integer", "description": "조회 기간 (기본: 30일)"}
            }
        }
    ),

    # === Setup Tools ===
    Tool(
        name="init_clouvel",
        description="Clouvel 온보딩. 플랫폼 선택 후 맞춤 설정.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "vscode", "cli", "ask"]}}
        }
    ),
    Tool(
        name="setup_cli",
        description="CLI 환경 설정. hooks, CLAUDE.md, pre-commit 생성.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "level": {"type": "string", "enum": ["remind", "strict", "full"]}
            },
            "required": ["path"]
        }
    ),

    # === Rules Tools (v0.5) ===
    Tool(
        name="init_rules",
        description="v0.5: 규칙 모듈화 초기화.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "template": {"type": "string", "enum": ["web", "api", "fullstack", "minimal"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="get_rule",
        description="v0.5: 경로 기반 규칙 로딩.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "파일 경로"},
                "context": {"type": "string", "enum": ["coding", "review", "debug", "test"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="add_rule",
        description="v0.5: 새 규칙 추가.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "rule_type": {"type": "string", "enum": ["never", "always", "prefer"]},
                "content": {"type": "string", "description": "규칙 내용"},
                "category": {"type": "string", "enum": ["api", "frontend", "database", "security", "general"]}
            },
            "required": ["path", "rule_type", "content"]
        }
    ),

    # === Verify Tools (v0.5) ===
    Tool(
        name="verify",
        description="v0.5: Context Bias 제거 검증.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "검증 대상 경로"},
                "scope": {"type": "string", "enum": ["file", "feature", "full"]},
                "checklist": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="gate",
        description="v0.5: lint → test → build 자동화.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "steps": {"type": "array", "items": {"type": "string"}},
                "fix": {"type": "boolean"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="handoff",
        description="v0.5: 의도 기록.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "feature": {"type": "string", "description": "완료한 기능"},
                "decisions": {"type": "string"},
                "warnings": {"type": "string"},
                "next_steps": {"type": "string"}
            },
            "required": ["path", "feature"]
        }
    ),

    # === Planning Tools (v0.6) ===
    Tool(
        name="init_planning",
        description="v0.6: 영속적 컨텍스트 초기화.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "task": {"type": "string", "description": "현재 작업"},
                "goals": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path", "task"]
        }
    ),
    Tool(
        name="save_finding",
        description="v0.6: 조사 결과 저장.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "topic": {"type": "string"},
                "question": {"type": "string"},
                "findings": {"type": "string"},
                "source": {"type": "string"},
                "conclusion": {"type": "string"}
            },
            "required": ["path", "topic", "findings"]
        }
    ),
    Tool(
        name="refresh_goals",
        description="v0.6: 목표 리마인드.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "프로젝트 루트 경로"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="update_progress",
        description="v0.6: 진행 상황 업데이트.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "completed": {"type": "array", "items": {"type": "string"}},
                "in_progress": {"type": "string"},
                "blockers": {"type": "array", "items": {"type": "string"}},
                "next": {"type": "string"}
            },
            "required": ["path"]
        }
    ),

    # === Agent Tools (v0.7) ===
    Tool(
        name="spawn_explore",
        description="v0.7: 탐색 전문 에이전트.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "query": {"type": "string", "description": "탐색 질문"},
                "scope": {"type": "string", "enum": ["file", "folder", "project", "deep"]},
                "save_findings": {"type": "boolean"}
            },
            "required": ["path", "query"]
        }
    ),
    Tool(
        name="spawn_librarian",
        description="v0.7: 라이브러리언 에이전트.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "topic": {"type": "string", "description": "조사 주제"},
                "type": {"type": "string", "enum": ["library", "api", "migration", "best_practice"]},
                "depth": {"type": "string", "enum": ["quick", "standard", "thorough"]}
            },
            "required": ["path", "topic"]
        }
    ),

    # === Hook Tools (v0.8) ===
    Tool(
        name="hook_design",
        description="v0.8: 설계 훅 생성.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "trigger": {"type": "string", "enum": ["pre_code", "pre_feature", "pre_refactor", "pre_api"]},
                "checks": {"type": "array", "items": {"type": "string"}},
                "block_on_fail": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),
    Tool(
        name="hook_verify",
        description="v0.8: 검증 훅 생성.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "trigger": {"type": "string", "enum": ["post_code", "post_feature", "pre_commit", "pre_push"]},
                "steps": {"type": "array", "items": {"type": "string"}},
                "parallel": {"type": "boolean"},
                "continue_on_error": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),

    # === Start Tool (Free, v1.2) ===
    Tool(
        name="start",
        description="프로젝트 온보딩. PRD 체크 및 생성, 다음 단계 안내. (Free)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "project_name": {"type": "string", "description": "프로젝트 이름 (선택)"}
            },
            "required": ["path"]
        }
    ),

    # === Manager Tool (Pro, v1.2) ===
    Tool(
        name="manager",
        description="8명 C-Level 매니저의 컨텍스트 기반 협업 피드백. PM/CTO/QA/CDO/CMO/CFO/CSO/Error. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "검토할 내용 (플랜, 코드, 질문 등)"},
                "mode": {"type": "string", "enum": ["auto", "all", "specific"], "description": "매니저 선택 모드"},
                "managers": {"type": "array", "items": {"type": "string"}, "description": "mode=specific일 때 매니저 목록"},
                "include_checklist": {"type": "boolean", "description": "체크리스트 포함 여부"}
            },
            "required": ["context"]
        }
    ),
    Tool(
        name="list_managers",
        description="사용 가능한 매니저 목록 조회. (Pro)",
        inputSchema={"type": "object", "properties": {}}
    ),

    # === Ship Tool (Pro, v1.2) ===
    Tool(
        name="ship",
        description="원클릭 테스트→검증→증거 생성. lint/typecheck/test/build 순차 실행. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "feature": {"type": "string", "description": "검증할 기능명 (선택)"},
                "steps": {"type": "array", "items": {"type": "string"}, "description": "실행할 단계 ['lint', 'typecheck', 'test', 'build']"},
                "generate_evidence": {"type": "boolean", "description": "증거 파일 생성 여부"},
                "auto_fix": {"type": "boolean", "description": "lint 에러 자동 수정 시도"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="quick_ship",
        description="빠른 ship - lint와 test만 실행. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "feature": {"type": "string", "description": "검증할 기능명 (선택)"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="full_ship",
        description="전체 ship - 모든 검증 단계 + 자동 수정. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "프로젝트 루트 경로"},
                "feature": {"type": "string", "description": "검증할 기능명 (선택)"}
            },
            "required": ["path"]
        }
    ),

    # === Pro 안내 ===
    Tool(
        name="upgrade_pro",
        description="Clouvel Pro 안내. Shovel 자동 설치, Error Learning 등.",
        inputSchema={"type": "object", "properties": {}}
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOL_DEFINITIONS


# ============================================================
# Tool Handlers
# ============================================================

TOOL_HANDLERS = {
    # Core
    "can_code": lambda args: can_code(args.get("path", "")),
    "scan_docs": lambda args: scan_docs(args.get("path", "")),
    "analyze_docs": lambda args: analyze_docs(args.get("path", "")),
    "init_docs": lambda args: init_docs(args.get("path", ""), args.get("project_name", "")),

    # Docs
    "get_prd_template": lambda args: get_prd_template(args.get("project_name", ""), args.get("output_path", ""), args.get("template", "generic"), args.get("layout", "standard")),
    "list_templates": lambda args: list_templates(),
    "write_prd_section": lambda args: write_prd_section(args.get("section", ""), args.get("content", "")),
    "get_prd_guide": lambda args: get_prd_guide(),
    "get_verify_checklist": lambda args: get_verify_checklist(),
    "get_setup_guide": lambda args: get_setup_guide(args.get("platform", "all")),

    # Setup
    "init_clouvel": lambda args: init_clouvel(args.get("platform", "ask")),
    "setup_cli": lambda args: setup_cli(args.get("path", ""), args.get("level", "remind")),

    # Rules (v0.5)
    "init_rules": lambda args: init_rules(args.get("path", ""), args.get("template", "minimal")),
    "get_rule": lambda args: get_rule(args.get("path", ""), args.get("context", "coding")),
    "add_rule": lambda args: add_rule(args.get("path", ""), args.get("rule_type", "always"), args.get("content", ""), args.get("category", "general")),

    # Verify (v0.5)
    "verify": lambda args: verify(args.get("path", ""), args.get("scope", "file"), args.get("checklist", [])),
    "gate": lambda args: gate(args.get("path", ""), args.get("steps", ["lint", "test", "build"]), args.get("fix", False)),
    "handoff": lambda args: handoff(args.get("path", ""), args.get("feature", ""), args.get("decisions", ""), args.get("warnings", ""), args.get("next_steps", "")),

    # Planning (v0.6)
    "init_planning": lambda args: init_planning(args.get("path", ""), args.get("task", ""), args.get("goals", [])),
    "save_finding": lambda args: save_finding(args.get("path", ""), args.get("topic", ""), args.get("question", ""), args.get("findings", ""), args.get("source", ""), args.get("conclusion", "")),
    "refresh_goals": lambda args: refresh_goals(args.get("path", "")),
    "update_progress": lambda args: update_progress(args.get("path", ""), args.get("completed", []), args.get("in_progress", ""), args.get("blockers", []), args.get("next", "")),

    # Agents (v0.7)
    "spawn_explore": lambda args: spawn_explore(args.get("path", ""), args.get("query", ""), args.get("scope", "project"), args.get("save_findings", True)),
    "spawn_librarian": lambda args: spawn_librarian(args.get("path", ""), args.get("topic", ""), args.get("type", "library"), args.get("depth", "standard")),

    # Hooks (v0.8)
    "hook_design": lambda args: hook_design(args.get("path", ""), args.get("trigger", "pre_code"), args.get("checks", []), args.get("block_on_fail", True)),
    "hook_verify": lambda args: hook_verify(args.get("path", ""), args.get("trigger", "post_code"), args.get("steps", ["lint", "test", "build"]), args.get("parallel", False), args.get("continue_on_error", False)),

    # Start (Free, v1.2)
    "start": lambda args: _wrap_start(args),

    # Manager (Pro, v1.2)
    "manager": lambda args: _wrap_manager(args),
    "list_managers": lambda args: _wrap_list_managers(),

    # Ship (Pro, v1.2)
    "ship": lambda args: _wrap_ship(args),
    "quick_ship": lambda args: _wrap_quick_ship(args),
    "full_ship": lambda args: _wrap_full_ship(args),

    # Pro 안내
    "upgrade_pro": lambda args: _upgrade_pro(),
}


async def _wrap_start(args: dict) -> list[TextContent]:
    """start 도구 래퍼"""
    import json
    result = start(args.get("path", ""), args.get("project_name", ""))
    # formatted 출력이 있으면 사용, 없으면 JSON
    if isinstance(result, dict):
        output = f"""# 🚀 Start

**상태**: {result.get('status', 'UNKNOWN')}
**프로젝트**: {result.get('project_name', 'N/A')}

{result.get('message', '')}

## 다음 단계
"""
        for step in result.get('next_steps', []):
            output += f"- {step}\n"

        if result.get('created_files'):
            output += "\n## 생성된 파일\n"
            for f in result['created_files']:
                output += f"- {f}\n"

        return [TextContent(type="text", text=output)]
    return [TextContent(type="text", text=str(result))]


async def _wrap_manager(args: dict) -> list[TextContent]:
    """manager 도구 래퍼"""
    result = manager(
        context=args.get("context", ""),
        mode=args.get("mode", "auto"),
        managers=args.get("managers", None),
        include_checklist=args.get("include_checklist", True)
    )
    # formatted_output 사용
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _wrap_list_managers() -> list[TextContent]:
    """list_managers 도구 래퍼"""
    managers_list = list_managers()
    output = "# 👔 사용 가능한 매니저 (8명)\n\n"
    for m in managers_list:
        output += f"- **{m['emoji']} {m['key']}** ({m['title']}): {m['focus']}\n"
    return [TextContent(type="text", text=output)]


async def _wrap_ship(args: dict) -> list[TextContent]:
    """ship 도구 래퍼"""
    result = ship(
        path=args.get("path", ""),
        feature=args.get("feature", ""),
        steps=args.get("steps", None),
        generate_evidence=args.get("generate_evidence", True),
        auto_fix=args.get("auto_fix", False)
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _wrap_quick_ship(args: dict) -> list[TextContent]:
    """quick_ship 도구 래퍼"""
    result = quick_ship(
        path=args.get("path", ""),
        feature=args.get("feature", "")
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _wrap_full_ship(args: dict) -> list[TextContent]:
    """full_ship 도구 래퍼"""
    result = full_ship(
        path=args.get("path", ""),
        feature=args.get("feature", "")
    )
    if isinstance(result, dict) and result.get("formatted_output"):
        return [TextContent(type="text", text=result["formatted_output"])]
    return [TextContent(type="text", text=str(result))]


async def _upgrade_pro() -> list[TextContent]:
    """Pro 업그레이드 안내"""
    return [TextContent(type="text", text="""
# Clouvel Pro

더 강력한 기능이 필요하다면 Clouvel Pro를 확인하세요.

## Pro 기능

### Shovel 자동 설치
- `.claude/` 워크플로우 구조 자동 생성
- 슬래시 커맨드 (/start, /plan, /gate...)
- 설정 파일 + 템플릿

### Error Learning
- 에러 패턴 자동 분류
- 방지 규칙 자동 생성
- 로그 파일 모니터링

### 커맨드 동기화
- Shovel 커맨드 업데이트

## 가격

| 티어 | 가격 | 인원 |
|------|------|------|
| Personal | $29 | 1명 |
| Team | $79 | 10명 |
| Enterprise | $199 | 무제한 |

## 구매

https://clouvel.lemonsqueezy.com

## 설치

```bash
pip install clouvel-pro
```
""")]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Analytics 기록
    project_path = arguments.get("path", None)
    if name != "get_analytics":
        try:
            log_tool_call(name, success=True, project_path=project_path)
        except Exception:
            pass

    # get_analytics 특별 처리
    if name == "get_analytics":
        return await _get_analytics(arguments.get("path", None), arguments.get("days", 30))

    # 핸들러 실행
    handler = TOOL_HANDLERS.get(name)
    if handler:
        return await handler(arguments)

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _get_analytics(path: str, days: int) -> list[TextContent]:
    """도구 사용량 통계"""
    stats = get_stats(days=days, project_path=path)
    return [TextContent(type="text", text=format_stats(stats))]


# ============================================================
# Server Entry Points
# ============================================================

async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _run_setup(global_only: bool = False) -> str:
    """B0: clouvel setup - 강제 호출 메커니즘 설치"""
    import subprocess
    import os
    from pathlib import Path

    results = []

    # 1. 글로벌 CLAUDE.md에 규칙 추가
    if os.name == 'nt':  # Windows
        claude_dir = Path.home() / ".claude"
    else:  # Mac/Linux
        claude_dir = Path.home() / ".claude"

    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_md_path = claude_dir / "CLAUDE.md"

    clouvel_rule = """
## Clouvel 규칙 (자동 생성)

**코드 작성 전 반드시 clouvel의 `can_code` 도구 호출 필수.**

- 코드를 작성(Edit/Write)하기 전에 항상 `can_code` 도구를 먼저 호출하세요
- path 인자로 프로젝트의 docs 폴더 경로를 전달하세요
- BLOCK이 뜨면 코드 작성 금지, 사용자에게 문서 작성 안내
- PASS가 뜨면 코딩 진행 가능
- WARN은 권장 사항, 진행 가능하지만 권장 문서 추가 안내

"""

    marker = "## Clouvel 규칙"

    if claude_md_path.exists():
        content = claude_md_path.read_text(encoding='utf-8')
        if marker in content:
            results.append("[OK] 글로벌 CLAUDE.md: 이미 Clouvel 규칙 있음")
        else:
            # 기존 내용 끝에 추가
            new_content = content.rstrip() + "\n\n---\n" + clouvel_rule
            claude_md_path.write_text(new_content, encoding='utf-8')
            results.append(f"[OK] 글로벌 CLAUDE.md: 규칙 추가됨 ({claude_md_path})")
    else:
        # 새로 생성
        initial_content = f"# Claude Code 글로벌 설정\n\n> 자동 생성됨 by clouvel setup\n\n---\n{clouvel_rule}"
        claude_md_path.write_text(initial_content, encoding='utf-8')
        results.append(f"[OK] 글로벌 CLAUDE.md: 생성됨 ({claude_md_path})")

    # 2. MCP 서버 등록 (global_only가 아닐 때만)
    if not global_only:
        try:
            # 먼저 기존 등록 확인
            check_result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "clouvel" in check_result.stdout:
                results.append("[OK] MCP 서버: 이미 등록됨")
            else:
                # 등록
                add_result = subprocess.run(
                    ["claude", "mcp", "add", "clouvel", "-s", "user", "--", "clouvel"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if add_result.returncode == 0:
                    results.append("[OK] MCP 서버: 등록 완료")
                else:
                    results.append(f"[WARN] MCP 서버: 등록 실패 - {add_result.stderr.strip()}")
                    results.append("   수동 등록: claude mcp add clouvel -s user -- clouvel")
        except FileNotFoundError:
            results.append("[WARN] MCP 서버: claude 명령어 없음")
            results.append("   Claude Code 설치 후 다시 실행하세요")
        except subprocess.TimeoutExpired:
            results.append("[WARN] MCP 서버: 타임아웃")
            results.append("   수동 등록: claude mcp add clouvel -s user -- clouvel")
        except Exception as e:
            results.append(f"[WARN] MCP 서버: 오류 - {str(e)}")
            results.append("   수동 등록: claude mcp add clouvel -s user -- clouvel")

    # 결과 출력
    output = """
================================================================
                    Clouvel Setup 완료
================================================================

"""
    output += "\n".join(results)
    output += """

----------------------------------------------------------------

## 작동 방식

1. Claude Code 실행
2. "로그인 기능 만들어줘" 요청
3. Claude가 자동으로 can_code 먼저 호출
4. PRD 없으면 → [BLOCK] BLOCK (코딩 금지)
5. PRD 있으면 → [OK] PASS (코딩 진행)

## 테스트

```bash
# PRD 없는 폴더에서 테스트
mkdir test-project && cd test-project
claude
> "코드 짜줘"
# → BLOCK 메시지 확인
```

----------------------------------------------------------------
"""

    return output


def main():
    import sys
    import asyncio
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Clouvel - 바이브코딩 프로세스 강제 도구")
    subparsers = parser.add_subparsers(dest="command")

    # init 명령
    init_parser = subparsers.add_parser("init", help="프로젝트 초기화")
    init_parser.add_argument("-p", "--path", default=".", help="프로젝트 경로")
    init_parser.add_argument("-l", "--level", choices=["remind", "strict", "full"], default="strict")

    # setup 명령 (B0) - 레거시, install 권장
    setup_parser = subparsers.add_parser("setup", help="Clouvel 강제 호출 메커니즘 설치 (글로벌)")
    setup_parser.add_argument("--global-only", action="store_true", help="CLAUDE.md만 설정 (MCP 등록 제외)")

    # install 명령 (신규, 권장)
    install_parser = subparsers.add_parser("install", help="Clouvel MCP 서버 설치 (권장)")
    install_parser.add_argument("--platform", choices=["auto", "code", "desktop", "cursor", "all"], default="auto", help="설치 대상 플랫폼")
    install_parser.add_argument("--force", action="store_true", help="이미 설치되어 있어도 재설치")

    # activate 명령 (라이센스 활성화)
    activate_parser = subparsers.add_parser("activate", help="라이선스 활성화")
    activate_parser.add_argument("license_key", help="라이선스 키")

    # status 명령 (라이센스 상태)
    status_parser = subparsers.add_parser("status", help="라이선스 상태 확인")

    # deactivate 명령 (라이센스 비활성화)
    deactivate_parser = subparsers.add_parser("deactivate", help="라이선스 비활성화 (로컬 캐시 삭제)")

    args = parser.parse_args()

    if args.command == "init":
        from .tools.setup import setup_cli as sync_setup
        import asyncio
        result = asyncio.run(sync_setup(args.path, args.level))
        print(result[0].text)
    elif args.command == "setup":
        result = _run_setup(global_only=args.global_only if hasattr(args, 'global_only') else False)
        print(result)
    elif args.command == "install":
        from .tools.install import run_install
        result = run_install(
            platform=args.platform if hasattr(args, 'platform') else "auto",
            force=args.force if hasattr(args, 'force') else False
        )
        print(result)
    elif args.command == "activate":
        try:
            from .license import activate_license_cli
            result = activate_license_cli(args.license_key)
            if result["success"]:
                print(f"""
================================================================
              Clouvel Pro 라이선스 활성화 완료
================================================================

{result['message']}

티어: {result.get('tier_info', {}).get('name', 'Unknown')}
기기: {result.get('machine_id', 'Unknown')[:8]}...
상품: {result.get('product', 'Clouvel Pro')}

----------------------------------------------------------------
프리미엄 기능은 활성화 후 7일이 지나야 사용할 수 있습니다.
'clouvel status'로 상태를 확인하세요.
================================================================
""")
            else:
                print(result["message"])
                sys.exit(1)
        except ImportError:
            print("""
================================================================
                   Clouvel Pro 필요
================================================================

이 기능은 Clouvel Pro에서만 사용할 수 있습니다.

구매: https://clouvel.lemonsqueezy.com
================================================================
""")
            sys.exit(1)
    elif args.command == "status":
        try:
            from .license import get_license_status
            result = get_license_status()
            if result.get("has_license"):
                tier_info = result.get("tier_info", {})
                unlock_status = "✅ 해제됨" if result.get("premium_unlocked") else f"⏳ {result.get('premium_unlock_remaining', '?')}일 남음"
                print(f"""
================================================================
                   Clouvel 라이선스 상태
================================================================

상태: ✅ 활성화됨
티어: {tier_info.get('name', 'Unknown')} ({tier_info.get('price', '?')})
기기: {result.get('machine_id', 'Unknown')[:8]}...

활성화 일시: {result.get('activated_at', 'N/A')[:19]}
경과 일수: {result.get('days_since_activation', 0)}일
프리미엄 기능: {unlock_status}

================================================================
""")
            else:
                print(f"""
================================================================
                   Clouvel 라이선스 상태
================================================================

상태: ❌ 미활성화

{result.get('message', '')}

구매: https://clouvel.lemonsqueezy.com
================================================================
""")
        except ImportError:
            print("""
================================================================
                   Clouvel Free 버전
================================================================

Pro 라이선스 기능은 Clouvel Pro에서만 사용할 수 있습니다.

구매: https://clouvel.lemonsqueezy.com
================================================================
""")
    elif args.command == "deactivate":
        try:
            from .license import deactivate_license_cli
            result = deactivate_license_cli()
            print(result["message"])
            if not result["success"]:
                sys.exit(1)
        except ImportError:
            print("Clouvel Pro 필요: https://clouvel.lemonsqueezy.com")
            sys.exit(1)
    else:
        asyncio.run(run_server())


if __name__ == "__main__":
    main()
