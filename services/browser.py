import asyncio
try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

class BrowserService:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def open_url_and_scrape(self, url: str) -> str:
        if not async_playwright:
            print("[BrowserService] Playwright not installed. Mocking search.")
            return f"Mocked webpage content for {url}"
            
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
            return content
