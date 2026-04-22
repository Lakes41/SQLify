from typing import List, Dict, Any

class PromptBuilder:
    SYSTEM_PROMPT = """You are a senior SQL engineer. Your task is to convert natural language business questions into safe, read-only SQLite queries.
    
    CRITICAL RULES:
    1. Output MUST be a valid JSON object.
    2. SQL must be READ-ONLY (SELECT only).
    3. Use the provided schema and business semantics.
    4. If the question is ambiguous, set "needs_clarification" to true and provide a "clarification_question".
    5. If the question cannot be answered with the available data, set "intent" to "reject".
    6. Do not include any comments in the SQL.
    7. Always use double quotes for table and column names to avoid conflicts with reserved words.
    
    JSON SCHEMA:
    {
        "intent": "generate_sql" | "reject",
        "sql": "string",
        "tables_used": ["string"],
        "business_terms_used": ["string"],
        "assumptions": ["string"],
        "needs_clarification": boolean,
        "clarification_question": "string" | null
    }
    """

    def build_user_prompt(
        self, 
        question: str, 
        schema_text: str, 
        metrics: List[Dict[str, Any]], 
        dimensions: List[Dict[str, Any]], 
        examples: List[Dict[str, Any]]
    ) -> str:
        prompt = f"### Question: {question}\n\n"
        
        prompt += "### Database Schema:\n"
        prompt += schema_text + "\n\n"
        
        if metrics:
            prompt += "### Business Metrics:\n"
            for m in metrics:
                prompt += f"- {m['name']}: {m['info']['description']} (Expression: {m['info']['expression']})\n"
            prompt += "\n"
            
        if dimensions:
            prompt += "### Business Dimensions:\n"
            for d in dimensions:
                prompt += f"- {d['name']}: {d['info']['description']} (Expression: {d['info']['expression']})\n"
            prompt += "\n"
            
        if examples:
            prompt += "### Few-Shot Examples:\n"
            for ex in examples:
                prompt += f"Question: {ex['info']['question']}\nSQL: {ex['info']['sql']}\n\n"
        
        prompt += "### Answer (JSON):"
        return prompt
