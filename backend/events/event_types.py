from enum import Enum


class EventType(str, Enum):

    PARTICIPANT_JOINED = "participant_joined"

    PARTICIPANT_LEFT = "participant_left"

    DISPLAY_NAME_CHANGED = "display_name_changed"

    CAMERA_ON = "camera_on"

    CAMERA_OFF = "camera_off"

    MICROPHONE_ON = "microphone_on"

    MICROPHONE_OFF = "microphone_off"

    SCREEN_SHARE_STARTED = "screen_share_started"

    SCREEN_SHARE_STOPPED = "screen_share_stopped"

    SPEECH_STARTED = "speech_started"

    SPEECH_STOPPED = "speech_stopped"

    TRANSCRIPT_RECEIVED = "transcript_received"

    NETWORK_LAG = "network_lag"

    RECONNECTED = "reconnected"

    CONFIDENCE_UPDATED = "confidence_updated"