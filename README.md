# Skills

Canonical home for reusable Codex and agent skills. 每個 skill 一個目錄、內含 `SKILL.md`；`~/.codex/skills/` 與 `~/.claude/skills/` 用 symlink／junction 指回這個 repo。只有被連結的 skill 會被 agent 載入。

## 分組與掛載

| 組別 | Skill | 掛載 |
|---|---|---|
| 通用 | `atlas-planner`、`atlas-relay`、`atlas-worker`、`project-foundation`、`handoff`、`summarize-project-work`、`bro`、`compass`、`engineering-judgment` | 兩台都掛 |
| 公司限定 | `cota`、`gpu-hosts`、`dev-flow`、`codex-update`、`cua-runtime-repair` | 只掛公司；GPU 主機從家裡連不到，其餘是公司規範與公司網路環境 |
| 封存 | `video-to-text`、`codex-wsl-terminal-repair`、`hermes-ops`、`openclaw-ops`、`mmx-cli`、`windows-cjk-font-substitution` | 兩台都不掛。原本是家裡用的，已經很少用，先保留內容；要用時再臨時掛回去。腳本裡寫死的 `/home/benny/skills/...` 路徑沒改，所以目錄不搬 |

| 機器 | `~/.codex/skills/` | `~/.claude/skills/` |
|---|---|---|
| 公司 | 通用 + 公司限定 | atlas×3、`project-foundation`、`handoff`、`summarize-project-work`、`cota`、`gpu-hosts`、`dev-flow` |
| 家裡 | 通用 | atlas×3、`project-foundation`、`handoff`、`summarize-project-work` |

### 回家同步

```bash
cd ~/skills && git pull
CODEX=~/.codex/skills; CLAUDE=~/.claude/skills   # 依家裡實際位置調整
# 拿掉已刪除、封存、公司限定的連結（只刪連結，真的目錄 rm -f 刪不掉，會報錯略過）
for n in blueprint video-to-text codex-wsl-terminal-repair hermes-ops openclaw-ops mmx-cli \
         windows-cjk-font-substitution cota gpu-hosts dev-flow codex-update cua-runtime-repair; do
  rm -f "$CODEX/$n" "$CLAUDE/$n"
done
for n in atlas-planner atlas-relay atlas-worker project-foundation handoff summarize-project-work bro compass engineering-judgment; do
  ln -sfn ~/skills/$n "$CODEX/$n"
done
for n in atlas-planner atlas-relay atlas-worker project-foundation handoff summarize-project-work; do
  ln -sfn ~/skills/$n "$CLAUDE/$n"
done
```

上面是 Linux／WSL 的寫法。Windows 的 Git Bash 執行 `ln -s` 會變成複製，所以 Windows 要用 PowerShell：`New-Item -ItemType SymbolicLink -Path "$HOME\.codex\skills\<name>" -Target "$HOME\skills\<name>"`（需要開發人員模式或系統管理員權限）。刪除 junction 用 `[System.IO.Directory]::Delete("<連結路徑>", $false)`，只會刪掉連結本身，不碰目標目錄。

## 2026-10-02 盤點與調整紀錄

依據：掃公司電腦的 Claude（09-02 起）與 Codex（06-22 起）對話紀錄，計算實際叫用或讀取 `SKILL.md` 的 session 數，不含在本 repo 修改 skill 本身的 session；再對照全域 AGENTS.md 逐一審查。

