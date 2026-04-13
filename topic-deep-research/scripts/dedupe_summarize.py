#!/usr/bin/env python3
"""
去重 + 摘要生成
接收 4 個 JSON 檔案（tavily, ddg, github, rss）
輸出合併、去重、分類後的 JSON
"""

import sys
import json

def load_json(filepath: str) -> list:
    """載入 JSON 檔案"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []
    except Exception:
        return []

def dedupe_and_merge(tavily_file: str, ddg_file: str, github_file: str, rss_file: str) -> list:
    """去重 + 合併所有來源"""
    
    all_items = []
    
    # 依序載入
    for filepath in [tavily_file, ddg_file, github_file, rss_file]:
        items = load_json(filepath)
        all_items.extend(items)
    
    # 去重（根據 URL）
    seen_urls = set()
    seen_titles = set()
    unique = []
    
    for item in all_items:
        url = item.get("url", "")
        title = item.get("title", "")
        
        # 標準化 URL
        if url:
            url = url.strip().lower()
            # 移除結尾斜線
            url = url.rstrip("/")
        
        # 標準化 title
        if title:
            title_clean = title.strip().lower()
        else:
            title_clean = ""
        
        # 跳過明顯重複
        if url and url in seen_urls:
            continue
        if title_clean and title_clean in seen_titles:
            continue
        
        if url:
            seen_urls.add(url)
        if title_clean:
            seen_titles.add(title_clean)
        
        # 確保有 source 欄位
        if "source" not in item:
            item["source"] = "unknown"
        
        unique.append(item)
    
    # 按 score 排序（有的話）
    try:
        unique.sort(key=lambda x: x.get("score", 0), reverse=True)
    except:
        pass
    
    return unique

def categorize(results: list) -> dict:
    """簡單分類：官方、部落格、討論、GitHub、news"""
    categories = {
        "official": [],
        "blog": [],
        "discussion": [],
        "github": [],
        "news": []
    }
    
    keywords_official = ["official", "docs", "documentation", "guide", "website"]
    keywords_blog = ["blog", "medium", "dev.to", "hashnode", "substack"]
    keywords_discuss = ["discuss", "thread", "question", "reddit", "hackernews", "news.ycombinator"]
    keywords_github = ["github.com"]
    keywords_news = ["news", "release", "announce"]
    
    for item in results:
        url = item.get("url", "").lower()
        title = item.get("title", "").lower()
        source = item.get("source", "")
        
        text = f"{url} {title}"
        
        if source == "github" or "github.com" in url:
            categories["github"].append(item)
        elif any(k in text for k in keywords_blog):
            categories["blog"].append(item)
        elif any(k in text for k in keywords_official):
            categories["official"].append(item)
        elif any(k in text for k in keywords_discuss):
            categories["discussion"].append(item)
        else:
            categories["news"].append(item)
    
    # 清理空類別
    return {k: v for k, v in categories.items() if v}

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: dedupe_summarize.py <tavily.json> <ddg.json> <github.json> <rss.json>")
        sys.exit(1)
    
    tavily_file = sys.argv[1]
    ddg_file = sys.argv[2]
    github_file = sys.argv[3]
    rss_file = sys.argv[4]
    
    merged = dedupe_and_merge(tavily_file, ddg_file, github_file, rss_file)
    categorized = categorize(merged)
    
    output = {
        "merged": merged,
        "by_category": categorized,
        "total": len(merged)
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))