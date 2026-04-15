import json
import re
from pydantic import BaseModel, ValidationError

class SQLResponse(BaseModel):
    can_answer: bool
    sql: str
    explanation: str

def parse_model_response(text: str) -> SQLResponse:
    """
    Safely parse model output to extract the JSON block.
    Handles extra text, markdown fences, and typical model errors.
    """
    if not text:
        return SQLResponse(can_answer=False, sql="", explanation="No output generated.")

    # Try to find JSON block between ```json and ```
    json_match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Fallback: look for the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1].strip()
        else:
            json_str = text.strip()

    try:
        parsed_dict = json.loads(json_str)
        # Validate with Pydantic
        return SQLResponse(**parsed_dict)
    except json.JSONDecodeError as e:
        return SQLResponse(
            can_answer=False, 
            sql="", 
            explanation=f"Failed to parse JSON output: {e}. Raw text: {text}"
        )
    except ValidationError as e:
        return SQLResponse(
            can_answer=False, 
            sql="", 
            explanation=f"JSON structure invalid: {e}"
        )
