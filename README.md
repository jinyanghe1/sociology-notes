# 社会学读书笔记 📚

一个支持**脑图关联**和**语义搜索**的社会学知识库网站。

🔗 **在线访问**: https://jinyanghe1.github.io/sociology-notes/

## ✨ 功能特性

### 1. 知识浏览
- 📑 按专题/标签分类浏览笔记
- 🔍 全文关键词搜索
- 📱 响应式设计，支持移动端阅读

### 2. 脑图关联
- 使用 `@作者名` 或 `@关键词` 在文章中关联其他内容
- 可视化关系图谱展示知识网络
- 支持内联跳转，快速导航相关内容

### 3. 语义搜索
- 基于向量相似度的智能搜索
- 搜索"基层治理"可匹配相关概念（如"社区自治"、"行政下沉"等）
- 无需精确关键词即可找到相关内容

## 📁 目录结构

```
.
├── docs/                 # Markdown 文档
│   ├── papers/           # 论文读书笔记
│   ├── books/            # 书籍读书笔记
│   └── concepts/         # 概念/理论整理
├── site/                 # 网站构建输出
├── scripts/              # 构建和索引脚本
└── data/                 # 索引数据、关系图谱数据
```

## 🚀 本地开发

```bash
# 克隆仓库
git clone https://github.com/jinyanghe1/sociology-notes.git
cd sociology-notes

# 安装依赖（构建脚本需要）
pip install -r requirements.txt

# 构建索引并启动本地服务器
python scripts/build_index.py
python -m http.server 8000 --directory site/
```

访问 http://localhost:8000 查看效果。

## 📝 写作规范

### 文件命名
- 论文笔记: `作者_年份_标题关键词.md`
- 书籍笔记: `作者_书名.md`
- 概念笔记: `概念名.md`

### 关联语法
在文档中使用 `@` 语法创建关联：

```markdown
本文讨论了 @周雪光 的行政发包制理论，
与 @渠敬东 的项目制有相似之处。

相关概念: @行政发包制 @项目制 @基层治理
```

### Frontmatter 格式

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

## 🔧 技术栈

- **构建**: Python + GitHub Actions
- **搜索**: Lunr.js (关键词) + 向量索引 (语义)
- **可视化**: D3.js (力导向图)
- **部署**: GitHub Pages

## 📄 License

MIT License
