class TeamsService:
    def __init__(self):
        pass

    def fetch_channel_messages(self, channel_id: str) -> list:
        print(f"[TeamsService] Gathering updates from channel: {channel_id}")
        return [
            {"sender": "Lead Dev", "message": "Deploying the dashboard to production tomorrow."}
        ]

    def post_message(self, channel_id: str, message: str) -> bool:
        print(f"[TeamsService] Posting message to channel {channel_id}: '{message}'")
        return True
