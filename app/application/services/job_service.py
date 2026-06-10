from typing import Optional
from app.domain.interfaces import IParserService, ISessionRepository, IVectorStoreService
from app.application.services.resume_service import chunk_text
from app.core.logging import logger

class JobService:
    def __init__(
        self, 
        parser_service: IParserService, 
        repository: ISessionRepository,
        vector_store: IVectorStoreService
    ):
        self.parser_service = parser_service
        self.repository = repository
        self.vector_store = vector_store

    def process_job_description(
        self, 
        session_id: str, 
        jd_text: Optional[str] = None, 
        file_bytes: Optional[bytes] = None
    ) -> str:
        """Process job description input (as text or PDF), persist, and embed into vector store."""
        logger.info("JobService: Processing job description", session_id=session_id)

        if file_bytes:
            text = self.parser_service.parse_pdf(file_bytes)
        elif jd_text:
            text = jd_text
        else:
            raise ValueError("Either jd_text or file_bytes must be provided to process job description")

        # 1. Save raw text to SQL database
        self.repository.save_raw_texts(session_id, jd_text=text)

        # 2. Chunk and embed into ChromaDB
        chunks = chunk_text(text)
        metadatas = [{"source": "jd", "session_id": session_id} for _ in chunks]
        ids = [f"{session_id}_jd_{i}" for i in range(len(chunks))]

        self.vector_store.clear_collection(f"jd_{session_id}")
        self.vector_store.add_documents(
            collection_name=f"jd_{session_id}",
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )

        logger.info("JobService: Job description processing completed", chunks_created=len(chunks))
        return text
