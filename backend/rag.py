import os
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger("rag")

class RAGEngine:
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.model = None
        self._load_model()
        
    def _load_model(self):
        # The model download can take minutes on a fresh machine. Keep the
        # hackathon flow responsive and use the keyword retriever unless
        # semantic retrieval has been explicitly enabled.
        if os.getenv("ENABLE_SEMANTIC_RAG", "false").lower() not in {"1", "true", "yes"}:
            logger.info("Semantic RAG disabled; using keyword retrieval.")
            return
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight CPU-friendly model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading SentenceTransformer: {e}. Semantic search will fall back to keyword search.")
            self.model = None

    def add_documents(self, parsed_docs: List[Dict[str, Any]]):
        """
        parsed_docs: List of parsed document dicts from parser.py
        Each contains:
        {
            "filename": str,
            "doc_type": str,
            "chunks": [
                {
                    "text": str,
                    "location": str,
                    "page": int,
                    "detail": str
                }
            ]
        }
        """
        new_chunks = []
        for doc in parsed_docs:
            for c in doc["chunks"]:
                new_chunks.append({
                    "text": c["text"],
                    "location": c["location"],
                    "page": c["page"],
                    "detail": c["detail"],
                    "filename": doc["filename"],
                    "doc_type": doc["doc_type"]
                })
                
        if not new_chunks:
            return
            
        self.chunks.extend(new_chunks)
        
        if self.model:
            try:
                texts = [c["text"] for c in new_chunks]
                new_embeddings = self.model.encode(texts, show_progress_bar=False)
                if len(self.embeddings) == 0:
                    self.embeddings = new_embeddings
                else:
                    self.embeddings = np.vstack([self.embeddings, new_embeddings])
            except Exception as e:
                logger.error(f"Failed to encode document chunks: {e}")
                self.embeddings = []

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top_k chunks matching the query.
        Falls back to keyword matching if embedding fails or model isn't loaded.
        """
        if not self.chunks:
            return []
            
        if self.model and len(self.embeddings) > 0:
            try:
                query_emb = self.model.encode([query], show_progress_bar=False)[0]
                # Cosine similarity
                norms = np.linalg.norm(self.embeddings, axis=1)
                query_norm = np.linalg.norm(query_emb)
                
                # Avoid division by zero
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
            except Exception as e:
                logger.error(f"Error in vector search: {e}. Falling back to keyword search.")
                
        # Keyword-based fallback search
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
                
        # Sort by match score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]
