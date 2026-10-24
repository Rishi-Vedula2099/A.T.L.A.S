class EmailService:
    def __init__(self):
        pass

    def fetch_emails(self, limit: int = 5) -> list:
        print(f"[EmailService] Fetching the latest {limit} emails...")
        return [
            {"from": "manager@company.com", "subject": "Review Code", "body": "Please review branch main."},
            {"from": "cloud-alerts@azure.com", "subject": "Resource Usage", "body": "Azure chatbot service exceeds metrics."}
        ]

    def send_email(self, to: str, subject: str, body: str) -> bool:
        print(f"[EmailService] Sending email to {to} with subject '{subject}'")
        # Ingestion API calls here
        return True
