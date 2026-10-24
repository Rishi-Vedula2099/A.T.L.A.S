import os

class WakewordService:
    def __init__(self):
        self.porcupine_key = os.getenv("PORCUPINE_ACCESS_KEY", "")
        self.running = False

    def start_listening(self, callback):
        self.running = True
        print("[Wakeword] Listening for 'Hey Atlas'...")
        
        # In actual run loop:
        # if wakephrase_detected: callback()
        
    def stop_listening(self):
        self.running = False
        print("[Wakeword] Stopped background listening.")
