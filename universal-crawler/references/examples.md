# Universal Crawler 实战案例

> **真实场景** - 从问题到解决方案

---

## 目录

1. [案例 1：竞品监控](#案例1竞品监控)
2. [案例 2：行业研究](#案例2行业研究)
3. [案例 3：博客备份](#案例3博客备份)
4. [案例 4：新闻聚合](#案例4新闻聚合)

---

## 案例1：竞品监控

### 场景

监控竞品网站的产品更新，及时了解竞争对手动态。

### 解决方案

```bash
# 1. 创建 URL 列表
cat > competitors.txt << EOF
https://competitor1.com/products
https://competitor2.com/new
https://competitor3.com/updates
EOF

# 2. 批量爬取
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --urls competitors.txt \
  --output competitors/$(date +%Y%m%d).md

# 3. 定时执行（crontab）
0 9 * * * python3 ~/.claude/skills/universal-crawler/scripts/crawl.py --urls competitors.txt --output ~/competitors/$(date +\%Y\%m\%d).md
```

### 效果

- ✅ 每天自动爬取竞品页面
- ✅ 按日期归档
- ✅ 便于对比分析

---

## 案例2：行业研究

### 场景

研究 "AI 编程工具" 行业，收集相关资料。

### 解决方案

```bash
# 1. Google 搜索并爬取
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --search "AI 编程工具 2026" \
  --top 10 \
  --output research/ai_programming_tools.md

# 2. 提取关键信息
grep -E "Claude|ChatGPT|Copilot" research/ai_programming_tools.md

# 3. 整理为报告
# 使用 data-cleaner 或手动整理
```

### 效果

- ✅ 自动搜索并爬取
- ✅ 获取最新信息
- ✅ 快速形成报告

---

## 案例3：博客备份

### 场景

备份自己喜欢的博客文章，防止网站关闭。

### 解决方案

```bash
# 1. 获取博客文章列表
# 可以从 RSS 或网站地图获取

# 2. 创建 URL 列表
cat > blog.txt << EOF
https://blog.example.com/post1
https://blog.example.com/post2
https://blog.example.com/post3
EOF

# 3. 批量爬取并保存
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --urls blog.txt \
  --output-dir ~/backup/blog

# 4. 验证完整性
ls ~/backup/blog/*.md | wc -l
```

### 效果

- ✅ 完整备份博客
- ✅ Markdown 格式便于阅读
- ✅ 本地存储安全可靠

---

## 案例4：新闻聚合

### 场景

聚合多个新闻源，形成个人新闻摘要。

### 解决方案

```bash
# 1. 创建新闻源列表
cat > news_sources.txt << EOF
https://news1.com/tech
https://news2.com/ai
https://news3.com/programming
EOF

# 2. 每日爬取
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --urls news_sources.txt \
  --output daily_news/$(date +%Y%m%d).md

# 3. 提取标题
grep -E "^#" daily_news/$(date +%Y%m%d).md | head -20
```

### 效果

- ✅ 整合多源新闻
- ✅ 按日期归档
- ✅ 快速浏览标题

---

## 高级技巧

### 技巧 1：增量爬取

```bash
# 只爬取最新的内容
# 比较文件大小，如果变化才爬取
last_size=$(stat -f%z output.md 2>/dev/null || echo 0)
python3 scripts/crawl.py --url "https://example.com" --output new.md
new_size=$(stat -f%z new.md)

if [ $new_size -ne $last_size ]; then
  mv new.md output.md
  echo "内容已更新"
else
  rm new.md
  echo "内容未变化"
fi
```

### 技巧 2：智能去重

```bash
# 爬取后去重
python3 scripts/crawl.py --url "https://example.com" --output raw.md
# 使用 data-cleaner 去重
```

### 技巧 3：关键词过滤

```bash
# 只保留包含关键词的内容
python3 scripts/crawl.py --url "https://example.com" | grep "关键词" > filtered.md
```

---

## 工作流模板

### 模板 1：研究工作流

```bash
# 1. 搜索发现
python3 scripts/crawl.py --search "研究主题" --top 20 --output discover.md

# 2. 深度爬取
# 从 discover.md 中提取关键 URL，批量爬取

# 3. 数据清洗
# 使用 data-cleaner 清洗数据

# 4. 分析报告
# 使用数据分析工具生成报告
```

### 模板 2：监控工作流

```bash
# 1. 定时爬取
# crontab 设置

# 2. 变化检测
# 比较新旧文件

# 3. 通知提醒
# 集成 feishu-universal 发送通知
```

---

**更新时间**: 2026-02-11
**版本**: v1.0.0
