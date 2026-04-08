# 🌅 AI 新闻简报生成系统

每日 AI 新闻的自动生成和展示工具。使用 Claude Code 抓取、分析新闻，生成精美的卡片式展示页面。

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 生成今日新闻

直接对 Claude Code 说：

```
按照 WORKFLOW.md 生成今天（2025-10-15）的 AI 新闻简报
```

Claude Code 会自动完成抓取、分析、去重、生成 JSON 的全部流程。

### 3. 查看新闻

```bash
npm run dev
```

浏览器访问 `http://localhost:5173/` 查看生成的新闻卡片。

## 📁 项目结构

```
aidaily/
├── WORKFLOW.md          # 🎯 核心配置（新闻源、评估标准、执行指令）
├── data/                # 数据目录
│   ├── raw/            # 原始抓取数据（.txt）
│   └── *.json          # 生成的新闻数据
├── src/                # Vue 3 前端代码
│   ├── components/
│   │   ├── NewsViewer.vue
│   │   └── NewsCard.vue
│   └── main.js
└── README.md           # 本文件
```

## 🎯 工作流程

1. **告诉 Claude Code**："按照 WORKFLOW.md 生成今天的新闻"
2. **Claude Code 自动**：
   - 抓取各大 AI 新闻源
   - 对比历史数据去重
   - 分析评估重要性
   - 生成结构化 JSON
3. **你运行前端**：`npm run dev` 查看结果

## 📖 详细配置

所有配置都在 `WORKFLOW.md` 中：
- 新闻源列表
- 评估标准（critical/high/medium）
- JSON 格式规范
- 执行指令模板

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可

MIT License
