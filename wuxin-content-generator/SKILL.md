---
name: wuxin-content-generator
description: ⚠️ **已废弃** - 此技能已拆分为4个独立技能，请使用新技能
version: 1.0.0
created: 2026-02-25
updated: 2026-02-25
status: deprecated
---

# ⚠️ 此技能已废弃

**废弃日期**: 2026-02-26
**原因**: 功能已拆分到4个独立技能，提供更好的模块化和可维护性

---

## 请使用以下新技能

| 新技能 | 功能 | 触发词 |
|--------|------|--------|
| **wuxin-script-generator** | 视频脚本生成器 | "生成视频脚本"、"悟昕脚本"、"30秒脚本" |
| **wuxin-xhs-content** | 小红书科普图文生成器 | "生成科普图文"、"小红书图文"、"悟昕科普" |
| **wuxin-pr-article** | 公关文章生成器 | "生成公关文章"、"品牌软文"、"媒体稿件" |
| **wuxin-wechat-article** | 公众号文章生成器 | "生成公众号文章"、"微信推文"、"长文" |

---

## 迁移指南

### 如果你之前使用此技能生成小红书图文
→ 使用 **wuxin-xhs-content** 技能

### 如果你需要生成视频脚本
→ 使用 **wuxin-script-generator** 技能

### 如果你需要生成公关文章
→ 使用 **wuxin-pr-article** 技能

### 如果你需要生成长文/公众号文章
→ 使用 **wuxin-wechat-article** 技能

---

## 保留内容（仅供参考）

以下内容保留用于参考，完整功能已迁移到新技能：

### 原 Skill 功能
- 根据睡眠科学 Wiki 内容生成小红书科普图文
- 支持多种主题（助眠、早醒、深度睡眠、失眠）
- 自动生成标题、正文、标签
- 支持图片素材关联
- 集成 MediaCrawler 数据采集
- 集成飞书自动化上传

## 使用方法
```bash
cd ~/Desktop/DMS/skills/wuxin-content-generator
python src/generate_content.py --topic "助眠" --output ./output
```

## 配置
将环境变量存储在 `.env` 文件：
\`\`\`bash
XIAOHONGSHU_API_KEY=your_api_key
WUXIN_API_KEY=your_api_key
OUTPUT_DIR=~/Desktop/DMS/03_WUXIN_CONTENT/output/
\`\`\`

## 依赖
- Python 3.9+
- openai
- requests
- MediaCrawler
- feishu-automation-v2

## 核心文件
- \`src/\` - 源代码目录
- \`tools/\` - 工具脚本目录
- \`assets/\` - 品牌资源（睡眠科学 Wiki）
- \`config.yaml\` - 配置文件
- \`requirements.txt\` - Python 依赖

## 相关 Skills
- wuxin-sleep-hotspot-collector - 睡眠热点采集
- wuxin-topic-pool-generator - 话题池生成
- wuxin-topic-rater - 话题评分

## 相关文档
- 03_WUXIN_CONTENT/campaigns/active/ 悟昕投放视频脚本
- 03_WUXIN_CONTENT/assets/悟昕资产库/ 品牌资源
- 05_SYSTEM_DOCS/global_brain/GLOBAL_LESSONS.md - 全局经验库

## 使用场景
1. **小红书科普内容生成**
   - 用户说"生成睡眠科普内容"、"小红书图文"
   - 输入主题关键词
   - 输出图文内容（标题+正文+标签）

2. **批量内容创作**
   - 用户提供主题列表
   - 批量生成多个图文内容
   - 支持飞书自动上传

3. **素材管理**
   - 查询睡眠科学 Wiki
   - 关联品牌资源
   - 调用图片素材

## 注意事项
- 确保环境变量正确配置
- 首次运行前检查依赖是否安装
- 输出目录权限可写
