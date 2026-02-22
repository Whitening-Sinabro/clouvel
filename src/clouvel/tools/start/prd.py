# Clouvel Start Tool - PRD Saving/Validation
# PRD save, validate, backup, diff, and impact analysis

from pathlib import Path
from typing import Dict, Any, Optional


def _get_trial_info() -> Optional[Dict[str, Any]]:
    """Get Trial status for Pro features via API."""
    try:
        from ...api_client import get_trial_status

        status = get_trial_status()

        if "error" in status:
            # API unavailable, show trial info anyway
            return {
                "has_trial": True,
                "message": """
---

\U0001f4a1 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test\u2192verify\u2192evidence |

> Try now: `manager(context="your plan", topic="feature")`
> Upgrade: https://polar.sh/clouvel
"""
            }

        features = status.get("features", {})

        # Check if any trial remaining
        has_trial = any(f.get("remaining", 0) > 0 for f in features.values())

        if has_trial:
            return {
                "has_trial": True,
                "features": features,
                "message": """
---

\U0001f4a1 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test\u2192verify\u2192evidence |

> Try now: `manager(context="your plan", topic="feature")`
> Upgrade: https://polar.sh/clouvel
"""
            }
        else:
            return {
                "has_trial": False,
                "message": "Trial exhausted. Upgrade to Pro: https://polar.sh/clouvel"
            }
    except Exception:
        # Fallback - show trial info
        return {
            "has_trial": True,
            "message": """
---

\U0001f4a1 **Pro Trial Available!**

| Feature | Free Uses | Description |
|---------|-----------|-------------|
| `manager` | 10 uses | 8 C-Level manager feedback |
| `ship` | 5 uses | One-click test\u2192verify\u2192evidence |

> Try now: `manager(context="your plan", topic="feature")`
> Upgrade: https://polar.sh/clouvel
"""
        }


def _validate_prd(content: str) -> Dict[str, Any]:
    """
    Validate PRD content.

    Required sections:
    - Project Overview (Purpose, Goals)
    - Functional Requirements

    Recommended sections:
    - Technical Spec
    - Data Model
    - Test Plan
    """
    # Check for both Korean and English section names
    required_sections = [
        (["Project Overview", "\ud504\ub85c\uc81d\ud2b8 \uac1c\uc694"], ["Purpose", "Goals", "\ubaa9\uc801", "\ubaa9\ud45c"]),
        (["Functional Requirements", "\uae30\ub2a5 \uc694\uad6c\uc0ac\ud56d"], ["Core Features", "\ud575\uc2ec \uae30\ub2a5"]),
    ]

    recommended_sections = [
        ["Technical Spec", "\uae30\uc220 \uc2a4\ud399"],
        ["Data Model", "\ub370\uc774\ud130 \ubaa8\ub378"],
        ["Test Plan", "\ud14c\uc2a4\ud2b8 \uacc4\ud68d"]
    ]

    missing_sections = []
    summary = {
        "sections_found": [],
        "has_goals": False,
        "has_features": False
    }

    # Required section check
    for section_names, subsection_names in required_sections:
        section_found = any(name in content for name in section_names)
        if not section_found:
            missing_sections.append(section_names[0])  # Use English name
        else:
            summary["sections_found"].append(section_names[0])

            # Check if content exists (not just template placeholder)
            for sub in subsection_names:
                if sub in content:
                    # Placeholder check
                    if sub in ["Purpose", "\ubaa9\uc801"] and ("[Describe the problem" in content or "[\uc774 \ud504\ub85c\uc81d\ud2b8\uac00 \ud574\uacb0\ud558\ub824\ub294 \ubb38\uc81c\ub97c \uc791\uc131\ud558\uc138\uc694]" in content):
                        missing_sections.append(f"{section_names[0]} > {sub}")
                    elif sub in ["Goals", "\ubaa9\ud45c"] and ("Core goal 1" in content or "\ud575\uc2ec \ubaa9\ud45c 1" in content):
                        pass  # Goals exist, OK
                    else:
                        if section_names[0] in ["Project Overview", "\ud504\ub85c\uc81d\ud2b8 \uac1c\uc694"]:
                            summary["has_goals"] = True

    # Functional requirements check
    if any(name in content for name in ["Functional Requirements", "\uae30\ub2a5 \uc694\uad6c\uc0ac\ud56d"]):
        if "**Feature 1**: Description" not in content and "**\uae30\ub2a5 1**: \uc124\uba85" not in content:
            summary["has_features"] = True

    # Recommended section check
    for section_names in recommended_sections:
        if any(name in content for name in section_names):
            summary["sections_found"].append(section_names[0])

    is_valid = len(missing_sections) == 0 and summary["has_goals"]

    return {
        "is_valid": is_valid,
        "missing_sections": missing_sections,
        "summary": summary
    }


