#!/usr/bin/env python3
"""
B站收藏夹视频自动总结工具

工作流程：
1. 抓取收藏夹视频列表
2. 筛选未处理的新视频（时长>10分钟）
3. 提取字幕（yt-dlp）
4. AI生成结构化摘要
5. 保存到飞书Base
6. 更新处理记录
"""

import argparse
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from openai import OpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliSummarizer:
    """B站视频总结器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.processed_videos = self._load_processed_videos()

        # 创建必要目录
        for dir_path in self.config["paths"].values():
            os.makedirs(dir_path, exist_ok=True)

        # 初始化 AI 客户端
        self.ai_client = self._init_ai_client()

        # 加载飞书配置
        self.feishu_config = self._load_feishu_config()
        self.tenant_access_token = None

    def _init_ai_client(self) -> Optional[OpenAI]:
        """初始化 DeepSeek AI 客户端"""
        ai_config = self.config.get("ai", {})
        api_key_env = ai_config.get("api_key_env", "DEEPSEEK_API_KEY")
        api_key = os.environ.get(api_key_env)

        if not api_key:
            logger.warning(f"{api_key_env} 未设置，AI摘要功能将不可用")
            return None

        try:
            client = OpenAI(
                api_key=api_key,
                base_url=ai_config.get("base_url", "https://api.deepseek.com")
            )
            logger.info(f"✅ AI 客户端初始化成功 ({ai_config.get('provider', 'deepseek')})")
            return client
        except Exception as e:
            logger.error(f"AI 客户端初始化失败: {e}")
            return None

    def _load_feishu_config(self) -> Dict:
        """加载飞书用户配置"""
        config_path = os.path.expanduser("~/.feishu_user_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)

        # 如果配置文件不存在，尝试从环境变量读取
        env_app_id = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
        env_app_secret = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
        env_refresh_token = os.getenv("FEISHU_REFRESH_TOKEN") or os.getenv("LARK_REFRESH_TOKEN")
        env_chat_id = os.getenv("FEISHU_CHAT_ID") or os.getenv("LARK_CHAT_ID")
        env_user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN") or os.getenv("LARK_USER_ACCESS_TOKEN")
        env_user_open_id = os.getenv("FEISHU_USER_OPEN_ID") or os.getenv("LARK_USER_OPEN_ID")
        env_expires_at = os.getenv("FEISHU_TOKEN_EXPIRES_AT") or os.getenv("LARK_TOKEN_EXPIRES_AT")

        if env_app_id and env_app_secret:
            config = {
                "app_id": env_app_id,
                "app_secret": env_app_secret
            }
            if env_refresh_token:
                config["refresh_token"] = env_refresh_token
            if env_chat_id:
                config["chat_id"] = env_chat_id
            if env_user_access_token:
                config["user_access_token"] = env_user_access_token
            if env_user_open_id:
                config["user_open_id"] = env_user_open_id
            if env_expires_at:
                try:
                    config["expires_at"] = int(env_expires_at)
                except ValueError:
                    pass
            return config

        return {}

    def _check_cookie_expiry(self):
        """检查 Cookie 过期时间，提前7天提醒"""
        import time
        cookies_file = Path("cookies.txt")

        if not cookies_file.exists():
            return

        try:
            with open(cookies_file, 'r') as f:
                for line in f:
                    if line.startswith('.bilibili.com') and 'SESSDATA' in line:
                        parts = line.strip().split('\t')
                        if len(parts) >= 6:
                            # SESSDATA 的过期时间在第5列（索引4）
                            expiry_timestamp = int(parts[4])
                            current_time = int(time.time())
                            days_left = (expiry_timestamp - current_time) // 86400

                            if days_left <= 7:
                                logger.warning(f"⚠️ B站 Cookie 将在 {days_left} 天后过期！")
                                self._send_cookie_expiry_warning(days_left, expiry_timestamp)
                            else:
                                logger.info(f"✅ Cookie 有效期还有 {days_left} 天")
                            break
        except Exception as e:
            logger.error(f"检查 Cookie 过期时间失败: {e}")

    def _send_cookie_expiry_warning(self, days_left: int, expiry_timestamp: int):
        """发送 Cookie 过期提醒到飞书"""
        try:
            from datetime import datetime
            expiry_date = datetime.fromtimestamp(expiry_timestamp).strftime("%Y-%m-%d")

            notify_config = self.config.get("feishu", {}).get("notification", {})
            if not notify_config.get("enabled", False):
                return

            token = self._get_valid_user_token()
            if not token:
                return

            card_content = {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "⚠️ B站Cookie即将过期提醒"
                    },
                    "template": "orange"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**剩余时间**\n{days_left} 天\n\n**过期日期**\n{expiry_date}\n\n**建议操作**\n1. 打开 B站 并登录\n2. 使用浏览器扩展导出新的 cookies.txt\n3. 覆盖项目目录下的 cookies.txt 文件"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": "Cookie 过期后将无法提取视频字幕，请及时更新！"
                        }
                    }
                ]
            }

            chat_id = notify_config.get("chat_id")
            if chat_id:
                url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
                payload = {
                    "receive_id": chat_id,
                    "msg_type": "interactive",
                    "content": json.dumps(card_content)
                }

                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8"
                }

                response = requests.post(url, headers=headers, json=payload, timeout=10)
                result = response.json()

                if result.get("code") == 0:
                    logger.info("✅ Cookie 过期提醒已发送")
                else:
                    logger.warning(f"提醒发送失败: {result.get('msg')}")

        except Exception as e:
            logger.error(f"发送 Cookie 过期提醒异常: {e}")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            logger.error(f"配置文件不存在: {self.config_path}")
            logger.info("请复制 config.json.template 并填入配置")
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_processed_videos(self) -> set:
        """加载已处理视频ID"""
        db_path = Path(self.config["processed_videos_db"])
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()

    def _save_processed_videos(self):
        """保存已处理视频ID"""
        db_path = Path(self.config["processed_videos_db"])
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(list(self.processed_videos), f, ensure_ascii=False, indent=2)

    def _parse_favlist_url(self, url: str) -> Dict[str, str]:
        """解析收藏夹URL，提取UID和收藏夹ID"""
        import re
        # 匹配 URL: https://space.bilibili.com/UID/favlist?fid=收藏夹ID
        match = re.search(r'space\.bilibili\.com/(\d+)/favlist\?fid=(\d+)', url)
        if match:
            return {"uid": match.group(1), "fid": match.group(2)}
        return {}

    def fetch_favlist_videos(self) -> List[Dict]:
        """获取收藏夹视频列表"""
        logger.info("正在获取收藏夹视频列表...")

        favlist_url = self.config.get("favlist_url", "")
        if not favlist_url:
            logger.error("请配置 favlist_url")
            return []

        # 解析URL获取收藏夹ID
        url_parts = self._parse_favlist_url(favlist_url)
        if not url_parts:
            logger.error(f"无法解析收藏夹URL: {favlist_url}")
            return []

        media_id = url_parts["fid"]
        uid = url_parts["uid"]

        # B站API端点
        api_url = "https://api.bilibili.com/x/v3/fav/resource/list"
        folder_api = "https://api.bilibili.com/x/v3/fav/folder/created/list"

        # B站API需要的请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": f"https://space.bilibili.com/{uid}/favlist",
            "Accept": "application/json, text/plain, */*"
        }

        videos = []
        seen = set()
        page = 1
        page_size = 20  # 每页视频数量
        scan_all = bool(self.config.get("scan_all_favlists", False))

        # 读取 cookies（用于访问私密收藏夹）
        cookies = {}
        cookies_file = Path("cookies.txt")
        if cookies_file.exists():
            for line in cookies_file.read_text().splitlines():
                line = line.strip()
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]

        media_ids = [media_id]
        if scan_all:
            try:
                resp = requests.get(folder_api, params={"up_mid": uid, "pn": 1, "ps": 50}, headers=headers, cookies=cookies, timeout=10)
                resp.raise_for_status()
                folder_list = resp.json().get("data", {}).get("list", [])
                media_ids = [str(f.get("id")) for f in folder_list if f.get("id")]
            except Exception as e:
                logger.error(f"获取收藏夹列表失败: {e}")
                media_ids = [media_id]

        try:
            for mid in media_ids:
                page = 1
                while True:
                    params = {
                        "media_id": mid,
                        "pn": page,
                        "ps": page_size
                    }

                    response = requests.get(api_url, params=params, headers=headers, cookies=cookies, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") != 0:
                        logger.error(f"B站API返回错误: {data.get('message', 'Unknown error')}")
                        break

                    # 解析视频列表
                    data_list = data.get("data", {}).get("medias", [])
                    if not data_list:
                        break  # 没有更多视频

                    for item in data_list:
                        # B站API中type=2表示视频，type=1或其他可能是文章
                        # 跳过非视频类型（如文章）
                        item_type = item.get("type")
                        if item_type != 2 and item_type != "video":
                            logger.info(f"跳过非视频类型: {item_type}")
                            continue

                        bvid = item.get("bv_id", item.get("bvid", ""))
                        if bvid in seen:
                            continue
                        seen.add(bvid)

                        # 视频信息直接在 item 中，不是 info 字段
                        # 根据实际 API 响应结构提取字段
                        videos.append({
                            "bvid": bvid,
                            "title": item.get("title", ""),
                            "author": item.get("upper", {}).get("name", ""),
                            "duration": item.get("duration", 0),  # 秒数，不需要解析
                            "url": f"https://www.bilibili.com/video/{bvid}",
                            "pubtime": item.get("pubtime", item.get("ptime", 0)),
                            "fav_time": item.get("fav_time", 0),
                            "cover": item.get("cover", "")
                        })

                    logger.info(f"第{page}页: 获取到 {len(data_list)} 个视频")

                    # 检查是否还有更多页
                    total_count = data.get("data", {}).get("info", {}).get("media_count", 0)
                    if page * page_size >= total_count:
                        break

                    page += 1

            logger.info(f"共获取到 {len(videos)} 个视频")

        except requests.RequestException as e:
            logger.error(f"请求B站API失败: {e}")
        except Exception as e:
            logger.error(f"获取视频列表异常: {e}")

        return videos

    def _parse_duration(self, duration_str: str) -> int:
        """解析时长字符串为秒数"""
        if not duration_str:
            return 0

        parts = duration_str.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0

    def filter_new_videos(self, videos: List[Dict]) -> List[Dict]:
        """筛选需要处理的新视频"""
        min_duration = self.config["min_duration_minutes"] * 60
        # 自动跳过“今天之前收藏”的旧视频，避免收藏夹切换导致重复
        try:
            from datetime import datetime
            start_of_today = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        except Exception:
            start_of_today = 0

        new_videos = []
        for video in videos:
            # 筛选条件
            if video["bvid"] in self.processed_videos:
                logger.info(f"跳过已处理: {video['title']} ({video['bvid']})")
                continue

            if video["duration"] < min_duration:
                logger.info(f"跳过短视频: {video['title']} ({video['duration']}秒)")
                continue

            fav_time = video.get("fav_time", 0) or 0
            if start_of_today and fav_time and fav_time < start_of_today:
                self.processed_videos.add(video["bvid"])
                logger.info(f"跳过旧收藏视频: {video['title']} ({video['bvid']})")
                continue

            new_videos.append(video)

        # 如果有新增标记，落盘
        self._save_processed_videos()
        logger.info(f"找到 {len(new_videos)} 个新视频待处理")
        return new_videos

    def extract_subtitle(self, bvid: str) -> Optional[str]:
        """提取视频字幕"""
        logger.info(f"正在提取字幕: {bvid}")

        subtitle_dir = Path(self.config["paths"]["subtitles_dir"])
        subtitle_file = subtitle_dir / f"{bvid}.srt"
        video_url = f"https://www.bilibili.com/video/{bvid}"

        # 使用 yt-dlp 提取字幕
        # 优先使用系统可用的 yt-dlp，其次使用 python -m yt_dlp（避免固定到 Python 3.9）
        yt_dlp_path = "yt-dlp"
        yt_dlp_cmd = None
        try:
            import shutil
            if shutil.which(yt_dlp_path):
                yt_dlp_cmd = [yt_dlp_path]
            else:
                yt_dlp_cmd = ["/opt/homebrew/bin/python3.11", "-m", "yt_dlp"]
        except Exception:
            yt_dlp_cmd = ["/opt/homebrew/bin/python3.11", "-m", "yt_dlp"]

        # 优先使用 cookies 文件，否则尝试浏览器 cookie
        cookies_file = Path("cookies.txt")
        cmd = [
            *yt_dlp_cmd,
            "--skip-download",
            "--write-sub",  # 写入字幕（非自动字幕）
            "--sub-lang", "ai-zh",  # B站AI生成中文字幕
            "--sub-format", "srt",
            "-o", str(subtitle_file.with_suffix("")),
        ]

        # 添加 cookie 参数
        if cookies_file.exists():
            cmd.extend(["--cookies", str(cookies_file)])
            logger.debug("使用 cookies.txt 文件")
        else:
            cmd.append("--cookies-from-browser")
            cmd.append("chrome")
            logger.debug("使用浏览器 Cookie")

        cmd.append(video_url)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # yt-dlp 会创建 {bvid}.ai-zh.srt 文件
            actual_subtitle_file = subtitle_dir / f"{bvid}.ai-zh.srt"

            if result.returncode == 0 and actual_subtitle_file.exists():
                logger.info(f"字幕提取成功: {actual_subtitle_file}")
                with open(actual_subtitle_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 重命名为标准文件名
                if actual_subtitle_file != subtitle_file:
                    actual_subtitle_file.rename(subtitle_file)
                return content
            else:
                logger.warning(f"字幕提取失败: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"字幕提取超时: {bvid}")
            return None
        except Exception as e:
            logger.error(f"字幕提取异常: {e}")
            return None

    def generate_summary(self, transcript: str, video_info: Dict) -> Optional[str]:
        """生成AI摘要（使用 DeepSeek API）"""
        if not self.ai_client:
            logger.error("AI 客户端未初始化，无法生成摘要")
            return None

        logger.info(f"开始生成摘要: {video_info['title']}")

        # 分段处理长字幕
        max_length = 50000
        chunks = self._split_text(transcript, max_length)
        logger.info(f"字幕分为 {len(chunks)} 段处理")

        # 收集所有核心观点
        all_key_points = []

        for i, chunk in enumerate(chunks):
            logger.info(f"处理字幕段 {i+1}/{len(chunks)}...")

            prompt = f"""请从以下B站视频字幕中提取核心内容，要求详细、易懂：

