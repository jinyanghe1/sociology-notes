#!/usr/bin/env python3
"""
构建脚本：将 Markdown 转换为 HTML，生成索引和概念映射
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

try:
    import frontmatter
    import markdown
    from markdown.extensions import fenced_code, tables, toc
except ImportError:
    print("请安装依赖: pip install python-frontmatter markdown")
    raise

# 配置
DOCS_DIR = Path("docs")
SITE_DIR = Path("site")
OUTPUT_DIR = SITE_DIR / "articles"
DATA_DIR = SITE_DIR / "data"

# Markdown 转换器
md_converter = markdown.Markdown(extensions=[
    'fenced_code',
    'tables',
    'toc',
    'nl2br',
], extension_configs={
    'toc': {'permalink': False}
})


def extract_concepts(content: str) -> list:
    """从文章内容中提取概念关键词（@概念名）"""
    pattern = r'@([^\s@,，。.!！?？\n\]\[]+)'
    concepts = re.findall(pattern, content)
    # 过滤掉可能是作者名的（通常2-4个汉字，或英文名字）
    filtered = []
    for c in concepts:
        c = c.strip()
        # 排除纯数字
        if c.isdigit():
            continue
        # 排除太短的
        if len(c) < 2:
            continue
        # 排除文件名格式（包含下划线）
        if '_' in c:
            continue
        filtered.append(c)
    return list(set(filtered))


def extract_summary(content: str, max_length: int = 200) -> str:
    """从内容中提取摘要"""
    # 移除 Markdown 标记
    text = re.sub(r'[#*`\[\]\(\)]', '', content)
    # 取前 max_length 个字符
    text = text.replace('\n', ' ').strip()
    if len(text) > max_length:
        text = text[:max_length] + '...'
    return text


def parse_markdown_file(filepath: Path) -> dict:
    """解析 Markdown 文件，转换为结构化数据"""
    try:
        post = frontmatter.load(filepath)
        
        # 提取概念
        concepts = extract_concepts(post.content)
        
        # 生成 HTML 内容
        html_content = md_converter.convert(post.content)
        md_converter.reset()
        
        # 基础信息
        article = {
            "id": filepath.stem,
            "filename": filepath.name,
            "path": str(filepath.relative_to(DOCS_DIR)),
            "html_path": f"articles/{filepath.stem}.html",
            "title": post.get("title", filepath.stem),
            "authors": post.get("authors", []),
            "year": post.get("year"),
            "tags": post.get("tags", []),
            "category": post.get("category", filepath.parent.name),
            "venue": post.get("venue", ""),
            "summary": post.get("summary", extract_summary(post.content)),
            "content": post.content,
            "html_content": html_content,
            "concepts": concepts,
            "mentions": extract_concepts(post.content),  # 提及的其他人/概念
            "updated": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
        }
        
        return article
    except Exception as e:
        print(f"❌ 解析文件失败: {filepath}, 错误: {e}")
        return None


def generate_article_html(article: dict) -> str:
    """生成完整的文章 HTML 页面"""
    
    # 构建作者链接
    authors_html = ', '.join([
        f'<a href="../index.html?author={quote(a)}" class="author-link">{a}</a>'
        for a in article.get('authors', [])
    ])
    
    # 构建标签链接
    tags_html = ' '.join([
        f'<a href="../index.html?tag={quote(t)}" class="tag-link">{t}</a>'
        for t in article.get('tags', [])
    ])
    
    # 构建概念链接
    concepts_html = ', '.join([
        f'<a href="../index.html?concept={quote(c)}" class="concept-link">{c}</a>'
        for c in article.get('concepts', [])
    ])
    
    # 处理内容中的 @ 提及，转换为链接
    content_html = article['html_content']
    for concept in article.get('concepts', []):
        content_html = re.sub(
            rf'@{re.escape(concept)}(?!\w)',
            f'<a href="../index.html?concept={quote(concept)}" class="mention-link">@{concept}</a>',
            content_html
        )
    
    category_labels = {
        'papers': '📄 论文笔记',
        'books': '📖 书籍笔记', 
        'concepts': '💡 概念梳理'
    }
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | 社会学读书笔记</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/interactive.css">
    <!-- Plotly.js -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <!-- Marked.js -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body class="article-page">
    <header class="article-header">
        <nav class="breadcrumb">
            <a href="../index.html">🏠 首页</a>
            <span>/</span>
            <a href="../index.html?view={article['category']}">{category_labels.get(article['category'], article['category'])}</a>
            <span>/</span>
            <span class="current">{article['title'][:30]}{'...' if len(article['title']) > 30 else ''}</span>
        </nav>
    </header>

    <main class="article-main">
        <article class="article-content">
            <header class="article-title-header">
                <span class="article-category {article['category']}">{category_labels.get(article['category'], article['category'])}</span>
                <h1>{article['title']}</h1>
                
                <div class="article-meta">
                    {f'<div class="authors">作者: {authors_html}</div>' if authors_html else ''}
                    {f'<div class="year">年份: {article["year"]}</div>' if article.get('year') else ''}
                    {f'<div class="venue">来源: {article["venue"]}</div>' if article.get('venue') else ''}
                    {f'<div class="updated">更新: {article["updated"][:10]}</div>' if article.get('updated') else ''}
                </div>
                
                {f'<div class="article-tags">标签: {tags_html}</div>' if tags_html else ''}
                
                {f'<div class="article-concepts">💡 涉及概念: {concepts_html}</div>' if concepts_html else ''}
            </header>
            
            <div class="article-body">
                {content_html}
            </div>
            
            <footer class="article-footer">
                <div class="article-nav">
                    <a href="../index.html" class="btn-back">← 返回列表</a>
                </div>
            </footer>
        </article>
    </main>

    <script src="../js/article.js"></script>
</body>
</html>'''


def build_concept_index(articles: list) -> dict:
    """构建概念索引：概念 → 文章列表"""
    concept_map = {}
    
    for article in articles:
        for concept in article.get('concepts', []):
            if concept not in concept_map:
                concept_map[concept] = {
                    'concept': concept,
                    'articles': [],
                    'mentioned_by': set()
                }
            concept_map[concept]['articles'].append({
                'id': article['id'],
                'title': article['title'],
                'authors': article.get('authors', []),
                'category': article.get('category'),
                'html_path': article.get('html_path')
            })
            concept_map[concept]['mentioned_by'].update(article.get('authors', []))
    
    # 转换为列表并排序
    concept_list = []
    for concept, data in sorted(concept_map.items(), key=lambda x: len(x[1]['articles']), reverse=True):
        concept_list.append({
            'concept': concept,
            'article_count': len(data['articles']),
            'articles': sorted(data['articles'], key=lambda x: x.get('year', 0), reverse=True),
            'mentioned_by': list(data['mentioned_by'])
        })
    
    return {
        'concepts': concept_list,
        'total_concepts': len(concept_list),
        'generated_at': datetime.now().isoformat()
    }


def build_author_index(articles: list) -> dict:
    """构建作者索引"""
    author_map = {}
    
    for article in articles:
        for author in article.get('authors', []):
            if author not in author_map:
                author_map[author] = {
                    'name': author,
                    'articles': []
                }
            author_map[author]['articles'].append({
                'id': article['id'],
                'title': article['title'],
                'year': article.get('year'),
                'category': article.get('category'),
                'html_path': article.get('html_path')
            })
    
    return {
        'authors': sorted([{
            'name': k,
            'article_count': len(v['articles']),
            'articles': sorted(v['articles'], key=lambda x: x.get('year', 0), reverse=True)
        } for k, v in author_map.items()], key=lambda x: x['article_count'], reverse=True),
        'total_authors': len(author_map)
    }


def save_article_html(article: dict):
    """保存文章 HTML 文件"""
    output_path = OUTPUT_DIR / f"{article['id']}.html"
    html = generate_article_html(article)
    output_path.write_text(html, encoding='utf-8')
    print(f"  ✓ 生成: {output_path}")


def load_existing_index_articles(index_file: Path) -> list:
    """读取已有 index.json 的 articles（若存在）"""
    if not index_file.exists():
        return []
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("articles", []) if isinstance(data, dict) else []
    except Exception:
        return []


def main():
    """主函数"""
    print("🔨 开始构建...")
    print(f"📁 文档目录: {DOCS_DIR}")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 增量构建：不删除旧 HTML，避免误删手工维护页面
    # 仅覆盖同名文档生成的 HTML
    
    articles = []
    failed_files = []
    
    # 遍历所有 Markdown 文件
    print("\n📄 扫描文档...")
    for category_dir in DOCS_DIR.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            for md_file in category_dir.glob("*.md"):
                print(f"  解析: {md_file}")
                article = parse_markdown_file(md_file)
                if article:
                    articles.append(article)
                    # 生成 HTML 文件
                    save_article_html(article)
                else:
                    failed_files.append(str(md_file))

    if failed_files:
        print("\n❌ 以下文件解析失败，已中止构建:")
        for f in failed_files:
            print(f"  - {f}")
        raise SystemExit(1)
    
    print(f"\n✅ 解析完成: {len(articles)} 篇文章")
    
    # 构建概念索引
    print("\n💡 构建概念索引...")
    concept_index = build_concept_index(articles)
    print(f"  提取概念: {concept_index['total_concepts']} 个")
    
    # 构建作者索引
    print("\n👥 构建作者索引...")
    author_index = build_author_index(articles)
    print(f"  作者数量: {author_index['total_authors']} 位")
    
    # 构建图谱数据
    print("\n🕸️ 构建知识图谱...")
    graph = build_graph(articles)
    print(f"  节点: {len(graph['nodes'])}, 连接: {len(graph['links'])}")
    
    # 保存主索引（并保留已有 index.json 中的非 docs 条目）
    existing_index_file = DATA_DIR / "index.json"
    existing_articles = load_existing_index_articles(existing_index_file)
    built_ids = {a['id'] for a in articles}

    preserved_articles = []
    for item in existing_articles:
        item_id = item.get("id")
        html_path = item.get("html_path", "")
        html_file = SITE_DIR / html_path if html_path else None
        if not item_id or item_id in built_ids:
            continue
        # 仅保留页面文件仍存在的历史条目
        if html_file and html_file.exists():
            preserved_articles.append(item)

    merged_articles = [{
        'id': a['id'],
        'title': a['title'],
        'authors': a['authors'],
        'year': a['year'],
        'tags': a['tags'],
        'category': a['category'],
        'venue': a['venue'],
        'summary': a['summary'],
        'html_path': a['html_path'],
        'concepts': a['concepts'],
        'updated': a['updated']
    } for a in articles] + preserved_articles

    index_data = {
        "articles": merged_articles,
        "concepts": concept_index,
        "authors": author_index,
        "graph": graph,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
            "preserved_articles": len(preserved_articles),
            "total_concepts": concept_index['total_concepts'],
            "total_authors": author_index['total_authors']
        }
    }
    
    output_file = DATA_DIR / "index.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 索引已保存: {output_file}")
    print(f"\n📊 统计:")
    print(f"  - 文章: {len(articles)} 篇")
    print(f"  - 保留历史条目: {len(preserved_articles)} 篇")
    print(f"  - 概念: {concept_index['total_concepts']} 个")
    print(f"  - 作者: {author_index['total_authors']} 位")
    print(f"  - 图谱节点: {len(graph['nodes'])} 个")
    print(f"  - 图谱连接: {len(graph['links'])} 条")
    
    print("\n🎉 构建完成!")


def build_graph(articles: list) -> dict:
    """构建知识图谱（简版）"""
    nodes = []
    links = []
    node_set = set()
    
    for article in articles:
        article_id = f"article-{article['id']}"
        if article_id not in node_set:
            nodes.append({
                "id": article_id,
                "name": article["title"],
                "type": article["category"],
                "group": 1
            })
            node_set.add(article_id)
        
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
        
        for concept in article.get("concepts", []):
            concept_id = f"concept-{concept}"
            if concept_id not in node_set:
                nodes.append({
                    "id": concept_id,
                    "name": concept,
                    "type": "concept",
                    "group": 4
                })
                node_set.add(concept_id)
            links.append({
                "source": article_id,
                "target": concept_id,
                "type": "has_concept"
            })
    
    return {"nodes": nodes, "links": links}


if __name__ == "__main__":
    main()
