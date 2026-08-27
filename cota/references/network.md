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
- **反向:專案要「回入口網」時也要自己產生簽章**——組好 hiseed 後透過
  `CryptUtilLib.IRSAHandler` 執行 RSASign,把 `hiseed` + `hisignedhash` 回傳給
  入口網驗證(入口網網址 `https://zta.cotabank.com.tw/Cota2024/Home/MenuBoard`)。
  行動入口網專案的完整標準見 `references/mobile-web.md`。

### hiseed 驗證範例程式

```csharp
// Controller:入口網跳轉過來時帶 hiseed / hisignedhash;hiseed 為 null 表示直接 AD 登入
public IActionResult Login(string hiseed, string hisignedhash)
{
    string directurl;

    if (hiseed == null)
        return View();  //AD Login
    try
    {
        var errMsg = CotaEntrance.VerifySignature(hiseed, hisignedhash, out string empNo);
        if (!string.IsNullOrEmpty(errMsg))
        {
            TempData["ErrorMessage"] = $"驗證簽章發生錯誤:{errMsg}";
            return RedirectToAction("Error", "Home");
        }

        empNo = hiseed.Split('$')[0];
        directurl = GetLoginUrl(empNo);
        ViewData["url"] = directurl;

        return View();
    }
    catch (Exception ex)
    {
        return RedirectToAction("Error" + ex.ToString(), "Home");
    }
}

// 驗證 helper:CryptUtilLib.RSAHandler 驗證簽章,回傳 "0000" 才算成功
public static string VerifySignature(string seed, string signedhash, out string cardNo, out string empName)
{
    string verifyResult;
    CryptUtilLib.IRSAHandler crypt = new CryptUtilLib.RSAHandler();

    verifyResult = crypt.VerifySignature(signedhash, seed);

    // 只有回傳"0000"才表示成功
    if (verifyResult != "0000")
    {
        cardNo = "";
        empName = "";
        return HttpUtility.HtmlEncode(verifyResult);
    }
    String[] strarrCrdData = seed.Split('$');

    cardNo = HttpUtility.HtmlEncode(strarrCrdData[0]);
    empName = HttpUtility.HtmlEncode(strarrCrdData[1]);
    /*  目前用不到
    dic["LoadTime"] = HttpUtility.HtmlEncode(Convert.ToDateTime(strarrCrdData[2]));
    dic["tbName"] = HttpUtility.HtmlEncode(strarrCrdData[3]);
    dic["CrdName"] = HttpUtility.HtmlEncode(strarrCrdData[4]);
    dic["LoginTime"] = HttpUtility.HtmlEncode(strarrCrdData[5]);
    dic["tbCrdseq"] = HttpUtility.HtmlEncode(strarrCrdData[6]);
    */
    return "";
}
```

重點:

- `CryptUtilLib.RSAHandler.VerifySignature(signedhash, seed)` 回傳值**只有 `"0000"` 才算驗證成功**,其他值都是錯誤碼,要導回入口網。
- 驗證成功後 `hiseed` 以 `$` 切割:`[0]`=員工編號、`[1]`=員工姓名(其餘欄位見上方 hiseed 組成說明)。
- 範例中 `CotaEntrance` 是專案自訂的包裝類別,核心就是上面的 `VerifySignature` helper。

### 接到 seed 後驗證(VB 版)與取得員工資料

```vb
' 入口網會傳送兩個參數:hiseed 和 hisignedhash
Dim seed As String = Request.Params("hiseed")
Dim signedhash As String = Request.Params("hisignedhash")

If VerifySignature(seed, signedhash) = True Then
    ' ...
End If
```

驗證通過後取得員工資料(變數名稱可自訂,也不一定要用 Session):

```vb
Session("EmpNo") = CrdData(0)         '員工編號
Session("EmpName") = CrdData(1)       '員工姓名
Session("LoadTime") = CrdData(2)      '上個網頁load的時間
Session("CardNum") = CrdData(3)       '晶片卡卡號
Session("CrdName") = CrdData(4)       '讀卡機
Session("LoginTime") = CrdData(5)     '入口網站登入時間
Session("CardSerialNum") = CrdData(6) '晶片卡序號
```

### 返回入口網(專案端產生簽章)

兩種做法:

**A. 重新組合 seed 後加密**(變數名稱可自訂,也不一定要用 Session):

