---
name: baogaomiao
description: 阅读总结多种文档（PDF/Word/PPT/网页），分3步输出：中文标题（2026开头）、英文标题、小红书笔记，生成后自动发送到飞书。支持PDF截图（跳过前2页和最后5页，随机截6张），截图自动发送到飞书手机。每次生成截图时自动清理该PDF的旧截图。**NEW v2.9**：东方财富研报爬虫升级，支持临时目录、页数过滤、去重选择。**NEW v2.8**：社论风封面生成！处理 PDF 后自动生成现代社论风格封面图片（3:4比例），并与其他内容一起发送到飞书。**NEW v2.7**：自动重命名 PDF 文件为标准格式（MMDD-Year+报告名称.pdf）。当用户提到"报告喵"或"阅读PDF"、"总结文档"、"生成小红书笔记"、"读一下这个"、"用baogaomiao"时使用。支持任务监听和自动处理。
version: 2.9.0
created: 2026-02-13
updated: 2026-02-27

---

# 📖 文档总结 - 小红书笔记生成

你是一个高效的文档阅读和内容总结专家，专注于将各类文档转化为吸引人的小红书笔记，**生成后自动发送到飞书**。

## 🚀 快速开始（3步）

### 第1步：确认PDF位置
```bash
# 查看报告喵文件夹中的最新PDF
python3 scripts/get_latest_pdf.py --list
```

**默认路径**：`~/Library/Mobile Documents/com~apple~CloudDocs/家人共享/报告喵`

### 第2步：处理PDF
```bash
# 直接使用默认路径
baogaomiao

# 或指定PDF路径
baogaomiao /path/to/file.pdf
```

### 第3步：查看飞书
自动发送到飞书，包含：
- 📝 中文标题 + 英文标题 + 小红书笔记
- 📷 6张PDF截图
- 📰 社论风封面

---

## ⚠️ 使用前必读

### 路径问题排查
如果找不到PDF文件，按以下步骤检查：

1. **确认目录名是"报告喵"**（不是"报告sir"或其他名称）
2. **检查iCloud同步是否完成**（文件可能在同步中）
3. **使用脚本验证路径**：
   ```bash
   python3 scripts/get_latest_pdf.py --list
   ```
4. **查看完整路径**：
   ```bash
   ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/家人共享/报告喵/
   ```

### 自定义路径
```bash
# 使用其他文件夹的PDF
baogaomiao ~/Documents/我的报告.pdf
```

---

## 📋 核心功能

你是一个高效的文档阅读和内容总结专家，专注于将各类文档转化为吸引人的小红书笔记，**生成后自动发送到飞书**。

**NEW v2.8**：社论风封面生成！处理 PDF 后自动生成现代社论风格封面图片（3:4比例），并与其他内容一起发送到飞书。

**NEW v2.7**：自动重命名 PDF 文件！读取 PDF 后自动重命名为标准格式 `MMDD-Year+报告名称.pdf`。

**NEW v2.6**：自动清理旧截图！每次生成截图时，自动删除该PDF的旧截图，确保只保留最新一天的截图。

### 报告喵文件夹路径 ⭐ FIXED (v2.3)

默认报告喵文件夹路径（macOS iCloud）：
```
~/Library/Mobile Documents/com~apple~CloudDocs/家人共享/报告喵
```

**获取最新PDF脚本**：
```bash
# 查找最新PDF
python3 scripts/get_latest_pdf.py

# 列出所有PDF
python3 scripts/get_latest_pdf.py --list

# 指定自定义目录
python3 scripts/get_latest_pdf.py --dir /path/to/folder

# JSON格式输出
python3 scripts/get_latest_pdf.py --json
```

**Python调用**：
```python
from scripts.get_latest_pdf import PDFFinder

# 使用默认路径
finder = PDFFinder()
result = finder.find_latest()

if result['success']:
    pdf_path = result['file_path']
    print(f"最新PDF: {pdf_path}")
else:
    print(f"错误: {result['error']}")
```

---

## 核心功能

当用户提供一个文档路径时，按以下 3 步分别输出，并自动发送到飞书：

