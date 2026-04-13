#!/usr/bin/env python3
"""
RSS 內容抓取
使用現有 ~/ai-intel/hourly/ 的 JSON 資料，額外擴展新來源
Topic: 從第一個參數取得
輸出:   JSON 陣列，每項包含 title, url, content, published, source
"""

import sys
import json
import os
import glob
from datetime import datetime, timedelta

RSS_DIR = os.path.expanduser("~/ai-intel/hourly")

def load_existing_rss(topic: str) -> list:
    """讀取現有 ~/ai-intel/hourly/ 的 JSON 資料"""
    results = []
    
    if not os.path.isdir(RSS_DIR):
        return results
    
    # 讀取最近 24 小時內的 JSON 檔案
    cutoff = datetime.now() - timedelta(hours=24)
    pattern = os.path.join(RSS_DIR, "*.json")
    
    for filepath in glob.glob(pattern):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                continue
            
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
            
            for item in data:
                title = item.get("title", "")
                content = item.get("content", "") or item.get("description", "")
                url = item.get("url", "") or item.get("link", "")
                
                # 簡單關鍵字比對
                if topic.lower() in title.lower() or topic.lower() in content.lower():
                    results.append({
                        "title": title,
                        "url": url,
                        "content": content[:500] if content else "",
                        "published": item.get("published", "") or item.get("date", ""),
                        "source": item.get("source", "") or os.path.basename(filepath),
                        "type": "rss"
                    })
        except Exception as e:
            continue
    
    return results

def expand_rss_sources(topic: str) -> list:
    """嘗試抓取額外的 RSS 來源"""
    results = []
    
    # 常見 RSS 聚合來源
    rss_feeds = [
        f"https://hnrss.org/search?q={topic.replace(' ', '%20')}&duration=7d",
        f"https://rsshub.app/hackernews/search?q={topic.replace(' ', '%20')}",
    ]
    
    for feed_url in rss_feeds:
        try:
            import subprocess
            cmd = ["curl", "-s", "--max-time", "15", feed_url]
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            
            # 嘗試解析 RSS/Atom XML
            import re
            items = re.findall(r'<item>(.*?)</item>', output, re.DOTALL)
            for item in items[:5]:
                title = re.search(r'<title[^>]*>([^<]+)</title>', item)
                link = re.search(r'<link[^>]*>([^<]+)</link>', item)
                desc = re.search(r'<description[^>]*>([^<]+)</description>', item)
                
                results.append({
                    "title": title.group(1) if title else "",
                    "url": link.group(1) if link else "",
                    "content": desc.group(1)[:500] if desc else "",
                    "published": "",
                    "source": "hackernews",
                    "type": "rss"
                })
        except Exception:
            continue
    
    return results

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not topic:
        print("[]")
        sys.exit(1)
    
    results = load_existing_rss(topic)
    results.extend(expand_rss_sources(topic))
    
    # 去重（根據 URL）
    seen = set()
    unique = []
    for r in results:
        if r["url"] and r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    
    print(json.dumps(unique, ensure_ascii=False))