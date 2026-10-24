from services.vision import VisionService

class VisionAgent:
    def __init__(self):
        self.vision_service = VisionService()

    def analyze_current_screen(self) -> str:
        print("[VisionAgent] Grabbing desktop active screen state...")
        img_path = self.vision_service.capture_screen()
        ocr_result = self.vision_service.extract_text(img_path)
        
        # Analyze layout structure or dispatch image to vision LLM (e.g. GPT-4o / Claude Vision)
        print(f"[VisionAgent] OCR content processed: {ocr_result}")
        return f"Screenshot analyzed. Key content: {ocr_result}"