### 路径参数支持 ⭐ UPDATED (v2.3)

支持多种路径格式：

1. **文件夹路径**：`报告喵 /path/to/folder` - 查找该文件夹中最新的PDF
2. **文件路径**：`报告喵 /path/to/file.pdf` - 直接处理指定文件
3. **默认路径**：`报告喵`（无参数）- 使用报告喵文件夹

**使用示例**：
```
报告喵                                    # 使用报告喵文件夹
报告喵 /Users/echochen/Documents/PDFs       # 处理指定文件夹
报告喵 ~/Documents/report.pdf                # 处理指定文件
```

### 新增功能 v2.7 ⭐ NEW

#### PDF 自动重命名 📁

读取 PDF 后，自动将文件重命名为标准格式，方便归档和管理。

**命名格式**：`MMDD-Year+报告名称.pdf`

**命名规则**：
- **MMDD**：当前日期（月日），如 `0227`
- **Year**：年份（从标题提取，默认2026）
- **报告名称**：12个中文字以内，体现行业或品牌

**示例**：
```
0227-2026珀莱雅化妆品研究报告.pdf
0227-2026母婴行业趋势报告.pdf
0227-2026连锁经营数据报告.pdf
```

**重命名时机**：
- 在 PDF 解析完成后
- 在生成中文标题后
- **在飞书发送之前**（确保文件名已更新）

**命令行测试**：
```bash
# 只生成文件名（不重命名）
python3 scripts/file_namer.py "🎯2026 母婴连锁经营数据报告 —— 逆势增长密码"

# 生成文件名并重命名
python3 scripts/file_namer.py "🎯2026 母婴连锁经营数据报告" /path/to/file.pdf

# 试运行模式（不实际重命名）
python3 scripts/file_namer.py "🎯2026 母婴连锁经营数据报告" /path/to/file.pdf --dry-run
```

**Python 调用**：
```python
from scripts.file_namer import PDFRenamer

renamer = PDFRenamer()

# 生成新文件名
new_name = renamer.generate_filename(
    chinese_title="🎯2026 母婴连锁经营数据报告 —— 逆势增长密码"
)
# 结果：0227-2026母婴连锁经营数据报告.pdf

# 执行重命名
result = renamer.rename_pdf(
    old_path="/path/to/original.pdf",
    new_name="0227-2026母婴连锁经营数据报告.pdf"
)

if result['success']:
    print(f"重命名成功: {result['old_path']} -> {result['new_path']}")
```

**安全措施**：
- 检查目标文件是否存在
- 文件名冲突时自动添加序号（如 `_1`, `_2`）
- 失败时记录日志但不中断主流程

### 新增功能 v2.8

#### 社论风封面生成 📰

处理 PDF 后自动生成现代社论风格封面图片（3:4比例），并与其他内容一起发送到飞书。

**封面参数提取规则**：

| 参数 | 提取来源 | 默认值 |
|------|---------|--------|
| source | 从封面页OCR或文字提取 | "研究报告" |
| page_count | PDFExtractor.total_pages | 自动获取 |
| chinese_title | 第一步生成的中文标题（移除emoji） | - |
| english_title | 第二步生成的英文标题（转大写） | - |
| year | 从中文标题提取 `🎯YYYY` 格式 | 当前年份 |
| highlight_title | 小红书笔记的"梗概" | "核心要点" |
| summary_text | 小红书笔记的"关键词" | 根据标题生成 |
| report_type | 报告类型 | "行业研究报告" |
| number | 自动生成 | MMDD 格式 |

**提取方式**：

1. **source（来源）**：
   - 优先从PDF封面页提取文字（pymupdf的 `get_text()`）
   - 提取第一页的前500字符，匹配机构名称模式
   - 模式：`xxx研究院`、`xxx咨询`、`xxx证券` 等
   - 如果提取失败，使用默认值"研究报告"

2. **year（年份）**：
   - 从中文标题提取 `🎯2026` 格式
   - 正则表达式：`🎯(\d{4})`
   - 如果提取失败，使用 `datetime.now().year`

3. **highlight_title**：
   - 直接使用小红书笔记的"梗概"内容

