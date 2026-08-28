---
name: cota
description: "三信商業銀行(Cota Bank)內部 .NET 開發標準與流程——CotaUtility 各 NuGet 模組(資料庫/Redis/Log/健康檢查/簽章驗證/主機呼叫/權限/報表/驗證登入/員工入口網串接)、內部平台標準(svrdb+SSPI 連線、入口網簽章、Session Timeout、HAProxy、HSTS)、行動入口網專案標準、開發環境準備、開發/上線申請流程、Git 版本控制與程式抄送/異動單、資訊看板監控。新專案開發時決定該裝哪些套件與該走哪些標準;既有專案維護、或使用者要求「健檢」「找出該替換成 CotaUtility 的地方」時,用來掃描程式碼;使用者問開發環境、上線流程、抄送/分支、監控告警時查對應 reference。"
---

# Cota 內部開發標準與流程

使用者在三信商業銀行(Cota Bank)內部。本 skill 涵蓋公司內部 .NET 開發的**標準做法**
與**流程**:CotaUtility 各 NuGet 模組、平台層標準(連線字串、入口網簽章、Session
Timeout、HAProxy)、開發環境準備、開發/上線申請、資訊看板監控。

**基本立場:內部專案預設符合公司標準。** 對內部專案而言,本 skill 裡的標準就是公司
標準做法——**預設要用,偏離才需要理由**。掃描既有專案時,視角是「找出偏離標準的地方」,
不是「評估要不要導入」。

- **內部專案**(預設):每個功能領域,專案有這個功能卻沒走公司標準的,列為「偏離標準,
  應修正」;專案沒有這個功能的,依「適用情境」判斷是否需要,需要才建議導入。
- **DMZ / 對外專案**:部分模組有對外版本或限制(例如 CotaRedis 的
  `RedisEnvironment.Dmz`),仍預設走公司標準,但注意各 reference 檔標示的環境差異。
- **例外**:某功能用公司標準確實不適用(Framework 裝不了、套件文件標示未完成、
  或專案性質上沒有該需求)時,才維持現狀,並說明理由。

**不要**用「這是業界標準做法,是否統一改用屬公司政策決定」這類外部評估者的措辭——
在公司內部,這些就是公司標準,不是待商議的政策選項。

**不涵蓋分行系統(Br 前綴專案)專用的 CotaUtility.BrXXX 套件家族**(BrApiHelper、BrMvc、
BrHoliday、BrPILog 等)——那是另一套完全不同的三層式架構規範(中台路由、AIX 主機整合),
跟這裡的通用模組是兩回事。偵測到專案是 Br 前綴 / 有中台路由架構時,提醒使用者那是另一個
體系,不要套用本 skill 的規則。

## 內容地圖

### CotaUtility 模組(NuGet 套件)

CotaUtility 原本是單一套件,已於 2023.12.01 停止更新(EOS),拆成多個獨立 NuGet 套件,
各自獨立維護、獨立版號。

