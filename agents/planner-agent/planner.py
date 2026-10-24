class PlannerAgent:
    def __init__(self):
        pass

    def build_dag_plan(self, query: str) -> list:
        print(f"[PlannerAgent] Processing goal: '{query}'")
        # Breaks prompt request into a structured graph sequence
        return [
            {"id": "task_1", "description": "Glean information", "agent": "researcher"},
            {"id": "task_2", "description": "Write and deploy code", "agent": "coder", "deps": ["task_1"]}
        ]
