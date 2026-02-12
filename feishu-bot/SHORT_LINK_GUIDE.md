# 短链接解析功能使用指南

**功能概述**：自动解析小红书短链接，调用 MediaCrawler 采集笔记和评论

---

## 🎯 使用流程

### 1. 从微信/小红书发送短链接到 OpenClaw

### 2. OpenClaw 通过飞书转发给你

### 3. 系统自动：
- 解析短链接获取笔记ID
- 配置 MediaCrawler 采集
- 采集完成后保存到本地
- 通过飞书发送结果通知

---

## 📋 技术架构

```
微信/小红书
    ↓
OpenClaw
    ↓
飞书
    ↓
bot_server.py (flask)
    ↓
short_link_resolver.py (解析模块)
    ↓
MediaCrawler (采集)
    ↓
本地文件保存
```

---

## 🔧 核心组件

### 1. short_link_resolver.py

**功能**：
- 单个短链接解析
- 批量短链接解析
- MediaCrawler 配置生成

**位置**：`~/.claude/skills/feishu-bot/scripts/short_link_resolver.py`

**使用示例**：
```python
from short_link_resolver import ShortLinkResolver

resolver = ShortLinkResolver()

# 解析单个链接
result = resolver.resolve_xhs_short_link("http://xhslink.com/o/xxx")
# 返回: {success: True, note_id: "xxx", full_url: "..."}

# 批量解析
results = resolver.batch_resolve_links([
    "http://xhslink.com/o/xxx",
    "http://xhslink.com/o/yyy"
])
```

### 2. bot_server.py

**已更新**：添加了 `short_link_resolver` 模块导入

**关键更新**：
```python
# 导入短链接解析器
from short_link_resolver import ShortLinkResolver

# 在 MessageHandler 类中初始化
class MessageHandler:
    def __init__(self):
        # ... 原有代码 ...
        self.short_resolver = ShortLinkResolver()
```

---

## 🚀 快速开始

### 测试短链接解析功能

```bash
cd ~/.claude/skills/feishu-bot/scripts
python3 -c "
from short_link_resolver import ShortLinkResolver
resolver = ShortLinkResolver()
result = resolver.resolve_xhs_short_link('http://xhslink.com/o/9BIu7Qm6rEy')
print(json.dumps(result, indent=2))
"
```

### 测试完整流程

```bash
# 启动飞书机器人
cd ~/.claude/skills/feishu-bot/scripts
python3 bot_server.py

# 然后在飞书中发送测试短链接：
http://xhslink.com/o/test123
```

---

## 📊 支持的短链接格式

| 格式 | 示例 | 解析结果 |
|------|------|----------|
| `xhslink.com/o/xxx` | ✅ 完全支持 | 返回笔记ID |
| `www.xiaohongshu.com/explore/xxx` | ✅ 完全支持 | 直接使用 |
| 含 `xsec_token` | ✅ 推荐 | 采集成功率更高 |

---

## ⚠️ 注意事项

### 1. 登录状态

MediaCrawler 需要有效登录状态才能采集评论：
- 检查：`~/MediaCrawler/browser_data/xhs_user_data_dir/`
- 如已过期，需要重新扫码登录

### 2. URL 有效性

短链接有时效性（通常24小时）：
- 如果解析失败，说明链接已过期
- 建议从原始平台重新复制链接

### 3. 采集限制

- 每次采集建议不超过 20 条笔记
- 批量大采集会触发限流

---

## 🔄 完整工作流示例

### 场景：监控竞品评论

```
# 1. 你在微信看到竞品相关笔记
# 2. 复制短链接发送到飞书
# 3. OpenClaw 转发给你
# 4. 机器人自动解析并采集
# 5. 完成后飞书通知你结果
```

**预期效果**：
- ✅ 自动解析短链接
- ✅ 自动采集笔记和评论
- ✅ 搜索"左点"等竞品关键词
- ✅ 生成报告并发送飞书

---

## 📞 相关文件

| 文件 | 路径 |
|------|------|
| 短链接解析器 | `~/.claude/skills/competitor-alert/scripts/parse_short_links.py` |
| 飞书机器人 | `~/.claude/skills/feishu-bot/scripts/bot_server.py` |
| MediaCrawler | `~/MediaCrawler/` |

---

**创建时间**：2026-02-11
**版本**：v1.0
