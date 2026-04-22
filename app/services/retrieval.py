import numpy as np
import os
import json
import yaml
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class SchemaRetriever:
    def __init__(
        self, 
        model_name: str = "BAAI/bge-small-en-v1.5",
        cache_dir: str = "app/schema_cache"
    ):
        self.model = SentenceTransformer(model_name)
        self.cache_dir = cache_dir
        self.embeddings_path = os.path.join(cache_dir, "retrieval_embeddings.npy")
        self.meta_path = os.path.join(cache_dir, "retrieval_meta.json")
        
        self.items: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None

    def build_index(
        self, 
        catalog: Dict[str, Any], 
        semantics: Dict[str, Any], 
        examples: List[Dict[str, Any]]
    ):
        """Creates retrieval items and computes embeddings."""
        self.items = []
        
        # 1. Table items
        for table, info in catalog.items():
            cols = [c['name'] for c in info['columns']]
            text = f"Table: {table}. Columns: {', '.join(cols)}. Description: Data about {table}."
            self.items.append({"type": "table", "name": table, "text": text})
            
        # 2. Metric items
        for metric_name, info in semantics.get('metrics', {}).items():
            text = f"Metric: {metric_name}. Description: {info.get('description', '')}. Formula: {info.get('expression', '')}"
            self.items.append({"type": "metric", "name": metric_name, "text": text, "info": info})
            
        # 3. Dimension items
        for dim_name, info in semantics.get('dimensions', {}).items():
            text = f"Dimension: {dim_name}. Description: {info.get('description', '')}. Expression: {info.get('expression', '')}"
            self.items.append({"type": "dimension", "name": dim_name, "text": text, "info": info})
            
        # 4. Example items
        for i, ex in enumerate(examples):
            text = f"Example Question: {ex['question']}. SQL: {ex['sql']}"
            self.items.append({"type": "example", "id": i, "text": text, "info": ex})

        # Compute embeddings
        texts = [item['text'] for item in self.items]
        self.embeddings = self.model.encode(texts, normalize_embeddings=True)
        
        # Save
        os.makedirs(self.cache_dir, exist_ok=True)
        np.save(self.embeddings_path, self.embeddings)
        with open(self.meta_path, 'w') as f:
            json.dump(self.items, f, indent=2)

    def load_index(self):
        """Loads index from disk."""
        if os.path.exists(self.embeddings_path) and os.path.exists(self.meta_path):
            self.embeddings = np.load(self.embeddings_path)
            with open(self.meta_path, 'r') as f:
                self.items = json.load(f)
            return True
        return False

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves top_k items of each type or overall."""
        if self.embeddings is None:
            raise ValueError("Index not loaded or built.")
            
        query_emb = self.model.encode([query], normalize_embeddings=True)
        similarities = np.dot(self.embeddings, query_emb.T).flatten()
        
        # Get top indices
        top_indices = np.argsort(similarities)[::-1][:top_k * 3] # Get more to filter by type
        
        results = {
            "tables": [],
            "metrics": [],
            "dimensions": [],
            "examples": []
        }
        
        for idx in top_indices:
            item = self.items[idx]
            item_type = item['type'] + "s"
            if len(results.get(item_type, [])) < top_k:
                results[item_type].append(item)
                
        return results
