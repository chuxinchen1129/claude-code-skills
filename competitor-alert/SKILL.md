---
name: competitor-alert
description: "小红书竞品评论监控预警系统。检查小红书笔记中的竞品品牌评论，发现后通过飞书推送预警。支持短链接批量检查和定时监控。使用场景：监控竞品、检查竞品评论、分析竞品提及。当用户提到"竞品监控"、"监控竞品"、"检查竞品评论"、"竞品提及"时使用。"
version: 2.0.0
updated: 2026-03-01
---

# 竞品预警系统

监控小红书笔记中的竞品品牌评论，发现后通过飞书推送预警。

---

## 最常用命令（5秒上手）

```bash
cd ~/.claude/skills/competitor-alert/scripts

# 方式1：检查短链接 ⭐ 最常用
python3 parse_short_links.py --links "链接列表"

# 方式2：定时监控
python3 monitor.py --start

# 方式3：单次扫描
python3 monitor.py --once
```

---

## 使用方式

### 方式A：批量检查短链接 ⭐ 推荐

直接提供小红书链接，自动解析并检查竞品评论。

**使用示例：**
```
用户："检查这些链接是否有'左点'评论：
http://xhslink.com/o/9BIu7Qm6rEy
http://xhslink.com/o/5ABFH6YLT5J"
```

**处理流程：**
1. 解析短链接 → 获取笔记ID
2. 采集笔记评论
3. 搜索竞品品牌（强脑、左点、温致）
4. 生成报告 → 发送飞书预警

**支持的输入格式：**
- 纯短链接：`http://xhslink.com/xxxxx`
- 混合文本：`春节送礼！http://xhslink.com/xxxxx`
- 笔记ID：直接指定笔记ID列表

---

### 方式B：定时监控

自动定期扫描"悟昕睡眠仪"相关笔记。

**使用示例：**
```
用户："开始监控，每2小时检查一次"
```

**命令：**
```bash
# 启动监控
python3 monitor.py --start

# 停止监控
python3 monitor.py --stop

# 查看状态
python3 monitor.py --status
```

---

## 配置（首次使用）

### 1. 飞书配置

编辑 `config/feishu_config.json`：
```json
{
  "app_id": "你的APP_ID",
  "app_secret": "你的APP_SECRET",
  "user_open_id": "你的OPEN_ID"
}
```

### 2. 监控品牌

编辑 `config/brands.json`：
```json
{
  "keywords": ["悟昕睡眠仪"],
  "competitors": ["强脑", "左点", "温致"],
  "interval_hours": 2,
  "max_notes": 10
}
```

---

## 命令速查

| 命令 | 说明 |
|-------|------|
| `parse_short_links.py --links "..."` | 解析短链接并检查评论 |
| `monitor.py --start` | 启动定时监控 |
| `monitor.py --stop` | 停止监控 |
| `monitor.py --status` | 查看监控状态 |
| `monitor.py --once` | 执行单次扫描 |
| `tail -f logs/monitor.log` | 查看日志 |

---

## 预警格式

### 飞书消息
```
🚨 竞品评论预警

品牌：左点
来源：小红书笔记《学习vlog》
链接：https://www.xiaohongshu.com/...

评论：用户@xxx："想get同款的可以上🍑🔍左点"

发现时间：2026-02-12 14:30
```

### 扫描总结
```
📊 扫描总结

扫描范围：10条笔记
发现竞品评论：4条
涉及竞品：左点(4)
```

---

## 常见问题

### Q: 短链接解析失败（404错误）？
**A:** 链接可能已失效或已删除。可尝试：
- 直接提供笔记ID（24位十六进制）
- 在浏览器中打开链接获取完整URL

### Q: 没有收到飞书通知？
**A:** 检查以下内容：
1. 飞书配置文件是否正确
2. 查看日志：`tail -f logs/monitor.log`
3. 确认网络连接正常

### Q: 采集数据失败？
**A:**
1. 检查 MediaCrawler 登录状态
2. 查看采集日志：`logs/collect_xhs.log`
3. 确认小红书账号正常

### Q: 如何调整监控频率？
**A:** 编辑 `config/brands.json` 中的 `interval_hours` 参数

### Q: 如何添加新的竞品品牌？
**A:** 编辑 `config/brands.json`，在 `competitors` 数组中添加品牌名称

---

## 进阶用法

### 自定义预警规则

编辑 `scripts/monitor.py` 中的过滤逻辑：
```python
def should_alert(comment):
    # 只预警长度超过20字的评论
    if len(comment['content']) < 20:
        return False
    # 只预警包含特定关键词的评论
    return any(brand in comment['content'] for brand in COMPETITORS)
```

### 关闭截图功能

编辑 `config/brands.json`：
```json
{
  "screenshot_enabled": false
}
```

---

**维护者**: Echo Chen
**最后更新**: 2026-02-12
**版本**: 2.0.0