def save_prd(
    path: str,
    content: str,
    project_name: str = "",
    project_type: str = ""
) -> Dict[str, Any]:
    """
    Save PRD content with version history and impact analysis (v3.1 Pro).

    Save PRD written by Claude through conversation with user.
    Pro feature: Tracks changes and analyzes impact on codebase.

    Args:
        path: Project root path
        content: PRD content (markdown)
        project_name: Project name (optional, used in header)
        project_type: Project type (optional, for metadata)

    Returns:
        Save result with diff and impact analysis (Pro)
    """
    from datetime import datetime

    project_path = Path(path).resolve()
    docs_path = project_path / "docs"
    prd_path = docs_path / "PRD.md"

    result = {
        "status": "UNKNOWN",
        "prd_path": str(prd_path),
        "message": "",
        "diff": None,
        "impact": None
    }

    # Create docs folder
    if not docs_path.exists():
        try:
            docs_path.mkdir(parents=True)
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"Failed to create docs folder: {e}"
            return result

    # Add PRD header (if missing)
    if not content.strip().startswith("#"):
        today = datetime.now().strftime("%Y-%m-%d")
        name = project_name or project_path.name
        header = f"# {name} PRD\n\n> Created: {today}\n\n---\n\n"
        content = header + content

    # v3.1 Pro: Backup previous PRD and calculate diff
    old_content = None
    if prd_path.exists():
        try:
            old_content = prd_path.read_text(encoding="utf-8")
            # Backup to history
            _backup_prd(project_path, old_content)
        except Exception:
            pass

    # Save new PRD
    try:
        prd_path.write_text(content, encoding="utf-8")
        result["status"] = "SAVED"
        result["message"] = f"\u2705 PRD saved: {prd_path}"

        # Validate
        validation = _validate_prd(content)
        result["validation"] = validation

        # v3.1 Pro: Calculate diff if previous version exists
        if old_content:
            diff_result = _calculate_prd_diff(old_content, content)
            result["diff"] = diff_result

            # v3.1 Pro: Impact analysis
            if diff_result.get("has_changes"):
                impact = _analyze_prd_impact(project_path, diff_result)
                result["impact"] = impact

        # Build next_steps
        if validation["is_valid"]:
            result["next_steps"] = [
                "PRD saved! You can start coding now.",
                "Check with `can_code` tool or start coding directly."
            ]
        else:
            result["next_steps"] = [
                f"PRD saved but some sections are incomplete: {', '.join(validation['missing_sections'])}",
                "Consider completing the PRD if needed."
            ]

        # Add Pro upsell or diff summary
        if result.get("diff") and result["diff"].get("has_changes"):
            result["next_steps"].append(
                f"\U0001f4ca PRD changed: +{result['diff']['added_lines']} -{result['diff']['removed_lines']} lines"
            )
            if result.get("impact") and result["impact"].get("affected_files"):
                result["next_steps"].append(
                    f"\u26a0\ufe0f Impact: {len(result['impact']['affected_files'])} files may need updates"
                )
        else:
            result["next_steps"].append(
                "\U0001f48e Pro: Track PRD changes & impact analysis with `ship` \u2192 https://polar.sh/clouvel"
            )

    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Failed to save PRD: {e}"

    return result


