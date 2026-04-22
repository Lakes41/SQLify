import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "schema_cache")

# App Config
CONFIG = {
    "db_path": os.path.join(DATA_DIR, "sample_business.db"),
    "semantics_path": os.path.join(BASE_DIR, "business_semantics.yml"),
    "examples_path": os.path.join(BASE_DIR, "fewshot_examples.yml"),
    "schema_cache_path": os.path.join(CACHE_DIR, "schema_catalog.json"),
    "cache_dir": CACHE_DIR,
    
    # LLM & Embeddings
    "llm_endpoint": "http://127.0.0.1:8080/v1",
    "embedding_model": "BAAI/bge-small-en-v1.5",
    
    # Execution constraints
    "timeout_ms": 2000,
    "row_cap": 500,
    "top_k_retrieval": 3
}

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
