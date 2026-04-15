import unittest
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import warnings

class TestModelLoader(unittest.TestCase):
    def setUp(self):
        # Ignore irrelevant transformers warnings about device placement
        warnings.filterwarnings("ignore")
        
        # Using a tiny dummy model for testing to avoid huge downloads or OutOfMemory errors.
        # This proves the mechanism without having to download the 13B model (26GB).
        self.model_id = "sshleifer/tiny-gpt2"
        self.prompt = "SELECT * FROM users WHERE"

    def test_pipeline_vs_manual_loading(self):
        """
        Verifies that the new pipeline-based code produces identical inference results 
        compared to the previous manual model-download approach.
        """
        
        print("\n[TEST] Loading model manually (legacy method)...")
        # 1. Manual Loading (Previous Approach)
        tokenizer_manual = AutoTokenizer.from_pretrained(self.model_id)
        model_manual = AutoModelForCausalLM.from_pretrained(self.model_id)
        pipe_manual = pipeline(
            "text-generation", 
            model=model_manual, 
            tokenizer=tokenizer_manual
        )
        
        print("[TEST] Loading model using pipeline API (new method)...")
        # 2. Pipeline API (New Approach)
        pipe_auto = pipeline(
            "text-generation", 
            model=self.model_id
        )
        
        # Fixed generation settings to ensure determinism
        gen_kwargs = {
            "max_new_tokens": 5,
            "do_sample": False,
            "return_full_text": False
        }
        
        print("[TEST] Running inference on both pipelines...")
        # Compare outputs
        out_manual = pipe_manual(self.prompt, **gen_kwargs)[0]['generated_text']
        out_auto = pipe_auto(self.prompt, **gen_kwargs)[0]['generated_text']
        
        print(f"[TEST] Manual Output: '{out_manual}'")
        print(f"[TEST] Auto Output: '{out_auto}'")
        
        self.assertEqual(
            out_manual, 
            out_auto, 
            "Outputs from manual loading and auto pipeline do not match!"
        )

if __name__ == '__main__':
    unittest.main()
