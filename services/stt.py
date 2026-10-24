import os

class SpeechToTextService:
    def __init__(self):
        self.model_path = os.getenv("WHISPER_MODEL_PATH", "base")
        self.model = None

    def initialize(self):
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(self.model_path, device="cpu", compute_type="int8")
            print("[STT] Faster-Whisper model loaded successfully.")
        except ImportError:
            print("[STT] faster-whisper package not installed. Operating in mock mode.")

    def transcribe(self, audio_file_path: str) -> str:
        if not self.model:
            self.initialize()
        
        if self.model:
            segments, info = self.model.transcribe(audio_file_path, beam_size=5)
            text = "".join([segment.text for segment in segments])
            return text
        else:
            return "Mock transcription: The user requested a system check."
