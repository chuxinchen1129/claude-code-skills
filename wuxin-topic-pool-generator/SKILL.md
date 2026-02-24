---
name: wuxin-topic-pool-generator
description: 生成悟昕短视频脚本的话题池。支持基础选题生成、场景裂变（5维度）、选题优化。当用户提到"生成话题池"、"话题池生成"、"悟昕话题"、"wuxin-topic"时使用。
---

# 悟昕话题池生成器

**Skill名称**：wuxin-topic-pool-generator

**用途**：生成悟昕短视频脚本的话题池（选题裂变）

**适用场景**：
- 营销节点规划（女神节、母亲节、520等）
- 选题库建设
- 内容规划前期调研

---

## 快速开始

用户触发本Skill时，请求以下必填信息：

```
请提供以下信息：
1. 营销节点（如：女神节、母亲节、520表白日）
2. 基础选题数量（默认10个）
3. 每个选题裂变数（默认5个）
```

---

## 工作流程

### 步骤1：读取品牌资产和营销日历

**品牌资产路径**（默认）：
- 品牌卖点库：`/知识库/悟昕资产库/01-品牌档案/悟昕睡眠仪-ToC卖点库.md`
- 品牌知识库：`/知识库/悟昕资产库/01-品牌档案/悟昕科技知识库.md`

**营销日历路径**（默认）：
- `../00.Wuxin_Zenoasis_Content_Project/00_Strategy_Planning/marketing_calendar.csv`

### 步骤1.5：场景分布比例讨论 ⭐ NEW

**目的**：分析当前场景分布，与用户讨论场景比例是否合理

**执行内容**：

1. **分析当前场景分布**
   - 统计各场景类型的数量和占比
   - 识别场景过于集中或缺失的场景类型
   - 显示场景分布数据

2. **生成场景分布建议**
   根据营销节点类型（送礼/科普/促销）生成场景建议
   - 提供推荐场景比例
   - 说明理由

3. **与用户讨论**
   - 使用 AskUserQuestion 工具征求用户意见
   - 让用户选择：接受建议、自定义比例、跳过调整

**实施指南**：
```python
# 读取候选选题（步骤1）
df = pd.read_excel('/Users/echochen/Desktop/DaMiShuSystem-main-backup/母亲节_话题池.xlsx')

# 步骤1.5：场景分布比例讨论
# 1. 分析当前场景分布
scene_distribution = df['场景分类'].value_counts()
total_count = len(df)

print("=== 场景分布分析 ===")
print(f"总选题数: {total_count}")
for scene, count in scene_distribution.items():
    percentage = (count / total_count) * 100
    print(f"{scene}: {count}个 ({percentage:.1f}%)")
```

# 2. 显示Markdown表格
distribution_table = pd.DataFrame({
    '场景类型': scene_distribution.index.tolist(),
    '数量': scene_distribution.values.tolist(),
    '占比 (%)': [(count / total_count * 100) for count in scene_distribution.values.tolist()]
})
print("\n场景分布表格:")
print(distribution_table.to_markdown(index=False))

# 3. 生成建议（根据营销节点类型）
marketing_node = "母亲节(5.10)"
if "母亲节" in marketing_node or "送礼" in marketing_node:
    suggested_distribution = {
        '送礼场景': 50,
        '使用感受场景': 20,
        '情感共鸣场景': 10,
        '更年期场景': 10,
        '其他场景': 10
    }
    reason = "母亲节以送礼为主，建议送礼场景占50%"
else:
    suggested_distribution = {'送礼场景': 40}  # 默认配置
    reason = "默认配置"

print("\n=== 场景分布建议 ===")
print(f"营销节点: {marketing_node}")
print(f"建议分布: {suggested_distribution}")
print(f"理由: {reason}")
```

# 4. 与用户讨论（使用AskUserQuestion）
# 在实际执行中，需要使用AskUserQuestion工具征求用户意见

```

