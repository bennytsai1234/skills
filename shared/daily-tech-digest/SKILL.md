---
name: daily-tech-digest
description: 每天台北時間 10:00 與 15:00 各執行一次。從本地 RSS 資料挑一篇最值得深入研究的技術文章，寫成 800–1200 字的技術解析。繼承 _blog-publisher-base。第二篇執行時會自動跳過當天已選過的文章。
---

# daily-tech-digest（每日技術解析）

**發文時段**：每天 `10:00` 與 `15:00`（台北，cron 觸發兩次，同一個 skill 檔）
**定位**：挑一篇當天最值得深入寫的論文 / 工程部落格 / 開源專案，消化後用自己的話寫成 800–1200 字有觀點的技術解析。

風格規則、schema、L1–L4 自檢、發佈管線全部繼承 `_blog-publisher-base/SKILL.md`。

---

## Variant 變數

執行當下讀取目前時間（台北）來決定本次 slot：

```bash
HOUR=$(TZ=Asia/Taipei date +%H)
if [ "$HOUR" -lt "12" ]; then
  PUBLISH_HHMM="10:00"
else
  PUBLISH_HHMM="15:00"
fi
```

其餘變數：

```
SLOT_ID       = <動態 slug，見 Step 4>
COVER_TITLE   = <文章標題>
COVER_TAGS    = <從 tags 取前 3 個，逗號分隔>
COMMIT_PREFIX = docs: 技術解析
SERIES        = (空，非系列文)
```

---

## Step 1｜讀取今日 RSS 資料

```bash
cat ~/ai-intel/hourly/$(date +%Y-%m-%d).json
```

若檔案不存在或為空：

```bash
bash ~/ai-intel/scripts/fetch-rss.sh
```

再讀一次。仍為空 → `exit 1`。

---

## Step 2｜讀取今日已選清單（防重複）

這是 daily-tech-digest 特有的機制。一天兩個 slot（10:00 / 15:00）都寫「技術解析」，第二次執行時必須避開第一次已選過的文章，否則會重複發文。

```bash
LOGFILE=~/ai-intel/digest-selection-log/$(date +%Y-%m-%d).json
if [ -f "$LOGFILE" ]; then
  cat "$LOGFILE"
else
  echo '{"date":"'$(date +%Y-%m-%d)'","selections":[]}'
fi
```

把 `selections[]` 裡所有的 `url` 和 `title` 收集起來，Step 3 選題時自動跳過命中項。

---

## Step 3｜挑選最值得寫的文章

判斷標準：

- **原創性**：提出新穎技術思路或方法
- **實用性**：對開發者日常工作有直接幫助
- **深度**：不是新聞，而是有技術內涵的長文
- **多樣性**：避免重複前幾天的主題
- **防重複**：URL 不得出現在 Step 2 已選清單

優先來源：

- arXiv 論文（AI/ML/NLP/CV）
- 專家部落格（Lilian Weng、Simon Willison、Sebastian Raschka、Chip Huyen…）
- 公司工程部落格（Anthropic、Hugging Face、OpenAI Research…）
- GitHub Trending 有技術深度的專案
- 技術社群熱門討論

排除：

- 純商業新聞、融資公告
- 政治爭議
- 僅為產品發表的宣傳稿

從命中清單挑 1 篇進入 Step 4。

---

## Step 4｜研究文章

1. `web_fetch` 原始文章完整內容
2. `web_search` 找背景：「標題關鍵字 2026」或「作者 官方」
3. 若有 code / repo，fetch GitHub 頁面了解專案背景

整理出：

- 文章核心主張（1–2 句）
- 技術細節（關鍵數字、方法名、工具鏈）
- 產業 / 開發者影響

決定 slug（英文小寫、連字號）：

```
SLUG=$(date +%Y-%m-%d)-<英文 slug>
SLOT_ID=<英文 slug>      # 用於 base Pipeline
```

例：「Gemma 4 稠密 vs MoE 深度解析」→ `2026-04-12-gemma-4-dense-vs-moe`

---

## Step 5｜寫作

目標讀者：有基礎技術背景但不是該領域專家的工程師。800–1200 字。

### Frontmatter

```yaml
---
title: "【技術解析】具體標題"
description: "一句話描述文章核心價值"
publishDate: "YYYY-MM-DDTHH:MM:00+08:00"   # HH:MM = 10:00 或 15:00
updatedDate: "YYYY-MM-DDTHH:MM:00+08:00"   # 執行當下
tags: ["具體技術", "具體工具", "具體論文領域"]
draft: false
---
```

### 結構（可彈性調整，不一定要四個段都寫）

```markdown
## 這篇文章在說什麼

1–2 段，用自己的話解釋文章在做什麼。不抄原文。

## 為什麼重要

技術或方法的價值，對誰有幫助，解決了什麼問題。

## 技術細節

核心方法、關鍵工具、數據支撐。用普通話說清楚，不寫流水帳。

## 我的觀點

消化後的判斷，可正面可批評，要有觀點，不當樹洞。

## 參考連結

- [原文標題](URL)
- [相關論文或文件](URL)
```

嚴格遵守 base 的禁用詞清單、具體工具名原則、繁中純度規則。

---

## Step 6｜寫入選文記錄

寫檔前（或寫檔後、push 前皆可）把這次選的文章登記到 `digest-selection-log`，確保同一天的下一個 slot 不會重複選到：

```bash
mkdir -p ~/ai-intel/digest-selection-log
LOGFILE=~/ai-intel/digest-selection-log/$(date +%Y-%m-%d).json
python3 - <<'PY'
import json, os
from datetime import datetime, timezone, timedelta

log_file = os.path.expanduser(f"~/ai-intel/digest-selection-log/{datetime.now().strftime('%Y-%m-%d')}")+ ".json"
tz = timezone(timedelta(hours=8))
new_entry = {
  "timestamp": datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
  "title": "<填入文章標題>",
  "url": "<填入原始 URL>",
  "source": "<填入來源名稱，例如 arxiv.org / lilianweng.github.io>",
  "slug": "<填入 SLOT_ID>",
}
try:
  with open(log_file) as f:
    data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
  data = {"date": datetime.now().strftime("%Y-%m-%d"), "selections": []}
data["selections"].append(new_entry)
with open(log_file, "w") as f:
  json.dump(data, f, ensure_ascii=False, indent=2)
print("logged:", new_entry["title"])
PY
```

---

## Step 7｜交給 base 的 Pipeline

套用 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F。

輸出摘要：

```
daily-tech-digest 完成

日期：YYYY-MM-DD
slot：HH:MM (動態 10:00 或 15:00)
選文：[來源] 標題
URL：原始網址
防重複：已記錄至 ~/ai-intel/digest-selection-log/YYYY-MM-DD.json
字數：約 N 字
檔案：post/YYYY-MM-DD-[slug].md
封面：已生成 / 跳過
自檢：L1 ✅ / L2 ✅ / L3 ✅ / L4 ✅
build：通過
push：成功
```

---

## Light Issue 處理

找不到任何合適文章時：

- 若 RSS 中有「技術相關但深度不夠」的文章 → 寫短版（500–800 字），commit 加 `[light-issue]`
- 若完全沒有技術類文章（純新聞稿、純融資公告）→ `exit 1`

不允許無腦選一篇湊數。寧可觸發 failureAlert，也不發水文污染部落格。