| Skill | 公司使用量（Codex / Claude） | 處理 |
|---|---|---|
| `cota` | 2 / 17 | 原本在 `SKILL.md` 裡的 PermProvider 1.0.5 公告，內容 `references/perm-provider.md` 都已涵蓋，所以本體改成一段串接前指引，只保留三個錯了也不會報錯的陷阱 |
| `gpu-hosts` | 3 / 14 | 不變 |
| `project-foundation` | 3 / 2 | 不變 |
| `atlas-planner` | 0 / 4 | 刪掉 5 處對已移除 codebase-atlas 的引用；`delegation.md` 角色表改成「明確說 planner 才進 Planner」，和觸發規則一致 |
| `atlas-worker`、`atlas-relay` | dispatch 5 / 9、1 / 0 | 不變（共用 contract 的修正見上一列） |
| `dev-flow` | 5 / 0（全在 08-27） | 濃縮：申請狀態規則只寫一次並以 `cota` 為準，偏航改成表格；階段、AA 檢查項與輸出不變 |
| `engineering-judgment` | 2 / 1 | 觸發條件收窄：只有明確要求「教我判斷」時才用；一般的 A／B 選擇照全域規則直接給推薦 |
| `compass` + `blueprint` | 各 1 / 0 | 合併成 `compass`，分成「校正」與「收斂成方案」兩個模式；`blueprint` 刪除 |
| `bro` | 1 / 2 | Codex 補上 `allow_implicit_invocation: false`，和 Claude 端一樣只能手動叫用 |
| `codex-update` | 1 / 0 | 腳本佔位路徑改成實際位置 |
| `cua-runtime-repair` | 2 / 0 | 原本只放在公司的 `~/.codex/skills/`，現在搬進 repo，再連結回去 |
| `summarize-project-work` | 0 / 1 | 拿掉已移除的 `trace_path`；`--stat` 只看候選任務的提交範圍，不一次展開全部歷史 |
| `handoff` | 0 / 0（10-01 新增） | 不變 |
| 封存組 6 個 | 0 / 0 | 拿掉公司 Codex 上的連結，內容保留 |

不由本 repo 管理：Codex 內建的 `~/.codex/skills/.system/`（`imagegen`、`openai-docs`、`review-agent`、`skill-creator`、`skill-installer`）。

## Atlas development workflow

- `atlas-planner` — formal planning path: investigate and discuss with the human until problem/root cause/target/solution are explicitly confirmed, then write detailed `atlas/v4` packages and one dispatch plan. Only on explicit request.
- `atlas-relay` — execute a confirmed dispatch plan sequentially, route workers, independently accept results, record completion, and deliver the batch.
- `atlas-worker` — implement one detailed worker package and return real verification evidence.

## Repository foundation and environments

- `project-foundation` — 整理／清理專案：精簡頂層、部署檔放 `deploy/<target>/`、`AGENTS.md` 作為唯一代理指南、實驗區規則（run 命名、版本登記、每次 run 的筆記），以及清掉主機上沒在用的 image tag、container 與權重。
- `gpu-hosts` —（公司限定）RTX 4090／H200 主機的連線資訊與操作指引，只在跟主機有關的任務才載入。
- `dev-flow` —（公司限定）明確呼叫時，唯讀診斷公司專案是否偏離本機／AA／公司服務整合的標準開發路線。
- `cota` —（公司限定）Cota 內部 .NET 開發標準、CotaUtility 套件、平台規範與流程。
- `codex-update` —（公司限定）在公司管控的 Windows 上更新或診斷 Codex CLI 與桌面版。
- `cua-runtime-repair` —（公司限定）修 Windows Codex CUA runtime 的套件解析失敗。

## Other skills

- `bro` — 把上一則訊息改寫成白話（只能手動叫用）
- `compass` — 校正偏掉的對話，或把已確認內容收斂成最小充分方案
- `engineering-judgment` — 明確要求時，教你身為工程師如何做技術取捨
- `handoff` — 整理目前對話成已遮蔽敏感資料的代理交接文件
- `summarize-project-work` — 依程式碼與 Git 紀錄整理會報式工作摘要

## Archived（保留但不掛載）

- `codex-wsl-terminal-repair` — 修 Codex 桌面版在 WSL／PowerShell 下的內建終端機
- `hermes-ops` — 操作 Hermes Agent 本身（版本、更新、doctor、token 設定）
- `mmx-cli` — 用 MiniMax `mmx` 生成文字、圖片、影片、語音、音樂
- `openclaw-ops` — 操作 OpenClaw 本身（版本、更新、gateway 服務、健康檢查）
- `video-to-text` — YouTube 影片轉帶時間戳的繁中逐字稿
- `windows-cjk-font-substitution` — 調整 Windows 中日韓字型替代（Noto → 更紗黑體）

## Structure

Each skill lives in its own directory with `SKILL.md`. Keep reusable references, scripts, assets, and `agents/openai.yaml` inside the owning skill. Prefer concise `SKILL.md` control planes and load detailed references only when the task needs them.
