class WhatsAppService:
    def __init__(self):
        pass

    def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        print(f"[WhatsAppService] Sending WhatsApp to {phone_number}: '{message}'")
        # Direct REST API POST to WhatsApp Business API
        return True

    def read_latest_chats(self) -> list:
        print("[WhatsAppService] Pulling latest conversation events...")
        return []