4. **summary_text**：
   - 直接使用小红书笔记的"关键词"内容

**长度限制规则**：

| 参数 | 限制 |
|------|------|
| 中文标题 | 总长度最多20字（不含年份前缀🎯2026），最多2行，每行最多10字（年份占1行，总共3行） |
| 英文标题 | 最多25个字符 |
| highlight_title | 最多12字 |
| summary_text | 最多40字 |

**字体设置参考**：
- 中文标题：`font-noto-serif font-black text-[3.6rem]` (57.6px)
- 英文标题：`text-accent font-bold tracking-wider`
- highlight标题：`font-noto-serif font-bold text-xl`
- 其他文本：`text-base`、`text-sm`、`text-xs`

**使用示例**：
```python
from scripts.editorial_cover import EditorialCoverGenerator
from scripts.html_to_image import HTMLToImageConverter

# 1. 提取PDF信息
extractor = PDFExtractor("document.pdf")
result = extractor.extract()
page_count = result['total_pages']
source = extractor.extract_source()  # 新增方法

# 2. 生成HTML封面
generator = EditorialCoverGenerator()
cover_result = generator.generate_cover(
    source=source,
    page_count=page_count,
    chinese_title=chinese_title,
    english_title=english_title,
    year=year,
    highlight_title=genggai,  # 梗概
    summary_text=guanjianci  # 关键词
)

# 3. 转换为PNG
converter = HTMLToImageConverter()
png_result = converter.convert_to_xhs_style(
    html_path=cover_result['path']
)

# 4. 发送到飞书
sender.send_image(png_result['path'])
```

**封面图片发送位置**：
- 在PDF截图之后发送
- 消息顺序：小红书笔记 → 6张PDF截图 → 封面图

**消息接收顺序更新**：
```
1. 小红书笔记
2-7. 6张PDF截图
8. 封面图
```

### 新增功能 v2.5

#### PDF 截图自动发送到飞书 📱

处理 PDF 时生成的 6 张截图会**自动发送到飞书**，无需手动操作：

**自动发送流程**：
1. PDF 解析完成，生成 6 张截图
2. 文本笔记发送到飞书（3 条消息）
3. **自动发送** 6 张截图（6 条图片消息）
4. 用户在手机飞书 APP 中可直接查看

**消息接收顺序**：
```
1. 中文标题
2. 英文标题
3. 小红书笔记
4-9. 6 张 PDF 截图
```

### 新增功能 v2.4

#### PDF 截图功能 📷

在解析 PDF 文档时，自动截取 **6 张随机页面**作为参考图片：

**截图策略**：
- 跳过前2页
- 跳过最后5页
- 从剩余页面中随机选择 6 页
- 截取完整 A4 版面（全页面截图）
- 2x 缩放，retina 质量输出

**使用方式**：
```python
from scripts.pdf_extractor import PDFExtractor

# 启用截图
extractor = PDFExtractor(
    "document.pdf",
    enable_screenshots=True,
    screenshot_dir="/path/to/screenshots",  # 可选，默认为 skill/screenshots/
    zoom=2.0  # 可选，默认 2.0
)

result = extractor.extract(max_pages=5)

if result['success']:
    print(result['text'])  # 提取的文本
    if 'screenshots' in result:
        for shot in result['screenshots']:
            print(f"第 {shot['page']} 页: {shot['path']}")
```

**命令行使用**：
```bash
# 启用截图
python3 scripts/pdf_extractor.py document.pdf --enable-screenshots

# 指定截图目录
python3 scripts/pdf_extractor.py document.pdf -s --dir /path/to/screenshots

# 调整缩放倍数
python3 scripts/pdf_extractor.py document.pdf -s --zoom 3.0
```

**返回结构**：
```python
{
    'success': True,
    'lib': 'pymupdf',
    'total_pages': 20,
    'extracted_pages': 5,
    'text': '...',
    'screenshots': [
        {'page': 3, 'path': '/path/to/screenshot_1.png'},
        {'page': 7, 'path': '/path/to/screenshot_2.png'},
        # ... 共 6 张
    ],
    'screenshot_count': 6
}
```

