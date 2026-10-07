# Jay Kuo Apps

仿 App Store 風格的 App 下載頁，網址 https://jaykuo0619.github.io/apps/ 。
純靜態網頁，沒有建置步驟：所有 App 的資料都在 `data/apps.json`，`assets/store.js` 依資料畫出頁面。

## 結構

```
apps/
├── index.html            商店首頁（列出所有 App）
├── assets/store.css      樣式（淺色／深色）
├── assets/store.js       讀 apps.json 畫首頁與介紹頁
├── data/apps.json        所有 App 的資料（改這個就好）
└── findtoilet/           廁略
    ├── index.html        介紹頁（標題、分享預覽圖等 meta）
    ├── icon.png          512×512 圖示
    ├── og.png            分享預覽圖、首頁大卡片
    ├── preview.mp4       預覽短影片
    ├── download/*.apk    Android 親友版 APK
    └── screens/*.jpg     截圖
```

## 發布新的 Android 版本

APK 直接放在 `findtoilet/download/`，由 GitHub Pages 提供下載（檔名用英數字，避免中文檔名在部分瀏覽器變亂碼）：

1. 把新的 APK 放進 `findtoilet/download/`，命名為 `findtoilet-family-版本號.apk`（例如 `findtoilet-family-1.0.1.apk`），並刪掉舊版的 APK，避免 repo 越來越大。
2. 修改 `data/apps.json` 裡 `findtoilet` → `platforms.android`：
   - `version`：新版本號
   - `apk`：`/apps/findtoilet/download/<檔名>`
   - `size`：例如 `"49 MB"`
   - `sha256`：`shasum -a 256 檔名.apk` 的結果（可留 `null`）
3. 在 `versions` 最前面加一筆版本紀錄。
4. 提交並推到 `main`，GitHub Pages 約一分鐘後更新。

單一檔案不能超過 100 MB（GitHub 的限制）。之後版本要用同一把親友版金鑰簽署，親友才能直接覆蓋安裝。

`apk` 是 `null` 時，下載按鈕會顯示「準備中」。

## 新增一個 App

1. 建資料夾 `apps/<id>/`，放 `icon.png`（512×512）、`og.png`（1024×500）、截圖。
2. 複製 `findtoilet/index.html`，改標題、描述、`data-id` 和 meta 標籤。
3. 在 `data/apps.json` 的 `apps` 陣列加一筆（第一筆會出現在首頁「今天推薦」大卡片）。
