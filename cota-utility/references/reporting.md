# CotaUtility.Reporting

## 何時適用

需要把網頁內容轉成 PDF 報表的專案——取代 Crystal Report / Reporting Service 的方案,
改成用網頁畫報表再轉 PDF。v1.0.0 用 wkhtmltopdf 實作(`PdfGenerator`),v1.0.1 新增
puppeteer-html-pdf 實作(`PuppeteerHtmlToPdf`),v1.0.2(2025.09)新增 PDF 加浮水印
(文件資訊、加密)。

**v1.0.2 浮水印**:`Reporting.WaterMarkGeneratorAsync(WaterMarkGeneratorRequest, byte[] pdf, timeout)`
回傳 `ResultModel`(`Success`/`Pdf`/`Message`)。`WaterMarkGeneratorRequest` 含
`SystemName`/`RptName`/`User`、`DocInfo`(Author/Title/Subject/UserPwd)、`Watermark`
(Text1/FontSize1/Repeat/Text2/FontSize2)。**PDF 請勿設定權限**,避免檔案無法開啟。

## 偵測特徵

- 直接呼叫 wkhtmltopdf / puppeteer 相關套件產生 PDF,沒有經過 CotaUtility 包裝
- 還在用 Crystal Report / SSRS(Reporting Service)產報表
- 自己刻的「觸發頁面 → 產報表頁面」token 傳遞/驗證機制

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.Reporting"`
- 程式碼使用 `PdfGenerator` 或 `PuppeteerHtmlToPdf`

## 已用時的正確用法檢查清單

- [ ] 產生報表的網頁是否確實實作了 **Verify 驗證機制**——套件的設計原則是報表網頁必須
      驗證簽章資料才能取得參數,沒做這步等於報表頁沒有存取控管,任何人帶對的網址/參數
      就能觸發
- [ ] 報表參數是否透過 **POST** 傳遞,而不是直接帶在網址上(文件明確建議,雖然套件本身
      無法強制限制)
- [ ] 產生報表頁面若發生錯誤,是否有回傳自訂錯誤碼 499(讓 Report 端讀取 PDF 第一行當
      錯誤訊息顯示),而不是讓例外直接噴出未處理的 500

## 未用時的替換建議

```csharp
// 產生報表頁面(接收簽章驗證)
public IActionResult OnGet()
{
    string token = Request.Headers["Authorization"].ToString();
    if (token.Length <= 0)
        return StatusCode(499, "缺少簽章資料");
    // ... Verify 通過後才取得報表參數、渲染內容
}
```

## Watermark(浮水印,最多兩行,字型預設微軟正黑體)

| 參數 | 型別 | 預設值 | 說明 |
|---|---|---|---|
| Text1 | string | "" | 文字(第一行);若為空字串則不產生浮水印 |
| Text2 | string | "" | 文字(第二行) |
| Repeat | int | 1 | 重複次數 |
| RotationAngle | float | 30 | 旋轉角度 |
| FontSize1 | float | 36 | 第一行字體大小 |
| FontSize2 | float | 24 | 第二行字體大小 |
| Bolder1 | bool | false | 第一行是否粗體 |
| Bolder2 | bool | false | 第二行是否粗體 |
| Opacity | float | 0.2F | 不透明度 |

## DocInfo(文件資訊)

| 參數 | 型別 | 預設值 | 說明 |
|---|---|---|---|
| Title | string | "" | 標題 |
| Subject | string | "" | 主題 |
| Author | string | "三信商業銀行" | 作者 |
| Creator | string | "" | 建立者 |
| UserPwd | string | null | 文件開啟密碼,不需密碼時給空白字串(不能給 null) |
| Permission | PrintPermissionEnum | ALLOW_PRINTING | 列印權限 |

## PrintPermissionEnum(列印權限列舉)

| 值 | 說明 |
|---|---|
| ALLOW_SCREENREADERS | 允許用戶提取文本和圖形以供輔助設備使用(128位加密) |
| ALLOW_COPY | 允許用戶複製/提取文本和圖形,包括使用輔助技術(如螢幕閱讀器) |
| ALLOW_PRINTING | 允許列印 |
| ALLOW_ASSEMBLY | 允許插入、旋轉頁面和加書籤(128位加密) |
| ALLOW_FILL_IN | 允許用戶填寫表單欄位(128位加密) |

## ResultModel(執行結果)

| 屬性 | 型別 | 預設值 | 說明 |
|---|---|---|---|
| Success | bool | false | 執行結果 |
| Message | string | "" | 錯誤訊息 |
| Pdf | byte[] | null | PDF 內容,失敗時可能無值,錯誤訊息看 Message |

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=63602691