### 新增功能 v2.1

#### 1. 智能PDF解析
支持多种PDF库自动检测和选择：

#### 2. 飞书自动发送
生成小红书笔记后自动发送到飞书：

## 任务监听功能（与bot_server集成）

### 任务文件位置
```
~/.claude/skills/feishu-bot/data/baogaomiao_tasks/
├── task_YYYYMMDD_HHMMSS.json  # 待处理任务
├── task_YYYYMMDD_HHMMSS.json  # 处理中
└── task_YYYYMMDD_HHMMSS.json  # 已完成
```

### 任务文件格式
```json
{
  "task_type": "baogaomiao_generate",
  "pdf_path": "/完整/PDF路径",
  "task_id": "20260211_143022",
  "created_at": "2026-02-11T14:30:22",
  "status": "pending|processing|completed",
  "result": {
    "chinese_title": "...",
    "english_title": "...",
    "xhs_note": "..."
  }
}
```

### 自动任务处理

当检测到新的pending任务时，自动执行以下流程：

1. **读取PDF内容**：使用 pdf_extractor.py
2. **生成3步输出**：中文标题、英文标题、小红书笔记（本skill完整逻辑）
3. **发送到飞书**：使用 feishu_sender.py 自动发送
4. **更新任务状态**：将status改为completed
5. **保存结果**：可选保存到任务文件中

### 手动触发方式

**方式一：对话触发**（推荐）
在Claude Code中说"检查baogaomiao任务"即可触发自动处理。

**方式二：命令触发**
创建快捷命令"处理任务"或"PT任务"，让用户通过对话快速触发。

### 工作流程

```
bot_server创建任务文件 → 检测到新任务 → 自动处理 → 发送飞书
```

### 新增功能 v2.1

#### 1. 智能PDF解析

- **pymupdf (fitz)**：优先使用，速度快、中文支持好
- **pdfplumber**：表格提取能力强
- **PyPDF2**：轻量级、兼容性好

使用方式：
```python
from scripts.pdf_extractor import PDFExtractor

extractor = PDFExtractor("document.pdf")
result = extractor.extract(max_pages=5)  # 最多提取前5页

if result['success']:
    print(result['text'])  # 提取的文本
    print(f"使用库: {result['lib']}")
```

#### 2. 飞书自动发送
生成小红书笔记后自动发送到飞书：

- **Webhook 模式**：配置 `FEISHU_WEBHOOK_URL` 环境变量
- **Bot Notifier 模式**：调用 `feishu-universal/skill` 的通知脚本
- **自动发送**：默认自动发送，无需手动触发

使用方式：
```python
from scripts.feishu_sender import FeishuSender

sender = FeishuSender()
result = sender.send(content, auto_send=True)  # 自动发送
```

### 原有功能

当用户提供一个文档路径时，按以下 3 步分别输出：

### 第一步：中文标题
- 统一以"2026"开头
- 格式：`🎯2026 [主标题] —— [副标题]`
- 主标题：一眼看出是报告，符合报告标题风格（如：行业趋势报告、数据经营白皮书、发展洞察报告等）
- 副标题：一句话提炼报告核心价值/亮点（10-20字）
- 例如："🎯2026母婴连锁数据经营报告 —— 逆势增长背后的经营密码"、"🎯2026母婴行业趋势白皮书 —— 团购爆发与会员复购破局"

### 第二步：英文标题
- 对应中文标题的英文翻译
- 保持简洁有力
- 例如："2026 How Maternal & Child Chains Defied the Odds"

### 第三步：小红书笔记
采用**紧凑高效**格式，信息密度高，视觉冲击强。

#### 标准模板
```
🎯2026 [标题]

梗概：[一句话总结核心洞察/结论]
关键词：[3-5个核心关键词]

💥1. [章节标题 Emoji + 名称]
• [核心结论]
  ◦ [支撑数据/细节]
  ◦ [支撑数据/细节]

💥2. [章节标题 Emoji + 名称]
• [核心结论]
  ◦ [支撑数据/细节]
  ◦ [支撑数据/细节]

💥3. [章节标题 Emoji + 名称]
• [核心结论]
  ◦ [支撑数据/细节]
  ◦ [支撑数据/细节]
```

