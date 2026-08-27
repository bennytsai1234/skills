# 行動裝置網頁開發(行動入口網專案)

專案要上**行動裝置入口網**(員工用手機/平板從行動入口網進來的網頁)時的標準。
跟一般內部 WEB 專案的差異集中在部署主機、hostname、UI 原則與幾項強制設定。

## 部署

- WEB 專案主機:`SvrMobile_AA01`、`SvrMobile_AA02`
- hostname 統一:`zta.cotabank.com.tw`
- HAProxy:`SvrMix_M`,狀態頁 `https://svrmix_m.cotabank.com/ServerStats`
- 務必確認專案有上到 SvrMobile 主機群(可透過開發環境的程式異動系統執行抄送);
  測試用行動設備向系統組申請(數銀、行內網頁應用、外匯財會組各有一台測試用平板,
  其他組請洽系統組)。

## 開發原則(強制)

1. **UI 設計須符合 RWD**。
2. **入口網簽章驗證**(hiseed/hisignedhash,見 `references/network.md`)。
3. **回入口網處理方式**(見下方)。
4. **Session timeout 處理方式**(統一 20 分鐘、6 秒倒數,見 `references/network.md`)。
5. **版面配置統一**:左上角功能選單、右上角回入口網按鈕。
6. **各覆核動作需加上生物辨識驗證**(CotaWebAuth FIDO2,見
   `references/web-auth.md`)。
7. **CotaRedisSession 要加 Cookie.Name 設定**(避免多專案共用同一台主機時
   session cookie 互相覆蓋):

   ```csharp
   builder.Services.AddCotaRedisSession(options =>
   {
       options.Cookie.Name = ".專案名稱.Session";
   });
   ```

8. **HSTS 設定**:

   ```csharp
   builder.Services.AddHsts(options =>
   {
       options.Preload = true;
       options.IncludeSubDomains = true;
       options.MaxAge = TimeSpan.FromDays(365);
   });

   // pipeline:
   app.UseHsts();
   ```

9. **三信 Logo**:官方素材在 Confluence「行動裝置網頁開發」頁(pageId 106561578)
   的附件 `logo_svg.zip`、`logo_白字.zip`(含白字版與中文字白字版)。

## 回入口網處理方式

「回入口網」按鈕要製作簽章資料導回入口網:

- 入口網網址:`https://zta.cotabank.com.tw/Cota2024/Home/MenuBoard`
- `hiseed` 由 8 個參數以 `$` 串接(員工編號、員工姓名、上個網頁 load 的時間、
  讀卡機卡片號碼、讀卡機名稱、入口網站登入時間、晶片卡序號、行動裝置 1/0);
  「上個網頁 load 的時間」填**專案所在主機目前時間**。
- seed 組合後透過 `CryptUtilLib.IRSAHandler` 執行 **RSASign**,將 `hiseed` 跟
  `hisignedhash` 回傳給入口網驗證。
- 若專案 session 已 timeout 無法取得登入資訊,依 Session Timeout 處理方式處理。

## 參考

- 行動裝置網頁開發: https://svrconf.cotabank.com/pages/viewpage.action?pageId=106561578
- 回入口網處理方式: https://svrconf.cotabank.com/pages/viewpage.action?pageId=106561639
- Session Timeout 處理方式: https://svrconf.cotabank.com/pages/viewpage.action?pageId=106561581
