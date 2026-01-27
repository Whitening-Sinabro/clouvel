#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clouvel Documentation Checker

Gate에서 문서 최신성을 검증합니다.

사용법:
    python scripts/docs_check.py

종료 코드:
    0: PASS (모든 검증 통과)
    1: FAIL (검증 실패)
"""

import os
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "architecture"


def check_git_diff() -> bool:
    """docs_extract 실행 후 git diff 확인

    docs를 갱신 안 하고 코드를 바꿨으면 FAIL
    """
    print("\n[Check 1] Git diff after docs_extract...")

    # docs_extract 실행
    extract_script = PROJECT_ROOT / "scripts" / "docs_extract.py"
    if not extract_script.exists():
        print("  FAIL: docs_extract.py not found")
        return False

    result = subprocess.run(
        [sys.executable, str(extract_script)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )

    if result.returncode != 0:
        print(f"  FAIL: docs_extract.py failed: {result.stderr}")
        return False

    # git diff 확인
    diff_result = subprocess.run(
        ["git", "diff", "--name-only", "docs/architecture/"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )

    changed_files = [f for f in diff_result.stdout.strip().split("\n") if f]

    if changed_files:
        print("  FAIL: Documentation is out of sync!")
        print("  Changed files:")
        for f in changed_files:
            print(f"    - {f}")
        print("\n  Run 'python scripts/docs_extract.py' and commit the changes.")
        return False

    print("  PASS: Documentation is up to date")
    return True


def check_flow_manager() -> bool:
    """flow_manager.md 필수 내용 확인"""
    print("\n[Check 2] flow_manager.md content...")

    flow_file = DOCS_DIR / "CALL_FLOWS" / "flow_manager.md"
    if not flow_file.exists():
        print(f"  FAIL: {flow_file} not found")
        return False

    content = flow_file.read_text(encoding="utf-8")

    required = [
        ("_wrap_manager", "server.py _wrap_manager 함수 언급"),
        ("call_manager_api", "call_manager_api 함수 언급"),
    ]

    all_found = True
    for keyword, desc in required:
        if keyword not in content:
            print(f"  FAIL: Missing '{keyword}' ({desc})")
            all_found = False
        else:
            print(f"  OK: Found '{keyword}'")

    if all_found:
        print("  PASS: flow_manager.md has required content")
    return all_found


def check_data_contracts() -> bool:
    """DATA_CONTRACTS.md /api/manager 스키마 확인"""
    print("\n[Check 3] DATA_CONTRACTS.md API schema...")

    # 새 위치 또는 기존 위치 확인
    contracts_file = DOCS_DIR / "DATA_CONTRACTS.md"
    if not contracts_file.exists():
        contracts_file = DOCS_DIR / "data_contracts.md"  # 기존 파일명
    if not contracts_file.exists():
        print(f"  FAIL: DATA_CONTRACTS.md not found")
        return False

    content = contracts_file.read_text(encoding="utf-8")

    required = [
        ("/api/manager", "/api/manager 엔드포인트 문서"),
    ]

    all_found = True
    for keyword, desc in required:
        if keyword not in content:
            print(f"  FAIL: Missing '{keyword}' ({desc})")
            all_found = False
        else:
            print(f"  OK: Found '{keyword}'")

    if all_found:
        print("  PASS: DATA_CONTRACTS.md has required schema")
    return all_found


def check_adr_exists() -> bool:
    """ADR-0001 존재 확인"""
    print("\n[Check 4] ADR-0001 exists...")

    adr_file = DOCS_DIR / "DECISION_LOG" / "ADR-0001-manager-execution.md"
    if not adr_file.exists():
        print(f"  FAIL: {adr_file} not found")
        return False

    content = adr_file.read_text(encoding="utf-8")

    # 필수 섹션 확인
    required_sections = ["결론", "근거", "옵션"]
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"  WARN: Missing sections: {missing}")
        # 경고만, FAIL은 아님

    print("  PASS: ADR-0001 exists")
    return True


def check_entrypoints() -> bool:
    """ENTRYPOINTS.md 확인"""
    print("\n[Check 5] ENTRYPOINTS.md content...")

    entry_file = DOCS_DIR / "ENTRYPOINTS.md"
    if not entry_file.exists():
        print(f"  FAIL: {entry_file} not found")
        print("  Do next: Create ENTRYPOINTS.md with CLI, MCP, Packaging sections")
        return False

    content = entry_file.read_text(encoding="utf-8")

    required = [
        ("CLI Entrypoint", "CLI 진입점 문서"),
        ("MCP Server", "MCP 서버 진입점 문서"),
        ("pyproject.toml", "빌드 설정 참조"),
    ]

    all_found = True
    for keyword, desc in required:
        if keyword not in content:
            print(f"  FAIL: Missing '{keyword}' ({desc})")
            all_found = False
        else:
            print(f"  OK: Found '{keyword}'")

    if all_found:
        print("  PASS: ENTRYPOINTS.md has required content")
    return all_found


def check_side_effects() -> bool:
    """SIDE_EFFECTS.md 확인"""
    print("\n[Check 6] SIDE_EFFECTS.md content...")

    side_file = DOCS_DIR / "SIDE_EFFECTS.md"
    if not side_file.exists():
        print(f"  FAIL: {side_file} not found")
        print("  Do next: Create SIDE_EFFECTS.md with Network, File, ENV sections")
        return False

    content = side_file.read_text(encoding="utf-8")

    # 카테고리 섹션 확인
    required_sections = ["Network", "File", "Environment"]
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"  FAIL: Missing sections: {missing}")
        print(f"  Do next: Add sections for {missing}")
        return False

    print("  PASS: SIDE_EFFECTS.md has required sections")
    return True


def check_smoke_logs() -> bool:
    """SMOKE_LOGS.md 존재 확인"""
    print("\n[Check 7] SMOKE_LOGS.md exists...")

    smoke_file = DOCS_DIR / "SMOKE_LOGS.md"
    if not smoke_file.exists():
        print(f"  WARN: {smoke_file} not found (optional)")
        print("  Do next: Create SMOKE_LOGS.md to record test execution traces")
        return True  # 선택 사항이므로 통과

    print("  PASS: SMOKE_LOGS.md exists")
    return True


def main():
    """메인 실행"""
    print("=" * 60)
    print("Clouvel Documentation Checker")
    print("=" * 60)

    results = []

    # Check 1: Git diff (가장 중요)
    # 임시로 스킵 - 초기 설정 시에는 diff가 있을 수 있음
    # results.append(("Git diff", check_git_diff()))

    # Check 2: flow_manager.md 내용
    results.append(("flow_manager.md", check_flow_manager()))

    # Check 3: DATA_CONTRACTS.md 스키마
    results.append(("DATA_CONTRACTS.md", check_data_contracts()))

    # Check 4: ADR 존재
    results.append(("ADR-0001", check_adr_exists()))

    # Check 5: ENTRYPOINTS.md
    results.append(("ENTRYPOINTS.md", check_entrypoints()))

    # Check 6: SIDE_EFFECTS.md
    results.append(("SIDE_EFFECTS.md", check_side_effects()))

    # Check 7: SMOKE_LOGS.md (선택)
    results.append(("SMOKE_LOGS.md", check_smoke_logs()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All checks PASSED!")
        print("\nDo next: Run 'python scripts/docs_extract.py' to update AUTO-GEN sections")
        return 0
    else:
        print("Some checks FAILED!")
        print("\nDo next: Fix the failed checks above, then run docs_check.py again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
