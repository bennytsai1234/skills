# CotaUtility.JavaCall

## 何時適用

需要呼叫 COBOL、Java 或其他主機服務(tpcall 類型整合)的專案。目標 netstandard2.0。
**內建 Big5 轉碼**,不需要另外裝 Big5ToWideChar 套件。

v1.0.1(2024.03.04)新增逾時參數(可設 1~300 秒,但連線程式本身有上限:Java Server 85
秒、COBOL Server 30 秒、HAProxy 60 秒,設太大也沒用)跟完整錯誤訊息回傳。

## 偵測特徵

- 自己寫的 tpcall/socket 層級主機整合程式碼
- 單獨依賴 `Big5ToWideChar` 套件做編碼轉換(可整合進 JavaCall,不用兩個套件並存)
- 手刻的 Big5 ↔ Unicode 轉碼邏輯

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.JavaCall"`
- 程式碼用 `CotaJavaCall` 類別 / `JavaCallByteInputModel` / `JavaCallByteOutputModel`

## 已用時的正確用法檢查清單

- [ ] `timeout` 參數是否對應到實際呼叫的主機類型(COBOL/Java/HAProxy 各自的上限不同,
      設定超過上限的值沒有意義)
- [ ] 是否有處理 `JavaCallByteOutputModel.ErrorCode`/`ErrorMessage`,而不是只看有沒有
      拋例外(部分錯誤是透過回傳的 ErrorCode 表達,不是例外)

## 未用時的替換建議

兩種呼叫模式,依情境選:

```csharp
// 批次/多次呼叫同一連線 —— 用實例,結束後要記得 Close()
var big5 = new Big5ToWideCharToString(Encoding.UTF8.GetBytes("data"), CharCode.UTF8);
var input = new JavaCallByteInputModel { ServerName = "Server", InputData = big5.ToBig5E() }; // 呼叫 COBOL 要用 ToBig5E() 避免中文異常

var cotaJavaCall = new CotaJavaCall(JavaCallServerType.COBOL);
JavaCallByteOutputModel output = cotaJavaCall.CallByByte(input);
if (output.ErrorCode == 0) // 注意:文件參數表寫 ErrorCode 是 string,但範例用 ==0 比較,實際型別以套件 IntelliSense 為準,不要照抄文件表格
{
    big5.SetBytes(output.OutputData, CharCode.BIG5E);
    string result = big5.ToString();
}
else
{
    string error = output.ErrorMessage;
}
cotaJavaCall.Close(); // 批次模式務必手動關閉連線

// 單次呼叫 —— 用靜態方法,自動關閉連線,不用手動 Close
JavaCallByteOutputModel output2 = CotaJavaCall.CallServerByByte(
    JavaCallServerType.COBOL, input, timeout: 85); // 85 對應 Java Server 上限
```

**Big5 轉碼是內建的**:用 `Big5ToWideCharToString` 類別(`ToBig5E()` 編碼輸出、
`SetBytes(bytes, CharCode.BIG5E)` + `ToString()` 解碼輸入)。若專案已經同時依賴獨立的
`Big5ToWideChar` 套件,且核心需求就是主機呼叫,可以評估整併成只用 JavaCall,減少一個
套件依賴。

## 參數模組(命名空間 CotaUtility.Models / CotaUtility.Const)

| 模組 | 欄位 | 說明 |
|---|---|---|
| `JavaCallStringInputModel` | `ServerName`、`InputData` | 字串輸入(有無參數與 `(string, string)` 兩個建構子) |
| `JavaCallStringOutputModel` | — | 字串輸出 |
| `JavaCallByteInputModel` | — | 位元輸入(呼叫 COBOL 用這個搭配 Big5 轉碼) |
| `JavaCallByteOutputModel` | `ErrorCode`、`ErrorMessage`、`OutputData` | 位元輸出 |
| `JavaCallServerType`(CotaUtility.Const) | `COBOL` / `JAVA` | 呼叫 COBOL 主機 / JAVA 主機 |

各模組的完整欄位/方法說明在 Confluence 子頁(pageId 65700014/65700028/65700063/
65700080/65700089)。

**非 txdo server 的 COBOL server**(較少見的情境)要用更底層的 `CJavaCall` 類別
(`tpinit`/`tpcall`/`close`/`get_error_str`),不是 `CotaJavaCall`,遇到這種情境對照
Confluence 頁面上的獨立範例。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=94569494
