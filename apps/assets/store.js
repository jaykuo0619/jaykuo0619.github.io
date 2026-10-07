// Jay Kuo Apps：讀取 data/apps.json，畫出商店首頁或單一 App 的介紹頁。
// 新增 App 或更新版本時只要改 apps.json（見 apps/README.md）。
(function () {
  "use strict";

  var root = document.getElementById("store");
  var page = root.getAttribute("data-page");
  var base = root.getAttribute("data-base") || "";

  var ICONS = {
    android: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.6 9.48l1.84-3.18a.38.38 0 0 0-.66-.38l-1.86 3.22A11.4 11.4 0 0 0 12 8.2c-1.77 0-3.43.35-4.92.94L5.22 5.92a.38.38 0 0 0-.66.38L6.4 9.48A10.78 10.78 0 0 0 1 18h22a10.78 10.78 0 0 0-5.4-8.52zM7 15.25a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm10 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5z"/></svg>'
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

  function androidOf(app) {
    return (app.platforms && app.platforms.android) || null;
  }

  function androidButton(app, big) {
    var a = androidOf(app);
    if (!a || !a.apk) {
      return '<span class="get disabled' + (big ? " big" : "") + '" title="Android 版準備中">' + ICONS.android + "準備中</span>";
    }
    return '<a class="get primary' + (big ? " big" : "") + '" href="' + esc(a.apk) + '" download>' +
      ICONS.android + "下載 APK</a>";
  }

  function footer(store) {
    return '<footer><div class="wrap">' +
      "<p>" + esc(store.name) + " · 開發者 " + esc(store.developer) + "</p>" +
      '<p>聯絡：<a href="mailto:' + esc(store.contact) + '">' + esc(store.contact) + "</a> · " +
      '<a href="' + base + '../">回到 Jay 的個人網站</a></p>' +
      "<p>Android 是 Google LLC 的商標。</p>" +
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
      var a = androidOf(app);
      var ready = a && a.apk;
      html += '<a class="app-row" href="' + esc(app.id) + '/">' +
        '<img src="' + esc(app.icon) + '" alt="" width="64" height="64" loading="lazy">' +
        '<div><div class="name">' + esc(app.name) + '</div><div class="sub">' + esc(app.subtitle) + "</div></div>" +
        '<span class="get' + (ready ? "" : " disabled") + '">' + (ready ? "取得" : "準備中") + "</span></a>";
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
    var android = androidOf(app);
    var ready = !!(android && android.apk);
    var img = function (p) { return base + p; };
    var screenshots = app.screenshots || [];
    var versions = app.versions || [];

    // 頭部
    var hint = dev === "desktop" && ready ? "用手機掃描下方 QR Code 也能下載" : "";

    var html = '<div class="wrap">' +
      '<header class="app-head">' +
      '<img class="icon" src="' + img(app.icon) + '" alt="' + esc(app.name) + ' 圖示" width="128" height="128">' +
      "<div><h1>" + esc(app.name) + "</h1>" + (app.enName ? '<div class="en">' + esc(app.enName) + "</div>" : "") +
      '<div class="subtitle">' + esc(app.subtitle) + "</div>" +
      '<div class="actions">' + androidButton(app, true) + (hint ? '<span class="hint" id="qr-hint" hidden>' + hint + "</span>" : "") + "</div>" +
      "</div></header>";

    // 資訊條
    html += '<div class="meta-strip">' +
      '<div><div class="k">價格</div><div class="v">' + esc(app.price) + '</div><div class="s">無廣告</div></div>' +
      '<div><div class="k">年齡</div><div class="v">' + esc(app.ageRating) + '</div><div class="s">歲</div></div>' +
      '<div><div class="k">類別</div><div class="v">' + esc(app.category) + '</div><div class="s">&nbsp;</div></div>' +
      '<div><div class="k">語言</div><div class="v">ZH</div><div class="s">' + esc(app.languages) + "</div></div>" +
      "</div>";

    // 預覽
    if (app.video || screenshots.length) {
      html += '<div class="section-title"><h2>預覽</h2></div><div class="shots">';
      if (app.video) {
        html += '<video src="' + img(app.video.src) + '" poster="' + img(app.video.poster) + '" muted loop playsinline preload="none" aria-label="App 預覽影片"></video>';
      }
      screenshots.forEach(function (s, i) {
        html += '<img src="' + img(s) + '" alt="' + esc(app.name) + " 畫面 " + (i + 1) + '" loading="lazy">';
      });
      html += "</div>";
    }

    // 說明
    html += '<div class="section-title"><h2>簡介</h2></div><div class="desc">';
    app.description.forEach(function (p) { html += "<p>" + esc(p) + "</p>"; });
    html += '</div><div class="features">';
    app.features.forEach(function (f) { html += "<div><b>" + esc(f.title) + "</b><span>" + esc(f.text) + "</span></div>"; });
    html += "</div>";

    // 下載
    html += '<div class="section-title" id="download"><h2>下載</h2></div><div class="downloads">';
    if (android) {
      var meta = [];
      if (ready) meta.push("版本 " + android.version + (android.size ? " · " + android.size : ""));
      if (android.requires) meta.push(android.requires);
      html += '<div class="dl' + (dev === "android" ? " recommended" : "") + '">' +
        '<div class="top"><h3>' + ICONS.android + esc(android.label || "Android") + "</h3>" + (dev === "android" ? '<span class="tag">適合你的裝置</span>' : "") + "</div>" +
        (android.note ? "<p>" + esc(android.note) + "</p>" : "") +
        '<div class="row"><span class="small">' + esc(meta.join(" · ")) + "</span>" + androidButton(app, false) + "</div>" +
        (android.sha256 ? '<div class="small">SHA-256：' + esc(android.sha256) + "</div>" : "") +
        "</div>";
    }
    html += "</div>";
    if (ready) {
      html += '<div class="qr" id="qr"><div id="qr-code"></div><div>用手機相機掃描，<br>直接在手機上打開這一頁。</div></div>';
      html += '<details class="howto"><summary>Android 怎麼安裝？</summary><ol class="steps">' +
        "<li>用 Android 手機打開這一頁，點「下載 APK」。</li>" +
        "<li>下載完成後點開檔案。第一次會提示無法安裝不明來源的應用程式：點「設定」，開啟「允許這個來源」，再返回。</li>" +
        "<li>點「安裝」。如果 Google Play 安全防護跳出警告，點「更多詳細資料」→「仍要安裝」。</li>" +
        "<li>打開 App，允許位置權限。" + esc(android.firstRun || "") + "</li>" +
        "<li>之後有新版時，回到這一頁重新下載安裝即可，資料不會不見。</li>" +
        "</ol></details>";
    }

    // 版本紀錄
    if (versions.length) {
      html += '<div class="section-title"><h2>版本紀錄</h2></div><div class="versions">';
      versions.forEach(function (v) {
        html += '<div class="ver"><div class="h"><b>' + esc(v.version) + (v.platform ? '<span class="plat">' + esc(v.platform) + "</span>" : "") + "</b><span>" + esc(v.date) + "</span></div><ul>";
        v.notes.forEach(function (n) { html += "<li>" + esc(n) + "</li>"; });
        html += "</ul></div>";
      });
      html += "</div>";
    }

    // 隱私
    if (app.privacy) {
      html += '<div class="section-title"><h2>App 隱私權</h2></div><div class="privacy">' +
        "<p>" + esc(app.privacy.summary) + "</p>" +
        (app.privacy.url ? '<a href="' + esc(app.privacy.url) + '" target="_blank" rel="noopener">隱私權政策</a>' : "") + "</div>";
    }

    // 資訊
    html += '<div class="section-title"><h2>資訊</h2></div><div class="info">' +
      '<div><div class="k">開發者</div><div class="v">' + esc(data.store.developer) + "</div></div>" +
      '<div><div class="k">類別</div><div class="v">' + esc(app.category) + "</div></div>" +
      '<div><div class="k">相容性</div><div class="v">' + esc((android && android.requires) || "Android 版準備中") + "</div></div>" +
      '<div><div class="k">語言</div><div class="v">' + esc(app.languages) + "</div></div>" +
      '<div><div class="k">年齡分級</div><div class="v">' + esc(app.ageRating) + "</div></div>" +
      '<div><div class="k">價格</div><div class="v">' + esc(app.price) + "</div></div>" +
      "</div>" +
      (app.dataSources ? '<p class="small" style="color:var(--dim);font-size:13px;margin-top:14px">資料來源：' + esc(app.dataSources) + "</p>" : "");

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
    if (ready && dev === "desktop" && window.QRCode) {
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
