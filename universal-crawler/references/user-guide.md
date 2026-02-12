# Universal Crawler 使用指南

> **完整指南** - 从入门到精通

---

## 目录

1. [快速开始](#快速开始)
2. [基本用法](#基本用法)
3. [高级功能](#高级功能)
4. [实际案例](#实际案例)
5. [最佳实践](#最佳实践)

---

## 快速开始

### 安装

```bash
# Skill 已内置，无需额外安装
# 确认 MCP 工具可用
ls-skills | grep web_reader
```

### 第一个爬取

```bash
# 爬取单个网页
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --url "https://example.com" \
  --output example.md
```

---

## 基本用法

### 1. 爬取单个网页

```bash
# 基本用法
python3 scripts/crawl.py --url "https://example.com"

# 保存到文件
python3 scripts/crawl.py --url "https://example.com" --output output.md

# 保留图片
python3 scripts/crawl.py --url "https://example.com" --keep-images

# 增加超时
python3 scripts/crawl.py --url "https://example.com" --timeout 60
```

### 2. 批量爬取

```bash
# 创建 URL 文件
cat > urls.txt << EOF
https://example.com/page1
https://example.com/page2
https://example.com/page3
EOF

# 批量爬取
python3 scripts/crawl.py --urls urls.txt --output batch.md
```

### 3. Google 搜索

```bash
# 搜索并爬取前 5 个结果
python3 scripts/crawl.py --search "Claude Code" --top 5

# 爬取前 10 个结果
python3 scripts/crawl.py --search "AI 编程" --top 10 --output research.md
```

---

## 高级功能

### 1. 仅提取链接

```bash
python3 scripts/crawl.py --url "https://example.com" --links-only
```

### 2. JSON 输出

```bash
python3 scripts/crawl.py --url "https://example.com" --format json --output data.json
```

### 3. 禁用缓存

```bash
python3 scripts/crawl.py --url "https://example.com" --no-cache
```

### 4. 自定义输出目录

```bash
python3 scripts/crawl.py --url "https://example.com" --output-dir ~/Downloads/crawl
```

---

## 实际案例

### 案例 1：竞品分析

```bash
# 爬取竞品产品页面
python3 scripts/crawl.py --url "https://competitor.com/product" --output competitor.md

# 分析内容
cat competitor.md
```

### 案例 2：资料收集

```bash
# 搜索并收集 AI 编程相关资料
python3 scripts/crawl.py --search "AI 编程工具 2026" --top 10 --output research.md

# 整理资料
# 使用 data-cleaner 或手动整理
```

### 案例 3：博客归档

```bash
# 批量归档博客文章
cat blog_urls.txt | python3 scripts/crawl.py --urls - --output archive/
```

### 案例 4：定时监控

```bash
# 添加到 crontab
# 每天早上 9 点爬取
0 9 * * * python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --url "https://example.com" --output ~/monitor/$(date +\%Y\%m\%d).md
```

---

## 最佳实践

### 1. 选择合适的超时时间

| 网页类型 | 推荐超时 |
|---------|---------|
| 简单文本 | 10 秒 |
| 普通网页 | 20 秒（默认） |
| 复杂页面 | 30-60 秒 |
| 视频网站 | 60 秒+ |

### 2. 处理特殊网页

**需要登录的网页**：
- Universal Crawler 无法处理需要登录的网页
- 建议手动登录后导出，或使用 MediaCrawler

**JavaScript 重度依赖**：
- 尝试增加超时时间
- 或使用 `--no-cache` 强制刷新

### 3. 批量爬取策略

```bash
# 小批量（推荐）
python3 scripts/crawl.py --urls urls.txt --timeout 30

# 分批处理（大量 URL）
split -l 10 urls.txt chunk_
for chunk in chunk_*; do
  python3 scripts/crawl.py --urls "$chunk" --output "output_$chunk.md"
done
```

### 4. 数据验证

```bash
# 验证 Markdown 格式
cat output.md | head -20

# 统计字数
wc -w output.md

# 检查链接
grep -E "^http" output.md
```

---

## 与其他 Skill 集成

### + MediaCrawler

```bash
# 1. 使用 Universal Crawler 发现网站
# 2. 使用 MediaCrawler 深度采集
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py --platform xhs --keywords "关键词"
```

### + feishu-universal

```bash
# 爬取 → 上传飞书
python3 scripts/crawl.py --url "https://example.com" --output temp.md
# 然后使用飞书自动化上传文档
```

### + data-cleaner

```bash
# 爬取 → 清洗 → 分析
python3 scripts/crawl.py --url "https://example.com" --format json --output data.json
# 然后使用 data-cleaner 清洗
```

---

## 故障排查

### Q1: 爬取超时？

**解决**：增加超时时间
```bash
--timeout 60
```

### Q2: 内容不完整？

**可能原因**：
- 网页仍在加载
- JavaScript 渲染问题

**解决**：
```bash
--no-cache  # 禁用缓存
--timeout 60  # 增加超时
```

### Q3: 格式混乱？

**解决**：使用 JSON 格式手动处理
```bash
--format json
```

---

**更新时间**: 2026-02-11
**版本**: v1.0.0
