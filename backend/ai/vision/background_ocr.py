"""
Background OCR
Extracts text visible in video frames using pytesseract.
Falls back to an OpenCV text-region heuristic when tesseract is not installed.

Use cases:
  - Detect cheat-sheets / notes in the background
  - Detect second monitor content being read
  - Detect suspicious text on screen during screen share
"""
from typing import List, Dict, Optional
import numpy as np

# Keywords that raise suspicion (candidate reading answers)
_SUSPICIOUS_KEYWORDS = [
    "answer", "solution", "code", "def ", "class ", "import ",
    "function", "return", "algorithm", "leetcode", "hackerrank",
    "geeksforgeeks", "stackoverflow", "python", "javascript",
]


class BackgroundOCR:
    """
    Extracts and analyses text from video frames.
    """

    def _extract_frame_tesseract(self, frame: np.ndarray) -> Optional[str]:
        try:
            import cv2
            import pytesseract
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Upscale for better OCR accuracy
            scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
            text = pytesseract.image_to_string(scaled, config="--psm 11")
            return text.strip() if text.strip() else None
        except Exception:
            return None

    def _detect_text_regions_heuristic(self, frame: np.ndarray) -> Optional[Dict]:
        """
        OpenCV MSER text-region detector as a fallback.
        Returns approximate count of text-like regions.
        """
        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            region_count = len(regions)
            # A high number of MSER regions suggests lots of text
            text_likely = region_count > 200
            return {
                "text_region_count": region_count,
                "text_likely": text_likely,
                "backend": "heuristic",
            }
        except Exception:
            return None

    def analyze_frames(
        self,
        frames: List[np.ndarray],
        sample_every_n: int = 5,
    ) -> Dict:
        """
        Run OCR on every Nth frame (OCR is expensive).

        Returns:
            {
                "backend": str,
                "frames_with_text": int,
                "suspicious_text_detected": bool,
                "suspicious_keywords_found": list[str],
                "sample_texts": list[str],  # first 3 non-empty
            }
        """
        frames_with_text = 0
        suspicious_keywords: List[str] = []
        sample_texts: List[str] = []
        backend = "none"

        for i, frame in enumerate(frames):
            if i % sample_every_n != 0:
                continue

            text = self._extract_frame_tesseract(frame)
            if text is not None:
                backend = "tesseract"
                frames_with_text += 1
                lower = text.lower()
                found = [kw for kw in _SUSPICIOUS_KEYWORDS if kw in lower]
                suspicious_keywords.extend(found)
                if len(sample_texts) < 3:
                    sample_texts.append(text[:200])
            else:
                # Fallback: count text regions
                heuristic = self._detect_text_regions_heuristic(frame)
                if heuristic and heuristic.get("text_likely"):
                    frames_with_text += 1
                    if backend == "none":
                        backend = "heuristic"

        unique_keywords = list(dict.fromkeys(suspicious_keywords))

        return {
            "backend": backend,
            "frames_with_text": frames_with_text,
            "suspicious_text_detected": len(unique_keywords) > 0,
            "suspicious_keywords_found": unique_keywords[:10],
            "sample_texts": sample_texts,
        }
