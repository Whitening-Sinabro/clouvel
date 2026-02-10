"""Regression Memory CRUD + 3-level matching engine.

v4.0: Stores past error patterns and matches them against new contexts.
"""

import re
import json
from datetime import datetime
from typing import Optional

from .schema import get_connection, get_db_path, init_db


def normalize_error_signature(error_text: str) -> str:
    """Normalize error text into a stable signature.

    Removes file paths, line numbers, hex addresses, and timestamps
    so that the same logical error produces the same signature.
    """
    sig = error_text
    # Remove timestamps like 2026-01-25T14:30:00 (BEFORE line numbers to avoid partial match)
    sig = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '<TIME>', sig)
    # Remove file paths (Unix and Windows)
    sig = re.sub(r'(?:[A-Za-z]:)?[\\/][\w.\-\\/]+', '<PATH>', sig)
    # Remove line numbers like :123, line 42
    sig = re.sub(r'(?::|line\s+)\d+', ':<LINE>', sig)
    # Remove hex addresses like 0x7fff1234
    sig = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', sig)
    # Remove UUIDs
    sig = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', sig)
    # Collapse whitespace
    sig = re.sub(r'\s+', ' ', sig).strip()
    return sig


def create_memory(
    *,
    error_signature: str,
    root_cause: str,
    project_name: str = "",
    error_category: str = "",
    file_paths: Optional[list[str]] = None,
    libraries: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    task_description: str = "",
    code_snippet: str = "",
    fix_snippet: str = "",
    prevention_rule: str = "",
    negative_constraint: str = "",
    severity: int = 3,
    source_error_id: str = "",
    project_path: Optional[str] = None,
) -> dict:
    """Create a regression memory entry + sync FTS."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        cursor = conn.execute(
            """INSERT INTO regression_memory (
                project_name, error_signature, error_category,
                file_paths, libraries, tags,
                task_description, code_snippet, fix_snippet,
                root_cause, prevention_rule, negative_constraint,
                severity, source_error_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_name,
                error_signature,
                error_category,
                json.dumps(file_paths or [], ensure_ascii=False),
                json.dumps(libraries or [], ensure_ascii=False),
                json.dumps(tags or [], ensure_ascii=False),
                task_description,
                code_snippet,
                fix_snippet,
                root_cause,
                prevention_rule,
                negative_constraint,
                severity,
                source_error_id or None,
            ),
        )
        memory_id = cursor.lastrowid

        # Sync FTS5 index
        conn.execute(
            """INSERT INTO regression_memory_fts (rowid, task_description, root_cause, prevention_rule)
               VALUES (?, ?, ?, ?)""",
            (memory_id, task_description, root_cause, prevention_rule),
        )
        conn.commit()
        return {"id": memory_id, "status": "created"}
    finally:
        conn.close()


def get_memory(memory_id: int, project_path: Optional[str] = None) -> Optional[dict]:
    """Get a single memory by ID."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        row = conn.execute(
            "SELECT * FROM regression_memory WHERE id = ?", (memory_id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        conn.close()


def list_memories(
    *,
    include_archived: bool = False,
    limit: int = 50,
    project_path: Optional[str] = None,
) -> list[dict]:
    """List memories, optionally including archived."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        if include_archived:
            rows = conn.execute(
                "SELECT * FROM regression_memory ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM regression_memory WHERE archived = 0 ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


# ============================================================
# 3-Level Matching Engine
# ============================================================

def match_level1_exact(error_signature: str, project_path: Optional[str] = None) -> list[dict]:
    """Level 1: Exact error_signature match."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        rows = conn.execute(
            """SELECT * FROM regression_memory
               WHERE error_signature = ? AND archived = 0
               ORDER BY hit_count DESC, timestamp DESC""",
            (error_signature,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def match_level2_tags(
    file_paths: Optional[list[str]] = None,
    libraries: Optional[list[str]] = None,
    error_category: str = "",
    project_path: Optional[str] = None,
) -> list[dict]:
    """Level 2: Weighted tag scoring (files x3 + libs x2 + category x1 >= 4)."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        rows = conn.execute(
            "SELECT * FROM regression_memory WHERE archived = 0"
        ).fetchall()

        results = []
        for row in rows:
            score = _compute_tag_score(row, file_paths, libraries, error_category)
            if score >= 4:
                d = _row_to_dict(row)
                d["match_score"] = score
                results.append(d)

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results
    finally:
        conn.close()


