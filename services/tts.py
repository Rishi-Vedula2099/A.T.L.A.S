import os

class TextToSpeechService:
    def __init__(self, mode: str = "friendly"):
        self.mode = mode
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")

    def speak(self, text: str, output_path: str = "response.wav") -> str:
        print(f"[TTS] Synthesizing voice in mode [{self.mode}]: '{text}'")
        if self.elevenlabs_api_key:
            return self._speak_elevenlabs(text, output_path)
        else:
            return self._speak_local_xtts(text, output_path)

    def _speak_elevenlabs(self, text: str, output_path: str) -> str:
        print("[TTS] Running cloud ElevenLabs voice synthesis.")
        # ElevenLabs generation logic goes here
        return output_path

    def _speak_local_xtts(self, text: str, output_path: str) -> str:
        print("[TTS] Running local XTTS synthesizer fallback.")
        # Local XTTS/Coqui generation logic goes here
        return output_path
