# WEB 平台設定 / 開發環境 / 部署上線

不是 NuGet 模組,是 WEB 專案的平台層事實:.NET 8 對傳統 Web.config 設定的等效寫法、
開發環境準備、開發/上線申請流程。健檢 .NET 8 專案的 `Program.cs` 設定、或使用者問
「開發環境怎麼裝」「上線要辦什麼」時查這裡。

## .NET 8 下 System.Web 設定的等效寫法

傳統 .NET Framework 的 `Web.config` `system.web` 節在 .NET 8 不適用,對應關係:

| Web.config 節 | .NET 8 等效 |
|---|---|
| `httpRuntime executionTimeout="300"` | Kestrel `Limits`:`RequestHeadersTimeout` / `KeepAliveTimeout` |
| `httpRuntime enableVersionHeader="false"` | .NET 8 預設就不含 HTTP 版本資訊,不需設定 |
| `customErrors mode="On" defaultRedirect="..."` | `AddExceptionHandler` / `UseStatusCodePages` 中間件(自訂 `IExceptionHandler`) |
| `compilation debug/strict/explicit` | 由 .csproj 編譯配置決定(Release 即無偵錯資訊);strict/explicit 無直接對應 |
| `httpCookies requireSSL httpOnlyCookies` | `CookiePolicyOptions`:`Secure = Always`、`HttpOnly = Always`、`MinimumSameSitePolicy = Lax`;`UseCookiePolicy()` 要放在 `UseRouting` 之後 |

Kestrel 超時範例:

```csharp
builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(300);
    options.Limits.KeepAliveTimeout = TimeSpan.FromSeconds(300);
});
```

Cookie 政策範例:

```csharp
builder.Services.Configure<CookiePolicyOptions>(options =>
{
    options.Secure = CookieSecurePolicy.Always;
    options.HttpOnly = Microsoft.AspNetCore.CookiePolicy.HttpOnlyPolicy.Always;
    options.MinimumSameSitePolicy = SameSiteMode.Lax;
});
// pipeline: app.UseCookiePolicy();  // 必須在 UseRouting 之後
```

## 開發環境準備

工具包(NAS 共用):

- Visual Studio: `\\nas\0146\UserData\PublicData\共用專區\000_WEB開發相關資源\VisualStudio\`(VS2022 / VS2019 / VS2015)
- Git: 同目錄 `\Git`
- SSMS: 同目錄 `\SSMS`
- 原始碼掃描 Checkmarx: `http://sca.cotabank.com/CotaSCA/`

IIS 安裝:「程式和功能 → 開啟或關閉 Windows 功能」勾選 IIS 相關項目。

開發憑證:

- 路徑: `Y:\共用專區\000_WEB開發相關資源\開發環境Cert`
- `mmc` 主控台 → 嵌入式管理單元「憑證」選**電腦帳戶** → 匯入 `star.cotabank.com.tw.p12`(密碼 `123123`)
- IIS 站台 → 繫結 → 新增 https 並選取該憑證

## 開發 / 上線申請流程

- 新專案開發時,無論將來放 HA 或 AA 主機,都需先填申請表;**開發與正式上線分開申請**。
  設定由管理組及系統組處理,上線時系統組會核對開發申請表。
- 每個 WEB 專案(或業務)有自己的網域名稱。
- 若專案會讓**主機呼叫**(主機有額外的 hosts 要設定),設計人員必須向系統組說明並在
  申請表備註。
- 採用 HAProxy 的專案:取得 Client IP / 驗證允許來源有專門頁面(見
  `references/network.md` 的 HAProxy 章節)。
- 專案監控:上線專案需接 CotaPerformanceCounter + 資訊看板(見
  `references/performance-counter-healthcheck.md`)。

### 頁面提供的相關作業入口

以下連結均來自 Confluence「WEB專案開發/上線申請」第 7 版(最後編輯
2024-03-07)。頁面本身列出的申請範例、開發機更新、監控、HAProxy 與 Client IP
說明，依實際作業需要開啟原頁確認最新內容:

