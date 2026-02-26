# -*- coding: utf-8 -*-
"""Audit rules: analyze CLAUDE.md bloat and migrate to .claude/rules/"""

import re
from pathlib import Path
from mcp.types import TextContent


# Section patterns that can be migrated to .claude/rules/
_SECTION_TARGETS = {
    "security": ["Security", "보안", "SECURITY"],
    "errors": ["Error Learning", "에러 학습"],
    "clouvel": ["Clouvel 규칙", "Clouvel Rules"],
}


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 chars for English, ≈ 2 chars for Korean)."""
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    non_ascii = len(text) - ascii_chars
    return (ascii_chars // 4) + (non_ascii // 2)


def _find_sections(content: str) -> list[dict]:
    """Find ## sections in CLAUDE.md that could be migrated."""
    sections = []
    lines = content.split("\n")
    current_section = None
    current_lines = []
    current_start = 0

    for i, line in enumerate(lines):
        if line.startswith("## "):
            # Save previous section
            if current_section:
                body = "\n".join(current_lines)
                sections.append({
                    "title": current_section,
                    "start_line": current_start,
                    "end_line": i - 1,
                    "line_count": len(current_lines),
                    "token_estimate": _estimate_tokens(body),
                    "body": body,
                })
            current_section = line[3:].strip()
            current_start = i
            current_lines = []
        elif current_section:
            current_lines.append(line)

    # Last section
    if current_section:
        body = "\n".join(current_lines)
        sections.append({
            "title": current_section,
            "start_line": current_start,
            "end_line": len(lines) - 1,
            "line_count": len(current_lines),
            "token_estimate": _estimate_tokens(body),
            "body": body,
        })

    return sections


def _classify_section(title: str) -> str:
    """Classify section into a target rules file."""
    for target, keywords in _SECTION_TARGETS.items():
        for kw in keywords:
            if kw.lower() in title.lower():
                return target
    return ""


async def audit_rules(path: str, migrate: bool = False) -> list[TextContent]:
    """Analyze CLAUDE.md for bloat and optionally migrate to .claude/rules/.

    Args:
        path: Project root path
        migrate: If True, actually perform the migration. If False, report only.
    """
    project_path = Path(path).resolve()
    claude_md = project_path / "CLAUDE.md"

    if not claude_md.exists():
        return [TextContent(type="text", text="# Audit Rules\n\nNo CLAUDE.md found.")]

    content = claude_md.read_text(encoding="utf-8")
    total_lines = len(content.split("\n"))
    total_tokens = _estimate_tokens(content)
    sections = _find_sections(content)

    # Identify migratable sections (> 5 lines)
    migratable = []
    for sec in sections:
        target = _classify_section(sec["title"])
        if target:
            sec["target_file"] = f"{target}.md"
            migratable.append(sec)
        elif sec["line_count"] > 10:
            # Large unclassified sections are candidates too
            safe_name = re.sub(r"[^a-zA-Z0-9가-힣_-]", "", sec["title"].lower().replace(" ", "_"))
            sec["target_file"] = f"{safe_name or 'misc'}.md"
            migratable.append(sec)

    # Build report
    result = "# CLAUDE.md Audit Report\n\n"
    result += f"**Total lines**: {total_lines}\n"
    result += f"**Estimated tokens**: {total_tokens}\n"
    result += f"**Sections found**: {len(sections)}\n"
    result += f"**Migratable sections**: {len(migratable)}\n\n"

    if migratable:
        savings = sum(s["token_estimate"] for s in migratable)
        result += f"**Potential token savings**: ~{savings} tokens ({savings * 100 // max(total_tokens, 1)}%)\n\n"

        result += "## Migratable Sections\n\n"
        result += "| Section | Lines | Tokens | Target |\n"
        result += "|---------|-------|--------|--------|\n"
        for sec in migratable:
            result += f"| {sec['title'][:40]} | {sec['line_count']} | ~{sec['token_estimate']} | `.claude/rules/{sec['target_file']}` |\n"
        result += "\n"
    else:
        result += "## No Migratable Sections Found\n\n"
        result += "CLAUDE.md looks lean already.\n"

    # Perform migration if requested
    if migrate and migratable:
        rules_dir = project_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        migrated = []
        remaining_content = content

        for sec in migratable:
            target_path = rules_dir / sec["target_file"]

            # Write section to rules file
            rule_content = f"# {sec['title']}\n\n{sec['body'].strip()}\n"
            if target_path.exists():
                # Append to existing
                existing = target_path.read_text(encoding="utf-8")
                target_path.write_text(existing.rstrip() + "\n\n" + rule_content, encoding="utf-8")
            else:
                target_path.write_text(rule_content, encoding="utf-8")

            # Replace section in CLAUDE.md with 1-line reference
            section_header = f"## {sec['title']}"
            # Find the section and replace with stub
            stub = f"## {sec['title']}\nSee `.claude/rules/{sec['target_file']}`\n"

            # Build regex to match the section (header + body until next ## or EOF)
            pattern = re.escape(section_header) + r"\n.*?(?=\n## |\Z)"
            remaining_content = re.sub(pattern, stub.rstrip(), remaining_content, count=1, flags=re.DOTALL)

            migrated.append(sec["target_file"])

        # Write updated CLAUDE.md
        claude_md.write_text(remaining_content, encoding="utf-8")

        new_tokens = _estimate_tokens(remaining_content)
        result += "## Migration Complete\n\n"
        result += f"**Files created/updated**: {len(set(migrated))}\n"
        for f in sorted(set(migrated)):
            result += f"- `.claude/rules/{f}`\n"
        result += f"\n**CLAUDE.md**: {total_tokens} → {new_tokens} tokens ({(total_tokens - new_tokens) * 100 // max(total_tokens, 1)}% reduction)\n"

    elif not migrate and migratable:
        result += "## Next Step\n\n"
        result += "Run `audit_rules(path, migrate=true)` to perform the migration.\n"

    return [TextContent(type="text", text=result)]
