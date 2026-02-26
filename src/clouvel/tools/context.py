# -*- coding: utf-8 -*-
"""Context recovery tools: recover_context for automatic state recovery after context compaction"""

import os
import re
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent

from ..license import require_license


def _extract_summary(current_md: str) -> dict:
    """current.md에서 핵심 정보 추출"""
    summary = {
        "status": None,
        "completed": [],
        "next_todos": [],
        "blockers": []
    }

    lines = current_md.split("\n")
    current_section = None

    for line in lines:
        # 섹션 헤더 감지
        if "## 지금 상태" in line or "## 현재 상태" in line or "## Current Status" in line:
            current_section = "status"
        elif "## 완료" in line or "## Completed" in line or "## 오늘 완료" in line:
            current_section = "completed"
        elif "## 다음 할 일" in line or "## Next" in line or "## TODO" in line:
            current_section = "next"
        elif "## 블로커" in line or "## Blocker" in line:
            current_section = "blockers"
        elif line.startswith("## "):
            current_section = None

        # 내용 파싱
        if current_section == "status" and "|" in line and "항목" not in line and "---" not in line:
            summary["status"] = line
        elif current_section == "completed" and line.strip().startswith("- [x]"):
            summary["completed"].append(line.strip()[6:].strip())
        elif current_section == "next" and line.strip().startswith("- ["):
            task = line.strip()
            if "[ ]" in task:
                summary["next_todos"].append(task[6:].strip())
        elif current_section == "blockers" and line.strip().startswith("-"):
            summary["blockers"].append(line.strip()[1:].strip())

    return summary


def _find_active_plans(claude_dir: Path) -> list[dict]:
    """활성 PLAN 파일 찾기"""
    plans = []
    plans_dir = claude_dir / "plans"

    if not plans_dir.exists():
        return plans

    for plan_file in plans_dir.glob("PLAN-*.md"):
        try:
            content = plan_file.read_text(encoding="utf-8")

            # 상태 감지
            status = "unknown"
            if "LOCKED" in content or "🔒" in content:
                status = "locked"
            elif "COMPLETE" in content or "✅ COMPLETE" in content:
                status = "complete"
            elif "IN_PROGRESS" in content or "진행 중" in content:
                status = "in_progress"

            # 현재 Step 감지
            current_step = None
            step_matches = re.findall(r"###\s+Step\s+(\d+)[^#]*?\n-\s*\[([x\s])\]", content, re.IGNORECASE)
            for step_num, checked in step_matches:
                if checked.strip() == "":
                    current_step = int(step_num)
                    break

            # 태스크명 추출
            task_match = re.search(r">\s*\*\*태스크\*\*:\s*(.+)", content)
            task = task_match.group(1).strip() if task_match else plan_file.stem

            plans.append({
                "file": plan_file.name,
                "status": status,
                "task": task,
                "current_step": current_step
            })
        except Exception:
            continue

    return plans


def _get_git_status(project_path: Path) -> dict:
    """git 상태 확인 (subprocess 없이)"""
    git_dir = project_path / ".git"

    if not git_dir.exists():
        return {"is_git": False}

    result = {
        "is_git": True,
        "branch": None,
        "has_changes": False
    }

    # 현재 브랜치 읽기
    head_file = git_dir / "HEAD"
    if head_file.exists():
        head_content = head_file.read_text(encoding="utf-8").strip()
        if head_content.startswith("ref: refs/heads/"):
            result["branch"] = head_content.replace("ref: refs/heads/", "")

    # 변경사항 여부 (index 파일 시간으로 대략 추정)
    index_file = git_dir / "index"
    if index_file.exists():
        # index 파일이 최근에 수정되었으면 변경 가능성 있음
        mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
        if (datetime.now() - mtime).total_seconds() < 3600:  # 1시간 이내
            result["has_changes"] = True

    return result


