# Entrypoints

> Clouvel Architecture Documentation
> 이 파일의 AUTO-GEN 섹션은 자동 생성됩니다. 수동 수정은 마커 밖에서 하세요.

---

## Summary

Clouvel은 3가지 진입점을 통해 실행됩니다:

1. **CLI**: `clouvel` 명령어 (PyPI 설치)
2. **MCP Server**: Claude Code에서 MCP 도구로 호출
3. **Packaging**: hatch 빌드 시스템

---

## (A) CLI Entrypoint

| 항목 | 값 | Evidence |
|------|-----|----------|
| Console Script | `clouvel` | `pyproject.toml:58` |
| Python Entry | `clouvel:main` | `pyproject.toml:58` |
| Import Chain | `__init__.py` → `server.py:main()` | `__init__.py:1-3`, `server.py:1896` |

### CLI Commands

| Command | Function | File:Line |
|---------|----------|-----------|
| (none) | MCP 서버 실행 | `server.py:2023` `asyncio.run(run_server())` |
| `init` | 프로젝트 초기화 | `server.py:1933-1936` |
| `setup` | 전역 설정 설치 | `server.py:1938-1942` |
| `install` | MCP 서버 등록 | `server.py:1944-1949` |
| `activate` | 라이선스 활성화 | `server.py:1951-1975` |
| `status` | 라이선스 상태 | `server.py:1977-2012` |
| `deactivate` | 라이선스 해제 | `server.py:2013-2021` |

### Evidence

```python
# pyproject.toml:57-58
[project.scripts]
clouvel = "clouvel:main"

# __init__.py:1-3
from .server import main
__all__ = ["main"]

# server.py:1896
def main():
    # ...
    asyncio.run(run_server())  # 2023
```

---

## (B) MCP Server Entrypoint

| 항목 | 값 | Evidence |
|------|-----|----------|
| Server Instance | `server = Server("clouvel")` | `server.py:69` |
| List Tools | `@server.list_tools()` | `server.py:756-758` |
| Call Tool | `@server.call_tool()` | `server.py:1589-1627` |
| Run Server | `async def run_server()` | `server.py:1640-1642` |

### Tool Registration Flow

```
TOOL_DEFINITIONS (79-753) → list_tools() (756-758)
                          ↓
TOOL_HANDLERS (765-853) → call_tool() (1589-1627)
```

### Evidence

```python
# server.py:69
server = Server("clouvel")

# server.py:756-758
@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOL_DEFINITIONS

# server.py:1589-1627
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if handler:
        result = await handler(arguments)
        return result
    return [TextContent(type="text", text=f"Unknown tool: {name}")]
```

---

## (C) Packaging Entrypoint

| 항목 | 값 | Evidence |
|------|-----|----------|
| Build System | `hatchling` | `pyproject.toml:2-3` |
| Package Dir | `src/clouvel` | `pyproject.toml:66` |
| Excluded Files | `license.py`, `ship_pro.py`, `tools/manager/` | `pyproject.toml:76-80` |

### Build Exclusions (Critical for Runtime Paths)

| File/Dir | Reason | Impact |
|----------|--------|--------|
| `license.py` | Pro 라이선스 검증 | PyPI: `license_free.py` 사용 |
| `tools/ship_pro.py` | Ship 구현 | PyPI: API 권한만 체크 후 실패 |
| `tools/manager/` | Manager 구현 | PyPI: Worker API 경유 필수 |

### Evidence

```toml
# pyproject.toml:74-80
[tool.hatch.build]
artifacts = ["src/clouvel/templates/**/*.md"]
exclude = [
    "src/clouvel/license.py",
    "src/clouvel/tools/ship_pro.py",
    "src/clouvel/tools/manager/",
]
```

---

## (D) Import Fallback Chain

PyPI 설치 시 Pro 모듈이 없으면 fallback 발생:

### License Module

```
server.py:62-66
try:
    from .license import activate_license_cli, get_license_status
except ImportError:
    from .license_free import activate_license_cli, get_license_status
```

### Manager Module

```
tools/__init__.py:88-118
try:
    from .manager import (manager, ...)
    _HAS_MANAGER = True
except ImportError as e:
    _HAS_MANAGER = False
    def manager(*args, **kwargs):
        return {"error": f"Manager module not available: ..."}
```

But **server.py** bypasses this via direct API call:

```python
# server.py:19
from .api_client import call_manager_api

# server.py:1194-1210
async def _wrap_manager(args: dict) -> list[TextContent]:
    result = call_manager_api(...)  # Always goes to Worker API
```

---

<!-- AUTO-GEN:START -->
## Entrypoints (Auto-Generated)

_Auto-generated: 2026-01-26 19:44_

### CLI Commands

