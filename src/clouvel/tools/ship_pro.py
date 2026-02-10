# Clouvel Ship Tool (Pro)
# 원클릭 테스트 → 검증 → 증거 생성

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Rich UI (optional)
try:
    from clouvel.ui import render_ship_result, HAS_RICH
except ImportError:
    HAS_RICH = False
    render_ship_result = None

# 기본 테스트 명령어 (프로젝트 타입별)
DEFAULT_TEST_COMMANDS = {
    "python": {
        "lint": "ruff check .",
        "typecheck": "mypy .",
        "test": "pytest",
        "build": "pip install -e ."
    },
    "node": {
        "lint": "npm run lint",
        "typecheck": "npm run typecheck",
        "test": "npm test",
        "build": "npm run build"
    },
    "bun": {
        "lint": "bun run lint",
        "typecheck": "bun run typecheck",
        "test": "bun test",
        "build": "bun run build"
    }
}


def ship(
    path: str,
    feature: str = "",
    steps: List[str] = None,
    generate_evidence: bool = True,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    원클릭으로 테스트, 검증, 증거 생성을 수행합니다.

    단계:
    1. lint - 코드 스타일 검사
    2. typecheck - 타입 검사
    3. test - 테스트 실행
    4. build - 빌드 검증
    5. evidence - 결과 증거 생성

    Args:
        path: 프로젝트 루트 경로
        feature: 검증할 기능명 (옵션)
        steps: 실행할 단계 ['lint', 'typecheck', 'test', 'build']
        generate_evidence: 증거 파일 생성 여부
        auto_fix: lint 에러 자동 수정 시도 여부

    Returns:
        각 단계별 결과 및 최종 상태
    """
    project_path = Path(path).resolve()

    result = {
        "status": "UNKNOWN",
        "project_path": str(project_path),
        "feature": feature,
        "timestamp": datetime.now().isoformat(),
        "steps": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        },
        "evidence": None,
        "can_ship": False
    }

    # 프로젝트 타입 감지
    project_type = _detect_project_type(project_path)
    result["project_type"] = project_type

    if not project_type:
        result["status"] = "ERROR"
        result["error"] = "프로젝트 타입을 감지할 수 없습니다"
        return result

    # v3.1: 상업용 안전장치 검사 (ship 전에)
    safety_check = _run_safety_checks(project_path)
    result["safety"] = safety_check

    if safety_check.get("blocked"):
        result["status"] = "BLOCKED"
        result["can_ship"] = False
        result["error"] = "안전장치 검사 실패"
        result["formatted_output"] = _format_safety_block(safety_check)
        return result

    # 기본 단계
    if steps is None:
        steps = ["lint", "typecheck", "test", "build"]

    result["summary"]["total"] = len(steps)

    # 명령어 매핑
    commands = _get_commands(project_path, project_type)

    # 각 단계 실행
    all_passed = True
    for step in steps:
        if step not in commands:
            result["steps"][step] = {
                "status": "SKIPPED",
                "message": f"명령어 없음: {step}"
            }
            result["summary"]["skipped"] += 1
            continue

        step_result = _run_step(
            project_path,
            step,
            commands[step],
            auto_fix=(auto_fix and step == "lint")
        )
        result["steps"][step] = step_result

        if step_result["status"] == "PASS":
            result["summary"]["passed"] += 1
        else:
            result["summary"]["failed"] += 1
            all_passed = False

    # 최종 상태 결정
    if all_passed:
        result["status"] = "PASS"
        result["can_ship"] = True
    elif result["summary"]["passed"] > 0:
        result["status"] = "PARTIAL"
        result["can_ship"] = False
    else:
        result["status"] = "FAIL"
        result["can_ship"] = False

    # 증거 생성
    if generate_evidence:
        evidence = _generate_evidence(result, project_path)
        result["evidence"] = evidence

    # 포맷팅된 출력
    result["formatted_output"] = _format_ship_result(result)

    return result


def _detect_project_type(project_path: Path) -> Optional[str]:
    """프로젝트 타입을 감지합니다."""
    if (project_path / "pyproject.toml").exists() or (project_path / "setup.py").exists():
        return "python"
    if (project_path / "bun.lockb").exists():
        return "bun"
    if (project_path / "package.json").exists():
        return "node"
    return None


def _get_commands(project_path: Path, project_type: str) -> Dict[str, str]:
    """프로젝트의 실행 명령어를 가져옵니다."""
    commands = DEFAULT_TEST_COMMANDS.get(project_type, {}).copy()

    # package.json에서 스크립트 확인
    if project_type in ["node", "bun"]:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package = json.load(f)
                    scripts = package.get("scripts", {})

                    # 사용 가능한 스크립트로 업데이트
                    runner = "bun run" if project_type == "bun" else "npm run"
                    if "lint" in scripts:
                        commands["lint"] = f"{runner} lint"
                    if "typecheck" in scripts:
                        commands["typecheck"] = f"{runner} typecheck"
                    if "test" in scripts:
                        commands["test"] = f"{runner} test"
                    if "build" in scripts:
                        commands["build"] = f"{runner} build"
            except Exception:
                pass

    # pyproject.toml에서 스크립트 확인
    if project_type == "python":
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            # ruff 사용 여부 확인
            content = pyproject_path.read_text(encoding="utf-8")
            if "ruff" in content:
                commands["lint"] = "ruff check ."
            if "mypy" in content:
                commands["typecheck"] = "mypy ."
            if "pytest" in content:
                commands["test"] = "pytest"

    return commands


def _run_step(
    project_path: Path,
    step: str,
    command: str,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """개별 단계를 실행합니다."""
    step_result = {
        "status": "UNKNOWN",
        "command": command,
        "output": "",
        "error": "",
        "duration_ms": 0
    }

    # auto_fix 모드에서 lint
    if auto_fix and step == "lint":
        fix_command = command.replace("check", "check --fix")
        if fix_command != command:
            command = fix_command
            step_result["command"] = command
            step_result["auto_fix"] = True

    start_time = datetime.now()

    try:
        # Windows에서는 shell=True 필요
        result = subprocess.run(
            command,
            cwd=str(project_path),
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )

        step_result["output"] = result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout
        step_result["error"] = result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr
        step_result["return_code"] = result.returncode

        if result.returncode == 0:
            step_result["status"] = "PASS"
        else:
            step_result["status"] = "FAIL"

    except subprocess.TimeoutExpired:
        step_result["status"] = "TIMEOUT"
        step_result["error"] = "명령어 실행 시간 초과 (5분)"

    except Exception as e:
        step_result["status"] = "ERROR"
        step_result["error"] = str(e)

    end_time = datetime.now()
    step_result["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

    return step_result


def _generate_evidence(result: Dict, project_path: Path) -> Dict[str, Any]:
    """검증 증거를 생성합니다.

    v3.1: COMPLETION_REPORT.md도 프로젝트 루트에 생성
    """
    evidence = {
        "generated_at": datetime.now().isoformat(),
        "file_path": None,
        "completion_report_path": None,
        "content": ""
    }

    # 증거 내용 생성
    lines = []
    lines.append("# Ship Evidence")
    lines.append("")
    lines.append(f"**프로젝트**: {project_path.name}")
    lines.append(f"**기능**: {result.get('feature', 'N/A')}")
    lines.append(f"**생성 시간**: {evidence['generated_at']}")
    lines.append(f"**최종 상태**: {result['status']}")
    lines.append("")

    # 요약
    lines.append("## 요약")
    lines.append("")
    lines.append(f"- 총 단계: {result['summary']['total']}")
    lines.append(f"- 통과: {result['summary']['passed']}")
    lines.append(f"- 실패: {result['summary']['failed']}")
    lines.append(f"- 스킵: {result['summary']['skipped']}")
    lines.append("")

    # 상세 결과
    lines.append("## 상세 결과")
    lines.append("")

    for step, step_result in result["steps"].items():
        status_emoji = "✅" if step_result["status"] == "PASS" else "❌" if step_result["status"] == "FAIL" else "⏭️"
        lines.append(f"### {status_emoji} {step.upper()}")
        lines.append("")
        lines.append(f"- **명령어**: `{step_result.get('command', 'N/A')}`")
        lines.append(f"- **상태**: {step_result['status']}")
        lines.append(f"- **소요 시간**: {step_result.get('duration_ms', 0)}ms")

        if step_result.get("error"):
            lines.append("")
            lines.append("**에러:**")
            lines.append("```")
            lines.append(step_result["error"][:500])
            lines.append("```")

        lines.append("")

    # Ship 가능 여부
    lines.append("## 결론")
    lines.append("")
    if result["can_ship"]:
        lines.append("✅ **Ship 가능** - 모든 검증 통과")
    else:
        lines.append("❌ **Ship 불가** - 아래 항목 수정 필요:")
        for step, step_result in result["steps"].items():
            if step_result["status"] != "PASS":
                lines.append(f"  - {step}: {step_result['status']}")

    evidence["content"] = "\n".join(lines)

    # 파일로 저장
    evidence_dir = project_path / ".claude" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    feature_slug = result.get("feature", "ship").replace(" ", "_").lower()
    evidence_file = evidence_dir / f"{feature_slug}_{timestamp}.md"

    try:
        evidence_file.write_text(evidence["content"], encoding="utf-8")
        evidence["file_path"] = str(evidence_file)
    except Exception as e:
        evidence["error"] = f"파일 저장 실패: {e}"

    # v3.1: COMPLETION_REPORT.md 생성 (프로젝트 루트에)
    completion_report = _generate_completion_report(result, project_path)
    evidence["completion_report_path"] = completion_report.get("file_path")
    evidence["completion_report_content"] = completion_report.get("content")

    # v3.1: EVIDENCE.md 생성 (프로젝트 루트에)
    evidence_md_path = _write_evidence_md(result, project_path)
    evidence["evidence_md_path"] = evidence_md_path

    return evidence


def _write_evidence_md(result: Dict, project_path: Path) -> str:
    """EVIDENCE.md 생성 (v3.1 - 프로젝트 루트에)

    AC 테이블에서 명확하게 근거를 확인할 수 있는 포맷.

    Returns:
        생성된 파일 경로 (str)
    """
    lines = []
    lines.append("# Evidence")
    lines.append("")
    lines.append(f"- **Timestamp**: {datetime.utcnow().isoformat()}Z")
    lines.append(f"- **Feature**: {result.get('feature', 'N/A')}")
    lines.append(f"- **Project**: {project_path.name}")
    lines.append(f"- **Status**: {result.get('status', 'UNKNOWN')}")
    lines.append("")

    # Verdict
    can_ship = result.get("can_ship", False)
    lines.append(f"## Verdict: {'SHIP READY' if can_ship else 'NOT READY'}")
    lines.append("")

    # Safety section
    safety = result.get("safety", {})
    if safety:
        lines.append("## Safety Checks")
        lines.append("")
        if safety.get("blocked"):
            lines.append("- **Status**: BLOCKED")
        else:
            lines.append("- **Status**: PASSED")
        if safety.get("warnings"):
            for warn in safety["warnings"]:
                lines.append(f"- Warning: {warn}")
        lines.append("")

    # Step Results table
    lines.append("## Step Results")
    lines.append("")
    lines.append("| Step | Status | Command | Duration |")
    lines.append("|------|--------|---------|----------|")

    for step_name, step_data in result.get("steps", {}).items():
        status = step_data.get("status", "SKIP")
        status_icon = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "SKIP"
        cmd = step_data.get("command", "N/A")
        duration = step_data.get("duration_ms", 0)
        lines.append(f"| {step_name.upper()} | {status_icon} | `{cmd}` | {duration}ms |")

    lines.append("")

    # Summary
    summary = result.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Steps**: {summary.get('total', 0)}")
    lines.append(f"- **Passed**: {summary.get('passed', 0)}")
    lines.append(f"- **Failed**: {summary.get('failed', 0)}")
    lines.append(f"- **Skipped**: {summary.get('skipped', 0)}")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("*Generated by Clouvel Pro `ship` tool*")

    content = "\n".join(lines)

    # Write to project root
    evidence_path = project_path / "EVIDENCE.md"
    try:
        evidence_path.write_text(content, encoding="utf-8")
        return str(evidence_path)
    except Exception as e:
        return f"ERROR: {e}"


def _generate_completion_report(result: Dict, project_path: Path) -> Dict[str, Any]:
    """COMPLETION_REPORT.md 생성 (v3.1 - Pro 유료 기능 핵심)

    AC 기준 PASS 근거를 담은 리포트.
    ship PASS 시에만 생성.

    Returns:
        {"file_path": str, "content": str}
    """
    report = {
        "file_path": None,
        "content": ""
    }

    # PASS가 아니면 리포트 생성하지 않음
    if not result.get("can_ship", False):
        return report

    lines = []
    lines.append("# Completion Report")
    lines.append("")
    lines.append(f"> Generated: {datetime.now().isoformat()}")
    lines.append(f"> Project: {project_path.name}")
    lines.append(f"> Feature: {result.get('feature', 'N/A')}")
    lines.append("")

    # Status Badge
    lines.append("## Status: ✅ SHIP READY")
    lines.append("")

    # AC Criteria (Acceptance Criteria)
    lines.append("## Acceptance Criteria Verification")
    lines.append("")
    lines.append("| Criteria | Status | Evidence |")
    lines.append("|----------|--------|----------|")

    for step, step_result in result.get("steps", {}).items():
        status = "✅ PASS" if step_result.get("status") == "PASS" else "❌ FAIL"
        command = step_result.get("command", "N/A")
        duration = step_result.get("duration_ms", 0)
        lines.append(f"| {step.upper()} | {status} | `{command}` ({duration}ms) |")

    lines.append("")

    # Summary
    summary = result.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Steps**: {summary.get('total', 0)}")
    lines.append(f"- **Passed**: {summary.get('passed', 0)}")
    lines.append(f"- **Failed**: {summary.get('failed', 0)}")
    lines.append(f"- **Skipped**: {summary.get('skipped', 0)}")
    lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")
    lines.append("All acceptance criteria have been verified. This feature is ready to ship.")
    lines.append("")
    lines.append("### Next Steps")
    lines.append("1. `git add . && git commit -m \"feat: ...\"` ")
    lines.append("2. Create PR or deploy directly")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("*Generated by Clouvel Pro `ship` tool*")

    report["content"] = "\n".join(lines)

    # Save to project root
    report_path = project_path / "COMPLETION_REPORT.md"
    try:
        report_path.write_text(report["content"], encoding="utf-8")
        report["file_path"] = str(report_path)
    except Exception as e:
        report["error"] = f"COMPLETION_REPORT 저장 실패: {e}"

    return report


def _format_ship_result(result: Dict) -> str:
    """결과를 읽기 좋은 형식으로 포맷팅합니다.

    v1.9.1: Rich UI support.
    """
    # Use Rich UI if available
    if HAS_RICH and render_ship_result:
        return _format_ship_result_rich(result)

    # Fallback to plain text
    return _format_ship_result_plain(result)


def _format_ship_result_rich(result: Dict) -> str:
    """Rich UI version of ship result."""
    # Build steps_summary dict for render_ship_result
    steps_summary = {}
    for step, step_result in result.get("steps", {}).items():
        status = step_result.get("status", "skip")
        if status == "PASS":
            steps_summary[step.upper()] = "pass"
        elif status == "FAIL":
            steps_summary[step.upper()] = "fail"
        else:
            steps_summary[step.upper()] = "skip"

    # Evidence path
    evidence_path = result.get("evidence", {}).get("file_path")

    return render_ship_result(
        passed=result.get("can_ship", False),
        steps_summary=steps_summary,
        evidence_path=evidence_path,
    )


def _format_ship_result_plain(result: Dict) -> str:
    """Plain text version of ship result (original implementation)."""
    lines = []

    # 헤더
    if result["can_ship"]:
        lines.append("🚀" + "=" * 48)
        lines.append("   SHIP READY - 배포 준비 완료!")
        lines.append("=" * 50)
    else:
        lines.append("⛔" + "=" * 48)
        lines.append("   SHIP BLOCKED - 수정 필요")
        lines.append("=" * 50)

    lines.append("")

    # 요약 바
    summary = result["summary"]
    lines.append(f"[{'█' * summary['passed']}{'░' * summary['failed']}{'·' * summary['skipped']}] {summary['passed']}/{summary['total']} PASS")
    lines.append("")

    # 각 단계 상태
    for step, step_result in result["steps"].items():
        status = step_result["status"]
        if status == "PASS":
            icon = "✅"
        elif status == "FAIL":
            icon = "❌"
        elif status == "SKIPPED":
            icon = "⏭️"
        else:
            icon = "⚠️"

        duration = step_result.get("duration_ms", 0)
        lines.append(f"  {icon} {step.upper():12} {status:8} ({duration}ms)")

        # 실패 시 간단한 에러 표시
        if status == "FAIL" and step_result.get("error"):
            error_preview = step_result["error"].split("\n")[0][:60]
            lines.append(f"      └─ {error_preview}...")

    lines.append("")

    # 증거 파일
    if result.get("evidence", {}).get("file_path"):
        lines.append(f"📋 Evidence: {result['evidence']['file_path']}")
    if result.get("evidence", {}).get("completion_report_path"):
        lines.append(f"📄 Completion Report: {result['evidence']['completion_report_path']}")
    if result.get("evidence"):
        lines.append("")

    # 다음 단계
    if result["can_ship"]:
        lines.append("✨ 다음 단계:")
        lines.append("   1. git add && git commit")
        lines.append("   2. PR 생성 또는 직접 배포")
    else:
        lines.append("🔧 수정 필요:")
        for step, step_result in result["steps"].items():
            if step_result["status"] == "FAIL":
                lines.append(f"   - {step} 에러 수정")

    return "\n".join(lines)


# 빠른 ship (lint + test만)
def quick_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """빠른 ship - lint와 test만 실행합니다."""
    return ship(
        path=path,
        feature=feature,
        steps=["lint", "test"],
        generate_evidence=True
    )


# 전체 ship (모든 단계)
def full_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """전체 ship - 모든 검증 단계를 실행합니다."""
    return ship(
        path=path,
        feature=feature,
        steps=["lint", "typecheck", "test", "build"],
        generate_evidence=True,
        auto_fix=True
    )


# ============================================================
# v3.1: 상업용 안전장치 (Commercial Safety Checks)
# ============================================================

# 시크릿 파일 패턴 (커밋/배포 금지)
SECRET_PATTERNS = [
    ".env",
    ".env.local",
    ".env.production",
    "*.key",
    "*.pem",
    "*.secret",
    "credentials.json",
    "secrets.json",
    "license*.json",
]

# 시크릿 내용 패턴 (파일 내용에서 검색)
SECRET_CONTENT_PATTERNS = [
    r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"(?i)(secret[_-]?key|secretkey)\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{4,}['\"]",
    r"(?i)(access[_-]?token|accesstoken)\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI API key
    r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*",  # Bearer token
]


def _run_safety_checks(project_path: Path) -> Dict[str, Any]:
    """상업용 안전장치 검사 (v3.1)

    - 시크릿 파일 탐지
    - 시크릿 내용 탐지
    - .env.example 존재 확인

    Returns:
        {
            "blocked": bool,
            "warnings": [],
            "secret_files": [],
            "secret_content": [],
            "env_example": bool
        }
    """
    import re

    result = {
        "blocked": False,
        "warnings": [],
        "secret_files": [],
        "secret_content": [],
        "env_example_exists": False,
    }

    # 1. .env.example 존재 확인 (권장)
    env_example = project_path / ".env.example"
    result["env_example_exists"] = env_example.exists()
    if not result["env_example_exists"]:
        result["warnings"].append(".env.example 파일이 없습니다 (권장)")

    # 2. 시크릿 파일 탐지
    for pattern in SECRET_PATTERNS:
        if "*" in pattern:
            # glob 패턴
            matched = list(project_path.glob(pattern))
            for f in matched:
                if f.is_file() and ".git" not in str(f):
                    result["secret_files"].append(str(f.relative_to(project_path)))
        else:
            # 정확한 파일명
            secret_file = project_path / pattern
            if secret_file.exists() and secret_file.is_file():
                result["secret_files"].append(pattern)

    # 시크릿 파일이 git에 추적되고 있는지 확인
    if result["secret_files"]:
        tracked_secrets = []
        try:
            import subprocess
            for sf in result["secret_files"]:
                check = subprocess.run(
                    ["git", "ls-files", sf],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if check.stdout.strip():
                    tracked_secrets.append(sf)
        except Exception:
            pass

        if tracked_secrets:
            result["blocked"] = True
            result["block_reason"] = f"시크릿 파일이 git에 추적됨: {', '.join(tracked_secrets)}"

    # 3. 소스 코드에서 시크릿 내용 탐지 (경고만)
    src_dir = project_path / "src"
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in SECRET_CONTENT_PATTERNS:
                    if re.search(pattern, content):
                        rel_path = str(py_file.relative_to(project_path))
                        if rel_path not in result["secret_content"]:
                            result["secret_content"].append(rel_path)
                        break
            except Exception:
                pass

    if result["secret_content"]:
        result["warnings"].append(
            f"시크릿 패턴 발견: {len(result['secret_content'])}개 파일 (하드코딩 금지)"
        )

    return result


def _format_safety_block(safety: Dict) -> str:
    """안전장치 BLOCK 결과 포맷팅"""
    lines = [
        "⛔" + "=" * 48,
        "   SHIP BLOCKED - 안전장치 검사 실패",
        "=" * 50,
        "",
        f"**이유**: {safety.get('block_reason', 'Unknown')}",
        "",
        "## 시크릿 파일 감지됨",
        "",
    ]

    for sf in safety.get("secret_files", []):
        lines.append(f"  - {sf}")

    lines.append("")
    lines.append("## 수정 방법")
    lines.append("")
    lines.append("1. `.gitignore`에 시크릿 파일 추가")
    lines.append("2. `git rm --cached <파일>` 로 추적 해제")
    lines.append("3. 다시 `ship` 실행")
    lines.append("")
    lines.append("---")
    lines.append("💡 시크릿은 환경변수 또는 `.env` 파일 사용")

    return "\n".join(lines)
