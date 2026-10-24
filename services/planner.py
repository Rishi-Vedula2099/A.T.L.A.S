from typing import List, Dict, Any

class PlannerService:
    def __init__(self):
        pass

    def create_plan(self, user_prompt: str) -> List[Dict[str, Any]]:
        print(f"[Planner] Designing task roadmap for request: '{user_prompt}'")
        # Example dynamic parser planning logic
        plan = [
            {"step": 1, "task": "research_topic", "agent": "researcher"},
            {"step": 2, "task": "generate_code", "agent": "coder"}
        ]
        return plan