def _extract_rules(claude_md: str, project_path: str = None) -> list[str]:
    """CLAUDE.md + .claude/rules/*.md에서 핵심 규칙 추출

    Args:
        claude_md: CLAUDE.md 파일 내용
        project_path: 프로젝트 경로 (옵셔널, .claude/rules/ 스캔용)
    """
    rules = []

    # CLAUDE.md에서 NEVER/ALWAYS 패턴 찾기
    never_matches = re.findall(r"NEVER[:\s]+([^\n]+)", claude_md, re.IGNORECASE)
    always_matches = re.findall(r"ALWAYS[:\s]+([^\n]+)", claude_md, re.IGNORECASE)

    for match in never_matches[:5]:  # 최대 5개
        rules.append(f"NEVER: {match.strip()}")

    for match in always_matches[:5]:
        rules.append(f"ALWAYS: {match.strip()}")

    # .claude/rules/*.md에서 추가 규칙 추출
    if project_path:
        rules_dir = Path(project_path) / ".claude" / "rules"
        if rules_dir.exists():
            seen = set(rules)
            for rule_file in sorted(rules_dir.glob("*.md")):
                try:
                    content = rule_file.read_text(encoding="utf-8")
                    r_never = re.findall(r"NEVER[:\s]+([^\n]+)", content, re.IGNORECASE)
                    r_always = re.findall(r"ALWAYS[:\s]+([^\n]+)", content, re.IGNORECASE)
                    for match in r_never:
                        entry = f"NEVER: {match.strip()}"
                        if entry not in seen:
                            rules.append(entry)
                            seen.add(entry)
                    for match in r_always:
                        entry = f"ALWAYS: {match.strip()}"
                        if entry not in seen:
                            rules.append(entry)
                            seen.add(entry)
                except Exception:
                    continue

    # 최대 10개 (CLAUDE.md 5개 + rules/ 5개)
    return rules[:10]


def _extract_prd_summary(prd_content: str) -> str:
    """PRD에서 첫 섹션 요약 추출"""
    lines = prd_content.split("\n")
    summary_lines = []
    in_summary = False

    for line in lines[:50]:  # 처음 50줄만
        if line.startswith("# ") and not in_summary:
            summary_lines.append(line)
            in_summary = True
        elif in_summary and line.startswith("## "):
            break
        elif in_summary and line.strip():
            summary_lines.append(line)

    return "\n".join(summary_lines[:10])  # 최대 10줄


def _get_recent_modified_files(project_path: Path, limit: int = 5) -> list[str]:
    """최근 수정된 파일 목록"""
    recent_files = []

    # 일반적인 소스 확장자
    extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".go", ".rs"}

    try:
        source_files = []
        for ext in extensions:
            source_files.extend(project_path.rglob(f"*{ext}"))

        # node_modules, .git, __pycache__ 제외
        filtered = [
            f for f in source_files
            if "node_modules" not in str(f)
            and ".git" not in str(f)
            and "__pycache__" not in str(f)
            and ".venv" not in str(f)
        ]

        # 수정 시간순 정렬
        sorted_files = sorted(filtered, key=lambda f: f.stat().st_mtime, reverse=True)

        for f in sorted_files[:limit]:
            rel_path = f.relative_to(project_path)
            recent_files.append(str(rel_path))
    except Exception:
        pass

    return recent_files