def match_level3_fts(query: str, project_path: Optional[str] = None) -> list[dict]:
    """Level 3: FTS5 keyword search on task_description, root_cause, prevention_rule."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Escape FTS5 special characters
        fts_query = _escape_fts5_query(query)
        try:
            rows = conn.execute(
                """SELECT rm.*, bm25(regression_memory_fts) as fts_score
                   FROM regression_memory_fts fts
                   JOIN regression_memory rm ON rm.id = fts.rowid
                   WHERE regression_memory_fts MATCH ? AND rm.archived = 0
                   ORDER BY fts_score
                   LIMIT 10""",
                (fts_query,),
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        except Exception:
            # FTS query syntax error, try LIKE fallback
            like = f"%{query}%"
            rows = conn.execute(
                """SELECT * FROM regression_memory
                   WHERE archived = 0
                   AND (task_description LIKE ? OR root_cause LIKE ? OR prevention_rule LIKE ?)
                   ORDER BY hit_count DESC
                   LIMIT 10""",
                (like, like, like),
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def match_all_levels(
    error_text: str,
    *,
    file_paths: Optional[list[str]] = None,
    libraries: Optional[list[str]] = None,
    error_category: str = "",
    context: str = "",
    top_n: int = 5,
    project_path: Optional[str] = None,
) -> list[dict]:
    """Run all 3 matching levels sequentially, deduplicate, return top N."""
    seen_ids = set()
    results = []

    # Level 1: Exact signature
    signature = normalize_error_signature(error_text)
    for m in match_level1_exact(signature, project_path=project_path):
        if m["id"] not in seen_ids:
            m["match_level"] = 1
            results.append(m)
            seen_ids.add(m["id"])

    # Level 2: Tag scoring
    for m in match_level2_tags(file_paths, libraries, error_category, project_path=project_path):
        if m["id"] not in seen_ids:
            m["match_level"] = 2
            results.append(m)
            seen_ids.add(m["id"])

    # Level 3: FTS on context or error_text
    search_query = context if context else error_text[:200]
    for m in match_level3_fts(search_query, project_path=project_path):
        if m["id"] not in seen_ids:
            m["match_level"] = 3
            results.append(m)
            seen_ids.add(m["id"])

    return results[:top_n]


# ============================================================
# Counter Updates
# ============================================================

def increment_hit_count(memory_id: int, project_path: Optional[str] = None) -> None:
    """Increment hit_count for a memory."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE regression_memory SET hit_count = hit_count + 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
    finally:
        conn.close()


def increment_times_saved(memory_id: int, project_path: Optional[str] = None) -> None:
    """Increment times_saved for a memory."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE regression_memory SET times_saved = times_saved + 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
    finally:
        conn.close()


# ============================================================
# Archive
# ============================================================

def archive_memory(memory_id: int, project_path: Optional[str] = None) -> dict:
    """Soft-archive a memory."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "UPDATE regression_memory SET archived = 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found"}
        return {"status": "archived", "id": memory_id}
    finally:
        conn.close()


def unarchive_memory(memory_id: int, project_path: Optional[str] = None) -> dict:
    """Unarchive a memory."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "UPDATE regression_memory SET archived = 0 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found"}
        return {"status": "unarchived", "id": memory_id}
    finally:
        conn.close()


# ============================================================
# Stats
# ============================================================

def get_memory_stats(project_path: Optional[str] = None) -> dict:
    """Get regression memory statistics."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        total = conn.execute("SELECT COUNT(*) FROM regression_memory").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM regression_memory WHERE archived = 0").fetchone()[0]
        archived = conn.execute("SELECT COUNT(*) FROM regression_memory WHERE archived = 1").fetchone()[0]
        total_hits = conn.execute("SELECT COALESCE(SUM(hit_count), 0) FROM regression_memory").fetchone()[0]
        total_saves = conn.execute("SELECT COALESCE(SUM(times_saved), 0) FROM regression_memory").fetchone()[0]

        save_rate = (total_saves / total_hits * 100) if total_hits > 0 else 0.0

        # Top memories by hit count
        top_rows = conn.execute(
            """SELECT id, error_signature, error_category, hit_count, times_saved
               FROM regression_memory
               WHERE archived = 0
               ORDER BY hit_count DESC
               LIMIT 5"""
        ).fetchall()
        top_memories = [
            {
                "id": r["id"],
                "error_signature": r["error_signature"][:80],
                "error_category": r["error_category"],
                "hit_count": r["hit_count"],
                "times_saved": r["times_saved"],
            }
            for r in top_rows
        ]

        # Category breakdown
        cat_rows = conn.execute(
            """SELECT error_category, COUNT(*) as count
               FROM regression_memory WHERE archived = 0
               GROUP BY error_category ORDER BY count DESC"""
        ).fetchall()
        categories = {r["error_category"] or "unknown": r["count"] for r in cat_rows}

        return {
            "total": total,
            "active": active,
            "archived": archived,
            "total_hits": total_hits,
            "total_saves": total_saves,
            "save_rate": round(save_rate, 1),
            "top_memories": top_memories,
            "categories": categories,
        }
    finally:
        conn.close()


