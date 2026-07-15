import asyncio
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import markdownify

CHROME_EXECUTABLE_PATH = os.environ.get(
    "CHROME_EXECUTABLE_PATH",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
)

TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")


def sanitize_filename(url: str) -> str:
    filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\-_]', '_', url)
    if len(filename) > 50:
        filename = filename[:50]
    return filename


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


async def run_tests():
    os.makedirs(TESTS_DIR, exist_ok=True)
    
    test_urls = [
        "https://www.example.com",
        "https://www.wikipedia.org",
        "https://www.baidu.com",
    ]

    print("=" * 60)
    print("      Credit-Scraper 核心功能测试")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for i, url in enumerate(test_urls, 1):
        print(f"测试 {i}: {url}")
        print("-" * 60)
        try:
            result = await scrape_to_markdown(url)
            
            output_data = {
                "url": url,
                "title": result["title"],
                "markdown_content": result["markdown"],
                "content_length": len(result["markdown"]),
                "scrape_time": asyncio.get_event_loop().time()
            }
            
            filename = f"{sanitize_filename(url)}.json"
            output_path = os.path.join(TESTS_DIR, filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 标题: {result['title']}")
            print(f"✅ 内容长度: {len(result['markdown'])} 字符")
            print(f"✅ 已保存到: {output_path}")
            print(f"✅ 内容预览:")
            preview = result['markdown'][:200].replace('\n', ' ')
            print(f"   {preview}..." if len(result['markdown']) > 200 else f"   {preview}")
            passed += 1
            
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            failed += 1
            
        print()

    print("=" * 60)
    print(f"测试结果: 通过 {passed} / 失败 {failed}")
    print(f"输出目录: {TESTS_DIR}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
