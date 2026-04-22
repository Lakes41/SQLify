import streamlit as st
import pandas as pd
import time
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from services.pipeline import SQLifyPipeline

# Page config
st.set_page_config(
    page_title="SQLify - Local Natural Language to SQL",
    page_icon="🔍",
    layout="wide"
)

# Initialize pipeline
@st.cache_resource
def get_pipeline():
    pipeline = SQLifyPipeline(CONFIG)
    pipeline.initialize()
    return pipeline

try:
    pipeline = get_pipeline()
except Exception as e:
    st.error(f"Failed to initialize pipeline: {e}")
    st.info("Make sure you have run the setup scripts and created the sample database.")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("Settings")
    db_path = st.text_input("Database Path", CONFIG["db_path"])
    llm_url = st.text_input("LLM Endpoint", CONFIG["llm_endpoint"])
    top_k = st.slider("Top-K Retrieval", 1, 10, CONFIG["top_k_retrieval"])
    
    st.divider()
    if st.button("Rebuild Schema Cache"):
        with st.spinner("Rebuilding..."):
            pipeline.initialize(force=True)
            st.success("Cache rebuilt!")
            
    st.divider()
    st.markdown("### About")
    st.info(
        "SQLify is a local-first NL-to-SQL tool designed for safety and privacy. "
        "It uses local LLMs and embeddings to query your data without cloud APIs."
    )

# Main UI
st.title("🔍 SQLify")
st.subheader("Ask questions about your business data in plain English")

# Query input
query = st.text_input(
    "Enter your question:",
    placeholder="e.g., 'Show total revenue by month for the last year'",
    key="query_input"
)

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🚀 Run Query", type="primary", use_container_width=True)

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

if run_button and query:
    with st.spinner("Analyzing question and generating SQL..."):
        result = pipeline.run(query, top_k=top_k)
        st.session_state.history.append({"query": query, "result": result})
        
        if result.get("needs_clarification"):
            st.warning(f"**Clarification Needed:** {result['clarification_question']}")
        
        elif not result["success"]:
            st.error(f"**Error:** {result['error']}")
            if "sql" in result:
                with st.expander("View Generated SQL (Invalid)"):
                    st.code(result["sql"], language="sql")
        
        else:
            # Success!
            st.success(f"Query executed in {result['elapsed_time']:.2f}s")
            
            # Results table
            if result.get("data"):
                df = pd.DataFrame(result["data"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data returned for this query.")
                
            # Tabs for details
            tab1, tab2, tab3, tab4 = st.tabs(["SQL & Plan", "Assumptions", "Retrieved Context", "Debug Info"])
            
            with tab1:
                st.markdown("#### Generated SQL")
                st.code(result["sql"], language="sql")
                if result.get("query_plan"):
                    st.markdown("#### Query Plan")
                    st.text(result["query_plan"])
                    
            with tab2:
                llm_out = result.get("llm_output", {})
                st.markdown("#### Assumptions")
                for assumption in llm_out.get("assumptions", []):
                    st.markdown(f"- {assumption}")
                
                st.markdown("#### Tables Used")
                st.write(", ".join(llm_out.get("tables_used", [])))
                
                st.markdown("#### Business Terms")
                st.write(", ".join(llm_out.get("business_terms_used", [])))
                
            with tab3:
                context = result.get("context", {})
                st.markdown("#### Relevant Tables")
                for t in context.get("tables", []):
                    st.markdown(f"- **{t['name']}**: {t['text']}")
                
                st.markdown("#### Relevant Metrics")
                for m in context.get("metrics", []):
                    st.markdown(f"- **{m['name']}**: {m['text']}")
                    
                st.markdown("#### Similar Examples")
                for e in context.get("examples", []):
                    st.markdown(f"- **Q:** {e['info']['question']}")
                    st.code(e['info']['sql'], language="sql")
                    
            with tab4:
                st.json(result)

# History sidebar
if st.session_state.history:
    with st.sidebar:
        st.divider()
        st.subheader("History")
        for i, h in enumerate(reversed(st.session_state.history)):
            if st.button(f"{h['query'][:30]}...", key=f"hist_{i}"):
                # This could re-populate the query input
                pass
