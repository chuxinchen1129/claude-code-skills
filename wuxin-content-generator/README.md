# Wuxin Zenoasis Content Project

> 小红书睡眠科普图文生成器

## 项目概述

这是一个Python项目，用于生成小红书平台的睡眠科普图文内容。通过智谱AI API，结合品牌资产库和科普知识库，自动化生成高质量的小红书笔记内容。

## 项目结构

```
Wuxin_Zenoasis_Content_Project/
├── 00_Strategy_Planning/         # marketing_calendar和策略规划
├── 01_Brand_Assets_Library/      # 品牌资产库
│   └── 05_Sleep_Science_Wiki/    # 睡眠科普知识库
├── src/                          # Python源代码
├── output/                       # 生成结果输出
├── requirements.txt              # 依赖包列表
└── README.md                     # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件或配置文件，添加智谱AI API密钥：

```bash
# .env 文件示例
ZHIPUAI_API_KEY=your_api_key_here
```

### 3. 运行示例

```bash
cd src
python main.py
```

## 核心功能

- **内容规划**：基于marketing_calendar自动规划内容主题
- **知识检索**：从睡眠科普知识库检索相关内容
- **内容生成**：使用智谱AI生成小红书笔记
- **格式输出**：生成适合小红书发布的格式化内容

## 开发进度

- [x] 项目初始化
- [ ] 配置文件设计
- [ ] 内容规划模块
- [ ] 知识库检索模块
- [ ] 内容生成模块
- [ ] 输出格式化模块

## 下一步建议

1. **配置文件设计**：创建 `config.yaml` 文件，定义API密钥、模板路径等配置
2. **数据准备**：准备marketing_calendar和睡眠科普知识库内容
3. **模块开发**：开发各个功能模块
4. **测试验证**：进行端到端测试

## 许可证

© 2026 Wuxin Zenoasis. All rights reserved.
