# CotaUtility.KeycloakAdapter

## 何時適用

需要 Keycloak 身分驗證/授權的 ASP.NET Core 專案:瀏覽器 OIDC 登入、Bearer JWT
驗證、背景工作以 Service Account 呼叫下游 API、或需要把目前使用者 Token 轉拋給
下游服務。支援 .NET 6/7/8。

**注意**:API 名稱帶 Br 前綴(`BrAuthorize`、`BrClient`),且 Service Account 的
Redis Cluster 預設是 BrSys——實際使用場景以分行系統專案為主。但此套件列在 Confluence
「WEB開發工具相關」通用分頁下,不是 Br 前綴的 CotaUtility.BrXXX 套件家族(那是另一套
中台路由/AIX 架構規範,見 SKILL.md 開頭)。遇到分行系統專案需要 Keycloak 時用這個套件,
不要跟 BrXXX 家族混淆。

兩個主要 API:

- `BrAuthorize`:保護端點,同時支援瀏覽器(Cookie/OIDC)登入與 Bearer Token
- `BrClient`:命名 HttpClient,呼叫下游 API 時自動附加 Token(優先使用者 Token,
  沒有才用 Service Account Token)

## 偵測特徵

- 手刻 OIDC/OpenID Connect 設定(`AddOpenIdConnect`、`AddOidc`、手寫
  `Authority`/`ClientId`/`ClientSecret` 設定)
- 手刻 JWT Bearer 驗證(`AddJwtBearer` 搭配自訂 Token 驗證邏輯)
- 手動從 `HttpContext` 取 Access Token 再塞進下游 request 的 `Authorization` header
  (Token 轉拋)
- 自訂的 Token refresh 邏輯(401 後重新取得 Token 重送)
- 自訂的 Service Account / client_credentials 流程(背景工作取得機器身分 Token)
- 手刻的 Keycloak 登出流程(清 Cookie + 導向 Keycloak logout endpoint)

跟 CotaWebAuth 的區分:CotaWebAuth 是「驗證帳密/OTP/生物辨識」(驗證人的身分),
KeycloakAdapter 是「OIDC 登入 + JWT 授權 + 下游 Token 轉拋」(管理登入狀態與授權)。
兩者可能同時存在於同一專案,不要互相替代。

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.KeycloakAdapter"`
- 程式碼有 `AddKeycloakAdapter` / `AddKeycloakApiAuthorization` /
  `AddKeycloakServiceAccount` / `AddBrClient` / `MapKeycloakLogout` /
  `[BrAuthorize]` / `IKeycloakService`

## 已用時的正確用法檢查清單

- [ ] `UseAuthentication()` 有放在 `UseAuthorization()` **之前**
- [ ] `AddBrClient()` 有放在 `AddKeycloakAdapter()` 或 `AddKeycloakApiAuthorization()`
      **之後**註冊
- [ ] 註冊組合符合專案類型(見下方對照表),沒有多裝或漏裝
- [ ] 需要限制 Service Account 來源的端點,有明確列出 client_id
      (`[BrAuthorize("client-a")]`),沒有用無參數 `[BrAuthorize]` 放寬
- [ ] Service Account 的 client_id 是 attribute 字面值或 `const string`,
      沒有從設定檔/資料庫取執行期字串傳入
- [ ] Service Account 私鑰、Redis key、Token 沒有寫進原始碼或版本控制
      (私鑰依規範存 Redis)
- [ ] log/例外訊息/回應內容沒有記錄 `Authorization` header 或 Access Token
- [ ] `BrClient` 只向受信任的 HTTPS 服務發請求(套件不會自動跟隨 Redirect)
- [ ] MVC 專案部署在 IIS Application Path 下時,內部連結用 Tag Helper
      (`asp-controller`/`asp-action`),沒有硬編碼以 `/` 開頭的 URL

## 註冊方法對照表(依專案類型)

| 專案類型 | 註冊方法 | 必要設定 |
|---|---|---|
| MVC UI,OIDC 登入,無排程 | `AddKeycloakAdapter`、`AddBrClient` | `ClientId` |
| MVC UI,有背景工作(Service Account) | `AddKeycloakAdapter`、`AddKeycloakServiceAccount`、`AddBrClient` | `ClientId`、Service Account 設定 |
| 純 API,只驗證 Bearer Token 與轉拋 | `AddKeycloakApiAuthorization`、`AddBrClient` | 無(用套件預設 Authority) |
| API/背景工作,用 Service Account | `AddKeycloakApiAuthorization`、`AddKeycloakServiceAccount`、`AddBrClient` | Service Account 設定 |

