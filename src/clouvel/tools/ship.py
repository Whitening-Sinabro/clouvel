# -*- coding: utf-8 -*-
"""
Clouvel Ship Tool - Pro 전용

원클릭 테스트→검증→증거 생성 도구입니다.

이 기능은 Pro 버전에서만 사용 가능합니다.
구매: https://polar.sh/clouvel
"""

from typing import Dict, Any, List


def ship(
    path: str,
    feature: str = "",
    steps: List[str] = None,
    generate_evidence: bool = True,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    Pro 전용 기능입니다.

    원클릭으로 테스트, 검증, 증거 생성을 수행합니다.
    - lint: 코드 스타일 검사
    - typecheck: 타입 검사
    - test: 테스트 실행
    - build: 빌드 검증

    구매: https://polar.sh/clouvel
    """
    return {
        "error": "Pro 전용 기능입니다",
        "message": "ship 도구는 Pro 버전에서만 사용 가능합니다.",
        "upgrade_url": "https://polar.sh/clouvel",
        "features": [
            "lint/typecheck/test/build 자동 실행",
            "프로젝트 타입 자동 감지",
            "검증 증거 파일 생성",
            "auto_fix 모드",
        ],
        "formatted_output": """
==================================================
🔒 PRO 전용 기능
==================================================

**ship** 도구는 Pro 버전에서만 사용 가능합니다.

### 포함 기능
- 🧪 lint → typecheck → test → build 자동화
- 🔍 프로젝트 타입 자동 감지 (Python/Node/Bun)
- 📋 검증 증거 파일 생성
- 🔧 lint 에러 auto_fix 모드

### 구매
https://polar.sh/clouvel

==================================================
"""
    }


def quick_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """Pro 전용 기능입니다. lint와 test만 빠르게 실행."""
    return ship(path=path, feature=feature)


def full_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """Pro 전용 기능입니다. 모든 검증 단계 + auto_fix."""
    return ship(path=path, feature=feature)
