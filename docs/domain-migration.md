# drchangtingwei.com 網域切換

目前尚未切換；保留 GitHub Pages 原網址，直到持有人完成購買與 DNS 設定。

## 已確認方案（2026-09-09）

- Cloudflare 登入後查詢：drchangtingwei.com 可註冊，1 年 US$10.46，續約當下 US$10.46／年，稅金以結帳為準。
- Cloudflare 提供註冊與 DNS；GitHub Pages 繼續提供網站主機。
- 對外網址預定為 https://drchangtingwei.com/，www 轉至主網域。
- 單純更換網域不保證搜尋排名或 AI 推薦提升。

## 購買後執行順序

1. 確認網域出現在使用者 Cloudflare 帳戶；完成註冊商要求的電子郵件驗證。
2. 在 GitHub 個人設定的 Pages 加入並驗證 drchangtingwei.com，取得專屬 TXT 值後加入 Cloudflare；不可猜測驗證碼。
3. 在本網站 GitHub Pages 設定自訂網域，確保 main 分支包含 CNAME，內容為 drchangtingwei.com。
4. 在 Cloudflare 新增以下 DNS 記錄，初始使用 DNS only，TTL Auto；保留無關的 MX/TXT 記錄。不要新增 wildcard。

| Type | Name | Content |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | drchangtingwei-code.github.io |

5. 確認 DNS 解析、Pages DNS check 與憑證，再啟用 Enforce HTTPS。
6. 將公開 HTML 的 canonical、hreflang、Open Graph、JSON-LD URL、robots、兩種 sitemap、llms 與 IndexNow 工作流程的主機一起切換。GitHub repository remote 不改。
7. 部署並逐頁確認新網址 200、舊網址與 www 永久重新導向、新 canonical 自我指向、圖片與內部連結正常。
8. 在 Search Console 驗證新網域、提交新 sitemap，視舊資源是否符合條件使用 Change of Address；以介面結果判定完成，不能將「提交」寫成「已收錄」。
9. 檢查 IndexNow key 在新網域可讀並送出通知；Google 收錄與 IndexNow 為不同機制。

## 若切換失敗

先查 DNS、憑證與 Pages 狀態。若無法短時間恢復，撤回本次自訂網域設定和 CNAME，並還原網站 canonical／sitemap 至原網域。不要只移除 DNS 卻保留未使用的 GitHub 網域設定。

## 官方參考

- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://developers.google.com/search/docs/appearance/ai-features
- https://www.cloudflare.com/products/registrar/
