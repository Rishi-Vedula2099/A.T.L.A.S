from services.memory import MemoryService
from services.graph_memory import GraphMemoryService

class MemoryAgent:
    def __init__(self):
        self.session_memory = MemoryService()
        self.graph_memory = GraphMemoryService()

    def process_and_commit_knowledge(self, session_id: str, user_name: str, message_content: str):
        print(f"[MemoryAgent] Parsing interaction for facts: '{message_content}'")
        # In a real environment, analyze sentence structure:
        # e.g., "I use Terraform for deploying chatbot services"
        # Extract fact: User -> USES -> Terraform
        
        self.session_memory.store_interaction(session_id, "user", message_content)
        
        # Simulated extraction and relationship commit
        self.graph_memory.add_relationship(user_name, "Terraform", "PREFERS")
        self.graph_memory.add_relationship(user_name, "Azure", "USES")
