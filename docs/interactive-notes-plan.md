# 交互式读书笔记功能规划

## 🎯 愿景

让静态的读书笔记变成"可计算的文档"(Executable Notes)，读者可以：
- 运行代码复现论文的数据分析
- 调节参数实时观察效应变化
- 与信息图表交互探索数据

## 🏗️ 技术架构

### 核心组件

```
┌─────────────────────────────────────────────────────┐
│                  交互式读书笔记                        │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  PyScript    │  │  Observable  │  │ Custom   │  │
│  │  (可运行代码) │  │  (响应式图表) │  │ 组件    │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
├─────────────────────────────────────────────────────┤
│              Markdown 扩展语法解析层                  │
├─────────────────────────────────────────────────────┤
│              静态站点 (GitHub Pages)                  │
└─────────────────────────────────────────────────────┘
```

### 技术选型

| 组件 | 技术 | 用途 | 优缺点 |
|------|------|------|--------|
| 可运行代码 | PyScript (Pyodide) | 浏览器内执行 Python | ✅ 原生Python ❌ 加载慢(10MB+) |
| 交互图表 | Plotly.js + D3 | 动态可视化 | ✅ 功能丰富 ❌ 需JS |
| 响应式数据 | Observable Runtime | 数据流响应 | ✅ 轻量快速 ❌ 学习曲线 |
| 信息图 | 自定义 Web Components | 专用交互组件 | ✅ 高度定制 ❌ 开发成本 |

## 📝 Markdown 扩展语法

### 1. 可运行代码块

````markdown
```python-runnable
# 计算项目制下的资金分配效率
import numpy as np
import pandas as pd

# 参数设置
total_funds = 1000  # 总资金
num_projects = 20   # 项目数量

# 模拟分配
distribution = np.random.pareto(1.5, num_projects)
distribution = distribution / distribution.sum() * total_funds

# 计算基尼系数
def gini(x):
    x = np.array(x)
    x = np.sort(x)
    n = len(x)
    cumsum = np.cumsum(x)
    return (2 * np.sum((np.arange(1, n+1) * x))) / (n * cumsum[-1]) - (n+1)/n

print(f"资金分配的基尼系数: {gini(distribution):.3f}")
print(f"最高占比: {distribution.max()/total_funds:.1%}")
print(f"最低占比: {distribution.min()/total_funds:.1%}")

# 可视化
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))
plt.bar(range(num_projects), sorted(distribution, reverse=True))
plt.xlabel('项目排名')
plt.ylabel('资金分配 (万元)')
plt.title('项目资金分配不平等分布')
plt.show()
```
````

**渲染效果：**
- 带代码编辑器的代码块
- "运行" 按钮
- 下方显示输出结果
- 可重置为原始代码

### 2. 参数滑块组件

```markdown
@slider[参数名](
  label="信息不对称程度",
  min=0, max=1, step=0.1, value=0.5,
  description="上级对下级执行情况的了解程度"
)

@formula[
  共谋概率 = 1 / (1 + exp(-k * (压力 - 监督强度 * (1 - 信息不对称))))
]

@chart[type="line"](
  x="压力水平",
  y="共谋概率",
  data="随滑块值动态计算"
)
```

**效果：** 拖动滑块，实时更新公式计算结果和图表

### 3. 交互式信息图

```markdown
@infographic[type="flow"](
  title="行政发包制的运行机制"
)
- 中央设定目标 → [点击展开: 目标如何分解到地方]
- 逐级发包任务 → [点击展开: 发包过程中的信息不对称]
- 地方执行落实 → [点击展开: 执行中的策略性行为]
- 考核验收 ← [可展开不同考核方式的效果]
@end
```

**效果：** 可点击每个节点展开详细解释

### 4. 数据表格（交互式）

```markdown
@table[interactive](
  source="data/sample.csv",
  columns=["变量", "均值", "标准差", "最小值", "最大值"],
  sortable=true,
  filterable=true
)
```

**效果：** 可排序、筛选、导出

### 5. 对比视图

```markdown
@compare[
  left="理性选择模型",
  right="制度主义模型"
]
- 核心假设 :: 行动者追求效用最大化 :: 行动者受制度约束
- 分析单位 :: 个体 :: 组织/制度
- 预测能力 :: 短期行为 :: 长期演化
@end
```

**效果：** 左右对比两列，便于理解理论差异

## 🎨 论文特定模板

### 定量分析论文模板

```markdown
## 数据分析复现

### 描述性统计
@table[desc-stats](variables=["因变量", "核心自变量", "控制变量"])

### 回归结果
@regression-table[
  models=["模型1: 基准", "模型2: 加入控制变量", "模型3: 稳健性检验"],
  interactive=true  # 可点击系数查看解释
]

### 敏感性分析
@slider[样本选择](剔除异常值比例: 0-20%)
@chart[coef-plot](显示系数变化)
```

