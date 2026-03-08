# 公众号文章发布助手

将交互式HTML教学页面转换为适合微信公众号发布的长图+Markdown格式。

## 功能特性

- ✅ **移动端适配**：自动优化字体、边距、行距，适合小屏幕阅读
- ✅ **长图生成**：自动截图并分段，支持超长文章
- ✅ **图片压缩**：智能压缩至200KB以内，加速加载
- ✅ **图床上传**：自动上传到SM.MS免费图床（国内CDN）
- ✅ **Markdown生成**：生成带外链的公众号适配Markdown
- ✅ **免费方案**：完全零成本，无需服务器

## 快速开始

### 1. 安装依赖

```bash
cd scripts
pip install -r requirements-wechat.txt
playwright install chromium
```

### 2. 使用方法

#### 方式A：处理指定文章

```bash
python scripts/wechat_publisher.py --article ovb_interactive_demo
```

#### 方式B：处理最新修改的文章

```bash
python scripts/wechat_publisher.py --latest
```

#### 方式C：列出所有可用文章

```bash
python scripts/wechat_publisher.py --list
```

## 输出结构

```
wechat_posts/
└── 2026-03-08-ovb-tutorial/
    ├── article.md          # 公众号Markdown
    ├── mobile.html         # 移动端适配HTML
    ├── meta.json           # 文章元数据
    └── images/
        ├── section_1.jpg   # 长图分段
        └── section_2.jpg
```

## 发布步骤

1. 打开 `article.md` 文件
2. 复制全部内容到公众号编辑器
3. 图片已外链，自动加载
4. 微调排版后发布

## 成本说明

完全免费！SM.MS图床每天20张限制，GitHub Actions公开仓库免费。

## 详细文档

参见项目根目录 AGENTS.md
