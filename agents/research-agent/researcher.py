from services.browser import BrowserService
from services.rag import RAGService

class ResearchAgent:
    def __init__(self):
        self.browser = BrowserService()
        self.rag = RAGService()

    async def conduct_research(self, topic: str) -> str:
        print(f"[ResearchAgent] Running deep research on: {topic}")
        # Check local documentation vector store
        local_context = self.rag.query_context(topic)
        # Search the web using browser agent context
        web_context = await self.browser.open_url_and_scrape(f"https://duckduckgo.com/?q={topic}")
        
        return f"Synthesized research: {local_context} | Web references retrieved."
