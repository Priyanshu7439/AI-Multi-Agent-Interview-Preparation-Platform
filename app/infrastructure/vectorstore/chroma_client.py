import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

from app.domain.interfaces.vector_store import IVectorStoreService
from app.core.exceptions import VectorStoreException
from app.core.logging import logger

from typing import List, Dict, Any

class LocalEmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB-compatible local embedding function.
    Uses SentenceTransformers instead of Gemini embeddings.
    """

    def __init__(self):
        try:
            self.model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

            logger.info(
                "SentenceTransformer initialized",
                model="all-MiniLM-L6-v2"
            )

        except Exception as e:
            logger.error(
                "Failed to initialize embedding model",
                error=str(e)
            )

            raise VectorStoreException(
                f"Embedding model initialization failed: {str(e)}"
            )

    def __call__(self, input: Documents) -> Embeddings:
        try:
            embeddings = self.model.encode(
                list(input),
                convert_to_numpy=True
            )

            return embeddings.tolist()

        except Exception as e:
            logger.error(
                "Embedding generation failed",
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed to generate embeddings: {str(e)}"
            )


class ChromaStoreService(IVectorStoreService):

    def __init__(self, db_path: str):
        try:
            self.client = chromadb.PersistentClient(
                path=db_path
            )

            self.embedding_function = LocalEmbeddingFunction()

            logger.info(
                "ChromaDB persistent client initialized",
                path=db_path
            )

        except Exception as e:
            logger.error(
                "ChromaDB initialization error",
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed to initialize ChromaDB: {str(e)}"
            )

    def _get_collection(self, collection_name: str):
        try:
            return self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

        except Exception as e:
            logger.error(
                "Error getting or creating collection",
                collection=collection_name,
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed to access collection {collection_name}: {str(e)}"
            )

    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:

        if not texts:
            return

        try:
            collection = self._get_collection(
                collection_name
            )

            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(
                "Documents successfully added",
                collection=collection_name,
                count=len(texts)
            )

        except Exception as e:
            logger.error(
                "Failed to add documents",
                collection=collection_name,
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed to add documents to collection {collection_name}: {str(e)}"
            )

    def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = 4
    ) -> List[str]:

        try:
            collection = self._get_collection(
                collection_name
            )

            results = collection.query(
                query_texts=[query],
                n_results=k
            )

            documents = results.get(
                "documents",
                []
            )

            if documents and len(documents) > 0:

                logger.info(
                    "Similarity search completed",
                    collection=collection_name,
                    matches=len(documents[0])
                )

                return documents[0]

            return []

        except Exception as e:

            logger.error(
                "Similarity search failed",
                collection=collection_name,
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed similarity search in collection {collection_name}: {str(e)}"
            )

    def _collection_exists(
        self,
        collection_name: str
    ) -> bool:

        try:
            existing = [
                c.name
                for c in self.client.list_collections()
            ]

            return collection_name in existing

        except Exception:

            try:
                self.client.get_collection(
                    collection_name
                )

                return True

            except Exception:
                return False

    def clear_collection(
        self,
        collection_name: str
    ) -> None:

        try:

            if not self._collection_exists(
                collection_name
            ):

                logger.warning(
                    "Collection does not exist, skipping deletion",
                    collection=collection_name
                )

                return

            self.client.delete_collection(
                collection_name
            )

            logger.info(
                "Collection deleted",
                collection=collection_name
            )

        except Exception as e:

            logger.error(
                "Failed to clear collection",
                collection=collection_name,
                error=str(e)
            )

            raise VectorStoreException(
                f"Failed to clear collection {collection_name}: {str(e)}"
            )