#### 结构要点

**梗概**
- 一句话概括：[现象] + [核心原因]
- 例如："逆势增长背后，母婴连锁靠团购爆发与会员复购破局"

**关键词**
- 3-5个核心概念
- 逗号分隔
- 例如："数字化经营、团购增长、会员复购、线下主导"

**章节命名**
- 使用 💥 标记
- 每章1个核心结论
- 用 • 标记主论点
- 用 ◦ 标记细节/数据
- 建议分3-5章

**Emoji 使用建议**
- 标题开头：🎯/🍼/📊/🚀/💡
- 章节1：📈/👶/📊/🔍
- 章节2：🛍️/💰/🎯/⭐
- 章节3：⚠️/🚧/💡/🔮

#### 内容提取原则
1. **品类优先**：优先提取产品/品类相关信息（市场规模、行业地位、技术特点）
2. **数据解读**：数据要说明品类趋势和市场机会，而非单纯财务表现
3. **对比突出**：品类对比、竞品对比、行业对比
4. **结论导向**：每段先说品类洞察，再给数据支撑
5. **适度详细**：每章3-4个细节点，内容充实但不冗长
6. **字数控制**：正文总字数控制在800字左右（不含标题、梗概、关键词）
7. **避免聚焦**：减少股权收购、净利润、股价等财务指标，聚焦品类和行业洞察

## 文档类型处理

根据文件后缀选择读取方式：

### PDF 文件
- **文件查找**：使用 `scripts/get_latest_pdf.py` 获取最新PDF（避免shell glob问题）
  - 使用 `Path.glob()` 而非 shell glob
  - 先检查目录是否存在
  - 按修改时间排序返回最新文件
  - 支持自定义路径和默认路径
- **文本提取**：使用 `scripts/pdf_extractor.py` 自动检测并提取文本
- 支持多库：pymupdf、pdfplumber、PyPDF2
- 大文件处理：`max_pages` 参数控制提取页数
- 如果 Read 工具不可用，回退到脚本解析

### Word 文件 (.docx)
- 提示用户转换为 PDF

### PPT 文件
- 使用 Read 工具读取（.pptx 格式）
- 优先读取标题页 + 目录页 + 核心内容页

### 网页/HTML
- 使用 web_reader MCP 工具读取

## 执行流程

```
用户：报告喵 / "用baogaomiao" / "阅读PDF"
↓
你：好的，我来阅读这份文档
↓
[步骤1：文件查找] 使用 get_latest_pdf.py 获取PDF
  • 检查目录是否存在
  • 使用 Path.glob() 查找PDF文件
  • 按修改时间排序返回最新文件
  • 如果有自定义路径则使用自定义路径
↓
[步骤2：PDF解析] 使用 pdf_extractor.py 自动检测并提取文本
  • 📷 启用截图功能（跳过前2页+最后5页，随机截6张）
  • 使用 pymupdf 渲染完整 A4 页面为 PNG
  • 截图保存到 ~/.claude/skills/baogaomiao/screenshots/
↓
[步骤3：文档扫描] 快速扫描文档：摘要目录 + 核心章节
↓
输出第一步：中文标题（🎯2026开头）
↓
输出第二步：英文标题
↓
输出第三步：小红书笔记（紧凑格式模板）
↓
[步骤4：飞书发送] 使用 feishu_sender.py 发送到飞书
  • 文本笔记发送（3条消息：中文标题、英文标题、笔记）
  • 📷 截图自动发送（6张图片消息）
↓
完成：用户可在飞书手机 APP 中查看完整笔记和截图
```

### 飞书发送配置

环境变量（可选）：
- `FEISHU_WEBHOOK_URL`：飞书 Webhook URL（优先使用）
- `FEISHU_APP_ID`：飞书应用 ID
- `FEISHU_APP_SECRET`：飞书应用密钥

如果未配置，脚本会自动回退到 `feishu-universal/skill` 的通知方法。

## 注意事项

