"""
AI Provider Interface for Dash2BI AI.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIProvider(ABC):
    """Abstract base class for AI Provider implementations."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the AI provider is configured and available."""
        pass

    @abstractmethod
    def map_fields_and_visuals(self, dataset_schema: Dict[str, Any], visuals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Maps dataset schema to HTML visual components using LLM reasoning."""
        pass
