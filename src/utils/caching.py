"""
Streamlit caching wrappers for expensive operations in Dash2BI AI.
"""

import streamlit as st

def cache_data(func):
    """Decorator to cache data parsing results in Streamlit."""
    return st.cache_data(show_spinner=False)(func)

def cache_resource(func):
    """Decorator to cache heavyweight resources like models in Streamlit."""
    return st.cache_resource(show_spinner=False)(func)
