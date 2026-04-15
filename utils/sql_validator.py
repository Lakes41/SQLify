import re
from typing import Dict, Any

def validate_sql(sql: str) -> Dict[str, Any]:
    """
    Validates SQL to ensure it is safe and read-only.
    Returns: { 'is_valid': bool, 'cleaned_sql': str, 'error_message': str }
    """
    if not sql or not sql.strip():
        return {
            'is_valid': False,
            'cleaned_sql': "",
            'error_message': "SQL query is empty."
        }
        
    cleaned_sql = sql.strip()
    
    # Remove any markdown code blocks
    cleaned_sql = re.sub(r"^```sql", "", cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r"```$", "", cleaned_sql).strip()
    
    # 1. Block comments
    if '--' in cleaned_sql or '/*' in cleaned_sql:
         return {
            'is_valid': False,
            'cleaned_sql': cleaned_sql,
            'error_message': "Comments are not allowed in the query."
        }
    
    # 2. Must start with SELECT or WITH
    upper_sql = cleaned_sql.upper()
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
         return {
            'is_valid': False,
            'cleaned_sql': cleaned_sql,
            'error_message': "Query must start with SELECT or WITH."
        }
        
    # 3. Exactly one statement (no semicolons separating multiple statements)
    # We allow one semicolon at the very end.
    if ';' in cleaned_sql:
        parts = cleaned_sql.split(';')
        # if the last part after splitting is not just whitespace, it means multiple statements
        if any(part.strip() for part in parts[1:]):
             return {
                'is_valid': False,
                'cleaned_sql': cleaned_sql,
                'error_message': "Multiple SQL statements are not allowed."
            }
            
    # 4. Block keywords anywhere in the SQL
    blocked_keywords = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', 
        r'\bALTER\b', r'\bCREATE\b', r'\bATTACH\b', r'\bDETACH\b', 
        r'\bPRAGMA\b', r'\bTRUNCATE\b', r'\bREPLACE\b', r'\bVACUUM\b'
    ]
    
    for kw in blocked_keywords:
        if re.search(kw, upper_sql):
             return {
                'is_valid': False,
                'cleaned_sql': cleaned_sql,
                'error_message': f"Blocked keyword detected: {kw.replace(r'\\b', '')}"
            }
            
    return {
        'is_valid': True,
        'cleaned_sql': cleaned_sql,
        'error_message': ""
    }
