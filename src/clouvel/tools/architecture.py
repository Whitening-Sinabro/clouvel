# -*- coding: utf-8 -*-
"""
Clouvel Architecture Guard Tools (v1.8)

아키텍처 가드 도구:
- arch_check: 새 코드 추가 전 기존 코드 검색
- check_imports: Import 규칙 검증
- check_duplicates: 중복 정의 감지

아키텍처 결정 #30, #40 기반
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def arch_check(
    name: str,
    purpose: str,
    path: str = "."
) -> Dict[str, Any]:
    """새 코드 추가 전 기존 코드 확인

    Args:
        name: 추가하려는 함수/클래스명
        purpose: 목적 설명
        path: 프로젝트 경로

    Returns:
        검색 결과 및 권장 사항
    """
    result = {
        "name": name,
        "purpose": purpose,
        "existing_code": [],
        "kb_decisions": [],
        "recommendation": "",
        "can_add": True,
    }

    project_path = Path(path).resolve()

    # 1. Knowledge Base에서 관련 결정 검색
    try:
        # db.knowledge의 sync 버전 사용 (tools.knowledge는 async)
        from ..db.knowledge import search_knowledge as kb_search
        kb_results = kb_search(name, limit=5)
        for r in kb_results:
            if r.get("type") == "location":
                result["existing_code"].append({
                    "source": "knowledge_base",
                    "name": r.get("name", ""),
                    "path": r.get("path", ""),
                    "description": r.get("description", ""),
                })
            elif r.get("type") == "decision":
                result["kb_decisions"].append({
                    "category": r.get("category", ""),
                    "content": r.get("content", "")[:200],
                })
    except Exception:
        pass  # KB 사용 불가 시 skip

    # 2. Grep으로 같은 이름 검색
    try:
        # def name( 또는 class name( 패턴 검색
        grep_result = subprocess.run(
            ["grep", "-rn", f"(def|class) {name}", str(project_path / "src")],
            capture_output=True,
            text=True,
            timeout=10
        )
        if grep_result.stdout:
            for line in grep_result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(":", 2)
                    if len(parts) >= 2:
                        result["existing_code"].append({
                            "source": "grep",
                            "path": parts[0],
                            "line": parts[1] if len(parts) > 1 else "",
                            "content": parts[2] if len(parts) > 2 else "",
                        })
    except Exception:
        # Windows에서 grep 없을 수 있음, findstr 사용
        try:
            grep_result = subprocess.run(
                ["findstr", "/s", "/n", f"def {name}", str(project_path / "src" / "*.py")],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if grep_result.stdout:
                for line in grep_result.stdout.strip().split("\n"):
                    if line:
                        result["existing_code"].append({
                            "source": "findstr",
                            "content": line,
                        })
        except Exception:
            pass

    # 3. __init__.py에서 export 확인
    init_files = list(project_path.glob("src/**/__init__.py"))
    for init_file in init_files:
        try:
            content = init_file.read_text(encoding="utf-8")
            if f'"{name}"' in content or f"'{name}'" in content or f" {name}," in content or f" {name}" in content:
                result["existing_code"].append({
                    "source": "init_export",
                    "path": str(init_file),
                    "note": f"'{name}' exported in __init__.py",
                })
        except Exception:
            pass

    # 4. 권장 사항 생성
    if result["existing_code"]:
        result["can_add"] = False
        locations = [e.get("path", e.get("content", "")) for e in result["existing_code"][:3]]
        result["recommendation"] = f"""## ⚠️ 기존 코드 발견

'{name}' 이미 존재합니다.

### 발견된 위치
{chr(10).join(f'- {loc}' for loc in locations)}

### 권장 사항
**새로 추가하지 말고 기존 코드를 수정하세요.**