视频：{video_info['title']}
作者：{video_info['author']}

字幕内容：
{chunk}

请按以下要求提取：
1. 如果是教程类视频（how-to），请提取具体步骤，每步都要详细
2. 如果有观点，请完整描述观点的背景、论据和结论
3. 如果有技术术语，请用中学生能理解的语言解释
4. 每个要点要独立完整，包含必要的上下文

请只输出要点列表，每项一行，不要编号，不要其他内容。"""

            try:
                response = self.ai_client.chat.completions.create(
                    model=self.config["ai"]["model"],
                    messages=[
                        {"role": "system", "content": "你是专业的视频内容分析助手，擅长提取核心观点。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=self.config["ai"].get("temperature", 0.7)
                )

                content = response.choices[0].message.content.strip()
                points = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 2]
                all_key_points.extend(points)
                logger.info(f"  提取到 {len(points)} 个观点")

            except Exception as e:
                logger.error(f"  AI 调用失败: {e}")
                continue

        if not all_key_points:
            logger.error("未能提取任何核心观点")
            return None

        # 生成最终结构化摘要
        logger.info("生成最终结构化摘要...")
        summary_prompt = f"""基于以下核心要点，为B站视频生成详细、易懂的结构化摘要：

视频标题：{video_info['title']}
作者：{video_info['author']}
时长：{self._format_duration(video_info['duration'])}

