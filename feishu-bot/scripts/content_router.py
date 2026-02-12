#!/usr/bin/env python3
"""
智能内容路由器

功能：
1. 检测URL类型（短链接/完整链接/微信文章/其他）
2. 解析短链接（使用ShortLinkResolver）
3. 路由到对应处理器
4. 返回统一格式的处理结果

作者：大秘书系统
版本：v1.0
创建时间：2026-02-12
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# 导入现有模块
import sys
sys.path.append(str(Path(__file__).parent))
from short_link_resolver import ShortLinkResolver

logger = logging.getLogger(__name__)


class ContentRouter:
    """智能内容路由器 - 检测URL类型并路由到对应处理器"""

    # URL 模式匹配
    PATTERNS = {
        'xhs_short': r'https?://(?:www\.)?xhslink\.com/o/[a-zA-Z0-9]+',
        'xhs_full': r'xiaohongshu\.com/explore/([a-f0-9]{24})',
        'xhs_alt': r'xhs\.com/(?:explore/)?([a-f0-9]{24})',
        'wechat': r'mp\.weixin\.qq\.com/s/([a-zA-Z0-9_-]+)',
        'wechat_article': r'weixin\.qq\.com/cgi-bin/readtemplate\?t='
    }

    def __init__(self, material_base_path=None):
        """
        初始化路由器

        Args:
            material_base_path: 材料存储基础路径
        """
        # 默认路径：DaMiShuSystem/工作空间/对标参考/
        if material_base_path is None:
            material_base_path = Path.home() / "Desktop" / "DaMiShuSystem-main-backup" / "工作空间" / "对标参考"
        self.material_base = Path(material_base_path)

        # 初始化短链接解析器
        self.short_link_resolver = ShortLinkResolver()

        # 创建输出目录
        self.output_dirs = {
            'xhs_video': self.material_base / "小红书视频",
            'xhs_image': self.material_base / "小红书图文",
            'wechat': self.material_base / "微信文章"
        }
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"ContentRouter initialized with material base: {self.material_base}")

    def detect_content_type(self, url):
        """
        检测内容类型

        Args:
            url: 输入的URL

        Returns:
            dict: {
                'type': 'xhs_video'|'xhs_image'|'wechat_article'|'unknown',
                'platform': 'xhs'|'wechat'|'unknown',
                'note_id': str|None,  # 笔记ID（如果适用）
                'original_url': str,
                'is_short_link': bool
            }
        """
        result = {
            'type': 'unknown',
            'platform': 'unknown',
            'note_id': None,
            'original_url': url,
            'is_short_link': False
        }

        # 检测是否为短链接
        if re.match(self.PATTERNS['xhs_short'], url):
            result['is_short_link'] = True
            result['platform'] = 'xhs'
            # 需要解析才能确定类型
            return result

        # 检测小红书完整链接
        xhs_full_match = re.search(self.PATTERNS['xhs_full'], url)
        xhs_alt_match = re.search(self.PATTERNS['xhs_alt'], url)

        if xhs_full_match or xhs_alt_match:
            result['platform'] = 'xhs'
            result['note_id'] = xhs_full_match.group(1) if xhs_full_match else xhs_alt_match.group(1)
            # 默认为视频，后续根据采集结果确定
            result['type'] = 'xhs_video'
            return result

        # 检测微信文章
        if re.search(self.PATTERNS['wechat'], url) or re.search(self.PATTERNS['wechat_article'], url):
            result['platform'] = 'wechat'
            result['type'] = 'wechat_article'
            return result

        return result

    def resolve_short_link(self, url):
        """
        解析短链接

        Args:
            url: 短链接URL

        Returns:
            dict: {success: bool, note_id: str, full_url: str, error: str}
        """
        return self.short_link_resolver.resolve_xhs_short_link(url)

    def route_content(self, url, user_open_id=None, feishu_api=None):
        """
        路由内容到对应处理器

        Args:
            url: 输入的URL
            user_open_id: 飞书用户ID（可选，用于发送通知）
            feishu_api: 飞书API实例（可选）

        Returns:
            dict: 处理结果
                {
                    'success': bool,
                    'type': str,
                    'action': str,  # 'resolve_short_link'|'mediate'|'process_xhs'|'process_wechat'|'unsupported'
                    'result': dict,
                    'message': str  # 用户通知消息
                }
        """
        # 1. 检测内容类型
        detection = self.detect_content_type(url)

        logger.info(f"Content detection result: {detection}")

        # 2. 如果是短链接，需要先解析
        if detection['is_short_link']:
            logger.info(f"Short link detected, resolving: {url}")
            resolve_result = self.resolve_short_link(url)

            if not resolve_result.get('success'):
                error_msg = f"❌ 短链接解析失败\n\nURL: {url}\n错误: {resolve_result.get('error', '未知错误')}"
                return {
                    'success': False,
                    'type': 'resolve_failed',
                    'action': 'resolve_short_link',
                    'result': resolve_result,
                    'message': error_msg
                }

            # 解析成功，更新为完整URL继续处理
            url = resolve_result.get('full_url', url)
            detection = self.detect_content_type(url)
            logger.info(f"Short link resolved to: {url}")

        # 3. 根据类型路由
        if detection['platform'] == 'xhs':
            return {
                'success': True,
                'type': detection['type'],
                'action': 'mediate',
                'result': {
                    'platform': 'xhs',
                    'note_id': detection.get('note_id'),
                    'url': url,
                    'output_dir': str(self.output_dirs['xhs_video'])  # 临时，后续根据类型确定
                },
                'message': f"✅ 收到小红书链接\n\nURL: {url[:80]}...\n\n正在启动智能处理..."
            }

        elif detection['platform'] == 'wechat':
            return {
                'success': True,
                'type': 'wechat_article',
                'action': 'process_wechat',
                'result': {
                    'platform': 'wechat',
                    'url': url,
                    'output_dir': str(self.output_dirs['wechat'])
                },
                'message': f"✅ 收到微信公众号文章\n\nURL: {url[:80]}...\n\n正在转换为Markdown..."
            }

        else:
            return {
                'success': False,
                'type': 'unsupported',
                'action': 'unsupported',
                'result': detection,
                'message': f"""❓ 暂不支持该平台

收到的链接：{url}

支持的平台：
• 小红书（短链接/完整链接）
• 微信公众号文章

💡 提示：
- 确保链接格式正确
- 查看帮助文档了解支持的平台"""
            }

    def batch_route(self, urls, user_open_id=None, feishu_api=None):
        """
        批量路由多个链接

        Args:
            urls: URL列表
            user_open_id: 飞书用户ID
            feishu_api: 飞书API实例

        Returns:
            list: 处理结果列表
        """
        results = []
        for url in urls:
            result = self.route_content(url, user_open_id, feishu_api)
            results.append(result)
        return results

    def get_output_dir(self, content_type):
        """
        获取指定内容类型的输出目录

        Args:
            content_type: 内容类型

        Returns:
            Path: 输出目录路径
        """
        dir_map = {
            'xhs_video': self.output_dirs['xhs_video'],
            'xhs_image': self.output_dirs['xhs_image'],
            'wechat_article': self.output_dirs['wechat']
        }
        return dir_map.get(content_type, self.material_base)


# 便捷函数
def create_router(material_base_path=None):
    """创建ContentRouter实例"""
    return ContentRouter(material_base_path)


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("Usage: python content_router.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    router = ContentRouter()

    print(f"Testing URL: {url}")
    print("=" * 60)

    result = router.route_content(url)
    print(f"Result: {result}")