| 功能領域 | 套件 | Framework 限制 | 詳細規則 |
|---|---|---|---|
| 原生風格 DB 存取(MSSQL) | CotaUtility.CotaDB | netstandard2.0(通用) | `references/cota-db.md` |
| Dapper 風格 DB 存取(MSSQL) | CotaUtility.CotaDapper | .NET Core only,**文件標示未完成** | `references/cota-dapper.md` |
| 分行系統 MySQL 存取 | CotaUtility.SecureMySql | .NET 5/6/7/8,Windows x64/x86 | `references/secure-mysql.md` |
| Redis 分散式 Cache / Session / PubSub | CotaUtility.CotaRedis | netstandard2.0 | `references/cota-redis.md` |
| 結構化 Log(寫入 Redis,Seq 查詢) | CotaUtility.CotaRedisLog(.Serilog / .NLog) | netstandard2.0 | `references/cota-redis-log.md` |
| 來源 IP 檢查 / COBOL↔Web 簽章驗證 / 入口網 hiseed 簽章 / HAProxy ClientIP | CotaUtility.Network | netstandard2.1 | `references/network.md` |
| 呼叫 COBOL/Java 主機(含 Big5 轉碼) | CotaUtility.JavaCall | netstandard2.0 | `references/java-call.md` |
| CotaInfo 內部通知訊息 | CotaUtility.CotaNotification | netstandard2.0 | `references/notification.md` |
| 專案監控資訊 / 健康檢查端點 / 資訊看板[專案監控]警告(推播+語音) | CotaUtility.CotaPerformanceCounter / CotaHealthCheckCore | netstandard2.0 / netcoreapp3.1+ (HealthCheckCore 僅限 .NET Core Web) | `references/performance-counter-healthcheck.md` |
| AD / OTP / FIDO2 生物辨識驗證 | CotaUtility.CotaWebAuth | v1.0.0=.NET5,v2.0.0+=.NET8 | `references/web-auth.md` |
| Keycloak OIDC 登入 / JWT 授權 / 下游 Token 轉拋 | CotaUtility.KeycloakAdapter | .NET 6/7/8 | `references/keycloak-adapter.md` |
| 員工入口網串接(進站驗證 / 回入口網,JWT 版) | CotaUtility.CotaPortal | net8.0 | `references/cota-portal.md` |
| 客戶統一編號遮罩 / 亂數化 / 統編證號驗證演算法 | CotaUtility.Customer | .NET Framework 4.7.2+ / .NET Core | `references/customer.md` |
| 集中權限/角色查詢與權限管理流程 | CotaUtility.PermProvider（本次公告含 1.0.5） | .NET Framework 4.6.1+ / .NET Core 2.0+ | `references/perm-provider.md` |
| 員工人事資料 / svremp 權限等級查詢 | CotaEmployee(命名空間 CotaUtility.Models) | .NET Framework 4.8 / .NET Core(套件拆分狀態待確認) | `references/cota-employee.md` |
| 網頁呼叫本機 32-bit DLL / 啟動桌面程式(用戶端服務) | CotaXMaster(用戶端 Windows 服務,非 NuGet) | 用戶端 Windows | `references/cota-xmaster.md` |
| 網頁轉 PDF 報表(含浮水印) | CotaUtility.Reporting | 未特別限制,依 wkhtmltopdf/puppeteer 執行環境 | `references/reporting.md` |

### 平台層標準與流程(非 NuGet 模組)

| 主題 | 內容 | 詳細規則 |
|---|---|---|
| 新專案標準開發流程(端到端) | 雙環境抄送(dev=測試/master=正式)、開發+上線兩次申請、前台雙機高可用為預設(AA 與 AP 主備皆為公司支援的擺法,由專案選,非硬性規定)→多機時 Redis 變標配、背景服務不可無腦雙跑、抄送/異動單、監控看板、開案檢查清單 | `references/new-project-flow.md` |
| 內部 MSSQL 連線標準 | svrdb + SSPI 整合驗證是標準;SQL 帳號連線字串列為偏離 | `references/cota-db.md` |
| 入口網簽章 / Session Timeout / HAProxy | hiseed/hisignedhash 驗證(舊機制;新專案優先用 CotaPortal,見 `references/cota-portal.md`)、20 分鐘 timeout、6 秒倒數、HAProxy 命名與環境 IP | `references/network.md` |
| 行動入口網專案標準 | SvrMobile 主機群、zta hostname、RWD、覆核生物辨識、CotaRedisSession Cookie.Name、HSTS、回入口網(RSASign 舊機制 / CotaPortal JWT 新機制) | `references/mobile-web.md` |
| .NET 8 平台設定 / 開發環境 / 上線申請 | Web.config 等效寫法、NAS 工具包、Checkmarx、IIS 憑證、開發與上線分開申請、上線申請單完整欄位(逐欄填寫)、HSTS 標準 | `references/web-platform.md` |
| 版本控制 / 抄送 / 異動單 | Gogs 倉庫、master=正式/dev=測試抄送、避免漏選檔案、風險評估表與測試報告、緊急抄送 | `references/git-workflow.md` |
| NuGet 私有來源 | CotaNuGet 設定(`\\192.168.251.238\data\CotaNuGet`)、開發環境 proxy | `references/nuget-setup.md` |

### 權限管理系統近期更新（CotaUtility.PermProvider 1.0.5）

- 專案異動流程現在只需「設計組長」核可，不再需要「管理組長」核可。
- 權限管理系統新增法遵主管指派規則；指派規則也可以排除特定單位，例如「所有單位，但不包含 XX 部」。
- 角色若指派給特定人員，該人員調離單位或離職時通知指派人員；專案成員若指派給特定人員，則通知專案管理人。
- 套件 1.0.5 新增同步查詢方法，.NET Framework 專案遇到非同步呼叫卡住時可改用同步方法；反查角色/權限的人員清單可用 `PermFilter.DpCode` 或 `PermFilter.Branch` 依單位過濾。
- 後台流程、指派規則與異動通知是權限管理系統的控制鏈；Client reference 只記錄串接時要核對的行為與查詢 API，完整方法與過濾語義見 `references/perm-provider.md`。

### 舊版 / 未拆分模組(掃描時遇到要特別處理)

