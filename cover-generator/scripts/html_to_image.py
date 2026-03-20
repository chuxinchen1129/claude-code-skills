#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 封面转图片工具

使用 Playwright 将 HTML 封面转换为高分辨率 PNG 图片
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright 未安装，请运行:")
    print("  pip3 install playwright")
    print("  playwright install chromium")
    raise


class HTMLToImageConverter:
    """HTML 转图片工具"""

    # 小红书封面尺寸 (3:4 比例)
    WIDTH = 1080
    HEIGHT = 1440

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            script_dir = Path(__file__).parent
            output_dir = script_dir / "covers"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert(
        self,
        html_path: str,
        output_filename: Optional[str] = None,
        element_id: Optional[str] = None,
        device_scale_factor: float = 2.0  # Retina 质量
    ) -> Dict:
        """
        将 HTML 转换为 PNG 图片

        Args:
            html_path: HTML 文件路径
            output_filename: 输出文件名（可选）
            element_id: 要截取的元素 ID（可选，用于定向截取特定容器）
            device_scale_factor: 设备缩放因子（默认2.0，Retina质量）

        Returns:
            结果字典
        """
        html_file = Path(html_path)

        if not html_file.exists():
            return {
                'success': False,
                'path': None,
                'message': f'HTML 文件不存在: {html_path}'
            }

        try:
            # 生成输出文件名
            if output_filename is None:
                output_filename = html_file.stem + '.png'

            output_path = self.output_dir / output_filename

            # 使用 Playwright 转换
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()

                # 读取 HTML 内容
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # 设置页面内容
                page.set_content(html_content)

                # 等待页面加载完成
                page.wait_for_load_state('networkidle', timeout=5000)

                if element_id:
                    # 定向截取：定位特定元素
                    card_locator = page.locator(f"#{element_id}")
                    card_locator.wait_for(state="visible", timeout=5000)
                    card_locator.screenshot(path=output_path, scale="device")
                else:
                    # 默认：截取整个页面
                    page.screenshot(path=output_path, scale="device")

                browser.close()

            return {
                'success': True,
                'path': output_path,
                'message': f'✓ HTML 转图片成功: {output_filename}'
            }

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'转换失败: {e}'
            }

    def convert_to_xhs_style(
        self,
        html_path: str,
        output_filename: Optional[str] = None,
        element_id: str = "editorial-card-container"  # 社论风默认使用卡片容器 ID
    ) -> Dict:
        """
        转换为小红书风格封面 (1080x1440, 3:4)

        Args:
            html_path: HTML 文件路径
            output_filename: 输出文件名（可选）
            element_id: 要截取的元素 ID

        Returns:
            结果字典
        """
        return self.convert(
            html_path=html_path,
            output_filename=output_filename,
            element_id=element_id,
            device_scale_factor=2.0
        )


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='HTML 封面转图片工具')
    parser.add_argument('html', help='HTML 文件路径')
    parser.add_argument('--output', '-o', help='输出文件名')
    parser.add_argument('--width', type=int, default=1080, help='宽度（像素）')
    parser.add_argument('--height', type=int, default=1440, help='高度（像素）')
    parser.add_argument('--xhs', action='store_true', help='小红书风格 (1080x1440)')
    parser.add_argument('--scale', type=float, default=2.0, help='设备缩放因子（默认2.0）')
    parser.add_argument('--element-id', help='要截取的元素 ID（用于定向截取特定容器）')

    args = parser.parse_args()

    converter = HTMLToImageConverter()

    if args.xhs:
        result = converter.convert_to_xhs_style(
            html_path=args.html,
            output_filename=args.output,
            element_id=args.element_id if args.element_id else "editorial-card-container"
        )
    else:
        result = converter.convert(
            html_path=args.html,
            output_filename=args.output,
            element_id=args.element_id,
            device_scale_factor=args.scale
        )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")


if __name__ == '__main__':
    main()
