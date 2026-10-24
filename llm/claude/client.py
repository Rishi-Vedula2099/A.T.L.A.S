import os
try:
    import anthropic
except ImportError:
    anthropic = None

class ClaudeAdapter:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = anthropic.Client(api_key=self.api_key) if anthropic and self.api_key else None

    def generate(self, prompt: str, system_instruction: str = None, model: str = "claude-3-5-sonnet-20241022") -> str:
        if not self.client:
            return "Anthropic client is not configured or anthropic package is missing."
        
        # Simple completion request wrapper
        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_instruction or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
