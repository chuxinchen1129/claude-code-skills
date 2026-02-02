# MediaCrawler Skill - 快速使用指南

> **社交媒体数据采集工具**
> **位置**: /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler

---

## 🚀 一分钟上手

### 采集小红书数据

```bash
cd /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler
uv run main.py --platform xhs --lt qrcode --type search --keywords "你的关键词"
```

**首次使用**：扫码登录（登录态保持 7-30 天）

---

## 📋 常用命令

### 基础命令

```bash
# 小红书采集（默认100条）
uv run main.py --platform xhs --lt qrcode --type search --keywords "关键词"

# 自定义采集数量
uv run main.py --platform xhs --lt qrcode --type search \
  --keywords "关键词" \
  --crawler_max_notes_count 50

# 多关键词（英文逗号分隔）
uv run main.py --platform xhs --lt qrcode --type search \
  --keywords "关键词1,关键词2,关键词3"
```

### 其他平台

```bash
# 微博
uv run main.py --platform wb --lt qrcode --type search --keywords "关键词"

# 知乎
uv run main.py --platform zhihu --lt qrcode --type search --keywords "关键词"

# 抖音
uv run main.py --platform douyin --lt qrcode --type search --keywords "关键词"
```

---

## 📂 数据位置

### Excel 文件（推荐）

```
/Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/data/xhs/
└── xhs_search_YYYYMMDD_HHMMSS.xlsx
    ├── Contents（笔记内容）
    ├── Comments（评论内容）
    └── Creators（作者信息）
```

### JSON 文件

```
/Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/data/xhs/search/
└── contents_YYYYMMDD.json
```

---

## 🛠️ 辅助工具

### 数据合并

```bash
# 合并小红书数据
python3 /Users/echo/merge_excel_data.py xhs
```

### 数据分析

```bash
# 分析 Excel 数据
python3 /Users/echo/analyze_data.py /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/data/xhs/*.xlsx
```

### 批量采集

```bash
# 采集小红书（默认20条）
/Users/echo/batch_crawl.sh xhs

# 自定义关键词和数量
/Users/echo/batch_crawl.sh xhs "关键词" 50
```

---

## ⚙️ 配置文件

### 修改配置

**位置**: `/Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/config/base_config.py`

**关键参数**:
```python
# 关键词
KEYWORDS = "无醇啤酒,0酒精啤酒"

# 采集数量
CRAWLER_MAX_NOTES_COUNT = 100

# 请求间隔（秒）
CRAWLER_MAX_SLEEP_SEC = 5

# 输出格式
SAVE_DATA_OPTION = "excel"  # json, excel, csv, sqlite
```

### 小红书排序

**位置**: `/Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/config/xhs_config.py`

```python
# 热门降序（点赞量最高）
SORT_TYPE = "popularity_descending"

# 最新降序（时间最新）
SORT_TYPE = "time_descending"
```

---

## ⚠️ 注意事项

### 采集限制

- ✅ 请求间隔不低于 3 秒（推荐 5 秒）
- ✅ 单次采集不超过 500 条
- ✅ 避免频繁采集同一关键词

### 登录态

- ✅ 扫码登录后保持 7-30 天
- ✅ 登录信息：`browser_data/cdp_xhs_user_data_dir/`
- ⚠️ 如遇 461 状态码，等待 1-2 小时后重试

### 反爬虫

- ⚠️ 不要短时间内大量采集
- ⚠️ 使用真实账号（不要使用小号）
- ⚠️ 遵守平台使用规范

---

## 🎯 使用场景

### 市场调研

```
采集 → 清洗 → 分析 → 可视化 → 报告
```

**案例**: 无醇啤酒小红书数据分析
- 100 条笔记 + 2,011 条评论
- 消费者意愿：78.6% 愿意尝试
- 关键驱动：口感（50.7%）
- 消费场景：聚会、开车、健身

### 竞品分析

```
采集竞品数据 → 品牌提及率 → 用户反馈对比
```

### 内容创作支持

```
采集热门内容 → 提取关键词 → 识别用户需求
```

---

## 📊 完整案例

查看完整项目案例：
```bash
cat /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/项目档案_无醇啤酒小红书数据分析.md
```

**包含**:
- 项目目标和流程
- 数据清洗方法
- 分析维度
- 可视化图表
- PPT 报告生成

---

## 📞 需要帮助？

**查看详细文档**:
- SKILL.md - 完整技能说明
- /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/README.md - 项目说明
- /Users/echo/Desktop/大秘书系统/LIBRARY/MediaCrawler/使用指南.md - 使用指南

**GitHub**:
- https://github.com/NanmiCoder/MediaCrawler
- Issues: https://github.com/NanmiCoder/MediaCrawler/issues

---

**版本**: v1.0
**最后更新**: 2026-01-27
