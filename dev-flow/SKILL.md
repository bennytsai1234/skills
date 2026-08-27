---
name: dev-flow
description: 依專案證據規劃本地先行開發、Cota 分階段接入與正式 AA + Redis 驗證，區分本機單 Web、雙 Web 整合和公司資源驗收；狀態混亂時先回復本地基線，再逐層接回 Cota；只做唯讀分析，不修改、部署或送申請。
---

# Dev Flow

## 目的

依專案目前的程式碼、設定、文件、Git 歷史、測試、部署資料與外部流程狀態，判斷目前在哪個階段、下一步該做什麼、卡在哪裡，以及哪些工作可以並行。這個 skill 是流程判斷與唯讀盤點，不是實作、部署或申請的授權。

## 核心原則

- 以可查證的專案證據為準（git 歷史、文件、腳本、設定檔、申請單狀態），不以對話印象、主機名稱、申請單草稿或單次成功啟動推定架構已完成。讀取足以支持判斷的證據即可，不足再擴大檢查。
- 分開記錄「已確認」「合理推定」「尚未確認」。完整盤點已證實的缺口時，列為待修正；只有尚未查到或工具未完成時才列為無法確認。
- 步驟代表階段，不代表單向前進：需求探索 ↔ 本機開發 ↔ 本機測試可以反覆；接 Cota 資源 → 發現差異 → 改程式 → 再測是正常循環。
- 分開判斷請求層高可用與背景工作的執行模型。兩台 Web 能同時收 request，不代表兩台都能安全執行同一個 queue、排程或 recovery worker。
- 正式部署目標未另行指定時，預設採 **AA + Redis**。若使用者明確改為 AP 或單機，才依該決策調整；本機單節點測試不等於 AA 已驗證。
- 申請單等外部流程有等待成本，能提早準備就提早準備；但申請狀態不等於資源已可用或架構已驗證。
- 跳步不禁止，但說明少了哪個驗證、可能留下什麼風險，由使用者決定。

## 本地先行邊界

本地先行代表先用可重建的本地資源完成業務流程、資料契約、設定邊界與測試基線，不代表延後盤點 Cota 依賴。Cota 資源申請、套件來源、目標 framework、帳號與網路需求可以並行準備；實際接入則等本機基線可驗收後分層進行。

- 本機日常開發：單一 Web process + 本地 DB／LocalDB + Docker Redis；依功能使用 fake identity、seed permission、local file、Console／File log 或 simulator。
- Cota 公司整合：依專案實際功能逐層替換本地替代物；涉及 `svrdb + SSPI`、CotaRedis、公司入口／權限、內部外部服務或監控的結果，才可作為 Cota 驗證證據。
- 本機替代物與 Cota adapter 要有清楚邊界。公司專用 endpoint、帳號、憑證與套件不可成為本機啟動的無條件前置；本機 profile 應能在沒有公司網路時建置、啟動與測試。
- 「本機通過」「Cota 接入通過」「測試環境 AA 通過」「正式 AA + Redis 通過」是四種不同結論，不可合併回報。

## 狀態混亂時的回復路徑

若出現本機與公司設定混用、Cota 套件版本／API 不明、啟動時強制連公司資源、無法判斷錯誤來源，或目前無法說明哪些功能依賴 Cota，先停止繼續接套件與環境設定，將工作拉回本地基線：

1. **保留現況證據**：記錄目前 commit、套件清單、啟動錯誤、設定 profile、Cota 註冊點與已知可用狀態；先建立可回復點，不刪除使用者既有的無關修改。
2. **移除或隔離 Cota 依賴**：從本機啟動路徑移除 Cota package reference、DI registration、middleware、公司 endpoint 與強制初始化；保留業務介面、資料契約與可供日後接回的 adapter boundary。若直接移除會破壞編譯，先隔離成可選的 infrastructure project／profile，再恢復本機建置。
3. **恢復本地可執行基線**：回到單 Web + 本地 DB／LocalDB + Docker Redis，使用本地 auth／permission／external service substitute，先通過 build、啟動、核心測試與必要 migration。
4. **重新建立分散式基線**：本地單 Web 穩定後，才用 Web A + Web B 共用本地 Redis／DB 驗證跨 process、lock／lease、共享狀態與 worker 唯一性。
5. **逐層接回 Cota**：依「套件／邊界 → DB／Redis → 身分／權限 → 外部服務 → 監控／HA」順序，一次只引入一層並記錄通過條件；任何一層讓本機或測試失去可驗證性，就回到上一個通過點，不把多層變更混在一起。

