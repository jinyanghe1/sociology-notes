#!/usr/bin/env python3
"""
Create a new Markdown note and optionally rebuild site outputs.

Example:
python scripts/create_note.py \
  --category papers \
  --title "基层政府间的共谋现象再讨论" \
  --authors "张三,李四" \
  --year 2026 \
  --tags "基层治理,共谋" \
  --venue "社会学研究" \
  --summary "讨论共谋机制在数字治理情境下的变化"
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


VALID_CATEGORIES = ("papers", "books", "concepts")


def parse_csv(text: str) -> list[str]:
    parts = re.split(r"[,，]", text.strip())
    return [p.strip() for p in parts if p.strip()]


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
    return f"\"{escaped}\""


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "untitled"


def title_keyword(title: str, max_len: int = 20) -> str:
    cleaned = re.sub(r"\s+", "", title).strip()
    return cleaned[:max_len] or "新笔记"


def build_stem(
    category: str,
    title: str,
    authors: list[str],
    year: int | None,
    custom_filename: str | None,
) -> str:
    if custom_filename:
        stem = custom_filename.removesuffix(".md")
        return sanitize_filename(stem)

    first_author = sanitize_filename(authors[0]) if authors else "匿名"
    keyword = sanitize_filename(title_keyword(title))

    if category == "papers":
        year_part = str(year or dt.datetime.now().year)
        return sanitize_filename(f"{first_author}_{year_part}_{keyword}")
    if category == "books":
        return sanitize_filename(f"{first_author}_{keyword}")
    return keyword


def render_frontmatter(
    category: str,
    title: str,
    authors: list[str],
    year: int | None,
    tags: list[str],
    venue: str,
    summary: str,
) -> str:
    y = year if year is not None else dt.datetime.now().year
    authors_yaml = ", ".join([yaml_quote(a) for a in authors])
    tags_yaml = ", ".join([yaml_quote(t) for t in tags])
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"authors: [{authors_yaml}]",
        f"year: {y}",
        f"tags: [{tags_yaml}]",
    ]
    if category == "papers":
        lines.append(f"venue: {yaml_quote(venue)}")
    lines.extend(
        [
            f"category: {yaml_quote(category)}",
            f"summary: {yaml_quote(summary)}",
            "---",
        ]
    )
    return "\n".join(lines)


def render_body(category: str, title: str) -> str:
    if category == "papers":
        return f"""# {title}

## 核心观点

## 研究问题与方法

## 主要发现

## 与相关研究的对话

## 可继续追问的问题
"""
    if category == "books":
        return f"""# {title}

## 核心命题

## 关键章节摘要

## 方法与材料

## 与既有理论的关系

## 个人评述
"""
    return f"""# {title}

## 概念定义

## 理论来源

## 经验应用

## 相关概念
"""


def run_build(repo_root: Path) -> None:
    cmd = [sys.executable, str(repo_root / "scripts" / "build.py")]
    result = subprocess.run(cmd, cwd=repo_root)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="生成新笔记并自动构建 HTML 与索引"
    )
    parser.add_argument("--category", required=True, choices=VALID_CATEGORIES)
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", default="", help="作者列表，用逗号分隔")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--tags", default="", help="标签列表，用逗号分隔")
    parser.add_argument("--venue", default="", help="仅论文笔记使用")
    parser.add_argument("--summary", default="待补充摘要")
    parser.add_argument("--filename", default=None, help="可选，自定义文件名")
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="仅创建 md，不自动执行 scripts/build.py",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs" / args.category
    docs_dir.mkdir(parents=True, exist_ok=True)

    authors = parse_csv(args.authors)
    tags = parse_csv(args.tags)
    stem = build_stem(args.category, args.title, authors, args.year, args.filename)
    md_path = docs_dir / f"{stem}.md"

    if md_path.exists():
        raise SystemExit(f"文件已存在: {md_path}")

    frontmatter = render_frontmatter(
        category=args.category,
        title=args.title.strip(),
        authors=authors,
        year=args.year,
        tags=tags,
        venue=args.venue.strip(),
        summary=args.summary.strip(),
    )
    body = render_body(args.category, args.title.strip())
    md_path.write_text(frontmatter + "\n\n" + body, encoding="utf-8")

    print(f"已创建: {md_path.relative_to(repo_root)}")

    if not args.no_build:
        run_build(repo_root)
        print("已执行构建: scripts/build.py")
        print(f"预计文章页面: site/articles/{stem}.html")


if __name__ == "__main__":
    main()
