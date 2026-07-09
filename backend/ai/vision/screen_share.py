from typing import Optional


class ScreenShareAnalyzer:
    """
    Analyzes screen share content to infer candidate activity.
    Works in conjunction with BackgroundOCR and CodingActivityDetector.
    """

    def classify(self, ocr_text: Optional[str]) -> dict:
        """
        Classify the screen share content type from OCR text.

        Args:
            ocr_text: OCR-extracted text from the screen frame.

        Returns:
            {
                "content_type": "code" | "resume" | "browser" | "unknown",
                "confidence": float,
            }
        """
        if not ocr_text:
            return {"content_type": "unknown", "confidence": 0.0}

        lower = ocr_text.lower()

        code_signals = ["def ", "function", "import ", "class ", "return", "if ", "for "]
        resume_signals = ["experience", "education", "skills", "references"]
        browser_signals = ["http", "www.", "search", "google", "chrome"]

        code_score = sum(1 for s in code_signals if s in lower)
        resume_score = sum(1 for s in resume_signals if s in lower)
        browser_score = sum(1 for s in browser_signals if s in lower)

        scores = {
            "code": code_score,
            "resume": resume_score,
            "browser": browser_score,
        }

        best = max(scores, key=scores.get)

        if scores[best] == 0:
            return {"content_type": "unknown", "confidence": 0.0}

        total = sum(scores.values())
        confidence = round(scores[best] / total, 2)

        return {"content_type": best, "confidence": confidence}
