from abc import ABC, abstractmethod

class IParserService(ABC):
    @abstractmethod
    def parse_pdf(self, file_bytes: bytes) -> str:
        """Parse PDF content and return extracted text.

        Args:
            file_bytes: Bytes of the PDF file.

        Returns:
            Extracted text from the PDF.
        """
        pass
