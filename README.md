# SQLify

A Streamlit web application that converts natural-language business questions into safe, read-only SQLite queries using a local Hugging Face transformer model.

## Features
- Connects dynamically to any SQLite database and extracts schema.
- Uses Hugging Face `transformers` to generate SQL from natural language.
- Strictly validates generated SQL for read-only safety (blocks `INSERT`, `UPDATE`, `DROP`, multi-statement, etc.).
- Clean Streamlit UI with query history, settings, and result display.

## Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.11 installed. Create a virtual environment and install the requirements:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory (or rename `.env.example` to `.env`) and update the paths:

```env
# Hugging Face Model ID (e.g. "budecosystem/sql-millennials-13b") 
# Or an absolute local path to your model folder
MODEL_ID_OR_PATH="budecosystem/sql-millennials-13b"

# Absolute path to your SQLite database
DATABASE_PATH="REPLACE_WITH_MY_SQLITE_DB"
```

### 3. Run the App
Start the Streamlit server:

```bash
streamlit run app.py
```

## Known Limitations
- The application currently supports SQLite only.
- Designed for small/medium local transformer models. Ensure you have adequate RAM/VRAM for the model you specify.
- V1 does not include user authentication or containerization.

## Example Questions
- "Show total sales by month"
- "How many users signed up last week?"
- "List the top 5 products by revenue"
