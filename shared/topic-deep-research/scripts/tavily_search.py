#!/usr/bin/env python3
"""
Tavily API 包裝
API Key: 從第一個參數取得
Topic:   從第二個參數取得
輸出:    JSON 陣列，每項包含 title, url, content, score
"""

import sys
import json
import urllib.request
import urllib.parse

def tavily_search(topic: str, api_key: str) -> list:
    """呼叫 Tavily Search API"""
    url = "https://api.tavily.com/search"
    
    payload = json.dumps({
        "query": topic,
        "search_depth": "advanced",
        "max_results": 10,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False
    })
    
    req = urllib.request.Request(
        url,
        data=payload.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0),
            "source": "tavily"
        })
    
    return results

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else ""
    api_key = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not topic or not api_key:
        print("[]")
        sys.exit(1)
    
    try:
        results = tavily_search(topic, api_key)
        print(json.dumps(results, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("[]")
        sys.exit(1)