def _backup_prd(project_path: Path, content: str) -> str:
    """Backup PRD to history folder (v3.1 Pro).

    Returns:
        Backup file path
    """
    from datetime import datetime

    history_dir = project_path / ".claude" / "prd_history"
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = history_dir / f"PRD_{timestamp}.md"

    try:
        backup_path.write_text(content, encoding="utf-8")
        return str(backup_path)
    except Exception:
        return None


def _calculate_prd_diff(old_content: str, new_content: str) -> Dict[str, Any]:
    """Calculate diff between old and new PRD (v3.1 Pro).

    Returns:
        Diff summary with changed sections
    """
    import difflib

    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))

    added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

    # Extract changed sections (## headers)
    changed_sections = set()
    current_section = "Unknown"

    for line in diff:
        if line.startswith('@@'):
            continue
        if line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
            actual_line = line[1:].strip()
            if actual_line.startswith('## '):
                current_section = actual_line[3:].strip()
            changed_sections.add(current_section)

    # Extract changed keywords (for impact analysis)
    changed_keywords = set()
    for line in diff:
        if line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
            # Extract words that look like identifiers
            words = line[1:].split()
            for word in words:
                # Filter: 3+ chars, alphanumeric, not common words
                clean = ''.join(c for c in word if c.isalnum() or c == '_')
                if len(clean) >= 3 and clean.lower() not in {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'todo'}:
                    changed_keywords.add(clean.lower())

    return {
        "has_changes": added_lines > 0 or removed_lines > 0,
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "changed_sections": list(changed_sections),
        "changed_keywords": list(changed_keywords)[:20],  # Limit to 20
        "diff_preview": '\n'.join(diff[:30]) if diff else ""
    }


def _analyze_prd_impact(project_path: Path, diff_result: Dict) -> Dict[str, Any]:
    """Analyze impact of PRD changes on codebase (v3.1 Pro).

    Searches for files that might be affected by PRD changes.

    Returns:
        Impact analysis with affected files and warnings
    """
    keywords = diff_result.get("changed_keywords", [])
    if not keywords:
        return {"affected_files": [], "warnings": []}

    affected_files = []
    warnings = []

    # Search in src/ directory
    src_dir = project_path / "src"
    if not src_dir.exists():
        src_dir = project_path

    # File extensions to search
    extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java'}

    try:
        for file_path in src_dir.rglob('*'):
            if not file_path.is_file():
                continue
            if file_path.suffix not in extensions:
                continue
            if '__pycache__' in str(file_path) or 'node_modules' in str(file_path):
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore').lower()

                # Check if any keyword appears in file
                matched_keywords = []
                for keyword in keywords:
                    if keyword in content:
                        matched_keywords.append(keyword)

                if matched_keywords:
                    rel_path = file_path.relative_to(project_path)
                    affected_files.append({
                        "path": str(rel_path),
                        "matched_keywords": matched_keywords[:5],
                        "match_count": len(matched_keywords)
                    })
            except Exception:
                continue

    except Exception:
        pass

    # Sort by match count (most affected first)
    affected_files.sort(key=lambda x: x["match_count"], reverse=True)
    affected_files = affected_files[:15]  # Limit to 15 files

    # Generate warnings
    if len(affected_files) > 10:
        warnings.append(f"Large impact: {len(affected_files)}+ files may need review")

    # Check if tests might be affected
    test_affected = [f for f in affected_files if 'test' in f["path"].lower()]
    if test_affected:
        warnings.append(f"Tests may need updates: {len(test_affected)} test files affected")

    # Check changed sections for critical areas
    changed_sections = diff_result.get("changed_sections", [])
    critical_sections = {'acceptance', 'criteria', 'api', 'database', 'schema', 'security'}
    critical_changes = [s for s in changed_sections if any(c in s.lower() for c in critical_sections)]
    if critical_changes:
        warnings.append(f"Critical sections changed: {', '.join(critical_changes)}")

    return {
        "affected_files": affected_files,
        "warnings": warnings,
        "summary": f"{len(affected_files)} files may be affected by PRD changes"
    }
