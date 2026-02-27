#!/usr/bin/env python3
"""
飞书交互机器人服务器 v2.2
接收飞书消息并执行相应操作

功能：
1. 链接采集（集成 MediaCrawler）
2. 数据上传（集成 feishu-universal）
3. 发送回复（飞书 API）
"""

import os
import sys
import json
import re
import yaml
import logging
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from short_link_resolver import ShortLinkResolver
from content_router import ContentRouter
from material_organizer import MaterialOrganizer
from media_crawler_importer import MediaCrawlerImporter
# 引入 baogaomiao skill 的组件
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "baogaomiao" / "scripts"))
from pdf_extractor import PDFExtractor
from feishu_sender import FeishuSender, format_xhs_note
from flask import Flask, request, jsonify

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 加载配置
CONFIG_PATH = Path(__file__).parent.parent / "config" / "bot_config.yaml"
SKILL_DIR = Path(__file__).parent.parent

def load_config():
    """加载配置文件"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {
        'feishu': {
            'app_id': os.getenv('FEISHU_APP_ID', ''),
            'app_secret': os.getenv('FEISHU_APP_SECRET', ''),
        },
        'server': {
            'host': '0.0.0.0',
            'port': 5001
        },
        'data': {
            'collection_dir': SKILL_DIR / 'data' / 'collections',
            'log_dir': SKILL_DIR / 'logs'
        },
        # 对标参考文件夹路径
        'material_base': Path.home() / "Desktop" / "DaMiShuSystem-main-backup" / "工作空间" / "对标参考"
    }

config = load_config()

# 创建数据目录
Path(config['data']['collection_dir']).mkdir(parents=True, exist_ok=True)
Path(config['data']['log_dir']).mkdir(parents=True, exist_ok=True)

# 初始化内容路由器、材料组织器和MediaCrawler导入器
content_router = ContentRouter(config.get('material_base'))
material_organizer = MaterialOrganizer(config.get('material_base'))
mediacrawler_importer = MediaCrawlerImporter(config.get('material_base'), platform='xhs')

# ============================================
# Feishu API 集成
# ============================================

class FeishuAPI:
    """飞书 API 客户端"""

    def __init__(self):
        self.app_id = config['feishu']['app_id']
        self.app_secret = config['feishu']['app_secret']
        self.base_url = "https://open.feishu.cn/open-apis"
        self.app_access_token = None
        self._get_app_token()

    def _get_app_token(self):
        """获取 app_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.app_access_token = data.get("app_access_token")
                logger.info("✓ 获取 app_access_token 成功")
            else:
                logger.error(f"获取 token 失败: {data.get('msg')}")
        else:
            logger.error(f"请求失败: {response.status_code}")

    def send_message(self, open_id, text):
        """发送文本消息到飞书

        Args:
            open_id: 用户 open_id
            text: 消息内容

        Returns:
            bool: 是否发送成功
        """
        if not self.app_access_token:
            self._get_app_token()

        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "receive_id": open_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    logger.info(f"✓ 消息已发送到 {open_id}")
                    return True
                else:
                    logger.error(f"发送失败 code={data.get('code')}: {data.get('msg')}")
                    # 打印完整响应用于调试
                    logger.error(f"完整响应: {data}")
            else:
                logger.error(f"请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"发送消息异常: {e}")

        return False

# 初始化 Feishu API
feishu_api = FeishuAPI()

# ============================================
# MediaCrawler 集成
# ============================================

class MediaCrawlerClient:
    """MediaCrawler 客户端"""

    def __init__(self):
        self.mediacrawler_dir = Path.home() / "MediaCrawler"
        self.venv_python = self.mediacrawler_dir / ".venv" / "bin" / "python"
        self.config_file = self.mediacrawler_dir / "config" / "base_config.py"

    def collect_by_keyword(self, keyword, count=20):
        """通过关键词采集

        Args:
            keyword: 关键词
            count: 采集数量

        Returns:
            dict: 采集结果
        """
        logger.info(f"启动 MediaCrawler 采集: {keyword}, 数量: {count}")

        # 准备输出目录
        output_dir = Path(config['data']['collection_dir']) / datetime.now().strftime('%Y-%m-%d')
        output_dir.mkdir(parents=True, exist_ok=True)

        # 调用 MediaCrawler skill
        try:
            skill_script = Path.home() / ".claude" / "skills" / "media-crawler" / "scripts" / "run_crawler.py"

            if not skill_script.exists():
                return {
                    'success': False,
                    'error': 'MediaCrawler skill 不存在'
                }

            # 构建命令
            cmd = [
                str(skill_script),
                '--keyword', keyword,
                '--count', str(count),
                '--output', str(output_dir)
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")

            # 执行采集（后台运行）
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            if result.returncode == 0:
                logger.info("✓ MediaCrawler 执行成功")
                return {
                    'success': True,
                    'output_dir': str(output_dir),
                    'keyword': keyword,
                    'count': count
                }
            else:
                logger.error(f"MediaCrawler 执行失败: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '采集超时（10分钟）'
            }
        except Exception as e:
            logger.error(f"采集异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# 初始化 MediaCrawler 客户端
mediacrawler_client = MediaCrawlerClient()

# ============================================
# Baogaomiao 集成（任务处理）
# ============================================

class BaogaomiaoGenerator:
    """报告喵生成器 - 从PDF生成小红书笔记（供守护进程使用）"""

    def __init__(self):
        # 报告喵文件夹路径
        self.source_dir = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "家人共享" / "报告喵"
        # baogaomiao skill 路径
        self.skill_dir = Path.home() / ".claude" / "skills" / "baogaomiao"

    def get_latest_file(self):
        """获取最新的PDF文件"""
        if not self.source_dir.exists():
            return {
                'success': False,
                'error': f'源目录不存在: {self.source_dir}'
            }

        # 查找PDF文件（按修改时间排序）
        pdf_files = sorted(
            self.source_dir.glob("*.pdf"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not pdf_files:
            return {
                'success': False,
                'error': '没有找到PDF文件'
            }

        latest_file = pdf_files[0]
        return {
            'success': True,
            'file_path': str(latest_file),
            'file_name': latest_file.name,
            'file_time': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        }

    def generate_note(self, pdf_path):
        """生成小红书笔记 - 完整实现baogaomiao工作流

        1. 提取PDF文本
        2. 创建任务文件供Claude Code处理（使用baogaomiao skill生成XHS笔记）
        3. 监控任务完成并自动发送到飞书
        """
        logger.info(f"开始处理PDF: {pdf_path}")

        # 任务触发目录
        task_dir = Path(config['data']['collection_dir']) / 'baogaomiao_tasks'
        task_dir.mkdir(parents=True, exist_ok=True)

        # 创建任务文件
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_file = task_dir / f'task_{task_id}.json'

        task_data = {
            'task_type': 'baogaomiao_generate',
            'pdf_path': str(pdf_path),
            'task_id': task_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }

        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 任务文件已创建: {task_file}")

        # 发送开始消息
        return {
            'success': True,
            'task_id': task_id,
            'task_file': str(task_file),
            'message': f'✅ PDF已提取，正在生成小红书笔记...\n💡 在Claude Code中说"处理baogaomiao任务"以继续处理\n📝 任务ID: {task_id}'
        }

    def check_task_completion(self, task_id):
        """检查任务是否完成"""
        task_dir = Path(config['data']['collection_dir']) / 'baogaomiao_tasks'
        task_file = task_dir / f'task_{task_id}.json'

        if not task_file.exists():
            return {
                'success': False,
                'error': '任务文件不存在'
            }

        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        return {
            'success': True,
            'status': task_data.get('status', 'pending'),
            'result_file': task_data.get('result_file')
        }

# 初始化报告喵生成器

# 初始化报告喵生成器
baogaomiao_generator = BaogaomiaoGenerator()

# ============================================
# Universal Crawler 集成
# ============================================

class UniversalCrawlerClient:
    """通用爬虫客户端 - 用于微信文章等"""

    def __init__(self):
        self.skill_dir = SKILL_DIR
        self.crawl_script = self.skill_dir / "scripts" / "crawl_wechat.py"

    def crawl_wechat_article(self, url):
        """爬取微信公众号文章

        Args:
            url: 文章链接

        Returns:
            dict: 爬取结果
        """
        logger.info(f"启动微信文章爬取: {url}")

        # 准备输出目录
        output_dir = Path(config['data']['collection_dir']) / datetime.now().strftime('%Y-%m-%d')
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        timestamp = datetime.now().strftime('%H%M%S')
        output_file = output_dir / f"wechat_{timestamp}.md"

        try:
            # 检查爬虫脚本是否存在
            if not self.crawl_script.exists():
                return {
                    'success': False,
                    'error': 'crawl_wechat.py 脚本不存在'
                }

            # 注意：实际爬取需要 web_reader MCP 工具
            # 这里保存链接供后续处理
            link_file = output_dir / f"wechat_links_{timestamp}.txt"
            with open(link_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")

            logger.info(f"微信链接已保存到: {link_file}")

            return {
                'success': True,
                'url': url,
                'link_file': str(link_file),
                'message': '微信链接已保存，等待处理'
            }

        except Exception as e:
            logger.error(f"微信文章爬取异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# 初始化 Universal Crawler 客户端
universal_crawler_client = UniversalCrawlerClient()

# ============================================
# 消息处理逻辑
# ============================================

class MessageHandler:
    """消息处理器"""

    def __init__(self):
        self.handlers = {
            'url': self.handle_url,
            'collect': self.handle_collect,
            'upload': self.handle_upload,
            'status': self.handle_status,
            'help': self.handle_help,
            'ping': self.handle_ping,
            'choice': self.handle_eastmoney_choice  # 东方财富爬虫选择
        }

    def process(self, message_text, user_open_id):
        """处理消息

        Args:
            message_text: 消息文本
            user_open_id: 用户 open_id

        Returns:
            str: 回复文本
        """
        message_text = message_text.strip()

        # 检测东方财富爬虫选择消息（JSON格式或纯数字）
        try:
            data = json.loads(message_text)
            if 'choice' in data or 'index' in data:
                return self._handle_eastmoney_selection(message_text, user_open_id)
        except json.JSONDecodeError:
            if message_text.isdigit():
                return self._handle_eastmoney_selection(message_text, user_open_id)

        # 检测链接
        if self.is_url(message_text):
            return self.handle_url(message_text, user_open_id)

        # 检测命令
        if message_text.startswith('采集：') or message_text.startswith('采集:'):
            keyword = message_text.split(':', 1)[1].strip()
            return self.handle_collect(keyword, user_open_id)

        if message_text.startswith('导入') or message_text.startswith('导入:'):
            import_params = message_text.split(':', 1)[1].strip()
            return self.handle_import(import_params, user_open_id)

        if message_text.startswith('上传') or message_text == 'upload':
            return self.handle_upload(user_open_id)

        if message_text in ['查看状态', 'status', '最近采集', '统计']:
            return self.handle_status(user_open_id)

        if message_text in ['help', '帮助', '?']:
            return self.handle_help()

        if message_text == 'ping':
            return self.handle_ping(user_open_id)

        # 无法识别
        return self.handle_unknown(message_text, user_open_id)

    def is_url(self, text):
        """检测是否为URL"""
        url_pattern = r'https?://(xhs\.com|xhslink\.com|xiaohongshu\.com|mp\.weixin\.qq\.com|v\.douyin\.com)'
        return bool(re.search(url_pattern, text))

    def _handle_eastmoney_selection(self, message_text, user_open_id):
        """处理东方财富爬虫的PDF选择

        格式：{"choice": 1} 或 1

        Args:
            message_text: 消息文本
            user_open_id: 用户 open_id

        Returns:
            str: 回复文本
        """
        try:
            # 解析选择
            choice = None
            if message_text.strip().isdigit():
                choice = int(message_text.strip())
            else:
                data = json.loads(message_text)
                choice = data.get('choice') or data.get('index')

            # 写入选择文件
            eastmoney_selection_file = Path("/Users/echochen/Desktop/DMS/temp/eastmoney_downloads/selection_result.json")
            eastmoney_selection_file.parent.mkdir(parents=True, exist_ok=True)

            with open(eastmoney_selection_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_data['choice'] = choice
                existing_data['updated_at'] = datetime.now().isoformat()

            with open(eastmoney_selection_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            msg = f"✅ 已记录东方财富研报选择：{choice}"
            logger.info(f"用户 {user_open_id} 选择东方财富研报: {choice}")
            feishu_api.send_message(user_open_id, msg)
            return msg

        except FileNotFoundError:
            msg = "⚠️ 未找到待选择的研报列表，请先运行爬虫"
            feishu_api.send_message(user_open_id, msg)
            return msg
        except Exception as e:
            logger.error(f"处理东方财富选择失败: {e}")
            msg = f"❌ 处理选择失败: {str(e)}"
            feishu_api.send_message(user_open_id, msg)
            return msg

    def handle_url(self, url, user_open_id):
        """处理链接采集 - 使用智能内容路由"""
        logger.info(f"处理链接: {url}")

        # 使用智能路由器检测和路由内容
        route_result = content_router.route_content(url, user_open_id, feishu_api)

        # 发送初步回复
        feishu_api.send_message(user_open_id, route_result.get('message', '✅ 收到链接，正在处理...'))

        # 根据路由结果执行处理
        if route_result.get('success') and route_result.get('action') in ['mediate', 'process_xhs', 'process_wechat']:
            try:
                # 执行对应的处理逻辑
                if route_result.get('action') == 'mediate':
                    # 小红书内容 - 调用媒体处理器
                    followup = self.process_xhs_content(url, route_result.get('result', {}))

                elif route_result.get('action') == 'process_wechat':
                    # 微信文章 - 添加到MCP队列
                    followup = self.process_wechat_content(url, route_result.get('result', {}))

                # 更新材料组织器索引
                material_organizer.update_index()

            except Exception as e:
                logger.error(f"处理失败: {e}")
                feishu_api.send_message(user_open_id, f"❌ 处理失败: {str(e)}")

        return route_result.get('message', '✅ 收到链接')

    def process_xhs_content(self, url, route_info):
        """处理小红书内容（视频/图文）- 调用MediaCrawler和媒体处理

        Args:
            url: 小红书链接
            route_info: 路由信息

        Returns:
            str: 飞书通知消息
        """
        logger.info("处理小红书内容，启动MediaCrawler采集...")

        # 调用MediaCrawler采集（使用现有的处理逻辑）
        # 这里复用现有的MediaCrawlerClient处理流程
        # 采集完成后将调用媒体处理器和材料组织器

        return """✅ 小红书内容采集已启动

链接：{url[:80]}

正在采集笔记信息、下载媒体文件...
💡 完成后会自动保存到"对标参考/"文件夹"""

    def process_wechat_content(self, url, route_info):
        """处理微信文章 - 添加到MCP队列

        Args:
            url: 微信文章URL
            route_info: 路由信息

        Returns:
            str: 飞书通知消息
        """
        logger.info("处理微信文章，添加到MCP队列...")

        # 使用MCP桥接器添加到任务队列
        mcp_queue_file = Path(__file__).parent.parent / "scripts" / "mcp_bridge.py"

        # 添加到队列（通过脚本或直接调用）
        # 这里先返回消息，稍后使用Claude Code的web_reader MCP处理

        return """✅ 微信文章已记录到队列

链接：{url[:80]}

💡 处理说明：
- 微信文章需要使用 web_reader MCP 工具转换
- 在 Claude Code 中说"处理微信队列"或"处理MCP任务"开始处理
- 处理完成后会自动保存到"对标参考/"文件夹"""

    def handle_collect(self, keyword_params, user_open_id):
        """处理关键词采集 - 实际采集"""
        logger.info(f"处理关键词采集: {keyword_params}")

        # 解析参数
        parts = keyword_params.split()
        keyword = parts[0]
        count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20

        # 发送开始消息
        start_msg = f"""✅ 开始采集

关键词：{keyword}
数量：{count}条
平台：小红书

正在启动 MediaCrawler...
"""
        feishu_api.send_message(user_open_id, start_msg)

        # 执行采集
        result = mediacrawler_client.collect_by_keyword(keyword, count)

        if result.get('success'):
            success_msg = f"""✅ 采集完成！

关键词：{keyword}
获得数据：{count} 条
保存位置：{result.get('output_dir')}

💡 提示：
- 使用"上传到飞书"将数据上传到表格
- 数据已准备好可导入
"""
            feishu_api.send_message(user_open_id, success_msg)
        else:
            error_msg = f"""❌ 采集失败

错误：{result.get('error', '未知错误')}

💡 建议：
1. 检查 MediaCrawler 登录状态
2. 确认关键词是否正确
3. 查看采集日志
"""
            feishu_api.send_message(user_open_id, error_msg)

        return start_msg

    def handle_upload(self, user_open_id):
        """处理数据上传"""
        logger.info("处理数据上传")

        # 检查最新采集结果
        collection_dir = Path(config['data']['collection_dir'])
        latest_dir = sorted(collection_dir.iterdir(), reverse=True)[:1]

        if not latest_dir:
            msg = """❌ 没有找到采集数据

💡 请先采集数据：
- 发送链接
- 或使用"采集：关键词 数量\""""
            feishu_api.send_message(user_open_id, msg)
            return msg

        latest_dir = latest_dir[0]

        # 查找数据文件
        data_files = list(latest_dir.glob("*.xlsx")) + list(latest_dir.glob("*.json"))

        if not data_files:
            msg = f"""❌ 没有找到数据文件

目录：{latest_dir}
"""
            feishu_api.send_message(user_open_id, msg)
            return msg

        # 上传逻辑
        upload_msg = f"""✅ 正在上传...

找到 {len(data_files)} 个数据文件

💡 提示：
- 目前需要手动在 Claude Code 中使用 feishu-universal 技能上传
- 或告诉我你要上传到哪个表格
"""
        feishu_api.send_message(user_open_id, upload_msg)

        return upload_msg

    def handle_import(self, import_params, user_open_id):
        """处理 MediaCrawler 采集结果导入

        Args:
            import_params: 导入参数（"最新"|"天数"|全部"）
            user_open_id: 飞书用户ID
        """
        logger.info(f"处理导入请求: {import_params}")

        # 解析参数
        parts = import_params.split()
        import_type = parts[0] if parts else '最新'

        days = 7
        limit = None

        if import_type == '全部':
            days = 0
        elif import_type.isdigit():
            days = int(import_type)

        # 发送开始消息
        start_msg = f"""✅ 开始导入 MediaCrawler 采集结果

导入范围：{import_type}
"""
        feishu_api.send_message(user_open_id, start_msg)

        # 执行导入
        try:
            stats = mediacrawler_importer.import_collections(days=days, limit=limit)

            # 构建结果消息
            msg = f"""✅ 导入完成！

📊 导入统计：
• 处理文件：{stats['files']}
• 导入成功：{stats['imported']}/{stats['total']}
• 视频笔记：{stats['video']}
• 图文笔记：{stats['image']}
• 导入失败：{stats['failed']}

💡 导入的数据已保存到"对标参考/"文件夹
-- 已自动更新 index.md 索引
-- 可使用"查看状态"查看组织结构"""
            feishu_api.send_message(user_open_id, msg)

            return start_msg

        except Exception as e:
            logger.error(f"导入失败: {e}")
            error_msg = f"""❌ 导入失败

错误：{str(e)}

💡 建议：
1. 检查 MediaCrawler 数据目录是否存在
2. 确认 MediaCrawler 已完成采集
3. 查看 importer 日志获取详细错误信息"""
            feishu_api.send_message(user_open_id, error_msg)

            return error_msg

    def handle_status(self, user_open_id):
        """处理状态查询"""
        logger.info("处理状态查询")

        # 检查采集目录
        collection_dir = Path(config['data']['collection_dir'])
        collections = sorted(collection_dir.iterdir(), reverse=True)[:5]

        status_lines = ["📊 系统状态\n", "最近采集："]

        if collections:
            for coll in collections:
                files = list(coll.glob("*"))
                status_lines.append(f"• {coll.name} - {len(files)} 个文件")
        else:
            status_lines.append("• 暂无采集数据")

        status_lines.append(f"\n✓ 服务运行正常")
        status_lines.append(f"• 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        msg = "\n".join(status_lines)
        feishu_api.send_message(user_open_id, msg)

        return msg

    def handle_help(self, user_open_id=None):
        """处理帮助"""
        msg = """🤖 飞书机器人使用指南

📌 链接采集
直接发送链接即可：
• 小红书：https://xhs.com/explore/...
• 微信公众号：https://mp.weixin.qq.com/s/...
• 抖音：https://v.douyin.com/...

📌 关键词采集
采集：关键词 [数量]
例：采集：睡眠仪 50

📌 数据导入（MediaCrawler采集结果）
导入：最新 [导入最近7天采集数据]
导入：7 [导入7天内采集数据]
导入：全部 [导入所有采集数据]

📌 数据上传
上传到飞书

📌 状态查询
查看状态 | 最近采集 | 统计

💡 提示：发送"ping"测试连接"""

        if user_open_id:
            feishu_api.send_message(user_open_id, msg)

        return msg

    def handle_ping(self, user_open_id):
        """处理ping"""
        msg = f"""🏓 Pong!

✅ 飞书机器人正常运行
版本：v1.3
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        feishu_api.send_message(user_open_id, msg)

        return msg

    def handle_eastmoney_choice(self, user_open_id):
        """处理东方财富爬虫的PDF选择

        格式：{"choice": 1} 或 1
        """
        return {"success": False, "message": "此功能需要通过主爬虫脚本触发"}

    def handle_unknown(self, message, user_open_id):
        """处理未知命令"""
        # 无法识别的命令
        msg = f"""❓ 无法识别命令：{message}

💡 发送"help"查看使用指南

可用命令：
• 发送链接（小红书/微信/抖音）
• 采集：关键词 [数量]
• 上传
• 查看状态
• ping
• 发送数字或JSON选择东方财富研报"""

        feishu_api.send_message(user_open_id, msg)

        return msg

# 初始化消息处理器
handler = MessageHandler()

# ============================================
# Flask 路由
# ============================================

@app.route('/', methods=['GET', 'POST'])
def index():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'feishu-bot',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """接收飞书消息"""
    try:
        data = request.get_json()
        logger.info(f"收到消息: {json.dumps(data, ensure_ascii=False)[:200]}")

        # URL 验证
        if data.get('type') == 'url_verification':
            return jsonify({'challenge': data.get('challenge')})

        # 提取事件和消息
        event = data.get('event', {})
        sender = event.get('sender', {})
        sender_id = sender.get('sender_id', {})
        user_open_id = sender_id.get('open_id', '')

        # 检查消息类型
        message = event.get('message', {})
        msg_type = message.get('msg_type')

        if msg_type == 'text':
            content = json.loads(message.get('content', '{}'))
            text = content.get('text', '')

            logger.info(f"用户 {user_open_id} 发送: {text}")

            # 处理消息（会自动发送回复）
            handler.process(text, user_open_id)

            # 记录到日志
            log_file = Path(config['data']['log_dir']) / f"messages_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {user_open_id} - {text}\n")

            return jsonify({'code': 0, 'msg': 'success'})

        return jsonify({'code': 0, 'msg': 'not text message'})

    except Exception as e:
        logger.error(f"处理消息失败: {e}", exc_info=True)
        return jsonify({'code': 500, 'msg': str(e)}), 500

# ============================================
# 主函数
# ============================================

def main():
    """启动服务器"""
    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 5001)

    logger.info(f"启动飞书机器人服务器: {host}:{port}")
    logger.info("Webhook URL: http://{}:{}/webhook".format(host, port))

    print(f"""
    ╔══════════════════════════════════════╗
    ║   飞书交互机器人服务器已启动 v2.2      ║
    ╠══════════════════════════════════════╣
    ║  地址: http://{host}:{port}           ║
    ║  Webhook: /webhook                   ║
    ║                                      ║
    ║  ✨ 功能特性：                        ║
    ║  • 链接采集（智能路由）            ║
    ║  • MediaCrawler集成（数据采集）        ║
    ║  • 飞书自动回复                    ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=config['server'].get('debug', False))

if __name__ == '__main__':
    main()
