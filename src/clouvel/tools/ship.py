# Clouvel Ship Tool (Pro)
# 원클릭 테스트 → 검증 → 증거 생성

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

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
    """검증 증거를 생성합니다."""
    evidence = {
        "generated_at": datetime.now().isoformat(),
        "file_path": None,
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

    return evidence


def _format_ship_result(result: Dict) -> str:
    """결과를 읽기 좋은 형식으로 포맷팅합니다."""
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
        lines.append(f"📋 증거 파일: {result['evidence']['file_path']}")
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
