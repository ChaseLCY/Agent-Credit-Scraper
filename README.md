# Credit-Scraper 微服务

企业信贷风险多智能体系统的网页爬取微服务，基于 FastAPI + Playwright 构建，能够有效处理 JavaScript 动态渲染的网页。

## 功能特性

- 🚀 **无状态设计**: 不存储数据，不依赖数据库
- 🎭 **动态渲染支持**: 使用 Playwright + Chrome 处理 JavaScript 渲染页面
- 🧹 **内容清洗**: 自动清除脚本、样式、导航栏等干扰内容
- 📝 **Markdown 输出**: 输出干净的 Markdown 格式文本
- 🔌 **REST API**: 提供标准的 HTTP 接口供智能体系统调用

## 环境要求

- Python >= 3.13
- Google Chrome 浏览器（已安装在系统中）

## 安装与启动

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

### 2. 安装依赖

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 方式一：直接启动
.venv\Scripts\python.exe main.py

# 方式二：使用启动脚本
start.bat
```

服务默认运行在 `http://localhost:9000`

### 停止服务

使用 `Ctrl+C` 可优雅关闭服务，系统会自动：
- ✅ 释放端口 9000
- ✅ 关闭正在运行的 Chrome 浏览器进程
- ✅ 输出关闭日志

## 配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `CHROME_EXECUTABLE_PATH` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | Chrome 浏览器可执行文件路径 |

## API 接口

### 1. 健康检查

**GET** `/health`

检查服务运行状态。

**响应示例**:
```json
{
  "status": "healthy",
  "service": "credit-scraper"
}
```

### 2. 网页爬取

**POST** `/scrape`

爬取目标网页并返回 Markdown 内容。

**请求体**:
```json
{
  "url": "https://example.com/company-news"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | 目标网页 URL |

**成功响应** (200):
```json
{
  "url": "https://www.example.com",
  "title": "Example Domain",
  "markdown_content": "# Example Domain\nThis domain is for use in documentation examples..."
}
```

**失败响应** (500):
```json
{
  "detail": "Scraping failed: 错误详情"
}
```

## 测试方法

### 方式一：自动化测试脚本

项目提供了两个自动化测试脚本：

**1. 核心功能测试** (`test_scraper_core.py`)

直接测试爬虫核心逻辑，无需启动服务：

```bash
.venv\Scripts\python.exe test_scraper_core.py
```

测试内容：
- 爬取 `https://www.example.com`
- 爬取 `https://www.wikipedia.org`
- 验证标题和内容提取是否正常

**2. API 接口测试** (`test_api.py`)

测试 HTTP 接口，模拟智能体系统调用方式：

```bash
# 先启动服务
.venv\Scripts\python.exe main.py

# 新开终端运行测试
.venv\Scripts\python.exe test_api.py
```

测试内容：
- 健康检查接口 (`GET /health`)
- 爬取接口 (`POST /scrape`)
- 标题验证和内容完整性检查

### 方式二：PowerShell

```powershell
# 测试健康检查
Invoke-WebRequest -Uri "http://localhost:9000/health" -UseBasicParsing | Select-Object -ExpandProperty Content

# 测试网页爬取
$body = '{"url": "https://www.example.com"}'
Invoke-RestMethod -Uri "http://localhost:9000/scrape" -Method POST -ContentType "application/json" -Body $body
```

### 方式三：curl

```bash
# 测试健康检查
curl http://localhost:9000/health

# 测试网页爬取
curl -X POST http://localhost:9000/scrape -H "Content-Type: application/json" -d '{"url": "https://www.example.com"}'
```

### 方式四：浏览器访问

打开浏览器访问 `http://localhost:9000/docs` 查看交互式 API 文档。

### 测试脚本说明

| 文件 | 功能 | 是否需要启动服务 |
|------|------|------------------|
| `test_scraper_core.py` | 测试爬虫核心逻辑 | ❌ 不需要 |
| `test_api.py` | 测试 HTTP 接口 | ✅ 需要 |

## 智能体系统集成

该服务专为企业信贷风险多智能体系统设计，智能体系统已通过 `scraper_tool.py` 集成了调用接口。

### 启动顺序

**必须先启动 Credit-Scraper 服务，再启动智能体系统！**

1. **终端 1 - 启动 Credit-Scraper**:
   ```bash
   cd D:\desktop\爬虫服务\Credit_Scraper
   .venv\Scripts\python.exe main.py
   ```
   服务运行在 `http://localhost:9000`

2. **终端 2 - 启动智能体系统**:
   ```bash
   cd D:\desktop\CreditRisk_MultiAgent_ICBC\agent_risk
   .venv\Scripts\python.exe main.py
   ```
   服务运行在 `http://localhost:8000`

### 调用方式

智能体系统通过 `scraper_tool.py` 调用爬虫服务：

```python
from backend.tools.scraper_tool import scrape_web_page, check_scraper_health

# 检查服务状态
if check_scraper_health():
    print("Credit-Scraper 服务正常运行")

# 爬取网页
result = scrape_web_page("https://example.com/company-news")
print(result["title"])
print(result["markdown_content"])
```

### 集成文件说明

| 文件 | 路径 | 说明 |
|------|------|------|
| `scraper_tool.py` | `backend/tools/scraper_tool.py` | 爬虫工具封装 |
| `__init__.py` | `backend/tools/__init__.py` | 工具导出 |

智能体系统中的 `scrape_web_page()` 函数会自动调用 `http://localhost:9000/scrape` 接口获取网页内容。

## 项目结构

```
Credit_Scraper/
├── main.py              # 核心服务代码
├── test_scraper_core.py # 爬虫核心功能测试
├── test_api.py          # API 接口测试
├── pyproject.toml       # 项目配置
├── requirements.txt     # 依赖列表
├── start.bat            # Windows 启动脚本
├── .gitignore           # Git 忽略配置
├── .python-version      # Python 版本标识
└── README.md            # 本文件
```

## 技术栈

- **框架**: FastAPI 0.115+
- **服务器**: Uvicorn 0.34+
- **浏览器自动化**: Playwright 1.40+
- **HTML 解析**: BeautifulSoup4 4.12+
- **HTML 转 Markdown**: markdownify 0.12+
