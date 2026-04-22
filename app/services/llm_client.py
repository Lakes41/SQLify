import requests
import json
from typing import Dict, Any, Optional, List

class LLMClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8080/v1"):
        self.base_url = base_url

    def generate(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calls the llama.cpp server completions endpoint."""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": "qwen2.5-coder-1.5b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if response_format:
            payload["response_format"] = response_format

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Attempt to parse JSON if requested
            if response_format and response_format.get("type") == "json_object":
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: find JSON block
                    import re
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
                    raise ValueError(f"Failed to parse JSON from LLM response: {content}")
            
            return {"content": content}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"LLM Server Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected Error: {str(e)}"}
