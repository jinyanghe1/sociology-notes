#!/usr/bin/env python3
"""
WeChat公众号文章生成器
将HTML交互式教学页面转换为适合公众号发布的长图+Markdown

Usage:
    python scripts/wechat_publisher.py --article ovb_interactive_demo
    python scripts/wechat_publisher.py --latest
    python scripts/wechat_publisher.py --all
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image, ImageDraw, ImageFont

# 配置
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
SITE_DIR = ROOT_DIR / "site"
ARTICLES_DIR = SITE_DIR / "articles"
WECHAT_POSTS_DIR = ROOT_DIR / "wechat_posts"
TEMPLATE_DIR = WECHAT_POSTS_DIR / "templates"

# SM.MS 图床 API（免费版，无需认证，每天20张限制）
SMMS_UPLOAD_URL = "https://sm.ms/api/v2/upload"
SMMS_DELETE_URL = "https://sm.ms/api/v2/delete"

# 截图配置
SCREENSHOT_WIDTH = 1080  # 公众号最佳宽度
SCREENSHOT_MAX_HEIGHT = 8000  # 超过则分段
SCREENSHOT_QUALITY = 85


def log(message: str, level: str = "info"):
    """打印日志"""
    colors = {
        "info": "\033[94m",      # 蓝色
        "success": "\033[92m",   # 绿色
        "warning": "\033[93m",   # 黄色
        "error": "\033[91m",     # 红色
        "reset": "\033[0m"
    }
    color = colors.get(level, colors["info"])
    print(f"{color}[{level.upper()}]{colors['reset']} {message}")


class WeChatPublisher:
    """公众号文章发布器"""
    
    def __init__(self):
        self.articles_dir = ARTICLES_DIR
        self.output_dir = WECHAT_POSTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "templates").mkdir(exist_ok=True)
        
    def find_article_html(self, article_name: str) -> Optional[Path]:
        """查找文章HTML文件"""
        # 尝试多种命名方式
        candidates = [
            self.articles_dir / f"{article_name}.html",
            self.articles_dir / f"{article_name}_interactive_demo.html",
        ]
        
        # 模糊匹配
        for candidate in self.articles_dir.glob("*.html"):
            if article_name.lower() in candidate.stem.lower():
                candidates.append(candidate)
        
        for path in candidates:
            if path.exists():
                return path
        
        return None
    
    def extract_article_info(self, html_path: Path) -> dict:
        """从HTML中提取文章信息"""
        content = html_path.read_text(encoding='utf-8')
        
        # 提取标题
        title_match = re.search(r'<title>(.*?)\|', content)
        title = title_match.group(1).strip() if title_match else html_path.stem
        
        # 提取摘要（从第一个p标签）
        summary_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
        summary = summary_match.group(1)[:200] if summary_match else ""
        summary = re.sub(r'<[^>]+>', '', summary)  # 去除HTML标签
        
        return {
            "title": title,
            "filename": html_path.stem,
            "summary": summary,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "html_path": str(html_path)
        }
    
    def generate_mobile_html(self, html_path: Path, output_path: Path) -> Path:
        """生成移动端适配的HTML"""
        log(f"生成移动端适配HTML: {html_path.name}")
        
        original_content = html_path.read_text(encoding='utf-8')
        
        # 移动端适配模板
        mobile_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <style>
        /* 基础重置 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #fff;
            font-size: 18px;
            width: {width}px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* 标题样式 */
        h1 {{
            font-size: 40px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 30px 0 20px;
            line-height: 1.4;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
        }}
        
        h2 {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin: 40px 0 20px;
            padding-left: 15px;
            border-left: 5px solid #007bff;
        }}
        
        h3 {{
            font-size: 26px;
            font-weight: bold;
            color: #34495e;
            margin: 30px 0 15px;
        }}
        
        h4 {{
            font-size: 22px;
            font-weight: bold;
            color: #555;
            margin: 20px 0 10px;
        }}
        
        /* 段落 */
        p {{
            margin: 20px 0;
            text-align: justify;
            font-size: 20px;
            line-height: 1.9;
        }}
        
        /* 强调框 */
        .concept-box, .formula-box, .warning-box, .step-box, .result-box {{
            margin: 25px 0;
            padding: 25px;
            border-radius: 12px;
            font-size: 19px;
        }}
        
        .concept-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 6px solid #2196f3;
        }}
        
        .formula-box {{
            background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
            border-left: 6px solid #ffc107;
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border-left: 6px solid #f44336;
        }}
        
        .step-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left: 6px solid #4caf50;
        }}
        
        .result-box {{
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-left: 6px solid #9c27b0;
        }}
        
        /* 步骤编号 */
        .step-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            font-weight: bold;
            font-size: 20px;
            margin-right: 15px;
            vertical-align: middle;
        }}
        
        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border: 1px solid #e0e0e0;
        }}
        
        th {{
            background: #007bff;
            color: white;
            font-weight: bold;
            font-size: 19px;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        /* 代码块 */
        pre, code {{
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
            background: #f4f4f4;
            border-radius: 6px;
        }}
        
        pre {{
            padding: 20px;
            overflow-x: auto;
            font-size: 16px;
            line-height: 1.6;
            margin: 20px 0;
            border-left: 4px solid #007bff;
        }}
        
        code {{
            padding: 3px 8px;
            font-size: 17px;
            color: #e83e8c;
        }}
        
        /* 列表 */
        ul, ol {{
            margin: 20px 0;
            padding-left: 35px;
            font-size: 19px;
        }}
        
        li {{
            margin: 12px 0;
            line-height: 1.8;
        }}
        
        /* 图表容器 */
        .chart-container {{
            background: white;
            padding: 20px;
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .chart-container h3 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 24px;
        }}
        
        /* 控制面板 */
        .control-panel {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
            border: 2px solid #dee2e6;
        }}
        
        /* 公式 */
        .formula-table {{
            font-size: 17px;
        }}
        
        /* 高亮 */
        .highlight {{
            background: linear-gradient(120deg, #fff59d 0%, #fff59d 100%);
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        /* 引用块 */
        blockquote {{
            margin: 25px 0;
            padding: 20px 25px;
            background: #f8f9fa;
            border-left: 5px solid #007bff;
            font-style: italic;
            font-size: 19px;
            border-radius: 0 8px 8px 0;
        }}
        
        /* 隐藏原网页元素 */
        .article-header, .breadcrumb, .demo-container > p:first-of-type, 
        nav, header, footer, script {{
            display: none !important;
        }}
        
        /* 显示主要内容 */
        .demo-container {{
            display: block !important;
            max-width: 100% !important;
            padding: 0 !important;
        }}
        
        /* 滑块样式 */
        input[type="range"] {{
            width: 100%;
            height: 40px;
            margin: 15px 0;
        }}
        
        button {{
            padding: 15px 30px;
            font-size: 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            margin: 10px 5px;
        }}
        
        /* 响应式图片 */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
        }}
        
        /* 分割线 */
        hr {{
            margin: 40px 0;
            border: none;
            height: 3px;
            background: linear-gradient(90deg, transparent, #007bff, transparent);
        }}
    </style>
</head>
<body>
    <div class="wechat-content">
        {content}
    </div>
    
    <!-- 隐藏原交互元素，添加提示 -->
    <div style="background: #fff3cd; padding: 20px; margin: 30px 0; border-radius: 8px; text-align: center;">
        <p style="font-size: 20px; margin: 0;">
            🎯 <strong>交互式版本</strong>：访问 
            <a href="{original_url}" style="color: #007bff; text-decoration: underline;">
                在线版本
            </a> 
            体验可调节参数的交互演示
        </p>
    </div>
</body>
</html>'''
        
        # 清理原HTML内容
        # 移除script标签（避免公众号不支持JS）
        content_cleaned = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', original_content, flags=re.IGNORECASE)
        
        # 移除导航等不必要元素
        content_cleaned = re.sub(r'<nav[^>]*>[\s\S]*?</nav>', '', content_cleaned, flags=re.IGNORECASE)
        content_cleaned = re.sub(r'<header[^>]*>[\s\S]*?</header>', '', content_cleaned, flags=re.IGNORECASE)
        content_cleaned = re.sub(r'<footer[^>]*>[\s\S]*?</footer>', '', content_cleaned, flags=re.IGNORECASE)
        
        # 提取body内容
        body_match = re.search(r'<body[^>]*>([\s\S]*)</body>', content_cleaned, re.IGNORECASE)
        body_content = body_match.group(1) if body_match else content_cleaned
        
        # 生成移动端HTML
        mobile_html = mobile_template.format(
            title=self.extract_article_info(html_path)["title"],
            width=SCREENSHOT_WIDTH,
            content=body_content,
            original_url=f"https://jinyanghe1.github.io/sociology-notes/articles/{html_path.name}"
        )
        
        output_path.write_text(mobile_html, encoding='utf-8')
        log(f"移动端HTML已生成: {output_path}", "success")
        return output_path
    
    async def capture_screenshot(self, html_path: Path, output_dir: Path) -> List[Path]:
        """使用Playwright截图"""
        log(f"开始截图: {html_path.name}")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            log("Playwright未安装，正在安装...", "warning")
            os.system("pip install playwright")
            os.system("playwright install chromium")
            from playwright.async_api import async_playwright
        
        screenshot_paths = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 设置视口
            await page.set_viewport_size({
                "width": SCREENSHOT_WIDTH,
                "height": 1920
            })
            
            # 加载HTML
            await page.goto(f"file://{html_path.absolute()}", wait_until="networkidle")
            
            # 等待字体和样式加载
            await page.wait_for_timeout(2000)
            
            # 获取页面高度
            page_height = await page.evaluate("document.body.scrollHeight")
            log(f"页面高度: {page_height}px")
            
            # 如果页面太高，分段截图
            if page_height > SCREENSHOT_MAX_HEIGHT:
                log(f"页面过高，将分段截图")
                segments = await self._split_screenshot(page, output_dir, page_height)
                screenshot_paths.extend(segments)
            else:
                # 单张截图
                screenshot_path = output_dir / "article_full.jpg"
                await page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                    type="jpeg",
                    quality=SCREENSHOT_QUALITY
                )
                screenshot_paths.append(screenshot_path)
                log(f"截图已保存: {screenshot_path}", "success")
            
            await browser.close()
        
        return screenshot_paths
    
    async def _split_screenshot(self, page, output_dir: Path, total_height: int) -> List[Path]:
        """分段截图 - 先全页面截图，再用Pillow裁剪"""
        paths = []
        segment_height = SCREENSHOT_MAX_HEIGHT
        num_segments = (total_height + segment_height - 1) // segment_height
        
        # 先全页面截图到临时文件
        temp_full_path = output_dir / "_temp_full.png"
        await page.screenshot(
            path=str(temp_full_path),
            full_page=True
        )
        
        # 用Pillow打开并裁剪
        full_img = Image.open(temp_full_path)
        
        for i in range(num_segments):
            start_y = i * segment_height
            end_y = min((i + 1) * segment_height, total_height)
            actual_height = end_y - start_y
            
            screenshot_path = output_dir / f"section_{i+1}.jpg"
            
            # 裁剪
            cropped = full_img.crop((0, start_y, SCREENSHOT_WIDTH, end_y))
            cropped.save(screenshot_path, "JPEG", quality=SCREENSHOT_QUALITY)
            
            paths.append(screenshot_path)
            log(f"分段截图 {i+1}/{num_segments}: {screenshot_path}", "success")
        
        # 删除临时文件
        temp_full_path.unlink()
        
        return paths
    
    def compress_image(self, image_path: Path, max_size_kb: int = 200) -> Path:
        """压缩图片"""
        img = Image.open(image_path)
        
        # 如果图片太大，逐步降低质量
        quality = SCREENSHOT_QUALITY
        while True:
            img.save(image_path, "JPEG", quality=quality, optimize=True)
            size_kb = image_path.stat().st_size / 1024
            
            if size_kb <= max_size_kb or quality <= 50:
                break
            
            quality -= 5
        
        log(f"图片已压缩: {image_path.name} ({size_kb:.1f}KB)", "success")
        return image_path
    
    def upload_to_smms(self, image_path: Path) -> Optional[str]:
        """上传到SM.MS图床"""
        log(f"上传图片: {image_path.name}")
        
        try:
            with open(image_path, "rb") as f:
                files = {"smfile": f}
                response = requests.post(
                    SMMS_UPLOAD_URL,
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    url = data["data"]["url"]
                    log(f"上传成功: {url}", "success")
                    return url
                else:
                    # 可能达到上传限制
                    log(f"上传失败: {data.get('message')}", "warning")
                    return None
            else:
                log(f"上传失败: HTTP {response.status_code}", "error")
                return None
                
        except Exception as e:
            log(f"上传异常: {e}", "error")
            return None
    
    def generate_markdown(self, article_info: dict, image_urls: List[str], output_path: Path):
        """生成公众号Markdown"""
        
        # 生成封面图（第一张图）
        cover_url = image_urls[0] if image_urls else ""
        
        # 构建文章内容
        sections = []
        for i, url in enumerate(image_urls):
            sections.append(f"\n![文章内容 {i+1}]({url})\n")
        
        markdown_content = f'''---
title: "{article_info['title']}"
subtitle: "{article_info['summary'][:100]}..."
cover: "{cover_url}"
date: "{article_info['created']}"
original_url: "https://jinyanghe1.github.io/sociology-notes/articles/{article_info['filename']}.html"
---

![封面图]({cover_url})

> 📚 **{article_info['summary'][:150]}...**

{''.join(sections)}

---

🎯 **阅读完整交互版**：点击"阅读原文"体验可调节参数的在线版本

📮 **关注本公众号**，获取更多社会学研究方法干货

💻 **GitHub 仓库**：[社会学读书笔记](https://github.com/jinyanghe1/sociology-notes)

---

*本文为自动生成，原始内容基于交互式教学网页*
'''
        
        output_path.write_text(markdown_content, encoding='utf-8')
        log(f"Markdown已生成: {output_path}", "success")
    
    async def process_article(self, article_name: str) -> Optional[Path]:
        """处理单篇文章"""
        log(f"开始处理文章: {article_name}")
        
        # 1. 查找HTML文件
        html_path = self.find_article_html(article_name)
        if not html_path:
            log(f"未找到文章: {article_name}", "error")
            return None
        
        # 2. 提取文章信息
        article_info = self.extract_article_info(html_path)
        log(f"文章标题: {article_info['title']}")
        
        # 3. 创建输出目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\u4e00-\u9fff]+', '-', article_info['title'])[:30]
        output_dir = self.output_dir / f"{date_str}-{safe_title}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存元数据
        (output_dir / "meta.json").write_text(
            json.dumps(article_info, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # 4. 生成移动端HTML
        mobile_html_path = output_dir / "mobile.html"
        self.generate_mobile_html(html_path, mobile_html_path)
        
        # 5. 截图
        screenshot_paths = await self.capture_screenshot(mobile_html_path, output_dir)
        
        # 6. 压缩图片
        compressed_paths = [self.compress_image(p) for p in screenshot_paths]
        
        # 7. 上传图床（可选，如果失败则使用本地路径）
        image_urls = []
        for img_path in compressed_paths:
            url = self.upload_to_smms(img_path)
            if url:
                image_urls.append(url)
            else:
                # 如果上传失败，使用相对路径
                log("图床上传失败，将使用本地图片路径", "warning")
                image_urls.append(f"./images/{img_path.name}")
        
        # 8. 生成Markdown
        markdown_path = output_dir / "article.md"
        self.generate_markdown(article_info, image_urls, markdown_path)
        
        # 9. 创建图片目录
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        for img_path in compressed_paths:
            import shutil
            shutil.copy(img_path, images_dir / img_path.name)
        
        log(f"处理完成！输出目录: {output_dir}", "success")
        log(f"Markdown文件: {markdown_path}", "info")
        
        return output_dir
    
    def list_available_articles(self) -> List[Path]:
        """列出可用文章"""
        if not self.articles_dir.exists():
            return []
        return list(self.articles_dir.glob("*.html"))


def main():
    parser = argparse.ArgumentParser(
        description="将HTML教学文章转换为公众号格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python wechat_publisher.py --article ovb_interactive_demo
    python wechat_publisher.py --latest
    python wechat_publisher.py --list
        """
    )
    
    parser.add_argument(
        "--article", "-a",
        help="指定文章名称（如: ovb_interactive_demo）"
    )
    parser.add_argument(
        "--latest", "-l",
        action="store_true",
        help="处理最新的文章"
    )
    parser.add_argument(
        "--list", "-ls",
        action="store_true",
        help="列出所有可用文章"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="处理所有文章"
    )
    
    args = parser.parse_args()
    
    publisher = WeChatPublisher()
    
    if args.list:
        articles = publisher.list_available_articles()
        log("可用文章列表:", "info")
        for i, article in enumerate(articles, 1):
            info = publisher.extract_article_info(article)
            print(f"  {i}. {article.stem}")
            print(f"     标题: {info['title']}")
            print()
        return
    
    if args.article:
        asyncio.run(publisher.process_article(args.article))
    elif args.latest:
        articles = publisher.list_available_articles()
        if articles:
            latest = max(articles, key=lambda p: p.stat().st_mtime)
            log(f"最新文章: {latest.stem}")
            asyncio.run(publisher.process_article(latest.stem))
        else:
            log("未找到任何文章", "error")
    elif args.all:
        articles = publisher.list_available_articles()
        for article in articles:
            asyncio.run(publisher.process_article(article.stem))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
