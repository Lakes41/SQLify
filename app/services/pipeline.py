import time
import yaml
import os
from typing import Dict, Any, Optional, List
from .schema_introspector import SchemaIntrospector
from .retrieval import SchemaRetriever
from .llm_client import LLMClient
from .prompting import PromptBuilder
from .sql_validator import SQLValidator
from .sqlite_executor import SQLiteExecutor

class SQLifyPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.introspector = SchemaIntrospector(config['db_path'], config['schema_cache_path'])
        self.retriever = SchemaRetriever(config['embedding_model'], config['cache_dir'])
        self.llm = LLMClient(config['llm_endpoint'])
        self.prompter = PromptBuilder()
        self.validator = SQLValidator()
        self.executor = SQLiteExecutor(config['db_path'], config['timeout_ms'], config['row_cap'])
        
        # Load semantics and examples
        with open(config['semantics_path'], 'r') as f:
            self.semantics = yaml.safe_load(f)
        with open(config['examples_path'], 'r') as f:
            self.examples = yaml.safe_load(f)

    def initialize(self, force: bool = False):
        """Builds or loads the retrieval index."""
        if not self.retriever.load_index() or force:
            catalog = self.introspector.load_catalog()
            self.retriever.build_index(catalog, self.semantics, self.examples)

    def run(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Retrieval
        context = self.retriever.retrieve(question, top_k=top_k)
        
        # 2. Schema text for retrieved tables
        table_names = [t['name'] for t in context['tables']]
        schema_text = self.introspector.get_readable_schema(table_names)
        
        # 3. Prompting
        user_prompt = self.prompter.build_user_prompt(
            question, 
            schema_text, 
            context['metrics'], 
            context['dimensions'], 
            context['examples']
        )
        
        # 4. LLM Generation
        llm_response = self.llm.generate(
            self.prompter.SYSTEM_PROMPT, 
            user_prompt,
            response_format={"type": "json_object"}
        )
        
        if "error" in llm_response:
            return {
                "success": False,
                "error": llm_response["error"],
                "context": context,
                "elapsed_time": time.time() - start_time
            }

        # 5. SQL Validation
        sql = llm_response.get("sql")
        if llm_response.get("intent") == "generate_sql" and sql:
            is_valid, val_error = self.validator.validate(sql)
            if not is_valid:
                # Optional: repair loop could go here
                return {
                    "success": False,
                    "error": f"SQL Validation Failed: {val_error}",
                    "sql": sql,
                    "context": context,
                    "llm_output": llm_response,
                    "elapsed_time": time.time() - start_time
                }
            
            # 6. Execution
            execution_result = self.executor.execute(sql)
            
            return {
                "success": execution_result["success"],
                "data": execution_result.get("data"),
                "columns": execution_result.get("columns"),
                "error": execution_result.get("error"),
                "sql": sql,
                "context": context,
                "llm_output": llm_response,
                "query_plan": self.executor.explain_query_plan(sql) if execution_result["success"] else None,
                "elapsed_time": time.time() - start_time
            }
        
        elif llm_response.get("needs_clarification"):
            return {
                "success": True,
                "needs_clarification": True,
                "clarification_question": llm_response.get("clarification_question"),
                "context": context,
                "llm_output": llm_response,
                "elapsed_time": time.time() - start_time
            }
        
        else:
            return {
                "success": False,
                "error": "The model could not generate a valid query for this question.",
                "context": context,
                "llm_output": llm_response,
                "elapsed_time": time.time() - start_time
            }
