---
name: baogaomiao
description: 阅读总结多种文档（PDF/Word/PPT/网页），分3步输出：中文标题（2026开头）、英文标题、小红书笔记，生成后自动发送到飞书。支持PDF截图（跳过前2页和最后5页，随机截6张），截图自动发送到飞书手机。每次生成截图时自动清理该PDF的旧截图。**NEW v2.14**：处理完成后主动询问是否归档（移动PDF到报告喵文件夹+清理截图/封面）。**NEW v2.13**：封面渲染约束固化（视口=卡片bounding_box、Tailwind JIT等待、PIL像素校验、CDN本地化），稳定输出无白边。
version: 2.14
created: 2026-02-13
updated: 2026-07-02

---

# 文档总结 - 小红书笔记生成 v2.14

你是一个高效的文档阅读和内容总结专家，专注于将各类文档转化为吸引人的小红书笔记，**生成后自动发送到飞书**。

**NEW v2.14**：处理完成后的归档询问！飞书发送成功后主动问用户「是否把 PDF 移到报告喵文件夹并清理截图/封面」，确认后执行 mv + rm。

**NEW v2.13**：封面渲染约束固化！视口动态读 bounding_box、Tailwind JIT 编译等待、PIL 四角像素校验、CDN 资源全部本地化，封面稳定输出无白边/无白底。

**NEW v2.12**：支持指定报告日期！PDF重命名和封面生成可使用指定日期，批量重命名支持跳过周末。

**NEW v2.8**：社论风封面生成！处理 PDF 后自动生成现代社论风格封面图片（3:4比例），并与其他内容一起发送到飞书。

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

### 新增功能 v2.12 ⭐ NEW

#### PDF 智能重命名 📁

读取 PDF 后，自动将文件重命名为标准格式，方便归档和管理。

**命名格式**：`MMDD-Year+报告名称.pdf`

**命名规则**：
- **MMDD**：用户指定的报告日期（月日），如 `0406`、`0320`
- **Year**：年份（从标题提取，默认2026）
- **报告名称**：12个中文字以内，体现行业或品牌

**示例**：
```
0406-2026三元乳业老字号复兴报告.pdf
0320-2026母婴连锁数据经营报告.pdf
0227-2026珀莱雅化妆品研究报告.pdf
```

**重命名时机**：
- 在 PDF 解析完成后
- 在生成中文标题后
- **在飞书发送之前**（确保文件名已更新）

#### 批量重命名功能 🔄

支持对整个文件夹的PDF进行批量重命名。

**命令行使用**：
```bash
# 交互式输入开始日期
python3 scripts/file_namer.py --batch /path/to/folder

# 指定开始日期
python3 scripts/file_namer.py --batch /path/to/folder --date "0320"

# 跳过周末（仅工作日）
python3 scripts/file_namer.py --batch /path/to/folder --date "0320" --skip-weekend

# 试运行（不实际重命名）
python3 scripts/file_namer.py --batch /path/to/folder --date "0320" --dry-run
```

**参数说明**：
| 参数 | 说明 |
|------|------|
| `--batch, -b` | 指定PDF文件夹路径 |
| `--date, -d` | 开始日期（YYYY-MM-DD 或 MMDD） |
| `--skip-weekend` | 跳过周末，仅使用工作日 |
| `--dry-run` | 试运行，不实际重命名 |
| `--use-today` | 使用今天作为开始日期 |

**批量重命名行为（跳过周末示例）**：

假设开始日期是 **2026-03-20（周五）**，有5个PDF文件：

| PDF | 日期 | 星期 | 文件名 |
|-----|------|------|--------|
| 1 | 0320 | Fri | 0320-2026xxx.pdf |
| 2 | 0323 | Mon | 0323-2026xxx.pdf（跳过周末） |
| 3 | 0324 | Tue | 0324-2026xxx.pdf |
| 4 | 0325 | Wed | 0325-2026xxx.pdf |
| 5 | 0326 | Thu | 0326-2026xxx.pdf |