這條路徑是整理依賴與恢復可驗證性，不是刪除業務功能，也不是把正式目標改成單機；正式目標仍維持 AA + Redis。

## 目標拓撲與共享狀態

正式目標預設為 AA（Active/Active，兩台同時服務）+ Redis。判斷時仍要確認實際節點、流量路由、Redis 角色與測試證據，不以設定中的 `AA=true`、主機名稱或申請文字代替實機驗證。

先盤點 AA 需要共享或協調的狀態：

- Session、cache、presence、connection metadata、SignalR 跨節點訊息；
- in-memory queue、取消登記、排程、recovery 與背景 worker 的唯一執行權；
- Data Protection key ring、憑證與其他跨節點解密資料；
- 上傳圖檔、報表或其他本機檔案產物；
- DB migration 的執行責任與併發方式；
- Redis 的 lock、lease、pub/sub 與多 key 原子操作。

若目標是 Redis Cluster，額外確認多 key 操作會落在同一 hash slot；本機 standalone Redis 通過，不代表 Cluster 不會發生 `CROSSSLOT`。

## 10 個階段

1. **需求探索／迭代**：先確認業務目標、資料契約與正式 AA + Redis 目標；做出可操作版本後邊看效果邊修改，需求逐步收斂。
2. **Cota 依賴盤點／資源並行準備**：列出實際會用到的 DB、Redis、身分、權限、外部服務、憑證、監控與套件來源；可提早申請公司資源，但不讓等待中的 Cota 資源阻塞本機開發，也不把申請狀態當成可用證據。
3. **本機架構骨架**：先建立本地 profile、adapter／interface、資料模型、migration 責任與測試替代物；確認沒有公司 endpoint、帳號或 Cota 初始化才能啟動的硬依賴。
4. **本機最小化開發**：以單 Web process + 本地 DB／LocalDB + Docker Redis 完成功能迭代；所有 endpoint、帳號與環境差異走設定，不寫死本機或公司連線。
5. **本機多節點整合測試**：本機單 Web 與核心測試穩定後，才以 Web A + Web B、同一個本地 Redis、同一個本地 DB、兩個獨立 process 測試跨程序狀態。這是 AA 行為的本地模擬，不是公司 AA 證據。
6. **本機基線驗收／必要時回復**：確認 build、啟動、核心測試、migration、重啟與必要的本機雙 Web檢查；若狀態混亂，依回復路徑移除或隔離 Cota，回到此階段重新建立基線。
7. **Cota 分階段接入**：本機基線通過後，依下方接入順序一次引入一層；每層都要有本機影響、公司資源、驗收證據與回退點，發現環境差異就回到上一個通過階段。
8. **測試環境部署／實際 AA 驗證**：將已接入的版本部署到實際測試節點，確認兩個節點、流量路由、Cota DB／Redis、帳號權限與健康檢查；具備實機證據後才宣稱 AA 行為通過。
9. **完整回歸／上線申請／版本凍結**：驗證功能、資料、Redis、身分權限、共享狀態、背景工作唯一性、重啟／故障切換、監控與回復方案，再整理正式版 commit／tag、部署文件與異動內容。
10. **正式上線**：依 AA + Redis 拓撲部署節點、接正式資源、執行 smoke test、清理測試設定並保留可追溯的最終版本。

核心路徑是：需求收斂 → Cota 依賴盤點（可並行申請）→ 本機架構與單 Web 開發 → 本機基線驗收 → 必要時本機雙 Web → Cota 分層接入 → 測試環境實機 AA → 完整回歸 → 上線。

## Cota 分階段接入

只接入專案實際需要的模組，不因「公司標準」一次加入所有 Cota package。每一層都先確認本機是否仍可建置與啟動，再確認公司資源與跨節點行為。

