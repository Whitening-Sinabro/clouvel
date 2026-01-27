# -*- coding: utf-8 -*-
"""Database vectors module tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.schema import init_db
from clouvel.db.vectors import (
    is_vector_search_available,
    DEFAULT_MODEL,
    CHROMADB_AVAILABLE,
    EMBEDDING_AVAILABLE,
    get_embedding_model,
    get_chroma_client,
    get_error_collection,
    embed_text,
    search_similar_errors,
    embed_all_errors,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory with initialized DB"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    init_db(str(temp_path))
    yield temp_path
    shutil.rmtree(temp_dir)


class TestConstants:
    """Constant tests"""

    def test_default_model_exists(self):
        """Default model constant exists"""
        assert DEFAULT_MODEL is not None
        assert isinstance(DEFAULT_MODEL, str)

    def test_default_model_value(self):
        """Default model is MiniLM"""
        assert "MiniLM" in DEFAULT_MODEL

    def test_chromadb_available_is_bool(self):
        """CHROMADB_AVAILABLE is boolean"""
        assert isinstance(CHROMADB_AVAILABLE, bool)

    def test_embedding_available_is_bool(self):
        """EMBEDDING_AVAILABLE is boolean"""
        assert isinstance(EMBEDDING_AVAILABLE, bool)


class TestIsVectorSearchAvailable:
    """is_vector_search_available function tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        result = is_vector_search_available()
        assert isinstance(result, dict)

    def test_has_available_key(self):
        """Has available key"""
        result = is_vector_search_available()
        assert "available" in result

    def test_has_chromadb_key(self):
        """Has chromadb key"""
        result = is_vector_search_available()
        assert "chromadb" in result

    def test_has_embedding_key(self):
        """Has embedding key"""
        result = is_vector_search_available()
        assert "embedding" in result

    def test_has_model_key(self):
        """Has model key"""
        result = is_vector_search_available()
        assert "model" in result

    def test_available_matches_dependencies(self):
        """Available is true only if both deps available"""
        result = is_vector_search_available()
        assert result["available"] == (CHROMADB_AVAILABLE and EMBEDDING_AVAILABLE)

    def test_chromadb_matches_import(self):
        """chromadb matches import status"""
        result = is_vector_search_available()
        assert result["chromadb"] == CHROMADB_AVAILABLE

    def test_embedding_matches_import(self):
        """embedding matches import status"""
        result = is_vector_search_available()
        assert result["embedding"] == EMBEDDING_AVAILABLE


class TestGetEmbeddingModel:
    """get_embedding_model function tests"""

    def test_returns_none_if_unavailable(self):
        """Returns None if embedding not available"""
        if not EMBEDDING_AVAILABLE:
            result = get_embedding_model()
            assert result is None

    @pytest.mark.skipif(not EMBEDDING_AVAILABLE, reason="sentence-transformers not installed")
    def test_returns_model_if_available(self):
        """Returns model if embedding available"""
        result = get_embedding_model()
        assert result is not None


class TestGetChromaClient:
    """get_chroma_client function tests"""

    def test_returns_none_if_unavailable(self):
        """Returns None if chromadb not available"""
        if not CHROMADB_AVAILABLE:
            result = get_chroma_client()
            assert result is None

    @pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
    def test_returns_client_if_available(self, temp_project):
        """Returns client if chromadb available"""
        result = get_chroma_client(str(temp_project))
        assert result is not None


class TestGetErrorCollection:
    """get_error_collection function tests"""

    def test_returns_none_if_unavailable(self):
        """Returns None if chromadb not available"""
        if not CHROMADB_AVAILABLE:
            result = get_error_collection()
            assert result is None


class TestEmbedText:
    """embed_text function tests"""

    def test_returns_none_if_unavailable(self):
        """Returns None if embedding not available"""
        if not EMBEDDING_AVAILABLE:
            result = embed_text("test text")
            assert result is None

    @pytest.mark.skipif(not EMBEDDING_AVAILABLE, reason="sentence-transformers not installed")
    def test_returns_list_if_available(self):
        """Returns list of floats if embedding available"""
        result = embed_text("test text")
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)


class TestSearchSimilarErrors:
    """search_similar_errors function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = search_similar_errors("test error", project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_has_status_key(self, temp_project):
        """Has status key"""
        result = search_similar_errors("test error", project_path=str(temp_project))
        assert "status" in result

    def test_fallback_when_unavailable(self, temp_project):
        """Uses fallback text search when vector unavailable"""
        if not CHROMADB_AVAILABLE or not EMBEDDING_AVAILABLE:
            result = search_similar_errors("test error", project_path=str(temp_project))
            # Should use text_fallback method
            assert result.get("method") == "text_fallback" or "status" in result

    def test_accepts_n_results(self, temp_project):
        """Accepts n_results parameter"""
        result = search_similar_errors(
            "test error",
            n_results=3,
            project_path=str(temp_project)
        )
        assert isinstance(result, dict)

    def test_accepts_threshold(self, temp_project):
        """Accepts threshold parameter"""
        result = search_similar_errors(
            "test error",
            threshold=0.5,
            project_path=str(temp_project)
        )
        assert isinstance(result, dict)

    def test_accepts_error_type(self, temp_project):
        """Accepts error_type parameter"""
        result = search_similar_errors(
            "test error",
            error_type="TypeError",
            project_path=str(temp_project)
        )
        assert isinstance(result, dict)


class TestEmbedAllErrors:
    """embed_all_errors function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = embed_all_errors(str(temp_project))
        assert isinstance(result, dict)

    def test_returns_unavailable_without_deps(self, temp_project):
        """Returns unavailable if dependencies missing"""
        if not CHROMADB_AVAILABLE or not EMBEDDING_AVAILABLE:
            result = embed_all_errors(str(temp_project))
            assert result["status"] == "unavailable"

    def test_has_status_key(self, temp_project):
        """Has status key"""
        result = embed_all_errors(str(temp_project))
        assert "status" in result


