"""
ui_utils.py - Shared UI utilities for AI Study Assistant.
Contains reusable rendering helpers to avoid circular imports.
"""

import streamlit as st


def render_ai_loading(message: str = "AI is analyzing your content..."):
    """Display a fancy AI loading animation with pulsing dots."""
    st.markdown(f"""
    <div class="ai-loading-container">
        <div style="display:flex;gap:6px;">
            <span class="ai-dot"></span>
            <span class="ai-dot"></span>
            <span class="ai-dot"></span>
        </div>
        <span style="color:#6b21a8;font-weight:600;font-size:0.95rem;">{message}</span>
    </div>
    """, unsafe_allow_html=True)
