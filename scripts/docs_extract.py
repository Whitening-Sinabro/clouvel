#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clouvel Documentation Extractor

자동으로 코드베이스를 스캔하여 문서 초안을 생성/갱신합니다.

사용법:
    python scripts/docs_extract.py

출력:
    - docs/architecture/MODULE_MAP.md (모듈/파일 목록)
    - docs/architecture/DATA_CONTRACTS.md (HTTP 호출, API 엔드포인트)
    - docs/architecture/RUNTIME_PATHS.md (조건 분기, 런타임 경로)
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "clouvel"
DOCS_DIR = PROJECT_ROOT / "docs" / "architecture"

# AUTO-GEN 마커
AUTO_START = "<!-- AUTO-GEN:START -->"
AUTO_END = "<!-- AUTO-GEN:END -->"


def run_grep(pattern: str, path: str = "src/clouvel", flags: str = "-rn") -> List[Tuple[str, int, str]]:
    """ripgrep 또는 grep 실행하여 결과 반환"""
    results = []
    output = ""

    # Python glob 기반 검색 (Windows 호환)
    search_path = PROJECT_ROOT / path
    if search_path.exists():
        for py_file in search_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                for i, line in enumerate(content.split("\n"), 1):
                    if re.search(pattern, line):
                        rel_path = py_file.relative_to(PROJECT_ROOT)
                        output += f"{rel_path}:{i}:{line}\n"
            except Exception:
                pass

    if not output:
        return results

    for line in output.strip().split("\n"):
        if not line:
            continue
        parts = line.split(":", 2)
        if len(parts) >= 3:
            file_path = parts[0]
            try:
                line_num = int(parts[1])
            except ValueError:
                continue
            content = parts[2] if len(parts) > 2 else ""
            # 프로젝트 루트 기준 상대 경로로 변환
            if str(PROJECT_ROOT) in file_path:
                file_path = file_path.replace(str(PROJECT_ROOT) + os.sep, "")
            results.append((file_path, line_num, content.strip()))

    return results


def extract_modules() -> str:
    """모듈 맵 추출"""
    lines = [
        "## Module Map",
        "",
        f"_Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "### Entry Points",
        "",
    ]

    # CLI 엔트리포인트
    cli_patterns = run_grep(r"argparse|click|typer|def main")
    if cli_patterns:
        lines.append("#### CLI")
        lines.append("")
        lines.append("| File | Line | Content |")
        lines.append("|------|------|---------|")
        for fp, ln, content in cli_patterns[:20]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # MCP 서버 엔트리포인트
    mcp_patterns = run_grep(r"@server\.|Tool\(|HANDLER_MAP")
    if mcp_patterns:
        lines.append("#### MCP Server")
        lines.append("")
        lines.append("| File | Line | Content |")
        lines.append("|------|------|---------|")
        for fp, ln, content in mcp_patterns[:30]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # 주요 클래스/함수
    lines.append("### Core Functions")
    lines.append("")
    core_patterns = run_grep(r"^def (can_code|manager|ship|activate|start)\(")
    if core_patterns:
        lines.append("| File | Line | Function |")
        lines.append("|------|------|----------|")
        for fp, ln, content in core_patterns:
            func_match = re.search(r"def (\w+)\(", content)
            func_name = func_match.group(1) if func_match else content[:40]
            lines.append(f"| `{fp}` | {ln} | `{func_name}()` |")
        lines.append("")

    return "\n".join(lines)


