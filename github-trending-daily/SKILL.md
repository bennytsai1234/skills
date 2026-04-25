---
name: github-trending-daily
description: 每天台北時間 07:30 執行。從 GitHub Trending 當日排行榜抓取有趣的開源專案，寫成「GitHub 熱門專案速讀」。繼承 _blog-publisher-base。防重複機制：過去 7 天內寫過的專案會被跳過。
---

# github-trending-daily（GitHub 熱門專案速讀）

**發文時段**：每天 `07:30`（台北）
**定位**：從 GitHub Trending 當日排行榜中挑 3–5 個最有價值的專案，讓讀者早上快速掌握當天最值得關注的開源專案。

風格規則、schema、L1–L4 自檢、發佈管線全部繼承 `_blog-publisher-base/SKILL.md`。

---

## Variant 變數

```
SLOT_ID       = github-trending-daily
PUBLISH_HHMM  = 07:30
COVER_TITLE   = GitHub 熱門專案｜YYYY-MM-DD
COVER_TAGS    = GitHub,trending,open-source
COMMIT_PREFIX = docs: GitHub 熱門專案
SERIES        = (空，非系列文)
```

---

## Step 1｜抓取 GitHub Trending

使用 `web_fetch` 或 `curl` 抓取當日 GitHub Trending：

```bash
curl -s "https://github.com/trending?since=daily" | grep -oP 'href="/[^/]+/[^"]+' | head -20
```

若抓取失敗：`exit 1`。

---

## Step 2｜讀取過去已選清單（防重複）

把 `selections[]` 裡所有的 `repo`（e.g. `user/project`）收集起來，Step 3 選題時自動跳過這些專案。

---

## Step 3｜挑選 3–5 個值得寫的專案

挑選標準：

- **技術價值**：不是湊熱鬧的專案，而是真的有技術內涵的
- **創新性**：提出新的做法、新的工具思路
- **實用性**：對開發者日常工作有幫助
- **多樣性**：避免同類型專案全部選上
- **防重複**：專案名稱（`user/project`）不得出現在 Step 2 已選清單

排除：
- 純個人 project、練習性質的玩具專案
- 已經紅超過一個月的舊專案
- 過去 7 天內已經寫過的專案

從命中清單挑 3–5 個進入 Step 4。

---

## Step 4｜研究每個專案

對每個入選的專案：

1. `web_fetch` 讀取 GitHub 倉庫的 README
2. `web_fetch` 看一下專案的程式碼結構
3. 找一下有沒有官方的 demo 或相關介紹文章
4. 確認它的 star 數、contributor 數、授權條款

整理出：
- 這個專案是做什麼的
- 它解決了什麼問題
- 技術上特別的地方在哪裡
- 適合什麼樣的開發者

---

## Step 5｜寫作

目標 **1200–1800 字**，3–5 個專案，平均每個專案 250–350 字。

### Frontmatter

```yaml
---
title: "【熱門專案】YYYY-MM-DD GitHub 趨勢速讀"
description: "今日 GitHub 熱門專案精選：<專案1>、<專案2>..."
publishDate: "YYYY-MM-DDT07:30:00+08:00"
tags: ["GitHub Trending", "open source", "工具"]
draft: false
---
```

### 寫法要求

走 **快節奏、濃縮精華型**：

1. **開頭直接破題**：一句話說明今天 GitHub Trending 的整體趨勢
2. **每個專案 2–3 段**：一句话介绍 + 核心技术点 + 适合谁
3. **用專案名稱當小節標題**
4. **結尾一句話**：點出今天趨勢的共通主題

---

## Step 6｜寫入選文記錄

寫檔後把這次選的專案登記到 log，確保未來 7 天內不會重複選到：

```bash
mkdir -p ~/ai-intel/github-trending-log
LOGFILE=~/ai-intel/github-trending-log/$(date +%Y-%m-%d).json
python3 - <<'PY'
import json, os
from datetime import datetime, timezone, timedelta

log_file = os.path.expanduser(f"~/ai-intel/github-trending-log/{datetime.now().strftime('%Y-%m-%d')}")+ ".json"
tz = timezone(timedelta(hours=8))
new_entry = {
  "timestamp": datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
  "repos": ["<repo1>", "<repo2>", ...],
}
try:
  with open(log_file) as f:
    data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
  data = {"date": datetime.now().strftime("%Y-%m-%d"), "selections": []}
data["selections"].append(new_entry)
with open(log_file, "w") as f:
  json.dump(data, f, ensure_ascii=False, indent=2)
print("logged:", new_entry["repos"])
PY
```

---

## Step 7｜交給 base 的 Pipeline

套用 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F。

---

## Light Issue 處理

若當日 GitHub Trending 完全沒有值得寫的專案，或所有候選都被過去 7 天過濾掉：

- `exit 1`

允許跳過。