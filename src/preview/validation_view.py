"""
Validation View UI for Dash2BI AI.
"""

import streamlit as st
from typing import Dict, Any

def render_validation_summary(val_summary: Dict[str, Any]):
    """Renders pre-flight validation status badge list."""
    st.markdown("### ⚡ Pre-Flight Validation Checks")
    
    is_ready = val_summary.get("is_ready", False)
    passed = val_summary.get("passed_count", 0)
    total = val_summary.get("total_checks", 10)

    if is_ready:
        st.success(f"✓ Project Validation Passed ({passed}/{total} Integrity Checks Succeeded)")
    else:
        st.warning(f"⚠ Project Contains Warnings ({passed}/{total} Integrity Checks Succeeded)")

    for check in val_summary.get("checks", []):
        icon = "✅" if check["passed"] else "❌"
        st.markdown(f"{icon} **{check['name']}**: {check['detail']}")