1. **分步输出**：严格按 3 步分别输出，中间用 `---` 分隔
2. **标题统一**：中文标题必须以"🎯2026"开头
3. **格式紧凑**：参考模板，不要冗长
4. **数据真实**：保留原文关键数据，不要编造
5. **速度优先**：快速响应，不解释过程
6. **自动飞书发送**（v2.1）：生成笔记后自动发送，无需手动触发
7. **截图自动发送**（v2.5）：PDF 解析时生成的 6 张截图会自动发送到飞书，手机 APP 可直接查看

## 参考示例

```
🍼2025母婴连锁经营数据报告✨

梗概：逆势增长背后，母婴连锁靠团购爆发与会员复购破局
关键词：数字化经营、团购增长、会员复购、线下主导

💥1. 📈行业整体表现
• 逆势增长：年支付总金额+13.24%、订单数+8.16%，经营门店数+18.33%
  ◦ 业绩分化：34%客户实现增长，66%客户持平或下滑，两极分化明显
  ◦ 商品销售仍是核心，团购和活动预售成为增长引擎

💥2. 👶会员消费特征
• 消费会员数、人均消费双增，客单价+、购物频次+、复购周期缩短
  ◦ 1-2岁幼儿期会员为核心，忠诚会员贡献超56%消费金额
  ◦ 首单后3个月是关键留存期，平均复购周期缩短至28天

💥3. 🛍️渠道表现对比
• 门店销售占比超97%，仍是核心阵地
  ◦ 第三方线上商城、外卖、抖音本地生活增长显著
  ◦ 海博订单+101.53%、团购核销金额+705.97%，成增长黑马

💥4. ⚠️现存挑战与模式
• 店效、人效小幅下滑，成本压力显现
  ◦ 区域整合与降本增效并行，数字化成破局关键
```

## 触发场景

### 基础触发
- "报告喵" - 使用默认路径（报告喵文件夹）
- "阅读这个 PDF"
- "总结这份文档"
- "帮我读一下 [文件]"
- "生成小红书笔记"
- "这个报告讲了什么"
- "用baogaomiao" [直接调用 skill]

### 路径参数触发 ⭐ NEW (v2.2)
- "报告喵 /path/to/folder" - 处理指定文件夹的最新PDF
- "报告喵 /path/to/file.pdf" - 处理指定PDF文件
- "用baogaomiao /path/to/file.pdf" - 处理指定PDF文件

**Claude Code端处理逻辑**：
1. 检测"报告喵"或"baogaomiao"触发词
2. 检查是否包含路径参数（空格分隔）
3. 如果有路径：
   - 验证路径存在
   - 如果是文件夹 → 使用 get_latest_pdf.py 查找最新PDF
   - 如果是文件 → 验证是PDF格式
4. 如果没有路径 → 使用默认的报告喵文件夹路径，通过 get_latest_pdf.py 获取最新PDF
5. **关键修复**：使用 Path.glob() 而非 shell glob，先检查目录是否存在


---
#### 修复记录

**社论风封面生成功能** (v2.8 - 2026-02-27)：
- ✅ 添加 `extract_source()` 方法到 pdf_extractor.py：从封面页提取机构名称
- ✅ 更新 editorial_cover.py：封面参数来源明确
- ✅ 更新 feishu_sender.py：移除中英文标题单独发送，只发送小红书笔记
- ✅ 更新 baogaomiao_task_processor.py：集成封面生成和发送逻辑
- ✅ 飞书消息接收顺序更新：小红书笔记 → 6张PDF截图 → 封面图

**使用效果**：
```python
# PDF 处理完成后，自动发送 8 条飞书消息：
# 1. 小红书笔记
# 2-7. 6 张 PDF 截图
# 8. 封面图

extractor = PDFExtractor("document.pdf", enable_screenshots=True)
result = extractor.extract()
# 封面和截图会自动生成并发送到飞书
```

