from services.teams import TeamsService

class TeamsAgent:
    def __init__(self):
        self.teams_service = TeamsService()

    def summarize_channel_updates(self, channel_id: str) -> str:
        messages = self.teams_service.fetch_channel_messages(channel_id)
        if not messages:
            return "No recent updates in channel."
            
        summary = f"Teams channel {channel_id} summary:\n"
        for msg in messages:
            summary += f"- {msg['sender']}: {msg['message']}\n"
        print(f"[TeamsAgent] Channel summary computed:\n{summary}")
        return summary
