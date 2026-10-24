import os
import requests

class TeamsConnector:
    def __init__(self):
        self.webhook_url = os.getenv("TEAMS_WEBHOOK_URL", "")

    def send_notification(self, title: str, text: str) -> bool:
        if not self.webhook_url:
            print(f"[TeamsConnector] Webhook missing. Simulated notify: [{title}] {text}")
            return True

        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0078D7",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": "ATLAS Autonomous Notification",
                "text": text
            }]
        }

        try:
            res = requests.post(self.webhook_url, json=card, timeout=10)
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[TeamsConnector] Failed to notify Teams: {e}")
            return False
