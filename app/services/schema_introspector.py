import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

class SchemaIntrospector:
    def __init__(self, db_path: str, cache_path: str):
        self.db_path = db_path
        self.cache_path = cache_path

    def introspect(self) -> Dict[str, Any]:
        """Extracts schema info: tables, columns, types, keys, and sample values."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")

        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row['name'] for row in cursor.fetchall()]

        catalog = {}
        for table in tables:
            # Get columns
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns_info = cursor.fetchall()
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list('{table}')")
            fks_info = cursor.fetchall()
            fks = []
            for fk in fks_info:
                fks.append({
                    "column": fk['from'],
                    "references_table": fk['table'],
                    "references_column": fk['to']
                })

            columns = []
            for col in columns_info:
                col_name = col['name']
                col_type = col['type']
                
                # Sample values (non-null)
                cursor.execute(f"SELECT DISTINCT \"{col_name}\" FROM \"{table}\" WHERE \"{col_name}\" IS NOT NULL LIMIT 3")
                samples = [str(row[0]) for row in cursor.fetchall()]
                
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "pk": bool(col['pk']),
                    "samples": samples
                })

            catalog[table] = {
                "columns": columns,
                "foreign_keys": fks
            }

        conn.close()

        # Save to cache
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w') as f:
            json.dump(catalog, f, indent=2)

        return catalog

    def load_catalog(self) -> Dict[str, Any]:
        """Loads schema from cache if exists, else introspects."""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        return self.introspect()

    def get_readable_schema(self, table_names: Optional[List[str]] = None) -> str:
        """Returns a human-readable string of the schema for the prompt."""
        catalog = self.load_catalog()
        output = []
        
        target_tables = table_names if table_names else catalog.keys()
        
        for table in target_tables:
            if table not in catalog: continue
            
            info = catalog[table]
            table_str = f"Table: {table}\n"
            cols_str = []
            for col in info['columns']:
                pk_str = " (PK)" if col['pk'] else ""
                sample_str = f" | Samples: {', '.join(col['samples'])}" if col['samples'] else ""
                cols_str.append(f"  - {col['name']} ({col['type']}){pk_str}{sample_str}")
            
            table_str += "\n".join(cols_str)
            
            if info['foreign_keys']:
                table_str += "\n  Foreign Keys:\n"
                for fk in info['foreign_keys']:
                    table_str += f"    - {fk['column']} -> {fk['references_table']}({fk['references_column']})\n"
            
            output.append(table_str)
            
        return "\n\n".join(output)
