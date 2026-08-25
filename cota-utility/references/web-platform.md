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

## 參考

- .Net下的System.Web 設定: https://svrconf.cotabank.com/pages/viewpage.action?pageId=118620211
- WEB專案開發/上線申請: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511273
- Web應用程式部署流程: https://svrconf.cotabank.com/pages/viewpage.action?pageId=119177262(頁面目前無文字內容,僅圖/附件,需要時直接開啟)
- 開發環境準備工作: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82510920
