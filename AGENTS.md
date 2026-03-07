# 社会学读书笔记 - Agent 配置

## 项目简介

这是一个基于 GitHub Pages 的社会学知识库网站，支持：
- 🔍 关键词搜索与语义搜索
- 🕸️ 知识脑图可视化
- @ 关联跳转
- 📑 分类浏览
- 🐍 交互式 Python 代码运行
- 📊 参数滑块与交互式图表

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

### interactive-notes
**路径**: `.agents/skills/interactive-notes/SKILL.md`

在读书笔记中嵌入可运行的 Python 代码和交互式可视化组件。

功能：
- `python-runnable` 代码块 - 浏览器内运行 Python
- `@slider` 参数滑块 - 动态调整模型参数
- `@chart` 交互式图表 - Plotly.js 可视化
- `@table` 数据表格 - 可排序筛选

使用方式：
```markdown
## 博弈模型演示

@slider[effort_cost](label="努力成本", min=0.1, max=2.0, value=1.0)

```python-runnable
# 计算最优努力
c = {{slider.effort_cost}}
print(f"最优努力: {1/(2*c):.2f}")
```

@chart[bar](x=["A", "B"], y=[10, 20], title="结果对比")
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

### 交互式 Markdown 扩展语法

#### 1. 可运行 Python 代码
```markdown
```python-runnable {height=300}
import numpy as np
print("Hello from Python!")
```
```

#### 2. 参数滑块
```markdown
@slider[变量名](label="显示名称", min=0, max=100, value=50, step=1)
```

在代码中引用：`{{slider.变量名}}`

#### 3. 交互式图表
```markdown
@chart[line](x=[1,2,3], y=[4,5,6], title="折线图")
```

支持类型：`line`, `bar`, `scatter`, `histogram`, `box`, `network`

#### 4. 交互式表格
```markdown
@table[data.csv](sortable=true, filterable=true)
```

## 技术栈

- **构建**: Python + GitHub Actions
- **搜索**: Lunr.js (关键词) + 向量索引 (语义)
- **可视化**: D3.js (力导向图) + Plotly.js (交互图表)
- **Python 运行时**: PyScript (Pyodide/WebAssembly)
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

## 文件结构

```
.
├── docs/                    # Markdown 文档
│   ├── papers/             # 论文笔记
│   ├── books/              # 书籍笔记
│   ├── concepts/           # 概念梳理
│   └── template.md         # 文档模板
├── site/                   # 网站构建输出
│   ├── js/
│   │   ├── components/     # 交互组件
│   │   │   ├── CodeRunner.js
│   │   │   ├── ParamSlider.js
│   │   │   ├── ChartRenderer.js
│   │   │   └── DataTable.js
│   │   ├── parsers/
│   │   │   └── MarkdownInteractive.js
│   │   └── app.js
│   ├── css/
│   │   ├── style.css
│   │   └── interactive.css
│   ├── py/
│   │   ├── pyscript.toml   # Python 包配置
│   │   └── utils.py        # Python 工具函数
│   └── index.html
├── scripts/
│   └── build_index.py      # 构建脚本
├── .agents/skills/         # Agent 技能
│   ├── paper-reading/
│   └── interactive-notes/
└── .github/workflows/      # GitHub Actions
    └── pages.yml
```
