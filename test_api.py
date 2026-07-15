import httpx
import sys
import os
import json
import re

SCRAPER_URL = "http://localhost:9000"
TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")


def sanitize_filename(url: str) -> str:
    filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\-_]', '_', url)
    if len(filename) > 50:
        filename = filename[:50]
    return filename


def test_health():
    print("测试健康检查接口...")
    try:
        response = httpx.get(f"{SCRAPER_URL}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康状态: {data.get('status')}")
            print(f"✅ 服务名称: {data.get('service')}")
            return True
        else:
            print(f"❌ 健康检查失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False


def test_scrape_api():
    os.makedirs(TESTS_DIR, exist_ok=True)
    
    test_cases = [
        {"url": "https://www.example.com", "expected_title": "Example Domain"},
        {"url": "https://www.wikipedia.org", "expected_title": "Wikipedia"},
        {"url": "https://www.baidu.com", "expected_title": "百度一下，你就知道"}
    ]

    passed = 0
    failed = 0

    print("\n测试爬取接口...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['url']}")
        print("-" * 60)
        
        try:
            response = httpx.post(
                f"{SCRAPER_URL}/scrape",
                json={"url": test_case["url"]},
                timeout=30.0
            )
            
            if response.status_code == 200:
                response.encoding = "utf-8"
                data = response.json()
                
                filename = f"api_{sanitize_filename(test_case['url'])}.json"
                output_path = os.path.join(TESTS_DIR, filename)
                
                output_data = {
                    "url": data.get("url"),
                    "title": data.get("title"),
                    "markdown_content": data.get("markdown_content"),
                    "content_length": len(data.get("markdown_content", "")),
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ URL: {data.get('url')}")
                print(f"✅ 标题: {data.get('title')}")
                print(f"✅ 已保存到: {output_path}")
                
                if test_case['expected_title'] in data.get('title', ''):
                    print(f"✅ 标题验证通过")
                else:
                    print(f"⚠️ 标题不匹配: 期望 '{test_case['expected_title']}', 实际 '{data.get('title')}'")
                
                content_len = len(data.get('markdown_content', ''))
                print(f"✅ Markdown内容长度: {content_len} 字符")
                
                if content_len > 0:
                    preview = data['markdown_content'][:150].replace('\n', ' ')
                    print(f"✅ 内容预览: {preview}...")
                    passed += 1
                else:
                    print(f"❌ Markdown内容为空")
                    failed += 1
                    
            elif response.status_code == 500:
                error_detail = response.json().get('detail', '')
                print(f"❌ 爬取失败 (500): {error_detail}")
                failed += 1
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                failed += 1
                
        except httpx.ConnectError:
            print(f"❌ 无法连接到服务，请确保 Credit-Scraper 已启动并运行在 {SCRAPER_URL}")
            failed += 1
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            failed += 1

    return passed, failed


def main():
    print("=" * 60)
    print("      Credit-Scraper API 接口测试")
    print("=" * 60)
    print()

    print("注意: 请确保 Credit-Scraper 服务已启动在 http://localhost:9000")
    print()

    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ 健康检查失败，请检查服务是否启动")
        sys.exit(1)

    passed, failed = test_scrape_api()

    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed} / 失败 {failed}")
    print(f"输出目录: {TESTS_DIR}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