核心要点：
{chr(10).join(f"- {p}" for p in all_key_points[:15])}

请按以下格式和要求生成摘要：

# {video_info['title']}

## 基本信息
- 视频ID: {video_info['bvid']}
- 作者: {video_info['author']}
- 时长: {self._format_duration(video_info['duration'])}
- URL: {video_info['url']}

## 核心观点
（如果是教程，按步骤列出；如果是观点，完整描述背景、论据、结论）

## 关键结论
（总结视频的核心价值和应用场景）

要求：
1. 教程类要详细写出每个步骤
2. 技术术语用中学生能理解的语言解释
3. 观点要包含完整的论证过程
4. 语言要通俗易懂，避免过于专业的表述

请严格按照上述格式输出。"""

        try:
            response = self.ai_client.chat.completions.create(
                model=self.config["ai"]["model"],
                messages=[
                    {"role": "system", "content": "你是专业的视频内容总结助手，擅长生成结构化摘要。"},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=self.config["ai"].get("max_tokens", 2000),
                temperature=self.config["ai"].get("temperature", 0.7)
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ 摘要生成成功，字数: {len(summary)}")
            return summary

        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return None

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """智能分段（避免在句子中间分割）"""
        if len(text) <= max_length:
            return [text]

        chunks = []
        current = ""
        sentences = text.split('。')  # 按句子分割

        for sentence in sentences:
            if len(current) + len(sentence) < max_length:
                current += sentence + '。'
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence + '。'

        if current:
            chunks.append(current.strip())

        return chunks

    def _parse_summary(self, summary: str) -> tuple:
        """解析摘要，提取核心观点和关键结论"""
        key_points = []
        conclusions = []

        current_section = None
        lines = summary.split('\n')

        for line in lines:
            line_stripped = line.strip()

            # 跳过标题行
            if line_stripped.startswith('#'):
                if '## 核心观点' in line_stripped or '核心观点' in line_stripped:
                    current_section = 'key_points'
                elif '## 关键结论' in line_stripped or '关键结论' in line_stripped:
                    current_section = 'conclusions'
                continue

            # 提取内容
            if line_stripped and current_section:
                # 清理列表标记（1. 2. - 等）
                cleaned = line_stripped
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*', '#']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):].strip()
                        break

                if cleaned and len(cleaned) > 2:  # 忽略太短的内容
                    if current_section == 'key_points':
                        key_points.append(cleaned)
                    elif current_section == 'conclusions':
                        conclusions.append(cleaned)

        return key_points, conclusions

    def save_to_feishu(self, summary: str, video_info: Dict, transcript: str = None) -> bool:
        """保存到飞书Base（优先使用 tenant_access_token）"""
        logger.info(f"正在保存到飞书: {video_info['title']}")

        # 解析摘要
        key_points, conclusions = self._parse_summary(summary)

        # 构建飞书字段数据
        field_mapping = self.config["feishu"]["field_mapping"]
        fields = {
            field_mapping["title"]: video_info.get("title", ""),
            field_mapping["bvid"]: video_info.get("bvid", ""),
            # URL字段使用对象格式: {"link": "url"}
            # 如果字段映射中有URL字段且飞书表格中该字段类型为URL，则使用对象格式
            # field_mapping["url"]: {"link": video_info.get("url", "")},
            field_mapping["author"]: video_info.get("author", ""),
            field_mapping["duration"]: self._format_duration(video_info.get("duration", 0)),
            field_mapping["key_points"]: "\n".join(key_points) if key_points else "",
            field_mapping["conclusions"]: "\n".join(conclusions) if conclusions else "",
            field_mapping["processed_at"]: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 添加逐字稿（如果存在）
        if transcript and "transcript" in field_mapping:
            fields[field_mapping["transcript"]] = transcript

        # 获取 tenant_access_token（应用身份）
        token = self._get_tenant_access_token()
        if not token:
            logger.error("无法获取有效的 tenant_access_token")
            # 备份到本地
            return self._backup_to_local(video_info, summary, fields, transcript)

        # 调用飞书 API
        app_token = self.config["feishu"]["app_token"]
        table_id = self.config["feishu"]["table_id"]

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload = {"fields": fields}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    logger.info("✅ 成功保存到飞书")
                    return True
                else:
                    logger.error(f"飞书API错误: {data.get('msg')}")
                    return self._backup_to_local(video_info, summary, fields)
            else:
                logger.error(f"HTTP错误: {response.status_code}")
                return self._backup_to_local(video_info, summary, fields)

        except Exception as e:
            logger.error(f"保存到飞书失败: {e}")
            return self._backup_to_local(video_info, summary, fields)

    def _get_tenant_access_token(self) -> Optional[str]:
        """获取 tenant_access_token（应用身份）"""
        if self.tenant_access_token:
            return self.tenant_access_token

        app_id = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
        if not app_id or not app_secret:
            logger.error("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")
            return None

        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        payload = {"app_id": app_id, "app_secret": app_secret}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            if data.get("code") != 0:
                logger.error(f"获取 tenant_access_token 失败: {data.get('msg')}")
                return None
            self.tenant_access_token = data.get("app_access_token")
            return self.tenant_access_token
        except Exception as e:
            logger.error(f"获取 tenant_access_token 异常: {e}")
            return None

    def _get_valid_user_token(self) -> Optional[str]:
        """获取有效的 user_access_token（自动刷新）"""
        import time

        config = self.feishu_config
        if not config:
            logger.error("飞书用户配置不存在")
            return None

        current_time = int(time.time())
        expires_at = config.get('expires_at', 0)

        # 如果 token 还有 30 分钟以上有效期，直接返回
        if expires_at - current_time > 1800:
            return config['user_access_token']

        # 需要刷新 token
        logger.info('Token 即将过期，正在刷新...')

        app_id = config.get('app_id')
        app_secret = config.get('app_secret')
        refresh_token = config.get('refresh_token')

        if not all([app_id, app_secret, refresh_token]):
            logger.error("飞书配置不完整，无法刷新 token")
            return None

        # 刷新 user_access_token
        url = 'https://open.feishu.cn/open-apis/authen/v1/refresh_access_token'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'app_id': app_id,
            'app_secret': app_secret
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()

            if result.get('code') != 0:
                logger.error(f'刷新 Token 失败: {result.get("msg")}')
                return None

            # 更新配置
            config['user_access_token'] = result['data']['access_token']
            config['refresh_token'] = result['data']['refresh_token']
            config['expires_at'] = current_time + result['data']['expires_in']

            # 保存配置
            config_path = os.path.expanduser("~/.feishu_user_config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info('✅ Token 刷新成功')
            return config['user_access_token']

        except Exception as e:
            logger.error(f'Token 刷新异常: {e}')
            return None

    def send_notification(self, success_count: int, total_count: int, videos: list):
        """发送飞书通知消息"""
        try:
            # 获取通知接收者
            notify_config = self.config.get("feishu", {}).get("notification", {})
            if not notify_config.get("enabled", False):
                logger.info("通知功能未启用")
                return

            # 获取 user_access_token
            token = self._get_valid_user_token()
            if not token:
                logger.error("无法获取有效的 token，跳过通知")
                return

            # 构建消息内容
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 提取关键观点（从最后一个视频中）
            key_points_preview = ""
            if videos:
                last_video = videos[-1]
                summary = last_video.get("summary", "")
                if "核心观点" in summary:
                    # 提取核心观点部分
                    lines = summary.split("\n")
                    in_section = False
                    preview_lines = []
                    for line in lines:
                        if "核心观点" in line:
                            in_section = True
                            continue
                        if in_section:
                            if line.startswith("##") or line.startswith("关键结论"):
                                break
                            if line.strip():
                                preview_lines.append(line.strip())
                            if len(preview_lines) >= 3:
                                break
                    key_points_preview = "\n".join(preview_lines[:3])

            # 构建卡片消息
            card_content = {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📺 B站视频总结完成"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**处理时间**\n{current_time}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**处理结果**\n{success_count}/{total_count} 成功"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**已处理视频：**\n" + "\n".join([
                                f"- [{v.get('title', 'N/A')}]({v.get('url', '')})"
                                for v in videos[:5]
                            ])
                        }
                    }
                ]
            }

            # 添加关键观点预览
            if key_points_preview:
                card_content["elements"].append({
                    "tag": "hr"
                })
                card_content["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**核心观点预览：**\n{key_points_preview}"
                    }
                })

            # 添加查看 Base 的按钮
            app_token = self.config["feishu"]["app_token"]
            card_content["elements"].append({
                "tag": "hr"
            })
            card_content["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看飞书 Base"
                        },
                        "type": "default",
                        "url": f"https://feishu.cn/base/{app_token}"
                    }
                ]
            })

            # 发送消息
            if notify_config.get("type") == "user":
                # 发送给个人
                open_id = notify_config.get("open_id")
                if open_id:
                    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
                    payload = {
                        "receive_id": open_id,
                        "msg_type": "interactive",
                        "content": json.dumps(card_content)
                    }
            else:
                # 发送到群聊
                chat_id = notify_config.get("chat_id")
                if chat_id:
                    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
                    payload = {
                        "receive_id": chat_id,
                        "msg_type": "interactive",
                        "content": json.dumps(card_content)
                    }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()

            if result.get("code") == 0:
                logger.info("✅ 通知发送成功")
            else:
                logger.warning(f"通知发送失败: {result.get('msg')}")

        except Exception as e:
            logger.error(f"发送通知异常: {e}")

    def _backup_to_local(self, video_info: Dict, summary: str, fields: Dict, transcript: str = None) -> bool:
        """备份到本地"""
        try:
            backup_dir = Path(self.config["paths"]["backup_dir"])
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = backup_dir / f"{video_info.get('bvid', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            backup_data = {
                "video_info": video_info,
                "summary": summary,
                "fields": fields
            }

            # 如果有逐字稿，也保存到备份中
            if transcript:
                backup_data["transcript"] = transcript

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            logger.info(f"已备份到本地: {backup_file}")
            return False

        except Exception as e:
            logger.error(f"本地备份失败: {e}")
            return False

    def _format_duration(self, seconds: int) -> str:
        """格式化时长为可读字符串"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def mark_processed(self, bvid: str):
        """标记视频已处理"""
        self.processed_videos.add(bvid)
        self._save_processed_videos()
        logger.info(f"已标记处理: {bvid}")

    def process_video(self, video: Dict) -> bool:
        """处理单个视频"""
        bvid = video["bvid"]

        try:
            # 提取字幕
            transcript = self.extract_subtitle(bvid)
            if not transcript:
                logger.warning(f"跳过无字幕视频: {video['title']}")
                return False

            # 生成摘要
            summary = self.generate_summary(transcript, video)
            if not summary:
                logger.warning(f"摘要生成失败，跳过写入飞书: {video['title']}")
                return False

            # 保存到飞书（包含逐字稿）
            self.save_to_feishu(summary, video, transcript)

            # 标记已处理
            self.mark_processed(bvid)

            return True

        except Exception as e:
            logger.error(f"处理失败 {bvid}: {e}")
            return False

    def run(self):
        """执行主流程"""
        logger.info("=" * 50)
        logger.info("B站视频自动总结 - 开始执行")
        logger.info("=" * 50)

        # 检查 Cookie 过期时间
        self._check_cookie_expiry()

        # 获取视频列表
        videos = self.fetch_favlist_videos()

        # 筛选新视频
        new_videos = self.filter_new_videos(videos)

        if not new_videos:
            logger.info("没有新视频需要处理")
            return

        # 处理每个视频
        success_count = 0
        processed_videos_info = []  # 收集处理的视频信息

        for video in new_videos:
            logger.info(f"\n处理: {video['title']}")
            if self.process_video(video):
                success_count += 1
                # 收集视频信息用于通知
                processed_videos_info.append({
                    "title": video.get("title", ""),
                    "url": video.get("url", ""),
                    "bvid": video.get("bvid", "")
                })

        logger.info("=" * 50)
        logger.info(f"处理完成: {success_count}/{len(new_videos)} 成功")
        logger.info("=" * 50)

        # 发送通知
        if processed_videos_info:
            self.send_notification(success_count, len(new_videos), processed_videos_info)


def main():
    parser = argparse.ArgumentParser(description="B站视频自动总结工具")
    parser.add_argument("--init", action="store_true", help="初始化配置")
    parser.add_argument("--fetch", action="store_true", help="获取视频列表")
    parser.add_argument("--list-new", action="store_true", help="列出新视频")
    parser.add_argument("--run", action="store_true", help="执行完整流程")
    parser.add_argument("--video", help="处理指定视频")
    parser.add_argument("--config", default="scripts/config.json", help="配置文件路径")

    args = parser.parse_args()

    try:
        summarizer = BilibiliSummarizer(args.config)

        if args.init:
            logger.info("配置文件已创建，请填写配置")
        elif args.fetch:
            videos = summarizer.fetch_favlist_videos()
            print(json.dumps(videos, ensure_ascii=False, indent=2))
        elif args.list_new:
            videos = summarizer.fetch_favlist_videos()
            new_videos = summarizer.filter_new_videos(videos)
            print(json.dumps(new_videos, ensure_ascii=False, indent=2))
        elif args.video:
            # 处理指定视频
            pass
        elif args.run:
            summarizer.run()
        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"执行失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()
