from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IVectorStoreService(ABC):
    @abstractmethod
    def add_documents(
        self, 
        collection_name: str, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str]
    ) -> None:
        """Add text documents to the vector store.

        Args:
            collection_name: Name of the target collection.
            texts: List of text chunks.
            metadatas: List of metadata dictionaries.
            ids: List of unique document identifiers.
        """
        pass

    @abstractmethod
    def similarity_search(
        self, 
        collection_name: str, 
        query: str, 
        k: int = 4
    ) -> List[str]:
        """Perform a similarity search on the vector store.

        Args:
            collection_name: Name of the collection to search.
            query: The query text.
            k: Number of top documents to retrieve.

        Returns:
            List of matching document texts.
        """
        pass

    @abstractmethod
    def clear_collection(self, collection_name: str) -> None:
        """Clear all entries in a collection.

        Args:
            collection_name: Collection to clear.
        """
        pass
