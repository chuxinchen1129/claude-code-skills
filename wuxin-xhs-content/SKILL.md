---
name: wuxin-xhs-content
description: |
  小红书科普图文生成器。当用户提到：
  - "生成科普图文"、"小红书图文"、"悟昕科普"
  - "生成小红书内容"、"小红书笔记"
  - "睡眠科普内容"、"Huberman科普"

  支持：营销日历驱动、科学概念匹配、并发生成、CSV输出
version: 1.0.0
created: 2026-02-26
updated: 2026-02-26
---

# 小红书科普图文生成器

**技能名称**：wuxin-xhs-content

**用途**：基于睡眠科学 Wiki 生成小红书科普图文内容

---

## 功能概览

| 功能 | 输入 | 输出 |
|------|------|------|
| **日历生成** | 营销日历+日期范围 | 发布计划 |
| **内容生成** | 主题+受众+痛点+概念 | JSON格式内容 |
| **批量生成** | ZhipuAI API并发生成 | CSV文件 |

---

## 使用场景

### 场景1：日期范围生成

**用户说**：
- "生成本周的小红书内容"
- "生成2026-02-26到2026-03-05的内容"

**自动执行**：
```
1. 读取营销日历
2. 生成发布计划（周一到周四）
3. 匹配科学概念
4. 并发生成内容（ZhipuAI）
5. 输出CSV文件
```

**输出**：`Content_YYYYMMDD_to_YYYYMMDD.csv`

### 场景2：单篇生成

**用户说**：
- "生成一篇关于助眠的科普图文"
- "主题：深睡，受众：职场人士"

---

## CLI 命令

```bash
# 生成今天之后7天的内容
python src/main.py

# 生成指定日期范围的内容
python src/main.py --start_date 2026-02-26 --end_date 2026-03-05

# 生成全部内容
python src/main.py --full
```

---

## 输出格式

### CSV 字段

| 字段 | 说明 | 示例 |
|------|------|------|
| Date | 发布日期 | 2026-02-26 |
| Theme | 内容主题 | 深睡质量提升 |
| Audience | 目标受众 | 职场人士 |
| Pain_Point | 核心痛点 | 睡够8小时还是累 |
| Product_Feature | 产品卖点 | 脑电波监测80%准确率 |
| Science_Concept | 科学概念 | Deep Sleep |
| Is_Marketing_Node | 是否营销节点 | Yes/No |
| Note_Title | 笔记标题（SEO） | 睡够8小时=白睡？ |
| Cover_Text | 封面大字（视觉） | 你的睡眠达标了吗？ |
| Content_Body | 完整正文 | intro + 3板块 + CTA |
| Section1/2/3_Header | 板块小标题 | 大脑洗澡、深度修复... |

---

## 内容结构

### 标准结构

```
开篇引入 (intro) - 30-50字
    ↓
板块1 (section_1) - 150字
    └─ 小标题 (4-8字)
    └─ 正文内容
    ↓
板块2 (section_2) - 150字
    └─ 小标题 (4-8字)
    └─ 正文内容
    ↓
板块3 (section_3) - 150字
    └─ 小标题 (4-8字)
    └─ 正文内容
    ↓
产品植入 (product_cta) - 50-80字
```

---

## 品牌调性

### 语气要求
- 温暖治愈
- 科学循证
- 优雅克制

### 禁用词汇
- 家人们
- 绝绝子
- 根治
- 第一
- 必需

### 品牌定位约束
- 悟昕 Zenoasis 是智能睡眠设备品牌，**不是营养补充剂公司**
- 禁止提及：镁、褪黑素、维生素、营养素、补充剂、胶囊、片剂等
- 产品特性：CES物理助眠、脑电监测、白噪音、零漏音、便携设计

---

## 配置

**共享配置**：`03_WUXIN_CONTENT/assets/config.yaml`

**本地配置**：`config.yaml`
```yaml
# 引用共享配置
include: ../../03_WUXIN_CONTENT/assets/config.yaml

# 技能特定配置
api:
  model: glm-4.7
  max_tokens: 3000
  temperature: 0.7
  timeout: 120

defaults:
  sections: 3
  target_words: 500
  brand_integration: soft
```

---

## 依赖资源

| 资源类型 | 路径 |
|---------|------|
| 营销日历 | `00_Strategy_Planning/marketing_calendar.csv` |
| 科学概念库 | `05_Sleep_Science_Wiki/sleep_science.json` |
| 通用主题库 | `general_topics_extended.csv` |
| 品牌资产 | `assets/brand/` |
| 内容模板 | `assets/templates/xhs-content/` |

---

## AI模型配置

- **模型**: ZhipuAI GLM-4.7
- **并发数**: 3
- **超时**: 120秒
- **重试**: 3次（指数退避）

---

## 相关文档

- 图文模板：`03_WUXIN_CONTENT/assets/templates/xhs-content/小红书图文模板.md`
- 品牌卖点：`03_WUXIN_CONTENT/assets/brand/selling-points.md`
- 知识库：`03_WUXIN_CONTENT/assets/wiki/guides/`
