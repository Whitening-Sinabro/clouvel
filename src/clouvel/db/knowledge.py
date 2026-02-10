"""SQLite Knowledge Base for Clouvel.

Stores decisions, meetings, code locations, and events across sessions.
Enables context recovery and decision tracking.

Security: Optional encryption via CLOUVEL_KB_KEY environment variable.
"""

import sqlite3
import json
import uuid
import os
import hashlib
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Encryption support (optional)
_ENCRYPTION_KEY = os.environ.get("CLOUVEL_KB_KEY")
_FERNET = None

def _init_encryption():
    """Initialize encryption if key is set and cryptography is available."""
    global _FERNET
    if not _ENCRYPTION_KEY:
        return False
    try:
        from cryptography.fernet import Fernet
        # Derive a valid Fernet key from the user's key
        key_bytes = hashlib.sha256(_ENCRYPTION_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        _FERNET = Fernet(fernet_key)
        return True
    except ImportError:
        return False

def _encrypt(text: str) -> str:
    """Encrypt text if encryption is enabled."""
    if not text or not _FERNET:
        return text
    try:
        return "ENC:" + _FERNET.encrypt(text.encode()).decode()
    except Exception:
        return text

def _decrypt(text: str) -> str:
    """Decrypt text if it's encrypted."""
    if not text or not _FERNET:
        return text
    if not text.startswith("ENC:"):
        return text  # Not encrypted, return as-is
    try:
        return _FERNET.decrypt(text[4:].encode()).decode()
    except Exception:
        return text  # Decryption failed, return as-is

# Initialize encryption on module load
_USE_ENCRYPTION = _init_encryption()

# Global DB path: ~/.clouvel/knowledge.db
KNOWLEDGE_DB_PATH = Path.home() / ".clouvel" / "knowledge.db"
ARCHIVE_DB_PATH = Path.home() / ".clouvel" / "knowledge_archive.db"

# Size limits
MAX_DB_SIZE_MB = 50
ARCHIVE_TRIGGER_MB = 40


def get_knowledge_db() -> Path:
    """Get knowledge database path."""
    KNOWLEDGE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return KNOWLEDGE_DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    db_path = get_knowledge_db()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_knowledge_db(auto_archive: bool = True) -> Path:
    """Initialize knowledge database with schema.

    Args:
        auto_archive: If True, check and archive old data if DB is large
    """
    db_path = get_knowledge_db()

    conn = get_connection()
    try:
        conn.executescript(KNOWLEDGE_SCHEMA)
        # v4.0: Add archived column (idempotent migration)
        try:
            conn.execute("ALTER TABLE decisions ADD COLUMN archived INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

        # v1.0: Domain scoping (idempotent migration)
        try:
            conn.execute("ALTER TABLE projects ADD COLUMN domain TEXT DEFAULT NULL")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            conn.execute("ALTER TABLE global_memories ADD COLUMN domain TEXT DEFAULT NULL")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_global_memories_domain ON global_memories(domain)")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        conn.commit()
    finally:
        conn.close()

    # Auto-archive if DB is getting large
    if auto_archive and db_path.exists():
        size_mb = get_db_size_mb()
        if size_mb >= ARCHIVE_TRIGGER_MB:
            check_and_archive()

    return db_path


# ============================================================
# CRUD Operations
# ============================================================

def get_or_create_project(
    name: str,
    path: Optional[str] = None,
    tech_stack: Optional[str] = None,
    domain: Optional[str] = None,
) -> str:
    """Get existing project or create new one. Returns project_id.

    Args:
        name: Project name
        path: Project filesystem path
        tech_stack: Tech stack description
        domain: Domain scoping (personal/work/client). Only set on creation.
    """
    conn = get_connection()
    try:
        # Try to find existing project
        if path:
            cursor = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (path,)
            )
        else:
            cursor = conn.execute(
                "SELECT id FROM projects WHERE name = ?",
                (name,)
            )

        row = cursor.fetchone()
        if row:
            return row["id"]

        # Create new project
        project_id = str(uuid.uuid4())[:8]
        conn.execute(
            """INSERT INTO projects (id, name, path, tech_stack, created_at, domain)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (project_id, name, path, tech_stack, datetime.now().isoformat(), domain)
        )
        conn.commit()
        return project_id
    finally:
        conn.close()


def set_project_domain(project_id: str, domain: str) -> Dict[str, Any]:
    """Set the domain for a project.

    Args:
        project_id: Project ID
        domain: Domain value (personal/work/client)

    Returns:
        {"status": "updated", "project_id": ..., "domain": ...}
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE projects SET domain = ? WHERE id = ?",
            (domain, project_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found", "project_id": project_id}
        return {"status": "updated", "project_id": project_id, "domain": domain}
    finally:
        conn.close()


def get_project_domain(project_id: str) -> Optional[str]:
    """Get the domain for a project. Returns None if not set."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT domain FROM projects WHERE id = ?",
            (project_id,),
        )
        row = cursor.fetchone()
        if row:
            return row["domain"]
        return None
    finally:
        conn.close()


def record_decision(
    category: str,
    decision: str,
    reasoning: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    project_id: Optional[str] = None,
    meeting_id: Optional[str] = None
) -> str:
    """Record a decision. Returns decision_id."""
    init_knowledge_db()  # Ensure DB exists

    # Encrypt sensitive fields if encryption is enabled
    enc_decision = _encrypt(decision)
    enc_reasoning = _encrypt(reasoning) if reasoning else None

    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO decisions
               (project_id, meeting_id, category, decision, reasoning, alternatives, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                meeting_id,
                category,
                enc_decision,
                enc_reasoning,
                json.dumps(alternatives) if alternatives else None,
                datetime.now().isoformat()
            )
        )
        conn.commit()
        decision_id = str(cursor.lastrowid)

        # Update FTS index (use plaintext for search - category is not sensitive)
        search_content = f"{category} {decision} {reasoning or ''}"
        _update_search_index(conn, f"decision:{decision_id}", search_content, project_id)
        conn.commit()

        return decision_id
    finally:
        conn.close()


def record_location(
    name: str,
    repo: str,
    path: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None
) -> str:
    """Record a code location. Returns location_id."""
    init_knowledge_db()

    # Encrypt sensitive description if encryption is enabled
    enc_description = _encrypt(description) if description else None

    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO locations
               (project_id, name, repo, path, description, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                name,
                repo,
                path,
                enc_description,
                datetime.now().isoformat()
            )
        )
        conn.commit()
        location_id = str(cursor.lastrowid)

        # Update FTS index (use plaintext for search)
        content = f"{name} {repo} {path} {description or ''}"
        _update_search_index(conn, f"location:{location_id}", content, project_id)
        conn.commit()

        return location_id
    finally:
        conn.close()


def record_meeting(
    topic: str,
    participants: List[str],
    contributions: Dict[str, str],
    project_id: Optional[str] = None
) -> str:
    """Record a meeting. Returns meeting_id."""
    init_knowledge_db()

    meeting_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO meetings
               (id, project_id, topic, participants, contributions, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                meeting_id,
                project_id,
                topic,
                json.dumps(participants),
                json.dumps(contributions),
                datetime.now().isoformat()
            )
        )
        conn.commit()

        # Update FTS index
        content = f"{topic} {' '.join(participants)} {json.dumps(contributions)}"
        _update_search_index(conn, f"meeting:{meeting_id}", content, project_id)
        conn.commit()

        return meeting_id
    finally:
        conn.close()


def record_event(
    event_type: str,
    data: Dict[str, Any],
    project_id: Optional[str] = None
) -> str:
    """Record an event. Returns event_id."""
    init_knowledge_db()

    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO events
               (project_id, type, data, created_at)
               VALUES (?, ?, ?, ?)""",
            (
                project_id,
                event_type,
                json.dumps(data),
                datetime.now().isoformat()
            )
        )
        conn.commit()
        return str(cursor.lastrowid)
    finally:
        conn.close()


def search_knowledge(
    query: str,
    project_id: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Search knowledge base using FTS5 with LIKE fallback.

    v3.1: Falls back to LIKE search if FTS5 returns nothing.
    """
    init_knowledge_db()

    conn = get_connection()
    try:
        results = []

        # Try FTS5 MATCH first (escape special chars for FTS5)
        fts_query = _escape_fts5_query(query)
        try:
            if project_id:
                cursor = conn.execute(
                    """SELECT content_id, content, project_id,
                              bm25(search_index) as score
                       FROM search_index
                       WHERE search_index MATCH ? AND project_id = ?
                       ORDER BY score
                       LIMIT ?""",
                    (fts_query, project_id, limit)
                )
            else:
                cursor = conn.execute(
                    """SELECT content_id, content, project_id,
                              bm25(search_index) as score
                       FROM search_index
                       WHERE search_index MATCH ?
                       ORDER BY score
                       LIMIT ?""",
                    (fts_query, limit)
                )

            for row in cursor:
                content_id = row["content_id"]
                content_type, actual_id = content_id.split(":", 1)
                results.append({
                    "type": content_type,
                    "id": actual_id,
                    "content": row["content"],
                    "project_id": row["project_id"],
                    "score": row["score"]
                })
        except sqlite3.OperationalError:
            # FTS5 query syntax error, fall through to LIKE
            pass

        # v3.1: Fallback to LIKE search if FTS5 returns nothing
        if not results:
            like_pattern = f"%{query}%"
            if project_id:
                cursor = conn.execute(
                    """SELECT content_id, content, project_id
                       FROM search_index
                       WHERE content LIKE ? AND project_id = ?
                       LIMIT ?""",
                    (like_pattern, project_id, limit)
                )
            else:
                cursor = conn.execute(
                    """SELECT content_id, content, project_id
                       FROM search_index
                       WHERE content LIKE ?
                       LIMIT ?""",
                    (like_pattern, limit)
                )

            for row in cursor:
                content_id = row["content_id"]
                content_type, actual_id = content_id.split(":", 1)
                results.append({
                    "type": content_type,
                    "id": actual_id,
                    "content": row["content"],
                    "project_id": row["project_id"],
                    "score": 0  # LIKE doesn't have score
                })

        return results
    finally:
        conn.close()


def _escape_fts5_query(query: str) -> str:
    """Escape special FTS5 characters and format query.

    v3.1: Makes queries more robust for common patterns.
    """
    # For simple queries, wrap in quotes to match exact phrase
    # This helps with queries like "v3.1" which have special chars
    if any(c in query for c in '.+-*(){}[]^~"'):
        # Escape double quotes in the query
        escaped = query.replace('"', '""')
        return f'"{escaped}"'
    return query


def get_recent_decisions(
    project_id: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get recent decisions (excludes archived)."""
    init_knowledge_db()

    conn = get_connection()
    try:
        if project_id:
            cursor = conn.execute(
                """SELECT * FROM decisions
                   WHERE project_id = ? AND (archived IS NULL OR archived = 0)
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (project_id, limit)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM decisions
                   WHERE (archived IS NULL OR archived = 0)
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,)
            )

        results = []
        for row in cursor:
            d = dict(row)
            # Decrypt sensitive fields
            d['decision'] = _decrypt(d.get('decision', ''))
            d['reasoning'] = _decrypt(d.get('reasoning', '')) if d.get('reasoning') else None
            results.append(d)

        return results
    finally:
        conn.close()


def get_recent_locations(
    project_id: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get recent code locations."""
    init_knowledge_db()

    conn = get_connection()
    try:
        if project_id:
            cursor = conn.execute(
                """SELECT * FROM locations
                   WHERE project_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (project_id, limit)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM locations
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,)
            )

        results = []
        for row in cursor:
            loc = dict(row)
            # Decrypt sensitive fields
            loc['description'] = _decrypt(loc.get('description', '')) if loc.get('description') else None
            results.append(loc)

        return results
    finally:
        conn.close()


def get_project_summary(project_id: str) -> Dict[str, Any]:
    """Get summary of a project's knowledge."""
    init_knowledge_db()

    conn = get_connection()
    try:
        # Get project info
        cursor = conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
        project = dict(cursor.fetchone()) if cursor.fetchone() else {}

        # Count items
        counts = {}
        for table in ["decisions", "locations", "meetings", "events"]:
            cursor = conn.execute(
                f"SELECT COUNT(*) as count FROM {table} WHERE project_id = ?",
                (project_id,)
            )
            counts[table] = cursor.fetchone()["count"]

        return {
            "project": project,
            "counts": counts
        }
    finally:
        conn.close()


def _update_search_index(
    conn: sqlite3.Connection,
    content_id: str,
    content: str,
    project_id: Optional[str]
):
    """Update FTS5 search index."""
    conn.execute(
        """INSERT INTO search_index (content_id, content, project_id)
           VALUES (?, ?, ?)""",
        (content_id, content, project_id)
    )


def get_db_size_mb() -> float:
    """Get current database size in MB."""
    if not KNOWLEDGE_DB_PATH.exists():
        return 0.0
    return KNOWLEDGE_DB_PATH.stat().st_size / (1024 * 1024)


def check_and_archive() -> dict:
    """Check DB size and archive old data if needed.

    Returns dict with:
    - size_mb: current size
    - archived: bool
    - archived_count: number of items archived (if any)
    """
    size_mb = get_db_size_mb()

    if size_mb < ARCHIVE_TRIGGER_MB:
        return {"size_mb": size_mb, "archived": False, "archived_count": 0}

    # Archive old data (older than 30 days)
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()

    conn = get_connection()
    try:
        # Count items to archive
        cursor = conn.execute(
            "SELECT COUNT(*) as cnt FROM decisions WHERE created_at < ?",
            (cutoff_date,)
        )
        decisions_count = cursor.fetchone()["cnt"]

        cursor = conn.execute(
            "SELECT COUNT(*) as cnt FROM locations WHERE created_at < ?",
            (cutoff_date,)
        )
        locations_count = cursor.fetchone()["cnt"]

        cursor = conn.execute(
            "SELECT COUNT(*) as cnt FROM events WHERE created_at < ?",
            (cutoff_date,)
        )
        events_count = cursor.fetchone()["cnt"]

        total_count = decisions_count + locations_count + events_count

        if total_count == 0:
            return {"size_mb": size_mb, "archived": False, "archived_count": 0, "message": "No old data to archive"}

        # Create archive DB connection
        archive_conn = sqlite3.connect(str(ARCHIVE_DB_PATH))
        archive_conn.row_factory = sqlite3.Row
        archive_conn.executescript(KNOWLEDGE_SCHEMA)

        # Copy old decisions to archive
        cursor = conn.execute(
            "SELECT * FROM decisions WHERE created_at < ?",
            (cutoff_date,)
        )
        for row in cursor:
            archive_conn.execute(
                """INSERT OR IGNORE INTO decisions
                   (id, project_id, meeting_id, category, decision, reasoning, alternatives, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["project_id"], row["meeting_id"], row["category"],
                 row["decision"], row["reasoning"], row["alternatives"], row["created_at"])
            )

        # Copy old locations to archive
        cursor = conn.execute(
            "SELECT * FROM locations WHERE created_at < ?",
            (cutoff_date,)
        )
        for row in cursor:
            archive_conn.execute(
                """INSERT OR IGNORE INTO locations
                   (id, project_id, name, repo, path, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["project_id"], row["name"], row["repo"],
                 row["path"], row["description"], row["created_at"])
            )

        # Copy old events to archive
        cursor = conn.execute(
            "SELECT * FROM events WHERE created_at < ?",
            (cutoff_date,)
        )
        for row in cursor:
            archive_conn.execute(
                """INSERT OR IGNORE INTO events
                   (id, project_id, type, data, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (row["id"], row["project_id"], row["type"], row["data"], row["created_at"])
            )

        archive_conn.commit()
        archive_conn.close()

        # Delete old data from main DB
        conn.execute("DELETE FROM decisions WHERE created_at < ?", (cutoff_date,))
        conn.execute("DELETE FROM locations WHERE created_at < ?", (cutoff_date,))
        conn.execute("DELETE FROM events WHERE created_at < ?", (cutoff_date,))

        # Clean up search index for deleted items
        conn.execute("DELETE FROM search_index WHERE content_id LIKE 'decision:%' AND content_id NOT IN (SELECT 'decision:' || id FROM decisions)")
        conn.execute("DELETE FROM search_index WHERE content_id LIKE 'location:%' AND content_id NOT IN (SELECT 'location:' || id FROM locations)")

        conn.commit()

        # Vacuum to reclaim space
        conn.execute("VACUUM")

        new_size_mb = get_db_size_mb()

        return {
            "size_mb": new_size_mb,
            "archived": True,
            "archived_count": total_count,
            "archive_path": str(ARCHIVE_DB_PATH),
            "message": f"Archived {total_count} items older than 30 days"
        }

    finally:
        conn.close()


def rebuild_search_index() -> int:
    """Rebuild entire search index from existing data."""
    init_knowledge_db()

    conn = get_connection()
    try:
        # Clear existing index
        conn.execute("DELETE FROM search_index")

        count = 0

        # Index decisions
        cursor = conn.execute("SELECT id, category, decision, reasoning, project_id FROM decisions")
        for row in cursor:
            content = f"{row['category']} {row['decision']} {row['reasoning'] or ''}"
            _update_search_index(conn, f"decision:{row['id']}", content, row['project_id'])
            count += 1

        # Index locations
        cursor = conn.execute("SELECT id, name, repo, path, description, project_id FROM locations")
        for row in cursor:
            content = f"{row['name']} {row['repo']} {row['path']} {row['description'] or ''}"
            _update_search_index(conn, f"location:{row['id']}", content, row['project_id'])
            count += 1

        # Index meetings
        cursor = conn.execute("SELECT id, topic, participants, contributions, project_id FROM meetings")
        for row in cursor:
            content = f"{row['topic']} {row['participants']} {row['contributions']}"
            _update_search_index(conn, f"meeting:{row['id']}", content, row['project_id'])
            count += 1

        conn.commit()
        return count
    finally:
        conn.close()


# ============================================================
# Free Tier KB Limits (v3.3: 7일 보관 + 50개 제한)
# ============================================================

FREE_KB_RETENTION_DAYS = 7
FREE_KB_MAX_ITEMS = 50


def enforce_free_kb_limits(project_path: str) -> Dict[str, Any]:
    """Enforce KB limits for Free tier users.

    v3.3: Free tier limits:
    - 7 days retention (older items deleted)
    - 50 items max (oldest deleted when exceeded)

    Called automatically when adding new items.

    Args:
        project_path: Project path for filtering

    Returns:
        dict with enforced, deleted_old, deleted_excess, message
    """
    # Check if Pro user
    try:
        from ..license_common import is_developer, load_license_cache, is_full_trial_active
        if is_developer():
            return {"enforced": False, "reason": "developer"}
        cached = load_license_cache()
        if cached and cached.get("tier"):
            return {"enforced": False, "reason": "pro"}
        if is_full_trial_active():
            return {"enforced": False, "reason": "trial"}
    except ImportError:
        pass

    init_knowledge_db()

    conn = get_connection()
    try:
        project_id = hashlib.sha256(project_path.encode()).hexdigest()[:16]
        cutoff_date = (datetime.now() - __import__('datetime').timedelta(days=FREE_KB_RETENTION_DAYS)).isoformat()

        # 1. Archive items older than 7 days (soft-archive, v4.0)
        # Get items to be archived for reporting
        cursor = conn.execute(
            """SELECT id, decision FROM decisions
               WHERE project_id = ? AND created_at < ? AND (archived IS NULL OR archived = 0)
               ORDER BY created_at ASC LIMIT 5""",
            (project_id, cutoff_date)
        )
        old_items = [{"id": r["id"], "decision": _decrypt(r["decision"])[:50]} for r in cursor.fetchall()]

        cursor = conn.execute(
            "UPDATE decisions SET archived = 1 WHERE project_id = ? AND created_at < ? AND (archived IS NULL OR archived = 0)",
            (project_id, cutoff_date)
        )
        archived_old = cursor.rowcount

        # 2. Check active count and archive excess
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM decisions WHERE project_id = ? AND (archived IS NULL OR archived = 0)",
            (project_id,)
        )
        total = cursor.fetchone()["count"]

        archived_excess = 0
        excess_items = []

        if total > FREE_KB_MAX_ITEMS:
            excess = total - FREE_KB_MAX_ITEMS

            # Get items to be archived for reporting
            cursor = conn.execute(
                """SELECT id, decision FROM decisions
                   WHERE project_id = ? AND (archived IS NULL OR archived = 0)
                   ORDER BY created_at ASC LIMIT ?""",
                (project_id, excess)
            )
            excess_items = [{"id": r["id"], "decision": _decrypt(r["decision"])[:50]} for r in cursor.fetchall()]

            # Archive oldest items exceeding limit
            cursor = conn.execute(
                """UPDATE decisions SET archived = 1 WHERE id IN (
                    SELECT id FROM decisions
                    WHERE project_id = ? AND (archived IS NULL OR archived = 0)
                    ORDER BY created_at ASC LIMIT ?
                )""",
                (project_id, excess)
            )
            archived_excess = cursor.rowcount

        conn.commit()

        # Return result with Ghost UX message (v4.0)
        if archived_old > 0 or archived_excess > 0:
            archived_items = old_items + excess_items
            items_summary = "\n".join([f"• {item['decision']}..." for item in archived_items[:5]])
            if len(archived_items) > 5:
                items_summary += f"\n• ... and {len(archived_items) - 5} more"

            message = f"""
📦 Knowledge Base 정리 알림

Free 플랜 정책에 따라 다음 항목이 아카이브되었습니다:

{items_summary}

**아카이브 내역**:
- 7일 경과: {archived_old}개
- 50개 초과: {archived_excess}개

💡 제목은 보이지만, 내용은 잠겨있어요.
   (titles visible, content locked)

Pro는 모든 결정을 **영구 보관**합니다.
6개월 후에도 "아, 그때 이런 이유로 이렇게 했구나" 확인 가능.

→ https://polar.sh/clouvel (월 $7.99)
"""
            # Log event
            try:
                from ..analytics import log_event
                log_event("kb_cleanup", {
                    "archived_old": archived_old,
                    "archived_excess": archived_excess,
                })
            except Exception:
                pass

            return {
                "enforced": True,
                "archived_old": archived_old,
                "archived_excess": archived_excess,
                "archived_items": archived_items,
                "message": message,
            }

        return {"enforced": False, "archived_old": 0, "archived_excess": 0}

    finally:
        conn.close()


# ============================================================
# Schema
# ============================================================

KNOWLEDGE_SCHEMA = """
-- 프로젝트
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT,
    tech_stack TEXT,
    created_at TEXT NOT NULL,
    archived_at TEXT
);

-- 회의
CREATE TABLE IF NOT EXISTS meetings (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    topic TEXT NOT NULL,
    participants TEXT NOT NULL,  -- JSON array
    contributions TEXT NOT NULL, -- JSON object
    created_at TEXT NOT NULL
);

-- 결정
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    meeting_id TEXT,
    category TEXT NOT NULL,
    decision TEXT NOT NULL,
    reasoning TEXT,
    alternatives TEXT,  -- JSON array
    created_at TEXT NOT NULL
);

-- 코드 위치
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    name TEXT NOT NULL,
    repo TEXT NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

-- 이벤트 로그
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    type TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON
    created_at TEXT NOT NULL
);

-- 전문 검색 (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
    content_id,
    content,
    project_id
);

-- 글로벌 메모리 (v5.0: Cross-Project Memory Transfer)
CREATE TABLE IF NOT EXISTS global_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT REFERENCES projects(id),
    origin_project_name TEXT,
    error_signature TEXT,
    error_category TEXT,
    libraries TEXT,          -- JSON array (tech stack filtering)
    tags TEXT,               -- JSON array
    root_cause TEXT NOT NULL,
    prevention_rule TEXT NOT NULL,
    negative_constraint TEXT,
    severity INTEGER DEFAULT 3,
    hit_count INTEGER DEFAULT 0,
    times_saved INTEGER DEFAULT 0,
    source_memory_id INTEGER,
    promoted_at TEXT NOT NULL,
    archived BOOLEAN DEFAULT 0
);

-- 글로벌 메모리 FTS5 인덱스
CREATE VIRTUAL TABLE IF NOT EXISTS global_memories_fts USING fts5(
    root_cause, prevention_rule,
    content='global_memories', content_rowid='id'
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category);
CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_locations_project ON locations(project_id);
CREATE INDEX IF NOT EXISTS idx_locations_repo ON locations(repo);
CREATE INDEX IF NOT EXISTS idx_meetings_project ON meetings(project_id);
CREATE INDEX IF NOT EXISTS idx_events_project ON events(project_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_global_memories_project ON global_memories(project_id);
CREATE INDEX IF NOT EXISTS idx_global_memories_signature ON global_memories(error_signature);
CREATE INDEX IF NOT EXISTS idx_global_memories_category ON global_memories(error_category);
CREATE INDEX IF NOT EXISTS idx_global_memories_archived ON global_memories(archived);
"""


# ============================================================
# Global Memory CRUD (v5.0: Cross-Project Memory Transfer)
# ============================================================

def promote_memory(
    memory_data: Dict[str, Any],
    project_id: str,
    origin_project_name: str,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """Promote a local regression memory to global.

    Only root_cause, prevention_rule, and metadata are stored.
    error_text/code_snippet are excluded (sensitive data stays local).

    Args:
        memory_data: Dict with error_signature, error_category, libraries,
                     tags, root_cause, prevention_rule, negative_constraint,
                     severity, source_memory_id
        project_id: Project ID in knowledge DB
        origin_project_name: Human-readable project name
        domain: Domain scoping (personal/work/client). Inherited from project if not set.

    Returns:
        {"id": int, "status": "promoted"} or {"status": "duplicate"}
    """
    init_knowledge_db()

    conn = get_connection()
    try:
        # Duplicate check: same error_signature + project_id
        existing = conn.execute(
            """SELECT id FROM global_memories
               WHERE error_signature = ? AND project_id = ?""",
            (memory_data.get("error_signature", ""), project_id),
        ).fetchone()

        if existing:
            return {"status": "duplicate", "existing_id": existing["id"]}

        cursor = conn.execute(
            """INSERT INTO global_memories (
                project_id, origin_project_name, error_signature, error_category,
                libraries, tags, root_cause, prevention_rule, negative_constraint,
                severity, source_memory_id, promoted_at, domain
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                origin_project_name,
                memory_data.get("error_signature", ""),
                memory_data.get("error_category", ""),
                json.dumps(memory_data.get("libraries") or [], ensure_ascii=False),
                json.dumps(memory_data.get("tags") or [], ensure_ascii=False),
                memory_data["root_cause"],
                memory_data["prevention_rule"],
                memory_data.get("negative_constraint", ""),
                memory_data.get("severity", 3),
                memory_data.get("source_memory_id"),
                datetime.now().isoformat(),
                domain,
            ),
        )
        memory_id = cursor.lastrowid

        # Sync FTS5 index
        conn.execute(
            """INSERT INTO global_memories_fts (rowid, root_cause, prevention_rule)
               VALUES (?, ?, ?)""",
            (memory_id, memory_data["root_cause"], memory_data["prevention_rule"]),
        )
        conn.commit()
        return {"id": memory_id, "status": "promoted"}
    finally:
        conn.close()


def search_global_memories(
    query: str,
    project_id_exclude: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search global memories using FTS5 with LIKE fallback.

    Args:
        query: Search keyword
        project_id_exclude: Exclude memories from this project (prevent local/global overlap)
        category: Filter by error_category
        limit: Max results
        domain: Filter by domain (personal/work/client). None returns all.

    Returns:
        List of global memory dicts
    """
    init_knowledge_db()

    conn = get_connection()
    try:
        results = []

        # Try FTS5 first
        fts_query = _escape_fts5_query(query)
        try:
            rows = conn.execute(
                """SELECT gm.* FROM global_memories_fts fts
                   JOIN global_memories gm ON gm.id = fts.rowid
                   WHERE global_memories_fts MATCH ? AND gm.archived = 0
                   ORDER BY bm25(global_memories_fts)
                   LIMIT ?""",
                (fts_query, limit * 2),  # fetch extra for filtering
            ).fetchall()

            for row in rows:
                d = _global_row_to_dict(row)
                if project_id_exclude and d.get("project_id") == project_id_exclude:
                    continue
                if category and d.get("error_category") != category:
                    continue
                if domain:
                    mem_domain = d.get("domain") or "personal"
                    if mem_domain != domain:
                        continue
                results.append(d)
                if len(results) >= limit:
                    break
        except sqlite3.OperationalError:
            pass

        # LIKE fallback
        if not results:
            like_pattern = f"%{query}%"
            rows = conn.execute(
                """SELECT * FROM global_memories
                   WHERE archived = 0
                   AND (root_cause LIKE ? OR prevention_rule LIKE ?)
                   ORDER BY hit_count DESC
                   LIMIT ?""",
                (like_pattern, like_pattern, limit * 2),
            ).fetchall()

            for row in rows:
                d = _global_row_to_dict(row)
                if project_id_exclude and d.get("project_id") == project_id_exclude:
                    continue
                if category and d.get("error_category") != category:
                    continue
                if domain:
                    mem_domain = d.get("domain") or "personal"
                    if mem_domain != domain:
                        continue
                results.append(d)
                if len(results) >= limit:
                    break

        return results
    finally:
        conn.close()


def get_global_memory_stats() -> Dict[str, Any]:
    """Get global memory statistics."""
    init_knowledge_db()

    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM global_memories").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM global_memories WHERE archived = 0").fetchone()[0]
        archived = conn.execute("SELECT COUNT(*) FROM global_memories WHERE archived = 1").fetchone()[0]

        # Top memories by hit_count
        top_rows = conn.execute(
            """SELECT id, origin_project_name, error_category, root_cause, hit_count, times_saved
               FROM global_memories WHERE archived = 0
               ORDER BY hit_count DESC LIMIT 5"""
        ).fetchall()
        top_memories = [
            {
                "id": r["id"],
                "origin_project_name": r["origin_project_name"],
                "error_category": r["error_category"],
                "root_cause": (r["root_cause"] or "")[:100],
                "hit_count": r["hit_count"],
                "times_saved": r["times_saved"],
            }
            for r in top_rows
        ]

        # Top categories
        cat_rows = conn.execute(
            """SELECT error_category, COUNT(*) as count
               FROM global_memories WHERE archived = 0
               GROUP BY error_category ORDER BY count DESC"""
        ).fetchall()
        top_categories = {r["error_category"] or "unknown": r["count"] for r in cat_rows}

        return {
            "total": total,
            "active": active,
            "archived": archived,
            "top_memories": top_memories,
            "top_categories": top_categories,
        }
    finally:
        conn.close()


def archive_global_memory(memory_id: int) -> Dict[str, Any]:
    """Archive a global memory."""
    init_knowledge_db()

    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE global_memories SET archived = 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found"}
        return {"status": "archived", "id": memory_id}
    finally:
        conn.close()


def unarchive_global_memory(memory_id: int) -> Dict[str, Any]:
    """Unarchive a global memory."""
    init_knowledge_db()

    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE global_memories SET archived = 0 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found"}
        return {"status": "unarchived", "id": memory_id}
    finally:
        conn.close()


def increment_global_hit(memory_id: int) -> None:
    """Increment hit_count for a global memory."""
    init_knowledge_db()

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE global_memories SET hit_count = hit_count + 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
    finally:
        conn.close()


def increment_global_save(memory_id: int) -> None:
    """Increment times_saved for a global memory."""
    init_knowledge_db()

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE global_memories SET times_saved = times_saved + 1 WHERE id = ?",
            (memory_id,),
        )
        conn.commit()
    finally:
        conn.close()


def _global_row_to_dict(row) -> Dict[str, Any]:
    """Convert a global_memories row to dict, parsing JSON fields."""
    d = dict(row)
    for field in ("libraries", "tags"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                d[field] = []
    return d
