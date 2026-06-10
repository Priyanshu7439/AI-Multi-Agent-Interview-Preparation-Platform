import pytest
import numpy as np
from unittest.mock import patch
from app.infrastructure.vectorstore.chroma_client import GeminiEmbeddingFunction
from app.core.exceptions import VectorStoreException


@pytest.fixture
def embedding_fn():
    """Create a GeminiEmbeddingFunction with a dummy API key (genai.configure is mocked)."""
    with patch("google.generativeai.configure"):
        return GeminiEmbeddingFunction(api_key="fake-key")


class TestGeminiEmbeddingFunction:
    """Tests for the GeminiEmbeddingFunction ChromaDB adapter."""

    def test_single_document_embedding(self, embedding_fn):
        """embed_content returns {"embedding": [[floats]]} for a one-item list."""
        mock_response = {"embedding": [[0.1, 0.2, 0.3]]}

        with patch("google.generativeai.embed_content", return_value=mock_response) as mock_embed:
            result = embedding_fn(["Hello world"])

        mock_embed.assert_called_once_with(
            model="models/text-embedding-004",
            content=["Hello world"],
            task_type="retrieval_document"
        )
        # ChromaDB's base EmbeddingFunction may convert inner lists to numpy arrays
        assert len(result) == 1
        np.testing.assert_array_almost_equal(result[0], [0.1, 0.2, 0.3])

    def test_batch_document_embedding(self, embedding_fn):
        """embed_content handles multiple documents and returns one embedding per doc."""
        docs = ["Document one", "Document two", "Document three"]
        mock_response = {
            "embedding": [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
                [0.7, 0.8, 0.9],
            ]
        }

        with patch("google.generativeai.embed_content", return_value=mock_response):
            result = embedding_fn(docs)

        assert len(result) == 3
        np.testing.assert_array_almost_equal(result[0], [0.1, 0.2, 0.3])
        np.testing.assert_array_almost_equal(result[2], [0.7, 0.8, 0.9])

    def test_uses_content_not_contents(self, embedding_fn):
        """Verify the SDK is called with `content=` (not `contents=`)."""
        mock_response = {"embedding": [[1.0, 2.0]]}

        with patch("google.generativeai.embed_content", return_value=mock_response) as mock_embed:
            embedding_fn(["test"])

        # Inspect the actual keyword arguments used
        call_kwargs = mock_embed.call_args.kwargs
        assert "content" in call_kwargs, "Must use 'content' keyword"
        assert "contents" not in call_kwargs, "Must NOT use 'contents' keyword"

    def test_uses_embedding_not_embeddings_key(self, embedding_fn):
        """Verify we read response['embedding'] (not response['embeddings'])."""
        mock_response = {"embedding": [[9.0]], "embeddings": "should_not_be_used"}

        with patch("google.generativeai.embed_content", return_value=mock_response):
            result = embedding_fn(["test"])

        # Should return the value from "embedding" key, not "embeddings"
        assert len(result) == 1
        np.testing.assert_array_almost_equal(result[0], [9.0])

    def test_returns_correct_shape(self, embedding_fn):
        """ChromaDB expects Embeddings = List[Vector] where each Vector is array-like."""
        mock_response = {"embedding": [[0.5, 0.6], [0.7, 0.8]]}

        with patch("google.generativeai.embed_content", return_value=mock_response):
            result = embedding_fn(["doc1", "doc2"])

        # Outer container should be a list
        assert isinstance(result, list)
        # Each item should be array-like with numeric values
        assert len(result) == 2
        for emb in result:
            assert len(emb) == 2
            for val in emb:
                assert isinstance(float(val), float)

    def test_raises_vector_store_exception_on_sdk_error(self, embedding_fn):
        """SDK errors should be wrapped in VectorStoreException."""
        with patch("google.generativeai.embed_content", side_effect=Exception("API quota exceeded")):
            with pytest.raises(VectorStoreException, match="Failed to generate embeddings"):
                embedding_fn(["test"])
