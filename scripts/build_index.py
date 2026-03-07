#!/usr/bin/env python3
"""
构建索引脚本：扫描 docs/ 目录下的所有 Markdown 文件，
生成搜索索引和知识图谱数据。
支持交互式 Markdown 扩展语法。
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime

try:
    import frontmatter
except ImportError:
    print("请安装依赖: pip install python-frontmatter")
    raise


DOCS_DIR = Path("docs")
OUTPUT_DIR = Path("site/data")


def extract_mentions(content: str) -> list:
    """提取 @提及的内容 """
    pattern = r'@([^\s@,，。.!！?？\n]+)'
    mentions = re.findall(pattern, content)
    return list(set(mentions))


def extract_interactive_elements(content: str) -> dict:
    """提取交互式元素信息 """
    elements = {
        'has_python_code': False,
        'has_sliders': False,
        'has_charts': False,
        'has_tables': False,
        'slider_vars': [],
        'chart_types': []
    }
    
    # 检测可运行代码块
    if re.search(r'```python-runnable', content):
        elements['has_python_code'] = True
    
    # 检测滑块
    slider_pattern = r'@slider\[(\w+)\]'
    sliders = re.findall(slider_pattern, content)
    if sliders:
        elements['has_sliders'] = True
        elements['slider_vars'] = sliders
    
    # 检测图表
    chart_pattern = r'@chart\[(\w+)\]'
    charts = re.findall(chart_pattern, content)
    if charts:
        elements['has_charts'] = True
        elements['chart_types'] = charts
    
    # 检测表格
    if re.search(r'@table\[', content):
        elements['has_tables'] = True
    
    return elements


def parse_markdown_file(filepath: Path) -> dict:
    """解析单个 Markdown 文件 """
    try:
        post = frontmatter.load(filepath)
        
        # 提取交互式元素
        interactive = extract_interactive_elements(post.content)
        
        # 基础信息
        article = {
            "id": filepath.stem,
            "filename": filepath.name,
            "path": str(filepath),
            "title": post.get("title", filepath.stem),
            "authors": post.get("authors", []),
            "year": post.get("year"),
            "tags": post.get("tags", []),
            "category": post.get("category", filepath.parent.name),
            "venue": post.get("venue", ""),
            "summary": post.get("summary", ""),
            "content": post.content,
            "mentions": extract_mentions(post.content),
            "interactive": interactive,
            "updated": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
        }
        
        return article
    except Exception as e:
        print(f"解析文件失败: {filepath}, 错误: {e}")
        return None


def build_graph(articles: list) -> dict:
    """构建知识图谱 """
    nodes = []
    links = []
    node_set = set()
    
    for article in articles:
        # 文章节点
        article_id = f"article-{article['id']}"
        if article_id not in node_set:
            nodes.append({
                "id": article_id,
                "name": article["title"],
                "type": article["category"],
                "group": 1
            })
            node_set.add(article_id)
        
        # 作者节点
        for author in article.get("authors", []):
            author_id = f"author-{author}"
            if author_id not in node_set:
                nodes.append({
                    "id": author_id,
                    "name": author,
                    "type": "author",
                    "group": 2
                })
                node_set.add(author_id)
            links.append({
                "source": author_id,
                "target": article_id,
                "type": "authored"
            })
        
        # 标签节点
        for tag in article.get("tags", []):
            tag_id = f"tag-{tag}"
            if tag_id not in node_set:
                nodes.append({
                    "id": tag_id,
                    "name": tag,
                    "type": "tag",
                    "group": 3
                })
                node_set.add(tag_id)
            links.append({
                "source": article_id,
                "target": tag_id,
                "type": "tagged"
            })
        
        # 提及关系
        for mention in article.get("mentions", []):
            mentioned = None
            for other in articles:
                if other["title"] == mention or mention in other.get("authors", []):
                    mentioned = other
                    break
            
            if mentioned and mentioned["id"] != article["id"]:
                mentioned_id = f"article-{mentioned['id']}"
                links.append({
                    "source": article_id,
                    "target": mentioned_id,
                    "type": "mentions"
                })
    
    return {"nodes": nodes, "links": links}


def generate_semantic_index(articles: list) -> dict:
    """生成语义搜索索引 """
    semantic_keywords = {}
    
    for article in articles:
        keywords = set()
        keywords.update(article.get("tags", []))
        keywords.update(article.get("mentions", []))
        
        title = article.get("title", "")
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
        keywords.update(words)
        
        # 标记有交互式内容的论文
        interactive = article.get("interactive", {})
        if interactive.get("has_python_code"):
            keywords.add("可运行代码")
            keywords.add("交互式")
        if interactive.get("has_sliders"):
            keywords.add("参数调节")
        if interactive.get("has_charts"):
            keywords.add("可视化")
        
        semantic_keywords[article["id"]] = list(keywords)
    
    return semantic_keywords


def main():
    """主函数 """
    print("🔍 扫描文档...")
    
    articles = []
    
    for category_dir in DOCS_DIR.iterdir():
        if category_dir.is_dir():
            for md_file in category_dir.glob("*.md"):
                print(f"  解析: {md_file}")
                article = parse_markdown_file(md_file)
                if article:
                    articles.append(article)
    
    print(f"\n✅ 解析完成: {len(articles)} 篇文章")
    
    # 统计交互式内容
    interactive_count = sum(
        1 for a in articles 
        if a.get("interactive", {}).get("has_python_code")
    )
    if interactive_count > 0:
        print(f"  包含交互式代码: {interactive_count} 篇")
    
    # 构建图谱
    print("🕸️ 构建知识图谱...")
    graph = build_graph(articles)
    print(f"  节点: {len(graph['nodes'])}, 连接: {len(graph['links'])}")
    
    # 语义索引
    print("🧠 生成语义索引...")
    semantic_index = generate_semantic_index(articles)
    
    # 输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存索引文件
    index_data = {
        "articles": articles,
        "graph": graph,
        "semantic": semantic_index,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
            "interactive_articles": interactive_count
        }
    }
    
    output_file = OUTPUT_DIR / "index.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 索引已保存: {output_file}")
    print(f"📊 统计: {len(articles)} 篇文章, {len(graph['nodes'])} 个节点, {len(graph['links'])} 条关系")


if __name__ == "__main__":
    main()