```vb
Dim seed As String

seed = Session("EmpNo") & "$" _
     & Session("EmpName") & "$" _
     & Session("eDocLoadTime") & "$" _
     & Session("CardNum") & "$" _
     & Session("CrdName") & "$" _
     & Session("LoginTime") & "$" _
     & Session("CardSerialNum")

'員工編號,員工姓名,上個網頁Load時間,晶片卡卡號,讀卡機名稱,入口網站登入時間,晶片卡序號

Dim signature As String = CreateSignature(seed)

hiseed.Value = seed
hisignedhash.Value = signature
```

**B. 直接把入口網傳來的 seed 字串重新使用**(收到什麼就回傳什麼):

```vb
hiseed = hiseed
hisignedhash = hisignedhash
```

回傳目標與注意事項:

- 請把網址 **POST** 到 `http://123.cotabank.com.tw/Cota/AllMenu.aspx`(有 https 較好,
  但目前用 http 比較多;專案有 https 就 POST 到 https)。
- **不要直連 `MenuBoard.aspx`,也不要 POST 資料給 `MenuBoard.aspx`**——測試時能跳回
  `MenuBoard.aspx` 只是因為 session 剛好還在;session 消失時使用者會被登出。
- 「上個網頁 load 的時間」欄位請填入**專案所在主機目前時間**。
- 若專案 session 已 timeout、無法取得登入資訊,依 Session Timeout 處理方式
  (pageId 106561581)處理。

### 從入口網跳轉出去(僅入口網本身使用)

入口網會用 POST 方式傳送:

```vb
Dim hiseed As String = Session("EmpNo") & "$" & Session("MEMsName") & "$" & dtnow & "$" & tbName.Value & "$" & hidReaderName.Value & "$" & Session("LoginTime") & "$" & Session("tbCrdseq")
Dim ret As Integer = crypt.RSASign(hiseed, hisignedhash)
```

### seed 錯誤用法(流傳已久的 BUG)

返回入口網、自行組合 seed 回傳 `hiseed` 時,第 4 個(index=3)參數放錯資料:
兩個都是 EmpNo、兩個都是 CardNum、兩個都是 sSNo,都是錯誤(看你變數怎麼取名,
反正不能一樣)。**第一個應該是員編,第四個應該是卡號**——使用備用卡時,卡號會跟
員編不一樣。

### CryptUtil 環境架設(簽章/驗證的 COM 元件)

所有專案皆透過 CryptUtil 元件產生與驗證簽章。架設步驟:

1. **註冊 `DataEnc.dll` 與 `CryptUtil.dll`**——IIS 啟用 32-bit 就裝 32-bit 元件,
   否則裝 64-bit(`DataEnc_x64.dll` / `CryptUtil_x64.dll`)。
2. **匯入 Registry 機碼**——到
   `HKEY_LOCAL_MACHINE\SOFTWARE\CotaBank\Portal` 及
   `HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\CotaBank\Portal`
   確認有 `priv_key` 及 `pub_key`。測試環境機碼(`DEV_KEY.reg`,同時含 32/64-bit,
   一併匯入)與正式環境機碼、各 DLL 最新版檔案,都在 Confluence
   「【入口網站】CryptUtil加密簽章」頁(pageId 3048856)的附件。
3. **個人電腦安裝**:在 C 槽新開目錄 `CotaDll` 放入下載的檔案,到該目錄執行
   `regsvr32 DataEnc_x64.dll`、`regsvr32 CryptUtil_x64.dll`。

專案端:將 COM 元件加入參考後使用 `CryptUtilLib.IRSAHandler`:

```vb
' A 網站產生簽章
Dim crypt As CryptUtilLib.IRSAHandler = New CryptUtilLib.RSAHandler
Dim signedData As String = Nothing
Dim seed As String = "This is Test Data for Signature"
Dim ret As Integer = crypt.RSASign(seed, signedData)

If ret = 0 Then 'success
    ' ...
Else
    Response.Write("<script language='Javascript'>alert('RSASign 失敗: " + Utility.FormatMsg(signedData) + "');</script>")
End If
```

```vb
' B 網站驗證簽章
Dim crypt As CryptUtilLib.IRSAHandler = New CryptUtilLib.RSAHandler
Dim signedData As String = Nothing
Dim seed As String = "This is Test Data for Signature"
Dim verifyResult As String = crypt.VerifySignature(signedData, seed)

If verifyResult <> "0000" Then
    Response.Write("<script language='Javascript'>alert('VerifySignature 失敗: " + Utility.FormatMsg(verifyResult) + "');</script>")
Else
    Response.Write("<script language='Javascript'>alert('VerifySignature 成功 !!!');</script>")
End If

Public Shared Function FormatMsg(ByVal msg As String)
    Return msg.Replace(Chr(13), "").Replace(Chr(10), "").Replace("'", """")
End Function
```

