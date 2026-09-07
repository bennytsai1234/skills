/**
 * Mend 平台 SAST findings CSV 匯出（自動化）
 *
 * 用法：
 *   node mend-export-csv.js --project Dev_AISTT --out "C:\path\Mend掃描_上線版_<sha>.csv"
 *   選填 --org "COTA Commercial Bank, Ltd."  --headed  --timeout 120000
 *
 * 需要 playwright。這台機器上可用：
 *   NODE_PATH="C:/Users/045650/.local/mcp/playwright-mcp/node_modules" node mend-export-csv.js ...
 *
 * 登入：帳密不寫在本檔，也不落地。執行時以 Windows 整合式驗證向內部送掃入口
 * https://sca.cotabank.com/Mendsca 取回頁面上公告的共用帳密，只存在記憶體。
 * 瀏覽器 profile 存在 %LOCALAPPDATA%\cota-mend-export\profile，登入過一次之後
 * 後續執行直接沿用 session，不必再輸入帳密。
 */
'use strict';

const { chromium } = require('playwright');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');

const args = process.argv.slice(2);
const arg = (name, fallback = null) => {
    const i = args.indexOf(`--${name}`);
    return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};
const has = name => args.includes(`--${name}`);

const PROJECT = arg('project');
const OUT = arg('out');
const ORG = arg('org', 'COTA Commercial Bank, Ltd.');
const TIMEOUT = Number(arg('timeout', '120000'));
const PROFILE = path.join(process.env.LOCALAPPDATA || os.tmpdir(), 'cota-mend-export', 'profile');

if (!PROJECT || !OUT) {
    console.error('用法：node mend-export-csv.js --project <Mend 專案名> --out <輸出 csv 路徑>');
    process.exit(2);
}

// 共用帳密公告在內部送掃入口頁上，走 Windows 整合式驗證取回；不 log、不寫檔。
function readSharedCredentials() {
    const ps = `
$ErrorActionPreference='Stop'
$c = (Invoke-WebRequest -Uri 'https://sca.cotabank.com/Mendsca' -UseDefaultCredentials -UseBasicParsing -TimeoutSec 60).Content
$m = [regex]::Matches($c, 'data-copy="([^"]+)"')
$user = $null; $pass = $null
foreach ($x in $m) { $v = $x.Groups[1].Value; if ($v -like '*@*') { if (-not $user) { $user = $v } } elseif (-not $pass) { $pass = $v } }
if (-not $user -or -not $pass) { throw '送掃入口頁沒有找到共用帳密' }
[Console]::Out.Write((ConvertTo-Json @{ user = $user; pass = $pass } -Compress))
`;
    const out = execFileSync('powershell', ['-NoProfile', '-NonInteractive', '-Command', ps], {
        encoding: 'utf8', timeout: 90000,
    });
    return JSON.parse(out);
}

async function findProjectUuid(page) {
    // 專案 UUID 不固定，從 Projects 清單查出來，避免每次都要人工找 UUID。
    // 清單是虛擬捲動的，只有前幾十筆在 DOM 裡，一定要先用搜尋框篩過。
    const search = page.locator('input[placeholder="Search by project name"]').first();
    await search.waitFor({ timeout: TIMEOUT });
    await search.fill(PROJECT);

    const uuid = await page.waitForFunction(name => {
        const link = [...document.querySelectorAll('a[href*="project="]')]
            .find(a => a.innerText.trim() === name);
        if (!link) return null;
        return new URL(link.href, location.origin).searchParams.get('project');
    }, PROJECT, { timeout: TIMEOUT }).then(handle => handle.jsonValue());

    if (!uuid) throw new Error(`找不到專案 ${PROJECT}`);
    return uuid;
}

(async () => {
    fs.mkdirSync(PROFILE, { recursive: true });
    const ctx = await chromium.launchPersistentContext(PROFILE, {
        headless: !has('headed'),
        acceptDownloads: true,
        viewport: { width: 1600, height: 1000 },
    });
    const page = ctx.pages()[0] || await ctx.newPage();
    page.setDefaultTimeout(TIMEOUT);

    try {
        await page.goto(`https://saas.mend.io/app/orgs/${encodeURIComponent(ORG)}/projects`,
            { waitUntil: 'domcontentloaded', timeout: TIMEOUT });

        // 沒有既存 session 會被導到 /app/login，但這是 SPA：網址一開始仍是
        // /app/orgs/...，過幾秒才換成 /app/login。用 URL 判斷會誤判成已登入，
        // 所以改成等「登入表單」或「專案搜尋框」誰先出現。
        const passwordBox = page.locator('input[type="password"]').first();
        const searchBox = page.locator('input[placeholder="Search by project name"]').first();
        await Promise.race([
            passwordBox.waitFor({ state: 'visible', timeout: TIMEOUT }),
            searchBox.waitFor({ state: 'visible', timeout: TIMEOUT }),
        ]);

        if (await passwordBox.isVisible().catch(() => false)) {
            const cred = readSharedCredentials();
            await page.locator('input[type="email"]').first().fill(cred.user);
            await passwordBox.fill(cred.pass);
            await page.getByRole('button', { name: 'Login', exact: true }).first().click();
            await searchBox.waitFor({ state: 'visible', timeout: TIMEOUT });
        }

        const uuid = arg('uuid') || await findProjectUuid(page);
        // status 篩選要跟既有報告一致，否則筆數會對不起來。
        const sastUrl = `https://saas.mend.io/app/orgs/${encodeURIComponent(ORG)}/applications/sast`
            + `?project=${uuid}`
            + `&filter_sast_findings_tbl_status=${encodeURIComponent('Unreviewed,In Review,Jira Issue Submitted')}`;
        await page.goto(sastUrl, { waitUntil: 'domcontentloaded', timeout: TIMEOUT });

        const csvBtn = page.getByRole('button', { name: 'CSV', exact: true }).first();
        await csvBtn.waitFor({ timeout: TIMEOUT });
        const [download] = await Promise.all([
            page.waitForEvent('download', { timeout: TIMEOUT }),
            csvBtn.click(),
        ]);

        fs.mkdirSync(path.dirname(OUT), { recursive: true });
        await download.saveAs(OUT);

        const text = fs.readFileSync(OUT, 'utf8');
        const rows = text.split(/\r?\n/).filter(Boolean);
        // 前 3 行是 Scope / Filtered by / 欄位名。
        console.log(`已匯出 ${OUT}`);
        console.log(`findings 筆數：${Math.max(0, rows.length - 3)}`);
    } finally {
        await ctx.close();
    }
})().catch(err => {
    console.error('匯出失敗：', err && err.message ? err.message : err);
    process.exit(1);
});
