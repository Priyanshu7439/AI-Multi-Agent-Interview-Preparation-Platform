import io
from app.domain.interfaces.parser_service import IParserService
from app.core.exceptions import PDFParsingException
from app.core.logging import logger

class PDFParserService(IParserService):
    def parse_pdf(self, file_bytes: bytes) -> str:
        """Parse PDF content trying pdfplumber first and falling back to PyMuPDF.

        Args:
            file_bytes: PDF file as raw bytes.

        Returns:
            Extracted text.
        """
        text = ""
        # 1. Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            text = text.strip()
            if text:
                logger.info("PDF parsed successfully using pdfplumber")
                return text
        except Exception as e:
            logger.warning("Failed parsing with pdfplumber, trying PyMuPDF fallback", error=str(e))

        # 2. Try PyMuPDF Fallback
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text() + "\n"
            text = text.strip()
            if text:
                logger.info("PDF parsed successfully using PyMuPDF")
                return text
        except Exception as e:
            logger.error("Failed parsing with PyMuPDF", error=str(e))
            raise PDFParsingException(f"Failed to extract text from PDF: {str(e)}")

        raise PDFParsingException("Parsed PDF is empty or contains no extractable text.")
