import sqlite3
import pandas as pd
from typing import Tuple, Optional

def execute_query(db_path: str, sql: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Executes a validated read-only SQL query against the SQLite database.
    Returns: (DataFrame with results, error message if any)
    """
    # Ensure URI format for read-only connection
    uri_path = f"file:{db_path}?mode=ro"
    
    try:
        # uri=True allows sqlite3 to interpret the URI and enforce read-only
        with sqlite3.connect(uri_path, uri=True) as conn:
            df = pd.read_sql_query(sql, conn)
            return df, ""
    except sqlite3.Error as e:
        return None, f"Database execution error: {str(e)}"
    except Exception as e:
         return None, f"Unexpected error executing query: {str(e)}"
