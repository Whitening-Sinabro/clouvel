"""Rule management for Clouvel Error System v2.0."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal

from .schema import get_connection, get_db_path


RuleType = Literal["NEVER", "ALWAYS", "PREFER"]
Category = Literal["api", "frontend", "database", "security", "general"]


def generate_rule_id() -> str:
    """Generate unique rule ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"rule_{timestamp}_{short_uuid}"


def add_rule(
    rule_type: RuleType,
    content: str,
    *,
    category: Optional[Category] = None,
    source_error_id: Optional[str] = None,
    project_path: Optional[str] = None,
) -> dict:
    """
    Add a new rule.

    Args:
        rule_type: NEVER, ALWAYS, or PREFER
        content: Rule content
        category: Optional category
        source_error_id: Error that triggered this rule
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    rule_id = generate_rule_id()

    try:
        # Check for duplicate content
        existing = conn.execute(
            "SELECT id FROM rules WHERE content = ? AND rule_type = ?",
            (content, rule_type),
        ).fetchone()

        if existing:
            return {
                "status": "duplicate",
                "existing_id": existing["id"],
                "message": "동일한 규칙이 이미 존재합니다",
            }

        conn.execute(
            """
            INSERT INTO rules (id, rule_type, content, category, source_error_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (rule_id, rule_type, content, category, source_error_id),
        )

        # Link to source error if provided
        if source_error_id:
            conn.execute(
                """
                INSERT OR IGNORE INTO error_rule_mapping (error_id, rule_id)
                VALUES (?, ?)
                """,
                (source_error_id, rule_id),
            )

        conn.commit()
        return {"status": "created", "id": rule_id}
    finally:
        conn.close()


def get_rules(
    *,
    rule_type: Optional[RuleType] = None,
    category: Optional[Category] = None,
    limit: int = 100,
    project_path: Optional[str] = None,
) -> list[dict]:
    """
    Get rules with optional filters.

    Args:
        rule_type: Filter by NEVER, ALWAYS, PREFER
        category: Filter by category
        limit: Maximum results
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    query = "SELECT * FROM rules WHERE 1=1"
    params: list = []

    if rule_type:
        query += " AND rule_type = ?"
        params.append(rule_type)

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY applied_count DESC, created_at DESC LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def apply_rule(
    rule_id: str,
    *,
    error_id: Optional[str] = None,
    prevented: bool = False,
    project_path: Optional[str] = None,
) -> dict:
    """
    Mark rule as applied (increment counter).

    Args:
        rule_id: Rule that was applied
        error_id: Optional error this was applied to
        prevented: Whether this rule prevented an error
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Update rule counter
        cursor = conn.execute(
            """
            UPDATE rules
            SET applied_count = applied_count + 1,
                last_applied = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (rule_id,),
        )

        if cursor.rowcount == 0:
            return {"status": "not_found", "id": rule_id}

        # Link to error if provided
        if error_id:
            conn.execute(
                """
                INSERT OR REPLACE INTO error_rule_mapping
                    (error_id, rule_id, prevented)
                VALUES (?, ?, ?)
                """,
                (error_id, rule_id, 1 if prevented else 0),
            )

        conn.commit()
        return {"status": "applied", "id": rule_id}
    finally:
        conn.close()


def get_rules_for_error(
    error_id: str,
    project_path: Optional[str] = None,
) -> list[dict]:
    """Get rules linked to an error."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        rows = conn.execute(
            """
            SELECT r.*, m.prevented
            FROM rules r
            JOIN error_rule_mapping m ON r.id = m.rule_id
            WHERE m.error_id = ?
            """,
            (error_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def export_rules_to_markdown(
    project_path: Optional[str] = None,
) -> str:
    """Export all rules to CLAUDE.md format."""
    rules = get_rules(project_path=project_path)

    if not rules:
        return ""

    lines = [
        "## Clouvel 학습 규칙 (자동 생성)",
        "",
        "> 이 규칙들은 에러 학습 시스템이 자동으로 추가했습니다.",
        "",
    ]

    # Group by type
    never_rules = [r for r in rules if r["rule_type"] == "NEVER"]
    always_rules = [r for r in rules if r["rule_type"] == "ALWAYS"]
    prefer_rules = [r for r in rules if r["rule_type"] == "PREFER"]

    if never_rules:
        lines.append("### NEVER (절대 금지)")
        lines.append("")
        for r in never_rules:
            lines.append(f"- {r['content']}")
        lines.append("")

    if always_rules:
        lines.append("### ALWAYS (필수 준수)")
        lines.append("")
        for r in always_rules:
            lines.append(f"- {r['content']}")
        lines.append("")

    if prefer_rules:
        lines.append("### PREFER (권장)")
        lines.append("")
        for r in prefer_rules:
            lines.append(f"- {r['content']}")
        lines.append("")

    return "\n".join(lines)
