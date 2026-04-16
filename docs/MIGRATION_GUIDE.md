# Migration Guide: Legacy to Refactored Structure

This document outlines the mapping from the original flat structure to the new senior-developer standard architecture.

## File Mappings

| Original Path | New Path | Description |
|---------------|----------|-------------|
| `app.py` | `app.py` | Main application logic (moved from `src/sqlify/app.py`). |
| `utils/schema_reader.py` | `src/sqlify/database/schema_reader.py` | Database schema extraction. |
| `utils/query_runner.py` | `src/sqlify/database/query_runner.py` | Safe query execution. |
| `utils/model_loader.py` | `src/sqlify/core/model_loader.py` | HF model/pipeline loading. |
| `utils/prompt_builder.py` | `src/sqlify/core/prompt_builder.py` | Prompt engineering logic. |
| `utils/sql_validator.py` | `src/sqlify/validation/sql_validator.py` | Security validation. |
| `utils/parsers.py` | `src/sqlify/validation/parsers.py` | Response parsing (JSON). |
| `utils/state.py` | `src/sqlify/ui/state.py` | Streamlit session state. |
| `tests/` | `tests/unit/` | Unit tests. |

## New Additions
- `src/sqlify/utils/logger.py`: Standardized logging for the entire project.
- `app.py`: New entry point at root.

## How to Run
Use:
```bash
streamlit run app.py
```
