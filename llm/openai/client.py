import os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIAdapter:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

    def generate(self, prompt: str, system_instruction: str = None, model: str = "gpt-4o") -> str:
        if not self.client:
            return "OpenAI client is not configured or open-ai dependency is missing."
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
