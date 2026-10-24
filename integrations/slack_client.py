import os
import requests

class SlackClientIntegration:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    def post_message(self, text: str) -> bool:
        if not self.webhook_url:
            print(f"[SlackClient] Webhook url missing. Simulated post: '{text}'")
            return True
            
        payload = {"text": text}
        try:
            res = requests.post(self.webhook_url, json=payload, timeout=10)
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[SlackClient] Failed to send: {e}")
            return False
