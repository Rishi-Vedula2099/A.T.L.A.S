import os
import sys
import time
import asyncio

# The agent folders use hyphens in their names, which are not importable as
# dotted modules. Add the folder to sys.path and import the flat module name,
# matching the pattern used in server.py.
_AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
sys.path.append(os.path.join(_AGENT_ROOT, "orchestrator-agent"))

from orchestrator import OrchestratorAgent  # noqa: E402


class TaskScheduler:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.running = False

    async def schedule_recurring_task(self, query: str, interval_seconds: int):
        self.running = True
        print(f"[Scheduler] Registered recurring run for '{query}' every {interval_seconds}s")
        while self.running:
            print(f"[Scheduler] Dispatching trigger check for query: '{query}'")
            # In actual implementation: run the orchestrator graph asynchronously
            # await self.orchestrator.run(query)
            await asyncio.sleep(interval_seconds)

    def stop(self):
        self.running = False
        print("[Scheduler] Intercepted shutdown. Stopped runner loop.")
