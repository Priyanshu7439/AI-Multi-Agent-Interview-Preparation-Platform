from app.domain.interfaces import IParserService, ISessionRepository, IVectorStoreService
from app.core.logging import logger
from typing import List

def chunk_text(text: str, chunk_size: int = 150, chunk_overlap: int = 30) -> List[str]:
    """Helper method to split text into chunks with overlap for embedding indexing."""
    words = text.split()
    chunks = []
    if not words:
        return chunks
    step = chunk_size - chunk_overlap
    if step <= 0:
        step = chunk_size
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

class ResumeService:
    def __init__(
        self, 
        parser_service: IParserService, 
        repository: ISessionRepository,
        vector_store: IVectorStoreService
    ):
        self.parser_service = parser_service
        self.repository = repository
        self.vector_store = vector_store

    def process_resume(self, session_id: str, file_bytes: bytes) -> str:
        """Parse, persist, chunk, and embed candidate resume into database and vector store."""
        logger.info("ResumeService: Processing resume file", session_id=session_id)
        
        # 1. Parse text from PDF
        text = self.parser_service.parse_pdf(file_bytes)

        # 2. Save raw text to SQL repository
        self.repository.save_raw_texts(session_id, resume_text=text)

        # 3. Chunk and embed into ChromaDB
        chunks = chunk_text(text)
        metadatas = [{"source": "resume", "session_id": session_id} for _ in chunks]
        ids = [f"{session_id}_resume_{i}" for i in range(len(chunks))]
        
        # Clear collection if it already has documents (e.g. re-upload)
        self.vector_store.clear_collection(f"resume_{session_id}")
        self.vector_store.add_documents(
            collection_name=f"resume_{session_id}",
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("ResumeService: Resume processing completed", chunks_created=len(chunks))
        return text
