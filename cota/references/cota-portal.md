# CotaUtility.CotaPortal

## 何時適用

需要串接**員工入口網**的 ASP.NET Core 專案——內部系統從入口網選單進站,由入口網交遞
身分,並提供「回入口網」。目標 **net8.0**。**JWT 機制**,依賴 `CotaUtility.CotaJWT`。

## 定位:與 network.md 舊 hiseed/RSASign 機制的關係(重要)

`references/network.md`(hiseed/hisignedhash + `CryptUtilLib.IRSAHandler` RSASign)與
`references/cota-employee.md`(`EmpCardModel.GetByCryptUtil`,需 COM 元件註冊)描述的是
**舊的入口網簽章機制**。**CotaPortal 是新的 JWT 版封裝**,對新專案串接入口網優先用這個:

- **公鑰自動抓**:`VerifyCotaPortalToken` 內部向入口網 API 取公鑰並快取,驗證失敗會重抓
  重試(處理金鑰輪替)——**不需持有 RSA 私鑰**。
- **純 managed net8.0**:**不需 COM 元件註冊/匯入機碼**(舊 EmpCardModel 才需要)。
- **入口網 API 位址寫死在套件**:`CotaApiBaseUrl = https://prjCotaAP.cotabank.com/CotaAP`
  (常數,非設定)——不需設定 base url,但**部署主機要連得到 `prjCotaAP.cotabank.com`
  與入口網 `zta.cotabank.com.tw`**。

掃描既有專案時,若看到專案自己用 hiseed/RSASign 或 EmpCardModel 手刻入口網串接,可提醒
新做法有 CotaPortal;但既有專案用舊機制且運作正常,不強制遷移。

## 偵測特徵(專案有沒有在做「串接入口網」這件事)

- 有「回入口網」按鈕/連結,或導回 `zta.cotabank.com.tw/.../MenuBoard` 的邏輯
- 手刻的入口網簽章驗證(驗 `hiseed`/`hisignedhash`,或自己組 seed + RSASign)
- 進站時從 query/header 取 token 或 empNo 建立登入 Session 的邏輯
- 直接呼叫 `prjCotaAP.cotabank.com/CotaAP/api/Utility/*`(GetPK / GetAccessItem /
  GetGoBackToken)

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaPortal"`
- `Program.cs` 有 `services.AddCotaPortal()`
- 注入 `CotaUtility.CotaPortal.CotaPortal`,呼叫 `VerifyCotaPortalToken` / `GetGoBackToken`

## 精確 API(已反編譯 1.0.0 確認)

- `IServiceCollection AddCotaPortal(this IServiceCollection services)`
  ——**無參數**;內部已呼叫 `AddCotaJWT(services, null)`、把 `CotaPortal` 註冊為 **Scoped**。
  服務 ctor 依賴 `IDistributedCache`、`ILogger<CotaPortal>`、`CotaJWTService`。
- `CotaPortalTokenResult VerifyCotaPortalToken(string token)`
  → `{ bool IsSuccess; string EmpNo; string ErrorMessage; }`
  驗入口網 JWT(自動抓/快取公鑰),取 payload 的 `EncEmpNo`→呼叫 GetAccessItem API 換回
  明文 EmpNo,並在 `IDistributedCache` 快取 `AccessToken:{EmpNo}` 供之後 GoBack 用。
- `CotaPortalGoBackTokenResult GetGoBackToken(string empNo)`
  → `{ bool IsSuccess; string EncGoBackToken; string ErrorMessage; }`
  讀快取的 `AccessToken:{empNo}`(找不到即失敗)→呼叫 GetGoBackToken API 取回程 token。
- 依賴套件:`CotaUtility.CotaJWT`(通用 JWT 簽/驗庫;`AddCotaJWT(services, Action<CotaJWTOptions>)`,
  `CotaJWTOptions` 為 token 效期/演算法/快取,**不含入口網位址**)。

`CotaApiBaseUrl` 常數指向的三個端點:`/api/Utility/GetPK`(取公鑰)、`/GetAccessItem`
(EncEmpNo→EmpNo+AccessToken)、`/GetGoBackToken`(產回程 token)。

## 已用時的正確用法檢查清單

