# 悟昕睡眠热点采集分析系统

> 自动采集和分析睡眠相关内容的热点数据

## 📖 简介

这是一个为悟昕（Zenoasis）睡眠仪品牌设计的内容情报分析系统，能够自动采集小红书、微信公众号、抖音等平台的睡眠相关内容，分析爆款特征，生成分析报告并上传到飞书。

## 🎯 核心功能

### 1. 小红书自动采集
- 关键词：睡眠仪、左点、睡眠等
- 筛选：TOP30 高互动笔记
- 数据：笔记、评论、封面、视频

### 2. 多平台链接处理
- 支持平台：小红书、微信公众号、抖音、通用网页
- 自动识别平台类型
- 使用对应工具抓取内容

### 3. 视频转文字
- 自动下载视频
- 使用 AI 转换为文字
- 保存为文本文件

### 4. 每周自动分析
- 爆款特征识别
- 标题公式分析
- 内容结构分析
- 核心卖点统计

### 5. 飞书集成
- 自动上传数据
- 生成多维表格
- 发送完成通知

## 🚀 快速开始

### 方式一：通过 Claude Code 触发

直接对 Claude 说：
- "采集小红书睡眠热点"
- "分析这个链接" + 链接
- "执行每周内容分析"

### 方式二：直接运行脚本

```bash
# 小红书采集
cd /Users/echochen/Desktop/DaMiShuSystem-main-backup/00.Wuxin_Zenoasis_Content_Project/.claude/skills/wuxin-sleep-hotspot-collector
python3 scripts/xiaohongshu_collector.py

# 处理链接
python3 scripts/link_processor.py "https://..."

# 每周分析
python3 scripts/weekly_analyzer.py
```

## 📁 目录结构

```
wuxin-sleep-hotspot-collector/
├── SKILL.md                    # Skill 主文件
├── README.md                   # 本文件
├── scripts/                    # Python 脚本
│   ├── xiaohongshu_collector.py    # 小红书采集
│   ├── link_processor.py           # 链接处理器
│   └── weekly_analyzer.py          # 每周分析器
├── references/                 # 参考文档
│   ├── 爆款特征分析模板.md
│   ├── 标题公式库.md
│   └── 内容结构分析框架.md
├── config/                     # 配置文件
│   ├── keywords.json           # 关键词配置
│   └── platforms.json          # 平台配置
└── data/                       # 数据存储
    ├── xiaohongshu_collection/ # 小红书采集数据
    ├── feishu_input/           # 飞书输入数据
    └── weekly_reports/         # 每周分析报告
```

## ⚙️ 配置

### 修改采集关键词

编辑 `config/keywords.json`：

```json
{
  "xiaohongshu": ["睡眠仪", "左点", "睡眠"],
  "douyin": ["睡眠仪", "左点睡眠仪"],
  "wechat": ["睡眠", "失眠", "助眠"]
}
```

### 修改平台配置

编辑 `config/platforms.json`：

```json
{
  "xiaohongshu": {
    "enabled": true,
    "min_likes": 100,
    "top_n": 30
  }
}
```

## 🔗 依赖技能

| Skill | 用途 |
|-------|------|
| media-crawler | 小红书数据采集 |
| baoyu-url-to-markdown | 微信/网页转 Markdown |
| douyin-mcp | 抖音视频解析 |
| video-scripts-extract | 视频转文字 |
| feishu-automation-v2 | 飞书上传和通知 |
| daily-review | 定时任务调度 |

## 📊 使用场景

### 场景 1：每周自动采集

**设置定时任务**：
```bash
# 编辑 crontab
crontab -e

# 添加：每周一中午 12 点执行
0 12 * * 1 cd /path/to/wuxin-sleep-hotspot-collector && python3 scripts/xiaohongshu_collector.py
```

### 场景 2：手动分析链接

**对 Claude 说**：
```
"分析这个小红书笔记"
https://www.xiaohongshu.com/...
```

### 场景 3：生成分析报告

**对 Claude 说**：
```
"执行每周内容分析"
```

## 📈 分析报告示例

每周分析报告包含：

1. **数据概览**：采集笔记数、总互动量、爆款笔记数
2. **爆款特征**：
   - 标题公式 TOP5
   - 内容结构分析
   - 核心卖点使用
3. **趋势洞察**：
   - 新兴话题
   - 情感词汇 TOP10
4. **更新建议**：
   - 建议添加的案例
   - 内容创作建议

## ⚠️ 注意事项

1. **首次使用**：确保已配置相关依赖技能
2. **飞书上传**：需要先完成 OAuth 授权（feishu-automation-v2）
3. **视频处理**：视频转文字需要 DASHSCOPE_API_KEY 环境变量
4. **数据量**：大量采集可能需要较长时间

## 🔄 定期维护

### 每周
- 检查采集数据质量
- 更新标题公式库
- 调整关键词配置

### 每月
- 分析爆款趋势变化
- 优化内容结构识别
- 更新核心卖点库

### 每季度
- 全面审查分析模板
- 更新平台配置
- 优化脚本性能

## 🐛 故障排除

### 问题 1：采集失败

**检查**：
- MediaCrawler Skill 是否已安装
- 网络连接是否正常
- 关键词是否正确

### 问题 2：视频转文字失败

**解决**：
```bash
export DASHSCOPE_API_KEY=your_key_here
```

### 问题 3：飞书上传说失败

**解决**：
```bash
# 重新完成 OAuth 授权
python3 ~/Desktop/DaMiShuSystem-main-backup/feishu_oauth_setup.py
```

## 📝 版本历史

### v1.0.0 (2026-02-10)

**初始功能**：
- ✅ 小红书自动采集
- ✅ 多平台链接处理
- ✅ 视频下载和转文字
- ✅ 每周自动分析
- ✅ 飞书上传集成

## 📧 反馈

如有问题或建议，请联系大秘书系统。

---

**创建时间**: 2026-02-10
**版本**: v1.0.0
**作者**: 大秘书系统
