import streamlit as st
import os
import sqlite3
import pandas as pd
import sys

# Add src to sys.path to allow absolute imports
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from sqlify.database.schema_reader import get_schema_metadata, format_schema_for_prompt
from sqlify.core.model_loader import load_hf_pipeline, generate_response
from sqlify.core.prompt_builder import build_prompt
from sqlify.validation.parsers import parse_model_response
from sqlify.validation.sql_validator import validate_sql
from sqlify.database.query_runner import execute_query
from sqlify.ui.state import init_state, add_to_history, clear_history
from sqlify.utils.logger import logger

def load_env_variables():
    """Helper to read from .env if python-dotenv is not installed."""
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, val = line.strip().split("=", 1)
                        os.environ[key] = val.strip('"\'')
                    except ValueError:
                        continue

def main():
    st.set_page_config(page_title="SQLify", page_icon="🔍", layout="wide")
    
    load_env_variables()
    
    MODEL_ID_OR_PATH = os.environ.get("MODEL_ID_OR_PATH", "REPLACE_WITH_MY_MODEL")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "REPLACE_WITH_MY_SQLITE_DB")
    
    init_state()
    
    # -----------------
    # Sidebar Settings
    # -----------------
    with st.sidebar:
        st.title("SQLify Settings ⚙️")
        st.markdown("### Environment")
        st.text(f"Model: {MODEL_ID_OR_PATH}")
        st.text(f"Database: {DATABASE_PATH}")
        
        st.markdown("### Generation Settings")
        max_new_tokens = st.number_input("Max New Tokens", min_value=10, max_value=2048, value=256)
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.1, step=0.1)
        top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
        do_sample = st.checkbox("Do Sample", value=False)
        
        st.markdown("### Schema Viewer")
        try:
            schema_metadata = get_schema_metadata(DATABASE_PATH)
            schema_text = format_schema_for_prompt(schema_metadata)
            st.code(schema_text, language="sql")
        except Exception as e:
            st.error(f"Error loading schema: {e}")
            schema_metadata = None
            schema_text = ""
    
        st.markdown("### Example Questions")
        st.markdown("- Show total sales by month")
        st.markdown("- How many users signed up last week?")
        st.markdown("- List the top 5 products by revenue")
    
    # -----------------
    # Main Area
    # -----------------
    st.title("🔍 SQLify")
    st.markdown("Convert natural language business questions into safe, read-only SQLite queries.")
    
    # Load Model
    pipe, tokenizer = load_hf_pipeline(MODEL_ID_OR_PATH)
    
    if not pipe:
        st.error("Model failed to load. Please check the model path in your environment variables.")
        st.stop()
    
    if not schema_metadata:
        st.error("Failed to read database schema. Please check DATABASE_PATH.")
        st.stop()
    
    # Input
    question = st.text_input("Ask a question about your data:", placeholder="e.g. Show total sales by month")
    
    # Action Buttons
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        generate_clicked = st.button("Generate SQL", type="primary")
    
    # Generation Logic
    if generate_clicked and question:
        with st.spinner("Generating SQL..."):
            prompt = build_prompt(question, schema_text)
            settings = {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": do_sample
            }
            
            raw_output = generate_response(pipe, tokenizer, prompt, settings)
            
            if raw_output:
                parsed_response = parse_model_response(raw_output)
                
                st.session_state.current_query = {
                    'question': question,
                    'can_answer': parsed_response.can_answer,
                    'sql': parsed_response.sql,
                    'explanation': parsed_response.explanation,
                    'is_valid': False,
                    'error_message': ""
                }
                
                if parsed_response.can_answer:
                    val_result = validate_sql(parsed_response.sql)
                    st.session_state.current_query['is_valid'] = val_result['is_valid']
                    st.session_state.current_query['sql'] = val_result['cleaned_sql']
                    st.session_state.current_query['error_message'] = val_result['error_message']
                
                add_to_history(
                    question, 
                    parsed_response.sql, 
                    parsed_response.explanation, 
                    st.session_state.current_query['is_valid']
                )
    
    # Display Current Query
    if st.session_state.current_query:
        cq = st.session_state.current_query
        
        st.markdown("### Generated Result")
        if not cq['can_answer']:
            st.warning(f"**The model cannot answer this question based on the schema.**\n\nExplanation: {cq['explanation']}")
        else:
            st.markdown(f"**Explanation:** {cq['explanation']}")
            st.code(cq['sql'], language="sql")
            
            if not cq['is_valid']:
                st.error(f"**SQL Validation Failed:** {cq['error_message']}")
            else:
                st.success("SQL is valid and read-only.")
                
                # Show Run Query Button
                if st.button("Run Query 🚀"):
                    with st.spinner("Executing query..."):
                        df, err = execute_query(DATABASE_PATH, cq['sql'])
                        if err:
                            st.error(f"Execution Error: {err}")
                        else:
                            st.markdown("### Results")
                            st.dataframe(df, use_container_width=True)
    
    # History
    st.markdown("---")
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("### Recent Queries")
    with col_h2:
        if st.button("Clear History"):
            clear_history()
            st.rerun()
    
    if not st.session_state.history:
        st.info("No query history yet.")
    else:
        for item in st.session_state.history:
            with st.expander(f"{'✅' if item['success'] else '❌'} {item['question']}"):
                st.markdown(f"**Explanation:** {item['explanation']}")
                st.code(item['sql'], language="sql")

if __name__ == "__main__":
    main()