| File | Line | Command |
|------|------|---------|
| `src\clouvel\pro_downloader.py` | 414 | `install_parser = subparsers.add_parser("install", help="Pro ...` |
| `src\clouvel\pro_downloader.py` | 415 | `install_parser.add_argument("--module", "-m", help="특정 모듈만 설...` |
| `src\clouvel\pro_downloader.py` | 416 | `install_parser.add_argument("--version", "-v", help="버전 지정")` |
| `src\clouvel\pro_downloader.py` | 419 | `status_parser = subparsers.add_parser("status", help="설치 상태 ...` |
| `src\clouvel\server.py` | 1906 | `init_parser = subparsers.add_parser("init", help="Initialize...` |
| `src\clouvel\server.py` | 1907 | `init_parser.add_argument("-p", "--path", default=".", help="...` |
| `src\clouvel\server.py` | 1908 | `init_parser.add_argument("-l", "--level", choices=["remind",...` |
| `src\clouvel\server.py` | 1911 | `setup_parser = subparsers.add_parser("setup", help="Install ...` |
| `src\clouvel\server.py` | 1912 | `setup_parser.add_argument("--global-only", action="store_tru...` |
| `src\clouvel\server.py` | 1913 | `setup_parser.add_argument("--hooks", action="store_true", he...` |

### MCP Tools

| File | Line | Tool |
|------|------|------|
| `src\clouvel\server.py` | 156 | `Tool(name="get_prd_guide", description="PRD writing guide.",...` |
| `src\clouvel\server.py` | 157 | `Tool(name="get_verify_checklist", description="Verification ...` |

### MCP Handlers

| File | Line | Handler |
|------|------|---------|
| `src\clouvel\server.py` | 767 | `"can_code": lambda args: can_code(args.get("path", ""), args...` |
| `src\clouvel\server.py` | 768 | `"scan_docs": lambda args: scan_docs(args.get("path", "")),` |
| `src\clouvel\server.py` | 769 | `"analyze_docs": lambda args: analyze_docs(args.get("path", "...` |
| `src\clouvel\server.py` | 770 | `"init_docs": lambda args: init_docs(args.get("path", ""), ar...` |
| `src\clouvel\server.py` | 773 | `"get_prd_template": lambda args: get_prd_template(args.get("...` |
| `src\clouvel\server.py` | 774 | `"list_templates": lambda args: list_templates(),` |
| `src\clouvel\server.py` | 775 | `"write_prd_section": lambda args: write_prd_section(args.get...` |
| `src\clouvel\server.py` | 776 | `"get_prd_guide": lambda args: get_prd_guide(),` |
| `src\clouvel\server.py` | 777 | `"get_verify_checklist": lambda args: get_verify_checklist(),` |
| `src\clouvel\server.py` | 778 | `"get_setup_guide": lambda args: get_setup_guide(args.get("pl...` |
| `src\clouvel\server.py` | 781 | `"init_clouvel": lambda args: init_clouvel(args.get("platform...` |
| `src\clouvel\server.py` | 782 | `"setup_cli": lambda args: setup_cli(args.get("path", ""), ar...` |
| `src\clouvel\server.py` | 785 | `"init_rules": lambda args: init_rules(args.get("path", ""), ...` |
| `src\clouvel\server.py` | 786 | `"get_rule": lambda args: get_rule(args.get("path", ""), args...` |
| `src\clouvel\server.py` | 787 | `"add_rule": lambda args: add_rule(args.get("path", ""), args...` |
| `src\clouvel\server.py` | 790 | `"verify": lambda args: verify(args.get("path", ""), args.get...` |
| `src\clouvel\server.py` | 791 | `"gate": lambda args: gate(args.get("path", ""), args.get("st...` |
| `src\clouvel\server.py` | 792 | `"handoff": lambda args: handoff(args.get("path", ""), args.g...` |
| `src\clouvel\server.py` | 795 | `"init_planning": lambda args: init_planning(args.get("path",...` |
| `src\clouvel\server.py` | 796 | `"plan": lambda args: create_detailed_plan(args.get("path", "...` |
| `src\clouvel\server.py` | 797 | `"save_finding": lambda args: save_finding(args.get("path", "...` |
| `src\clouvel\server.py` | 798 | `"refresh_goals": lambda args: refresh_goals(args.get("path",...` |
| `src\clouvel\server.py` | 799 | `"update_progress": lambda args: update_progress(args.get("pa...` |
| `src\clouvel\server.py` | 802 | `"spawn_explore": lambda args: spawn_explore(args.get("path",...` |
| `src\clouvel\server.py` | 803 | `"spawn_librarian": lambda args: spawn_librarian(args.get("pa...` |
| `src\clouvel\server.py` | 806 | `"hook_design": lambda args: hook_design(args.get("path", "")...` |
| `src\clouvel\server.py` | 807 | `"hook_verify": lambda args: hook_verify(args.get("path", "")...` |
| `src\clouvel\server.py` | 810 | `"start": lambda args: _wrap_start(args),` |
| `src\clouvel\server.py` | 811 | `"save_prd": lambda args: _wrap_save_prd(args),` |
| `src\clouvel\server.py` | 814 | `"record_decision": lambda args: _wrap_record_decision(args),` |

<!-- AUTO-GEN:END -->

---

## Manual Notes

### Do Next (Red Volkswagen)

- **코드 추가 시**: 새 CLI 명령은 `server.py:main()` argparse에 추가
- **새 MCP 도구 추가 시**: `TOOL_DEFINITIONS`에 Tool 정의 + `TOOL_HANDLERS`에 핸들러 추가
- **빌드 제외 파일 추가 시**: `pyproject.toml` exclude 배열에 추가 + fallback 로직 확인
