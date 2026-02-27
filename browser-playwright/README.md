# Browser Playwright Skill

独立的浏览器自动化技能，使用 Playwright 直接控制 Chrome/Chromium 浏览器。

## 功能特性

- ✅ 直接控制浏览器，不依赖 MCP 工具
- ✅ 点击授权按钮
- ✅ 截屏二维码
- ✅ 填写表单
- ✅ 页面截图
- ✅ 提取文本
- ✅ 执行 JavaScript

## 安装

### 1. 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 2. 验证安装

```bash
python -m playwright install --help
python scripts/browser_actions.py --help
```

## 使用方法

### 方式一：Python API

```python
import asyncio
from scripts.browser_actions import BrowserController

async def main():
    browser = BrowserController(headless=False)
    try:
        await browser.start()
        await browser.navigate("https://example.com")
        await browser.click("text=登录")
        await browser.screenshot("temp/screenshot.png")
    finally:
        await browser.close()

asyncio.run(main())
```

### 方式二：命令行

```bash
# 截图
python scripts/browser_actions.py screenshot --url https://example.com --output temp/screenshot.png

# 点击按钮
python scripts/browser_actions.py click --url https://example.com --selector "text=授权"

# 截取二维码
python scripts/browser_actions.py qrcode --url https://example.com --output temp/qrcode.png
```

## 典型场景

### 授权登录

```python
browser = BrowserController(headless=False)
await browser.start()
await browser.navigate("https://auth.example.com")
await browser.click("text=同意授权")
```

### 扫码登录

```python
browser = BrowserController(headless=False)
await browser.start()
await browser.navigate("https://example.com/login")
await browser.wait_for("img.qrcode")
await browser.screenshot("temp/qrcode.png", selector="img.qrcode")
```

## 目录结构

```
browser-playwright/
├── SKILL.md              # 技能定义文件
├── scripts/
│   └── browser_actions.py  # 核心脚本
├── references/
│   ├── css-selectors.md    # CSS 选择器参考
│   └── xpath-guide.md      # XPath 指南
└── README.md              # 本文件
```

## 注意事项

1. **非无头模式**: 涉及扫码、验证码时使用 `headless=False`
2. **选择器**: 优先使用稳定的 ID、name 属性，避免动态类名
3. **等待策略**: 使用 `wait_for()` 而不是 `sleep()`
4. **资源清理**: 始终调用 `close()` 释放资源

## 参考资源

- [Playwright 官方文档](https://playwright.dev/python/)
- [CSS 选择器参考](references/css-selectors.md)
- [XPath 指南](references/xpath-guide.md)