**注意**：
- 重命名后的文件保存在 `renamed/` 子文件夹
- 已符合标准格式的文件会被跳过
- 周六（0321）和周日（0322）被自动跳过
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

**封面参数提取规则** ⭐ UPDATED (v2.8.2)：

| 参数 | 提取来源 | 默认值 | 严格要求 |
|------|---------|--------|----------|
| source | 从封面页OCR或文字提取 | "研究报告" | - |
| page_count | PDFExtractor.total_pages | 自动获取 | **显示实际页数，不是日期** |
| chinese_title | 从PDF提取的精简标题 | - | **≤30字，3行内，含地域/品类** |
| english_title | 第二步生成的英文标题（转大写） | - | - |
| year | 从中文标题提取 `🎯YYYY` 格式 | 当前年份 | - |
| highlight_title | 从PDF提取的核心观点句 | "核心要点" | **必须是完整的一句话，不是标题** |
| summary_text | 从PDF提取的核心品类 | 根据标题生成 | **核心品类（如：饰品、玩具）** |
| report_type | 报告类型 | "行业研究报告" | - |
| number | 自动生成 | MMDD 格式 | - |

**封面三要素提取规则**（需要从PDF中反复提取和优化）：

1. **主标题（chinese_title）**：
   - 最多30个字，分3行显示（每行≤8字）
   - 必须包含地域（如：义乌）或品类（如：饰品）
   - 示例：`2026 义乌小商品城\n数智外贸转型报告`（14字，2行）
   - 示例：`2026 义乌饰品产业\n品类升级与渠道拓展报告`（18字，2行）

2. **摘要标题（highlight_title）**：
   - 从PDF核心观点中提取，必须是完整的一句话
   - 示例：`从市场运营商升级为数智外贸综合服务平台`
   - ❌ 不是：`数智化转型`（太短，不是完整句）

3. **核心品类（summary_text）**：
   - 从PDF中提取的核心品类词，替换原来的"发布年份"
   - 示例：`饰品、玩具、家居` 或 `饰品占比超30%`
   - ❌ 不是：`2026`

**提取方式**：

1. **source（来源）**：
   - 优先从PDF封面页提取文字（pymupdf的 `get_text()`）
   - 提取第一页的前500字符，匹配机构名称模式
   - 模式：`xxx研究院`、`xxx咨询`、`xxx证券` 等
   - 如果提取失败，使用默认值"研究报告"

2. **chinese_title（主标题）**：
   - 从PDF封面或标题页提取
   - 移除emoji后精简到≤30字
   - 必须包含地域（义乌）或核心品类
   - 分3行显示，每行≤8字

3. **highlight_title（摘要标题）**：
   - 从PDF核心观点或摘要中提取完整句子
   - 必须是完整的一句话，不是关键词或短语

4. **summary_text（核心品类）**：
   - 从PDF中提取的品类关键词
   - 用于替换网格区中间位置的"发布年份"

**长度限制规则**：

| 参数 | 限制 |
|------|------|
| 中文标题 | 每行最多8字 |
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

# 4. 转换为PNG并移动到screenshots目录
converter = HTMLToImageConverter()
png_result = converter.convert_to_xhs_style(
    html_path=cover_result['path']
)

# 将封面图移动到screenshots目录与截图一起管理
import shutil
import os
from pathlib import Path

screenshots_dir = Path.home() / ".claude" / "skills" / "baogaomiao" / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)

# 移动封面到screenshots目录
cover_png = Path(png_result['path'])
target_cover = screenshots_dir / cover_png.name
shutil.move(str(cover_png), str(target_cover))

