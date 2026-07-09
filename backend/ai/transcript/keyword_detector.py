from typing import List, Dict


class KeywordDetector:
    """
    Detects domain-relevant keywords in transcript text.
    Used to infer candidate expertise and validate role fit.
    """

    _TECH_KEYWORDS = [
        "algorithm", "data structure", "api", "database", "sql",
        "python", "javascript", "typescript", "react", "fastapi",
        "docker", "kubernetes", "cloud", "aws", "gcp", "azure",
        "machine learning", "neural network", "gradient", "backprop",
        "recursion", "binary search", "hash map", "linked list",
        "time complexity", "big o", "rest", "graphql", "microservice",
    ]

    _SOFT_KEYWORDS = [
        "collaboration", "teamwork", "leadership", "communication",
        "problem solving", "deadline", "agile", "scrum", "sprint",
        "stakeholder", "cross-functional", "initiative",
    ]

    def detect(self, text: str) -> Dict:
        """
        Detect technical and soft-skill keywords in text.

        Returns:
            {
                "tech_keywords": List[str],
                "soft_keywords": List[str],
                "tech_count": int,
                "soft_count": int,
            }
        """
        lower = text.lower()
        tech_found = [kw for kw in self._TECH_KEYWORDS if kw in lower]
        soft_found = [kw for kw in self._SOFT_KEYWORDS if kw in lower]

        return {
            "tech_keywords": tech_found,
            "soft_keywords": soft_found,
            "tech_count": len(tech_found),
            "soft_count": len(soft_found),
        }
