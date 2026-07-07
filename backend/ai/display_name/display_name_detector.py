from ai.display_name.display_name_rules import COMMON_DEVICE_NAMES


class DisplayNameDetector:

    def detect(self, display_name: str):

        if display_name.strip() in COMMON_DEVICE_NAMES:

            return {
                "match": False,
                "reason": "Generic device name detected",
                "weight": -0.25,
            }

        return {
            "match": True,
            "reason": "Looks like a person's name",
            "weight": 0.10,
        }