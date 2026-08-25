# CotaXMaster 跨瀏覽器主控服務

## 何時適用

網頁需要呼叫本機 32-bit DLL(金融卡/員工卡元件、印表機、掃碼器等桌面功能),或需要
啟動可與桌面互動的獨立程式(需跑在前景)的專案。CotaXMaster 是安裝在用戶端的
Windows 服務,網頁端以 HTTPS JSON POST 跟它溝通,解決瀏覽器沙箱無法直接碰本機
DLL/桌面的問題。

**注意**:這是**用戶端**服務,不是伺服器端 NuGet 套件——正式環境由系統組統一發派
到全行自動安裝,開發時手動註冊。

## 偵測特徵

- 網頁端直接 `LoadLibrary` / P/Invoke 呼叫本機 DLL(瀏覽器環境做不到,通常是
  舊式 ActiveX/IE 插件寫法)
- 自己刻的本地 IPC(Socket/NamedPipe)讓網頁呼叫桌面程式
- 金融卡/員工卡操作元件的呼叫邏輯(另見 Confluence「金融卡、員工卡操作元件」頁)

## 安裝與開發

- 安裝:以管理者身分執行 `CotaXMasterSetup.exe`(目前最新版 V1.0.1.3, 2025/02);
  正式環境由系統組統一發派到全行自動安裝。
- 開發時手動註冊:`CotaXMaster.exe /service`
- DLL 與 `CotaXMaster.exe` 需同一資料夾;其他相關執行檔放 `CotaXMaster\progs` 子資料夾。
- 溝通方式:皆用 JSON 格式 POST 給 `https://localhost:21443/`。

## 兩個端點

**功能 1:呼叫 DLL** — `POST https://localhost:21443/rundll`

```json
{
  "dll": "XXX.dll",
  "method": "XXX_fun",
  "params": "<params to dll>"
}
```

`params` 可以是 JSON 物件、字串或數字。

**功能 2:啟動可與桌面互動的程式**(需跑在前景時)— `POST https://localhost:21443/invokeProg`

```json
{
  "appName": "XXX.exe",
  "cmdLine": "..."
}
```

`cmdLine` 為 optional。

## 回傳值

```json
{ "result": null, "retCode": 16830000 }
```

- `retCode` 介於 16830000~16839999 之間時為 CotaXMaster 本身的回傳值:
  `16830000` 成功,其餘 1683 開頭的八碼代表錯誤,`result` 為錯誤訊息字串。
- 其他 `retCode` 為 DLL 自行定義的回傳值。

## DLL 端要求

- DLL 需為 **32-bit**。
- 被呼叫的介面需定義為:

```c
typedef int (*DLLFunction)(const char*, char**);
```

  - 參數 1:input,由網頁端傳給元件的資料(JSON 物件或字串)。
  - 參數 2:output,元件將執行結果或錯誤訊息傳回;**必須明確配置記憶體**,
    由主控程式使用完後釋放。
  - 回傳值 int 由元件自行定義。

## 呼叫 DLL vs 啟動獨立程式

| | 呼叫 DLL | 啟動獨立程式 |
|---|---|---|
| 用途 | 提供與底層互動的 API | 需要 UI/前景的動作 |
| 方式 | LoadLibrary 動態載入 | 以 AD 身分執行,多一個 Process |
| 限制 | 無法執行需要 UI 的動作(改用啟動獨立程式) | 需處理 IPC(Socket/NamedPipe) |

## 跨瀏覽器元件生態(CotaXMaster 周邊)

跨瀏覽器架構分三區塊:(1) javascript 跨瀏覽器套件(實作 UI、提供網頁呼叫介面)、
(2) CotaXMaster 主控服務(網頁 js 與元件端的溝通橋樑)、(3) dll/exe 跨瀏覽器元件
(實作原 IE 前端元件功能)。另有 **XBCenter** 專案(跨瀏覽器程式管理網頁)管理 dll/exe
版本並提供下載連結,讓 CotaXMaster 自動下載更新。

已知的跨瀏覽器元件(前端 js 套件,皆需先安裝 CotaXMaster):

| 元件 | 用途 | Confluence pageId |
|---|---|---|
| SealStarter | 印鑑啟動(行員建檔/幹部放行;後端 SealTrigger.exe 放 CotaXMaster\progs) | 67338941 |
| DocTool | 檔案上傳(電子公文、行內傳真;只有上傳沒有 FileInput) | 72354857 |
| FileSelector | 選檔元件(程式抄送選檔、RZSZ 選檔) | 72354859 |
| Twain | 掃描套件(透過 CotaXMaster 與 TwainUI.exe 溝通;CallTwain 錯誤 2000 = CotaXMaster 服務沒跑) | 72362375 |
| ImageView | 掃描/選圖的縮圖 List 顯示與大圖檢視(行內傳真) | 72362393 |

跨瀏覽器元件使用說明:http://192.168.251.198/note/index.html

## 參考

- CotaXMaster 溝通規則: https://svrconf.cotabank.com/pages/viewpage.action?pageId=67338932
- 跨瀏覽器前端服務(架構總覽): https://svrconf.cotabank.com/pages/viewpage.action?pageId=67338927
