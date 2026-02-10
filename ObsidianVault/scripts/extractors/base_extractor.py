# PURPOSE: Abstract base class for text extractors.
# DEPENDENCIES: None (abstract interface).
# MODIFICATION NOTES: Phase 1 - Foundation for pluggable extractors.

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

class TextExtractor(ABC):
    """Abstract base class for PDF text extractors."""
    
    @abstractmethod
    def extract(self, pdf_path: Path, **kwargs) -> Tuple[str, Optional[Path], dict]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Extractor-specific options (e.g., vault_root)
            
        Returns:
            Tuple of (extracted_text, source_path, metadata)
            - extracted_text: Extracted text content
            - source_path: Path to source file if using cache, None otherwise
            - metadata: Dict with extraction metadata (confidence, method, etc.)
        """
        pass
    
    @abstractmethod
    def can_extract(self, pdf_path: Path) -> bool:
        """
        Check if this extractor can handle the given PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if extractor can handle this PDF, False otherwise
        """
        pass
