#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理器 - 清洗数据、计算互动分、筛选TOP、处理媒体文件
"""

import pandas as pd
import shutil
from pathlib import Path


def convert_count(val):
    """转换互动数为数值"""
    if pd.isna(val) or val == '' or val is None:
        return 0
    if isinstance(val, str) and '万' in val:
        try:
            return float(val.replace('万', '')) * 10000
        except:
            return 0
    try:
        return float(val)
    except:
        return 0


class DataProcessor:
    """数据处理器"""

    def __init__(self):
        pass

    def process(self, json_data, keywords, temp_dir):
        """处理数据并返回TOP笔记和媒体文件"""
        if not json_data:
            print("  没有数据可处理")
            return pd.DataFrame(), []

        # 创建DataFrame
        df = pd.DataFrame(json_data)

        # 处理关键词：支持单个字符串或列表
        if isinstance(keywords, str):
            keyword_list = [keywords]
        else:
            keyword_list = keywords

        # 筛选包含任意关键词的笔记
        def contains_any_keyword(row):
            title = str(row.get('title', ''))
            desc = str(row.get('desc', ''))
            for kw in keyword_list:
                if kw in title or kw in desc:
                    return True
            return False

        df_filtered = df[df.apply(contains_any_keyword, axis=1)]
        print(f"  筛选后: {len(df_filtered)} 条")

        if len(df_filtered) == 0:
            print("  ⚠ 没有找到包含关键词的笔记，使用全部数据")
            df_filtered = df

        # 计算互动总分
        df_filtered['liked_num'] = df_filtered['liked_count'].apply(convert_count)
        df_filtered['collected_num'] = df_filtered['collected_count'].apply(convert_count)
        df_filtered['comment_num'] = df_filtered['comment_count'].apply(convert_count)
        df_filtered['share_num'] = df_filtered['share_count'].apply(convert_count)

        # 计算互动总分（点赞 + 收藏×2 + 评论×3 + 分享×4）
        df_filtered['互动总分'] = (
            df_filtered['liked_num'] +
            df_filtered['collected_num'] * 2 +
            df_filtered['comment_num'] * 3 +
            df_filtered['share_num'] * 4
        )

        # 按互动量降序排列
        df_sorted = df_filtered.sort_values('互动总分', ascending=False)

        # 去重（按note_id）
        df_top = df_sorted.drop_duplicates('note_id').head(30)

        print(f"  TOP {len(df_top)} 条笔记")

        # 处理媒体文件
        media_files = self._process_media_files(df_top, temp_dir)

        # 清理champ文件
        self._cleanup_champ_files(temp_dir)

        return df_top, media_files

    def _process_media_files(self, df_top, temp_dir):
        """处理媒体文件：复制和重命名"""
        # media_data_path从temp_dir推导，指向data/目录
        output_dir = Path(temp_dir).parent
        media_data_path = output_dir / "data"
        # MediaCrawler原始数据路径
        mediacrawler_path = Path("/Users/echochen/Desktop/DMS/01_INFO_COLLECT/采集数据/xhs")

        # 筛选媒体目录中的笔记
        processed = []
        media_data = []

        # 遍历TOP笔记
        for idx, row in df_top.iterrows():
            note_id = row['note_id']
            title = str(row.get('title', ''))
            content_type = '图文' if row.get('type') == 'normal' else '视频'

            # 初始化media_path
            media_path = None

            # 清理标题，移除文件名非法字符
            safe_title = ''.join(c for c in title if c.isalnum() or c in ' _-().，。！？')
            safe_title = safe_title[:50]  # 限制标题长度

            # 优先在输出目录查找（已经下载的媒体）
            image_folder = media_data_path / "images" / note_id
            # 检查是否需要重命名（如果文件夹名只有note_id，没有标题）
            needs_rename = False
            old_folder = None  # 每次循环都重新初始化
            if image_folder.exists():
                # 检查文件夹名是否包含标题（是否有下划线分隔）
                if '_' not in str(image_folder.name):
                    # 这是hash格式，需要重命名
                    needs_rename = True
                    old_folder = image_folder

            # 优先处理重命名（如果需要）
            if needs_rename and old_folder:
                new_folder = media_data_path / "images" / f"{safe_title}_{note_id}"
                try:
                    shutil.move(str(old_folder), str(new_folder))
                    print(f"    重命名图片文件夹: {old_folder.name} -> {new_folder.name}")
                    image_folder = new_folder
                    image_files = list(image_folder.glob("*.jpg"))
                    if image_files:
                        media_path = str(image_files[0])
                except Exception as e:
                    print(f"    重命名失败 {old_folder.name}: {e}")

            if not media_path and not image_folder.exists():
                # 从MediaCrawler原始路径查找并复制
                image_folder = mediacrawler_path / "images" / note_id
                if image_folder.exists():
                    image_files = list(image_folder.glob("*.jpg"))
                    if image_files:
                        # 复制到输出目录，使用新命名格式
                        output_image_folder = media_data_path / "images" / f"{safe_title}_{note_id}"
                        output_image_folder.mkdir(parents=True, exist_ok=True)
                        for img_file in image_files:
                            shutil.copy2(str(img_file), str(output_image_folder / img_file.name))
                        media_path = str(output_image_folder / image_files[0].name)
            elif not media_path and image_folder.exists():
                # 文件夹已存在（可能是hash格式或已正确命名）
                image_files = list(image_folder.glob("*.jpg"))
                if image_files:
                    media_path = str(image_files[0])

            # 如果不是图片，查找视频
            if not media_path:
                # 优先在输出目录查找
                video_files = list((media_data_path / "videos").glob(f"{safe_title}_{note_id}*"))
                if not video_files:
                    # 从MediaCrawler原始路径查找
                    video_files = list((mediacrawler_path / "videos").glob(f"{note_id}*"))
                    for vf in video_files:
                        if not vf.is_dir():
                            # 复制并重命名
                            import shutil
                            new_name = f"{safe_title}_{note_id}{vf.suffix}"
                            shutil.copy2(str(vf), str(media_data_path / "videos" / new_name))
                            media_path = str(media_data_path / "videos" / new_name)
                            break

            if media_path:
                media_data.append({
                    'note_id': note_id,
                    'title': title,
                    'type': content_type,
                    'media_path': media_path
                })
                processed.append(note_id)

            if media_path:
                media_data.append({
                    'note_id': note_id,
                    'title': title,
                    'type': content_type,
                    'media_path': media_path
                })
                processed.append(note_id)

        print(f"  媒体文件: {len(media_data)} 个")
        return media_data

    def _cleanup_champ_files(self, temp_dir):
        """清理champ临时文件"""
        temp_path = Path(temp_dir)
        for champ_file in temp_path.rglob("champ_*.pyc"):
            try:
                champ_file.unlink()
            except:
                pass

    def generate_excel(self, df_top, excel_path, media_files):
        """生成Excel数据表"""
        # 创建媒体路径映射
        media_path_map = {mf['note_id']: mf['media_path'] for mf in media_files}

        # 准备数据
        excel_data = []

        for idx, row in df_top.iterrows():
            note_id = row['note_id']
            title = row.get('title', '')
            desc = row.get('desc', '')
            nickname = row.get('nickname', '')
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            content_type = '图文' if row.get('type') == 'normal' else '视频'

            excel_data.append({
                '排名': idx + 1,
                '互动总分': int(row['互动总分']),
                '点赞数': int(row['liked_num']),
                '收藏数': int(row['collected_num']),
                '评论数': int(row['comment_num']),
                '分享数': int(row['share_num']),
                '标题': title,
                '完整文本': desc if pd.notna(desc) else '',
                '作者': nickname,
                '笔记链接': note_url,
                '内容类型': content_type,
                '媒体路径': media_path_map.get(note_id, '')
            })

        # 创建DataFrame
        df_export = pd.DataFrame(excel_data)

        # 保存Excel
        df_export.to_excel(excel_path, index=False)
        print(f"  已保存 {len(df_export)} 条记录")
