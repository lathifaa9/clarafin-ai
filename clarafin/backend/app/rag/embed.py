import logging

logger = logging.getLogger("embed")

class Embedder:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("RAG SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}. Falling back to keyword search.")
            self.model = None

    def encode(self, texts: list):
        if self.model:
            try:
                return self.model.encode(texts, show_progress_bar=False)
            except Exception as e:
                logger.error(f"Encoding failed: {e}")
        return None
