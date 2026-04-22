import sys
import os

# Add parent dir to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from services.pipeline import SQLifyPipeline

def rebuild():
    print("Rebuilding schema cache and retrieval index...")
    pipeline = SQLifyPipeline(CONFIG)
    pipeline.initialize(force=True)
    print("Done!")

if __name__ == "__main__":
    rebuild()
