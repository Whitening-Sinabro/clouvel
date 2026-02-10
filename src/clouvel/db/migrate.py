"""Migration from MD files to SQLite for Clouvel Error System v2.0."""

import re
from pathlib import Path
from typing import Optional
from datetime import datetime

from .schema import init_db, get_db_path
from .errors import record_error
from .rules import add_rule


def parse_error_md(content: str) -> dict:
    """Parse error MD file content into structured data."""
    result = {
        "error_message": "",
        "error_type": None,
        "context": None,
        "file_path": None,
        "five_whys": [],
        "root_cause": None,
        "solution": None,
        "prevention": None,
        "created_at": None,
    }

    # Extract date from header
    date_match = re.search(r"\*\*일시\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
    if date_match:
        result["created_at"] = date_match.group(1)

    # Extract title as error message
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        result["error_message"] = title_match.group(1).strip()

    # Extract error type from title or content
    type_patterns = [
        r"(TypeError|AttributeError|ValueError|KeyError|IndexError|ImportError)",
        r"(MCP|Schema|Cache|License)\s*(Error|Issue|Problem)",
    ]
    for pattern in type_patterns:
        type_match = re.search(pattern, content, re.IGNORECASE)
        if type_match:
            result["error_type"] = type_match.group(0)
            break

    # Extract sections
    sections = {
        "에러 상황": "context",
        "상황": "context",
        "원인": "root_cause",
        "근본 원인": "root_cause",
        "해결": "solution",
        "해결 방법": "solution",
        "재발 방지": "prevention",
        "방지": "prevention",
    }

    for korean, field in sections.items():
        # Match section headers like "## 에러 상황" or "### 원인"
        pattern = rf"##?\s*{korean}[^\n]*\n([\s\S]*?)(?=\n##|\n---|\Z)"
        match = re.search(pattern, content)
        if match and not result[field]:
            result[field] = match.group(1).strip()

    # Extract 5 Whys
    whys_pattern = r"\|\s*(\d)\s*\|\s*[Ww]hy\s*\|\s*(.+?)\s*\|"
    whys = re.findall(whys_pattern, content)
    if whys:
        result["five_whys"] = [w[1].strip() for w in sorted(whys, key=lambda x: x[0])]

    return result


def migrate_error_files(
    source_dir: str,
    project_path: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Migrate MD error files to SQLite.

    Args:
        source_dir: Directory containing .clouvel/errors/*.md files
        project_path: Target project path for database
        dry_run: If True, only report what would be done
    """
    source_path = Path(source_dir)
    errors_dir = source_path / ".clouvel" / "errors"

    if not errors_dir.exists():
        return {
            "status": "no_source",
            "message": f"에러 디렉토리가 없습니다: {errors_dir}",
        }

    md_files = list(errors_dir.glob("*.md"))
    if not md_files:
        return {
            "status": "no_files",
            "message": "마이그레이션할 MD 파일이 없습니다",
        }

    # Initialize database
    if not dry_run:
        init_db(project_path or source_dir)

    results = {
        "status": "success",
        "total": len(md_files),
        "migrated": 0,
        "skipped": 0,
        "errors": [],
        "files": [],
    }

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            parsed = parse_error_md(content)

            if not parsed["error_message"]:
                results["skipped"] += 1
                results["errors"].append(f"{md_file.name}: 에러 메시지 추출 실패")
                continue

            if dry_run:
                results["files"].append({
                    "file": md_file.name,
                    "parsed": parsed,
                })
            else:
                record_result = record_error(
                    error_message=parsed["error_message"],
                    error_type=parsed["error_type"],
                    context=parsed["context"],
                    five_whys=parsed["five_whys"] or None,
                    root_cause=parsed["root_cause"],
                    solution=parsed["solution"],
                    prevention=parsed["prevention"],
                    project_path=project_path or source_dir,
                )
                results["files"].append({
                    "file": md_file.name,
                    "id": record_result["id"],
                })

            results["migrated"] += 1

        except Exception as e:
            results["errors"].append(f"{md_file.name}: {str(e)}")
            results["skipped"] += 1

    return results


def extract_rules_from_claude_md(
    claude_md_path: str,
    project_path: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Extract existing rules from CLAUDE.md and import to database.

    Args:
        claude_md_path: Path to CLAUDE.md
        project_path: Target project path
        dry_run: If True, only report what would be done
    """
    path = Path(claude_md_path)
    if not path.exists():
        return {"status": "not_found", "message": f"파일이 없습니다: {path}"}

    content = path.read_text(encoding="utf-8")

    results = {
        "status": "success",
        "rules": [],
        "imported": 0,
        "skipped": 0,
    }

    # Pattern to find NEVER/ALWAYS/PREFER rules
    rule_patterns = [
        (r"NEVER[:\s]+(.+?)(?:\n|$)", "NEVER"),
        (r"ALWAYS[:\s]+(.+?)(?:\n|$)", "ALWAYS"),
        (r"절대[^가-힣]*금지[:\s]*(.+?)(?:\n|$)", "NEVER"),
        (r"반드시[:\s]+(.+?)(?:\n|$)", "ALWAYS"),
        (r"-\s*\*\*NEVER\*\*[:\s]*(.+?)(?:\n|$)", "NEVER"),
        (r"-\s*\*\*ALWAYS\*\*[:\s]*(.+?)(?:\n|$)", "ALWAYS"),
    ]

    for pattern, rule_type in rule_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            rule_content = match.strip()
            if len(rule_content) < 5:  # Skip too short
                continue

            if dry_run:
                results["rules"].append({
                    "type": rule_type,
                    "content": rule_content,
                })
            else:
                add_result = add_rule(
                    rule_type=rule_type,
                    content=rule_content,
                    category="general",
                    project_path=project_path,
                )
                if add_result["status"] == "created":
                    results["imported"] += 1
                    results["rules"].append({
                        "type": rule_type,
                        "content": rule_content,
                        "id": add_result["id"],
                    })
                else:
                    results["skipped"] += 1

    return results


def full_migration(
    project_path: str,
    dry_run: bool = False,
) -> dict:
    """
    Full migration: errors + CLAUDE.md rules.

    Args:
        project_path: Project root path
        dry_run: If True, only report what would be done
    """
    project = Path(project_path)

    # Initialize DB first
    if not dry_run:
        init_db(project_path)

    results = {
        "project": project_path,
        "dry_run": dry_run,
        "errors": None,
        "rules": None,
    }

    # Migrate error files
    results["errors"] = migrate_error_files(
        project_path,
        project_path=project_path,
        dry_run=dry_run,
    )

    # Extract rules from CLAUDE.md
    claude_md = project / "CLAUDE.md"
    if claude_md.exists():
        results["rules"] = extract_rules_from_claude_md(
            str(claude_md),
            project_path=project_path,
            dry_run=dry_run,
        )
    else:
        results["rules"] = {"status": "no_claude_md"}

    return results
