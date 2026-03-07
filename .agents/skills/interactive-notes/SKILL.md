# Interactive Notes Skill

## 描述

在社会学读书笔记中嵌入可运行的 Python 代码和交互式可视化组件，实现"可计算的文档"。

## 技术栈

- **PyScript** (Pyodide) - 浏览器内运行 Python
- **Plotly.js** - 交互式图表
- **CodeMirror 6** - 代码编辑器
- **Web Components** - 自定义交互组件

## Markdown 扩展语法规范

### 1. 可运行代码块

````markdown
```python-runnable
# Python 代码
print("Hello")
```
````

**渲染结果：**
- 带行号的代码编辑器
- 运行按钮
- 输出显示区域
- 重置按钮

**属性（可选）：**
```markdown
```python-runnable {height=300, packages="numpy,pandas"}
# 指定编辑器高度和额外包
```
````

### 2. 参数滑块

```markdown
@slider[变量名](label="显示名称", min=0, max=100, value=50, step=1)
```

**使用：**
- 在代码中通过 `{{slider.变量名}}` 引用
- 支持多个滑块
- 滑块值变化自动触发关联图表更新

### 3. 交互式图表

```markdown
@chart[type](config)
```

**类型：**
- `line` - 折线图
- `bar` - 柱状图
- `scatter` - 散点图
- `network` - 网络图
- `custom` - 自定义 Plotly 配置

### 4. 交互式表格

```markdown
@table[csv-data.csv](sortable=true, filterable=true)
```

### 5. 信息图组件

```markdown
@infographic[type="flow"]
- 节点1 → [详情]
- 节点2 → [详情]
@end
```

## 代码内引用语法

在 Python 代码块中引用滑块值：

```python
# 基础引用
x = {{slider.param1}}

# 带默认值
y = {{slider.param2 ?? 0.5}}

# 表达式
z = {{slider.param1 * 2}}
```

## 预装 Python 包

默认已安装：
- numpy
- pandas
- matplotlib
- scipy
- statsmodels
- scikit-learn
- networkx

## 文件结构

```
site/
├── js/
│   ├── components/
│   │   ├── CodeRunner.js      # 代码执行组件
│   │   ├── ParamSlider.js     # 参数滑块
│   │   ├── ChartRenderer.js   # 图表渲染
│   │   └── DataTable.js       # 数据表格
│   └── parsers/
│       └── MarkdownInteractive.js  # 语法解析
├── py/
│   ├── pyscript.toml          # 包配置
│   └── utils.py               # 工具函数
└── css/
    └── interactive.css        # 交互组件样式
```

## 使用流程

1. 在 Markdown 中使用扩展语法编写交互内容
2. 构建时解析扩展语法，生成 HTML + JS
3. 浏览器加载 PyScript 运行时
4. 用户与交互组件互动

## 注意事项

- PyScript 首次加载约 10-15MB
- 建议在笔记开头添加加载提示
- 复杂计算建议使用预计算结果
- 数据文件需放在可访问路径

## 示例

```markdown
## 博弈模型演示

@slider[effort_cost](label="努力成本", min=0.1, max=2.0, value=1.0, step=0.1)
@slider[supervision](label="监督强度", min=0, max=1, value=0.5, step=0.05)

```python-runnable
# 计算最优努力水平
c = {{slider.effort_cost}}
p = {{slider.supervision}}

# 代理人的最优反应
optimal_effort = p / (2 * c)
print(f"最优努力: {optimal_effort:.2f}")
```

@chart[bar](
  x=["低压力", "中压力", "高压力"],
  y=[0.2, 0.5, 0.8],
  title="不同压力下的共谋概率"
)
```
