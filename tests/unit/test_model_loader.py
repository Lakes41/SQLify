import unittest
import sys
import os

# Add src to path so we can import the refactored code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sqlify.core.model_loader import load_hf_pipeline
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import warnings

class TestModelLoader(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore")
        self.model_id = "sshleifer/tiny-gpt2"
        self.prompt = "SELECT * FROM users WHERE"

    def test_pipeline_loading(self):
        """
        Verifies that the refactored load_hf_pipeline works correctly with a tiny model.
        """
        print(f"\n[TEST] Loading tiny model: {self.model_id}")
        pipe, tokenizer = load_hf_pipeline(self.model_id)
        
        self.assertIsNotNone(pipe, "Pipeline should not be None")
        self.assertIsNotNone(tokenizer, "Tokenizer should not be None")
        
        # Test generation
        gen_kwargs = {
            "max_new_tokens": 5,
            "do_sample": False,
            "return_full_text": False
        }
        
        output = pipe(self.prompt, **gen_kwargs)[0]['generated_text']
        print(f"[TEST] Generated output: '{output}'")
        self.assertTrue(len(output) > 0, "Output should not be empty")

if __name__ == '__main__':
    unittest.main()
