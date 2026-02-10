"""Error CRUD operations for Clouvel Error System v2.0."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .schema import get_connection, get_db_path


def generate_error_id() -> str:
    """Generate unique error ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"err_{timestamp}_{short_uuid}"


def record_error(
    error_message: str,
    *,
    error_type: Optional[str] = None,
    stack_trace: Optional[str] = None,
    context: Optional[str] = None,
    file_path: Optional[str] = None,
    five_whys: Optional[list[str]] = None,
    root_cause: Optional[str] = None,
    solution: Optional[str] = None,
    prevention: Optional[str] = None,
    project_path: Optional[str] = None,
) -> dict:
    """
    Record a new error.

    Returns:
        dict with error id and status
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    error_id = generate_error_id()
    five_whys_json = json.dumps(five_whys, ensure_ascii=False) if five_whys else None

    try:
        conn.execute(
            """
            INSERT INTO errors (
                id, error_type, error_message, stack_trace, context,
                file_path, five_whys, root_cause, solution, prevention
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                error_id,
                error_type,
                error_message,
                stack_trace,
                context,
                file_path,
                five_whys_json,
                root_cause,
                solution,
                prevention,
            ),
        )
        conn.commit()
        return {"id": error_id, "status": "recorded"}
    finally:
        conn.close()


def get_error(error_id: str, project_path: Optional[str] = None) -> Optional[dict]:
    """Get error by ID."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        row = conn.execute(
            "SELECT * FROM errors WHERE id = ?", (error_id,)
        ).fetchone()

        if row is None:
            return None

        result = dict(row)
        # Parse JSON fields
        if result.get("five_whys"):
            result["five_whys"] = json.loads(result["five_whys"])

        return result
    finally:
        conn.close()


def list_errors(
    *,
    days: int = 7,
    error_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 50,
    project_path: Optional[str] = None,
) -> list[dict]:
    """
    List errors with filters.

    Args:
        days: Number of days to look back
        error_type: Filter by error type
        resolved: Filter by resolution status (True/False/None for all)
        limit: Maximum number of results
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    query = """
        SELECT id, created_at, error_type, error_message, file_path,
               resolved_at, resolution_effective
        FROM errors
        WHERE created_at >= datetime('now', ?)
    """
    params: list = [f"-{days} days"]

    if error_type:
        query += " AND error_type = ?"
        params.append(error_type)

    if resolved is True:
        query += " AND resolved_at IS NOT NULL"
    elif resolved is False:
        query += " AND resolved_at IS NULL"

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def resolve_error(
    error_id: str,
    *,
    effective: bool = True,
    solution: Optional[str] = None,
    prevention: Optional[str] = None,
    project_path: Optional[str] = None,
) -> dict:
    """
    Mark error as resolved with effectiveness feedback.

    Args:
        error_id: Error ID to resolve
        effective: Whether the solution was effective
        solution: Optional solution update
        prevention: Optional prevention update
    """
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Build update query
        updates = ["resolved_at = CURRENT_TIMESTAMP", "resolution_effective = ?"]
        params: list = [1 if effective else 0]

        if solution:
            updates.append("solution = ?")
            params.append(solution)
        if prevention:
            updates.append("prevention = ?")
            params.append(prevention)

        params.append(error_id)

        query = f"UPDATE errors SET {', '.join(updates)} WHERE id = ?"
        cursor = conn.execute(query, params)
        conn.commit()

        if cursor.rowcount == 0:
            return {"status": "not_found", "id": error_id}

        return {"status": "resolved", "id": error_id, "effective": effective}
    finally:
        conn.close()


def search_errors_by_type(
    error_type: str,
    *,
    limit: int = 10,
    project_path: Optional[str] = None,
) -> list[dict]:
    """Search errors by type (for hybrid search first stage)."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        rows = conn.execute(
            """
            SELECT id, error_message, solution, prevention, resolved_at
            FROM errors
            WHERE error_type = ?
            ORDER BY
                CASE WHEN resolution_effective = 1 THEN 0 ELSE 1 END,
                created_at DESC
            LIMIT ?
            """,
            (error_type, limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_error_stats(
    *,
    days: int = 30,
    project_path: Optional[str] = None,
) -> dict:
    """Get error statistics."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Total errors
        total = conn.execute(
            "SELECT COUNT(*) FROM errors WHERE created_at >= datetime('now', ?)",
            (f"-{days} days",),
        ).fetchone()[0]

        # By type
        by_type = conn.execute(
            """
            SELECT error_type, COUNT(*) as count
            FROM errors
            WHERE created_at >= datetime('now', ?)
            GROUP BY error_type
            ORDER BY count DESC
            """,
            (f"-{days} days",),
        ).fetchall()

        # Resolution stats
        resolved = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE resolved_at IS NOT NULL) as resolved,
                COUNT(*) FILTER (WHERE resolution_effective = 1) as effective
            FROM errors
            WHERE created_at >= datetime('now', ?)
            """,
            (f"-{days} days",),
        ).fetchone()

        # MTTR (Mean Time To Resolution)
        mttr = conn.execute(
            """
            SELECT AVG(
                (julianday(resolved_at) - julianday(created_at)) * 24 * 60
            ) as mttr_minutes
            FROM errors
            WHERE resolved_at IS NOT NULL
              AND created_at >= datetime('now', ?)
            """,
            (f"-{days} days",),
        ).fetchone()

        return {
            "period_days": days,
            "total": total,
            "by_type": {row["error_type"] or "unknown": row["count"] for row in by_type},
            "resolved": resolved["resolved"] if resolved else 0,
            "effective": resolved["effective"] if resolved else 0,
            "mttr_minutes": round(mttr["mttr_minutes"], 1) if mttr and mttr["mttr_minutes"] else None,
        }
    finally:
        conn.close()
