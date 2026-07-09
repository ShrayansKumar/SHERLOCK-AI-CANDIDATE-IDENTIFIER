from ai.display_name.display_name_detector import DisplayNameDetector
from ai.display_name.display_name_rules import COMMON_DEVICE_NAMES


class DisplayNameAnalyzer:
    """
    Full analysis of a participant's display name — combines detection,
    rules, and history to produce a rich analysis dict.
    """

    def __init__(self):
        self._detector = DisplayNameDetector()

    def analyze(self, display_name: str) -> dict:
        """
        Full analysis of a display name.

        Returns:
            {
                "display_name": str,
                "is_person_name": bool,
                "is_device_name": bool,
                "reason": str,
                "confidence_delta": float,
            }
        """
        result = self._detector.detect(display_name)
        is_device = display_name.strip() in COMMON_DEVICE_NAMES

        return {
            "display_name": display_name,
            "is_person_name": result["match"],
            "is_device_name": is_device,
            "reason": result["reason"],
            "confidence_delta": result["weight"],
        }
