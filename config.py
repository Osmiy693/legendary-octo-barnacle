"""
config.py - Loads environment variables and provides configuration.
Uses python-dotenv to load OPENAI_API_KEY from .env file.
Also supports Streamlit Community Cloud secrets (st.secrets).
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """
    Returns the OpenAI API key from environment variables or Streamlit secrets.
    Priority: Streamlit secrets > environment variable > empty string.
    """
    # Try Streamlit Cloud secrets first
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # Fall back to environment variable (.env file)
    return os.getenv("OPENAI_API_KEY", "")
