# -*- coding: utf-8 -*-
"""Tracking tools: record_file, list_files (v1.5)

파일 생성 기록을 자동화하는 도구들.
"기록을 잃지 않는다" 모토 이행.
"""

from pathlib import Path
from datetime import datetime
from mcp.types import TextContent


async def record_file(
    path: str,
    file_path: str,
    purpose: str,
    deletable: bool = False,
    session: str = None
) -> list[TextContent]:
    """Record a file creation to .claude/files/created.md

    Args:
        path: Project root path
        file_path: Relative path of the created file
        purpose: What this file does
        deletable: Whether this file can be deleted (default: False)
        session: Session name for grouping (optional)

    Returns:
        Confirmation message
    """
    project_path = Path(path).resolve()

    # Ensure .claude/files directory exists
    files_dir = project_path / ".claude" / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    created_md = files_dir / "created.md"

    # Create template if file doesn't exist
    if not created_md.exists():
        template = """# Created Files

> 삭제하면 안 되는 핵심 파일만 기록. Record essential files only.

---

## Files

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|

---

## 생성 기록

| 날짜 | 세션 | 파일 |
|------|------|------|
"""
        created_md.write_text(template, encoding='utf-8')

    # Read current content
    content = created_md.read_text(encoding='utf-8')

    # Check if file already recorded
    if file_path in content:
        return [TextContent(type="text", text=f"⚠️ Already recorded: `{file_path}`")]

    # Add to Files table (only once)
    deletable_mark = "⚠️" if deletable else "❌"
    file_row = f"| `{file_path}` | {purpose} | {deletable_mark} |"

    # Find the FIRST Files table and add row
    lines = content.split('\n')
    new_lines = []
    file_added = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Detect first Files table header and add after separator
        if not file_added and ('| 파일경로 |' in line or '| File |' in line):
            # Check if next line is separator
            if i + 1 < len(lines) and lines[i + 1].startswith('|--'):
                continue  # Will add after separator

        # Add row after first table header separator
        if not file_added and line.startswith('|--') and i > 0:
            prev_line = lines[i - 1]
            if '| 파일경로 |' in prev_line or '| File |' in prev_line:
                new_lines.append(file_row)
                file_added = True

    # Add to 생성 기록 table (only once)
    today = datetime.now().strftime('%Y-%m-%d')
    session_name = session or "auto"
    record_row = f"| {today} | {session_name} | `{file_path}` |"

    final_lines = []
    record_added = False

    for i, line in enumerate(new_lines):
        final_lines.append(line)

        # Add to first record table only
        if not record_added and ('| 날짜 |' in line or '| Date |' in line):
            if i + 1 < len(new_lines) and new_lines[i + 1].startswith('|--'):
                continue

        if not record_added and line.startswith('|--') and i > 0:
            prev_line = new_lines[i - 1]
            if '| 날짜 |' in prev_line or '| Date |' in prev_line:
                final_lines.append(record_row)
                record_added = True

    # Write updated content
    created_md.write_text('\n'.join(final_lines), encoding='utf-8')

    return [TextContent(type="text", text=f"""✅ File recorded: `{file_path}`

**Purpose**: {purpose}
**Deletable**: {"Yes ⚠️" if deletable else "No ❌"}
**Location**: `.claude/files/created.md`
""")]


async def list_files(path: str) -> list[TextContent]:
    """List all recorded files from .claude/files/created.md

    Args:
        path: Project root path

    Returns:
        List of recorded files
    """
    project_path = Path(path).resolve()
    created_md = project_path / ".claude" / "files" / "created.md"

    if not created_md.exists():
        return [TextContent(type="text", text="📋 No files recorded yet. Use `record_file` to start tracking.")]

    content = created_md.read_text(encoding='utf-8')

    # Count files (rows starting with | ` )
    file_count = len([line for line in content.split('\n')
                      if line.startswith('| `') and '파일경로' not in line])

    return [TextContent(type="text", text=f"""📋 **Recorded Files**: {file_count}

{content}
""")]
