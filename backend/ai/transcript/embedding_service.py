import json
from typing import List
from utils.logger import logger
from models.embedding import TranscriptEmbedding
from repositories.embedding_repository import EmbeddingRepository


class TranscriptEmbeddingService:
    """
    Generates and persists embeddings for transcript chunks using
    HuggingFace sentence-transformers/all-MiniLM-L6-v2.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model_name = model_name
        self._model = None
        self.repository = EmbeddingRepository()

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of string chunks."""
        if not texts:
            return []
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return []

    def save_embedding(
        self,
        db,
        chunk_text: str,
        embedding_vector: List[float],
        participant_id: str,
        meeting_id: str = None,
        transcript_id: int = None,
    ) -> TranscriptEmbedding:
        """Persist a transcript chunk and its vector to database."""
        emb_obj = TranscriptEmbedding(
            transcript_id=transcript_id,
            participant_id=participant_id,
            meeting_id=meeting_id,
            chunk_text=chunk_text,
            embedding_vector=json.dumps(embedding_vector),
            model_name=self.model_name,
        )
        return self.repository.create(db, emb_obj)
