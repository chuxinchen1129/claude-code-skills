# CC生成笔记 - 完整工作流说明

## 概述

"CC生成笔记"功能使用任务队列模式连接飞书机器人和Claude Code，实现完整的baogaomiao工作流。

## 工作流程

```
用户在飞书说"CC生成笔记"
    ↓
飞书机器人接收消息（webhook）
    ↓
bot_server.py 的 handle_cc_generate 处理
    ↓
1. 获取最新PDF文件（从报告喵文件夹）
2. 创建任务文件到 baogaomiao_tasks/ 目录
   - 任务ID：YYYYMMDD_HHMMSS
   - 任务类型：baogaomiao_generate
   - PDF路径：完整路径
   ↓
3. 发送确认消息到飞书
   - 消息包含任务ID
    ↓
用户在Claude Code中说"处理baogaomiao任务"或"完成CC生成"
    ↓
Claude Code检测到新任务文件
    ↓
4. 加载baogaomiao skill
   - 读取PDF内容
   - 生成3步输出：中文标题、英文标题、小红书笔记
    ↓
5. 使用feishu_sender.py自动发送到飞书
    ↓
6. 更新任务状态为completed
    ↓
用户在飞书中收到完整小红书笔记
```

## 文件结构

```
~/.claude/skills/feishu-bot/data/baogaomiao_tasks/
├── task_20260211_143022.json      # 待处理任务
├── task_20260211_143022.json      # 处理中
└── task_20260211_143022.json      # 已完成
```

## 任务文件格式

```json
{
  "task_type": "baogaomiao_generate",
  "pdf_path": "/完整/PDF路径",
  "task_id": "20260211_143022",
  "created_at": "2026-02-11T14:30:22",
  "status": "pending|processing|completed",
  "result_file": "/可选/结果文件路径",
  "result": {
    "chinese_title": "...",
    "english_title": "...",
    "xhs_note": "..."
  }
}
```

## 使用方式

### 方式一：完整自动流程（推荐）

1. **在飞书中发送"CC生成笔记"**
2. **等待机器人响应**（包含任务ID）
3. **在Claude Code中说**："处理baogaomiao任务"
4. **Claude Code自动**：
   - 检测新任务文件
   - 读取PDF并生成XHS笔记
   - 使用baogaomiao skill的feishu_sender发送到飞书
   - 更新任务状态

### 方式二：直接调用（调试用）

在Claude Code中直接说："用baogaomiao处理这个PDF"或直接提供PDF路径。

## 错误处理

| 场景 | 处理方式 |
|-------|----------|
| PDF文件不存在 | 发送错误消息到飞书 |
| PDF提取失败 | 发送错误消息到飞书 |
| 任务创建失败 | 记录日志，返回错误 |

## 代码修改说明

修改了 `bot_server.py` 中的以下部分：

1. **新增导入**：
   ```python
   from scripts.feishu_sender import FeishuSender, format_xhs_note
   ```

2. **BaogaomiaoGenerator.generate_note() 重写**：
   - 不再直接调用pdf_extractor
   - 改为创建任务文件模式
   - 任务文件保存到 `data/baogaomiao_tasks/`

3. **handle_cc_generate() 更新**：
   - 使用新的generate_note()返回结果
   - 发送包含任务ID的消息

## Claude Code端处理（待实现）

Claude Code需要实现以下逻辑来处理任务：

1. **检测新任务**：
   ```python
   from pathlib import Path
   task_dir = Path("~/.claude/skills/feishu-bot/data/baogaomiao_tasks")
   pending_tasks = list(task_dir.glob("task_*.json"))
   # 过滤status=pending的任务
   ```

2. **处理任务**：
   - 读取PDF内容（使用pdf_extractor.py或Read工具）
   - 调用baogaomiao skill生成XHS笔记（3步输出）
   - 使用feishu_sender发送到飞书
   - 更新任务状态为completed

3. **清理旧任务**：
   - 定期清理已完成的任务文件
   - 或根据任务ID更新而不是新建

## 注意事项

1. **bot_server.py必须运行**：webhook才能接收飞书消息
2. **Claude Code需要监听**：可以通过定时任务或手动触发
3. **任务文件位置**：确保目录存在且有写权限
4. **飞书发送配置**：确保feishu_sender.py能正确发送消息

## 与MediaCrawler集成的关系

"CC生成笔记"功能独立于MediaCrawler采集功能：

- **CC生成笔记**：PDF → XHS笔记 → 飞书
- **MediaCrawler采集**：小红书/抖音链接 → 采集数据 → 导入飞书

两者在同一个bot_server.py中并行运行，互不干扰。

## 调试

```bash
# 查看任务文件
ls -la ~/.claude/skills/feishu-bot/data/baogaomiao_tasks/

# 查看bot日志
tail -f ~/.claude/skills/feishu-bot/logs/*.log

# 测试bot
curl -X POST http://localhost:5001/webhook -d '{"event":{"sender":{"sender_id":{"open_id":"test"}}}'
```

## 更新历史

- **v1.0 (2026-02-11)**: 初始实现
  - 任务队列模式
  - PDF提取
  - 任务文件创建
  - 飞书消息发送
