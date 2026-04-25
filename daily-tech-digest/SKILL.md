---
name: daily-tech-digest
description: 每天台北時間 10:00 與 15:00 各執行一次。從本地 RSS 資料挑一篇最值得深入研究的技術文章，寫成慢節奏、技術故事型的技術解析（1400–2200 字）。繼承 _blog-publisher-base。第二篇執行時會自動跳過當天已選過的文章。
---

# daily-tech-digest（每日技術解析）

**發文時段**：每天 `10:00` 與 `15:00`（台北，cron 觸發兩次，同一個 skill 檔）
**定位**：挑一篇當天最值得深入寫的論文 / 工程部落格 / 開源專案，用慢節奏、技術故事型的方式消化寫成 **1400–2200 字**，讓讀者像跟著作者一起把問題想明白，不是交作業。

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

最低研究要求，不可省略：

1. `web_fetch` 原始文章完整內容
2. `web_search` 找背景：「標題關鍵字 2026」或「作者 官方」
3. 若有 code / repo，fetch GitHub 頁面了解專案背景
4. 若是論文，至少補一個論文頁 / 作者頁 / benchmark 討論來源
5. 若是工程文章，至少補一個官方文件或產品頁

整理出：

- 文章核心主張（1–2 句）
- 技術細節（關鍵數字、方法名、工具鏈）
- 它跟既有做法差在哪裡
- 產業 / 開發者影響
- 哪個部分可能被高估或被低估

決定 slug（英文小寫、連字號）：

```
SLUG=$(date +%Y-%m-%d)-<英文 slug>
SLOT_ID=<英文 slug>      # 用於 base Pipeline
```

例：「Gemma 4 稠密 vs MoE 深度解析」→ `2026-04-12-gemma-4-dense-vs-moe`

---

## Step 5｜寫作

目標讀者：有基礎技術背景但不是該領域專家的工程師。**1400–2200 字**。

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

### 寫法要求（這次是重點）

這個 variant 預設走 **慢節奏、技術故事型**，不要再寫成教科書式摘要，也不要把文章拆成一排模板標題，像是「這篇文章在說什麼 / 背景脈絡 / 為什麼重要 / 技術細節」。那種寫法資訊可能完整，但閱讀體感很硬，像在交差。

請改用一條比較連續的敘事線去寫，讓讀者像是跟著作者一起把問題想明白：

1. 先從一個具體卡點、反直覺現象、舊方法的尷尬處境，或這篇文章真正想處理的麻煩開始。
2. 再慢慢帶出作者為什麼會往這個方向走，前面有哪些做法不夠好。
3. 中段才進入方法、模型、系統設計或實驗細節，但不要突然切成答題格式，要像故事推進時自然走到技術核心。
4. 後段再談它真正改變了什麼、代價在哪裡、哪些地方可能被高估。
5. 收尾要像一個寫完後的判斷，而不是心得模板。要讓人感覺「讀到這裡，我知道這件事到底值不值得在意了」。

### 結構規則

- **可以只有 3–5 個 `##` 小節**，甚至比原本更少，只要整體閱讀順。
- **禁止**把小節命名成過度模板化的標題，例如：
  - `## 這篇文章在說什麼`
  - `## 背景脈絡`
  - `## 為什麼重要`
  - `## 技術細節`
  - `## 我的觀點`
- 小節標題要像文章的一部分，能承接敘事，例如：
  - `## 問題不是模型不會推理，而是我們一直看錯地方`
  - `## 舊方法其實早就碰到牆，只是大家沒有明講`
  - `## 真正有意思的，不是它做到了，而是它怎麼繞過去`
- 若某篇真的適合幾乎不切小節，也可以，但**文末仍然必須保留 `## 參考連結`**。

### 節奏規則

- 允許鋪陳，**不要一上來三句話就把結論講光**。
- 每一段都要有往前推進的感覺，像在慢慢揭開問題，而不是把資料一塊一塊丟給讀者。
- 段落可以更長，但每段都要有內在重心，不能只是同義改寫。
- 優先使用「先讓人理解困境，再帶方法，再談影響」的順序，而不是固定答案卡格式。

### 內容底線

雖然要像故事，但不能變成散文。以下幾件事還是一定要清楚寫到，只是要自然融進敘事裡：

- 文章核心主張是什麼
- 舊做法卡在哪裡
- 新方法或新系統到底做了什麼
- 至少一個具體比較對象
- 至少一段清楚判斷它的價值與代價

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

- 若 RSS 中有「技術相關但深度不夠」的文章 → 寫短版（1000–1400 字），commit 加 `[light-issue]`
- 若完全沒有技術類文章（純新聞稿、純融資公告）→ `exit 1`

不允許無腦選一篇湊數。寧可觸發 failureAlert，也不發水文污染部落格。