@require_license
async def recover_context(
    project_path: str = None,
    depth: str = "normal"
) -> list[TextContent]:
    """
    컨텍스트 압축 후 프로젝트 상태 자동 복구.

    Args:
        project_path: 프로젝트 경로 (기본: 현재 디렉토리)
        depth: 복구 깊이
            - "minimal": current.md + active PLAN만
            - "normal": + git status + CLAUDE.md 규칙
            - "full": + PRD 요약 + 최근 수정 파일

    Returns:
        구조화된 프로젝트 상태 요약
    """
    # 경로 설정
    if project_path:
        path = Path(project_path)
    else:
        path = Path.cwd()

    if not path.exists():
        return [TextContent(type="text", text=f"# ❌ 프로젝트 경로 없음\n\n`{path}` 경로를 찾을 수 없습니다.")]

    # .claude 디렉토리 찾기
    claude_dir = path / ".claude"

    result_parts = []
    result_parts.append("# 🔄 컨텍스트 복구")
    result_parts.append(f"\n> **경로**: `{path}`")
    result_parts.append(f"> **깊이**: {depth}")
    result_parts.append(f"> **시간**: {datetime.now().isoformat()[:19]}")
    result_parts.append("")

    # ============================================================
    # Step 1: current.md 읽기
    # ============================================================
    current_md_path = claude_dir / "status" / "current.md"

    if current_md_path.exists():
        current_content = current_md_path.read_text(encoding="utf-8")
        summary = _extract_summary(current_content)

        result_parts.append("## 📍 현재 상태")
        result_parts.append("")

        if summary["status"]:
            result_parts.append(f"**상태**: {summary['status']}")

        if summary["completed"]:
            result_parts.append("")
            result_parts.append("**최근 완료**:")
            for item in summary["completed"][-5:]:  # 최근 5개
                result_parts.append(f"- ✅ {item}")

        if summary["next_todos"]:
            result_parts.append("")
            result_parts.append("**다음 할 일**:")
            for item in summary["next_todos"][:5]:  # 상위 5개
                result_parts.append(f"- ⏳ {item}")

        if summary["blockers"]:
            result_parts.append("")
            result_parts.append("**블로커**:")
            for item in summary["blockers"]:
                result_parts.append(f"- 🚫 {item}")

        result_parts.append("")
    else:
        result_parts.append("## ⚠️ current.md 없음")
        result_parts.append("")
        result_parts.append("`.claude/status/current.md`가 없습니다. Shovel 설치가 필요할 수 있습니다.")
        result_parts.append("")

    # ============================================================
    # Step 2: 활성 PLAN 찾기
    # ============================================================
    plans = _find_active_plans(claude_dir)

    if plans:
        result_parts.append("## 📋 활성 계획")
        result_parts.append("")

        for plan in plans:
            status_emoji = {
                "locked": "🔒",
                "in_progress": "🔄",
                "complete": "✅",
                "unknown": "❓"
            }.get(plan["status"], "❓")

            step_info = f" (Step {plan['current_step']})" if plan["current_step"] else ""
            result_parts.append(f"- {status_emoji} **{plan['task']}**{step_info}")
            result_parts.append(f"  - 파일: `{plan['file']}`")
            result_parts.append(f"  - 상태: {plan['status']}")

        result_parts.append("")

        # LOCKED 플랜이 있으면 강조
        locked_plans = [p for p in plans if p["status"] == "locked"]
        if locked_plans:
            result_parts.append("### ⚠️ 범위 잠금 활성")
            result_parts.append("")
            result_parts.append("잠긴 계획이 있습니다. 범위 외 작업은 BACKLOG로 이동됩니다.")
            result_parts.append("")
    else:
        result_parts.append("## 📋 활성 계획")
        result_parts.append("")
        result_parts.append("활성 계획이 없습니다.")
        result_parts.append("")

    # ============================================================
    # Step 3: Git 상태 (normal 이상)
    # ============================================================
    if depth in ["normal", "full"]:
        git_status = _get_git_status(path)

        result_parts.append("## 🔀 Git 상태")
        result_parts.append("")

        if git_status["is_git"]:
            result_parts.append(f"- **브랜치**: `{git_status['branch'] or 'unknown'}`")
            if git_status["has_changes"]:
                result_parts.append("- **변경**: 있음 (최근 활동)")
        else:
            result_parts.append("Git 저장소가 아닙니다.")

        result_parts.append("")

    # ============================================================
    # Step 4: CLAUDE.md 규칙 (normal 이상)
    # ============================================================
    if depth in ["normal", "full"]:
        claude_md_path = path / "CLAUDE.md"

        if claude_md_path.exists():
            claude_content = claude_md_path.read_text(encoding="utf-8")
            rules = _extract_rules(claude_content)

            if rules:
                result_parts.append("## 📜 핵심 규칙")
                result_parts.append("")
                for rule in rules:
                    result_parts.append(f"- {rule}")
                result_parts.append("")

    # ============================================================
    # Step 5: PRD 요약 + 최근 파일 (full만)
    # ============================================================
    if depth == "full":
        # PRD 찾기
        prd_paths = [
            path / "docs" / "PRD.md",
            path / "PRD.md",
            path / "docs" / "prd.md"
        ]

        for prd_path in prd_paths:
            if prd_path.exists():
                prd_content = prd_path.read_text(encoding="utf-8")
                prd_summary = _extract_prd_summary(prd_content)

                if prd_summary:
                    result_parts.append("## 📄 PRD 요약")
                    result_parts.append("")
                    result_parts.append(prd_summary)
                    result_parts.append("")
                break

        # 최근 수정 파일
        recent_files = _get_recent_modified_files(path)

        if recent_files:
            result_parts.append("## 📁 최근 수정 파일")
            result_parts.append("")
            for f in recent_files:
                result_parts.append(f"- `{f}`")
            result_parts.append("")

    # ============================================================
    # 다음 액션 가이드
    # ============================================================
    result_parts.append("---")
    result_parts.append("")
    result_parts.append("## 🎯 다음 액션")
    result_parts.append("")

    if locked_plans := [p for p in plans if p["status"] == "locked"]:
        plan = locked_plans[0]
        result_parts.append(f"1. **활성 계획 계속**: `{plan['file']}` 읽기")
        if plan["current_step"]:
            result_parts.append(f"2. **현재 Step {plan['current_step']}** 진행")
    elif summary.get("next_todos"):
        result_parts.append(f"1. **다음 할 일**: {summary['next_todos'][0]}")
    else:
        result_parts.append("1. `current.md` 확인 또는 `/plan` 으로 새 계획 수립")

    return [TextContent(type="text", text="\n".join(result_parts))]
