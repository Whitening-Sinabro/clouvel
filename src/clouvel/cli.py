# -*- coding: utf-8 -*-
"""
Clouvel CLI Entry Points

run_server(), _run_setup(), and main() for CLI usage.
Extracted from server.py for maintainability.
"""

import os
import sys
import argparse
from pathlib import Path

from mcp.server.stdio import stdio_server


async def run_server():
    from .server import server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _run_setup(global_only: bool = False, hooks: bool = False) -> str:
    """B0: clouvel setup - install forced invocation mechanism"""
    import subprocess

    results = []

    # --hooks: Install pre-commit hooks in current project
    if hooks:
        git_hooks_dir = Path(".git/hooks")
        if git_hooks_dir.exists():
            pre_commit = git_hooks_dir / "pre-commit"
            pre_commit_content = '''#!/bin/bash
# Clouvel pre-commit hook (v1.6)
# 1. PRD check
# 2. Record files check (files/created.md, status/current.md)
# 3. New files tracking check
# 4. Sensitive files check

# === PRD Check ===
DOCS_DIR="./docs"
if ! ls "$DOCS_DIR"/*[Pp][Rr][Dd]* 1> /dev/null 2>&1; then
    echo "[Clouvel] BLOCKED: No PRD document found."
    echo "Please create docs/PRD.md first."
    exit 1
fi

# === Record Files Check (v1.5) ===
if [ ! -f ".claude/files/created.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: files/created.md missing"
    echo "========================================"
    echo ""
    echo "No file creation record found."
    echo "Fix: Create .claude/files/created.md before commit"
    echo ""
    exit 1
fi

if [ ! -f ".claude/status/current.md" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] BLOCKED: status/current.md missing"
    echo "========================================"
    echo ""
    echo "No work status record found."
    echo "Fix: Create .claude/status/current.md before commit"
    echo ""
    exit 1
fi

# === New Files Tracking Check (v1.6) ===
# Check if newly added files are recorded in created.md
CREATED_MD=".claude/files/created.md"
NEW_FILES=$(git diff --cached --name-only --diff-filter=A 2>/dev/null)

# Skip certain files/patterns from tracking requirement
SKIP_PATTERNS="(\\.md$|\\.txt$|\\.json$|\\.yml$|\\.yaml$|\\.gitignore|\\.env|__pycache__|\\.pyc$|node_modules|\\.git)"

if [ -n "$NEW_FILES" ] && [ -f "$CREATED_MD" ]; then
    UNTRACKED=""
    while IFS= read -r file; do
        # Skip files matching skip patterns
        if echo "$file" | grep -qE "$SKIP_PATTERNS"; then
            continue
        fi
        # Check if file is recorded in created.md
        if ! grep -qF "$file" "$CREATED_MD" 2>/dev/null; then
            UNTRACKED="$UNTRACKED$file\n"
        fi
    done <<< "$NEW_FILES"

    if [ -n "$UNTRACKED" ]; then
        echo ""
        echo "========================================"
        echo "[Clouvel] WARNING: Untracked new files"
        echo "========================================"
        echo ""
        echo "These files are not recorded in .claude/files/created.md:"
        echo -e "$UNTRACKED" | while read -r file; do
            [ -n "$file" ] && echo "  📁 $file"
        done
        echo ""
        echo "To record these files, copy & run in Claude:"
        echo "────────────────────────────────────────"
        echo -e "$UNTRACKED" | while read -r file; do
            [ -n "$file" ] && echo 'record_file(path=".", file_path="'"$file"'", purpose="...")'
        done
        echo "────────────────────────────────────────"
        echo ""
        echo "Continuing commit... (this is a warning, not a block)"
        echo ""
    fi
fi

# === Security Check (sensitive files) ===
SENSITIVE_PATTERNS="(marketing|strategy|pricing|server_pro|_pro\\.py|\\.key$|\\.secret$|credentials|password)"

SENSITIVE_FILES=$(git diff --cached --name-only | grep -iE "$SENSITIVE_PATTERNS" 2>/dev/null)

if [ -n "$SENSITIVE_FILES" ]; then
    echo ""
    echo "========================================"
    echo "[Clouvel] SECURITY BLOCK: Sensitive files detected!"
    echo "========================================"
    echo ""
    echo "Cannot commit these files:"
    echo "$SENSITIVE_FILES" | while read -r file; do
        echo "  ❌ $file"
    done
    echo ""
    echo "Fix: git reset HEAD <filename>"
    echo "Skip: git commit --no-verify (not recommended)"
    echo ""
    exit 1
fi

echo "[Clouvel] All checks passed. ✓"
'''
            pre_commit.write_text(pre_commit_content, encoding='utf-8')
            try:
                os.chmod(pre_commit, 0o755)
            except OSError:
                pass
            results.append(f"[OK] Pre-commit hook installed: {pre_commit}")
            return "\n".join(results)
        else:
            return "[ERROR] .git/hooks not found. Run from git repository root."

    # 1. Add rules to global CLAUDE.md
    if os.name == 'nt':  # Windows
        claude_dir = Path.home() / ".claude"
    else:  # Mac/Linux
        claude_dir = Path.home() / ".claude"

    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_md_path = claude_dir / "CLAUDE.md"

    clouvel_rule = """
## Clouvel Rules (Auto-generated)

**Must call clouvel's `can_code` tool before writing code.**

- Always call `can_code` tool before writing code (Edit/Write)
- Pass the project's docs folder path as the path argument
- If BLOCK appears, do not write code, guide user to write documentation
- If PASS appears, proceed with coding
- WARN is a recommendation, can proceed but suggest adding recommended docs

**Must call `record_file` after creating important files.**

- After creating a new file with Write tool, call `record_file` to track it
- Required fields: path (project root), file_path (relative), purpose (what it does)
- Skip for: temporary files, test data, config files (.json, .yml, .env)
- This enables file tracking and prevents accidental deletion

"""

    marker = "## Clouvel Rules"
    marker_ko = "## Clouvel 규칙"

    if claude_md_path.exists():
        content = claude_md_path.read_text(encoding='utf-8')
        if marker in content or marker_ko in content:
            results.append("[OK] Global CLAUDE.md: Clouvel rules already exist")
        else:
            # Append to existing content
            new_content = content.rstrip() + "\n\n---\n" + clouvel_rule
            claude_md_path.write_text(new_content, encoding='utf-8')
            results.append(f"[OK] Global CLAUDE.md: Rules added ({claude_md_path})")
    else:
        # Create new
        initial_content = f"# Claude Code Global Settings\n\n> Auto-generated by clouvel setup\n\n---\n{clouvel_rule}"
        claude_md_path.write_text(initial_content, encoding='utf-8')
        results.append(f"[OK] Global CLAUDE.md: Created ({claude_md_path})")

    # 2. Register MCP server (only when not global_only)
    if not global_only:
        try:
            # First check existing registration
            check_result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "clouvel" in check_result.stdout:
                results.append("[OK] MCP Server: Already registered")
            else:
                # Register
                add_result = subprocess.run(
                    ["claude", "mcp", "add", "clouvel", "-s", "user", "--", "clouvel"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if add_result.returncode == 0:
                    results.append("[OK] MCP Server: Registration complete")
                else:
                    results.append(f"[WARN] MCP Server: Registration failed - {add_result.stderr.strip()}")
                    results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")
        except FileNotFoundError:
            results.append("[WARN] MCP Server: claude command not found")
            results.append("   Please install Claude Code and try again")
        except subprocess.TimeoutExpired:
            results.append("[WARN] MCP Server: Timeout")
            results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")
        except Exception as e:
            results.append(f"[WARN] MCP Server: Error - {str(e)}")
            results.append("   Manual registration: claude mcp add clouvel -s user -- clouvel")

    # Output results
    output = """
================================================================
                    Clouvel Setup Complete
================================================================

"""
    output += "\n".join(results)
    output += """

----------------------------------------------------------------

## How It Works

1. Run Claude Code
2. Request "Build a login feature"
3. Claude automatically calls can_code first
4. No PRD -> [BLOCK] BLOCK (coding blocked)
5. PRD exists -> [OK] PASS (proceed with coding)

## Test

```bash
# Test in a folder without PRD
mkdir test-project && cd test-project
claude
> "Write some code"
# -> Verify BLOCK message
```

----------------------------------------------------------------
"""

    return output


def main():

    parser = argparse.ArgumentParser(description="Clouvel - Vibe coding process enforcement tool")
    subparsers = parser.add_subparsers(dest="command")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("-p", "--path", default=".", help="Project path")
    init_parser.add_argument("-l", "--level", choices=["remind", "strict", "full"], default="strict")

    # setup command (B0) - legacy, install recommended
    setup_parser = subparsers.add_parser("setup", help="Install Clouvel forced invocation mechanism (global)")
    setup_parser.add_argument("--global-only", action="store_true", help="Configure CLAUDE.md only (exclude MCP registration)")
    setup_parser.add_argument("--hooks", action="store_true", help="Install pre-commit hooks for record enforcement")
    setup_parser.add_argument("--proactive", choices=["free", "pro"], help="Setup proactive hooks (v2.0) - auto PRD check, drift detection")
    setup_parser.add_argument("--path", "-p", default=".", help="Project root path")

    # install command (new, recommended)
    install_parser = subparsers.add_parser("install", help="Install Clouvel MCP server (recommended)")
    install_parser.add_argument("--platform", choices=["auto", "code", "desktop", "cursor", "all"], default="auto", help="Target platform for installation")
    install_parser.add_argument("--force", action="store_true", help="Reinstall even if already installed")

    # can_code command (for hooks integration)
    can_code_parser = subparsers.add_parser("can_code", help="Check if coding is allowed (for hooks)")
    can_code_parser.add_argument("--path", "-p", default=".", help="Project docs path")
    can_code_parser.add_argument("--silent", "-s", action="store_true", help="Silent mode - exit code only")

    # drift_check command (for hooks integration)
    drift_parser = subparsers.add_parser("drift_check", help="Check for context drift (Pro)")
    drift_parser.add_argument("--path", "-p", default=".", help="Project root path")
    drift_parser.add_argument("--silent", "-s", action="store_true", help="Silent mode - minimal output")

    # activate command (license activation)
    activate_parser = subparsers.add_parser("activate", help="Activate license")
    activate_parser.add_argument("license_key", help="License key")

    # status command (license status)
    subparsers.add_parser("status", help="Check license status")

    # gate_check command (lightweight hook check)
    subparsers.add_parser("gate_check", help="Lightweight gate check for PreToolUse hooks")

    # deactivate command (license deactivation)
    subparsers.add_parser("deactivate", help="Deactivate license (delete local cache)")

    args = parser.parse_args()

    if args.command == "init":
        from .tools.setup import setup_cli as sync_setup
        import asyncio
        result = asyncio.run(sync_setup(args.path, args.level))
        print(result[0].text)
    elif args.command == "setup":
        # Handle --proactive option
        if hasattr(args, 'proactive') and args.proactive:
            from .tools.setup import setup_cli as sync_setup
            result = asyncio.run(sync_setup(
                path=args.path if hasattr(args, 'path') else ".",
                proactive=args.proactive
            ))
            print(result[0].text)
        else:
            result = _run_setup(
                global_only=args.global_only if hasattr(args, 'global_only') else False,
                hooks=args.hooks if hasattr(args, 'hooks') else False
            )
            print(result)
    elif args.command == "install":
        from .tools.install import run_install
        result = run_install(
            platform=args.platform if hasattr(args, 'platform') else "auto",
            force=args.force if hasattr(args, 'force') else False
        )
        print(result)
    elif args.command == "can_code":
        # CLI for hooks integration
        from .tools.core import can_code as sync_can_code
        result = asyncio.run(sync_can_code(args.path))

        # Parse result to determine exit code
        result_text = result[0].text if result else ""
        is_block = "BLOCK" in result_text

        if args.silent:
            # Silent mode: just exit code
            if is_block:
                sys.exit(1)  # BLOCK = fail
            else:
                sys.exit(0)  # PASS or WARN = ok
        else:
            # Normal mode: print result
            print(result_text)
            if is_block:
                sys.exit(1)
    elif args.command == "drift_check":
        # CLI for hooks integration
        from .tools.proactive import drift_check as sync_drift_check
        result = asyncio.run(sync_drift_check(args.path, silent=args.silent))

        result_text = result[0].text if result else ""

        if args.silent:
            print(result_text)  # Short status like "OK:0" or "DRIFT:75"
            if "DRIFT" in result_text:
                sys.exit(1)
            sys.exit(0)
        else:
            print(result_text)
            if "DRIFT" in result_text or "🚨" in result_text:
                sys.exit(1)
    elif args.command == "activate":
        try:
            from .license import activate_license_cli
        except ImportError:
            from .license_free import activate_license_cli
        result = activate_license_cli(args.license_key)
        if result["success"]:
            print(f"""
================================================================
              Clouvel Pro License Activated
================================================================

{result['message']}

Tier: {result.get('tier_info', {}).get('name', 'Unknown')}
Machine: {result.get('machine_id', 'Unknown')[:8]}...
Product: {result.get('product', 'Clouvel Pro')}

----------------------------------------------------------------
Premium features will be available 7 days after activation.
Check status with 'clouvel status'.
================================================================
""")
        else:
            print(result["message"])
            sys.exit(1)
    elif args.command == "status":
        try:
            from .license import get_license_status
        except ImportError:
            from .license_free import get_license_status
        result = get_license_status()
        if result.get("has_license"):
            tier_info = result.get("tier_info", {})
            unlock_status = "[OK] Unlocked" if result.get("premium_unlocked") else f"[...] {result.get('premium_unlock_remaining', '?')} days remaining"
            print(f"""
================================================================
                   Clouvel License Status
================================================================

Status: [OK] Activated
Tier: {tier_info.get('name', 'Unknown')} ({tier_info.get('price', '?')})
Machine: {result.get('machine_id', 'Unknown')[:8]}...

Activated at: {result.get('activated_at', 'N/A')[:19]}
Days since activation: {result.get('days_since_activation', 0)}
Premium features: {unlock_status}

================================================================
""")
        else:
            print(f"""
================================================================
                   Clouvel License Status
================================================================

Status: [X] Not activated

{result.get('message', '')}

Start trial: clouvel activate --trial
Purchase:    https://polar.sh/clouvel
================================================================
""")
    elif args.command == "gate_check":
        # Lightweight gate check — calls main() directly
        from .gate_check import main as gate_main
        sys.exit(gate_main())
    elif args.command == "deactivate":
        try:
            from .license import deactivate_license_cli
        except ImportError:
            from .license_free import deactivate_license_cli
        result = deactivate_license_cli()
        print(result["message"])
        if not result["success"]:
            sys.exit(1)
    else:
        asyncio.run(run_server())


