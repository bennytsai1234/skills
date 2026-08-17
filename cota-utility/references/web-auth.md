# CotaUtility.CotaWebAuth

## 何時適用

需要以下任一驗證機制的專案:行動裝置生物辨識(FIDO2/WebAuthn)註冊與驗證、AD 帳密
驗證、OTP 驗證、或 AD+OTP 組合驗證。版本對應 Framework:1.0.0=.NET 5,2.0.0/3.0.0=.NET 8。
AD/OTP 的加解密採用 `DataEnc`。

**要用生物辨識功能的專案,需要提供來源給 CotaWebAuth 專案**(套件方需要額外設定)。

## 偵測特徵

- 自己刻的 WebAuthn/FIDO2 註冊或驗證流程
- 直接用 `System.DirectoryServices` / `PrincipalContext` 做 AD bind 驗證
- 自訂的 OTP 產生/驗證邏輯(產生驗證碼、比對、時效控制)
- 自訂的「AD + OTP 雙因子」驗證組合邏輯
- **ASP.NET Core 內建的 Windows 整合驗證**(`AddAuthentication().AddNegotiate()`、
  `AddAuthentication(NegotiateDefaults.AuthenticationScheme)`,或 IIS 設定裡開啟
  Windows Authentication)——這也是在做 AD 身分驗證,只是不是「自己刻的」,也不是
  CotaUtility。**不要因為找不到手刻特徵就判定 CotaWebAuth 不適用/略過**,這種情況要
  歸類到「有這個功能、但沒用 CotaUtility」,標「待確認」並列出現況,原因見下方
  「Windows Negotiate 的判斷方式」

## Windows Negotiate 的判斷方式

Windows 整合驗證(Negotiate/Kerberos)本身是業界標準做法,不是自刻程式碼,合不合適不是
單純的程式碼品質問題,而是**這間銀行內部政策**——是否要求所有系統統一走 CotaWebAuth
(例如為了統一的稽核/加密/日誌格式)不是能從程式碼判斷出來的事。掃描到這種情況時:

- **不要**直接判「不適用」略過(找不到自刻特徵不等於沒有 AD 驗證需求)
- **不要**直接判「該替換」強推(Windows Negotiate 是合法的標準做法,不是明顯的壞寫法)
- 列為「待確認」,說明現況(用 Windows Negotiate 做身分驗證,搭配 PermProvider 做權限
  查詢),並附上為什麼沒用 CotaWebAuth.VerifyAD 的可能原因(SSO 免密碼輸入的使用者體驗、
  不用自己處理加密傳輸),讓使用者自行判斷是否符合公司規範

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaWebAuth"`
- 程式碼呼叫 `VerifyAD` / `VerifyOTP` / `VerifyADOTP` /
  `CreateCredentialOption`/`CreateCredential`/`GetAssertionOption`/`VerifyAssertion`

## 已用時的正確用法檢查清單

- [ ] AD/OTP 相關輸入(帳號、密碼、OTP)是否都是**加密後**傳入(`EncEmpNo`/
      `EncADPassword`/`EncOTP`),沒有明碼直接帶入的情況
- [ ] 生物辨識流程是否照兩步驟順序執行:註冊要先
      `CreateCredentialOption` 再 `CreateCredential`;驗證要先
      `GetAssertionOption` 再 `VerifyAssertion`,不能跳步驟
- [ ] `UserVerificationType`/`AuthenticatorType` 是否符合實際安全需求(例如要求強制生物
      辨識驗證應設 `強制用戶驗證`,而不是預設寬鬆值)

## 未用時的替換建議

所有方法都是**靜態呼叫**(`CotaUtility.CotaWebAuth.CotaWebAuth` 類別的靜態方法),不是注入實例:

```csharp
// AD 驗證
var result = CotaWebAuth.VerifyAD(new ADAuthModelIn
{
    EncEmpNo = encEmpNo,
    EncADPassword = encPassword
});
if (result.IsSuccess) { /* 驗證通過,result.Data 取回覆資料 */ }

// AD + OTP 組合驗證
var result2 = CotaWebAuth.VerifyADOTP(new ADOTPAuthModelIn
{
    EncEmpNo = encEmpNo, EncADPassword = encPassword, EncOTP = encOtp
});

// 生物辨識註冊步驟一(Controller Action 範例)
var paramter = new CredentialOptionModelIn
{
    EmpNo = empNo,
    AttestationType = AttestationTypeEnum.直接驗證,
    AuthenticatorType = AuthenticatorTypeEnum.僅接受裝置內建驗證器,
    UserVerificationType = UserVerificationTypeEnum.不強制用戶驗證,
    RequireResidentKey = true
};
var option = CotaWebAuth.CreateCredentialOption(paramter);
```

前端需搭配 WebAuthn 標準 API(`navigator.credentials.create`/`navigator.credentials.get`),
註冊/驗證各兩支 API 要依序呼叫(先 Option 再 Create/Verify),並且要帶
Anti-Forgery Token(`RequestVerificationToken` header)。完整前端範例(含 base64url⇄
ArrayBuffer 轉換 helper、使用 sweetalert2 彈窗)在 Confluence 頁上,量較大不內嵌在這裡,
需要時附連結即可。

## ResultModelOut(通用回傳格式)

| 屬性 | 型別 | 說明 |
|---|---|---|
| IsSuccess | bool | 是否成功 |
| Data | string | 回覆資料 |
| ErrorMessage | string | 錯誤訊息 |

## AttestationTypeEnum(驗證器證明類型)

| 值 | 說明 |
|---|---|
| 不驗證 = 0(alias "none") | 驗證器不進行驗證,AAGuid 以 0 填充 |
| 間接驗證 = 1(alias "indirect") | 驗證器透過替換 AAGuid 進行匿名證明 |
| 直接驗證 = 2(alias "direct") | 驗證器提供最直接的證明訊息 |

## AuthenticatorTypeEnum(驗證器類型)

| 值 | 說明 |
|---|---|
| 所有驗證器皆可 = 0 | 不限制 |
| 僅接受裝置內建驗證器 = 1(alias "platform") | 如手機指紋/臉部辨識 |
| 僅接受外接驗證器 = 2(alias "cross-platform") | 如 USB 硬體金鑰 |

## UserVerificationTypeEnum(用戶驗證類型)

| 值 | 說明 |
|---|---|
| 強制用戶驗證 = 1(alias "required") | 必須叫用裝置上的使用者驗證方法 |
| 不強制用戶驗證 = 2(alias "preferred") | 有則用,沒有可略過 |
| 不關心用戶驗證 = 3(alias "discouraged") | 不採用,但部分裝置仍可能執行 |

安全性要求高的場景(例如登入、交易確認)應該用「強制用戶驗證」+「僅接受裝置內建驗證器」;
如果專案掃描到用「不關心用戶驗證」卻是敏感操作情境,值得在回報時特別標注。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=102236690
