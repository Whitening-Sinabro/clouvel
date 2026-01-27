"""Knowledge Base tools for Clouvel.

Tools for recording and retrieving decisions, code locations, and context.
Requires Pro license - db module not included in Free version.
Developer mode: full access for development.

v3.1: Runtime entitlement checks (no import-time constants).
v3.2: project_path based detection for MCP compatibility.
"""

from typing import Optional, List

# Runtime entitlement check (not import-time constant)
from ..utils.entitlements import is_developer, can_use_pro

# DB module reference (lazy loaded)
_db_module = None


def _get_db():
    """Lazy load db module at runtime."""
    global _db_module
    if _db_module is not None:
        return _db_module

    try:
        from ..db import knowledge as db
        _db_module = db
        return db
    except ImportError:
        return None


def can_use_kb(project_path: Optional[str] = None) -> bool:
    """Runtime check: can use Knowledge Base?

    True if:
    - Developer mode (env-based OR project_path is clouvel repo), OR
    - DB module available (Pro installed)

    Args:
        project_path: Project path for auto-detection (MCP-friendly)
    """
    if is_developer(project_path):
        return True
    return _get_db() is not None


PRO_MESSAGE = {
    "status": "pro_required",
    "error": "Knowledge Base requires Clouvel Pro license.",
    "purchase": "https://polar.sh/clouvel"
}


def _format_pro_message() -> str:
    """Formatted Pro message for display."""
    return """# ❌ Error Recording Decision

Knowledge Base requires Clouvel Pro license."""