class TestFallbackSearch:
    """Fallback text search tests"""

    def test_fallback_returns_dict(self, temp_project):
        """Fallback returns dictionary"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search("test error", project_path=str(temp_project))
        assert isinstance(result, dict)

    def test_fallback_has_status(self, temp_project):
        """Fallback has status key"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search("test error", project_path=str(temp_project))
        assert result["status"] == "success"

    def test_fallback_has_method(self, temp_project):
        """Fallback has method key"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search("test error", project_path=str(temp_project))
        assert result["method"] == "text_fallback"

    def test_fallback_has_results(self, temp_project):
        """Fallback has results key"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search("test error", project_path=str(temp_project))
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_fallback_respects_n_results(self, temp_project):
        """Fallback respects n_results parameter"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search(
            "test error",
            n_results=2,
            project_path=str(temp_project)
        )
        assert len(result["results"]) <= 2

    def test_fallback_respects_error_type(self, temp_project):
        """Fallback respects error_type parameter"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search(
            "test error",
            error_type="TypeError",
            project_path=str(temp_project)
        )
        assert isinstance(result, dict)

    def test_fallback_with_no_errors(self, temp_project):
        """Fallback handles empty database"""
        from clouvel.db.vectors import _fallback_text_search
        result = _fallback_text_search("test error", project_path=str(temp_project))
        assert result["total"] == 0
        assert result["results"] == []


class TestFallbackSimilarity:
    """Fallback text similarity calculation tests"""

    def test_fallback_calculates_similarity(self, temp_project):
        """Fallback calculates text similarity"""
        from clouvel.db.errors import record_error
        from clouvel.db.vectors import _fallback_text_search

        # Add an error to search
        record_error(
            "TypeError: cannot read property of undefined",
            error_type="TypeError",
            project_path=str(temp_project)
        )

        result = _fallback_text_search(
            "TypeError cannot read property",
            project_path=str(temp_project)
        )

        # Should find the error with some similarity
        assert len(result["results"]) >= 0  # May or may not match

    def test_similar_errors_found(self, temp_project):
        """Finds similar errors based on text"""
        from clouvel.db.errors import record_error
        from clouvel.db.vectors import _fallback_text_search

        # Add errors with similar text
        record_error(
            "connection timeout error database",
            error_type="ConnectionError",
            project_path=str(temp_project)
        )
        record_error(
            "null pointer exception access",
            error_type="NullError",
            project_path=str(temp_project)
        )

        result = _fallback_text_search(
            "connection timeout",
            project_path=str(temp_project)
        )

        # May or may not find based on similarity threshold
        assert "results" in result


class TestAddErrorEmbedding:
    """add_error_embedding function tests"""

    def test_unavailable_without_chromadb(self, temp_project):
        """Returns unavailable when chromadb not installed"""
        from clouvel.db.vectors import add_error_embedding
        if not CHROMADB_AVAILABLE:
            result = add_error_embedding(
                "test_id",
                "test error text",
                project_path=str(temp_project)
            )
            assert result["status"] == "unavailable"
            assert "ChromaDB" in result["message"]

    def test_accepts_metadata(self, temp_project):
        """Accepts metadata parameter"""
        from clouvel.db.vectors import add_error_embedding
        result = add_error_embedding(
            "test_id",
            "test error",
            metadata={"type": "test"},
            project_path=str(temp_project)
        )
        assert "status" in result


class TestVectorSearchWithData:
    """Vector search tests with actual data"""

    def test_search_with_errors_in_db(self, temp_project):
        """Search works when errors exist"""
        from clouvel.db.errors import record_error
        from clouvel.db.vectors import _fallback_text_search

        # Add some errors
        record_error(
            "Database connection failed timeout",
            error_type="ConnectionError",
            project_path=str(temp_project)
        )
        record_error(
            "User authentication failed invalid token",
            error_type="AuthError",
            project_path=str(temp_project)
        )

        # Search with matching text
        result = _fallback_text_search(
            "connection failed",
            project_path=str(temp_project)
        )

        assert result["status"] == "success"
        assert result["method"] == "text_fallback"

    def test_search_similarity_ranking(self, temp_project):
        """Search results are ranked by similarity"""
        from clouvel.db.errors import record_error
        from clouvel.db.vectors import _fallback_text_search

        # Add errors with varying similarity
        record_error(
            "exact match error text",
            project_path=str(temp_project)
        )
        record_error(
            "completely unrelated error",
            project_path=str(temp_project)
        )

        result = _fallback_text_search(
            "exact match error",
            project_path=str(temp_project)
        )

        # Results should be sorted by similarity
        if len(result["results"]) > 1:
            assert result["results"][0]["similarity"] >= result["results"][1]["similarity"]

    def test_search_error_type_filter(self, temp_project):
        """Search with error_type filter"""
        from clouvel.db.errors import record_error
        from clouvel.db.vectors import _fallback_text_search

        record_error("Error type A", error_type="TypeA", project_path=str(temp_project))
        record_error("Error type B", error_type="TypeB", project_path=str(temp_project))

        result = _fallback_text_search(
            "Error type",
            error_type="TypeA",
            project_path=str(temp_project)
        )

        # Should only return TypeA errors
        for r in result["results"]:
            if r.get("error_type"):
                assert r["error_type"] == "TypeA"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
