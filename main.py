import asyncio
import os
import sys

if sys.platform == "win32":
    os.system("chcp 65001 >nul")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import markdownify

CHROME_EXECUTABLE_PATH = os.environ.get(
    "CHROME_EXECUTABLE_PATH",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
)


async def lifespan(app):
    print("Credit-Scraper 服务启动中...")
    yield
    print("\nCredit-Scraper 服务正在关闭...")
    print("端口 9000 已释放")
    print("服务已优雅关闭")


app = FastAPI(
    title="Credit-Scraper Microservice",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="The target website URL to scrape.")


class ScrapeResponse(BaseModel):
    url: str
    title: str
    markdown_content: str


async def scrape_to_markdown(url: str) -> dict:
    async with async_playwright() as p:
        launch_options = {"headless": True}
        
        if os.path.exists(CHROME_EXECUTABLE_PATH):
            launch_options["executable_path"] = CHROME_EXECUTABLE_PATH
            launch_options["channel"] = None
        
        browser = await p.chromium.launch(**launch_options)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)

            title = await page.title()
            html_content = await page.content()

            soup = BeautifulSoup(html_content, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                element.decompose()

            body_html = str(soup.body) if soup.body else str(soup)
            markdown_text = markdownify.markdownify(body_html, heading_style="ATX")

            cleaned_markdown = "\n".join([line.strip() for line in markdown_text.splitlines() if line.strip()])

            return {"title": title, "markdown": cleaned_markdown}

        except Exception as e:
            print(f"Error occurred during scraping {url}: {str(e)}")
            raise e
        finally:
            await browser.close()


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(payload: ScrapeRequest):
    try:
        result = await scrape_to_markdown(payload.url)
        return ScrapeResponse(
            url=payload.url,
            title=result["title"],
            markdown_content=result["markdown"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "credit-scraper"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