async def record_decision(
    category: str,
    decision: str,
    reasoning: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    project_name: Optional[str] = None,
    project_path: Optional[str] = None,
    locked: bool = False
) -> dict:
    """
    Record a decision to the knowledge base.

    Args:
        category: Decision category (architecture, pricing, security, feature, etc.)
        decision: The actual decision made
        reasoning: Why this decision was made
        alternatives: Other options that were considered
        project_name: Project name (optional, for grouping)
        project_path: Project path (optional, for auto-detection)
        locked: If True, decision is locked and should not be changed without explicit unlock

    Returns:
        dict with decision_id and status
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = db.get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        # Prefix category with "locked:" if locked=True
        stored_category = f"locked:{category}" if locked else category

        decision_id = db.record_decision(
            category=stored_category,
            decision=decision,
            reasoning=reasoning,
            alternatives=alternatives,
            project_id=project_id
        )

        return {
            "status": "recorded",
            "decision_id": decision_id,
            "category": category,
            "locked": locked,
            "project_id": project_id
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def record_location(
    name: str,
    repo: str,
    path: str,
    description: Optional[str] = None,
    project_name: Optional[str] = None,
    project_path: Optional[str] = None
) -> dict:
    """
    Record a code location to the knowledge base.

    Args:
        name: Descriptive name (e.g., "License validation endpoint")
        repo: Repository name (e.g., "clouvel-workers")
        path: File path within repo (e.g., "src/index.js:42")
        description: What this code does
        project_name: Project name (optional)
        project_path: Project path (optional)

    Returns:
        dict with location_id and status
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = db.get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        location_id = db.record_location(
            name=name,
            repo=repo,
            path=path,
            description=description,
            project_id=project_id
        )

        return {
            "status": "recorded",
            "location_id": location_id,
            "name": name,
            "repo": repo,
            "path": path,
            "project_id": project_id
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def search_knowledge(
    query: str,
    project_name: Optional[str] = None,
    project_path: Optional[str] = None,
    limit: int = 20
) -> dict:
    """
    Search the knowledge base.

    Args:
        query: Search query (FTS5 syntax supported)
        project_name: Filter by project (optional)
        project_path: Project path for auto-detection (MCP-friendly)
        limit: Max results (default 20)

    Returns:
        dict with search results
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        project_id = None
        if project_name:
            project_id = db.get_or_create_project(name=project_name)

        results = db.search_knowledge(
            query=query,
            project_id=project_id,
            limit=limit
        )

        return {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def get_context(
    project_name: Optional[str] = None,
    project_path: Optional[str] = None,
    include_decisions: bool = True,
    include_locations: bool = True,
    limit: int = 10
) -> dict:
    """
    Get recent context for a project.

    Args:
        project_name: Project name
        project_path: Project path
        include_decisions: Include recent decisions
        include_locations: Include code locations
        limit: Max items per category

    Returns:
        dict with recent decisions and locations
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = db.get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        result = {
            "status": "success",
            "project_id": project_id
        }

        if include_decisions:
            result["decisions"] = db.get_recent_decisions(
                project_id=project_id,
                limit=limit
            )

        if include_locations:
            result["locations"] = db.get_recent_locations(
                project_id=project_id,
                limit=limit
            )

        return result

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def init_knowledge(project_path: Optional[str] = None) -> dict:
    """
    Initialize the knowledge base.

    Args:
        project_path: Project path for auto-detection (MCP-friendly)

    Returns:
        dict with database path and status
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db_path = db.init_knowledge_db()
        return {
            "status": "initialized",
            "db_path": str(db_path),
            "message": "Knowledge base ready. Use record_decision and record_location to store context."
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def rebuild_index(project_path: Optional[str] = None) -> dict:
    """
    Rebuild the search index from existing data.
    Use this if search results seem incomplete or out of sync.

    Args:
        project_path: Project path for auto-detection (MCP-friendly)

    Returns:
        dict with count of indexed items
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        count = db.rebuild_search_index()
        return {
            "status": "rebuilt",
            "indexed_count": count,
            "message": f"Search index rebuilt with {count} items."
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def unlock_decision(
    decision_id: int,
    reason: Optional[str] = None,
    project_path: Optional[str] = None
) -> dict:
    """
    Unlock a locked decision.

    Args:
        decision_id: The ID of the decision to unlock
        reason: Why this decision is being unlocked
        project_path: Project path for auto-detection (MCP-friendly)

    Returns:
        dict with status and unlocked decision info
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        # Import sqlite3 for direct update
        import sqlite3
        from pathlib import Path

        db_path = Path.home() / ".clouvel" / "knowledge.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get current decision
        cursor.execute(
            "SELECT category, decision, reasoning FROM decisions WHERE id = ?",
            (decision_id,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {
                "status": "error",
                "error": f"Decision {decision_id} not found"
            }

        category, decision, reasoning = row

        # Check if it's locked
        if not category.startswith("locked:"):
            conn.close()
            return {
                "status": "error",
                "error": f"Decision {decision_id} is not locked"
            }

        # Remove locked: prefix
        new_category = category[7:]  # Remove "locked:" prefix

        # Update reasoning with unlock note
        new_reasoning = reasoning or ""
        if reason:
            new_reasoning = f"{new_reasoning}\n\n[UNLOCKED: {reason}]" if new_reasoning else f"[UNLOCKED: {reason}]"

        cursor.execute(
            "UPDATE decisions SET category = ?, reasoning = ? WHERE id = ?",
            (new_category, new_reasoning, decision_id)
        )
        conn.commit()
        conn.close()

        return {
            "status": "unlocked",
            "decision_id": decision_id,
            "category": new_category,
            "decision": decision,
            "unlock_reason": reason
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def list_locked_decisions(
    project_name: Optional[str] = None,
    project_path: Optional[str] = None
) -> dict:
    """
    List all locked decisions.

    Args:
        project_name: Filter by project name (optional)
        project_path: Filter by project path (optional)

    Returns:
        dict with list of locked decisions
    """
    if not can_use_kb(project_path):
        return PRO_MESSAGE

    db = _get_db()
    if not db:
        return PRO_MESSAGE

    try:
        db.init_knowledge_db()

        import sqlite3
        from pathlib import Path

        db_path = Path.home() / ".clouvel" / "knowledge.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get project_id if filtering
        project_id = None
        if project_name or project_path:
            project_id = db.get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        # Query locked decisions
        if project_id:
            cursor.execute(
                """SELECT id, category, decision, reasoning, created_at
                   FROM decisions
                   WHERE category LIKE 'locked:%' AND project_id = ?
                   ORDER BY created_at DESC""",
                (project_id,)
            )
        else:
            cursor.execute(
                """SELECT id, category, decision, reasoning, created_at
                   FROM decisions
                   WHERE category LIKE 'locked:%'
                   ORDER BY created_at DESC"""
            )

        rows = cursor.fetchall()
        conn.close()

        decisions = []
        for row in rows:
            decisions.append({
                "id": row[0],
                "category": row[1][7:],  # Remove "locked:" prefix for display
                "decision": row[2],
                "reasoning": row[3],
                "created_at": row[4],
                "locked": True
            })

        return {
            "status": "success",
            "count": len(decisions),
            "decisions": decisions
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
