import os
import wave
import time
import threading
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from utils.logger import logger
from database.postgres import SessionLocal

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None
    np = None


class VBCableAudioService:
    """
    Live Windows VB-Audio Cable Capture Service.
    
    Step 1: Scans audio input devices for 'CABLE Output' (VB-Audio Virtual Cable)
            or any specified audio device index.
    Step 2: Captures live audio stream (both interviewer and candidate speaking
            in Google Meet routed via CABLE Input -> CABLE Output).
    Step 3: Automatically buffers and writes .wav chunks every N seconds
            and sends them to AudioService.process_audio_upload() for live
            transcription, diarization, evidence collection, and WebSocket broadcast.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VBCableAudioService, cls).__new__(cls)
                cls._instance._init_service()
            return cls._instance

    def _init_service(self):
        self.is_capturing: bool = False
        self.current_meeting_id: Optional[str] = None
        self.current_participant_id: Optional[str] = None
        self.device_index: Optional[int] = None
        self.device_name: str = "Not Connected"
        self.chunks_processed: int = 0
        self.chunk_seconds: int = 10
        self.sample_rate: int = 16000
        self.channels: int = 1
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.audio_buffer: List = []

    def list_devices(self) -> Dict:
        """
        List all available audio input devices and identify VB-Audio Cable.
        Equivalent to:
            for i, dev in enumerate(sd.query_devices()):
                if 'CABLE Output' in dev['name']: ...
        """
        if not SOUNDDEVICE_AVAILABLE:
            return {
                "sounddevice_available": False,
                "devices": [],
                "vb_cable_index": None,
                "vb_cable_name": None,
                "message": "Python sounddevice package is not installed. Run: pip install sounddevice numpy"
            }

        try:
            devices_info = sd.query_devices()
            input_devices = []
            vb_index = None
            vb_name = None

            for i, dev in enumerate(devices_info):
                max_in = dev.get("max_input_channels", 0)
                name = dev.get("name", "")
                if max_in > 0:
                    is_vb = ("CABLE OUTPUT" in name.upper() or "VB-AUDIO" in name.upper() or "CABLE" in name.upper())
                    dev_data = {
                        "index": i,
                        "name": name,
                        "channels": max_in,
                        "sample_rate": int(dev.get("default_samplerate", 16000)),
                        "is_vb_cable": is_vb
                    }
                    input_devices.append(dev_data)
                    if is_vb and vb_index is None:
                        vb_index = i
                        vb_name = name

            return {
                "sounddevice_available": True,
                "devices": input_devices,
                "vb_cable_index": vb_index,
                "vb_cable_name": vb_name,
                "message": f"Found VB-Cable at index {vb_index}: {vb_name}" if vb_index is not None else "VB-Cable not found. Using system default input device."
            }
        except Exception as e:
            logger.error(f"Error querying audio devices: {e}")
            return {
                "sounddevice_available": True,
                "devices": [],
                "vb_cable_index": None,
                "vb_cable_name": None,
                "message": f"Error querying devices: {str(e)}"
            }

    def start_capture(
        self,
        meeting_id: str,
        participant_id: str,
        device_index: Optional[int] = None,
        chunk_seconds: int = 10,
    ) -> Dict:
        """
        Start background audio capture from VB-Audio Cable or selected device index.
        """
        if self.is_capturing:
            return {
                "status": "already_capturing",
                "message": f"Audio capture is already running on device {self.device_name}",
                "meeting_id": self.current_meeting_id,
                "device_index": self.device_index,
            }

        if not SOUNDDEVICE_AVAILABLE:
            return {
                "status": "error",
                "message": "sounddevice package not available on server. Install via pip install sounddevice numpy"
            }

        device_info = self.list_devices()
        selected_index = device_index

        if selected_index is None:
            selected_index = device_info.get("vb_cable_index")
            if selected_index is None and len(device_info.get("devices", [])) > 0:
                selected_index = device_info["devices"][0]["index"]

        selected_name = "Default Input"
        for d in device_info.get("devices", []):
            if d["index"] == selected_index:
                selected_name = d["name"]
                break

        self.current_meeting_id = meeting_id
        self.current_participant_id = participant_id
        self.device_index = selected_index
        self.device_name = selected_name
        self.chunk_seconds = chunk_seconds
        self.chunks_processed = 0
        self._stop_event.clear()

        self._capture_thread = threading.Thread(
            target=self._run_capture_loop,
            daemon=True,
            name=f"VBCableCapture-{meeting_id}"
        )
        self.is_capturing = True
        self._capture_thread.start()

        logger.info(f"Started live VB-Audio Cable capture on index {selected_index} ({selected_name}) for meeting {meeting_id}")

        return {
            "status": "started",
            "message": f"Listening to Google Meet audio via '{selected_name}' (Index {selected_index})",
            "meeting_id": meeting_id,
            "participant_id": participant_id,
            "device_index": selected_index,
            "device_name": selected_name,
        }

    def stop_capture(self) -> Dict:
        """
        Stop live audio capture.
        """
        if not self.is_capturing:
            return {
                "status": "stopped",
                "message": "Capture was not active.",
                "chunks_processed": self.chunks_processed
            }

        self._stop_event.set()
        self.is_capturing = False

        logger.info(f"Stopped VB-Audio Cable capture. Total chunks processed: {self.chunks_processed}")

        return {
            "status": "stopped",
            "message": "VB-Audio Cable capture stopped cleanly.",
            "chunks_processed": self.chunks_processed,
            "device_name": self.device_name,
        }

    def get_status(self) -> Dict:
        """Get current live capture status."""
        return {
            "is_capturing": self.is_capturing,
            "meeting_id": self.current_meeting_id,
            "participant_id": self.current_participant_id,
            "device_index": self.device_index,
            "device_name": self.device_name,
            "chunks_processed": self.chunks_processed,
            "chunk_seconds": self.chunk_seconds,
            "sounddevice_available": SOUNDDEVICE_AVAILABLE,
        }

    def _run_capture_loop(self):
        """Background thread running sounddevice InputStream and processing audio chunks."""
        from services.audio_service import AudioService
        audio_service = AudioService()

        upload_dir = os.path.join("uploads", "audio")
        os.makedirs(upload_dir, exist_ok=True)

        frames_per_chunk = int(self.sample_rate * self.chunk_seconds)
        buffer = []

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"VB-Cable capture status: {status}")
            buffer.append(indata.copy())

        try:
            with sd.InputStream(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
                dtype="int16"
            ):
                while not self._stop_event.is_set():
                    time.sleep(1.0)
                    total_frames = sum(b.shape[0] for b in buffer)
                    if total_frames >= frames_per_chunk:
                        chunk_data = np.concatenate(buffer[:], axis=0)
                        buffer.clear()

                        # Write to temporary .wav file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"live_vb_{self.current_participant_id}_{timestamp}.wav"
                        filepath = os.path.join(upload_dir, filename)

                        with wave.open(filepath, "wb") as wf:
                            wf.setnchannels(self.channels)
                            wf.setsampwidth(2)  # 16-bit
                            wf.setframerate(self.sample_rate)
                            wf.writeframes(chunk_data.tobytes())

                        self.chunks_processed += 1
                        logger.info(f"VB-Cable chunk #{self.chunks_processed} saved: {filename} ({len(chunk_data)} frames)")

                        # Process via AudioService in a fresh database session
                        db = SessionLocal()
                        try:
                            # Run async process_audio_upload via sync wrapper or asyncio run
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(
                                    audio_service.process_audio_upload(
                                        db=db,
                                        meeting_id=self.current_meeting_id,
                                        participant_id=self.current_participant_id or "candidate_001",
                                        file_path=filepath,
                                        file_name=filename,
                                        file_format="wav",
                                    )
                                )
                            finally:
                                loop.close()
                        except Exception as proc_e:
                            logger.error(f"Error processing VB-Cable audio chunk: {proc_e}")
                        finally:
                            db.close()

        except Exception as e:
            logger.error(f"Error in VB-Cable live capture thread: {e}")
        finally:
            self.is_capturing = False


vb_cable_service = VBCableAudioService()
