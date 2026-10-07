// Jay Kuo Apps：讀取 data/apps.json，畫出商店首頁或單一 App 的介紹頁。
// 新增 App 或更新版本時只要改 apps.json（見 apps/README.md）。
(function () {
  "use strict";

  var root = document.getElementById("store");
  var page = root.getAttribute("data-page");
  var base = root.getAttribute("data-base") || "";

  var ICONS = {
    apple: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.6c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.7-3.18-1.73-1.35-.14-2.64.8-3.33.8-.69 0-1.74-.78-2.86-.76-1.47.02-2.83.86-3.59 2.17-1.53 2.65-.39 6.58 1.1 8.73.73 1.05 1.6 2.23 2.73 2.19 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.07 2.65-2.13.84-1.22 1.18-2.4 1.2-2.46-.03-.01-2.29-.88-2.3-3.48zM14.2 6.13c.6-.73 1.01-1.75.9-2.76-.87.04-1.92.58-2.54 1.31-.56.64-1.05 1.68-.92 2.67.97.08 1.96-.49 2.56-1.22z"/></svg>',
    android: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.6 9.48l1.84-3.18a.38.38 0 0 0-.66-.38l-1.86 3.22A11.4 11.4 0 0 0 12 8.2c-1.77 0-3.43.35-4.92.94L5.22 5.92a.38.38 0 0 0-.66.38L6.4 9.48A10.78 10.78 0 0 0 1 18h22a10.78 10.78 0 0 0-5.4-8.52zM7 15.25a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm10 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5z"/></svg>',
    download: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a1 1 0 0 1 1 1v9.59l3.3-3.3a1 1 0 1 1 1.4 1.42l-5 5a1 1 0 0 1-1.4 0l-5-5a1 1 0 1 1 1.4-1.42L11 13.6V4a1 1 0 0 1 1-1zM5 19h14a1 1 0 1 1 0 2H5a1 1 0 1 1 0-2z"/></svg>'
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function device() {
    var ua = navigator.userAgent || "";
    if (/android/i.test(ua)) return "android";
    if (/iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)) return "ios";
    return "desktop";
  }

  function iosButton(app, big) {
    var ios = app.platforms.ios;
    if (!ios || !ios.url) return "";
    return '<a class="get primary' + (big ? " big" : "") + '" href="' + esc(ios.url) + '" target="_blank" rel="noopener">' +
      ICONS.apple + "App Store</a>";
  }

  function androidButton(app, big, primary) {
    var a = app.platforms.android;
    if (!a) return "";
    if (!a.apk) {
      return '<span class="get disabled' + (big ? " big" : "") + '" title="Android 版準備中">' + ICONS.android + "準備中</span>";
    }
    return '<a class="get' + (primary ? " primary" : "") + (big ? " big" : "") + '" href="' + esc(a.apk) + '" download>' +
      ICONS.android + "下載 APK</a>";
  }

  function footer(store) {
    return '<footer><div class="wrap">' +
      "<p>" + esc(store.name) + " · 開發者 " + esc(store.developer) + "</p>" +
      '<p>聯絡：<a href="mailto:' + esc(store.contact) + '">' + esc(store.contact) + "</a> · " +
      '<a href="' + base + '../">回到 Jay 的個人網站</a></p>' +
      "<p>App Store 是 Apple Inc. 的商標；Android 是 Google LLC 的商標。</p>" +
      "</div></footer>";
  }

  function renderHome(data) {
    var store = data.store;
    var first = data.apps[0];
    var html = '<section class="hero wrap">' +
      '<div class="eyebrow">' + esc(store.name) + "</div>" +
      "<h1>今天推薦</h1>" +
      "<p>" + esc(store.tagline) + "</p></section>";

    if (first) {
      html += '<section class="wrap"><a class="feature-card" href="' + esc(first.id) + '/">' +
        '<div class="art"><img src="' + esc(first.id) + '/og.png" alt="" loading="lazy"></div>' +
        '<div class="body"><div class="kicker">新上架</div><h3>' + esc(first.name) + "</h3>" +
        "<p>" + esc(first.subtitle) + "</p>" +
        '<div><span class="get primary">查看</span></div></div></a></section>';
    }

    html += '<section class="wrap"><div class="section-title"><h2>所有 App</h2></div><div class="app-list">';
    data.apps.forEach(function (app) {
      html += '<a class="app-row" href="' + esc(app.id) + '/">' +
        '<img src="' + esc(app.icon) + '" alt="" width="64" height="64" loading="lazy">' +
        '<div><div class="name">' + esc(app.name) + '</div><div class="sub">' + esc(app.subtitle) + "</div></div>" +
        '<span class="get">取得</span></a>';
    });
    html += "</div></section>" + footer(store);
    root.innerHTML = html;
  }

  function renderApp(data, id) {
    var app = data.apps.filter(function (a) { return a.id === id; })[0];
    if (!app) {
      root.innerHTML = '<div class="wrap noscript">找不到這個 App。<a href="' + base + '">回商店首頁</a></div>';
      return;
    }
    var dev = device();
    var ios = app.platforms.ios;
    var android = app.platforms.android;
    var img = function (p) { return base + p; };

    // 頭部
    var primaryButtons = dev === "android"
      ? androidButton(app, true, true) + iosButton(app, true).replace("get primary", "get")
      : iosButton(app, true) + androidButton(app, true, false);
    var hint = dev === "desktop" ? "用手機掃描下方 QR Code 也能下載" : "";

    var html = '<div class="wrap">' +
      '<header class="app-head">' +
      '<img class="icon" src="' + img(app.icon) + '" alt="' + esc(app.name) + ' 圖示" width="128" height="128">' +
      "<div><h1>" + esc(app.name) + '</h1><div class="en">' + esc(app.enName) + "</div>" +
      '<div class="subtitle">' + esc(app.subtitle) + "</div>" +
      '<div class="actions">' + primaryButtons + (hint ? '<span class="hint" id="qr-hint" hidden>' + hint + "</span>" : "") + "</div>" +
      "</div></header>";

    // 資訊條
    html += '<div class="meta-strip">' +
      '<div><div class="k">價格</div><div class="v">' + esc(app.price) + '</div><div class="s">無廣告</div></div>' +
      '<div><div class="k">年齡</div><div class="v">' + esc(app.ageRating) + '</div><div class="s">歲</div></div>' +
      '<div><div class="k">類別</div><div class="v">' + esc(app.category) + '</div><div class="s">&nbsp;</div></div>' +
      '<div><div class="k">語言</div><div class="v">ZH</div><div class="s">' + esc(app.languages) + "</div></div>" +
      "</div>";

    // 預覽
    html += '<div class="section-title"><h2>預覽</h2></div><div class="shots">';
    if (app.video) {
      html += '<video src="' + img(app.video.src) + '" poster="' + img(app.video.poster) + '" muted loop playsinline preload="none" aria-label="App 預覽影片"></video>';
    }
    app.screenshots.forEach(function (s, i) {
      html += '<img src="' + img(s) + '" alt="' + esc(app.name) + " 畫面 " + (i + 1) + '" loading="lazy">';
    });
    html += "</div>";

    // 說明
    html += '<div class="section-title"><h2>簡介</h2></div><div class="desc">';
    app.description.forEach(function (p) { html += "<p>" + esc(p) + "</p>"; });
    html += '</div><div class="features">';
    app.features.forEach(function (f) { html += "<div><b>" + esc(f.title) + "</b><span>" + esc(f.text) + "</span></div>"; });
    html += "</div>";

    // 下載
    html += '<div class="section-title" id="download"><h2>下載</h2></div><div class="downloads">';
    if (ios) {
      html += '<div class="dl' + (dev === "ios" ? " recommended" : "") + '">' +
        '<div class="top"><h3>' + ICONS.apple + esc(ios.label) + "</h3>" + (dev === "ios" ? '<span class="tag">適合你的裝置</span>' : "") + "</div>" +
        "<p>" + esc(ios.note) + "</p>" +
        '<div class="row"><span class="small">' + esc(ios.requires) + "</span>" + iosButton(app, false) + "</div></div>";
    }
    if (android) {
      var meta = [android.requires];
      if (android.apk) meta.unshift("版本 " + android.version + (android.size ? " · " + android.size : ""));
      html += '<div class="dl' + (dev === "android" ? " recommended" : "") + '">' +
        '<div class="top"><h3>' + ICONS.android + esc(android.label) + "</h3>" + (dev === "android" ? '<span class="tag">適合你的裝置</span>' : "") + "</div>" +
        "<p>" + esc(android.note) + (android.apk ? "" : " 目前正在打包，很快就能下載。") + "</p>" +
        '<div class="row"><span class="small">' + esc(meta.join(" · ")) + "</span>" + androidButton(app, false, true) + "</div>" +
        (android.sha256 ? '<div class="small">SHA-256：' + esc(android.sha256) + "</div>" : "") +
        "</div>";
    }
    html += "</div>";
    html += '<div class="qr" id="qr"><div id="qr-code"></div><div>用手機相機掃描，<br>直接在手機上打開這一頁。</div></div>';

    if (android) {
      html += '<details class="howto"><summary>Android 怎麼安裝？</summary><ol class="steps">' +
        "<li>用 Android 手機打開這一頁，點「下載 APK」。</li>" +
        "<li>下載完成後點開檔案。第一次會提示無法安裝不明來源的應用程式：點「設定」，開啟「允許這個來源」，再返回。</li>" +
        "<li>點「安裝」。如果 Google Play 安全防護跳出警告，點「更多詳細資料」→「仍要安裝」。</li>" +
        "<li>打開 App，允許位置權限。第一次開啟會下載全國公廁資料，大約半分鐘。</li>" +
        "<li>之後有新版時，回到這一頁重新下載安裝即可，收藏與回報不會不見。</li>" +
        "</ol></details>";
    }

    // 版本紀錄
    html += '<div class="section-title"><h2>版本紀錄</h2></div><div class="versions">';
    app.versions.forEach(function (v) {
      html += '<div class="ver"><div class="h"><b>' + esc(v.version) + '<span class="plat">' + esc(v.platform) + "</span></b><span>" + esc(v.date) + "</span></div><ul>";
      v.notes.forEach(function (n) { html += "<li>" + esc(n) + "</li>"; });
      html += "</ul></div>";
    });
    html += "</div>";

    // 隱私
    html += '<div class="section-title"><h2>App 隱私權</h2></div><div class="privacy">' +
      "<p>" + esc(app.privacy.summary) + "</p>" +
      '<a href="' + esc(app.privacy.url) + '" target="_blank" rel="noopener">隱私權政策</a></div>';

    // 資訊
    html += '<div class="section-title"><h2>資訊</h2></div><div class="info">' +
      '<div><div class="k">開發者</div><div class="v">' + esc(data.store.developer) + "</div></div>" +
      '<div><div class="k">類別</div><div class="v">' + esc(app.category) + "</div></div>" +
      '<div><div class="k">相容性</div><div class="v">' + esc([ios && ios.requires, android && android.requires].filter(Boolean).join("；")) + "</div></div>" +
      '<div><div class="k">語言</div><div class="v">' + esc(app.languages) + "</div></div>" +
      '<div><div class="k">年齡分級</div><div class="v">' + esc(app.ageRating) + "</div></div>" +
      '<div><div class="k">價格</div><div class="v">' + esc(app.price) + "</div></div>" +
      "</div>" +
      '<p class="small" style="color:var(--dim);font-size:13px;margin-top:14px">資料來源：' + esc(app.dataSources) + "</p>";

    html += "</div>" + footer(data.store);
    root.innerHTML = html;

    // 影片：點一下播放／暫停
    var video = root.querySelector(".shots video");
    if (video) {
      video.addEventListener("click", function () { video.paused ? video.play() : video.pause(); });
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) { video.play().catch(function () {}); } else { video.pause(); }
          });
        }, { threshold: 0.6 }).observe(video);
      }
    }

    // 電腦上顯示 QR Code
    if (dev === "desktop" && window.QRCode) {
      try {
        new window.QRCode(document.getElementById("qr-code"), { text: location.href.split("#")[0], width: 200, height: 200 });
        document.getElementById("qr").classList.add("show");
        var qrHint = document.getElementById("qr-hint");
        if (qrHint && window.matchMedia("(hover: hover) and (min-width: 900px)").matches) qrHint.hidden = false;
      } catch (e) { /* 沒有 QR Code 也不影響下載 */ }
    }
  }

  fetch(base + "data/apps.json", { cache: "no-cache" })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (page === "app") renderApp(data, root.getAttribute("data-id"));
      else renderHome(data);
    })
    .catch(function () {
      root.innerHTML = '<div class="wrap noscript">資料載入失敗，請重新整理頁面。</div>';
    });
})();
