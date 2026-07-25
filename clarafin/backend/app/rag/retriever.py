import numpy as np
from typing import List, Dict, Any
from clarafin.backend.app.rag.embed import Embedder

class Retriever:
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.embedder = Embedder()
        
    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        if not new_chunks:
            return
            
        start_idx = len(self.chunks)
        self.chunks.extend(new_chunks)
        
        texts = [c["text"] for c in new_chunks]
        embs = self.embedder.encode(texts)
        
        if embs is not None:
            if len(self.embeddings) == 0:
                self.embeddings = embs
            else:
                self.embeddings = np.vstack([self.embeddings, embs])

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []
            
        # Semantic search
        if len(self.embeddings) > 0:
            try:
                query_emb = self.embedder.encode([query])
                if query_emb is not None:
                    query_emb = query_emb[0]
                    norms = np.linalg.norm(self.embeddings, axis=1)
                    query_norm = np.linalg.norm(query_emb)
                    
                    norms[norms == 0] = 1e-10
                    if query_norm == 0:
                        query_norm = 1e-10
                        
                    similarities = np.dot(self.embeddings, query_emb) / (norms * query_norm)
                    top_indices = np.argsort(similarities)[::-1][:top_k]
                    
                    results = []
                    for idx in top_indices:
                        chunk = self.chunks[idx].copy()
                        chunk["score"] = float(similarities[idx])
                        results.append(chunk)
                    return results
            except Exception:
                pass
                
        # Keyword fallback
        results = []
        query_words = query.lower().split()
        for c in self.chunks:
            matches = 0
            text_lower = c["text"].lower()
            for qw in query_words:
                if qw in text_lower:
                    matches += 1
            if matches > 0:
                chunk_copy = c.copy()
                chunk_copy["score"] = matches / len(query_words)
                results.append(chunk_copy)
                
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]
