#!/usr/bin/env python3
"""
构建索引脚本：扫描 docs/ 目录下的所有 Markdown 文件，
生成搜索索引和知识图谱数据。
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


def parse_markdown_file(filepath: Path) -> dict:
    """解析单个 Markdown 文件 """
    try:
        post = frontmatter.load(filepath)
        
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
            # 查找被提及的文章
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
    """生成语义搜索索引 (预留接口) """
    # 这里可以集成 sentence-transformers 或其他向量库
    # 目前返回关键词列表用于简单语义匹配
    semantic_keywords = {}
    
    for article in articles:
        keywords = set()
        keywords.update(article.get("tags", []))
        keywords.update(article.get("mentions", []))
        
        # 从标题提取关键词
        title = article.get("title", "")
        # 简单分词（可以改进）
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
        keywords.update(words)
        
        semantic_keywords[article["id"]] = list(keywords)
    
    return semantic_keywords


def main():
    """主函数 """
    print("🔍 扫描文档...")
    
    articles = []
    
    # 遍历所有 markdown 文件
    for category_dir in DOCS_DIR.iterdir():
        if category_dir.is_dir():
            for md_file in category_dir.glob("*.md"):
                print(f"  解析: {md_file}")
                article = parse_markdown_file(md_file)
                if article:
                    articles.append(article)
    
    print(f"\n✅ 解析完成: {len(articles)} 篇文章")
    
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
            "total_articles": len(articles)
        }
    }
    
    output_file = OUTPUT_DIR / "index.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 索引已保存: {output_file}")
    print(f"📊 统计: {len(articles)} 篇文章, {len(graph['nodes'])} 个节点, {len(graph['links'])} 条关系")


if __name__ == "__main__":
    main()
