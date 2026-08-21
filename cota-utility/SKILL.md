---
name: cota-utility
description: "在 .NET (Framework/Core) 專案套用或掃描公司內部 CotaUtility 框架——資料庫存取(MSSQL/MySQL)、Redis Cache/Session、結構化Log、健康檢查、IP/簽章驗證、呼叫COBOL/Java主機、統一編號遮罩、集中權限查詢、HTML轉PDF報表、AD/OTP/生物辨識驗證、Keycloak OIDC登入/JWT授權等。新專案開發時用來決定該裝哪些套件;既有專案維護、或使用者要求「健檢」「找出該替換成 CotaUtility 的地方」時,用來掃描程式碼。"
---

# CotaUtility 導入與健檢

CotaUtility 是三信商業銀行(Cota Bank)內部的 .NET 工具庫。原本是單一套件,已於
2023.12.01 停止更新(EOS),拆成多個獨立 NuGet 套件,各自獨立維護、獨立版號。本 skill
涵蓋這些拆分後、目前仍在維護的模組。

**不涵蓋分行系統(Br 前綴專案)專用的 CotaUtility.BrXXX 套件家族**(BrApiHelper、BrMvc、
BrHoliday、BrPILog 等)——那是另一套完全不同的三層式架構規範(中台路由、AIX 主機整合),
跟這裡的通用模組是兩回事。偵測到專案是 Br 前綴 / 有中台路由架構時,提醒使用者那是另一個
體系,不要套用本 skill 的規則。

## Confluence 文件存取(更新本 skill 時用)

各套件的原始文件在 Confluence「系統開發專區 > WEB開發工具相關」下。存取帳號密碼、
pageId 對照表與 REST API 用法在 `references/confluence-access.md`(**該檔含憑證,
刻意不進 git 版控**;若該檔不存在,請使用者提供 Confluence 存取方式,不要猜)。

## 前置檢查

1. **讀 .csproj 確認 TargetFramework** —— 決定哪些模組能裝(見下方模組對照表的
   Framework 限制欄)。舊 .NET Framework 專案裝不了只支援 .NET Core/5+/8 的模組
   (CotaDapper、CotaWebAuth 2.0+、SecureMySql、部分 HealthCheckCore)。
2. **確認是否為分行系統專案**(專案名 Br 前綴、或架構明顯走中台/AIX 路由)—— 是的話
   不適用本 skill,提醒使用者查分行系統專用規範。
3. **確認專案是否已設定 CotaNuGet 私有來源** —— 沒有的話參考
   `references/nuget-setup.md`。**注意**:目前找到兩個不同時期文件記載的 UNC 路徑
   (`\\192.168.251.238\data\CotaNuGet` 與較舊文件的 `\\192.168.233.237\data\CotaNuGet`),
   哪個才是目前有效的路徑待確認,提醒使用者跟系統組核對,不要自己猜。

## 掃描流程(既有專案健檢 / 使用者要求找替換點時)

對模組對照表的每一列(功能領域)依序判斷:

1. **找功能** —— 依對應 reference 檔的「偵測特徵」段落,在程式碼裡搜尋這個功能領域
   有沒有被實作出來(不是找 CotaUtility 的 API,是找「這件事有沒有在做」)。
2. **找到了** → 檢查是否已經在用對應的 CotaUtility 套件
   (`.csproj` 有沒有 `PackageReference`、程式碼有沒有對應 `using`/型別)。
   - **已經在用** → 對照 reference 檔的「正確用法檢查清單」逐項檢查。用法沒問題就
     不用回報;有問題(參數沒指定型別、用了已淘汰的舊版單體 `CotaUtility` 套件、
     設定方式跟建議不符等)才提醒。
   - **沒在用** → 分兩種情況,**不要混為一談**:
     - **自己刻的**(手工實作,通常是明顯的重複造輪子)→ 列為候選替換點,附
       reference 檔裡的遷移範例跟 Confluence 連結。
     - **用了其他非 CotaUtility 的合法標準做法**(例如框架內建機制、業界標準協定、
       第三方成熟套件——不是隨手刻的)→ **不要**直接判「不適用」略過,也**不要**
       直接判「該替換」強推。列為「待確認」,說明現況跟為什麼沒用 CotaUtility 的
       可能理由,是否要統一改用 CotaUtility 通常涉及公司內部政策(稽核、加密、
       日誌格式等要求),不是單純的程式碼品質問題,不是靠讀程式碼就能斷定的事。
       (例如:專案用 ASP.NET Core 內建的 Windows Negotiate 做 AD 身分驗證,而不是
       呼叫 CotaWebAuth.VerifyAD——這不是自己刻的,是標準做法,但也不是 CotaUtility,
       應該標待確認而不是因為找不到「自刻」關鍵字特徵就當作沒有這個功能)
