"""
Anthropic Claude integration provider for Dash2BI AI.
"""

import os
import json
import streamlit as st
from typing import Dict, Any, List, Optional
from src.ai.provider import AIProvider
from src.ai.prompt_builder import build_mapping_prompt
from src.utils.logging import log_event

class AnthropicProvider(AIProvider):
    """Integrates with Anthropic Claude API using ANTHROPIC_API_KEY."""

    def __init__(self):
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        # 1. Check Streamlit secrets
        try:
            if "ANTHROPIC_API_KEY" in st.secrets:
                return st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            pass
        # 2. Check environment variables
        return os.getenv("ANTHROPIC_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def map_fields_and_visuals(self, dataset_schema: Dict[str, Any], visuals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            log_event("ai", "Anthropic API key not configured; skipping AI mapping.", "INFO")
            return None

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            prompt = build_mapping_prompt(dataset_schema, visuals)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            text_resp = response.content[0].text
            # Extract JSON block
            json_match = re.search(r'\{.*\}', text_resp, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                log_event("ai", "AI mapping successfully returned semantic suggestions.")
                return parsed
        except Exception as e:
            log_event("ai", f"AI mapping call failed: {str(e)}", "WARNING")
            return None
        return None
