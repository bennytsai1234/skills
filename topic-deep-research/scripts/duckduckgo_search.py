#!/usr/bin/env python3
"""
DuckDuckGo 搜尋包裝
使用 urllib 直接發送 HTTP POST 請求（無需 API Key / curl）
Topic: 從第一個參數取得
輸出:   JSON 陣列，每項包含 title, url, content, source
"""

import sys
import json
import urllib.request
import urllib.parse
import re


def duckduckgo_search(topic: str) -> list:
    """用 urllib POST 抓取 DuckDuckGo HTML 搜尋結果"""
    results = []

    try:
        encoded_topic = urllib.parse.quote_plus(topic)
        search_url = "https://html.duckduckgo.com/html/"

        # POST data
        post_data = urllib.parse.urlencode({
            "q": topic,
            "kl": "wt-wt"
        }).encode("utf-8")

        req = urllib.request.Request(
            search_url,
            data=post_data,
            method="POST",
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
                "Connection": "keep-alive",
            }
        )

        with urllib.request.urlopen(req, timeout=25) as resp:
            output = resp.read().decode("utf-8", errors="replace")

        # 用 finditer 找每個 result__a block（屬性順序任意）
        link_pattern = re.compile(
            '<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            re.DOTALL
        )
        snippet_pattern = re.compile(
            '<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            re.DOTALL
        )

        for link_match in link_pattern.finditer(output):
            url = link_match.group(1).strip()
            title_html = link_match.group(2)
            title = re.sub(r'<[^>]+>', '', title_html).strip()

            if not title or not url:
                continue

            # 跳過非結果連結
            skip = ["duckduckgo.com", "yahoo.com", "bing.com", "google.com"]
            if any(p in url.lower() for p in skip):
                continue

            # 在同一 block 周圍找 snippet
            start = link_match.start()
            end = min(link_match.end() + 500, len(output))
            block_around = output[start:end]
            snippet_match = snippet_pattern.search(block_around)
            snippet = ""
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()

            results.append({
                "title": title[:300],
                "url": url,
                "content": snippet[:500] if snippet else "",
                "score": 0.8,
                "source": "duckduckgo"
            })

    except Exception as e:
        print(f"DuckDuckGo search error: {e}", file=sys.stderr)

    return results


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else ""

    if not topic:
        print("[]")
        sys.exit(1)

    results = duckduckgo_search(topic)
    print(json.dumps(results, ensure_ascii=False))
