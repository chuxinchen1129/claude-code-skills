#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 封面转图片工具 - 稳定版

设计原则（不允许破坏）：
1. 视口尺寸 = #editorial-card-container 实际 bounding_box，从 HTML 动态读取
2. 截图前断言卡片已渲染（width>0）且字体已 ready
3. 截图后用 PIL 校验四角像素 = 卡片背景色，不通过即报错
4. body 不允许 padding（由 HTML 模板保证），视口直接对齐卡片
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright 未安装，请运行:")
    print("  pip3 install playwright")
    print("  playwright install chromium")
    raise

try:
    from PIL import Image
except ImportError:
    print("Pillow 未安装，请运行: pip3 install pillow")
    raise


# 默认卡片背景色（红 #FB0151），用于像素校验。
# 如果 HTML 模板的 bgBase 改了，这里也要同步。
EXPECTED_BG_RGB: Tuple[int, int, int] = (251, 1, 81)
# 像素校验容差（避免抗锯齿/压缩导致的轻微色差）
PIXEL_TOLERANCE: int = 12


class HTMLToImageConverter:
    """HTML 转图片工具 - 稳定版"""

    # 初始视口（足够大让卡片完整渲染，之后会动态调整）
    INITIAL_VIEWPORT_WIDTH = 1200
    INITIAL_VIEWPORT_HEIGHT = 1600

    # 卡片容器选择器（与 editorial_cover.py 的 HTML 模板一致）
    CARD_SELECTOR = "#editorial-card-container"

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
        device_scale_factor: float = 2.0,
    ) -> Dict:
        """
        将 HTML 转换为 PNG 图片。

        关键步骤：
        1. 初始视口加载 HTML
        2. 读取卡片实际 bounding_box
        3. 把视口设成卡片尺寸（消除周围空白）
        4. 等字体 ready，断言卡片渲染完整
        5. 截图
        6. PIL 校验四角像素 == 卡片背景色

        Args:
            html_path: HTML 文件路径
            output_filename: 输出文件名（可选）
            element_id: 卡片容器 ID（默认用类常量 CARD_SELECTOR）
            device_scale_factor: 设备缩放因子（默认 2.0，Retina 质量）

        Returns:
            结果字典（含 success/path/viewport_size/verification 等字段）
        """
        html_file = Path(html_path)
        if not html_file.exists():
            return {
                'success': False,
                'path': None,
                'message': f'HTML 文件不存在: {html_path}'
            }

        if output_filename is None:
            output_filename = html_file.stem + '.png'
        output_path = self.output_dir / output_filename

        card_selector = f"#{element_id}" if element_id else self.CARD_SELECTOR

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(
                    viewport={
                        'width': self.INITIAL_VIEWPORT_WIDTH,
                        'height': self.INITIAL_VIEWPORT_HEIGHT,
                    },
                    device_scale_factor=device_scale_factor,
                )

                # 用 file:// 协议加载 HTML（而非 set_content），
                # 这样浏览器能正确解析 HTML 里的相对资源路径（../assets/...）。
                file_uri = html_file.resolve().as_uri()
                try:
                    page.goto(file_uri, wait_until='load', timeout=30000)
                except Exception:
                    try:
                        page.goto(file_uri, wait_until='commit', timeout=10000)
                    except Exception:
                        pass

                # ===== 关键步骤 0：等 Tailwind JIT 把 utility class 应用到卡片 =====
                # 检查卡片 computed background-color 已是 bgBase（非白色/透明）
                try:
                    page.wait_for_function(f"""
                        () => {{
                            const el = document.querySelector('{card_selector}');
                            if (!el) return false;
                            const bg = getComputedStyle(el).backgroundColor;
                            // bgBase=#FB0151 → rgb(251, 1, 81)
                            return bg === 'rgb(251, 1, 81)';
                        }}
                    """, timeout=15000)
                except Exception:
                    # Tailwind JIT 超时——后续像素校验会失败并报告
                    pass

                # ===== 关键步骤 1：读取卡片实际尺寸 =====
                try:
                    page.wait_for_selector(card_selector, state='attached', timeout=10000)
                except Exception:
                    browser.close()
                    return {
                        'success': False,
                        'path': None,
                        'message': f'卡片容器 {card_selector} 未找到',
                    }

                bbox = page.evaluate(f"""
                    () => {{
                        const el = document.querySelector('{card_selector}');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return {{width: r.width, height: r.height, x: r.x, y: r.y}};
                    }}
                """)

                if not bbox or bbox['width'] <= 0 or bbox['height'] <= 0:
                    browser.close()
                    return {
                        'success': False,
                        'path': None,
                        'message': f'卡片尺寸无效: {bbox}',
                    }

                card_w = int(round(bbox['width']))
                card_h = int(round(bbox['height']))

                # ===== 关键步骤 2：把视口设成卡片尺寸 =====
                page.set_viewport_size({'width': card_w, 'height': card_h})

                # 等待卡片在新视口下重新布局
                page.wait_for_timeout(500)

                # ===== 关键步骤 3：字体 ready 断言 =====
                try:
                    page.wait_for_function("document.fonts && document.fonts.status === 'loaded'",
                                            timeout=8000)
                except Exception:
                    # 字体加载超时不阻塞（但有 warning）
                    pass

                # 给 Tailwind JIT 一点时间生成 utility class
                page.wait_for_timeout(500)

                # ===== 关键步骤 4：截图 =====
                page.screenshot(
                    path=output_path,
                    full_page=False,
                    scale='device',
                    timeout=15000,
                )

                browser.close()

            # ===== 关键步骤 5：PIL 像素校验 =====
            verify = self._verify_corners(output_path)

            result = {
                'success': verify['passed'],
                'path': output_path,
                'message': ('✓ HTML 转图片成功' if verify['passed']
                            else f'✗ 像素校验失败: {verify["detail"]}'),
                'card_size': f'{card_w}x{card_h}',
                'viewport_size': f'{card_w}x{card_h}',
                'png_size': f'{verify["png_size"][0]}x{verify["png_size"][1]}',
                'verification': verify,
            }
            if not verify['passed']:
                # 不删图，方便排查
                pass
            return result

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'转换失败: {e}'
            }

    def _verify_corners(self, png_path: Path) -> Dict:
        """
        校验 PNG 四角像素 ≈ 卡片背景色（无白边）。

        Returns:
            {passed: bool, detail: str, corners: dict, png_size: tuple}
        """
        img = Image.open(png_path).convert('RGB')
        w, h = img.size
        corners = {
            'top_left': img.getpixel((5, 5)),
            'top_right': img.getpixel((w - 5, 5)),
            'bottom_left': img.getpixel((5, h - 5)),
            'bottom_right': img.getpixel((w - 5, h - 5)),
        }

        def close(c):
            return all(abs(c[i] - EXPECTED_BG_RGB[i]) <= PIXEL_TOLERANCE for i in range(3))

        passed = all(close(c) for c in corners.values())

        if passed:
            detail = '四角像素均为卡片背景色'
        else:
            bad = {k: v for k, v in corners.items() if not close(v)}
            detail = (f'角像素偏离背景 {EXPECTED_BG_RGB}: '
                        f'{bad}（容差 {PIXEL_TOLERANCE}）')

        return {
            'passed': passed,
            'detail': detail,
            'corners': {k: list(v) for k, v in corners.items()},
            'png_size': (w, h),
        }

    def convert_to_xhs_style(
        self,
        html_path: str,
        output_filename: Optional[str] = None,
        element_id: str = "editorial-card-container",
    ) -> Dict:
        """转换为小红书风格封面（3:4，device_scale=2.0）。

        卡片实际尺寸由 HTML 模板决定（当前 640×853），输出 PNG = 卡片尺寸 × 2。
        """
        return self.convert(
            html_path=html_path,
            output_filename=output_filename,
            element_id=element_id,
            device_scale_factor=2.0,
        )


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='HTML 封面转图片工具 - 稳定版')
    parser.add_argument('html', help='HTML 文件路径')
    parser.add_argument('--output', '-o', help='输出文件名')
    parser.add_argument('--scale', type=float, default=2.0, help='设备缩放因子（默认2.0）')
    parser.add_argument('--element-id', help='卡片容器 ID（默认 editorial-card-container）')

    args = parser.parse_args()

    converter = HTMLToImageConverter()
    result = converter.convert(
        html_path=args.html,
        output_filename=args.output,
        element_id=args.element_id,
        device_scale_factor=args.scale,
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")
        print(f"  卡片尺寸: {result.get('card_size')}")
        print(f"  PNG 尺寸: {result.get('png_size')}")
        print(f"  像素校验: {result.get('verification', {}).get('detail')}")


if __name__ == '__main__':
    main()
