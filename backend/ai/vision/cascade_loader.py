"""
Cascade Loader Utility
Resolves OpenCV Haar Cascade XML paths reliably across environments.
"""
import os
from typing import Optional


def get_cascade_path(xml_name: str) -> str:
    """
    Returns the absolute path to a Haar Cascade XML file.
    Checks local ai/vision/cascades first, then falls back to cv2.data.haarcascades.
    """
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cascades")
    local_path = os.path.join(local_dir, xml_name)
    if os.path.exists(local_path):
        return local_path

    try:
        import cv2
        cv_path = os.path.join(cv2.data.haarcascades, xml_name)
        if os.path.exists(cv_path):
            return cv_path
    except Exception:
        pass

    return local_path
