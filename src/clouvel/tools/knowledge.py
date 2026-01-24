"""Knowledge Base tools for Clouvel.

Tools for recording and retrieving decisions, code locations, and context.
"""

from typing import Optional, List
from ..db.knowledge import (
    init_knowledge_db,
    get_or_create_project,
    record_decision as db_record_decision,
    record_location as db_record_location,
    record_meeting as db_record_meeting,
    record_event as db_record_event,
    search_knowledge as db_search_knowledge,
    get_recent_decisions,
    get_recent_locations,
    get_project_summary,
    rebuild_search_index as db_rebuild_search_index,
)


async def record_decision(
    category: str,
    decision: str,
    reasoning: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    project_name: Optional[str] = None,
    project_path: Optional[str] = None
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

    Returns:
        dict with decision_id and status
    """
    try:
        init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        decision_id = db_record_decision(
            category=category,
            decision=decision,
            reasoning=reasoning,
            alternatives=alternatives,
            project_id=project_id
        )

        return {
            "status": "recorded",
            "decision_id": decision_id,
            "category": category,
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
    try:
        init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        location_id = db_record_location(
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
    limit: int = 20
) -> dict:
    """
    Search the knowledge base.

    Args:
        query: Search query (FTS5 syntax supported)
        project_name: Filter by project (optional)
        limit: Max results (default 20)

    Returns:
        dict with search results
    """
    try:
        init_knowledge_db()

        project_id = None
        if project_name:
            project_id = get_or_create_project(name=project_name)

        results = db_search_knowledge(
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
    try:
        init_knowledge_db()

        project_id = None
        if project_name or project_path:
            project_id = get_or_create_project(
                name=project_name or "default",
                path=project_path
            )

        result = {
            "status": "success",
            "project_id": project_id
        }

        if include_decisions:
            result["decisions"] = get_recent_decisions(
                project_id=project_id,
                limit=limit
            )

        if include_locations:
            result["locations"] = get_recent_locations(
                project_id=project_id,
                limit=limit
            )

        return result

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def init_knowledge() -> dict:
    """
    Initialize the knowledge base.

    Returns:
        dict with database path and status
    """
    try:
        db_path = init_knowledge_db()
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


async def rebuild_index() -> dict:
    """
    Rebuild the search index from existing data.
    Use this if search results seem incomplete or out of sync.

    Returns:
        dict with count of indexed items
    """
    try:
        count = db_rebuild_search_index()
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
