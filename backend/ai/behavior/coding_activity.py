from typing import List, Dict


class CodingActivityDetector:
    """
    Detects coding-related activity from screen share and transcript signals.
    Future: parse OCR text from screen shares for code patterns.
    """

    _CODE_KEYWORDS = [
        "function", "def ", "class ", "import ", "return",
        "if __name__", "console.log", "print(", "var ", "const ",
        "let ", "async ", "await ", "lambda", "yield",
    ]

    def detect_from_transcript(self, transcript_text: str) -> bool:
        """
        Check if transcript contains coding-related vocabulary.
        """
        lower = transcript_text.lower()
        return any(kw in lower for kw in self._CODE_KEYWORDS)

    def detect_from_ocr(self, ocr_text: str) -> Dict:
        """
        Analyze OCR-extracted screen text for code patterns.

        Returns:
            {"is_coding": bool, "keywords_found": List[str]}
        """
        lower = ocr_text.lower()
        found = [kw for kw in self._CODE_KEYWORDS if kw in lower]
        return {
            "is_coding": len(found) > 0,
            "keywords_found": found,
        }
