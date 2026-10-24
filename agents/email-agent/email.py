from services.email import EmailService

class EmailAgent:
    def __init__(self):
        self.email_service = EmailService()

    def process_inbox(self) -> str:
        emails = self.email_service.fetch_emails()
        summary_lines = []
        for mail in emails:
            summary_lines.append(f"- From {mail['from']}: {mail['subject']}")
        
        summary = "\n".join(summary_lines)
        print(f"[EmailAgent] Inbox parsed. Summary generated:\n{summary}")
        return summary

    def prepare_reply(self, recipient: str, original_subject: str, reply_context: str) -> bool:
        subject = f"Re: {original_subject}"
        body = f"Hello,\n\n{reply_context}\n\nBest regards,\nAtlas"
        return self.email_service.send_email(recipient, subject, body)
