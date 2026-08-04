# 傳輸層保護不足：快速判讀

在題目類別涉及「敏感資訊傳輸無保護措施」、cleartext transmission 或 insufficient transport layer protection 時載入本參考。

## 高訊號模式

### 1. 以 GET 傳送密碼或個資

- `BeginForm(..., FormMethod.Get)` 會把整個表單模型放入 query string。
- 若表單含 password、token、個資或其他秘密，表單宣告所在的候選區塊通常就是答案；不要只選 submit button。
- 即使網站使用 HTTPS，query string 仍可能出現在歷程、proxy、伺服器／分析 log、Referer 或其他 URL 記錄中。

### 2. 未加密的 SMTP 傳送敏感內容

- `SmtpClient.EnableSsl = false`、明確的明文 SMTP 或缺少 TLS 設定，表示郵件通道未受保護。
- 若候選區塊是組成郵件 body 的姓名、生日、電話、Email、地址、密碼重設連結或 token，將它與實際 `TrySend`／`client.Send` 路徑連起來再判斷。
- 候選不一定包含 `EnableSsl` 那一行；若題目候選標記的是敏感內容區塊，答案應使用頁面提供的完整候選行號，並以傳輸設定作為佐證。

### 3. HTTP endpoint 缺乏 HTTPS 強制

- 先查基底控制器、全域 filter、middleware、web server 設定與實際 URL。
- 只有在確認沒有其他層強制 HTTPS，且該 endpoint 實際接收或回傳敏感資料時，才把「缺少 `[RequireHttps]`」列為直接答案。
- 不要只因為一個 GET／POST 方法沒有看到 attribute 就判定漏洞；這通常是需要驗證的推論。

## 常見干擾項

- anti-forgery token 只處理 CSRF，不等於傳輸加密。
- `Authorize`、角色檢查與 throttling 處理存取控制或濫用，不等於 TLS。
- 對資料庫欄位做 AES／IV 加密是靜態資料保護，不代表網路傳輸安全。
- 一般 GET、一般 POST、錯誤訊息或輸入驗證若沒有敏感資料流，不應只因方法名稱而選取。

## 快速交叉驗證

1. 找出敏感資料欄位或秘密 token。
2. 找出真正的傳輸 sink：表單提交、HTTP client、SMTP client、redirect URL 或 response。
3. 確認該 sink 的保護設定與全域／基底補強。
4. 把結論映射回題目實際提供的候選區塊，保留完整檔名與行號。

## 可泛化的例子

- `Register.cshtml:8` 的 `BeginForm(..., FormMethod.Get)`，若同一表單包含 password，屬於把秘密放入 URL 的高訊號候選。
- `EmailService.cs:70-74` 組成個資郵件內容，若同一路徑的 SMTP client 設為 `EnableSsl = false`，屬於敏感資料經未加密郵件通道傳送的高訊號候選。
