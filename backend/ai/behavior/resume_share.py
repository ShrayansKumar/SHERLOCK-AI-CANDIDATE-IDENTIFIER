class ResumeShareDetector:
    """
    Detects resume sharing behaviour from screen share events
    and OCR-extracted text.
    """

    _RESUME_KEYWORDS = [
        "experience", "education", "skills", "summary",
        "objective", "references", "certifications",
        "curriculum vitae", "cv", "resume",
    ]

    def detect_from_ocr(self, ocr_text: str) -> bool:
        """
        Return True if OCR text looks like a resume.
        """
        lower = ocr_text.lower()
        matches = sum(1 for kw in self._RESUME_KEYWORDS if kw in lower)
        return matches >= 3

    def confidence_delta(self, detected: bool) -> float:
        """
        Return the confidence delta for resume sharing evidence.
        Positive if resume detected (sharing own screen like candidate),
        neutral if not.
        """
        return 0.12 if detected else 0.0
