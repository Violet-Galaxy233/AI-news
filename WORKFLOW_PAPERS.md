# 前沿论文周报生成工作流

## 触发条件

**仅在周一执行。** 执行前先判断今天是否为周一：
- 是周一 → 执行此工作流，生成本周论文文件
- 否则 → 跳过，无需生成

## 输出文件

路径：`papers/YYYY-MM-DD.json`（使用当天周一的日期，如 `papers/2026-04-07.json`）

---

## Step 1：确定本周时间范围

- 本周一日期 = 今天（触发日）
- 覆盖范围：上周二 00:00 UTC → 本周一 00:00 UTC（约 6 天）
- arxiv 提交时间以此为准，避免重复上周已发的论文

---

## Step 2：从多个来源抓取候选论文

### 来源 A：Hugging Face Daily Papers（首选）
- URL：`https://huggingface.co/papers`
- 用 WebFetch 获取，提取过去 5-6 天内的论文列表
- 这是社区筛选信号，优先参考

### 来源 B：arxiv CS.AI / CS.LG / CS.CL 新提交
- 用 WebSearch 检索：`arxiv cs.AI new papers week of [日期]`
- 或直接访问：`https://arxiv.org/list/cs.AI/recent`
- 重点关注：cs.AI、cs.LG、cs.CL、cs.CV（视觉语言）、cs.RO（具身智能）

### 来源 C：Papers With Code 趋势
- WebSearch：`papers with code trending this week`
- 补充工程影响力强的论文（有代码 = 落地价值高）

### 来源 D：社区讨论信号
- WebSearch：`arxiv paper AI [本周] site:news.ycombinator.com` 或 Twitter 热词
- 被广泛讨论的论文优先级提升

**目标候选池：20-30 篇，进入 Step 3 筛选**

---

## Step 3：筛选与评分

对每篇候选论文评估以下维度，满足越多优先级越高：

| 维度 | 说明 |
|------|------|
| 社区热度 | HF Daily Papers 收录、HN 讨论、Twitter 传播 |
| 机构背书 | 来自 Google DeepMind / OpenAI / Anthropic / Meta AI / MIT / CMU 等 |
| 有开源代码 | GitHub 链接、Papers With Code 收录 |
| 实验结果突出 | SOTA、大幅超越 baseline，有具体数字 |
| 应用覆盖广 | 影响多个下游任务或产品方向 |
| 方向新颖 | 开辟新研究方向，而非渐进改进 |

**最终选取 8-12 篇**（最少 5 篇，最多 15 篇）

**importance 分配原则：**
- `critical`（2-4 篇）：同时满足社区热度高 + 技术突破显著，或来自顶级机构的重磅工作
- `high`（3-5 篇）：方法有创新或结果强，但影响面稍窄
- `medium`（2-4 篇）：值得关注但不紧迫，领域内有参考价值

---

## Step 4：为每篇论文撰写内容

### 字段说明

```
id              arxiv 编号（如 "2504.01234"）
title           中文译名（简洁，≤20 字）
original_title  原英文标题（完整）
authors_org     第一作者机构（如 "Google DeepMind"，critical 专用）
arxiv_url       完整 arxiv 链接（https://arxiv.org/abs/XXXX.XXXXX）
importance      critical / high / medium
summary         中文总结（见长度规定）
impact          领域影响分析（仅 critical，见规定）
keywords        关键词列表（2-4 个中文词）
```

### 内容长度规定（以"词"计：汉字每个=1，英文单词=1，数字=1）

| importance | summary | impact |
|------------|---------|--------|
| critical | 60-90 词，涵盖：问题→方法→效果数据→意义 | 40-60 词，说明对领域的影响 |
| high | 35-55 词，涵盖：方法创新点→效果数据 | 不填 |
| medium | 20-35 词，一句话说清核心贡献 | 不填 |

### 写作规范

- **全程中文**，专有名词保留英文（如 GPT-4、ViT、RLHF）
- **必须包含具体数字**：提升百分比、参数量、测试集分数等；若论文无具体数字，注明"具体指标未公开"
- **禁止模糊表述**：不写"大幅提升""显著改善"，改为"在 MMLU 上提升 4.2%"
- **禁止术语直译**：
  - benchmark → 评测 / 测试集（如"MMLU 评测"）
  - token → 字符 / 处理量
  - LLM / VLM → 大语言模型 / 视觉语言模型
  - fine-tuning → 微调
  - context window → 上下文长度
- **中英文之间加空格**（如"在 ImageNet 上"而非"在ImageNet上"）

---

## Step 5：质量检查

逐篇确认：
- [ ] arxiv_url 格式正确（`https://arxiv.org/abs/` 开头）
- [ ] summary 含具体数字或注明"未公开"
- [ ] critical 论文的 impact 字段已填写
- [ ] 无禁用术语
- [ ] 论文来自本周（上周二至本周一），非旧文
- [ ] 总数在 5-15 篇之间，importance 分布合理

---

## Step 6：生成 JSON 文件

文件路径：`papers/YYYY-MM-DD.json`（周一日期）

```json
{
  "metadata": {
    "week": "YYYY-WXX",
    "date": "YYYY-MM-DD",
    "date_range": "YYYY-MM-DD 至 YYYY-MM-DD",
    "total": 10,
    "sources": ["Hugging Face Daily Papers", "arxiv cs.AI", "Papers With Code"]
  },
  "papers": [
    {
      "id": "2504.01234",
      "title": "中文译名",
      "original_title": "Full English Title",
      "authors_org": "Google DeepMind",
      "arxiv_url": "https://arxiv.org/abs/2504.01234",
      "importance": "critical",
      "summary": "中文总结内容……",
      "impact": "对领域的影响分析……",
      "keywords": ["强化学习", "视觉语言模型"]
    },
    {
      "id": "2504.05678",
      "title": "中文译名",
      "original_title": "Full English Title",
      "authors_org": "",
      "arxiv_url": "https://arxiv.org/abs/2504.05678",
      "importance": "high",
      "summary": "中文总结……",
      "impact": "",
      "keywords": ["推理", "训练效率"]
    }
  ]
}
```

**注意：**
- `authors_org` 在 `high`/`medium` 条目可为空字符串
- `impact` 在 `high`/`medium` 条目为空字符串
- JSON 内容中的引号使用「」而非 ASCII `"`（避免解析错误）
- week 格式：ISO 周次，如 `"2026-W15"`

---

## 快速检查清单

```
[ ] 今天是周一 → 继续；否则停止
[ ] 候选池 ≥ 20 篇
[ ] 最终选取 5-15 篇
[ ] 每篇 summary 含数字或注明未公开
[ ] critical 均有 impact
[ ] arxiv_url 全部有效
[ ] JSON 无语法错误（引号用「」）
[ ] 文件保存至 papers/YYYY-MM-DD.json
```
