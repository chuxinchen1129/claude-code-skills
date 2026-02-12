# Claude Skills Collection

这是你安装的所有 Claude Skills 的集合目录。

## 📚 已安装的 Skills (6)

| Skill | 描述 | 命令 |
|-------|------|------|
| **pdf** | PDF 处理工具包 - 提取文本/表格、合并/拆分、旋转页面 | `/pdf` |
| **xlsx** | Excel 工具包 - 创建/编辑/分析表格数据 | `/xlsx` |
| **pptx** | PowerPoint 工具包 - 创建/编辑演示文稿 | `/pptx` |
| **lark-connector** | 飞书/Lark 连接器 - 文档、表格、消息操作 | `/lark` |
| **skill-creator** | Skill 创建器 - 快速创建新技能 | `/create-skill` |
| **doc-to-table** | 文档转表格 - 将任意格式文档转为 Excel | `/table` |

## 📂 目录结构

```
~/.claude/
├── skills/                    # Skills 文档（本目录）
│   ├── pdf.md
│   ├── xlsx.md
│   ├── pptx.md
│   ├── lark-connector.md
│   ├── skill-creator.md
│   ├── doc-to-table.md
│   └── README.md
│
└── plugins/                   # 可执行命令
    ├── custom/
    │   ├── pdf/commands/pdf.md
    │   ├── xlsx/commands/xlsx.md
    │   ├── pptx/commands/pptx.md
    │   ├── lark-connector/commands/lark.md
    │   └── skill-creator/commands/create-skill.md
    │
    └── custom-doc-to-table/
        └── commands/
            ├── doc-to-table.md
            └── table.md
```

## 🚀 使用方法

### 直接询问相关问题
当你问相关问题时，我会自动参考这些 skills：
```
如何提取 PDF 中的表格？
如何合并多个 Excel 文件？
```

### 使用可执行命令
通过斜杠命令直接执行功能：
```
/pdf extract-text document.pdf
/xlsx create data.xlsx --rows "A,B\n1,2"
/table report.pdf output.xlsx
```

## 📖 查看单个 Skill 文档

```bash
cat ~/.claude/skills/pdf.md        # 查看 PDF skill
cat ~/.claude/skills/xlsx.md       # 查看 Excel skill
```

## 🔧 添加新 Skills

1. 创建新的 skill 文档：`~/.claude/skills/my-skill.md`
2. 创建对应的命令：`~/.claude/plugins/custom/my-skill/commands/my-skill.md`
3. 使用 `/create-skill` 命令快速创建

---
*最后更新：2025-01-21*