def extract_data_contracts() -> str:
    """데이터 계약 추출 (HTTP 호출, API 엔드포인트)"""
    lines = [
        "## Data Contracts",
        "",
        f"_Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "### External API Calls",
        "",
    ]

    # HTTP 호출
    http_patterns = run_grep(r"requests\.(get|post|put|delete)|httpx\.")
    if http_patterns:
        lines.append("| File | Line | Call |")
        lines.append("|------|------|------|")
        for fp, ln, content in http_patterns:
            content_short = content[:70] + "..." if len(content) > 70 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # API Base URLs
    lines.append("### API Endpoints")
    lines.append("")
    url_patterns = run_grep(r"API_BASE_URL|workers\.dev|/api/")
    if url_patterns:
        lines.append("| File | Line | Endpoint |")
        lines.append("|------|------|----------|")
        for fp, ln, content in url_patterns:
            content_short = content[:70] + "..." if len(content) > 70 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # Worker 호출
    lines.append("### Worker Integrations")
    lines.append("")
    worker_patterns = run_grep(r"clouvel.*workers\.dev")
    if worker_patterns:
        lines.append("| File | Line | Worker |")
        lines.append("|------|------|--------|")
        for fp, ln, content in worker_patterns:
            content_short = content[:70] + "..." if len(content) > 70 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    return "\n".join(lines)


def extract_runtime_paths() -> str:
    """런타임 경로 추출 (조건 분기)"""
    lines = [
        "## Runtime Paths",
        "",
        f"_Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "### Conditional Branches",
        "",
    ]

    # 주요 조건 분기
    branch_patterns = run_grep(r"if (use_dynamic|_HAS_MANAGER|_HAS_ERROR|is_developer|has_license)")
    if branch_patterns:
        lines.append("| File | Line | Condition |")
        lines.append("|------|------|-----------|")
        for fp, ln, content in branch_patterns:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # Import fallbacks
    lines.append("### Import Fallbacks")
    lines.append("")
    fallback_patterns = run_grep(r"except ImportError")
    if fallback_patterns:
        lines.append("| File | Line | Context |")
        lines.append("|------|------|---------|")
        for fp, ln, content in fallback_patterns:
            lines.append(f"| `{fp}` | {ln} | `{content}` |")
        lines.append("")

    # Try-except 패턴
    lines.append("### Error Handling Paths")
    lines.append("")
    error_patterns = run_grep(r"except (Exception|requests\.)")
    if error_patterns:
        lines.append("| File | Line | Handler |")
        lines.append("|------|------|---------|")
        for fp, ln, content in error_patterns[:20]:
            lines.append(f"| `{fp}` | {ln} | `{content}` |")
        lines.append("")

    return "\n".join(lines)


def extract_side_effects() -> str:
    """사이드 이펙트 추출 (네트워크, 파일, 환경변수, 프로세스)"""
    lines = [
        "## Side Effects (Auto-Generated)",
        "",
        f"_Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "### Network Calls",
        "",
    ]

    # HTTP 호출
    http_patterns = run_grep(r"requests\.(post|get|put|delete)\(")
    if http_patterns:
        lines.append("| File | Line | Call |")
        lines.append("|------|------|------|")
        for fp, ln, content in http_patterns[:15]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # 파일 I/O
    lines.append("### File I/O")
    lines.append("")
    file_patterns = run_grep(r"\.(write_text|read_text|mkdir|unlink)\(")
    if file_patterns:
        lines.append("| File | Line | Operation |")
        lines.append("|------|------|-----------|")
        for fp, ln, content in file_patterns[:15]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # 환경변수
    lines.append("### Environment Variables")
    lines.append("")
    env_patterns = run_grep(r"os\.environ\.get\(|os\.environ\[")
    if env_patterns:
        lines.append("| File | Line | Variable |")
        lines.append("|------|------|----------|")
        for fp, ln, content in env_patterns[:15]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # subprocess
    lines.append("### Process Calls")
    lines.append("")
    proc_patterns = run_grep(r"subprocess\.(run|call|Popen)")
    if proc_patterns:
        lines.append("| File | Line | Call |")
        lines.append("|------|------|------|")
        for fp, ln, content in proc_patterns[:10]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    return "\n".join(lines)


