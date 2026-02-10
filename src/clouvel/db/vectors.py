"""Vector search for Clouvel Error System v2.0.

Optional dependency: chromadb, sentence-transformers
Falls back to text similarity if not available.
"""

import hashlib
from pathlib import Path
from typing import Optional

from .schema import get_connection, get_db_path

# Optional imports
try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

# Default embedding model
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Singleton instances
_embedding_model = None
_chroma_client = None


def is_vector_search_available() -> dict:
    """Check if vector search is available."""
    return {
        "available": CHROMADB_AVAILABLE and EMBEDDING_AVAILABLE,
        "chromadb": CHROMADB_AVAILABLE,
        "embedding": EMBEDDING_AVAILABLE,
        "model": DEFAULT_MODEL if EMBEDDING_AVAILABLE else None,
    }


def get_embedding_model():
    """Get or create embedding model (lazy loading)."""
    global _embedding_model

    if not EMBEDDING_AVAILABLE:
        return None

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(DEFAULT_MODEL)

    return _embedding_model


def get_chroma_client(project_path: Optional[str] = None):
    """Get or create ChromaDB client."""
    global _chroma_client

    if not CHROMADB_AVAILABLE:
        return None

    if _chroma_client is None:
        if project_path:
            persist_dir = Path(project_path) / ".clouvel" / "chroma"
        else:
            persist_dir = Path.cwd() / ".clouvel" / "chroma"

        persist_dir.mkdir(parents=True, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

    return _chroma_client


def get_error_collection(project_path: Optional[str] = None):
    """Get or create error collection in ChromaDB."""
    client = get_chroma_client(project_path)
    if client is None:
        return None

    return client.get_or_create_collection(
        name="clouvel_errors",
        metadata={"description": "Clouvel error embeddings"},
    )


def embed_text(text: str) -> Optional[list[float]]:
    """Generate embedding for text."""
    model = get_embedding_model()
    if model is None:
        return None

    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def add_error_embedding(
    error_id: str,
    error_text: str,
    metadata: Optional[dict] = None,
    project_path: Optional[str] = None,
) -> dict:
    """
    Add error embedding to ChromaDB.

    Args:
        error_id: Unique error ID
        error_text: Text to embed (message + stack trace)
        metadata: Optional metadata to store
        project_path: Project path for DB location
    """
    collection = get_error_collection(project_path)
    if collection is None:
        return {
            "status": "unavailable",
            "message": "ChromaDB가 설치되지 않았습니다. pip install chromadb",
        }

    embedding = embed_text(error_text)
    if embedding is None:
        return {
            "status": "unavailable",
            "message": "sentence-transformers가 설치되지 않았습니다. pip install sentence-transformers",
        }

    # Add to ChromaDB
    collection.add(
        ids=[error_id],
        embeddings=[embedding],
        documents=[error_text],
        metadatas=[metadata or {}],
    )

    # Update SQLite tracking table
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO error_embeddings (error_id, embedding_model)
            VALUES (?, ?)
            """,
            (error_id, DEFAULT_MODEL),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "embedded", "id": error_id}


def search_similar_errors(
    query_text: str,
    *,
    error_type: Optional[str] = None,
    n_results: int = 5,
    threshold: float = 0.8,
    project_path: Optional[str] = None,
) -> dict:
    """
    Search for similar errors using vector similarity.

    Args:
        query_text: Error text to search for
        error_type: Optional filter by error type
        n_results: Maximum results to return
        threshold: Minimum similarity score (0-1)
        project_path: Project path

    Returns:
        Dict with similar errors and their scores
    """
    collection = get_error_collection(project_path)

    # Fallback to text search if vector search unavailable
    if collection is None:
        return _fallback_text_search(
            query_text,
            error_type=error_type,
            n_results=n_results,
            project_path=project_path,
        )

    # Generate query embedding
    query_embedding = embed_text(query_text)
    if query_embedding is None:
        return _fallback_text_search(
            query_text,
            error_type=error_type,
            n_results=n_results,
            project_path=project_path,
        )

    # Build where filter
    where_filter = None
    if error_type:
        where_filter = {"error_type": error_type}

    # Query ChromaDB
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "fallback": _fallback_text_search(
                query_text,
                error_type=error_type,
                n_results=n_results,
                project_path=project_path,
            ),
        }

    # Process results
    similar_errors = []
    for i, error_id in enumerate(results["ids"][0]):
        # ChromaDB returns L2 distance, convert to similarity
        distance = results["distances"][0][i]
        similarity = 1 / (1 + distance)  # Convert distance to similarity

        if similarity >= threshold:
            similar_errors.append(
                {
                    "id": error_id,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": round(similarity, 3),
                }
            )

    # Categorize by similarity
    highly_similar = [e for e in similar_errors if e["similarity"] >= 0.9]
    possibly_related = [e for e in similar_errors if 0.8 <= e["similarity"] < 0.9]

    return {
        "status": "success",
        "method": "vector",
        "total": len(similar_errors),
        "highly_similar": highly_similar,
        "possibly_related": possibly_related,
    }


def _fallback_text_search(
    query_text: str,
    *,
    error_type: Optional[str] = None,
    n_results: int = 5,
    project_path: Optional[str] = None,
) -> dict:
    """Fallback to simple text similarity when vector search unavailable."""
    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        query = """
            SELECT id, error_message, error_type, solution
            FROM errors
            WHERE 1=1
        """
        params = []

        if error_type:
            query += " AND error_type = ?"
            params.append(error_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(n_results * 3)  # Get more to filter

        rows = conn.execute(query, params).fetchall()

        # Simple text matching
        query_lower = query_text.lower()
        query_words = set(query_lower.split())

        results = []
        for row in rows:
            msg_lower = row["error_message"].lower()
            msg_words = set(msg_lower.split())

            # Jaccard similarity
            intersection = len(query_words & msg_words)
            union = len(query_words | msg_words)
            similarity = intersection / union if union > 0 else 0

            if similarity > 0.1:  # Minimum threshold
                results.append(
                    {
                        "id": row["id"],
                        "error_message": row["error_message"],
                        "error_type": row["error_type"],
                        "solution": row["solution"],
                        "similarity": round(similarity, 3),
                    }
                )

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:n_results]

        return {
            "status": "success",
            "method": "text_fallback",
            "note": "벡터 검색 불가 - 텍스트 유사도 사용",
            "total": len(results),
            "results": results,
        }
    finally:
        conn.close()


def embed_all_errors(project_path: Optional[str] = None) -> dict:
    """Embed all errors that haven't been embedded yet."""
    if not CHROMADB_AVAILABLE or not EMBEDDING_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "chromadb 또는 sentence-transformers가 필요합니다",
        }

    db_path = get_db_path(project_path)
    conn = get_connection(db_path)

    try:
        # Get errors without embeddings
        rows = conn.execute(
            """
            SELECT e.id, e.error_message, e.stack_trace, e.error_type
            FROM errors e
            LEFT JOIN error_embeddings ee ON e.id = ee.error_id
            WHERE ee.error_id IS NULL
            """
        ).fetchall()

        embedded = 0
        for row in rows:
            text = row["error_message"]
            if row["stack_trace"]:
                text += "\n" + row["stack_trace"]

            result = add_error_embedding(
                row["id"],
                text,
                metadata={"error_type": row["error_type"]},
                project_path=project_path,
            )
            if result["status"] == "embedded":
                embedded += 1

        return {
            "status": "success",
            "total": len(rows),
            "embedded": embedded,
        }
    finally:
        conn.close()