# 5. 发送到飞书
sender.send_image(str(target_cover))
```

**封面图片保存位置** ⭐ UPDATED (v2.8.3)：
- 封面PNG生成后自动移动到 `screenshots` 目录
- 与6张PDF截图放在同一目录，方便管理

**封面图片发送位置**：
- 在PDF截图之后发送
- 消息顺序：小红书笔记 → 6张PDF截图 → 封面图

**消息接收顺序更新**：
```
1. 小红书笔记
2-7. 6张PDF截图
8. 封面图
```

#### 封面渲染约束（v2.13）⭐ NEW

为了保证封面稳定输出（无白边、比例正确、背景色到位），`scripts/html_to_image.py` 与 `scripts/editorial_cover.py` 必须共同遵守以下 5 条硬约束。**修改任一文件前请先核对这 5 条**：

| # | 约束 | 实现位置 | 说明 |
|---|------|---------|------|
| 1 | **视口 = 卡片实际 bounding_box** | `html_to_image.py` 关键步骤 1-2 | 视口尺寸不硬编码。先用 1200×1600 加载 HTML，读 `#editorial-card-container.getBoundingClientRect()`，再把视口设成卡片实际尺寸（当前 640×853）。 |
| 2 | **body 不允许 padding** | `editorial_cover.py` HTML_TEMPLATE | `<body style="margin: 0; padding: 0; width: 640px; height: 853px; overflow: hidden;">`，让视口与卡片完全对齐，消除周围红色边框。 |
| 3 | **截图前 Tailwind JIT 必须编译完成** | `html_to_image.py` 关键步骤 0 | `page.wait_for_function` 检查 `getComputedStyle(card).backgroundColor === 'rgb(251, 1, 81)'`，超时 15s。未编译会让背景变成白色。 |
| 4 | **截图后 PIL 校验四角像素** | `html_to_image.py` `_verify_corners()` | 校验 PNG 四角 `(5,5)`、`(w-5,5)`、`(5,h-5)`、`(w-5,h-5)` 均 ≈ `EXPECTED_BG_RGB=(251,1,81)`，容差 `PIXEL_TOLERANCE=12`。任一角不通过即报错（不删图，便于排查）。 |
| 5 | **本地化所有外部资源** | `scripts/assets/` | Tailwind Play CDN、Font Awesome、Google Fonts（Noto Serif SC / Oswald / Noto Sans SC）必须从本地 `scripts/assets/` 加载，HTML 模板用相对路径 `../assets/js/tailwind.js` 等注入。**禁止 CDN**（断网即失败）。 |

**截图 API 选择**：
- ✅ 用 `page.screenshot(path=..., full_page=False, scale='device')` —— 截整个视口，与卡片对齐
- ❌ 不要用 `locator.screenshot()` —— 字体加载超时会让截图失败

**HTML 加载方式**：
- ✅ `page.goto(html_file.resolve().as_uri(), wait_until='load')` —— 用 file:// 协议加载，浏览器能正确解析 `../assets/...` 相对路径
- ❌ 不要用 `page.set_content()` + file:// URI —— Chromium 会拒绝从 about:blank 加载本地文件

**像素校验失败排查**：
| 现象 | 原因 | 处理 |
|------|------|------|
| 四角全白 (255,255,255) | Tailwind JIT 没编译 | 检查 `tailwind.js` 是否加载、HTML 是否引入了 `bg-bgBase` |
| 四角红色但偏暗 | 抗锯齿/缩放 | 容差已设为 12，仍失败可调高 `PIXEL_TOLERANCE` |
| 仅某角偏色 | 卡片被裁切 | 视口尺寸与 bounding_box 不一致，检查约束 #1 |

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

#### PDF 截图功能 📷 ⭐ UPDATED (v2.8.1)

在解析 PDF 文档时，自动截取 **固定 6 张随机页面**作为参考图片：

**截图策略** ⭐ 严格要求：
- **固定数量**：必须截取 **6 张** 图片
- 跳过前2页（封面、目录等）
- 跳过最后5页（封底、免责声明等）
- 从剩余页面（第3页到倒数第6页）中随机选择 6 页
- 截取完整 A4 版面（全页面截图）
- 2x 缩放，retina 质量输出
- **截图逻辑独立**：不受 `max_pages` 参数影响，在整个PDF范围内选择截图页面

**示例**：
- 33页PDF → 跳过前2页和后5页 → 可选范围：第3-28页（26页）→ 随机选6页
- 20页PDF → 跳过前2页和后5页 → 可选范围：第3-15页（13页）→ 随机选6页
- 10页PDF → 跳过前2页和后5页 → 可选范围：第3-5页（3页）→ 全部截取（少于6张）

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

