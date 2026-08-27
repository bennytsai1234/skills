---
name: dev-flow
description: 依專案程式碼、設定、Git、測試與外部資源狀態，判斷目前開發階段、可信基線、卡點、下一步與可並行工作。適用於本機開發、AA + Redis、Cota 分階段接入與整合混亂的既有專案。只做唯讀流程判斷，不執行修改、部署或申請。
---

# Dev Flow

## 核心原則

- 只依可查證證據判斷，不靠對話印象或設定名稱推定完成。
- 分開標記：**已確認／尚未確認／卡點**。
- 正式目標未另行指定時，預設 **AA + Redis**。
- 本機成功、Cota 成功、AA 成功是不同結論。
- 外部資源等待期間，本機開發與申請可並行。
- 找出「最後一個可信且已驗證的狀態」，再決定前進或回退。
- 不為了最佳實務主動重構；只處理目前會阻塞或造成錯誤的問題。

## 開發流程

```text
需求
↓
Local Baseline
↓
Local Functional
↓
Local AA Verification
↓
Cota Integration
↓
Company AA Verification
↓
Release
↓
Production
```

### Local Baseline

預設使用：

```text
單 Web
+ 本地 DB / LocalDB
+ Docker Redis
+ Fake / Local Identity
+ Local / Simulator 外部服務
```

要求：

- 沒有公司網路也能 build、啟動與測試。
- 公司 endpoint、帳號、憑證不能是本機啟動必要條件。
- 業務邏輯與 Cota implementation 有明確邊界。
- 本地替代物只負責本地驗證，不把本地通過誤報為 Cota 通過。

### Local Functional

先完成業務流程、資料契約、設定邊界、核心測試與必要 migration。業務程式依賴介面或 adapter boundary；本機使用 local implementation，後續才替換為 Cota implementation，不因切換環境重寫業務流程。

### Local AA Verification

本機功能穩定後才測：

```text
Web A + Web B
      ↓
共用 Redis + DB
```

依專案實際功能檢查：

- Session / cache
- 跨 process state
- worker / scheduler 是否重複
- distributed lock / lease
- Data Protection
- SignalR
- 共用檔案
- restart / recovery

本機雙 Web 通過不代表公司 AA 已通過。

### Cota Integration

一次只接一層：

```text
Local DB → CotaDB
Docker Redis → CotaRedis
Identity / Permission
External Service
Monitoring / HA
```

每層都確認：

- 公司資源是否已取得。
- 本機是否仍可執行。
- 是否有實際驗證證據。
- 是否有明確回退點。

某層失敗就退回上一個已通過狀態，不把多層半成品一起繼續往前推。若 CotaRedis 或公司 DB 依賴內部資源且尚未取得，不要用 Docker Redis 或 LocalDB 的成功代替公司整合證據。

## 狀態異常

### BLOCKED

公司 DB、Redis、帳號、權限、憑證或網路尚未取得。

→ 保持 Local Baseline／Local Functional 繼續開發，申請流程與依賴盤點並行。

### MIXED

Local 與 Cota 混在一起，已無法判斷錯誤來源，或專案未按 AA + Redis 建立可信基線。

→ 停止繼續整合，回到 Local Baseline。

### INTEGRATION FAILED

某一層 Cota 整合失敗。

→ 退回上一個成功層，只處理該整合，不同時引入其他 Cota 變更。

### AA FAILED

單 Web 正常，但雙 Web 出現狀態、worker、lock、session、檔案或 recovery 問題。

→ 回到 Local AA Verification 修正，不重寫業務功能；先處理共享狀態、執行責任與 infrastructure boundary。

## Recover to Local

既有專案整合混亂時：

1. 保留目前 commit、設定、錯誤與套件證據，建立可回復點。
2. 先移除或隔離本機啟動路徑中的 Cota package、DI registration、middleware、公司 endpoint 與強制初始化；保留業務介面、資料契約與 adapter boundary。
3. 恢復：
   `單 Web + Local DB + Docker Redis + Local/Fake Service`
4. 通過 build、啟動、核心功能、測試與必要 migration。
5. 再測 Local AA。
6. 最後逐層接回 Cota。

目的是恢復可驗證性，不是刪除業務功能或全面重寫。若直接移除 Cota package 會造成編譯失敗，先隔離成可選的 infrastructure project／profile，再恢復本機建置。

## 判斷流程

執行本 Skill 時：

1. 找出最後可信狀態。
2. 判斷目前屬於正常前進、BLOCKED、MIXED、INTEGRATION FAILED 或 AA FAILED。
3. 找出真正卡點，區分資源等待、環境差異、程式問題與驗證不足。
4. 只提出下一個最小可驗收動作。
5. 列出可以並行的工作，例如本機功能開發、AA 設計盤點、測試資料準備與 Cota 資源申請。
6. 若使用者想跳步，說明缺少的驗證與實際風險。

## 輸出

預設只回答：

- **目前階段**
- **已確認**
- **卡點／尚未確認**
- **下一步**
- **可並行**
- **跳步代價**

不要每次重新講完整流程。

## Cota

涉及 CotaUtility、CotaRedis、CotaDB、入口網、權限、監控或公司申請流程時，查 `cota` skill 對應 reference，不在此 Skill 重複平台規格。