- 申請表填寫範例: [WEB專案上線申請單-範例.pdf](https://svrconf.cotabank.com/download/attachments/82511127/WEB%E5%B0%88%E6%A1%88%E4%B8%8A%E7%B7%9A%E7%94%B3%E8%AB%8B%E5%96%AE-%E7%AF%84%E4%BE%8B.pdf?version=1&modificationDate=1679963289950&api=v2)
- 開發機 WEB 專案更新: <https://svrconf.cotabank.com/x/JoDSAw>
- 專案監控: <https://svrconf.cotabank.com/x/DgBeAg>
- `CotaPerformanceCounter`: <https://svrconf.cotabank.com/x/noDSAw>
- HAProxy 負載平衡器管理: <https://svrconf.cotabank.com/x/F4wDB>
- HAProxy Client IP / 允許來源: <https://svrconf.cotabank.com/x/oATrB>

### Web 專案上線申請單欄位

依實際畫面順序還原。**★＝必填(畫面有紅色星號);「條件」＝有使用該功能才填。**
使用者要實際申請某專案時,照這份逐欄填;「無異動」選項代表該項與現況相同、不需變更。

**基本資料**

- 案號:送出後自動產生
- 申請表單:自動帶入
- 申請日期:自動帶入
- 申請人:自動帶入
- 申請單位:自動帶入
- ★ 申請主機類別:`正式機 / 開發機`
- ★ 專案名稱(同應用程式集區名稱)
- ★ 申請事由

**專案設定**

- ★ 專案說明
- ★ 系統類別
- ★ AP User
- ★ 應用程式名稱
- ★ 目標 Framework
- ★ 程式開發工具版本
- ★ 程式開發語言
- ★ 提供 AIX 主機呼叫:`COBOL主機 / JAVA主機 / 無異動`
- ★ 是否有使用資料庫:`是 / 否 / 無異動`
- 條件:主要資料庫
- ★ 程式開發版本控制路徑:`Git 連結`
- ★ 專案類型:`Web (.Core) / Web (.Net Framework) / 無異動`
- 條件:Packages 路徑
- ★ 專案安裝路徑
- ★ 主機放置區域
- ★ 抄送主機
- ★ 目標主機
- ★ HostName
- ★ HAProxy:`啟用 / 不啟用 / 無異動`
- 允許來源
- ★ Active/Active 模式服務:`啟用 / 不啟用 / 無異動`

**入口網選單設定**

- 入口網選單路徑
- 連結
- 是否權限設定?(姓名／員編、分行單位)
- 是否設定選單排序?(排序編號)
- 是否另開分頁:`是 / 否`
- 是否隱藏選單:`是 / 否`
- 是否使用員工晶片卡:`是 / 否`
- 條件:晶片卡版本:`新 / 舊`
- 是否只允許 GET:`是 / 否`(預設 Method 為 POST)

**新增 Keycloak 客戶端應用**

- 客戶端名稱(同專案名稱)
- 類型:`Public Client(網頁系統)` / `Service Account(服務帳戶)`
- 應用區域:`分行系統` / `入口網系統`
- 「執行人員／確認人員」區塊是後續操作說明,不是一般申請欄位。

**RedisDB 帳號**

- 帳號(專案名稱,全大寫)
- 資料庫區域:`內部 / DMZ / 核心系統`
- 資料庫 ID(畫面預設 `02`)
- 「執行人員／確認人員」同樣是後續建置與驗證說明。

**其他設定**

- 專案相關資訊 API
- 專案額外服務狀態 API
- 專案狀態檢查 URL
- IE MODE

**備註**

- 其他說明(最多 1000 字)

### 頁面評論中的欄位格式補充

頁面上的欄位說明評論補充了以下填寫格式；這是申請單的實務填寫提示，不是另一組
套件或執行環境規範:

- **程式開發版本控制路徑**:專案檔與方案檔同一層填 `#/專案名稱`;不同層填
  `#/專案名稱/專案名稱`。
- **Packages 路徑**:若是 .NET Framework 專案且使用 NuGet,專案檔與方案檔同一層填
  `packages`;不同層填 `../packages`。

## HSTS 標準

正式環境 HSTS 表頭(`Strict-Transport-Security`)要求:**max-age 至少一年**、
**要設 includeSubDomains**——缺任一項都會被資安掃描列為風險(中間人攻擊)。
.NET 8 寫法見 `references/mobile-web.md` 的 HSTS 設定(內部專案通用,不只行動專案)。

## 開發環境模擬 HAProxy

要在本機把 `http://localhost:1338` 轉為 `https://prjchartsserver.cotabank.com/`
(模擬正式環境的 proxy 行為)時:IIS 安裝 **ARR + URL Rewrite**
(iis.net 下載)→ 開 ARR proxy → 設站台 → 設 URL Rewrite 規則。

## 資安掃描常見項目

公司資安簡報系列(OWASP Top Ten 2023、CSP、HSTS、Heuristic_Parameter_Tampering
等)對應到 WEB 專案的實際檢查點:HSTS 設定(見上)、Content-Security-Policy
header、直接物件參考(參數未經權限驗證直接拼進查詢)的輸入驗證與過濾。

## 版本控制 / 抄送 / 異動單

Git 分支與環境對應、避免漏選檔案、原始碼檢測、風險評估表與測試報告、緊急抄送——
見 `references/git-workflow.md`。

## 參考

- .Net下的System.Web 設定: https://svrconf.cotabank.com/pages/viewpage.action?pageId=118620211
- HAProxy應用(命名規則/環境 IP): https://svrconf.cotabank.com/pages/viewpage.action?pageId=67342647
- IIS模擬HA PROXY 轉網址: https://svrconf.cotabank.com/pages/viewpage.action?pageId=117276931
- WEB專案上線申請流程: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82510181
- HSTS 設定不足風險與解決方案: https://svrconf.cotabank.com/pages/viewpage.action?pageId=120062615
- 資安相關(簡報系列索引): https://svrconf.cotabank.com/pages/viewpage.action?pageId=120062612
- WEB專案開發/上線申請: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511273
- Web應用程式部署流程: https://svrconf.cotabank.com/pages/viewpage.action?pageId=119177262(頁面目前無文字內容,僅圖/附件,需要時直接開啟)
- 開發環境準備工作: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82510920
