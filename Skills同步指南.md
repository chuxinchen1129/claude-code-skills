# Skills 同步指南

> **目标**: 在两台电脑上同步 Claude Code Skills
> **状态**: Git 仓库已初始化，待推送到 GitHub
> **位置**: ~/.config/claude-code/skills/

---

## 📋 第 1 步：在 GitHub 创建仓库（2 分钟）

### 1.1 创建仓库

1. **访问**: https://github.com/new
2. **填写信息**:
   - **Repository name**: `claude-code-skills`
   - **Description**: `Claude Code 技能包 - weChat-article-creator、pptx、xlsx、skill-creator`
   - **Visibility**: 选择 **Private**（私有）⚠️
3. **不要勾选**:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
4. **点击**: "Create repository"

---

## 📋 第 2 步：推送到 GitHub（1 分钟）

### 2.1 添加远程仓库并推送

**打开终端，执行**:

```bash
cd ~/.config/claude-code/skills
git remote add origin git@github.com:chuxinchen1129/claude-code-skills.git
git branch -M main
git push -u origin main
```

---

## 📋 第 3 步：在另一台电脑克隆（2 分钟）

### 3.1 确认环境

**检查 Git**:
```bash
git --version
```

**检查 SSH 密钥**:
```bash
ls ~/.ssh/id_ed25519.pub
```

**如果没有 SSH 密钥**，生成一个：
```bash
ssh-keygen -t ed25519 -C "chuxinchen1129@github" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub  # 复制公钥到 GitHub
```

### 3.2 备份现有 Skills（重要！）

**在另一台电脑，如果已有 skills**:
```bash
# 备份现有 skills
mv ~/.config/claude-code/skills ~/.config/claude-code/skills.backup
```

**或者直接删除**（如果你确定不需要）:
```bash
rm -rf ~/.config/claude-code/skills
```

### 3.3 克隆 Skills

**在另一台电脑执行**:

```bash
# 创建父目录（如果不存在）
mkdir -p ~/.config/claude-code

# 克隆 skills
cd ~/.config/claude-code
git clone git@github.com:chuxinchen1129/claude-code-skills.git skills
```

---

## 📋 第 4 步：验证 Skills（1 分钟）

### 4.1 检查文件结构

**在另一台电脑验证**:
```bash
ls ~/.config/claude-code/skills/
```

**应该看到**:
- ✅ weChat-article-creator/
- ✅ pptx/
- ✅ xlsx/
- ✅ skill-creator/

### 4.2 验证 Claude Code 能识别

**打开 Claude Code，执行**:
```
列出所有可用的 skills
```

**应该看到**:
- ✅ weChat-article-creator
- ✅ pptx
- ✅ xlsx
- ✅ skill-creator

---

## 📊 Skills 内容统计

**包含的技能包**:

### 1. weChat-article-creator（最重要）
- **文件数**: 约 20+ 个
- **大小**: 约 2.5 MB
- **用途**:
  - 自媒体写作（商业分析、科普文章）
  - 品牌推广（公关软文、官方媒体、合作方、小红书）
  - 三遍审校、选题讨论、调研方法
- **核心文档**:
  - SKILL.md（主配置）
  - three_pass_review.md（三遍审校）
  - topic_frameworks.md（选题框架）
  - personal_material_guide.md（个人素材库）

### 2. pptx
- **用途**: PowerPoint 文档创建
- **功能**: HTML 转 PPTX

### 3. xlsx
- **用途**: Excel 表格创建
- **功能**: 数据格式化、公式

### 4. skill-creator
- **用途**: 创建新的技能包
- **功能**: 技能开发工具

---

## 📋 日常使用

### 同步最新 Skills

**开始工作前**（任一电脑）:
```bash
cd ~/.config/claude-code/skills
git pull
```

### 推送修改

**修改 Skills 后**（任一电脑）:
```bash
cd ~/.config/claude-code/skills
git add .
git commit -m "更新：优化写作技能"
git push
```

---

## ⚠️ 重要提示

### 备份现有 Skills

**在另一台电脑克隆前**，一定要：
1. ✅ 备份现有的 skills 目录
2. ✅ 或者确保本地不需要保留

### 技能包位置

**Claude Code 会从以下位置读取 Skills**:
```
~/.config/claude-code/skills/
├── weChat-article-creator/
├── pptx/
├── xlsx/
└── skill-creator/
```

**克隆后，路径会自动正确**:
```bash
cd ~/.config/claude-code
git clone git@github.com:chuxinchen1129/claude-code-skills.git skills
# 结果：~/.config/claude-code/skills/weChat-article-creator/
```

---

## 🎯 完整同步方案

### 三个系统都已配置 Git

1. **ObsidianVault-2026**
   - 位置: ~/Documents/ObsidianVault-2026/
   - GitHub: https://github.com/chuxinchen1129/ObsidianVault-2026
   - 用途: 知识管理、笔记、复盘

2. **DaMiShuSystem（大秘书系统）**
   - 位置: ~/Desktop/大秘书系统/
   - GitHub: https://github.com/chuxinchen1129/DaMiShuSystem
   - 用途: 项目管理、知识库、数据分析、写作

3. **claude-code-skills** ⭐ NEW
   - 位置: ~/.config/claude-code/skills/
   - GitHub: https://github.com/chuxinchen1129/claude-code-skills
   - 用途: Claude Code 技能包

---

## 🚀 快速开始（最小步骤）

### 当前电脑（现在）

**执行**:
```bash
cd ~/.config/claude-code/skills
git remote add origin git@github.com:chuxinchen1129/claude-code-skills.git
git branch -M main
git push -u origin main
```

### 另一台电脑（稍后）

**执行**:
```bash
# 1. 备份现有 skills（如果有）
mv ~/.config/claude-code/skills ~/.config/claude-code/skills.backup

# 2. 克隆新的 skills
cd ~/.config/claude-code
git clone git@github.com:chuxinchen1129/claude-code-skills.git skills

# 3. 验证
ls ~/.config/claude-code/skills/
```

---

## 📞 需要帮助？

如果遇到问题：
1. 复制错误信息
2. 在对话中告诉我
3. 我会帮你解决

---

**准备好了就开始推送吧！** 🚀

**仓库地址**: https://github.com/new
**仓库名**: `claude-code-skills`