**截图自动发送功能** (v2.5 - 2026-02-25)：
- ✅ 添加 `upload_image()` 方法到 feishu_bot_notifier.py：上传图片到飞书获取 image_key
- ✅ 添加 `send_image_message()` 方法到 feishu_bot_notifier.py：发送单张图片消息
- ✅ 添加 `send_image_batch()` 方法到 feishu_bot_notifier.py：批量发送多张图片（支持限流重试）
- ✅ 添加 `send_screenshots()` 方法到 feishu_sender.py：封装截图发送逻辑
- ✅ 更新 baogaomiao_task_processor.py：文本发送成功后自动发送截图
- ✅ 飞书消息接收顺序：中文标题 → 英文标题 → 小红书笔记 → 6张截图

**使用效果**：
```python
# PDF 处理完成后，自动发送 9 条飞书消息：
# 1-3. 文本笔记（中文标题、英文标题、小红书笔记）
# 4-9. 6 张 PDF 截图

extractor = PDFExtractor("document.pdf", enable_screenshots=True)
result = extractor.extract()
# 截图会自动上传并发送到飞书
```

**PDF 截图功能** (v2.4 - 2026-02-25)：
- ✅ 添加 PDF 截图功能，使用 pymupdf 原生渲染
- ✅ 固定截取 6 张图片，跳过前2页和最后5页
- ✅ 从剩余页面中随机选择，截取完整 A4 版面
- ✅ 2x 缩放输出 retina 质量 PNG
- ✅ 截图保存到 `~/.claude/skills/baogaomiao/screenshots/`
- ✅ 更新 pdf_extractor.py 支持截图参数
- ✅ 更新 baogaomiao_task_processor.py 集成截图功能

**使用方法**：
```python
# 启用截图
extractor = PDFExtractor("document.pdf", enable_screenshots=True)
result = extractor.extract()

# 访问截图
for shot in result['screenshots']:
    print(f"第 {shot['page']} 页: {shot['path']}")
```

**文件查找问题修复** (v2.3 - 2026-02-24)：
- ✅ 创建 `get_latest_pdf.py` 脚本，专门处理PDF文件查找
- ✅ 使用 `Path.glob()` 而非 shell glob，避免 shell 扩展问题
- ✅ 先检查目录是否存在，提供清晰的错误信息
- ✅ 支持自定义路径和默认路径
- ✅ 新增 SKILL.md 默认配置说明

**修复前的问题**：
```bash
# shell glob 失败
ls -lt ~/Library/Mobile\ Documents/.../报告喵/*.pdf
# 返回: no matches found
```

**修复后的方案**：
```bash
# 使用 Python glob
python3 scripts/get_latest_pdf.py
# 返回: ✅ 找到最新PDF
```

**多消息发送支持** (v2.2.1 - 2026-02-11)：
- 笔记内容会分成3条独立消息，分别发送：
  1. 中文标题
  2. 英文标题（带分隔符）
  3. 小红书笔记
- 每条消息间隔1秒，避免限流

**修复记录**：
- ✅ 修复 feishu_bot_notifier.py 参数处理：`__main__` 块添加 argparse，支持 `--message` 和 `--test` 参数
- ✅ 修复 feishu_sender.py 分批发送：`format_xhs_note()` 返回列表，`send_via_bot_notifier()` 和 `send_via_webhook()` 支持发送列表
- ✅ 修复路径解析问题：使用 `Path(__file__).resolve().parent` 确保正确的脚本路径
- ✅ 验证测试：成功发送 3 条消息到飞书

EOF

---

## 东方财富研报爬虫 ⭐ NEW (v2.9)

**位置**：`bin/crawl_huaxin_robots.py`

**功能**：爬取华鑫证券关于机器人赛道的研报，支持智能过滤和去重。

### 工作流程

```
爬取研报列表 → 下载到临时目录 → 页数过滤 → 去重选择 → 复制到报告喵
```

### 核心特性

| 特性 | 说明 |
|------|------|
| 临时目录 | 下载的PDF先存到 `temp/eastmoney_downloads/` |
| 页数过滤 | 少于10页的PDF自动删除 |
| 去重选择 | 同一天多份时支持飞书/对话框选择 |
| 最终操作 | 只把选中的一份复制到报告喵文件夹 |
| 自动清理 | 选择完成后自动清理临时文件 |

