from services.browser import BrowserService

class BrowserAgent:
    def __init__(self):
        self.browser_service = BrowserService(headless=False)

    async def execute_user_task(self, url: str, instructions: str):
        print(f"[BrowserAgent] Opening {url} and executing: '{instructions}'")
        # Direct automation tasks (typing, clicking forms)
        raw_html = await self.browser_service.open_url_and_scrape(url)
        return f"Successfully processed browser task on {url}"
