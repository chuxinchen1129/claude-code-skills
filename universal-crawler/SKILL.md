---
name: universal-crawler
description: 通用网页爬虫 - 使用 web_reader MCP 工具爬取任意网页内容，支持 Google 搜索、自定义 URL、批量处理。输出 Markdown 格式。当用户提到"爬虫"、"网页抓取"、"Google 搜索"、"提取网页内容"、"批量爬取"时使用。
version: 1.0.0
created: 2026-02-11
updated: 2026-02-11
---

# Universal Crawler Skill v1.0

> **核心理念**：任意网页，一键抓取
> 使用 web_reader MCP 工具，无反爬限制

---

## 🚀 快速开始

### 基本用法

```bash
# 爬取单个网页
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --url "https://example.com"

# Google 搜索并爬取结果
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --search "Claude Code"

# 批量爬取多个网页
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --urls urls.txt

# 保存到文件
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --url "https://example.com" --output output.md
```

---

## 📋 核心功能

### 1. 单网页爬取 ⭐

```bash
# 爬取网页，自动转换为 Markdown
python3 scripts/crawl.py --url "https://example.com"
```

**输出**：
- 标题
- 正文内容（Markdown 格式）
- 链接列表
- 图片摘要

### 2. Google 搜索爬取

```bash
# 搜索并爬取前 N 个结果
python3 scripts/crawl.py --search "Claude Code" --top 5
```

**功能**：
- 执行 Google 搜索
- 自动爬取搜索结果
- 整合为单一文档

### 3. 批量爬取

```bash
# 从文件读取 URL 列表
python3 scripts/crawl.py --urls urls.txt

# URL 文件格式（每行一个 URL）
# urls.txt:
# https://example.com/page1
# https://example.com/page2
# https://example.com/page3
```

### 4. 高级选项

```bash
# 保留图片（默认仅保留摘要）
python3 scripts/crawl.py --url "https://example.com" --keep-images

# 设置超时（默认 20 秒）
python3 scripts/crawl.py --url "https://example.com" --timeout 30

# 禁用缓存
python3 scripts/crawl.py --url "https://example.com" --no-cache

# 仅提取链接
python3 scripts/crawl.py --url "https://example.com" --links-only
```

---

## 🔧 技术原理

### web_reader MCP 工具

Universal Crawler 使用集成的 `web_reader` MCP 工具：

**特点**：
- ✅ 无反爬限制
- ✅ 自动处理 JavaScript
- ✅ 智能 Markdown 转换
- ✅ 保留结构（标题、列表、表格）

**参数**：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| url | 目标 URL | 必填 |
| timeout | 超时时间（秒） | 20 |
| retain_images | 保留图片 | true |
| no_cache | 禁用缓存 | false |
| return_format | 返回格式 | markdown |

---

## 📂 输出格式

### Markdown 输出

```markdown
# 网页标题

正文内容...

## 链接

- [链接1](https://...)
- [链接2](https://...)

## 图片

- [图片1](https://...)
- [图片2](https://...)
```

### JSON 输出

```bash
# 输出 JSON 格式
python3 scripts/crawl.py --url "https://example.com" --format json
```

---

## 🎯 使用场景

### 场景 1：竞品分析

```bash
# 爬取竞品产品页面
python3 scripts/crawl.py --url "https://competitor.com/product" --output competitor.md
```

### 场景 2：资料收集

```bash
# Google 搜索并收集资料
python3 scripts/crawl.py --search "AI 编程工具 2026" --top 10 --output research.md
```

### 场景 3：批量归档

```bash
# 批量爬取并归档
cat urls.txt | xargs -I {} python3 scripts/crawl.py --url "{}" --output "archive/$(date +%Y%m%d)_{}.md"
```

### 场景 4：内容监控

```bash
# 定时爬取，监控变化
# 添加到 crontab
0 9 * * * python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --url "https://example.com" --output daily/$(date +\%Y\%m\%d).md
```

---

## 📚 参考文档

| 文档 | 内容 | 何时查看 |
|------|------|---------|
| `user-guide.md` | 完整使用指南 | 首次使用 |
| `examples.md` | 实战案例 | 学习用法 |
| `troubleshooting.md` | 问题排查 | 遇到错误 |

---

## ⚠️ 重要注意事项

### 1. 合理使用

- ✅ 仅用于学习研究
- ✅ 遵守 robots.txt
- ❌ 不得用于商业用途
- ❌ 不得恶意攻击

### 2. 请求频率

- 建议间隔 1-2 秒
- 避免同时请求过多
- 遵守网站服务条款

### 3. 数据验证

- 检查输出完整性
- 验证 Markdown 格式
- 必要时手动调整

---

## 🚨 常见问题

### Q1: 网页爬取失败？

**原因**：
- 网络连接问题
- URL 无效
- 超时

**解决**：
```bash
# 增加超时时间
--timeout 60

# 检查 URL 有效性
curl -I "https://example.com"
```

### Q2: Markdown 格式不对？

**原因**：
- 网页结构复杂
- JavaScript 渲染问题

**解决**：
```bash
# 尝试禁用缓存
--no-cache

# 或使用 JSON 格式手动处理
--format json
```

### Q3: Google 搜索无结果？

**原因**：
- 搜索关键词过于具体
- 触发 Google 限制

**解决**：
- 更换搜索关键词
- 减少爬取数量
- 使用 VPN

---

## 🔄 与其他 Skill 集成

### + MediaCrawler

```bash
# 1. Google 搜索找到目标网站
# 2. 使用 Universal Crawler 爬取
# 3. 使用 MediaCrawler 深度采集
```

### + feishu-universal

```bash
# 爬取 → 保存 → 上传飞书
python3 scripts/crawl.py --url "https://example.com" --output temp.md
# 然后使用飞书自动化上传
```

---

**记住**：这个 Skill 基于稳定的 web_reader MCP 工具，无需担心反爬问题！
