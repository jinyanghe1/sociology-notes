# 社会学读书笔记 - Agent 配置

## 项目简介

这是一个基于 GitHub Pages 的社会学知识库网站，支持：
- 🔍 关键词搜索与语义搜索
- 🕸️ 知识脑图可视化
- @ 关联跳转
- 📑 分类浏览

## 可用技能

### paper-reading
**路径**: `.agents/skills/paper-reading/SKILL.md`

当需要深入阅读、讨论一篇社会学/社会科学论文时使用此技能。

角色设定：以社科基金资深审稿人的视角，系统性地分析论文的社会价值、边际贡献和逻辑严谨性。

使用方式：
```
用户：请帮我深入阅读这篇论文《基层政府间的共谋现象》
→ 启动 paper-reading skill
→ 进行多轮深度对话
→ 生成凝练的读书笔记
```

## 文档规范

### 文件命名
- 论文笔记: `作者_年份_标题关键词.md`
- 书籍笔记: `作者_书名.md`
- 概念笔记: `概念名.md`

### 关联语法
使用 `@` 创建文章间关联：
```markdown
本文讨论了 @周雪光 的 @行政发包制 理论，
与 @渠敬东 的 @项目制 形成对话。
```

### Frontmatter 模板
```yaml
---
title: "论文/书籍标题"
authors: ["作者1", "作者2"]
year: 2023
tags: ["标签1", "标签2", "标签3"]
venue: "期刊名"  # 论文可选
category: "papers"  # papers/books/concepts
summary: "一句话摘要"
---
```

## 技术栈

- **构建**: Python + GitHub Actions
- **搜索**: Lunr.js (关键词) + 语义匹配
- **可视化**: D3.js (力导向图)
- **部署**: GitHub Pages

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 构建索引
python scripts/build_index.py

# 本地预览
python -m http.server 8000 --directory site/
```

## 部署

推送至 main 分支后，GitHub Actions 自动构建并部署到 Pages。
