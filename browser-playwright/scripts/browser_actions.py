#!/usr/bin/env python3
"""
Browser Playwright Actions
独立的浏览器自动化工具，不依赖 MCP 工具
"""

import os
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Locator


class BrowserController:
    """浏览器控制器 - 封装 Playwright 核心功能"""

    def __init__(self, headless: bool = False, browser_type: str = "chromium"):
        """
        初始化浏览器控制器

        Args:
            headless: 是否无头模式（False 会显示浏览器窗口）
            browser_type: 浏览器类型 (chromium, firefox, webkit)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()

        browser_map = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }

        browser_launcher = browser_map.get(self.browser_type, self.playwright.chromium)
        self.browser = await browser_launcher.launch(headless=self.headless)
        self.page = await self.browser.new_page()

        # 设置视口大小
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

    async def navigate(self, url: str):
        """
        导航到指定 URL

        Args:
            url: 目标网址
        """
        if not self.page:
            raise RuntimeError("浏览器未启动，请先调用 start()")
        await self.page.goto(url, wait_until="networkidle")

    async def click(self, selector: str, timeout: int = 5000):
        """
        点击元素

        Args:
            selector: CSS 选择器或 XPath
            timeout: 超时时间（毫秒）
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.wait_for_selector(selector, timeout=timeout)
        await self.page.click(selector)

    async def fill(self, selector: str, text: str):
        """
        填写表单

        Args:
            selector: CSS 选择器或 XPath
            text: 要填写的文本
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.fill(selector, text)

    async def select(self, selector: str, value: str):
        """
        选择下拉框选项

        Args:
            selector: CSS 选择器
            value: 选项值
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.select_option(selector, value)

    async def screenshot(self, path: str, selector: Optional[str] = None):
        """
        截图

        Args:
            path: 保存路径
            selector: 元素选择器（可选，如果指定则只截取该元素）
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if selector:
            element = await self.page.query_selector(selector)
            if element:
                await element.screenshot(path=path)
            else:
                raise ValueError(f"未找到元素: {selector}")
        else:
            await self.page.screenshot(path=path, full_page=True)

    async def get_text(self, selector: str) -> str:
        """
        获取元素文本

        Args:
            selector: CSS 选择器或 XPath

        Returns:
            元素文本内容
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        element = await self.page.query_selector(selector)
        if element:
            return await element.inner_text()
        return ""

    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        获取元素属性

        Args:
            selector: CSS 选择器或 XPath
            attribute: 属性名

        Returns:
            属性值
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        element = await self.page.query_selector(selector)
        if element:
            return await element.get_attribute(attribute)
        return None

    async def wait_for(self, selector: str, timeout: int = 30000):
        """
        等待元素出现

        Args:
            selector: CSS 选择器或 XPath
            timeout: 超时时间（毫秒）
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.wait_for_selector(selector, timeout=timeout)

    async def execute_script(self, script: str):
        """
        执行 JavaScript 代码

        Args:
            script: JavaScript 代码

        Returns:
            执行结果
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        return await self.page.evaluate(script)

    async def get_page_content(self) -> str:
        """
        获取页面完整 HTML 内容

        Returns:
            HTML 字符串
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        return await self.page.content()

    async def wait_for_navigation(self, timeout: int = 30000):
        """
        等待页面导航完成

        Args:
            timeout: 超时时间（毫秒）
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.wait_for_load_state("networkidle", timeout=timeout)

    async def scroll_to_bottom(self):
        """滚动到页面底部"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# 便捷函数

async def quick_screenshot(url: str, output_path: str, headless: bool = True):
    """
    快速截取网页截图

    Args:
        url: 网页地址
        output_path: 输出路径
        headless: 是否无头模式
    """
    controller = BrowserController(headless=headless)
    try:
        await controller.start()
        await controller.navigate(url)
        await controller.screenshot(output_path)
    finally:
        await controller.close()


async def click_authorization_button(url: str, button_selector: str = "text=授权"):
    """
    点击授权按钮（登录流程）

    Args:
        url: 授权页面地址
        button_selector: 按钮选择器

    Returns:
        是否成功点击
    """
    controller = BrowserController(headless=False)
    try:
        await controller.start()
        await controller.navigate(url)
        await controller.click(button_selector)
        return True
    except Exception as e:
        print(f"点击授权按钮失败: {e}")
        return False
    finally:
        await controller.close()


async def capture_qrcode(url: str, output_path: str, qrcode_selector: str = "img[src*='qrcode']"):
    """
    截取页面中的二维码

    Args:
        url: 页面地址
        output_path: 输出路径
        qrcode_selector: 二维码元素选择器
    """
    controller = BrowserController(headless=False)
    try:
        await controller.start()
        await controller.navigate(url)
        await controller.wait_for(qrcode_selector)
        await controller.screenshot(output_path, selector=qrcode_selector)
        return True
    except Exception as e:
        print(f"截取二维码失败: {e}")
        return False
    finally:
        await controller.close()


# 主函数入口

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Browser Playwright Actions")
    parser.add_argument("action", choices=["screenshot", "click", "qrcode"], help="操作类型")
    parser.add_argument("--url", help="目标 URL")
    parser.add_argument("--output", default="temp/screenshot.png", help="输出路径")
    parser.add_argument("--selector", help="元素选择器")
    parser.add_argument("--headless", action="store_true", help="无头模式")

    args = parser.parse_args()

    if args.action == "screenshot" and args.url:
        asyncio.run(quick_screenshot(args.url, args.output, args.headless))
        print(f"截图已保存: {args.output}")

    elif args.action == "click" and args.url and args.selector:
        success = asyncio.run(click_authorization_button(args.url, args.selector))
        print(f"点击{'成功' if success else '失败'}")

    elif args.action == "qrcode" and args.url:
        selector = args.selector or "img[src*='qrcode']"
        success = asyncio.run(capture_qrcode(args.url, args.output, selector))
        print(f"二维码截取{'成功' if success else '失败'}: {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