#### 内容提取原则 ⭐ IMPORTANT (v2.9)

**核心定位**：行业洞察笔记，**深度展开报告中的具体行业内容，而非投资相关信息**！

**内容质量要求**：
1. **拒绝干巴描述**：避免空洞的"增长"、"发展"等词汇，要用具体案例和数据说话
2. **深入展开行业内容**：根据报告中的行业信息深度展开分析
   - 技术壁垒与创新点
   - 产品线布局逻辑
   - 市场竞争格局变化
   - 产业链上下游动态
   - 消费者需求演变
   - 供应链与成本结构
3. **品类信息优先**：提取具体的产品品类、品牌、消费者行为变化
4. **细节要具体**：
   - ❌ "销售额增长" → ✅ "美妆品类销售额+23%，其中护肤彩妆占比超60%"
   - ❌ "渠道布局优化" → ✅ "抖音渠道GMV突破10亿，占比从5%提升至18%"
5. **数据优先**：保留关键数字和增长率
6. **对比突出**：正负对比、同期对比、竞品对比
7. **结论导向**：每段先说结论，再给数据支撑
8. **适度详细**：每章3-4个细节点，内容充实但不冗长
9. **数据解读**：不仅要给数据，还要说明数据背后的含义和趋势
10. **字数控制**：正文总字数控制在800字左右（不含标题、梗概、关键词）
11. **避免投资相关信息**：不讨论股价、不预测涨跌、不提供买入卖出建议

**品类信息提取清单**：
- [ ] 具体品类名称（如：美妆、母婴、食品饮料）
- [ ] 细分赛道（如：护肤、彩妆、个护）
- [ ] 品牌案例（具体品牌名、产品名）
- [ ] 消费者行为（购买偏好、使用场景）
- [ ] 渠道变化（线上线下、各平台占比）
- [ ] 价格带分布（高端/中端/大众，具体价格区间）

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
  • 封面图也保存到 ~/.claude/skills/baogaomiao/screenshots/（v2.8.3）
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
[步骤5：归档询问]（v2.14 ⭐ NEW）**在 Claude Code 对话里直接问用户**：
  "处理完成。是否将 PDF 移动到报告喵文件夹，并清理本地截图/封面？"
  • 目标目录：~/Library/Mobile Documents/com~apple~CloudDocs/家人共享/报告喵/
  • 用户确认后执行：
    1. mv 重命名后的 PDF（如 0701-2026xxx.pdf）从源目录到报告喵文件夹
    2. rm ~/.claude/skills/baogaomiao/screenshots/ 里本次生成的 6 张截图和封面 PNG
  • 用户拒绝则保留所有产物不动