以下模組出自舊版單體 `CotaUtility`(2023.12.01 EOS)時期,沒有拆分後獨立維護的
套件文件。掃描到專案在用時,**不要**直接建議「升級到拆分後套件」(沒有拆分後套件),
也不要因為找不到對應 reference 就漏報:

- **CotaJWT**(pageId 64127126):JWT 簽發/驗證,只提供 HS256。1.0.0.6 起
  Encrypt/Decrypt 回傳 `(bool, string)`。新專案需要 JWT 時優先評估
  `CotaUtility.KeycloakAdapter`(見 `references/keycloak-adapter.md`)或框架內建
  `AddJwtBearer`,CotaJWT 僅供既有專案維護參考。
- **CotaNLog**(pageId 64127047):舊版 NLog 整合,已被
  `CotaUtility.CotaRedisLog.NLog` 取代(見 `references/cota-redis-log.md`)。
- **CotaNetwork(已過時)**(pageId 64127130):已被 `CotaUtility.Network` 取代
  (見 `references/network.md`)。
- **CoraRedisLog.Core**(pageId 98763065):CotaRedisLog 的核心功能套件,
  一般專案不直接引用,由 `.Serilog`/`.NLog` 套件帶入。

## 使用情境

### 情境 A:新專案開發

使用者開新專案、或問「這個新專案該裝哪些套件 / 該走哪些標準」時:

0. **先給端到端骨架**:內部新專案**預設走完整流程**——雙環境抄送(dev=測試/
   master=正式)、開發+上線兩次申請、**前台雙機高可用為預設**、因而多機時
   Redis(Session/Cache)成為標配、接監控看板。這是預設姿態,不是逐項問「要不要導入」;
   要精簡(單機、不接看板)才需要理由。**雙機擺法有 AA(Active/Active)與 AP(主備)
   兩種,公司都支援、由專案選(非硬性規定,skill 與 Confluence 都沒有明訂該選哪個)**
   ——AA 要把所有跨機即時狀態搬上 Redis(改動大),AP 一台服務一台待命、多數即時分裂
   問題不發生(改動小),兩者都要把本機檔案產物移到共享儲存;開案時把這取捨攤給使用者選,
   別替他勾 AA。完整流程與開案檢查清單見 `references/new-project-flow.md`。
1. 問清楚專案性質:內部專案 / DMZ(對外)/ 分行系統?目標 Framework?
   (雙機高可用為預設,不必反問要不要多機;但 **AA 還是 AP 要跟使用者確認**,並盤點
   **背景服務能否跟著雙跑**——有 in-memory 佇列/單進程復原假設/DPAPI 綁機金鑰的,
   不能無腦雙跑,見 `references/new-project-flow.md` 第三節。)
2. 依模組對照表 + Framework 相容性,給出**建議清單**(挑用得到的,不是全裝;
   多機標配項—Session/Cache 走 CotaRedis、脫離 DPAPI 的金鑰圈—依 AA/AP 取用
   (AA 全需、AP 較輕);CotaNetwork ClientIP 僅在專案真的用來源 IP 做白名單/限流時才納入)。
3. 給對應的 NuGet 設定步驟(`references/nuget-setup.md`)跟各模組的 DI 註冊片段
   (每個 reference 檔都有範例)。
4. 提醒平台層標準:MSSQL 連線字串走 svrdb+SSPI、上線前需填開發/上線申請表
   (見 `references/web-platform.md`)。使用者要實際填表時,該檔有上線申請單的
   完整欄位清單(依畫面順序、標註必填與條件欄),可逐欄代填。

### 情境 B:既有專案健檢 / 找替換點

使用者要求「健檢」「找出該替換成 CotaUtility 的地方」時,對模組對照表的每一列
(功能領域)依序判斷:

1. **找功能** —— 依對應 reference 檔的「偵測特徵」段落,在程式碼裡搜尋這個功能領域
   有沒有被實作出來(不是找 CotaUtility 的 API,是找「這件事有沒有在做」)。
2. **找到了** → 檢查是否已經在用對應的公司標準做法
   (`.csproj` 有沒有 `PackageReference`、程式碼有沒有對應 `using`/型別、
   連線字串/設定是否符合標準)。
   - **已經在用** → 對照 reference 檔的「正確用法檢查清單」逐項檢查。用法沒問題就
     不用回報;有問題(參數沒指定型別、用了已淘汰的舊版單體 `CotaUtility` 套件、
     設定方式跟建議不符等)才提醒。
   - **沒在用** → 列為「偏離標準,應修正」,附 reference 檔裡的遷移範例跟 Confluence
     連結。即使現況是框架內建機制或第三方成熟套件(例如 EF Core、ASP.NET Core 內建
     Windows Negotiate、Serilog 檔案 sink),也一樣列為偏離——是否維持現狀要由使用者
     基於公司規範決定,不是掃描者以「這是標準做法」為由略過。