- [ ] 有註冊 `IDistributedCache`(CotaPortal ctor 需要)——單機用 `AddDistributedMemoryCache()`,
      多機/HA 用 `CotaUtility.CotaRedis`(見 `references/cota-redis.md`)。**少了它 DI 會失敗**。
- [ ] **GoBack 依賴進站時快取的 `AccessToken:{EmpNo}`**:多機部署或 App 重啟後 in-memory
      快取遺失,`GetGoBackToken` 會回「於 Cache 中未能找到對應 AccessToken」。要多機就得把
      `IDistributedCache` 換成共享的(CotaRedis),否則維持單機。
- [ ] 進站驗證通過後有建立 **Session**,並符合入口網標準:**20 分鐘 timeout、6 秒倒數
      導回入口網、`Cookie.Name` 具名**(見 `references/network.md`、`references/mobile-web.md`)。
- [ ] 角色查詢仍走 `CotaUtility.PermProvider`(以 EmpNo 查),CotaPortal 只負責身分,不管角色。
- [ ] 用了 CotaPortal 就**不要並存**舊的 hiseed/RSASign/EmpCardModel 手刻邏輯。
- [ ] **姓名/部門**:token 只給 **EmpNo**,CotaPortal 不提供姓名/部門。要顯示「部門·姓名」
      需另一來源(CotaEmployee 或共用員工 DB view;CotaNuGet 目前無獨立 CotaEmployee 套件,
      見 `references/cota-employee.md`),向系統組確認入口網專案的標準查法。

## 未用時的替換建議(ASP.NET Core net8.0,單機)

```csharp
// DI
builder.Services.AddDistributedMemoryCache();          // CotaPortal 需要 IDistributedCache(單機 in-memory)
builder.Services.AddCotaPortal();                      // 內含 AddCotaJWT + 註冊 scoped CotaPortal
builder.Services.AddSession(o =>
{
    o.IdleTimeout = TimeSpan.FromMinutes(20);          // 入口網標準:20 分逾時
    o.Cookie.Name = ".專案名稱.Session";               // 具名,避免多專案共用主機互相覆蓋
    o.Cookie.HttpOnly = true; o.Cookie.IsEssential = true;
    o.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});
// pipeline: app.UseSession() 要在 UseAuthentication() 之前

// 進站(入口網以 token 導向此處):驗證→取 EmpNo→寫 Session→導首頁;失敗導回入口網
var result = cotaPortal.VerifyCotaPortalToken(token);
if (result.IsSuccess) { HttpContext.Session.SetString("EmpNo", result.EmpNo); /* ... */ }

// 回入口網:產 GoBack token→導回入口網選單頁
var back = cotaPortal.GetGoBackToken(empNo);
// Redirect 到 https://zta.cotabank.com.tw/Cota2024/Home/MenuBoard,附上 back.EncGoBackToken
```

身分整合建議:寫一個自訂 `AuthenticationHandler`,每個請求由 Session 的 EmpNo 還原
`ClaimsPrincipal`(Name=EmpNo),未登入時挑戰動作導回入口網;角色由 PermProvider 的
`IClaimsTransformation` 補上。這樣 `[Authorize]`/`[Authorize(Roles=...)]` 不用改。

## 待確認的入口網交遞契約(DLL 推不出來,需系統組/Confluence)

CotaPortal 只負責「拿到 token 後驗證」與「產回程 token」,**不規定 token 怎麼在入口網與
專案之間傳遞**。以下兩點要跟系統組確認,程式先以合理預設實作、以設定開關校正即可:

1. **進站**:入口網用什麼方式把 JWT token 帶進專案(query / form / header)、參數名為何。
2. **回程**:拿到 `EncGoBackToken` 後,用什麼方式帶回入口網
   (`https://zta.cotabank.com.tw/Cota2024/Home/MenuBoard`;query 參數名?GET 或 POST?)。

## 參考

- Confluence 待補(系統開發專區 > WEB開發工具相關;本套件原未在 skill 收錄,
  於 CotaNuGet `\\192.168.251.238\data\CotaNuGet` 現場確認,版本 1.0.0)。
- 入口網簽章舊機制 / Session Timeout:`references/network.md`、`references/mobile-web.md`。
