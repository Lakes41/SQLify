import streamlit as st
from typing import Dict, Any

def init_state():
    """Initialize the Streamlit session state."""
    if 'history' not in st.session_state:
        st.session_state.history = []
        
    if 'current_query' not in st.session_state:
        st.session_state.current_query = None

def add_to_history(question: str, sql: str, explanation: str, success: bool):
    """Adds a generated query to the session history."""
    st.session_state.history.insert(0, {
        'question': question,
        'sql': sql,
        'explanation': explanation,
        'success': success
    })
    
    # Keep only the last 10 queries
    if len(st.session_state.history) > 10:
        st.session_state.history = st.session_state.history[:10]

def clear_history():
    """Clears the session history."""
    st.session_state.history = []
    st.session_state.current_query = None