↓
完成：用户可在飞书手机 APP 中查看完整笔记和截图
```

#### 归档询问硬性规则（v2.14）⭐ IMPORTANT

**询问方式**：**在 Claude Code 对话里直接问，不发飞书消息**。用户在终端回复 yes/no。

**询问时机**：飞书发送成功之后，立刻询问。**不允许跳过询问直接移动/删除**。

**询问措辞模板**：
> 处理完成。是否将 PDF `0701-2026xxx.pdf` 移动到 `~/Library/Mobile Documents/com~apple~CloudDocs/家人共享/报告喵/`，并清理本次截图和封面？

**用户确认后操作**：
1. **移动 PDF**：用 `mv` 把重命名后的 PDF 从源目录移动到报告喵目录（保留文件名）
2. **清理截图**：删除 `~/.claude/skills/baogaomiao/screenshots/` 下**本次生成**的截图（按文件名匹配本次 PDF 的 base name，不要误删其他 PDF 的截图）
3. **清理封面**：删除 `~/.claude/skills/baogaomiao/scripts/covers/` 下本次生成的 HTML 和 PNG
4. **不删除原始 PDF**（已经移动而非删除）
5. **不删除其他历史文件**

**安全保护**：
- ❌ 禁止不询问直接移动
- ❌ 禁止 `rm -rf` 整个 screenshots 目录（会误删其他 PDF 的截图）
- ❌ 禁止删除 `.pdf` 原始文件（只能 mv）
- ❌ 禁止通过飞书发送询问消息（询问只在 Claude Code 对话里）
- ✅ 删除前用 `ls` 列出待删文件让用户可见
- ✅ 用户拒绝时，所有文件保持原状

### 飞书发送配置 ⭐ UPDATED (v2.8)

#### 配置文件位置

飞书配置统一存储在用户配置文件中：

```
~/.feishu_user_config.json
```

**当前配置结构**（v3.0 - tenant_token模式）：
```json
{
  "app_id": "cli_a9d0ce936278dced",
  "app_secret": "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy",
  "user_open_id": "ou_55a1ea53df8c6fe203ecb456d0a4db54",
  "chat_id": "oc_922ab5c6faff499c0485499681a98f33",
  "folder_token": "",
  "target_table": {
    "app_token": "Fq2UwBpcIioq9skLNbocGiGKnsc",
    "table_id": "tblYOmRbvsHw5JxZ",
    "name": "默认导入表格"
  }
}
```

#### 飞书脚本路径 ⭐ IMPORTANT

**已验证的实际路径**：
```
/Users/echochen/Desktop/DMS/skills/feishu-universal/scripts/
├── feishu_bot_notifier.py     # 飞书机器人通知器（发送文本/图片）
├── feishu_paths.py             # 飞书路径管理
└── feishu_user_auto.py         # 飞书用户客户端
```

**路径发现工具**：
```bash
# 检查飞书设置状态
python3 scripts/feishu_finder.py --check

# 获取 notifier 路径
python3 scripts/feishu_finder.py --notifier

# 获取所有路径（JSON格式）
python3 scripts/feishu_finder.py --json
```

**Python调用**：
```python
from scripts.feishu_finder import FeishuFinder

finder = FeishuFinder()

# 获取脚本目录
scripts_dir = finder.get_scripts_dir()

# 获取 notifier 路径
notifier_path = finder.get_notifier_path()

# 检查是否有效
if finder.is_valid():
    print("✅ 飞书功能可用")
```

#### 环境变量配置（可选）

```bash
# 飞书 Webhook URL（优先使用）
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

# 飞书应用凭证（备用方案）
export FEISHU_APP_ID="cli_a9d0ce936278dced"
export FEISHU_APP_SECRET="your_app_secret"
```

#### 发送方式选择

**优先级**：
1. **Webhook 模式**：配置 `FEISHU_WEBHOOK_URL` 环境变量
2. **Bot Notifier 模式**：调用 `feishu-universal/scripts/feishu_bot_notifier.py`
3. **自动回退**：未配置时自动使用方案2

#### 路径问题排查 🔧

如果遇到"未找到 feishu_bot_notifier.py"错误：

**步骤1：运行路径检查**
```bash
cd ~/.claude/skills/baogaomiao
python3 scripts/feishu_finder.py --check
```

**步骤2：检查可能的位置**
```bash
# 检查 Desktop/DMS 路径
ls -la ~/Desktop/DMS/skills/feishu-universal/scripts/feishu_bot_notifier.py

# 检查 .claude/skills 路径
ls -la ~/.claude/skills/feishu-universal/scripts/feishu_bot_notifier.py

# 使用 find 搜索
find ~ -name "feishu_bot_notifier.py" -type f 2>/dev/null
```

**步骤3：验证配置文件**
```bash
# 检查配置文件是否存在
ls -la ~/.feishu_user_config.json

# 验证配置内容
cat ~/.feishu_user_config.json | python3 -m json.tool
```

**步骤4：测试飞书连接**
```bash
# 测试通知发送
python3 ~/Desktop/DMS/skills/feishu-universal/scripts/feishu_bot_notifier.py --test
```

#### 常见问题解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 未找到 feishu_bot_notifier.py | 路径解析错误 | 使用 `feishu_finder.py --check` 诊断 |
| 发送失败：99991663 | API限流 | 等待60秒后重试（已自动处理） |
| 发送失败：权限错误 | 配置文件凭证过期 | 检查 `~/.feishu_user_config.json` |
| 图片上传失败 | 文件路径不存在 | 验证图片文件路径正确性 |
| 截图生成失败 | pymupdf未安装 | `pip install pymupdf` |

#### 完整发送流程

```python
# 文本发送
from scripts.feishu_sender import FeishuSender