1. 위 위치에서 기존 구현 확인
2. 필요하면 기존 코드 수정/확장
3. 중복 정의는 충돌을 유발함 (아키텍처 결정 #30)
"""
    else:
        result["can_add"] = True
        result["recommendation"] = f"""## ✅ 추가 가능

'{name}'은(는) 기존 코드에 없습니다.

### 추가 후 할 일
1. `record_location(name="{name}", repo="clouvel", path="<파일경로>")` 호출
2. 적절한 `__init__.py`에서 export
3. 단일 위치에서만 export (아키텍처 결정 #30)
"""

    # 5. formatted_output 생성
    output_lines = [
        f"# arch_check: {name}",
        "",
        f"**목적**: {purpose}",
        "",
        result["recommendation"],
    ]

    if result["kb_decisions"]:
        output_lines.append("\n### 관련 과거 결정")
        for d in result["kb_decisions"][:3]:
            output_lines.append(f"- [{d['category']}] {d['content'][:100]}...")

    result["formatted_output"] = "\n".join(output_lines)
    return result


def check_imports(path: str = ".") -> Dict[str, Any]:
    """server.py의 import 패턴 검증

    아키텍처 결정 #30:
    - ✅ from .tools import xxx
    - ❌ from .tools.manager import xxx
    - ❌ from .tools.xxx.yyy import zzz

    Args:
        path: 프로젝트 경로

    Returns:
        검증 결과
    """
    project_path = Path(path).resolve()
    server_file = project_path / "src" / "clouvel" / "server.py"

    result = {
        "valid": True,
        "violations": [],
        "warnings": [],
        "checked_file": str(server_file),
    }

    if not server_file.exists():
        result["valid"] = False
        result["warnings"].append(f"server.py not found at {server_file}")
        result["formatted_output"] = f"⚠️ server.py not found at {server_file}"
        return result

    try:
        content = server_file.read_text(encoding="utf-8")
    except Exception as e:
        result["valid"] = False
        result["warnings"].append(f"Cannot read server.py: {e}")
        result["formatted_output"] = f"⚠️ Cannot read server.py: {e}"
        return result

    # 패턴 검사
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # 허용: from .tools import xxx
        # 금지: from .tools.xxx import yyy (xxx가 폴더인 경우)
        # 예외: try-except 블록 내부는 허용 (fallback용)

        if "from .tools." in line and " import " in line:
            # from .tools.xxx import 패턴
            match = re.search(r"from \.tools\.(\w+)", line)
            if match:
                submodule = match.group(1)
                # 허용된 단일 파일 모듈들
                allowed_files = ["ship", "errors", "knowledge", "tracking", "start", "core", "docs"]

                if submodule not in allowed_files:
                    # from .tools.manager.xxx import 같은 깊은 import
                    if ".tools." in line and line.count(".") > 2:
                        result["violations"].append({
                            "line": i,
                            "content": line.strip(),
                            "reason": f"Deep import from tools/{submodule}/ - use tools/__init__.py",
                            "suggestion": f"Move import to tools/__init__.py and use: from .tools import {submodule}",
                        })

    if result["violations"]:
        result["valid"] = False

    # formatted_output 생성
    output_lines = [
        "# check_imports 결과",
        "",
        f"**파일**: {server_file}",
        f"**상태**: {'✅ PASS' if result['valid'] else '❌ FAIL'}",
        "",
    ]

    if result["violations"]:
        output_lines.append("## 위반 사항")
        output_lines.append("")
        for v in result["violations"]:
            output_lines.append(f"### Line {v['line']}")
            output_lines.append(f"```python")
            output_lines.append(v["content"])
            output_lines.append("```")
            output_lines.append(f"**이유**: {v['reason']}")
            output_lines.append(f"**수정 방법**: {v['suggestion']}")
            output_lines.append("")
    else:
        output_lines.append("모든 import가 아키텍처 규칙을 준수합니다.")

    output_lines.append("")
    output_lines.append("---")
    output_lines.append("**규칙 (아키텍처 결정 #30)**:")
    output_lines.append("- ✅ `from .tools import xxx`")
    output_lines.append("- ❌ `from .tools.xxx.yyy import zzz`")

    result["formatted_output"] = "\n".join(output_lines)
    return result


def check_duplicates(path: str = ".") -> Dict[str, Any]:
    """같은 함수명이 여러 곳에 정의되었는지 확인

    Args:
        path: 프로젝트 경로

    Returns:
        중복 검사 결과
    """
    project_path = Path(path).resolve()
    tools_dir = project_path / "src" / "clouvel" / "tools"

    result = {
        "duplicates": [],
        "all_exports": {},
        "valid": True,
    }

    if not tools_dir.exists():
        result["formatted_output"] = f"⚠️ tools directory not found at {tools_dir}"
        return result

    # 모든 __init__.py에서 export된 이름 수집
    init_files = list(tools_dir.glob("**/__init__.py"))

    for init_file in init_files:
        try:
            content = init_file.read_text(encoding="utf-8")
            relative_path = init_file.relative_to(tools_dir)

            # __all__ = [...] 패턴 찾기
            all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if all_match:
                all_content = all_match.group(1)
                # 문자열 추출
                exports = re.findall(r'["\'](\w+)["\']', all_content)
                for exp in exports:
                    if exp not in result["all_exports"]:
                        result["all_exports"][exp] = []
                    result["all_exports"][exp].append(str(relative_path))

            # from xxx import yyy 패턴에서 re-export 찾기
            from_imports = re.findall(r"from \.\w+ import (.*?)$", content, re.MULTILINE)
            for imp in from_imports:
                names = [n.strip() for n in imp.split(",")]
                for name in names:
                    # 'as' 처리
                    if " as " in name:
                        name = name.split(" as ")[1].strip()
                    name = name.strip()
                    if name and name.isidentifier():
                        if name not in result["all_exports"]:
                            result["all_exports"][name] = []
                        if str(relative_path) not in result["all_exports"][name]:
                            result["all_exports"][name].append(str(relative_path))

        except Exception:
            pass

    # 중복 찾기
    for name, locations in result["all_exports"].items():
        if len(locations) > 1:
            # tools/__init__.py와 다른 곳에서 동시에 export되면 중복
            if "__init__.py" in locations and len(locations) > 1:
                # tools/__init__.py는 re-export이므로 제외
                other_locations = [loc for loc in locations if loc != "__init__.py"]
                if len(other_locations) >= 1:
                    result["duplicates"].append({
                        "name": name,
                        "locations": locations,
                    })

    if result["duplicates"]:
        result["valid"] = False

    # formatted_output 생성
    output_lines = [
        "# check_duplicates 결과",
        "",
        f"**상태**: {'✅ PASS' if result['valid'] else '⚠️ 중복 발견'}",
        "",
    ]

    if result["duplicates"]:
        output_lines.append("## 중복 정의")
        output_lines.append("")
        for d in result["duplicates"]:
            output_lines.append(f"### `{d['name']}`")
            for loc in d["locations"]:
                output_lines.append(f"- tools/{loc}")
            output_lines.append("")
        output_lines.append("**권장**: 단일 위치에서만 export (아키텍처 결정 #30)")
    else:
        output_lines.append("중복 정의가 없습니다.")

    result["formatted_output"] = "\n".join(output_lines)
    return result
