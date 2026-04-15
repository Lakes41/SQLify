def build_prompt(question: str, schema_text: str) -> str:
    """
    Constructs a compact prompt instructing the model to generate SQL.
    Includes rules, the schema, and few-shot examples.
    """
    prompt = f"""You are a helpful and accurate SQL assistant. Your task is to convert natural language business questions into safe, read-only SQLite queries.

RULES:
1. Generate SQLite SQL only.
2. Use ONLY tables and columns from the provided schema.
3. Produce ONLY ONE read-only query (e.g., SELECT or WITH).
4. Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, or other modifying commands.
5. If the question cannot be answered using the schema, set can_answer to false.
6. You MUST return your response as valid JSON ONLY, with no extra text or markdown outside the JSON block.

JSON FORMAT:
{{
    "can_answer": true/false,
    "sql": "YOUR SQL QUERY HERE OR EMPTY STRING",
    "explanation": "Brief explanation of what the query does or why it cannot be answered."
}}

{schema_text}

EXAMPLES:
Question: Show the total number of users.
JSON:
{{
    "can_answer": true,
    "sql": "SELECT COUNT(*) FROM users;",
    "explanation": "Counting all records in the users table."
}}

Question: Add a new user named Alice.
JSON:
{{
    "can_answer": false,
    "sql": "",
    "explanation": "I can only read data, not modify it."
}}

Question: {question}
JSON:
"""
    return prompt
