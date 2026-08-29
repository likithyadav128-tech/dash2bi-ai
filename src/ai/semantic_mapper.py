"""
Semantic Mapper helper in AI package.
"""

from typing import Dict, Any, List, Optional
from src.ai.anthropic_provider import AnthropicProvider

def run_ai_semantic_mapping(dataset_schema: Dict[str, Any], visuals: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Attempts AI mapping via AnthropicProvider.
    Returns (is_ai_used, ai_mapping_result)
    """
    provider = AnthropicProvider()
    if provider.is_available():
        result = provider.map_fields_and_visuals(dataset_schema, visuals)
        if result:
            return True, result
    return False, None