### 常見問題

- **Q1. 收不到入口網傳來的 seed?**
  MVC / Core 專案注意有一個 Validation 的 Config 要設,否則會接不到 POST 過來的
  資料(anti-forgery token 相關,參考
  https://exceptionnotfound.net/using-anti-forgery-tokens-in-asp-net-core-razor-pages/)。
  註:請設定單頁就好,請勿整個網站脫光裸奔。
- **Q2. 跳轉有時成功、有時失敗(驗證失敗或收不到 seed)?**
  注意網址的 http 是不是自己變成 https——IE 在轉換 https 時會把 POST 資料忘掉
  (IE 的 BUG),Edge 則正常。
- **Q3. 測試環境都成功、正式環境都失敗(驗證失敗)?**
  新建的 server 可能沒有 CryptUtil 的機碼,見上方「CryptUtil 環境架設」。

### Session Timeout 標準實作(SweetAlert2 倒數彈窗)

session timeout 時執行以下程式碼,倒數時間統一 **6 秒**。效果使用到
**SweetAlert2** 與 **Bootstrap 5.3**(https://sweetalert2.github.io/、
https://getbootstrap.com/docs/5.3/getting-started/introduction/)。

CSS(複製到專案內,`logout-loader-msg` 顏色可依各系統配色調整):

```css
.logout-loader-img {
    width: 32px;
    margin-right: 12px;
}
.logout-loader-msg {
    color: #000;
}
```

loader 圖示:`loader.gif` 在 Confluence「Session Timeout 處理方式」頁
(pageId 106561581)的附件 `loader.zip`,下載解壓縮後複製到專案下。

```js
let timerInterval;
Swal.fire({
    title: "您尚未登入系統或閒置過久\n請重新登入！",
    html: "<img src=\"loader圖片路徑\" class=\"logout-loader-img\" /><b class=\"text-danger\"></b> <span class=\"logout-loader-msg\">秒後自動返回登入頁！</span>",
    timer: 6000,
    color: "#334d4d",
    reverseButtons: true,
    denyButtonText: '回登入頁',
    showDenyButton: true,
    showConfirmButton: false,
    denyButtonColor: '#5c8a8a',
    allowOutsideClick : false,
    allowEscapeKey : false,
    didOpen: () => {
        const timer = Swal.getPopup().querySelector("b");
        timerInterval = setInterval(() => {
            timer.textContent = Math.ceil(Swal.getTimerLeft() / 1000);
        }, 100);
    },
    willClose: () => {
        clearInterval(timerInterval);
    }
}).then((result) => {
    if (result.dismiss === Swal.DismissReason.timer || result.isDenied) {
         window.location.href = "https://ztaag.cotabank.com.tw/AccessGateway";
    }
});
```

回跳網址依入口而異:

- **WEB 版員工入口網**:`https://ztaag.cotabank.com.tw/AccessGateway`
- **行動裝置入口網**:`https://zta.cotabank.com.tw/Cota2024/Home/MenuBoard`
- 專案可從兩個入口登入時,用 `HttpContext.Request.Host.Host` 判斷 timeout 後
  該回哪一個入口網。

## 掛 HAProxy 時的整合寫法

**命名與環境規則**(找系統組設定):

- Proxy Server 命名規則見 Confluence 命名規則頁;站台名稱 = `prj` + 自定義名稱
  (建議用專案名稱),例如專案 eLoan → hostname `prjeLoan.cotabank.com`。
- **開發階段**:請系統組設定開發環境 host,IP 指到 `192.168.251.112`(HAProxy)。
- **上線階段**:請系統組設定正式環境 host,IP 指到 `10.1.103.140`(HAProxy)。
- HAProxy 負載平衡器管理、Client IP 檢查各有專門頁面(見下方參考)。

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
- 【入口網站】串接入口網程式碼範例: https://svrconf.cotabank.com/pages/viewpage.action?pageId=67342248
- 【入口網站】CryptUtil加密簽章: https://svrconf.cotabank.com/pages/viewpage.action?pageId=3048856
