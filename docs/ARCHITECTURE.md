# SQLify Architecture

## Overview
SQLify is built with a domain-driven modular architecture designed for scalability, maintainability, and clear separation of concerns.

## Directory Structure
- `app.py`: Main entry point for the Streamlit application.
- `src/sqlify/`: Root package for the application logic.
    - `core/`: Core LLM logic, including model loading and prompt construction.
    - `database/`: Database interaction layer (schema reading, query execution).
    - `validation/`: Security and parsing layer for SQL queries.
    - `ui/`: Streamlit-specific UI components and state management.
    - `utils/`: Shared utilities like centralized logging.
- `tests/`: Organized into `unit` and `integration` tests.
- `docs/`: Technical documentation and migration guides.
- `config/`: Configuration files and environment templates.

## Key Design Principles
1. **SOLID Principles**:
    - **Single Responsibility**: Each module handles a specific domain (e.g., `sql_validator` only validates SQL).
    - **Open/Closed**: The system is designed to be easily extendable (e.g., adding new validation rules).
2. **Centralized Logging**: All modules use a standardized logger from `utils/logger.py` for consistent observability.
3. **Read-Only Safety**: Security is enforced at both the application level (validation) and the database level (URI `mode=ro`).
4. **Session State Isolation**: UI state is managed centrally in `ui/state.py`.

## Data Flow
1. User enters a question in the Streamlit UI.
2. `schema_reader` extracts metadata from the SQLite database.
3. `prompt_builder` constructs an LLM prompt with the schema and question.
4. `model_loader` executes inference using a local Hugging Face pipeline.
5. `parsers` extracts JSON from the model response.
6. `sql_validator` checks the generated SQL for forbidden keywords and patterns.
7. `query_runner` executes the validated SQL and returns a Pandas DataFrame.