3. **沒找到這個功能** → 對照 reference 檔的「適用情境」段落,評估這個專案性質上是否
   用得到,給輕量建議(不是強推、不是自動加)。看不出專案是否需要(例如是否要跨機
   共享 Session)就標「待確認」,交給使用者判斷。
4. 套用前置檢查第 1 點的 Framework 過濾,裝不了的模組不用建議。

**判斷「找到功能」時要看目的,不要只比對字面關鍵字。** 每個 reference 檔的「偵測特徵」
列的是常見寫法,不是完整清單——掃描時先想清楚這個模組解決的實際問題是什麼(例如
CotaWebAuth 解決的是「怎麼驗證這個人的身分」),再判斷專案裡有沒有東西在解決同一個
問題,即使寫法不在清單上。字面比對抓不到的,才是最容易漏判成「不適用」的地方。

## 模組對照表

| 功能領域 | 套件 | Framework 限制 | 詳細規則 |
|---|---|---|---|
| 原生風格 DB 存取(MSSQL) | CotaUtility.CotaDB | netstandard2.0(通用) | `references/cota-db.md` |
| Dapper 風格 DB 存取(MSSQL) | CotaUtility.CotaDapper | .NET Core only,**文件標示未完成** | `references/cota-dapper.md` |
| 分行系統 MySQL 存取 | CotaUtility.SecureMySql | .NET 5/6/7/8,Windows x64/x86 | `references/secure-mysql.md` |
| Redis 分散式 Cache / Session / PubSub | CotaUtility.CotaRedis | netstandard2.0 | `references/cota-redis.md` |
| 結構化 Log(寫入 Redis,Seq 查詢) | CotaUtility.CotaRedisLog(.Serilog / .NLog) | netstandard2.0 | `references/cota-redis-log.md` |
| 來源 IP 檢查 / COBOL↔Web 簽章驗證 | CotaUtility.Network | netstandard2.1 | `references/network.md` |
| 呼叫 COBOL/Java 主機(含 Big5 轉碼) | CotaUtility.JavaCall | netstandard2.0 | `references/java-call.md` |
| CotaInfo 內部通知訊息 | CotaUtility.CotaNotification | netstandard2.0 | `references/notification.md` |
| 專案監控資訊 / ASP.NET Core 健康檢查端點 | CotaUtility.CotaPerformanceCounter / CotaHealthCheckCore | netstandard2.0 / netcoreapp3.1+ (HealthCheckCore 僅限 .NET Core Web) | `references/performance-counter-healthcheck.md` |
| AD / OTP / FIDO2 生物辨識驗證 | CotaUtility.CotaWebAuth | v1.0.0=.NET5,v2.0.0+=.NET8 | `references/web-auth.md` |
| Keycloak OIDC 登入 / JWT 授權 / 下游 Token 轉拋 | CotaUtility.KeycloakAdapter | .NET 6/7/8 | `references/keycloak-adapter.md` |
| 客戶統一編號遮罩 / 亂數化 | CotaUtility.Customer | .NET Framework 4.7.2+ / .NET Core | `references/customer.md` |
| 集中權限/角色查詢 | CotaUtility.PermProvider | .NET Framework 4.6.1+ / .NET Core 2.0+ | `references/perm-provider.md` |
| 網頁轉 PDF 報表 | CotaUtility.Reporting | 未特別限制,依 wkhtmltopdf/puppeteer 執行環境 | `references/reporting.md` |

## 新專案導入模式

使用者開新專案、或問「這個新專案該裝哪些 CotaUtility」時:

1. 問清楚專案性質:內部專案 / DMZ(對外)/ 分行系統?需不需要多機部署或 HA(影響
   Session/Cache 要不要用 Redis)?目標 Framework?
2. 依模組對照表 + Framework 相容性,給出**建議清單**(挑用得到的,不是全裝)。
3. 給對應的 NuGet 設定步驟(`references/nuget-setup.md`)跟各模組的 DI 註冊片段
   (每個 reference 檔都有範例)。

## 回報格式

掃描完成後,依下列優先級整理,不要混在一起丟一大串:

1. **現在用錯了**(已用 CotaUtility 但用法有問題,或還在用已 EOS 的舊版單體套件)
2. **該替換但目前是自己刻的**(功能存在、沒用 CotaUtility、明顯是重複造輪子)
3. **功能存在,但用了其他非 CotaUtility 的標準做法,待確認是否要統一改用**(不是自刻,
   是否要換屬於公司政策決定——這一類**必須獨立列出**,不要因為「不是自刻」就併進第
   2 類強推替換,也不要因為「找不到自刻特徵」就直接漏掉不報)
4. **目前沒有這功能、可考慮導入**(輕量建議,非強制)

每一項附:檔案位置、現況(簡述,不用整段貼程式碼)、建議寫法、對應 Confluence 連結。
判斷不出來是否適用的(例如看不出這個 Session 是否需要跨機共享),標「待確認」,不要
自己腦補專案需求。
