import streamlit as st
from transformers import pipeline
import torch
from typing import Dict, Any, Optional

@st.cache_resource(show_spinner="Loading Hugging Face model (this may take a while)...")
def load_hf_pipeline(model_id_or_path: str):
    """
    Loads the Hugging Face model and tokenizer using the pipeline API directly.
    Caches the resource in Streamlit so it's only loaded once per session.
    """
    try:
        # The pipeline automatically handles fetching the tokenizer, configuration, 
        # and model weights based on the model_id_or_path identifier.
        pipe = pipeline(
            "text-generation",
            model=model_id_or_path,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            # For 13B models, you may want to set low_cpu_mem_usage=True, but HF pipeline 
            # handles most of this out of the box when device_map="auto" is passed.
            model_kwargs={"low_cpu_mem_usage": True}
        )
        return pipe, pipe.tokenizer
    except Exception as e:
        st.error(f"Failed to load model from {model_id_or_path}. Error: {e}")
        return None, None

def generate_response(
    pipe, 
    tokenizer, 
    prompt: str, 
    settings: Dict[str, Any],
    is_chat_model: bool = False
) -> Optional[str]:
    """
    Generates text using the loaded pipeline and settings.
    If is_chat_model is True, tries to apply chat template.
    """
    if pipe is None:
        return None
        
    generation_kwargs = {
        "max_new_tokens": settings.get("max_new_tokens", 256),
        "temperature": settings.get("temperature", 0.1),
        "top_p": settings.get("top_p", 0.95),
        "do_sample": settings.get("do_sample", False),
        "return_full_text": False
    }

    # If it's a chat-tuned model, we could use the chat template.
    # For simplicity and flexibility with different models, we just pass the raw prompt 
    # unless it's explicitly formatted as a list of messages.
    try:
        output = pipe(prompt, **generation_kwargs)
        return output[0]['generated_text']
    except Exception as e:
        st.error(f"Generation error: {e}")
        return None
