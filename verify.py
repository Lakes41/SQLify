import sys
try:
    import transformers
    import streamlit
    import accelerate
    import torch
    import pandas
    import pydantic
    print("All dependencies are correctly installed!")
except ImportError as e:
    print(f"Missing dependency: {e}")