sender = FeishuSender()
result = sender.send(content, auto_send=True)

# 图片发送（批量）
from scripts.feishu_finder import FeishuFinder
finder = FeishuFinder()
notifier_path = finder.get_notifier_path()

# 使用 notifier 发送图片
import sys
sys.path.insert(0, str(finder.get_scripts_dir()))
from feishu_bot_notifier import FeishuBotNotifier

notifier = FeishuBotNotifier()
notifier.send_image_batch(image_paths, delay=1)
```

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

**内容质量和封面截图修复** (v2.8.1 - 2026-03-03)：
- ✅ **小红书笔记内容升级**：
  - 拒绝干巴描述，要求提取品类相关信息
  - 添加具体细节：品牌案例、产品品类、价格带、渠道占比
  - 明确定位：行业洞察笔记，不是投资建议
  - 新增品类信息提取清单
- ✅ **封面生成修复**：
  - 标题必须以"2026"开头（移除emoji后保留年份）
  - 页码显示实际页数 `{page_count}` 而非日期 `{day}`
- ✅ **截图功能修复**：
  - 修复截图逻辑bug：截图独立循环，覆盖整个PDF范围
  - 之前截图只在 `max_pages` 范围内检查，导致漏掉后续页面
  - 现在固定截取6张，不受文本提取页数限制
- ✅ 更新 SKILL.md 版本：v2.8.0 → v2.8.1
- ✅ **小红书笔记内容升级**：
  - 拒绝干巴描述，要求提取品类相关信息
  - 添加具体细节：品牌案例、产品品类、价格带、渠道占比
  - 明确定位：行业洞察笔记，不是投资建议
  - 新增品类信息提取清单
- ✅ **封面生成修复**：
  - 标题必须以"2026"开头（移除emoji后保留年份）
  - 页码显示实际页数 `{page_count}` 而非日期 `{day}`
- ✅ **截图功能修复**：
  - 修复截图逻辑bug：截图独立循环，覆盖整个PDF范围
  - 之前截图只在 `max_pages` 范围内检查，导致漏掉后续页面
  - 现在固定截取6张，不受文本提取页数限制
- ✅ 更新 SKILL.md 版本：v2.8.0 → v2.8.1

**使用效果**：
```python
# 33页PDF，截图不再受max_pages=10限制
extractor = PDFExtractor(pdf_path, enable_screenshots=True)
result = extractor.extract(max_pages=10)
# 截图范围：第3-28页（26页可选），随机选6页
# 结果：第3、13、14、17、20、27页 ✅
```

**路径配置和发现功能** (v2.8 - 2026-03-03)：
- ✅ 创建 `feishu_finder.py` 路径发现工具：自动定位 feishu-universal 脚本
- ✅ 更新 SKILL.md：添加完整的飞书发送配置章节
- ✅ 记录已验证的实际路径：`/Users/echochen/Desktop/DMS/skills/feishu-universal/scripts/`
- ✅ 新增路径问题排查指南：4步诊断流程 + 常见问题解决表
- ✅ 提供多种使用方式：类接口、函数接口、CLI命令

**使用效果**：
```python
# 路径检查
python3 scripts/feishu_finder.py --check
# 输出：飞书路径检查 v3.0
#       ✅ 找到脚本目录: /Users/echochen/Desktop/DMS/skills/feishu-universal/scripts
#       ✓ feishu_bot_notifier.py → /path/to/feishu_bot_notifier.py
#       ✓ feishu_paths.py → /path/to/feishu_paths.py
#       ✓ feishu_user_auto.py → /path/to/feishu_user_auto.py

