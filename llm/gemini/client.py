import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiAdapter:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.configured = True
        else:
            self.configured = False

    def generate(self, prompt: str, system_instruction: str = None, model: str = "gemini-1.5-flash") -> str:
        if not self.configured:
            return "Gemini API client not configured or google-generativeai package is missing."
        
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            contents=prompt,
            config=config if system_instruction else None
        )
        return response.text
