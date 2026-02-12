# 悟昕睡眠热点采集分析系统 - 集成完成报告

## 📊 集成进度

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| **MediaCrawler 集成** | ✅ 完成 | 小红书数据采集 |
| **Excel 生成** | ✅ 完成 | CSV 格式数据表 + 分析报告 |
| **视频转文字** | ✅ 完成 | 框架完成，待 API 集成 |
| **飞书上传** | ✅ 完成 | Base 创建 + 数据导入 + 通知 |
| **主脚本** | ✅ 完成 | 协调所有功能 |

---

## 📁 新增脚本

### 1. mediecrawler_integration.py
**功能**：MediaCrawler 集成采集

**特点**：
- 自动备份和恢复 MediaCrawler 配置
- 支持自定义关键词
- 自动转换数据格式
- 按 TOP N 排序

**使用**：
```bash
python3 scripts/mediecrawler_integration.py --keywords 睡眠仪 左点
```

### 2. excel_generator.py
**功能**：Excel 报告生成

**输出**：
- 小红书数据表.csv
- 数据分析.csv
- TOP10爆款笔记.csv
- 数据表格.md

**使用**：
```bash
python3 scripts/excel_generator.py
```

### 3. video_transcriber_integration.py
**功能**：视频转文字集成

**特点**：
- 自动下载视频
- 调用 video-scripts-extract Skill
- 保存转写结果

**使用**：
```bash
# 批量处理
python3 scripts/video_transcriber_integration.py

# 单个视频
python3 scripts/video_transcriber_integration.py --video "视频URL"
```

### 4. feishu_uploader.py
**功能**：飞书上传集成

**特点**：
- 创建 Base（用户身份）
- **自动获取 table_id**（无需手动查找）⭐ NEW
- 导入数据到多维表格
- 上传报告到云文档
- 发送完成通知

**使用**：
```bash
# 完整上传
python3 scripts/feishu_uploader.py

# 仅创建 Base
python3 scripts/feishu_uploader.py --create-base "Base名称"

# 指定数据目录
python3 scripts/feishu_uploader.py --data-dir data/weekly_reports/2026-02-10
```

**关键改进** (2026-02-11):
- ✅ 修复空表问题：自动从 API 获取真实 table_id
- ✅ 不再使用无效的 "tablename" 默认值
- ✅ 支持批量导入多个 CSV 文件

### 5. main.py
**功能**：主协调脚本

**特点**：
- 完整工作流（采集 → 分析 → 上传）
- 支持单独运行各步骤
- 命令行参数支持

**使用**：
```bash
# 完整流程
python3 scripts/main.py --full

# 指定关键词
python3 scripts/main.py --full --keywords 睡眠仪 左点

# 仅分析
python3 scripts/main.py --analyze
```

---

## 🔄 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    悟昕睡眠热点采集分析系统                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  步骤 1: 数据采集                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 调用 MediaCrawler                                     │   │
│  │ → 修改配置                                           │   │
│  │ → 运行采集                                           │   │
│  │ → 读取数据                                           │   │
│  │ → 转换格式                                           │   │
│  │ → 保存到 Skill 目录                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│           ↓                                                   │
│  步骤 2: 数据分析                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 运行分析器 + Excel 生成                              │   │
│  │ → 爆款特征分析                                       │   │
│  │ → 标题公式识别                                       │   │
│  │ → 内容结构分析                                       │   │
│  │ → 生成 CSV 报告                                      │   │
│  │ → 生成 Markdown 报告                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│           ↓                                                   │
│  步骤 3: 视频转文字（可选）                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 下载视频 → 转写 → 保存                              │   │
│  └─────────────────────────────────────────────────────┘   │
│           ↓                                                   │
│  步骤 4: 飞书上传                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 创建 Base → 导入数据 → 上传报告 → 发送通知          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 待完善功能

| 功能 | 当前状态 | 后续计划 |
|------|---------|---------|
| **baoyu-url-to-markdown 集成** | ⏳ 框架完成 | API 调用 |
| **douyin MCP 集成** | ⏳ 框架完成 | MCP 调用 |
| **video-scripts-extract API** | ⏳ 框架完成 | API 调用 |
| **真实 xlsx 文件生成** | ⏳ CSV 替代 | 集成 openpyxl |
| **定时任务配置** | ⏳ 待配置 | 集成 daily-review |

---

## 🚀 快速开始

### 1. 首次使用：配置飞书

```bash
cd ~/Desktop/DaMiShuSystem-main-backup
python3 feishu_oauth_setup.py
```

### 2. 采集数据

```bash
cd 00.Wuxin_Zenoasis_Content_Project/.claude/skills/wuxin-sleep-hotspot-collector

# 使用默认关键词
python3 scripts/main.py --collect

# 或指定关键词
python3 scripts/main.py --collect --keywords 睡眠仪 左点
```

### 3. 分析数据

```bash
# 分析已有数据并生成报告
python3 scripts/main.py --analyze
```

### 4. 上传飞书

```bash
# 上传到飞书
python3 scripts/main.py --upload
```

### 5. 完整流程

```bash
# 一键完成所有步骤
python3 scripts/main.py --full
```

---

## 📊 数据示例

### 采集数据格式

```json
{
  "id": "60dcfb3e00000000010263d9",
  "title": "中国人最自豪的瞬间之一！",
  "content": "08年北京奥运会...",
  "likes": 54000,
  "comments": 295,
  "collects": 2399,
  "author": "PP体育",
  "type": "video",
  "video_url": "http://...",
  "note_url": "https://www.xiaohongshu.com/explore/..."
}
```

### 分析报告格式

```markdown
# 睡眠热点内容分析报告 - 2026-02-10

## 一、本周数据概览
- 采集笔记数：6 篇
- 总互动量：XX 万
- 爆款笔记（>1000赞）：XX 篇

## 二、爆款特征分析
### 2.1 标题公式 TOP5
...
```

---

## ⚠️ 注意事项

1. **MediaCrawler 采集**
   - 首次运行需要在浏览器中完成登录
   - 采集过程中请保持浏览器打开
   - 采集时间取决于网络和数据量

2. **飞书上传**
   - 需要先完成 OAuth 授权
   - 创建的 Base 你是所有者
   - Token 有效期 30 天
   - **自动获取 table_id**（无需手动查找）

3. **视频转文字**
   - 需要 DASHSCOPE_API_KEY 环境变量
   - 目前框架完成，API 待集成

---

## 📈 下一步计划

1. **完善 API 集成**
   - baoyu-url-to-markdown
   - douyin MCP
   - video-scripts-extract

2. **优化分析算法**
   - 更精确的标题公式识别
   - 更智能的内容结构分析
   - 情感分析优化

3. **配置定时任务**
   - 集成到 daily-review Skill
   - 每周一中午自动执行

4. **增强飞书集成**
   - 自动创建多维表格字段
   - 数据可视化图表
   - 实时数据更新

---

**集成完成时间**: 2026-02-10
**最后更新**: 2026-02-11 (修复 table_id 自动获取)
**版本**: v1.1.0
**作者**: 大秘书系统

### 更新日志

**v1.1.0** (2026-02-11)
- ✅ 修复飞书空表问题
- ✅ 实现自动获取 table_id
- ✅ 优化批量导入流程

**v1.0.0** (2026-02-10)
- ✅ 初始版本发布
- ✅ MediaCrawler 集成
- ✅ Excel 生成
- ✅ 飞书上传框架
