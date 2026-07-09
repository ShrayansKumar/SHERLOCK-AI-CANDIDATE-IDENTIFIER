class LLMReasoner:
    """
    LLM-powered transcript reasoner.
    Analyzes transcript segments for:
    - Answer quality scoring
    - Relevance to the question
    - Technical depth estimation

    Currently returns rule-based heuristics.
    Future: send transcript context to Gemini/GPT for deep analysis.
    """

    def reason(
        self,
        question: str,
        answer: str,
    ) -> dict:
        """
        Evaluate an answer against a question.

        Args:
            question: The interview question text.
            answer: The candidate's answer text.

        Returns:
            {
                "relevance": float [0,1],
                "depth": "shallow" | "medium" | "deep",
                "word_count": int,
            }
        """
        # TODO: build LLM prompt and call API
        # prompt = f"Q: {question}\nA: {answer}\nRate relevance 0-1 and depth."

        word_count = len(answer.strip().split())
        q_words = set(question.lower().split())
        a_words = set(answer.lower().split())
        overlap = len(q_words & a_words)
        relevance = round(min(1.0, overlap / max(len(q_words), 1)), 2)

        if word_count > 60:
            depth = "deep"
        elif word_count > 20:
            depth = "medium"
        else:
            depth = "shallow"

        return {
            "relevance": relevance,
            "depth": depth,
            "word_count": word_count,
        }