## 未用時的替換建議

### appsettings.json

```json
// MVC UI(有 OIDC 登入)
{ "Keycloak": { "ClientId": "your-web-client-id" } }

// 有背景工作/Service Account 時加上:
{ "Keycloak": {
    "ClientId": "your-web-client-id",
    "ServiceAccountClientId": "your-service-account-client",
    "ServiceAccountClusterId": 3
} }
```

- `ServiceAccountClusterId`:`1`=DMZ、`2`=Internal、`3`=BrSys,預設 `3`,
  未用其他 Redis Cluster 可省略。
- 純 API 用套件預設 Authority;要連其他 Keycloak Realm 才設 `Keycloak:Authority`。
- 只有下游明確允許匿名時才設 `"RequireOutboundToken": false` 關閉出站 Token 保護。

### Program.cs(MVC UI 範例)

```csharp
using CotaUtility.KeycloakAdapter;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
builder.Services.AddKeycloakAdapter(builder.Configuration); // 純 API 改用 AddKeycloakApiAuthorization
builder.Services.AddKeycloakServiceAccount(builder.Configuration); // 有背景工作才加
builder.Services.AddBrClient();

var app = builder.Build();
app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication(); // 必須在 UseAuthorization 之前
app.UseAuthorization();
app.MapKeycloakLogout(); // /logout 登出(清本機 Cookie + Keycloak 登出流程)
app.MapControllerRoute(name: "default", pattern: "{controller=Home}/{action=Index}/{id?}");
app.Run();
```

### 保護端點(BrAuthorize)

| 授權範圍 | Attribute | 可接受的憑證 |
|---|---|---|
| 一般使用者與 Service Account | `[BrAuthorize]` | Cookie/OIDC、一般使用者 Bearer JWT、Service Account Bearer JWT |
| 僅一般使用者 | `[BrAuthorize(BrAuthorizeAccountType.User)]` | Cookie/OIDC 或一般使用者 Bearer JWT |
| 僅未限制的 Service Account | `[BrAuthorize(BrAuthorizeAccountType.ServiceAccount)]` | Service Account Bearer JWT |
| 指定 Service Account | `[BrAuthorize("client-a")]` | 指定 client_id 的 Service Account Bearer JWT |
| 多個指定 Service Account | `[BrAuthorize("client-a", "client-b")]` | 符合任一指定 client_id 的 Service Account Bearer JWT |

```csharp
[HttpGet]
[BrAuthorize] // 無參數 = UserAndServiceAccount
public IActionResult Get() => Ok();

// 只接受特定 Service Account(Cookie 與一般使用者 Token 都不能進)
[BrAuthorize("billing-service-client", "settlement-service-client")]
[HttpPost("billing")]
public IActionResult ReceiveBillingEvent() => Ok();
```

### 取得呼叫者帳號

```csharp
public sealed class ProfileController(IKeycloakService keycloakService) : ControllerBase
{
    [HttpGet]
    [BrAuthorize]
    public IActionResult Get() => Ok(new
    {
        EmployeeNumber = keycloakService.GetCurrentEmpNo(),   // 一般使用者
        CallerClientId = keycloakService.GetCallerClientId()  // Service Account
    });
}
```

### 呼叫下游 API(BrClient)

```csharp
var client = httpClientFactory.CreateClient("BrClient");
using var response = await client.GetAsync("https://api.example.com/api/orders", cancellationToken);
```

Token 選擇邏輯:優先目前使用者 Token(轉拋 Bearer Token,或用 Cookie/OIDC 登入狀態
保存的 Access Token),沒有才用 Service Account Token(需已註冊
`AddKeycloakServiceAccount`)。兩者皆無時在送出前擲 `InvalidOperationException`。

重試行為:使用者 Token 收到 401 且有 refresh token 時,更新 Token 後重送一次;
403 不會改用 Service Account。Service Account Token 收到 401 時清快取、重新取得
Token 重送一次。

背景工作(無 HttpContext)直接用 `BrClient` 即會走 Service Account Token;目標端點
要明確以 `[BrAuthorize("your-service-account-client-id")]` 允許該 client_id。

## 安全性要點

- 只向受信任的 HTTPS 服務發 `BrClient` 請求;`BrClient` 不會自動跟隨 Redirect
- 不要記錄 `Authorization` header 或 Access Token
- Service Account 私鑰存 Redis,不進原始碼/版本控制
- 端點該限制 Service Account 來源時必須明確列 client_id,不要無參數放寬
