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

## 員工入口網 / 行動裝置入口網簽章驗證(hiseed / hisignedhash)

另一套簽章機制:從**員工入口網/行動裝置入口網**過來的 request 會帶上 `hiseed`
及 `hisignedhash` 兩項資訊,各系統接收到後需驗證簽章正確性,**驗證失敗需導回入口網**。
這跟上面的 `X-Cota-Authentication`(系統間呼叫簽章)是兩套不同的機制,不要混用。

- `hiseed` 由以下參數以 `$` 串接而成:員工編號、員工姓名、上個網頁 load 的時間、
  讀卡機讀取到的卡片號碼、讀卡機名稱、入口網站登入時間、晶片卡序號、行動裝置
  (1=是行動裝置,0=不是)。
- **行動裝置版**各網頁系統除驗證簽章外,需加驗三項:
  1. 「行動裝置」是否為 1
  2. 「入口網站登入時間」是否為空值(驗證員工入口網有登入過)
  3. 「上個網頁 load 的時間」與網頁所在主機目前時間比較,是否超過 **30 秒**
- 驗證通過後,可將登入資訊寫入 session 供後續作業判斷;**session timeout 時間
  統一為 20 分鐘**。
- Session timeout 的標準處理:彈出倒數(統一 **6 秒**)後回登入頁;若專案可從
  「WEB 版員工入口網」及「行動裝置入口網」兩個入口登入,要用
  `HttpContext.Request.Host.Host` 判斷 timeout 後該回哪一個入口網。

驗證範例程式在 Confluence(另見 pageId 106561628 的連結)。

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

- CotaUtility.Network: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511008
- 採用 HAProxy 的專案取 Client IP / 驗證允許來源(官方說明): https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511273(「WEB專案開發/上線申請」頁內連結)
