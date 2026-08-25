# CotaUtility.CotaNotification

## 何時適用

需要發送/取消內部 CotaInfo 系統通知訊息的專案(例如針對特定卡號、主管、幹部或員工發送
通知)。目標 netstandard2.0。套件內含 `DataEnc.dll` + `NotifyAPI.dll`。

## 偵測特徵

- 自訂的「發通知/發訊息」邏輯,直接呼叫內部通知/公告相關 API 或資料庫寫入 CotaInfo
  相關的表
- 自己刻的訊息取消/撤回邏輯

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaNotification"`
- 程式碼使用 `CotaNotification.Send(ref NotificationModel)` /
  `CotaNotification.Disable(...)`

## NotificationModel 完整欄位表

| 屬性 | 型別 | 預設值 | 說明 |
|---|---|---|---|
| SenderEmpNo | string | 空字串 | 發送人員員編 |
| SenderDpCode | string | 空字串 | 發送單位營業代碼(DpCode) |
| NotifyDpCode | string | 空字串 | 通知單位營業代碼(DpCode) |
| ActiveDateTime | DateTime | DateTime.Now | 生效時間 |
| CancelType | int | 1 | 取消類型(0:不可自行取消,1:可自行取消) |
| NotifyType | int | 0 | 通知類型(0:針對卡號,1:主管,2:幹部,3:非主管幹部的員工) |
| ContentType | int | 1 | 內容格式(0:HTML,1:純文字) |
| Content | string | 空字串 | 訊息內容 |
| NotifyEmpNos | string[] | null | 通知人員清單 |
| NotifyId | string | 空字串 | 發送成功回傳的訊息編號(用於之後 Disable) |
| ErrorMessage | string | 空字串 | 發送失敗回傳的錯誤訊息 |
| RetCode | int | - | 發送結果代碼,0 為成功 |

方法簽章:`void Send(ref NotificationModel info)`(注意是 `ref` 參數,結果寫回同一個物件)、
`int Disable(string notifyId, string[] disableEmpNos, out string errorMessage)`。

## 已用時的正確用法檢查清單

- [ ] 發送後是否檢查 `NotificationModel.RetCode == 0` 才視為成功,而不是假設呼叫沒
      拋例外就代表發送成功
- [ ] `CancelType`/`NotifyType`/`ContentType` 是否依實際需求正確設定(例如需要讓收訊
      人自行取消,`CancelType` 要設 1)

## 未用時的替換建議

```csharp
var notifyInfo = new NotificationModel
{
    SenderEmpNo = "000000",
    SenderDpCode = "AAAA",
    NotifyDpCode = "AAAA",
    NotifyEmpNos = new string[] { },
    CancelType = 1,
    NotifyType = 0,
    ContentType = 1,
    Content = "訊息內容"
};
CotaNotification.Send(ref notifyInfo);
if (notifyInfo.RetCode == 0)
{
    // 成功,notifyInfo.NotifyId 可用來之後取消
}
```

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=94569373