# ============================================================
# Helpers
# ============================================================

def _row_to_dict(row) -> dict:
    """Convert a sqlite3.Row to dict, parsing JSON fields."""
    d = dict(row)
    for field in ("file_paths", "libraries", "tags"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                d[field] = []
    # Remove fts_score if present (from JOIN)
    d.pop("fts_score", None)
    return d


def _compute_tag_score(row, file_paths, libraries, error_category) -> int:
    """Compute weighted tag score for Level 2 matching."""
    score = 0

    # File paths: 3 points per overlap
    if file_paths:
        try:
            mem_files = json.loads(row["file_paths"]) if row["file_paths"] else []
        except (json.JSONDecodeError, TypeError):
            mem_files = []
        for fp in file_paths:
            if any(fp in mf or mf in fp for mf in mem_files):
                score += 3
                break  # one match is enough

    # Libraries: 2 points per overlap
    if libraries:
        try:
            mem_libs = json.loads(row["libraries"]) if row["libraries"] else []
        except (json.JSONDecodeError, TypeError):
            mem_libs = []
        for lib in libraries:
            if lib in mem_libs:
                score += 2
                break

    # Category: 1 point for match
    if error_category and row["error_category"] == error_category:
        score += 1

    return score


def search_memories(
    query: str = "",
    category: str = "",
    limit: int = 20,
    include_archived: bool = False,
    project_path: Optional[str] = None,
) -> list[dict]:
    """Search memories by keyword (FTS5) and/or category filter."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # FTS search if query provided
        if query:
            fts_query = _escape_fts5_query(query)
            try:
                sql = """SELECT rm.*
                         FROM regression_memory_fts fts
                         JOIN regression_memory rm ON rm.id = fts.rowid
                         WHERE regression_memory_fts MATCH ?"""
                params: list = [fts_query]

                if not include_archived:
                    sql += " AND rm.archived = 0"
                if category:
                    sql += " AND rm.error_category = ?"
                    params.append(category)

                sql += " ORDER BY bm25(regression_memory_fts) LIMIT ?"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
                return [_row_to_dict(r) for r in rows]
            except Exception:
                # FTS syntax error, fall back to LIKE
                like = f"%{query}%"
                sql = """SELECT * FROM regression_memory
                         WHERE (task_description LIKE ? OR root_cause LIKE ? OR prevention_rule LIKE ?)"""
                params = [like, like, like]

                if not include_archived:
                    sql += " AND archived = 0"
                if category:
                    sql += " AND error_category = ?"
                    params.append(category)

                sql += " ORDER BY hit_count DESC LIMIT ?"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
                return [_row_to_dict(r) for r in rows]
        else:
            # Category-only filter (no keyword)
            sql = "SELECT * FROM regression_memory WHERE 1=1"
            params = []

            if not include_archived:
                sql += " AND archived = 0"
            if category:
                sql += " AND error_category = ?"
                params.append(category)

            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def mark_stale_memories(
    days_threshold: int = 60,
    project_path: Optional[str] = None,
) -> dict:
    """Auto-archive memories with 0 hits older than threshold days."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Find stale memories: hit_count = 0, older than threshold, not already archived
        rows = conn.execute(
            """SELECT id FROM regression_memory
               WHERE hit_count = 0
               AND archived = 0
               AND timestamp < datetime('now', ? || ' days')""",
            (f"-{days_threshold}",),
        ).fetchall()

        stale_ids = [r["id"] for r in rows]

        if stale_ids:
            placeholders = ",".join("?" for _ in stale_ids)
            conn.execute(
                f"UPDATE regression_memory SET archived = 1 WHERE id IN ({placeholders})",
                stale_ids,
            )
            conn.commit()

        return {"archived_count": len(stale_ids), "ids": stale_ids}
    finally:
        conn.close()


def get_memory_report(
    days: int = 30,
    project_path: Optional[str] = None,
) -> dict:
    """Generate memory report for given period."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # New memories in period
        new_count = conn.execute(
            """SELECT COUNT(*) FROM regression_memory
               WHERE timestamp >= datetime('now', ? || ' days')""",
            (f"-{days}",),
        ).fetchone()[0]

        # Total hits in period (use overall stats since we don't track per-hit timestamps)
        total_hits = conn.execute(
            "SELECT COALESCE(SUM(hit_count), 0) FROM regression_memory"
        ).fetchone()[0]
        total_saves = conn.execute(
            "SELECT COALESCE(SUM(times_saved), 0) FROM regression_memory"
        ).fetchone()[0]

        save_rate = (total_saves / total_hits * 100) if total_hits > 0 else 0.0

        # Top 5 most-hit memories
        top_rows = conn.execute(
            """SELECT id, error_signature, error_category, hit_count, times_saved, root_cause
               FROM regression_memory
               WHERE archived = 0 AND hit_count > 0
               ORDER BY hit_count DESC
               LIMIT 5"""
        ).fetchall()
        top_memories = [
            {
                "id": r["id"],
                "error_signature": r["error_signature"][:80],
                "error_category": r["error_category"],
                "hit_count": r["hit_count"],
                "times_saved": r["times_saved"],
                "root_cause": r["root_cause"][:100] if r["root_cause"] else "",
            }
            for r in top_rows
        ]

        # Top 3 categories
        cat_rows = conn.execute(
            """SELECT error_category, COUNT(*) as count
               FROM regression_memory WHERE archived = 0
               GROUP BY error_category ORDER BY count DESC LIMIT 3"""
        ).fetchall()
        top_categories = [
            {"category": r["error_category"] or "unknown", "count": r["count"]}
            for r in cat_rows
        ]

        # Active / archived counts
        active = conn.execute(
            "SELECT COUNT(*) FROM regression_memory WHERE archived = 0"
        ).fetchone()[0]
        archived = conn.execute(
            "SELECT COUNT(*) FROM regression_memory WHERE archived = 1"
        ).fetchone()[0]

        # Time saved estimate: saves × 15 minutes
        time_saved_minutes = total_saves * 15
        time_saved_hours = round(time_saved_minutes / 60, 1)

        return {
            "period_days": days,
            "new_memories": new_count,
            "active": active,
            "archived": archived,
            "total_hits": total_hits,
            "total_saves": total_saves,
            "save_rate": round(save_rate, 1),
            "top_memories": top_memories,
            "top_categories": top_categories,
            "time_saved_minutes": time_saved_minutes,
            "time_saved_hours": time_saved_hours,
        }
    finally:
        conn.close()


def get_memory_for_promote(memory_id: int, project_path: Optional[str] = None) -> Optional[dict]:
    """Get memory data formatted for promotion (excludes sensitive fields).

    Returns only the fields safe for global storage:
    error_signature, error_category, libraries, tags, root_cause,
    prevention_rule, negative_constraint, severity, source_memory_id.

    Excludes: task_description, code_snippet, fix_snippet, source_error_id.
    """
    mem = get_memory(memory_id, project_path=project_path)
    if mem is None:
        return None
    return {
        "error_signature": mem.get("error_signature", ""),
        "error_category": mem.get("error_category", ""),
        "libraries": mem.get("libraries") or [],
        "tags": mem.get("tags") or [],
        "root_cause": mem.get("root_cause", ""),
        "prevention_rule": mem.get("prevention_rule", ""),
        "negative_constraint": mem.get("negative_constraint", ""),
        "severity": mem.get("severity", 3),
        "source_memory_id": memory_id,
    }


def _escape_fts5_query(query: str) -> str:
    """Escape special FTS5 characters."""
    if any(c in query for c in '.+-*(){}[]^~"'):
        escaped = query.replace('"', '""')
        return f'"{escaped}"'
    return query
