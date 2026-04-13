#!/usr/bin/env python3
"""
GitHub 搜尋（無需 API Key）
使用 web_fetch 直接抓取 GitHub 搜尋頁面
Topic: 從第一個參數取得
輸出:   JSON 陣列，每項包含 name, url, description, stars, updated
"""

import sys
import json
import subprocess
import re

def fetch_github_search(topic: str) -> list:
    """用 web_fetch 直接抓 GitHub 搜尋頁面"""
    results = []
    search_url = f"https://github.com/search?q={topic}&type=repositories&sort=stars"
    
    try:
        # 用 curl 抓頁面（避免 subprocess 複雜度）
        cmd = [
            "curl", "-s", "--max-time", "20",
            "-A", "Mozilla/5.0 (compatible; topic-deep-research/1.0)",
            search_url
        ]
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        
        # 解析 HTML 中的 repo 資訊
        # GitHub 頁面結構：<a class="v-align-middle" href="/owner/repo">Repo Name</a>
        repo_pattern = r'href="(/[^/]+/[^/"]+)"[^>]*>.*?</a>.*?<p[^>]*>([^<]+)</p>'
        
        # 用更簡單的方式解析：找所有 repo 連結
        repo_links = re.findall(r'/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', output)
        repo_links = list(dict.fromkeys(repo_links))[:15]  # 去重，取前15
        
        for link in repo_links:
            parts = link.strip("/").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                if any(kw in [owner, repo] for kw in ["search", "issues", "pulls", "wiki", "actions", "settings"]):
                    continue
                results.append({
                    "name": f"{owner}/{repo}",
                    "url": f"https://github.com{link}" if link.startswith("/") else link,
                    "description": "",
                    "source": "github",
                    "type": "repository"
                })
        
        # 也嘗試解析 stars
        stars_match = re.findall(r'(\d+[\d,]*)\s+star', output, re.IGNORECASE)
        for i, count in enumerate(stars_match[:len(results)]):
            clean_count = count.replace(",", "")
            try:
                results[i]["stars"] = int(clean_count)
            except:
                pass
        
        # 解析 description
        desc_pattern = re.findall(r'<p[^>]*class="[^"]*"[^>]*>([^<]+)</p>', output)
        for i, desc in enumerate(desc_pattern[:len(results)]):
            if desc.strip():
                results[i]["description"] = desc.strip()[:200]
        
    except Exception as e:
        print(f"GitHub fetch error: {e}", file=sys.stderr)
    
    return results[:15]

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not topic:
        print("[]")
        sys.exit(1)
    
    results = fetch_github_search(topic)
    print(json.dumps(results, ensure_ascii=False))