### 博弈论模型演示

```markdown
## 委托-代理博弈模型

### 参数设置
@slider[努力成本系数](c: 0.1-2.0)
@slider[监督精度](p: 0.5-1.0)
@slider[激励强度](w: 0-100)

### 均衡计算
```python-runnable
# 根据滑块值计算均衡
c = {{slider.c}}  # 从滑块获取值
p = {{slider.p}}
w = {{slider.w}}

# 代理人的最优努力
optimal_effort = w * p / (2 * c)
print(f"代理人最优努力水平: {optimal_effort:.2f}")

# 委托人的期望收益
principal_payoff = 10 * optimal_effort - w
print(f"委托人期望收益: {principal_payoff:.2f}")
```

### 可视化
@chart[nash-equilibrium](显示均衡点的相图)
```

## 🔧 实现路线图

### Phase 1: 基础框架 (1-2周)
- [ ] 集成 PyScript 到网站
- [ ] 实现 `python-runnable` 代码块组件
- [ ] 创建代码编辑器 UI (CodeMirror)
- [ ] 基础输出显示（文本/图表）

### Phase 2: 交互组件库 (2-3周)
- [ ] 参数滑块组件 `@slider`
- [ ] 交互式图表封装 `@chart`
- [ ] 可展开信息卡 `@infocard`
- [ ] 对比视图 `@compare`

### Phase 3: 数据组件 (2周)
- [ ] CSV 数据加载器
- [ ] 交互式表格 `@table`
- [ ] 数据筛选器
- [ ] 简单统计计算

### Phase 4: 论文专用 (持续)
- [ ] 回归结果展示模板
- [ ] 因果图可视化
- [ ] 博弈论模型交互器
- [ ] 样本选择演示

## 📂 文件结构

```
site/
├── index.html
├── css/
├── js/
│   ├── app.js              # 主应用
│   ├── components/         # 交互组件
│   │   ├── CodeRunner.js   # Python 代码执行
│   │   ├── ParamSlider.js  # 参数滑块
│   │   ├── DataTable.js    # 交互表格
│   │   └── InfoGraphic.js  # 信息图
│   └── parsers/
│       └── MarkdownExt.js  # 扩展语法解析
├── py/                     # Python 支持
│   ├── pyscript.json       # 包配置
│   └── startup.py          # 初始化代码
└── templates/              # 论文分析模板
    ├── quantitative.md
    ├── qualitative.md
    └── game-theory.md
```

## 💡 使用示例场景

### 场景1：复现论文回归
```markdown
周雪光 (2008) 发现考核压力与共谋行为呈正相关。
下面复现这一结果：

```python-runnable
# 加载模拟数据
import pandas as pd
df = pd.read_csv('data/gov_data.csv')

# 运行回归
import statsmodels.formula.api as smf
model = smf.ols('conspiracy ~ pressure + gdp_growth + region', data=df).fit()
print(model.summary().tables[1])
```

**交互探索：** 调节 @slider[样本范围](年份: 2000-2010)，
观察系数如何变化。
```

### 场景2：理论模型演示
```markdown
@infographic[type="mechanism"](
  title="项目制的意外后果"
)
1. 专项资金下达 @param[金额](100-1000万)
2. 地方配套压力 @param[配套比例](0-50%)
3. 项目包装策略 [展开: 具体策略类型]
4. 短期行为激励 [展开: 长期发展受损]
@end

实时计算：
```python-runnable
funds = {{param.金额}}
match_ratio = {{param.配套比例}} / 100
local_burden = funds * match_ratio

print(f"地方配套压力: {local_burden:.0f}万元")
print(f"包装项目概率: {min(local_burden/100, 0.9):.1%}")
```
```

## ⚠️ 技术约束

1. **性能限制**
   - PyScript 首次加载 ~15MB
   - 复杂计算可能卡顿
   - 建议数据集 < 10MB

2. **浏览器兼容**
   - 需要 WebAssembly 支持
   - 现代浏览器 (Chrome/Firefox/Edge)

3. **安全限制**
   - 无法访问本地文件系统
   - 网络请求受 CORS 限制
   - 无法安装任意 Python 包

## 🚀 下一步行动

1. **本周内** - 我可以帮你实现 Phase 1 的基础框架
2. **收集反馈** - 你希望优先实现哪个论文的交互示例？
3. **数据准备** - 是否有特定的数据集想要集成？

---

*这个方案将让你的读书笔记从"可读"升级为"可玩可探索"。* 🎮📊
