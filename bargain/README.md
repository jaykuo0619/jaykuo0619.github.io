# 撿便宜

搜尋商品，比較附近 7-11、全家、全聯的優惠與折後單價；開啟「逛街模式」後，走近有優惠的門市會跳出提醒。

網址：https://jaykuo0619.github.io/bargain/

## 裝到 iPhone

1. 用 Safari 開上面的網址，允許取用位置。
2. 點分享按鈕 →「加入主畫面」。
3. 從主畫面圖示開啟，打開「逛街模式」時允許通知。

## 資料

- 門市位置：開啟時即時查詢 OpenStreetMap（Overpass API）半徑 1.5 公里內的 7-11、全家、全聯。
- 優惠：`data/offers.json`，目前是範例資料，尚未與門市核對。
- 使用者回報的優惠只存在該手機的瀏覽器裡（localStorage）。

## 限制

網頁 App 只有開著的時候會提醒；App 關掉後不會在背景偵測位置。要背景提醒需要改做原生 App。

## 檔案

- `index.html`、`style.css`、`app.js`：App 本體，不需建置。
- `sw.js`、`manifest.webmanifest`、圖示：讓 App 能加入主畫面並離線開啟。
- `vendor/leaflet/`：地圖套件 Leaflet 1.9.4（BSD-2-Clause）。