# Python调用
from scripts.feishu_finder import FeishuFinder
finder = FeishuFinder()
notifier_path = finder.get_notifier_path()
# 自动返回正确的路径，无需硬编码
```

**解决的核心问题**：
- ✅ 消除"未找到 feishu_bot_notifier.py"错误
- ✅ 提供统一的路径发现接口
- ✅ 支持多个可能位置的自动检测
- ✅ 简化飞书功能集成

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

**封面生成修复** (v2.8.2 - 2026-03-03)：
- ✅ 移除标题"2026"后面的空格：`f"2026{chinese_title}"`
- ✅ 智能换行保护短语："义乌小商品城"不被断开，短语列表可配置
- ✅ 页码字号调整：`text-[5rem]` 替代 `text-4rem`
- ✅ 网格区中间改为"核心品类"：图标从 `fa-calendar` 改为 `fa-tag`
- ✅ 添加 `categories` 参数到 `generate_cover()` 方法：支持传递核心品类信息

**封面参数提取规则**（需要从PDF中反复提取和优化）：

1. **主标题（chinese_title）**：
   - 最多30个字，分3行显示（每行≤8字）
   - 必须包含地域（如：义乌）或品类（如：饰品）
   - 示例：`2026 义乌小商品城\n数智外贸转型报告`（14字，2行）
   - 示例：`2026 义乌饰品产业\n品类升级与渠道拓展报告`（18字，2行）

2. **摘要标题（highlight_title）**：
   - 从PDF核心观点中提取，必须是完整的一句话
   - 示例：`从市场运营商升级为数智外贸综合服务平台`
   - ❌ 不是：`数智化转型`（太短，不是完整句）

3. **核心品类（categories）**：
   - 从PDF中提取的品类关键词，替换原来的"发布年份"
   - 示例：`饰品、玩具、家居` 或 `饰品占比超30%`
   - ❌ 不是：`2026`

EOF

---

#### 修复记录

**小红书笔记生成要求升级** (v2.9 - 2026-03-04)：
- ✅ **深入展开行业内容**：根据报告中的行业信息深度展开分析
   - 技术壁垒与创新点
   - 产品线布局逻辑
   - 市场竞争格局变化
   - 产业链上下游动态
   - 消费者需求演变
   - 供应链与成本结构
- ✅ **避免投资相关信息**：不讨论股价、不预测涨跌、不提供买入卖出建议
- ✅ **内容质量要求扩充**：新增11项具体要求，确保笔记有借鉴意义

**封面断句修复** (v2.10 - 2026-03-04)：
- ✅ **年份单独第一行**：修复年份提取逻辑，"2026"始终作为第一行单独显示
- ✅ **短语保护正确**：修复断句逻辑，保护"海菲曼电声"、"义乌小商品城"、"数智外贸"、"母婴连锁"等语义单元不被断开
- ✅ **正则表达式修复**：修复年份提取正则 `^(20\d{2})`，正确匹配4位年份
- ✅ **使用\n替代<br>**：改用 `\n` 作为换行符，确保HTML正确渲染

**修复效果**：
```python
# 示例1：电声行业高端品牌商
# 结果：2026\n电声行业高端品\n牌商 —— 创新赋\n能全球影响力

# 年份单独第一行，每行最多8字，短语保持完整
```

**标题生成和断句修复** (v2.11 - 2026-03-04)：
- ✅ **标题格式统一**：更新`_generate_chinese_title`方法，符合SKILL.md要求的 `🎯2026 [主标题] —— [副标题]` 格式
- ✅ **主副标题提取**：从PDF文本中智能提取主标题（≥6字）和副标题（10-20字）
- ✅ **断句逻辑修复**：修复editorial_cover.py中的年份提取和短语保护逻辑
  - 修复空行判断条件：移除 `current_line and` 的多余检查
  - 年份始终单独第一行：即使标题不含年份也使用"2026"作为第一行
  - 短语保护生效："海菲曼电声"、"义乌小商品城"、"数智外贸"、"母婴连锁"等保持完整
  - 使用 `<br>` 标签：确保HTML正确渲染换行




