from ai.explainability.explanation_generator import ExplanationGenerator

_generator = ExplanationGenerator()


class LLMExplainer:
    """
    Explanation engine designed for LLM augmentation.
    Currently delegates to rule-based ExplanationGenerator.
    Future: send evidence context to an LLM (e.g., Gemini/GPT)
    and return a natural-language paragraph.
    """

    def explain(
        self,
        evidence_type: str,
        reason: str,
        confidence_delta: float,
        participant_id: str = None,
        context: dict = None,
    ) -> str:
        """
        Generate an explanation for a single evidence event.

        Args:
            evidence_type: e.g. 'camera_on', 'display_name'
            reason: Short machine reason string.
            confidence_delta: Signed confidence change.
            participant_id: Optional participant context.
            context: Optional extra context dict for future LLM prompt.

        Returns:
            Human-readable explanation string.
        """
        # TODO: When LLM integration is ready, build a prompt from
        # evidence_type, reason, confidence_delta, and context, then
        # call the LLM API here.

        return _generator.generate(
            evidence_type=evidence_type,
            reason=reason,
            confidence_delta=confidence_delta,
        )