### 配置

```python
# 脚本中的配置常量
TEMP_DIR = Path("/Users/echochen/Desktop/DMS/temp/eastmoney_downloads")
FINAL_DIR = Path("~/Library/Mobile Documents/com~apple~CloudDocs/家人共享/报告喵").expanduser()
MIN_PAGE_COUNT = 10  # 最少页数阈值
```

### 使用方法

```bash
# 爬取最近7天的研报（默认）
python3 bin/crawl_huaxin_robots.py

# 爬取最近30天的研报
python3 bin/crawl_huaxin_robots.py --days 30
```

### 飞书反馈格式

当发现多份研报时，会创建选择文件供飞书使用：

```json
// temp/eastmoney_downloads/selection_result.json
{
  "timestamp": "2026-02-27T10:00:00",
  "options": [
    {"index": 1, "title": "中国工控领域领先企业积极开拓机器人赛道", "pages": 59},
    {"index": 2, "title": "华鑫证券机器人赛道深度分析", "pages": 42}
  ],
  "choice": null  // 飞书回复时填充：{"choice": 1}
}
```

飞书回复格式：
```json
{"choice": 1}
```

### 自动选择逻辑

当不需要用户选择时，自动选择规则：
- 只有1份 → 直接保留
- 多份时超时 → 选择页数最多的
- 用户取消 → 跳过本次操作


---

## 🔧 故障排查

### 常见问题

#### 问题1：找不到PDF文件

**现象**：运行 baogaomiao 后提示"找不到PDF"或"没有找到文件"

**排查步骤**：
1. 确认目录名是"报告喵"（不是"报告sir"或其他名称）
2. 确认iCloud同步已完成（文件可能正在同步中）
3. 使用脚本查看：
   ```bash
   python3 scripts/get_latest_pdf.py --list
   ```
4. 手动检查路径：
   ```bash
   ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/家人共享/报告喵/*.pdf
   ```

**解决方案**：
- 使用完整路径：`baogaomiao ~/Documents/我的报告.pdf`
- 等待iCloud同步完成后再运行

#### 问题2：PDF截图失败

**现象**：只生成1-2张截图，或截图全部失败

**排查步骤**：
1. 检查PDF页数是否足够（至少需要 3+2+5=10页才能生成6张截图）
2. 检查截图目录权限：
   ```bash
   ls -la scripts/screenshots/
   ```
3. 重新生成截图：
   ```bash
   rm scripts/screenshots/当前PDF_*.png
   ```

**解决方案**：
- 对于少于10页的PDF，会生成可用页数的截图
- 检查磁盘空间是否充足

#### 问题3：飞书发送失败

**现象**：消息显示"发送失败"但程序继续运行

**排查步骤**：
1. 检查飞书配置：
   ```bash
   cat ~/.feishu_user_config.json
   ```
2. 检查chat_id是否正确
3. 查看日志：
   ```bash
   tail -50 logs/baogaomiao_*.log
   ```

**解决方案**：
- 确认 `chat_id` 指向正确的群（东方财富群：`oc_922ab5c6faff499c0485499681a98f33`）
- 重新获取飞书Token：
   ```bash
   python3 ~/Desktop/DMS/skills/feishu-universal/scripts/feishu_token_checker.py
   ```

#### 问题4：封面生成乱码

**现象**：封面显示为乱码或方框

**排查步骤**：
1. 检查中文字体是否正确加载
2. 检查HTML文件编码（应为UTF-8）
3. 查看生成的HTML：
   ```bash
   cat scripts/covers/editorial_*.html | head -30
   ```

**解决方案**：
- 确保 `editorial_cover.py` 使用UTF-8编码保存HTML
- 中文字体使用 Noto Serif SC

#### 问题5：标题断行不合理

**现象**：标题在词中间断开（如"研究报"断开）

**排查步骤**：
1. 查看生成的HTML中的 `<br>` 位置
2. 检查 `COMMON_WORDS` 是否包含相关词汇

**解决方案**：
- 已实现智能断词逻辑（`_split_title_by_semantics`）
- 可手动用 `<br>` 标注断行位置

---

