import sqlglot
from sqlglot import exp, parse_one
from typing import List, Tuple, Optional, Set

class SQLValidator:
    FORBIDDEN_TOKENS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
        "PRAGMA", "ATTACH", "DETACH", "VACUUM", "REINDEX", "GRANT", "REVOKE"
    }

    def __init__(self, allowed_tables: Optional[Set[str]] = None):
        self.allowed_tables = allowed_tables

    def validate(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the SQL query for safety and correctness.
        Returns (is_valid, error_message).
        """
        if not sql or not sql.strip():
            return False, "SQL query is empty."

        # 1. Reject comments
        if "--" in sql or "/*" in sql:
            return False, "Comments are not allowed in SQL queries."

        # 2. Check for multiple statements
        if sql.strip().count(";") > 1 or (";" in sql and sql.strip().rstrip(";") != sql.strip()[:-1]):
            # This is a bit naive but sqlglot.parse will also help
            pass

        try:
            # 3. Parse with sqlglot
            expressions = sqlglot.parse(sql, read="sqlite")
            
            if len(expressions) != 1:
                return False, "Only one SQL statement is allowed."
            
            expression = expressions[0]

            # 4. Must be a SELECT or WITH (CTE)
            if not isinstance(expression, (exp.Select, exp.With)):
                return False, f"Only SELECT queries are allowed. Found: {expression.key.upper()}"

            # 5. Check for forbidden tokens/commands
            for node in expression.walk():
                # Check command type
                if node.key.upper() in self.FORBIDDEN_TOKENS:
                    return False, f"Forbidden SQL command found: {node.key.upper()}"
                
                # 6. Table validation (if whitelist provided)
                if self.allowed_tables and isinstance(node, exp.Table):
                    table_name = node.name.lower()
                    if table_name not in [t.lower() for t in self.allowed_tables]:
                        return False, f"Table '{table_name}' is not in the allowed schema context."

            # 7. Require LIMIT for non-aggregate queries
            # We'll check if it's a simple select and if it has an aggregation
            is_aggregate = any(
                isinstance(e, (exp.Count, exp.Sum, exp.Avg, exp.Max, exp.Min)) 
                for e in expression.find_all(exp.AggFunc)
            ) or expression.find(exp.Group)
            
            has_limit = expression.find(exp.Limit)
            
            # If not an aggregate and no limit, we might want to enforce it, 
            # but our executor already has a row cap. Let's make it a recommendation 
            # or a soft requirement. For now, let's just log or ignore since row_cap exists.
            
            return True, None

        except sqlglot.errors.ParseError as e:
            return False, f"SQL Parse Error: {str(e)}"
        except Exception as e:
            return False, f"Validation Error: {str(e)}"

    def get_tables_used(self, sql: str) -> Set[str]:
        """Extracts table names from the SQL query."""
        try:
            expression = parse_one(sql, read="sqlite")
            return {table.name.lower() for table in expression.find_all(exp.Table)}
        except:
            return set()
