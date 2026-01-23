# -*- coding: utf-8 -*-
"""
clouvel install - 통합 설치 도구

MCP 서버 설치를 한 줄로 간소화
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Literal

Platform = Literal["auto", "code", "desktop", "cursor", "all"]


def _get_desktop_config_path() -> Path:
    """플랫폼별 Claude Desktop config 경로"""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def _detect_platform() -> list[str]:
    """설치 가능한 플랫폼 감지"""
    available = []

    # Claude Code (claude CLI)
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            available.append("code")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Claude Desktop (config 파일 존재)
    desktop_config = _get_desktop_config_path()
    if desktop_config.parent.exists():
        available.append("desktop")

    # Cursor (향후 지원)
    # cursor_config = ...

    return available


def _get_python_command() -> list[str]:
    """플랫폼별 Python 명령어 반환"""
    if sys.platform == "win32":
        # Windows: py -m clouvel.server
        return ["py", "-m", "clouvel.server"]
    else:
        # Linux/Mac/WSL: python3 -m clouvel.server
        return ["python3", "-m", "clouvel.server"]


def _install_for_code(force: bool = False) -> dict:
    """Claude Code에 MCP 등록"""
    result = {"platform": "code", "success": False, "message": ""}

    try:
        # 기존 등록 확인 (encoding 명시로 Windows cp949 문제 해결)
        check = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )

        stdout = check.stdout or ""

        if "clouvel" in stdout and not force:
            result["success"] = True
            result["message"] = "이미 등록됨"
            result["skipped"] = True
            return result

        # 등록 (force면 기존 것 제거 후 등록)
        if force and "clouvel" in stdout:
            subprocess.run(
                ["claude", "mcp", "remove", "clouvel"],
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )

        # 플랫폼별 Python 명령어 사용
        python_cmd = _get_python_command()
        add_result = subprocess.run(
            ["claude", "mcp", "add", "clouvel", "-s", "user", "--"] + python_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )

        if add_result.returncode == 0:
            result["success"] = True
            result["message"] = f"등록 완료 ({' '.join(python_cmd)})"
        else:
            stderr = add_result.stderr or ""
            result["message"] = f"등록 실패: {stderr.strip()}"

    except FileNotFoundError:
        result["message"] = "claude 명령어 없음"
    except subprocess.TimeoutExpired:
        result["message"] = "타임아웃"
    except Exception as e:
        result["message"] = f"오류: {str(e)}"

    return result


def _install_for_desktop(force: bool = False) -> dict:
    """Claude Desktop config.json 수정"""
    result = {"platform": "desktop", "success": False, "message": ""}

    config_path = _get_desktop_config_path()

    try:
        # 기존 config 로드
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # mcpServers 섹션
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # 이미 등록됨?
        if "clouvel" in config["mcpServers"] and not force:
            result["success"] = True
            result["message"] = "이미 등록됨"
            result["skipped"] = True
            return result

        # clouvel 서버 추가 (플랫폼별 Python 명령어)
        python_cmd = _get_python_command()
        config["mcpServers"]["clouvel"] = {
            "command": python_cmd[0],
            "args": python_cmd[1:]
        }

        # 저장
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        result["success"] = True
        result["message"] = f"등록 완료 ({config_path})"

    except json.JSONDecodeError:
        result["message"] = f"config 파일 파싱 실패: {config_path}"
    except PermissionError:
        result["message"] = f"권한 없음: {config_path}"
    except Exception as e:
        result["message"] = f"오류: {str(e)}"

    return result


def _add_global_rules(force: bool = False) -> dict:
    """~/.claude/CLAUDE.md에 규칙 추가"""
    result = {"success": False, "message": ""}

    claude_dir = Path.home() / ".claude"
    claude_md = claude_dir / "CLAUDE.md"

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

    try:
        claude_dir.mkdir(parents=True, exist_ok=True)

        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")

            if marker in content and not force:
                result["success"] = True
                result["message"] = "이미 규칙 있음"
                result["skipped"] = True
                return result

            if marker in content and force:
                # 기존 규칙 제거 후 재추가
                lines = content.split("\n")
                new_lines = []
                skip = False
                for line in lines:
                    if line.strip().startswith("## Clouvel 규칙"):
                        skip = True
                        continue
                    if skip and line.startswith("## "):
                        skip = False
                    if not skip:
                        new_lines.append(line)
                content = "\n".join(new_lines).rstrip()

            new_content = content.rstrip() + "\n\n---\n" + clouvel_rule
        else:
            new_content = f"# Claude Code 글로벌 설정\n\n> clouvel install로 생성됨\n\n---\n{clouvel_rule}"

        claude_md.write_text(new_content, encoding="utf-8")
        result["success"] = True
        result["message"] = f"규칙 추가됨 ({claude_md})"

    except PermissionError:
        result["message"] = f"권한 없음: {claude_md}"
    except Exception as e:
        result["message"] = f"오류: {str(e)}"

    return result


def _verify_installation(platform: str) -> dict:
    """설치 확인"""
    result = {"success": False, "message": ""}

    if platform == "code":
        try:
            check = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            stdout = check.stdout or ""
            if "clouvel" in stdout:
                result["success"] = True
                result["message"] = "MCP 목록에 clouvel 확인됨"
            else:
                result["message"] = "MCP 목록에 clouvel 없음"
        except Exception as e:
            result["message"] = f"확인 실패: {str(e)}"

    elif platform == "desktop":
        config_path = _get_desktop_config_path()
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if "clouvel" in config.get("mcpServers", {}):
                    result["success"] = True
                    result["message"] = "Desktop config에 clouvel 확인됨"
                else:
                    result["message"] = "Desktop config에 clouvel 없음"
            else:
                result["message"] = "Desktop config 파일 없음"
        except Exception as e:
            result["message"] = f"확인 실패: {str(e)}"

    return result


def run_install(platform: Platform = "auto", force: bool = False) -> str:
    """
    clouvel install 메인 함수

    Args:
        platform: 설치 대상 (auto, code, desktop, cursor, all)
        force: 이미 설치되어 있어도 재설치

    Returns:
        설치 결과 문자열
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("              Clouvel 설치 중...")
    lines.append("=" * 60)
    lines.append("")

    # 1. 플랫폼 감지
    lines.append("[1/4] 플랫폼 감지...")
    available = _detect_platform()

    if platform == "auto":
        if "code" in available:
            targets = ["code"]
            lines.append("      → Claude Code 감지됨")
        elif "desktop" in available:
            targets = ["desktop"]
            lines.append("      → Claude Desktop 감지됨")
        else:
            lines.append("      → 설치 가능한 플랫폼 없음")
            lines.append("")
            lines.append("수동 설치:")
            if sys.platform == "win32":
                lines.append("  Claude Code: claude mcp add clouvel -s user -- py -m clouvel.server")
            else:
                lines.append("  Claude Code: claude mcp add clouvel -s user -- python3 -m clouvel.server")
            lines.append("  Desktop: claude_desktop_config.json에 clouvel 추가")
            return "\n".join(lines)
    elif platform == "all":
        targets = available if available else []
        lines.append(f"      → 대상: {', '.join(targets) if targets else '없음'}")
    else:
        targets = [platform]
        lines.append(f"      → 대상: {platform}")

    if not targets:
        lines.append("      [FAIL] 설치 대상 없음")
        return "\n".join(lines)

    lines.append("")

    # 2. MCP 서버 등록
    lines.append("[2/4] MCP 서버 등록...")
    install_results = []

    for target in targets:
        if target == "code":
            r = _install_for_code(force)
        elif target == "desktop":
            r = _install_for_desktop(force)
        else:
            r = {"platform": target, "success": False, "message": "미지원"}

        install_results.append(r)

        status = "[OK]" if r["success"] else "[FAIL]"
        skip_mark = " (건너뜀)" if r.get("skipped") else ""
        lines.append(f"      {status} {r['platform']}: {r['message']}{skip_mark}")

    lines.append("")

    # 3. 글로벌 규칙 추가
    lines.append("[3/4] 글로벌 규칙 추가...")
    rules_result = _add_global_rules(force)
    status = "[OK]" if rules_result["success"] else "[FAIL]"
    skip_mark = " (건너뜀)" if rules_result.get("skipped") else ""
    lines.append(f"      {status} {rules_result['message']}{skip_mark}")
    lines.append("")

    # 4. 설치 확인
    lines.append("[4/4] 설치 확인...")
    all_verified = True
    for target in targets:
        v = _verify_installation(target)
        status = "[OK]" if v["success"] else "[FAIL]"
        lines.append(f"      {status} {target}: {v['message']}")
        if not v["success"]:
            all_verified = False

    lines.append("")

    # 결과
    lines.append("=" * 60)
    if all_verified:
        lines.append("              [OK] 설치 완료!")
    else:
        lines.append("              [WARN] 일부 설치됨 (확인 필요)")
    lines.append("=" * 60)
    lines.append("")

    # 다음 단계
    lines.append("다음 단계:")
    if "code" in targets:
        lines.append("  1. Claude Code 재시작 (또는 새 세션)")
    if "desktop" in targets:
        lines.append("  1. Claude Desktop 재시작")
    lines.append("  2. \"코드 짜줘\" 요청 시 can_code가 자동 호출됨")
    lines.append("  3. PRD 없으면 BLOCK, 있으면 PASS")
    lines.append("")
    lines.append("문제가 있으면:")
    lines.append("  clouvel install --force  (재설치)")
    lines.append("  clouvel --help           (도움말)")
    lines.append("")

    return "\n".join(lines)
