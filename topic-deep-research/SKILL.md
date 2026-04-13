# Topic Deep Research → Blog Skill

## 觸發條件

當使用者說「研究 XXX」、「幫我研究 XXX」、「研究一下 XXX」等類似語句時，自動觸發本 skill。

## 行為描述

1. 解析輸入的關鍵詞（Topic）
2. 並行執行多源情報搜集：
   - Tavily 搜尋（主），失敗時 fallback 到 DuckDuckGo
   - GitHub 搜尋（直接抓頁面，不需要 API key）
   - RSS 資料抓取（使用現有 ~/ai-intel/hourly/ JSON 資料）
3. 彙整、去重、分類
4. 生成結構化研究摘要，輸出到 stdout + 儲存 JSON
5. **AI 根據研究摘要直接生成 12 章結構化技術解析文**（不走 Gemini subprocess）
6. 寫入部落格並自動 commit + push
7. 發送 Telegram 完成通知

## 搜尋原則

- **Tavily 為主**：讀取 `~/.openclaw/workspace/.secrets/tavily.key` 的 API key
- **DuckDuckGo fallback**：當 Tavily 失敗時，使用 `duckduckgo_search.py` 直接 HTTP POST 抓取
- **GitHub**：用 `curl` 抓 `https://github.com/search?q=<topic>` 頁面
- **RSS**：解析 `~/ai-intel/hourly/*.json` 的現有資料，額外擴展新來源

## 輸出

- **研究 JSON**：`openclaw-blog/src/content/post/YYYY-MM-DD-<slug>-research.json`（備份用）
- **文章檔案**：`~/projects/openclaw-blog/src/content/post/YYYY-MM-DD-<slug>.md`
- Frontmatter：`title`, `description`, `publishDate`, `tags`, `draft: false`
- 自動 git commit + push

## 文章格式規則

**⚠️ 禁止在文章 body 的開頭寫 `# 標題`（H1）**

部落格主題（`Masthead.astro`）會自動把 frontmatter 的 `title` 渲染成頁面 `<h1>`。
文章 body 若再寫 `# 標題`，會導致標題在頁面上出現兩次。

正確格式：
```markdown
---
title: "文章標題"
...
---

## 1. 第一章節  ← 從 H2 開始，不要有 H1
```

錯誤格式（禁止）：
```markdown
---
title: "文章標題"
---

# 文章標題   ← ❌ 這行會造成標題重複
## 1. 第一章節
```

## 章節結構（固定 12 章）

1. 專案總覽
2. 核心功能解析
3. 實際應用案例
4. 橫向比較
5. 競爭格局
6. 優缺點分析
7. 常見問題 FAQ
8. 版本演化時間線
9. 安全與風險
10. 成本分析
11. 個人觀點章節
12. 入門指南

## 使用方式

```
# research.sh <topic>
./research.sh "Hermes Agent"
```

## 所需檔案

- `research.sh` — 入口腳本，負責搜尋 + 彙整，輸出研究摘要供 AI 寫文章
- `scripts/tavily_search.py` — Tavily API 包裝
- `scripts/duckduckgo_search.py` — DuckDuckGo HTTP POST 搜尋（urllib 直連）
- `scripts/github_search.py` — GitHub 搜尋（curl HTML 解析）
- `scripts/rss_search.py` — RSS 內容抓取
- `scripts/dedupe_summarize.py` — 去重 + 分類 + 彙整
- `scripts/write_blog.py` — 研究摘要生成器（輸出結構化摘要，AI據此寫文章）

## 預估執行時間

3–5 分鐘（多源並行搜尋）
文章生成由 AI 直接處理，無 subprocess timeout 限制。