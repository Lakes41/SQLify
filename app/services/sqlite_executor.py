import sqlite3
import time
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

class SQLiteExecutor:
    def __init__(self, db_path: str, timeout_ms: int = 1000, row_cap: int = 1000):
        self.db_path = db_path
        self.timeout_ms = timeout_ms
        self.row_cap = row_cap
        self.uri = f"file:{db_path}?mode=ro"

    def _authorizer_callback(self, action_code, arg1, arg2, db_name, trigger_name):
        """
        Enforce strict read-only access at the authorizer level.
        Deny any action that isn't a basic SELECT or metadata read.
        """
        # Allowed codes for SELECT statements
        allowed_codes = {
            sqlite3.SQLITE_SELECT,
            sqlite3.SQLITE_READ,
            sqlite3.SQLITE_FUNCTION,
            sqlite3.SQLITE_RECURSIVE,
        }
        
        if action_code in allowed_codes:
            return sqlite3.SQLITE_OK
        
        # Deny everything else
        return sqlite3.SQLITE_DENY

    def _progress_handler(self):
        """
        Aborts queries that take too long.
        Called every N instructions.
        """
        # In a real implementation, we'd check elapsed time here.
        # For simplicity in this demo, we'll return 1 to abort if needed.
        # But we'll handle the actual timeout logic in execute.
        return 0 

    def execute(self, sql: str) -> Dict[str, Any]:
        start_time = time.time()
        try:
            # Connect using URI mode for read-only
            conn = sqlite3.connect(self.uri, uri=True)
            conn.row_factory = sqlite3.Row
            
            # Extra safety: PRAGMA query_only
            conn.execute("PRAGMA query_only = ON")
            
            # Set authorizer
            conn.set_authorizer(self._authorizer_callback)
            
            # Set progress handler (called every 1000 instructions)
            # We use this as a simple way to prevent long-running queries
            # though a more robust way is to check time in the callback.
            def timeout_checker():
                if (time.time() - start_time) * 1000 > self.timeout_ms:
                    return 1 # Abort
                return 0
            
            conn.set_progress_handler(timeout_checker, 1000)
            
            cursor = conn.execute(sql)
            
            # Fetch up to row_cap + 1 to check if there's more data
            rows = cursor.fetchmany(self.row_cap + 1)
            
            has_more = len(rows) > self.row_cap
            if has_more:
                rows = rows[:self.row_cap]
                
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Convert to list of dicts
            results = [dict(row) for row in rows]
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "columns": columns,
                "data": results,
                "row_count": len(results),
                "has_more": has_more,
                "elapsed_time": elapsed_time,
                "sql": sql
            }
            
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time,
                "sql": sql
            }
        finally:
            if 'conn' in locals():
                conn.close()

    def explain_query_plan(self, sql: str) -> str:
        """Runs EXPLAIN QUERY PLAN for the given SQL."""
        try:
            conn = sqlite3.connect(self.uri, uri=True)
            cursor = conn.execute(f"EXPLAIN QUERY PLAN {sql}")
            plans = cursor.fetchall()
            return "\n".join([str(dict(p)) for p in plans])
        except Exception as e:
            return f"Error explaining query plan: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()
