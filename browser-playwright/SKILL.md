---
name: browser-playwright
description: Browser automation skill using Playwright for direct control of Chrome/Chromium browsers. Capabilities: navigate to URLs, click elements, fill forms, take screenshots, extract text, handle QR codes, wait for elements, execute JavaScript. Use when user mentions "browser automation", "playwright", "click button", "screenshot", "login", "authorization", or needs programmatic browser control without MCP tools dependency.
version: 1.0.0
---

# Browser Playwright Skill

你是一名浏览器自动化专家，使用 Playwright 直接控制浏览器完成任务。

## 核心能力

### 1. 基础操作
- **导航**: 访问 URL，前进后退
- **点击**: 定位并点击元素（按钮、链接等）
- **输入**: 填写表单、文本输入
- **截图**: 全屏截图、元素截图
- **等待**: 等待元素出现、等待页面加载

### 2. 高级操作
- **提取文本**: 获取页面元素文本
- **执行 JS**: 执行自定义 JavaScript 代码
- **处理弹窗**: 处理 alerts, confirms, prompts
- **下载文件**: 触发并等待文件下载
- **Cookie 管理**: 获取、设置、删除 cookies

### 3. 二维码处理 ⭐
- **定位二维码**: 自动识别页面中的二维码元素
- **截图二维码**: 截取二维码区域并保存
- **通知用户**: 提示用户扫描二维码

### 4. 授权流程 ⭐
- **点击授权按钮**: 定位并点击"授权"、"同意"等按钮
- **登录辅助**: 填写账号密码（需用户提供）
- **验证码处理**: 截图验证码，等待用户输入

## 使用流程

### 步骤 1: 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 步骤 2: 编写脚本

使用 `scripts/browser_actions.py` 中的函数：

```python
from scripts.browser_actions import BrowserController

# 创建控制器
browser = BrowserController(headless=False)  # headless=True 无头模式

# 执行操作
browser.navigate("https://example.com")
browser.click("#submit-button")
browser.fill("#username", "user123")
browser.screenshot("output/screenshot.png")

# 关闭浏览器
browser.close()
```

### 步骤 3: 执行脚本

```bash
python scripts/browser_actions.py
```

## 常用函数

### BrowserController 类

```python
class BrowserController:
    def __init__(self, headless=False, browser_type="chromium"):
        """初始化浏览器控制器"""

    def navigate(self, url):
        """导航到指定 URL"""

    def click(self, selector, timeout=5000):
        """点击元素"""

    def fill(self, selector, text):
        """填写表单"""

    def screenshot(self, path, selector=None):
        """截图，可指定元素"""

    def get_text(self, selector):
        """获取元素文本"""

    def wait_for(self, selector, timeout=30000):
        """等待元素出现"""

    def execute_script(self, script):
        """执行 JavaScript"""

    def close(self):
        """关闭浏览器"""
```

## 定位策略

### 选择器优先级
1. **CSS 选择器**: `#id`, `.class`, `[attr="value"]`
2. **XPath**: `//div[@class="xxx"]`
3. **文本**: `text="登录"`
4. **组合选择器**: `button >> text="提交"`

### 示例
```python
# CSS 选择器
browser.click("#submit-btn")
browser.fill("input[name='email']", "user@example.com")

# XPath
browser.click("//button[contains(text(), '授权')]")

# 文本定位
browser.click("text=同意并继续")

# 组合
browser.click(".modal >> text=确定")
```

## 典型场景

### 场景 1: 授权登录
```python
# 打开授权页面
browser.navigate("https://auth.example.com/authorize")

# 点击授权按钮
browser.click("text=同意授权")

# 等待授权完成
browser.wait_for(".success-message")

# 截图确认
browser.screenshot("temp/auth_success.png")
```

### 场景 2: 扫码登录
```python
# 打开登录页
browser.navigate("https://example.com/login")

# 等待二维码出现
browser.wait_for("img.qrcode")

# 截图二维码
browser.screenshot("temp/qrcode.png", selector="img.qrcode")

print("请扫描二维码登录，然后告诉我继续...")
```

### 场景 3: 表单填写
```python
browser.navigate("https://example.com/form")
browser.fill("#name", "张三")
browser.fill("#email", "zhangsan@example.com")
browser.select("#country", "China")
browser.click("text=提交")
```

## 输出位置

遵循文件流转协议：
- **截图**: `temp/` 目录
- **日志**: `temp/` 目录
- **提取数据**: `output/YYYY-MM-DD_data.json` 或 `output/YYYY-MM-DD_data.csv`

## 最佳实践

1. **非无头模式**: 涉及扫码、验证码时使用 `headless=False`
2. **等待策略**: 使用 `wait_for()` 而不是 `sleep()`
3. **错误处理**: 捕获异常并给出清晰提示
4. **资源清理**: 始终调用 `close()` 释放资源
5. **日志记录**: 记录关键操作到 `temp/browser.log`

## 错误处理

```python
try:
    browser.click("#submit")
except Exception as e:
    print(f"点击失败: {e}")
    browser.screenshot("temp/error.png")
    raise
```

## 注意事项

- 不依赖 MCP 工具，完全独立的浏览器控制
- 使用 Chromium 浏览器（默认安装）
- 支持自定义 User-Agent
- 支持代理设置

## 参考资源

- Playwright 官方文档: https://playwright.dev/python/
- CSS 选择器参考: [references/css-selectors.md](references/css-selectors.md)
- XPath 指南: [references/xpath-guide.md](references/xpath-guide.md)
