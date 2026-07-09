WEIGHTS = {

    "display_name_match": 0.30,

    "display_name_changed": -0.25,

    "camera_on": 0.05,

    "camera_off": -0.08,

    "camera_never_on": -0.12,

    "screen_share_without_speaking": -0.07,

    "speech_analysis": 0.10,

    "speaking": 0.20,

    "long_answer": 0.18,

    "resume_shared": 0.12,

    "network_lag": -0.03,

    "similar_name": -0.05,

    "reconnect": -0.04,

    "disconnect": -0.06,

    "silent_observer": 0.00,

    "metadata_match": 0.35,

    "missing_metadata": -0.08,

    "joined_late": -0.10,

    "technical_answer": 0.15,

    "confident_speech": 0.12,

    "short_answer": -0.08,

    "long_silence": -0.10,

    "empty_transcript": -0.05,

    # ── Video AI ──────────────────────────────────────────────────────────
    "multiple_faces_detected":     -0.35,
    "eye_contact_maintained":       0.08,
    "eye_contact_avoided":         -0.06,
    "positive_emotion":             0.05,
    "negative_emotion":            -0.04,
    "gesture_active":               0.04,
    "suspicious_text_detected":    -0.15,
    "identity_inconsistency":      -0.30,
    "camera_evasion":              -0.10,
    "camera_position_stable":       0.03,
}