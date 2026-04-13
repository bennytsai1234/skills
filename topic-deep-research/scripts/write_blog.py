#!/usr/bin/env python3
"""
研究摘要生成器（不走 Gemini，由 AI 直接寫文章）
讀取 consolidated.json，輸出結構化研究摘要供 AI 使用
"""

import sys
import json
from datetime import datetime

def load_json(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def build_research_summary(topic: str, research_file: str) -> str:
    """把研究資料整理成人類可讀的結構化摘要"""
    data = load_json(research_file)
    if not data:
        return f"# {topic}\n\n研究資料載入失敗。"

    merged = data.get("merged", [])
    by_cat = data.get("by_category", {})

    lines = []
    lines.append(f"# 研究主題：{topic}")
    lines.append(f"資料筆數：共 {len(merged)} 筆\n")

    # --- GitHub ---
    github_items = by_cat.get("github", [])
    if github_items:
        lines.append("## GitHub 資源")
        for item in github_items[:8]:
            name = item.get("name", "")
            url = item.get("url", "")
            desc = item.get("description", "")[:150]
            stars = item.get("stars", "")
            stars_str = f" ⭐{stars}" if stars else ""
            lines.append(f"- **{name}**{stars_str}")
            if desc:
                lines.append(f"  {desc}")
            lines.append(f"  URL: {url}")
        lines.append("")

    # --- 官方資源 ---
    official = by_cat.get("official", [])
    if official:
        lines.append("## 官方資源")
        for item in official[:5]:
            title = item.get("title", "")
            url = item.get("url", "")
            lines.append(f"- [{title}]({url})")
        lines.append("")

    # --- 部落格文章 ---
    blogs = by_cat.get("blog", [])
    if blogs:
        lines.append("## 部落格文章")
        for item in blogs[:8]:
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")[:300]
            lines.append(f"- **[{title}]({url})**")
            if content:
                lines.append(f"  {content}")
        lines.append("")

    # --- 社群討論 ---
    discussions = by_cat.get("discussion", [])
    if discussions:
        lines.append("## 社群討論")
        for item in discussions[:5]:
            title = item.get("title", "")
            url = item.get("url", "")
            lines.append(f"- [{title}]({url})")
        lines.append("")

    # --- 最新消息 ---
    news = by_cat.get("news", [])
    if news:
        lines.append("## 最新消息")
        for item in news[:5]:
            title = item.get("title", "")
            url = item.get("url", "")
            lines.append(f"- [{title}]({url})")
        lines.append("")

    # --- 所有內容片段（按相關性取前 20 筆）---
    all_content = []
    for item in merged[:20]:
        title = item.get("title", "")
        content = item.get("content", "")[:500]
        url = item.get("url", "")
        if content:
            all_content.append(f"**{title}**\n{content}\n來源：{url}")

    if all_content:
        lines.append("## 原始內容片段（供 AI 學習）")
        lines.append("")
        lines.append("\n---\n\n".join(all_content))

    return "\n".join(lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: write_blog.py <topic> <consolidated.json>", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]
    research_file = sys.argv[2]

    summary = build_research_summary(topic, research_file)
    print(summary)

if __name__ == "__main__":
    main()
