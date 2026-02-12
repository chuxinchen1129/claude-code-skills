#!/usr/bin/env python3
"""
监控指定小红书笔记的评论，检测竞品品牌
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

class NoteMonitor:
    """笔记评论监控器"""
    
    def __init__(self, config_path=None):
        """初始化监控器"""
        SKILL_DIR = Path(__file__).parent.parent
        if config_path is None:
            config_path = SKILL_DIR / "config" / "brands.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.competitors = self.config.get('competitors', [])
        print(f"✅ 监控品牌: {', '.join(self.competitors)}")
    
    def check_comments_for_brands(self, note_data):
        """
        检查笔记评论中是否包含竞品品牌
        
        Args:
            note_data: 笔记数据，包含评论列表
        
        Returns:
            list: 包含竞品的评论
        """
        results = []
        
        # 从笔记数据中提取评论
        comments = self._extract_comments(note_data)
        
        # 检查每条评论
        for comment in comments:
            content = self._get_comment_content(comment)
            
            # 检查是否包含竞品关键词
            for brand in self.competitors:
                if brand in content:
                    results.append({
                        'brand': brand,
                        'comment': content,
                        'user': self._get_comment_user(comment),
                        'time': self._get_comment_time(comment),
                        'note_id': note_data.get('note_id', ''),
                        'note_title': note_data.get('title', '')
                    })
                    break
        
        return results
    
    def _extract_comments(self, note_data):
        """从笔记数据中提取评论"""
        comments = []
        
        # 检查多种可能的评论字段
        if 'comments' in note_data:
            comments = note_data['comments']
        elif 'comment_list' in note_data:
            comments = note_data['comment_list']
        elif 'raw_data' in note_data:
            raw = note_data['raw_data']
            if 'comments' in raw:
                comments = raw['comments']
            elif 'comment_list' in raw:
                comments = raw['comment_list']
        
        return comments if isinstance(comments, list) else []
    
    def _get_comment_content(self, comment):
        """获取评论内容"""
        if isinstance(comment, str):
            return comment
        if isinstance(comment, dict):
            return comment.get('content') or comment.get('text') or comment.get('comment_content') or comment.get('desc', '')
        return ''
    
    def _get_comment_user(self, comment):
        """获取评论用户"""
        if isinstance(comment, dict):
            if 'user' in comment:
                user = comment['user']
                if isinstance(user, dict):
                    return user.get('nickname', user.get('username', '匿名'))
                return str(user)
            return comment.get('nickname', comment.get('author', '匿名'))
        return '匿名'
    
    def _get_comment_time(self, comment):
        """获取评论时间"""
        if isinstance(comment, dict):
            return comment.get('time') or comment.get('create_time') or comment.get('timestamp', '未知')
        return '未知'
    
    def load_notes_from_file(self, file_path):
        """
        从文件加载笔记数据
        
        Args:
            file_path: JSON 文件路径
        
        Returns:
            list: 笔记列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同的数据格式
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 可能是 {'data': [...]} 格式
            if 'data' in data:
                return data['data']
            # 或者 {'items': [...]} 格式
            if 'items' in data:
                return data['items']
            # 或者是单个笔记
            if 'note_id' in data or 'title' in data:
                return [data]
        
        return []
    
    def scan_note_ids(self, note_ids):
        """
        扫描指定笔记ID列表
        
        Args:
            note_ids: 笔记ID列表
        
        Returns:
            dict: 扫描结果
        """
        results = {
            'scan_time': datetime.now().isoformat(),
            'notes_scanned': len(note_ids),
            'total_comments_checked': 0,
            'competitor_mentions': []
        }
        
        # 这里我们暂时返回一个占位结果
        # 实际需要从采集的数据中读取
        return results


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("小红书笔记评论监控 - 竞品检测")
    print("=" * 60)
    print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='监控指定小红书笔记的评论')
    parser.add_argument('--note-ids', help='笔记ID列表（逗号分隔）')
    parser.add_argument('--data-file', help='包含笔记数据的JSON文件')
    parser.add_argument('--output', help='输出结果文件')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 初始化监控器
    monitor = NoteMonitor()
    
    if args.data_file:
        print(f"📂 加载数据文件: {args.data_file}")
        notes = monitor.load_notes_from_file(args.data_file)
        print(f"✅ 加载了 {len(notes)} 条笔记数据")
        print()
        
        total_mentions = []
        for note in notes:
            mentions = monitor.check_comments_for_brands(note)
            if mentions:
                print(f"🔍 笔记: {note.get('title', 'N/A')[:50]}")
                print(f"   ID: {note.get('note_id', 'N/A')}")
                for m in mentions:
                    print(f"   ⚠️  发现品牌 '{m['brand']}'")
                    print(f"      用户: {m['user']}")
                    print(f"      内容: {m['comment'][:50]}...")
                    print()
                total_mentions.extend(mentions)
        
        print("=" * 60)
        print(f"📊 扫描结果汇总")
        print(f"   扫描笔记: {len(notes)}")
        print(f"   发现竞品提及: {len(total_mentions)} 条")
        
        if total_mentions:
            brands_found = {}
            for m in total_mentions:
                brand = m['brand']
                brands_found[brand] = brands_found.get(brand, 0) + 1
            
            print(f"   品牌分布:")
            for brand, count in brands_found.items():
                print(f"     - {brand}: {count} 条")
        
        print("=" * 60)
        
        # 保存结果
        if args.output and total_mentions:
            output_data = {
                'scan_time': datetime.now().isoformat(),
                'notes_scanned': len(notes),
                'competitor_mentions': total_mentions,
                'summary': {
                    'total_mentions': len(total_mentions),
                    'brands_found': brands_found
                }
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {args.output}")
    
    elif args.note_ids:
        note_ids = args.note_ids.split(',')
        print(f"📝 监控笔记ID: {len(note_ids)} 个")
        results = monitor.scan_note_ids(note_ids)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    else:
        print("❌ 请提供 --data-file 或 --note-ids 参数")
        print()
        print("使用示例:")
        print("  python monitor_notes.py --data-file notes_data.json")
        print("  python monitor_notes.py --note-ids abc123,def456 --output results.json")


if __name__ == '__main__':
    main()