---

### 步骤2：生成基础选题

生成{基础选题数量}个基础选题，每个包含：
- 场景分类
- 目标人群
- 核心痛点
- 营销切入角度
- 选题标题（15-25字）

**场景类型**：
- 送礼场景：送礼对象（父母/伴侣/闺蜜/自己）
- 爱自己：犒劳自己场景
- 闺蜜/朋友：闺蜜互动场景
- 职场女性/自己：职场压力场景
- 家庭场景：家庭互动场景

### 步骤3：场景裂变（5维度）

对每个基础选题生成{每个选题裂变数}个变体：

**维度1：场景显微镜（画面细节）**
- 目标：将场景放大到极致细节
- 要求：具体的画面描述、场景氛围营造

**维度2：认知粉碎机（科学概念）**
- 目标：用科学原理冲击用户认知
- 要求：引入脑电波、CES、80%准确率等科学概念

**维度3：情绪共振器（第一人称）**
- 目标：用第一人称引发情感共鸣
- 要求：强代入感的叙事、情绪词汇丰富

**维度4：剧情反转器（意外转折）**
- 目标：制造意想不到的转折
- 要求：开头假设A，结尾揭示B

**维度5：社交话题器（讨论性）**
- 目标：引发讨论和传播
- 要求：争议性/话题性的切入点

### 步骤4：选题优化

**优化方向**：
1. 词汇规范化：将"三八"替换为"女神节/女生节/女王节"
2. 钩子增强：数据冲击型、痛点直击型、反常识型、悬念设置型
3. 标题隐形化：90%爆款标题不直接说产品名
4. 口语化表达：避免AI味（"在当今时代"、"综上所述"）

### 步骤5：输出格式

**JSON格式**：
```json
{
  "marketing_node": "女神节",
  "base_topics_count": 10,
  "fission_count_per_topic": 5,
  "total_topics": 50,
  "topics": [
    {
      "id": 1,
      "base_topic_id": 1,
      "fission_type": "场景显微镜",
      "scene_category": "送礼场景",
      "target_audience": "闺蜜/朋友",
      "core_pain_point": "...",
      "marketing_angle": "...",
      "title": "...",
      "optimized": true
    }
  ]
}
```

**Excel格式**：
| 营销节点 | 基础选题ID | 裂变类型 | 场景分类 | 目标人群 | 核心痛点 | 营销切入角度 | 选题标题 | 是否优化 |
|---------|-----------|---------|---------|---------|-----------|-----------|----------|----------|
| 女神节 | 1 | 场景显微镜 | 送礼场景 | 闺蜜/朋友 | ... | ... | ... | ✅ |

---

## 质量标准

### 选题质量要求

| 检查项 | 说明 | 标准 |
|---------|------|------|
| **营销节点关联** | 必须与营销节点强关联 | ✅ 必须包含节点关键词 |
| **场景多样性** | 场景分类不重复 | ✅ 同一场景最多2个 |
| **人群细分** | 目标人群具体化 | ✅ 避免"全人群"等模糊表达 |
| **痛点具体化** | 痛点描述具体 | ✅ 不使用抽象标签 |
| **钩子强度** | 标题有吸引力 | ✅ 15-25字，有冲击力 |
| **词汇规范性** | 符合营销节日调性 | ✅ 不使用不当词汇 |

---

## 输出文件

输出文件保存到当前工作目录：
- `{营销节点}_话题池.json` - 完整JSON格式
- `{营销节点}_话题池.xlsx` - Excel格式便于查看

---

## 与其他Skill的关系

| Skill | 输入 | 输出 | 关系 |
|-------|------|------|------|
| wuxin-topic-pool-generator | 营销节点、选题数量 | 候选选题列表 | → wuxin-topic-rater |
| wuxin-topic-rater | 候选选题列表 | 高质量选题列表 | ← wuxin-topic-pool-generator |
