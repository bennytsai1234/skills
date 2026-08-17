# CotaUtility.Network

## 何時適用

需要來源 IP 檢查、或 Web 服務跟 COBOL/其他主機之間簽章驗證的專案。目標 netstandard2.1。
套件內含 `DataEnc.dll` 負責加解密。

## 偵測特徵

- 手刻的 IP 白名單比對(自己解析 `HttpContext.Connection.RemoteIpAddress` 或
  `X-Forwarded-For` header 跟允許清單比對)
- 手刻的 DNS 查詢邏輯取得 host 的 IP 清單
- 自訂的「呼叫端簽章驗證」機制(自己組字串 + 加密 + 帶在自訂 header),尤其是
  COBOL 主機呼叫 Web 服務、或 Web 服務互相呼叫時的來源驗證

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.Network"`
- 程式碼呼叫 `CotaUtility.Network.CotaNetwork.*` 靜態方法

## 方法簽章

| 方法 | 說明 |
|---|---|
| `static string GetClientIP(HttpContext httpContext, string[]? proxys)` | 取得來源 IP;無 proxy 時 `proxys` 傳 null |
| `static bool CheckIP(HttpContext httpContext, string[] clientSources, string[]? proxys)` | 檢查來源是否在允許清單內 |
| `static bool IsValidIP(string ip)` | 驗證是否為合法 IP 格式 |
| `static List<string> GetIpAddressListFromDNS(string[] hosts)` | 由 DNS 取得指定 host 清單的 IP |
| `static bool CheckCotaAuthentication(HttpContext httpContext, string path, int difference)` | 驗證簽章 header,`difference` 是允許的時間誤差秒數 |
| `static string CreateCotaAuthentication(string path)` | 產生簽章字串,放進呼叫外部服務時的 header |

## CotaAuthentication 驗證機制原理

簽章資料 = `絕對路徑 + ";" + 主機目前時間(Unix Time)`,經 `DataEnc` 加密後放在
`X-Cota-Authentication` header。驗證端解密後用 `;` 切割還原路徑與時間,核對路徑是否相符、
時間誤差是否在 `difference` 秒數內(主機時間可能有些許落差,所以需要容許值,不是要求完全
相等)。了解這個機制,遇到「驗證一直失敗」的問題時能判斷是路徑不符、時間誤差設太小、還是
兩端主機時間本身就跑掉。

## 已用時的正確用法檢查清單

- [ ] 有經過 proxy server 的場景,`GetClientIP`/`CheckIP` 是否正確帶入 `proxys` 陣列
      參數(沒帶或帶錯會導致 IP 判斷失準)
- [ ] `CheckCotaAuthentication` 的允許時間誤差(`difference` 參數)是否合理——太寬鬆
      失去驗證意義,太嚴格則主機時間稍有落差就會被拒絕

## 未用時的替換建議

```csharp
// 檢查來源 IP
bool allowed = CotaUtility.Network.CotaNetwork.CheckIP(httpContext,
    new string[] { "hostA" }, new string[] { "proxyA" });

// 驗證 COBOL 主機發來的簽章 header(X-Cota-Authentication)
if (!CotaNetwork.CheckCotaAuthentication(HttpContext, "/eLoan/api/SyncData/NewJob1", 30))
{
    // 非允許來源
}

// Web 端呼叫其他服務前,產生簽章帶入 header
string encString = CotaNetwork.CreateCotaAuthentication(uri.AbsolutePath);
request.Headers.Add("X-Cota-Authentication", encString);
```

其餘方法:`IsValidIP`(合法 IP 格式驗證)、`GetIpAddressListFromDNS`(由 DNS 取得
host 的 IP 清單)。

## 掛 HAProxy 時的整合寫法

專案部署在 HAProxy(或其他反向代理)後面時,`HttpContext.Connection.RemoteIpAddress`
拿到的會是代理伺服器的 IP,不是真實用戶端 IP——這會連帶影響任何以來源 IP 為依據的邏輯
(例如 per-IP 速率限制、`GetClientIP`/`CheckIP` 判斷)。已驗證的實際案例(`CotaIT2019`
專案,確實掛在 HAProxy 後面)採用的整合寫法:

```csharp
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
});
...
var app = builder.Build();
app.UseForwardedHeaders();   // 要放在其他 middleware 之前

// 取得真實來源 IP 時,proxys 參數帶 HAProxy 的主機名稱
string realIp = CotaNetwork.GetClientIP(httpContext, new[] { "ha_svrmix.cotabank.com" });
```

掃描既有專案時,若判斷專案已經(或即將)掛 HAProxy,但只看到直接使用
`HttpContext.Connection.RemoteIpAddress`(沒有 `UseForwardedHeaders()`/沒有帶
`proxys` 參數給 `GetClientIP`/`CheckIP`),要一併提醒——這類邏輯掛 HAProxy 後全部請求
會變成同一個代理 IP,以 IP 為鍵的功能(速率限制分區、IP 白名單判斷)會失準。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511008
