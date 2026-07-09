from typing import List, Optional


class VoiceEmbedding:
    """
    Voice embedding extractor for speaker verification.
    Production: use SpeechBrain, resemblyzer, or a cloud voice API.
    This stub defines the interface.
    """

    def extract(self, audio_path: str) -> Optional[List[float]]:
        """
        Extract a voice embedding (d-vector) from an audio file.

        Args:
            audio_path: Path to the speaker's audio file.

        Returns:
            A list of floats representing the voice embedding,
            or None if extraction fails.

        Note:
            Stub — returns None. Replace with:
            from resemblyzer import VoiceEncoder
            encoder = VoiceEncoder()
            embed = encoder.embed_utterance(wav)
        """
        # TODO: integrate resemblyzer or SpeechBrain
        return None

    def similarity(
        self,
        embedding_a: List[float],
        embedding_b: List[float],
    ) -> float:
        """
        Cosine similarity between two voice embeddings.

        Returns:
            Similarity score in [-1, 1]. Values > 0.75 suggest same speaker.
        """
        if not embedding_a or not embedding_b:
            return 0.0

        dot = sum(a * b for a, b in zip(embedding_a, embedding_b))
        norm_a = sum(a ** 2 for a in embedding_a) ** 0.5
        norm_b = sum(b ** 2 for b in embedding_b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return round(dot / (norm_a * norm_b), 4)