def extract_entrypoints() -> str:
    """엔트리포인트 추출 (CLI, MCP)"""
    lines = [
        "## Entrypoints (Auto-Generated)",
        "",
        f"_Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "### CLI Commands",
        "",
    ]

    # argparse subparser
    cli_patterns = run_grep(r"add_parser\(|parser\.add_argument")
    if cli_patterns:
        lines.append("| File | Line | Command |")
        lines.append("|------|------|---------|")
        for fp, ln, content in cli_patterns[:10]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # MCP Tool 정의
    lines.append("### MCP Tools")
    lines.append("")
    tool_patterns = run_grep(r"Tool\(\s*name=")
    if tool_patterns:
        lines.append("| File | Line | Tool |")
        lines.append("|------|------|------|")
        for fp, ln, content in tool_patterns[:30]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    # MCP Handler
    lines.append("### MCP Handlers")
    lines.append("")
    handler_patterns = run_grep(r'"[a-z_]+"\s*:\s*(lambda|async)')
    if handler_patterns:
        lines.append("| File | Line | Handler |")
        lines.append("|------|------|---------|")
        for fp, ln, content in handler_patterns[:30]:
            content_short = content[:60] + "..." if len(content) > 60 else content
            lines.append(f"| `{fp}` | {ln} | `{content_short}` |")
        lines.append("")

    return "\n".join(lines)


def update_doc_file(filepath: Path, auto_content: str, header: str = ""):
    """문서 파일 업데이트 (AUTO-GEN 섹션만)"""
    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")

        # AUTO-GEN 섹션 찾기
        start_idx = existing.find(AUTO_START)
        end_idx = existing.find(AUTO_END)

        if start_idx != -1 and end_idx != -1:
            # 기존 AUTO-GEN 섹션 교체
            new_content = (
                existing[:start_idx + len(AUTO_START)] +
                "\n" + auto_content + "\n" +
                existing[end_idx:]
            )
        else:
            # AUTO-GEN 섹션 추가
            new_content = existing + "\n\n" + AUTO_START + "\n" + auto_content + "\n" + AUTO_END
    else:
        # 새 파일 생성
        new_content = f"""# {header}

> Clouvel Architecture Documentation
> 이 파일의 AUTO-GEN 섹션은 자동 생성됩니다. 수동 수정은 마커 밖에서 하세요.

{AUTO_START}
{auto_content}
{AUTO_END}

---

## Manual Notes

_(수동으로 추가할 내용은 여기에)_
"""

    filepath.write_text(new_content, encoding="utf-8")
    print(f"Updated: {filepath}")


def main():
    """메인 실행"""
    print("=" * 60)
    print("Clouvel Documentation Extractor")
    print("=" * 60)
    print()

    # 디렉토리 생성
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # MODULE_MAP.md
    print("Extracting MODULE_MAP...")
    module_content = extract_modules()
    update_doc_file(DOCS_DIR / "MODULE_MAP.md", module_content, "Module Map")

    # DATA_CONTRACTS.md (기존 파일에 AUTO-GEN 추가)
    print("Extracting DATA_CONTRACTS...")
    data_content = extract_data_contracts()
    update_doc_file(DOCS_DIR / "DATA_CONTRACTS.md", data_content, "Data Contracts")

    # RUNTIME_PATHS.md
    print("Extracting RUNTIME_PATHS...")
    runtime_content = extract_runtime_paths()
    update_doc_file(DOCS_DIR / "RUNTIME_PATHS.md", runtime_content, "Runtime Paths")

    # ENTRYPOINTS.md
    print("Extracting ENTRYPOINTS...")
    entry_content = extract_entrypoints()
    update_doc_file(DOCS_DIR / "ENTRYPOINTS.md", entry_content, "Entrypoints")

    # SIDE_EFFECTS.md
    print("Extracting SIDE_EFFECTS...")
    side_content = extract_side_effects()
    update_doc_file(DOCS_DIR / "SIDE_EFFECTS.md", side_content, "Side Effects")

    print()
    print("=" * 60)
    print("Documentation extraction complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
