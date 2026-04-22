# SQLify - Local NL-to-SQL

SQLify is a production-quality local-first Streamlit application that converts natural language business questions into safe, read-only SQLite queries. It is designed to run on CPU-only hardware with limited RAM, ensuring privacy and security by keeping all data and processing local.

## Features

- **Local LLM**: Uses `Qwen2.5-Coder-1.5B-Instruct-GGUF` running via `llama.cpp` server.
- **Local Embeddings**: Uses `BAAI/bge-small-en-v1.5` for schema retrieval.
- **Safety by Construction**:
  - Read-only SQLite connection (`mode=ro`).
  - `PRAGMA query_only = ON`.
  - Custom SQLite authorizer to block dangerous operations (INSERT, UPDATE, DELETE, etc.).
  - SQL validation using `sqlglot`.
- **Business Semantic Layer**: YAML-based definitions for metrics, dimensions, and synonyms.
- **Retrieval-Augmented Generation (RAG)**: Retrieves only relevant schema and few-shot examples to keep prompts compact.

## Setup Instructions

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Download LLM Model
Download the `Qwen2.5-Coder-1.5B-Instruct-GGUF` model (q4_k_m recommended) from Hugging Face.
```bash
# Example using huggingface-cli
huggingface-cli download Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF qwen2.5-coder-1.5b-instruct-q4_k_m.gguf --local-dir models
```

### 3. Start llama.cpp Server
Run the `llama-server` (part of llama.cpp):
```bash
./llama-server -m models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf --port 8080 --ctx-size 4096
```

### 4. Initialize Database and Cache
```bash
python scripts/create_sample_db.py
python scripts/rebuild_schema_cache.py
```

### 5. Run the App
```bash
streamlit run app.py
```

## Architecture

1. **User Input**: Question received via Streamlit.
2. **Retrieval**: `SchemaRetriever` finds relevant tables, metrics, and examples using embeddings.
3. **Prompting**: `PromptBuilder` constructs a compact prompt with the retrieved context.
4. **LLM Generation**: `LLMClient` calls the local `llama.cpp` server for structured JSON output.
5. **Validation**: `SQLValidator` parses the SQL with `sqlglot` to ensure it's a single, safe SELECT statement.
6. **Execution**: `SQLiteExecutor` runs the query with multiple runtime guards.
7. **Presentation**: Results are displayed in a Pandas dataframe with supporting info.

## Safety Measures

- **SQLite URI Mode**: `file:path?mode=ro` ensures the OS-level file handle is read-only.
- **Authorizer**: A Python callback intercepts every SQLite action, denying anything that isn't a read operation.
- **Progress Handler**: Aborts queries that exceed the time limit (timeout).
- **SQL Parser**: `sqlglot` ensures the generated SQL follows strict rules before it even touches the database.