| 接入層 | 接入時機與內容 | 本機替代／限制 | 通過條件 |
|---|---|---|---|
| 套件與邊界 | 確認 target framework、NuGet 來源、package 版本、adapter／DI 邊界 | local profile 不依賴公司 feed、endpoint 或帳號；公司 package restore 可能需要內網或快取 | 本機可 restore、build、啟動；Cota 依賴點可逐項列出 |
| DB／Redis 基礎 | 本機資料契約與 migration 穩定後，再接 Cota DB／Redis | 本地 DB／LocalDB + Docker Redis 只驗證應用邏輯；CotaRedis 若無 local fallback，不可假裝指向 Docker | 實際連線、認證、session／cache／pub-sub／lock／lease 與 migration 責任有證據 |
| 身分／權限 | 核心流程穩定後，接入口網、WebAuth、Keycloak、permission、employee 等實際用到的整合 | fake identity、seed role、local Keycloak 或 simulator 可支援本機；不代表公司登入或權限已通 | claims、角色、權限、員工資料與失敗處理在目標環境通過 |
| 外部服務 | 功能需要且內部流程已可測後，接 Java／主機呼叫、通知、Customer、簽章等服務 | local simulator、no-op／outbox、fixture 或 deterministic mapping；不可讓公司服務成為本機必需 | endpoint、服務帳號、TLS／簽章、timeout、錯誤與重試行為有測試證據 |
| 監控／HA | Cota 功能接入後，接 Redis log、HealthCheck、看板、HAProxy、共享檔案、DP keys 與 worker 協調 | 本機可用 Console／File log、local health endpoint、reverse proxy；不能證明公司監控或正式故障切換 | 兩節點路由、共享狀態、背景工作唯一性、重啟／故障切換與告警均完成驗收 |

若某一層無法取得公司資源，保留該層為「待接入／待驗證」，先完成不依賴它的本機工作；不要用本機替代物把該層標成 Cota 通過。

## 本機配置怎麼判斷

| 目的 | 合理配置 | 可以證明 | 不能證明 |
|---|---|---|---|
| 日常功能開發 | Web A + 本地 Redis + 本地 DB／LocalDB | 業務邏輯、資料存取與設定邊界 | 跨節點狀態、HAProxy、公司權限與故障切換 |
| 分散式整合 | Web A + Web B + 共用本地 Redis + 共用本地 DB | A 寫 B 讀、跨程序狀態、重複 worker、lock／lease、路由與重啟行為 | 公司 Redis／MSSQL、網路、服務帳號、正式拓撲 |
| 測試環境驗收 | 實際測試節點 + 測試 DB／Redis／路由 | 部署相容性、權限、真實連線與 AA 行為 | 正式上線本身，仍需正式 smoke test |

Redis 通常適合用 Docker 維持可重建的本地環境。MSSQL 用 Docker 或 LocalDB 依驗證目的選擇：需要貼近 SQL Server 版本、Provider、權限或 migration 行為時偏向 Docker；只做快速功能迭代且另有 SQL Server 驗證時，LocalDB 可以接受。這個選擇本身不代表已完成或未完成 HA。

雙 Web 本機整合至少檢查：A 寫入的資料或狀態能否由 B 讀取、請求分流後 Session／cache 是否一致、背景工作是否重複執行、lock／lease 是否跨 process、SignalR 或連線命令是否能路由、Data Protection key 是否共用、檔案是否可由接手節點取得，以及重啟後狀態能否恢復。依專案實際使用的功能取用，不要為沒有的功能硬加驗證項。

## 判斷方式

1. 讀取足以支持判斷的專案證據，定位目前階段。
2. 先定位正式目標拓撲與本機配置的用途，再對照目前已實作的共享狀態、執行責任與驗收證據。
3. 回報目前階段、證據、卡點／缺口、下一步、可並行工作與跳步代價；將觀察結果和結論分開。
4. 不執行修改、部署或送申請；沒有證據的項目標為尚未確認，不用摘要或 timeout 直接判定成功或失敗。

## 輸出格式

- **目前階段**：依哪些證據判定。
- **已確認**：已完成的實際條件。
- **卡點／尚未確認**：缺少的證據、資源或決策。
- **下一步**：最小可驗收動作。
- **可並行**：不依賴卡點即可先做的工作。
- **跳步代價**：若適用，說明未做哪個驗證與留下的風險。

預設只回答上述項目；只有使用者要求盤點時才輸出完整 checklist。

## Cota 專案

Cota 專案遇到公司環境、DB、Redis、AA、Git、申請流程或監控細節時，查 `cota` skill 的相關 reference，不在本 skill 重複平台規格。此 skills repo 的 reference 目前位於 `C:\Users\045650\skills\cota\references\`；優先依情境讀取 `new-project-flow.md`、`cota-redis.md`、`cota-db.md`、`web-platform.md` 或 `git-workflow.md`。
