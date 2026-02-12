#!/usr/bin/env python3
"""
竞品监控主程序
支持单次扫描和定时守护进程
"""

import os
import sys
import json
import time
import signal
import argparse
import schedule
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from collect_xhs import XHSCollector
from send_feishu import FeishuNotifier


class CompetitorMonitor:
    """竞品监控器"""

    def __init__(self, config_path=None):
        """
        初始化监控器

        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'brands.json'

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.interval_hours = self.config.get('interval_hours', 2)
        self.collector = XHSCollector(config_path)
        self.notifier = FeishuNotifier()

        # 日志目录
        self.log_dir = Path(__file__).parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)

        # PID 文件
        self.pid_file = Path(__file__).parent / 'monitor.pid'

        # 运行标志
        self.running = False

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        # 写入日志文件
        log_file = self.log_dir / f'monitor_{datetime.now().strftime("%Y%m%d")}.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    async def scan_once(self):
        """执行一次扫描"""
        self.log("🔍 开始扫描...")

        try:
            result = await self.collector.scan()

            # 输出扫描结果
            self.log(f"✅ 扫描完成!")
            self.log(f"   - 扫描笔记: {result['total_notes_scanned']} 条")
            self.log(f"   - 扫描评论: {result['total_comments_scanned']} 条")

            if result['competitors_found']:
                self.log(f"   - 发现竞品评论: {sum(result['competitors_found'].values())} 条")
                for brand, count in result['competitors_found'].items():
                    self.log(f"     * {brand}: {count} 条")

                # 发送整合的预警消息（包含所有发现的竞品评论）
                self.log(f"🚨 发送整合预警消息")
                self.notifier.send_alert(result)

            else:
                self.log("   - 未发现竞品评论")

            # 发送扫描总结
            # self.notifier.send_summary(result)  # 整合后不需要额外发送总结

            return result

        except Exception as e:
            self.log(f"❌ 扫描出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_daemon(self):
        """以守护进程运行"""
        # 写入 PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

        self.log(f"🚀 守护进程启动 (PID: {os.getpid()})")
        self.log(f"⏰ 扫描间隔: {self.interval_hours} 小时")

        # 设置定时任务
        schedule.every(self.interval_hours).hours.do(self._run_scan_job)

        # 立即执行一次
        self._run_scan_job()

        # 运行循环
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def _run_scan_job(self):
        """执行扫描任务（包装器）"""
        import asyncio
        asyncio.run(self.scan_once())

    def stop(self):
        """停止监控"""
        self.running = False
        self.log("🛑 监控已停止")

        # 删除 PID 文件
        if self.pid_file.exists():
            self.pid_file.unlink()


def check_running():
    """检查监控是否正在运行"""
    pid_file = Path(__file__).parent / 'monitor.pid'
    if pid_file.exists():
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        # 检查进程是否存在
        try:
            os.kill(pid, 0)
            return pid
        except OSError:
            # 进程不存在，删除 PID 文件
            pid_file.unlink()
            return None
    return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='竞品监控系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --once              # 执行一次扫描
  %(prog)s --daemon            # 启动守护进程
  %(prog)s --start             # 启动监控
  %(prog)s --stop              # 停止监控
  %(prog)s --status            # 查看状态
  %(prog)s --restart           # 重启监控
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--once', action='store_true', help='执行一次扫描')
    group.add_argument('--daemon', action='store_true', help='以守护进程运行')
    group.add_argument('--start', action='store_true', help='启动监控')
    group.add_argument('--stop', action='store_true', help='停止监控')
    group.add_argument('--status', action='store_true', help='查看状态')
    group.add_argument('--restart', action='store_true', help='重启监控')

    args = parser.parse_args()

    import asyncio

    # 单次扫描
    if args.once:
        monitor = CompetitorMonitor()
        asyncio.run(monitor.scan_once())
        return

    # 查看状态
    if args.status:
        pid = check_running()
        if pid:
            print(f"✅ 监控正在运行 (PID: {pid})")
            sys.exit(0)
        else:
            print("❌ 监控未运行")
            sys.exit(1)

    # 停止监控
    if args.stop:
        pid = check_running()
        if pid:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ 监控已停止 (PID: {pid})")
        else:
            print("❌ 监控未运行")
        return

    # 启动监控
    if args.start:
        pid = check_running()
        if pid:
            print(f"⚠️  监控已在运行 (PID: {pid})")
            sys.exit(1)

        print("正在启动监控...")
        # Fork 守护进程
        if os.fork() > 0:
            print(f"✅ 监控已启动")
            sys.exit(0)

        # 子进程
        os.setsid()
        if os.fork() > 0:
            sys.exit(0)

        # 重定向标准输出
        sys.stdout.flush()
        sys.stderr.flush()

        monitor = CompetitorMonitor()
        monitor.run_daemon()
        return

    # 重启监控
    if args.restart:
        pid = check_running()
        if pid:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)

        print("正在重启监控...")
        if os.fork() > 0:
            print(f"✅ 监控已重启")
            sys.exit(0)

        os.setsid()
        if os.fork() > 0:
            sys.exit(0)

        sys.stdout.flush()
        sys.stderr.flush()

        monitor = CompetitorMonitor()
        monitor.run_daemon()
        return

    # 守护进程模式（前台）
    if args.daemon:
        pid = check_running()
        if pid:
            print(f"⚠️  监控已在运行 (PID: {pid})")
            sys.exit(1)

        monitor = CompetitorMonitor()
        monitor.run_daemon()
        return


if __name__ == '__main__':
    main()