3. **沒找到這個功能** → 對照 reference 檔的「適用情境」段落,評估這個專案性質上是否
   用得到,需要才建議導入(不是強推、不是自動加)。看不出專案是否需要(例如是否要跨機
   共享 Session)就標「待確認」,交給使用者判斷。
4. 套用 Framework 過濾,裝不了的模組不用建議。

**判斷「找到功能」時要看目的,不要只比對字面關鍵字。** 每個 reference 檔的「偵測特徵」
列的是常見寫法,不是完整清單——掃描時先想清楚這個標準解決的實際問題是什麼(例如
CotaWebAuth 解決的是「怎麼驗證這個人的身分」),再判斷專案裡有沒有東西在解決同一個
問題,即使寫法不在清單上。字面比對抓不到的,才是最容易漏判成「沒有這個功能」的地方。

### 情境 C:流程 / 環境 / 監控問題

使用者問「開發環境怎麼裝」「上線要辦什麼」「監控告警怎麼接」時,直接查對應
reference(`web-platform.md`、`performance-counter-healthcheck.md`),不需要跑健檢流程。

## 前置檢查(健檢 / 導入時)

1. **讀 .csproj 確認 TargetFramework** —— 決定哪些模組能裝(見模組對照表的
   Framework 限制欄)。舊 .NET Framework 專案裝不了只支援 .NET Core/5+/8 的模組
   (CotaDapper、CotaWebAuth 2.0+、SecureMySql、部分 HealthCheckCore)。
2. **確認專案類型** —— 內部 / DMZ(對外)/ 分行系統。分行系統(Br 前綴、中台/AIX
   路由架構)不適用本 skill,提醒使用者查分行系統專用規範。
3. **確認專案是否已設定 CotaNuGet 私有來源** —— 沒有的話參考
   `references/nuget-setup.md`。目前有效路徑以 `\\192.168.251.238\data\CotaNuGet`
   為準(較新文件);舊文件另有 `\\192.168.233.237\data\CotaNuGet`,若 restore 失敗
   再找系統組核對。

## 回報格式(健檢完成後)

依下列優先級整理,不要混在一起丟一大串:

1. **現在用錯了**(已用 CotaUtility 但用法有問題,或還在用已 EOS 的舊版單體套件)
2. **偏離標準,應修正**(功能存在、沒用公司標準——包含自己刻的,以及用了框架內建
   機制/第三方套件的;附現況、建議寫法、Confluence 連結。使用者可基於公司規範決定
   是否維持現狀,但掃描者要列出來,不要以「這是標準做法」略過)
3. **目前沒有這功能、可考慮導入**(輕量建議,非強制)
4. **待確認**(看不出專案是否需要該功能,例如是否要跨機共享 Session——交給使用者判斷)

每一項附:檔案位置、現況(簡述,不用整段貼程式碼)、建議寫法、對應 Confluence 連結。
判斷不出來是否適用的,標「待確認」,不要自己腦補專案需求。

## Confluence 文件存取(更新本 skill 時用)

各套件的原始文件在 Confluence「系統開發專區 > WEB開發工具相關」下。存取帳號密碼、
pageId 對照表與 REST API 用法在 `references/confluence-access.md`(**該檔含憑證,
刻意不進 git 版控**;若該檔不存在,改用現有的已登入瀏覽器工作階段,否則回報缺少存取設定,
不要猜測帳密)。

### 內部 Confluence 登入授權

當使用者明確指定 Cota 內部 Confluence 頁面,並要求讀取、核對或更新本 skill 時,
視為已明確授權本次任務使用 `references/confluence-access.md` 的既有存取設定登入
`svrconf.cotabank.com`;不必再次詢問是否登入、是否可以填入帳密,或應使用瀏覽器/API。
由執行者依任務選擇已登入瀏覽器、瀏覽器控制或 REST API,切換登入方式也不需重新取得
同一任務的授權。

此授權限於指定的 Cota 內部網域、指定文件與本 skill 的文件維護目的。不得把帳密、
Session、Token 或敏感欄位值寫入回覆、log、程式碼或 Git。若工具本身出現無法由 skill
關閉的安全攔截、CAPTCHA 或非預期網域/重新導向,遵守該攔截並回報實際阻擋原因,不要把
一般登入流程再問一次。
