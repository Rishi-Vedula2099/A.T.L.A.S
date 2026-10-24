import os
import requests

class WhatsAppAPIIntegration:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

    def send_text_message(self, recipient_phone: str, text: str) -> bool:
        if not self.access_token or not self.phone_number_id:
            print(f"[WhatsAppAPI] Credentials missing. Simulated msg to {recipient_phone}: '{text}'")
            return True

        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {"body": text}
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[WhatsAppAPI] API call failed: {e}")
            return False
