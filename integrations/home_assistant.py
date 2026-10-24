import os
import requests

class HomeAssistantIntegration:
    def __init__(self):
        self.base_url = os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123/api")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN", "")

    def trigger_service(self, domain: str, service: str, entity_id: str, data: dict = None) -> bool:
        if not self.token:
            print("[HomeAssistant] Token not configured. Simulated trigger successful.")
            return True
            
        url = f"{self.base_url}/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"entity_id": entity_id}
        if data:
            payload.update(data)

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[HomeAssistant] Request failed: {e}")
            return False
