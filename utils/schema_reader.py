import sqlite3
import os
from typing import Dict, List, Any

def get_schema_metadata(db_path: str) -> Dict[str, Any]:
    """
    Connect to SQLite database and extract table schemas dynamically.
    Returns structured schema metadata.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    schema_metadata = {}
    
    # Connect to database in read-only mode using URI
    uri_path = f"file:{db_path}?mode=ro"
    with sqlite3.connect(uri_path, uri=True) as conn:
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            # Skip SQLite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            schema_metadata[table_name] = {
                'columns': [],
                'foreign_keys': []
            }
            
            # Get column information
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            for col in columns:
                # cid, name, type, notnull, dflt_value, pk
                schema_metadata[table_name]['columns'].append({
                    'name': col[1],
                    'type': col[2],
                    'is_pk': bool(col[5])
                })
                
            # Get foreign key information
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
            fks = cursor.fetchall()
            for fk in fks:
                # id, seq, table, from, to, on_update, on_delete, match
                schema_metadata[table_name]['foreign_keys'].append({
                    'from_column': fk[3],
                    'to_table': fk[2],
                    'to_column': fk[4]
                })
                
    return schema_metadata

def format_schema_for_prompt(schema_metadata: Dict[str, Any]) -> str:
    """
    Format the extracted structured schema into a readable text format for the LLM prompt.
    """
    lines = ["Database Schema:"]
    for table, details in schema_metadata.items():
        lines.append(f"Table: {table}")
        
        cols_str = []
        for col in details['columns']:
            pk_str = " (PRIMARY KEY)" if col['is_pk'] else ""
            cols_str.append(f"  - {col['name']} ({col['type']}){pk_str}")
        lines.extend(cols_str)
        
        if details['foreign_keys']:
            lines.append("  Foreign Keys:")
            for fk in details['foreign_keys']:
                lines.append(f"  - {fk['from_column']} -> {fk['to_table']}({fk['to_column']})")
        
        lines.append("") # Empty line for separation
        
    return "\n".join(lines)
