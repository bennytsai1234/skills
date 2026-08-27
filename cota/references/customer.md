# CotaUtility.Customer

## 何時適用

需要保護客戶真實統一編號(法人統編、身分證、居留證、聯名戶、OBU 客戶等)的專案——
把真實統編轉成亂數統編儲存/傳遞,或需要對個資欄位(姓名、生日、地址、Email、統編)做
遮罩顯示。支援 .NET Core / .NET Framework 4.7.2+。

## 偵測特徵

- 資料庫、Log、或前端顯示裡**明碼儲存/輸出真實統一編號**
- 自己刻的正規表示式做姓名/生日/地址/電話遮罩(例如手動字串切割加 `*` 或 `〇`)
- 自己刻的統編↔代碼對照表邏輯(而不是用套件提供的 IDRNG 服務)

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.Customer"`
- 程式碼注入 `IIDRNG` 或用 `MaskExtensions` 擴充方法(`.MaskChineseName()` 等)

## 已用時的正確用法檢查清單

- [ ] 亂數統編轉換(`GetCustomerRandomID`/`GetCustomerRealID` 及其批次版本)是否用在
      所有需要對外/儲存真實統編的路徑上,沒有漏掉某些查詢直接回傳明碼
- [ ] 遮罩方法是否用對類型(中文姓名用 `MaskChineseName`、身分證/統編用
      `MaskIDOrNumber`,不要混用導致遮罩位置不對)
- [ ] `GetCustomerRandomID`/`GetCustomerRealID` 回傳的 `ResultDataModel.Result` 是否
      有正確反序列化成 `IDRNGT` 才取值(常見漏洞:直接把 `Result` 當字串或忽略反序列化,
      導致拿到的其實是 JObject 而非預期資料)

## UnifiedNumberType 列舉(統編身分別)

| 值 | 說明 |
|---|---|
| UNKNOWN | 未知 |
| LZ | 公司戶 |
| NF | 個人戶 女性 |
| NM | 個人戶 男性 |
| OL | OBU 客戶 公司戶 |
| ON | OBU 客戶 個人戶 |
| JOINT_ACCOUNT | 聯名戶 |

## IDRNGT / 各方法回傳模組欄位表

`ResultDataModel`:`Success`(bool,預設 false)、`Result`(object,成功時需反序列化成下列對應
型別,失敗時是錯誤訊息字串)。

`IDRNGT`(單筆結果反序列化目標,及 `BatchResultModel.SuccessList` 的 Value 型別):
`Id`(string,實際統一編號)、`RngId`(string,亂數統一編號)、`Type`(UnifiedNumberType)。

`BatchResultModel`:除 `Success`/`Result` 外,另有 `SuccessList`
(`Dictionary<string,IDRNGT>`)、`FailedList`(`Dictionary<string,string>`,Value 為失敗原因)。

`ChangeResultModel`:`Success`/`Result` 之外,直接帶 `RngId`(string)、`Type`
(UnifiedNumberType),不用再反序列化。

`IDBaseDateResultModel`:`Success`/`Result` 之外,`Data`(型別 `RealID_History`)。

`RealID_History`:`Id`(string)、`RngID`(string)、`Type`(UnifiedNumberType)、
`CreateDt`(DateTime)、`ProjectName`(string,變更來源)。

`IdHistoryResultModel`:`Success`/`Result` 之外,`HistoryList`(`List<RealID_History>`)。

`GetCustomerIDBaseDate` 的 `baseDate` 參數支援多種日期字串格式解析(COBOL 精確格式含毫秒
`yyyyMMddHHmmssfff`、常見格式 `yyyy-MM-dd HH:mm:ss` 等一系列格式),使用時傳 `DateTime`
即可,不用自己處理字串格式。

## 未用時的替換建議

```csharp
// DI 注入
builder.Services.AddScoped<IIDRNG, IDRNG>();

// 使用 —— 注意:Result 要反序列化成 IDRNGT 才能取值,不是直接讀 Result
ResultDataModel result = await rngService.GetCustomerRandomID("A123456789");
if (result.Success)
{
    IDRNGT idrngt = (result.Result as JObject)?.ToObject<IDRNGT>()!; // 或用 JsonConvert.DeserializeObject
    // idrngt.Id = 原始統編, idrngt.RngId = 亂數統編, idrngt.Type = UnifiedNumberType
}
else
{
    // result.Result 此時是 string,存放錯誤訊息
}

// 批次版本回傳 BatchResultModel,直接讀 SuccessList(Dictionary<string,IDRNGT>)/
// FailedList(Dictionary<string,string>),不用額外反序列化
BatchResultModel batch = await rngService.GetCustomerBatchRandomID(new List<string> { "A123456789" });

// 遮罩擴充方法(這幾個不用反序列化,直接回傳字串)
"陳小明".MaskChineseName();          // 陳〇〇
"A123456789".MaskIDOrNumber();       // A12345〇〇〇〇
"aa_webbox@mail.taipei.gov.tw".MaskEmail(); // 〇〇@mail.taipei.gov.tw
```

其餘方法回傳型別各自不同,要注意取值方式:
- `ChangeID` → `ChangeResultModel`,`RngId`/`Type` 直接在物件上,不用反序列化
- `GetCustomerIDBaseDate` → `IDBaseDateResultModel`,實際資料在 `.Data`(型別
  `RealID_History`:Id/RngID/Type/CreateDt/ProjectName)
- `GetCustomerHistory(id, isOriginal)` → `IdHistoryResultModel`,清單在
  `.HistoryList`(`List<RealID_History>`)。**`isOriginal` 參數容易搞混**:傳入
  `id` 是真實統編就給 `true`,是虛擬統編就給 `false`,給錯會查不到變更軌跡

`MaskExtensions` 還有 `MaskRomanizedName` / `MaskEnglishName` / `MaskBirthday` /
`MaskAddress` / `MaskLandNumber`。

## 適用情境提醒

只有專案確實處理到真實統一編號或其他 PII 欄位時才建議,不要對完全不碰個資的專案
硬套。

COBOL 端對應呼叫方式(透過 `web_access` 呼叫外部程式):

- **來源白名單**:COBOL 呼叫會驗證來源,允許的白名單是**資料夾名稱**,使用時須自行
  指定 AppDomain,格式 `目錄名稱/程式名稱`(例如 `dp2/dpe110`、`ln2/lapply`)。
- **API 位址**(注意大小寫):
  - 單筆:`https://prjCustomerRNG.cotabank.com/CustomerRNG/api/COBOLService/GetRngID`
    傳入 JSON `{ "ID":"", "AppDomain":"" }`;回傳字串用 tab 切割,欄位順序:
    1. 執行結果 Y/N 2. 成功=統一編號/失敗=失敗訊息 3. 成功=虛擬統編 4. 成功=身分別
  - 批次:`https://prjCustomerRNG.cotabank.com/CustomerRNG/api/COBOLService/GetBatchRngID`
    傳入 AppDomain + 上傳 text 檔案;回傳檔案一行一個統編,同樣 tab 切割、欄位順序相同。

## 統編/證號驗證演算法參考文件

需要自己驗證統編/證號格式(而非亂數化)時,Confluence 有標準演算法文件,不要自己
憑印象寫檢查碼邏輯:

- **營利事業統一編號**(8 碼,權重 1,2,1,2,1,2,4,1,加總後個位數進位再 mod 5,
  含第 7 碼為 7 的特例):pageId 121734791
- **新式統一證號驗證**(身分證):pageId 121734827
- **舊式外來人口統一證號編碼原則**:pageId 121734847

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=119177439
