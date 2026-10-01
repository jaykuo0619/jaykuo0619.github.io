'use strict';

// ---------- 設定 ----------
const DEFAULT_CENTER = [25.0478, 121.5170]; // 台北車站，拿不到定位時使用
const STORE_RADIUS_M = 1500;
const ALERT_COOLDOWN_MS = 30 * 60 * 1000;
const OVERPASS_URLS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter'
];
const CHAINS = {
  '7-11': { cls: 'c711', color: '#E8642C', test: /7[\s-]?eleven|7-11|統一超商|セブン/i },
  '全家': { cls: 'cfm', color: '#1BA36B', test: /family\s?mart|全家/i },
  '全聯': { cls: 'cpx', color: '#1F4E9C', test: /全聯|px\s?mart/i }
};
const LS = {
  userOffers: 'bargain.userOffers',
  watch: 'bargain.watch',
  alerted: 'bargain.alerted',
  settings: 'bargain.settings'
};

// ---------- 小工具 ----------
const $ = (id) => document.getElementById(id);

function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}

function save(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* 無痕模式等情況會失敗，忽略 */ }
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function distanceM(a, b) {
  const R = 6371000;
  const toRad = (d) => d * Math.PI / 180;
  const dLat = toRad(b[0] - a[0]);
  const dLon = toRad(b[1] - a[1]);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a[0])) * Math.cos(toRad(b[0])) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function fmtDist(m) {
  if (m == null) return '';
  if (m < 1000) return `${Math.round(m / 10) * 10} 公尺`;
  return `${(m / 1000).toFixed(1)} 公里`;
}

function walkMin(m) {
  return Math.max(1, Math.round(m / 75)); // 每分鐘約 75 公尺
}

function todayStr() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function chainOf(tags) {
  const text = [tags.brand, tags['brand:zh'], tags['brand:en'], tags.name, tags['name:zh'], tags['name:en']]
    .filter(Boolean).join(' ');
  for (const [chain, def] of Object.entries(CHAINS)) {
    if (def.test.test(text)) return chain;
  }
  return null;
}

// ---------- 價格計算 ----------
function effectiveEach(o) {
  const p = o.promo || { type: 'none' };
  switch (p.type) {
    case 'price': return p.price;
    case 'second_discount': return (o.original + o.original * p.rate) / 2;
    case 'bogo': return o.original / 2;
    case 'multi': return p.total / p.qty;
    default: return o.original;
  }
}

function unitPrice(o) {
  return effectiveEach(o) / (o.unitCount || 1);
}

function promoText(o) {
  const p = o.promo || { type: 'none' };
  switch (p.type) {
    case 'price': return `特價 ${p.price} 元，原價 ${o.original}`;
    case 'second_discount': return `第二件 ${+(p.rate * 10).toFixed(1)} 折，買 2 件平均`;
    case 'bogo': return '買一送一，買 2 件平均';
    case 'multi': return `任選 ${p.qty} 件 ${p.total} 元`;
    default: return `售價 ${o.original} 元`;
  }
}

function hasPromo(o) {
  return o.promo && o.promo.type !== 'none';
}

function isActive(o, today) {
  return (!o.start || o.start <= today) && (!o.end || o.end >= today);
}

// ---------- 狀態 ----------
const state = {
  offers: [],
  stores: [],
  me: null,
  query: '',
  watch: new Set(load(LS.watch, [])),
  alerted: load(LS.alerted, {}),
  settings: Object.assign({ stroll: false, distance: 200, watchOnly: false }, load(LS.settings, {})),
  geoWatchId: null,
  lastStoreFetch: null,
  markers: null,
  meMarker: null,
  map: null
};

function allOffers() {
  const today = todayStr();
  return state.offers.concat(load(LS.userOffers, [])).filter((o) => isActive(o, today));
}

function nearestStore(chain) {
  if (!state.me) return null;
  let best = null;
  for (const s of state.stores) {
    if (s.chain !== chain) continue;
    if (!best || s.dist < best.dist) best = s;
  }
  return best;
}

function chainsWithPromo() {
  // 有搜尋時，只有該商品有優惠的連鎖加光圈；沒搜尋時看關注清單；都沒有就看全部優惠
  const q = state.query.trim();
  let list = allOffers().filter(hasPromo);
  if (q) list = list.filter((o) => matches(o, q));
  else if (state.watch.size) list = list.filter((o) => state.watch.has(o.product));
  return new Set(list.map((o) => o.chain));
}

// ---------- 地圖 ----------
function initMap() {
  state.map = L.map('map', { zoomControl: false, attributionControl: true }).setView(DEFAULT_CENTER, 16);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(state.map);
  state.markers = L.layerGroup().addTo(state.map);
}

function renderStores() {
  state.markers.clearLayers();
  const hot = chainsWithPromo();
  for (const s of state.stores) {
    const def = CHAINS[s.chain];
    const icon = L.divIcon({
      className: '',
      html: `<div class="store-pin${hot.has(s.chain) ? ' hot' : ''}" style="background:${def.color}"></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });
    const label = `${esc(s.chain)} ${esc(s.name || '')}${s.dist != null ? `<br>${fmtDist(s.dist)}` : ''}`;
    L.marker([s.lat, s.lon], { icon }).bindPopup(
      `${label}<br><a href="${mapsLink(s)}" target="_blank" rel="noopener">導航</a>`
    ).addTo(state.markers);
  }
}

function mapsLink(s) {
  return `https://maps.apple.com/?daddr=${s.lat},${s.lon}&dirflg=w`;
}

function renderMe() {
  if (!state.me) return;
  const icon = L.divIcon({ className: '', html: '<div class="me-pin"></div>', iconSize: [18, 18], iconAnchor: [9, 9] });
  if (state.meMarker) state.meMarker.setLatLng(state.me);
  else state.meMarker = L.marker(state.me, { icon, interactive: false, zIndexOffset: 1000 }).addTo(state.map);
}

// ---------- 門市（OpenStreetMap Overpass） ----------
async function fetchStores(center) {
  const q = `[out:json][timeout:25];(nwr["shop"~"^(convenience|supermarket)$"](around:${STORE_RADIUS_M},${center[0]},${center[1]}););out center 400;`;
  let lastErr;
  for (const url of OVERPASS_URLS) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'data=' + encodeURIComponent(q)
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const json = await res.json();
      return json.elements.map((el) => {
        const tags = el.tags || {};
        const chain = chainOf(tags);
        const lat = el.lat != null ? el.lat : el.center && el.center.lat;
        const lon = el.lon != null ? el.lon : el.center && el.center.lon;
        if (!chain || lat == null || lon == null) return null;
        return { id: `${el.type}/${el.id}`, chain, name: tags['branch'] || tags['name:zh'] || tags.name || '', lat, lon, dist: null };
      }).filter(Boolean);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}

async function refreshStores(center) {
  $('storeStatus').textContent = '正在找附近門市…';
  try {
    const stores = await fetchStores(center);
    state.stores = stores;
    state.lastStoreFetch = center;
    updateDistances();
    renderStores();
    const counts = Object.keys(CHAINS).map((c) => `${c} ${stores.filter((s) => s.chain === c).length}`).join('、');
    $('storeStatus').textContent = `${fmtDist(STORE_RADIUS_M)}內：${counts} 間`;
  } catch (e) {
    $('storeStatus').textContent = '門市資料暫時載不到，稍後再試';
  }
  renderResults();
}

function updateDistances() {
  for (const s of state.stores) s.dist = state.me ? distanceM(state.me, [s.lat, s.lon]) : null;
  state.stores.sort((a, b) => (a.dist ?? 0) - (b.dist ?? 0));
}

// ---------- 定位 ----------
function onPosition(pos) {
  const first = !state.me;
  state.me = [pos.coords.latitude, pos.coords.longitude];
  renderMe();
  if (first) state.map.setView(state.me, 16);
  if (!state.lastStoreFetch || distanceM(state.lastStoreFetch, state.me) > STORE_RADIUS_M / 2) {
    refreshStores(state.me);
  } else {
    updateDistances();
    renderResults();
  }
  if (state.settings.stroll) checkProximity();
}

function onPositionError() {
  if (!state.lastStoreFetch) {
    $('storeStatus').textContent = '沒有取得定位，先顯示台北車站附近';
    refreshStores(DEFAULT_CENTER);
  }
}

function startGeo() {
  if (!('geolocation' in navigator)) { onPositionError(); return; }
  if (state.geoWatchId != null) navigator.geolocation.clearWatch(state.geoWatchId);
  state.geoWatchId = navigator.geolocation.watchPosition(onPosition, onPositionError, {
    enableHighAccuracy: true, maximumAge: 15000, timeout: 20000
  });
}

// ---------- 搜尋與結果 ----------
function matches(o, q) {
  if (!q) return true;
  const hay = [o.product, o.category, o.chain].concat(o.keywords || []).join(' ').toLowerCase();
  return q.toLowerCase().split(/\s+/).filter(Boolean).every((w) => hay.includes(w));
}

function renderResults() {
  const q = state.query.trim();
  let list = allOffers().filter((o) => matches(o, q));
  if (!q) list = list.filter(hasPromo);
  list.sort((a, b) => unitPrice(a) - unitPrice(b));

  $('sheetTitle').textContent = q ? `「${q}」比價` : '本期優惠';
  const box = $('results');
  if (!list.length) {
    box.innerHTML = `<div class="empty">${q ? '找不到這個商品。可以按下方「回報一個優惠」自己加上去。' : '目前沒有進行中的優惠。'}</div>`;
    return;
  }
  const bestPrice = q ? unitPrice(list[0]) : null;
  box.innerHTML = list.map((o) => {
    const near = nearestStore(o.chain);
    const def = CHAINS[o.chain] || { cls: '' };
    const each = unitPrice(o);
    const unitWord = o.unitCount ? '每入' : '每件';
    const watched = state.watch.has(o.product);
    const isBest = bestPrice != null && each === bestPrice;
    return `<article class="card${isBest ? ' best' : ''}">
      <div class="chain ${def.cls}">${esc(o.chain)}${isBest ? ' <span class="badge">最便宜</span>' : ''}</div>
      <div class="name">${esc(o.product)}</div>
      <div class="promo">${esc(promoText(o))}${o.end ? `，到 ${esc(o.end.slice(5).replace('-', '/'))}` : ''}</div>
      <div class="unit"><small>${unitWord}</small><b>${Math.round(each * 10) / 10}</b><small>元</small></div>
      <div class="meta">
        ${near ? `<span>最近：${fmtDist(near.dist)}（走 ${walkMin(near.dist)} 分）</span><a href="${mapsLink(near)}" target="_blank" rel="noopener">導航</a>` : '<span>附近沒找到這家</span>'}
        <span class="badge ${o.source === '我回報' ? 'mine' : ''}">${esc(o.source || '')}</span>
        <button class="secondary" data-watch="${esc(o.product)}">${watched ? '★ 已關注' : '☆ 關注'}</button>
        ${o.source === '我回報' ? `<button class="secondary" data-del="${esc(o.id)}">刪除</button>` : ''}
      </div>
    </article>`;
  }).join('');
}

// ---------- 接近提醒（逛街模式） ----------
function checkProximity() {
  if (!state.me) return;
  const limit = Number(state.settings.distance);
  const now = Date.now();
  const offers = allOffers().filter(hasPromo).filter((o) => !state.settings.watchOnly || state.watch.has(o.product));
  if (!offers.length) return;

  for (const s of state.stores) {
    if (s.dist == null || s.dist > limit) continue;
    if (state.alerted[s.id] && now - state.alerted[s.id] < ALERT_COOLDOWN_MS) continue;
    // 排序：關注的商品優先，其次是正在搜尋的商品，再來是省最多的
    const q = state.query.trim();
    const rank = (o) => (state.watch.has(o.product) ? 0 : 2) + (q && matches(o, q) ? 0 : 1);
    const saving = (o) => 1 - effectiveEach(o) / o.original;
    const here = offers.filter((o) => o.chain === s.chain).sort((a, b) => rank(a) - rank(b) || saving(b) - saving(a));
    if (!here.length) continue;

    state.alerted[s.id] = now;
    save(LS.alerted, state.alerted);
    const top = here[0];
    const title = `前方 ${fmtDist(s.dist)}｜${s.chain}${s.name ? ' ' + s.name : ''}`;
    const body = `${top.product}：${promoText(top)}${here.length > 1 ? `，還有 ${here.length - 1} 個優惠` : ''}`;
    showAlert(title, body);
    notify(title, body);
    break; // 一次只提醒一間
  }
}

function showAlert(title, body) {
  $('alertTitle').textContent = title;
  $('alertBody').textContent = body;
  $('alert').hidden = false;
  if (navigator.vibrate) navigator.vibrate([120, 60, 120]);
}

async function notify(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  try {
    const reg = await navigator.serviceWorker.ready;
    await reg.showNotification(title, { body, icon: 'apple-touch-icon.png', tag: 'bargain-nearby' });
  } catch (e) { /* 部分瀏覽器不支援，畫面上的提醒已經顯示 */ }
}

async function askNotificationPermission() {
  if (!('Notification' in window) || Notification.permission !== 'default') return;
  try { await Notification.requestPermission(); } catch (e) { /* 忽略 */ }
}

// ---------- 回報優惠 ----------
function openOfferDialog() {
  const form = $('offerForm');
  form.reset();
  if (state.query) form.product.value = state.query;
  syncPromoFields();
  $('offerDialog').showModal();
}

function syncPromoFields() {
  const type = $('promoType').value;
  document.querySelectorAll('#offerForm [data-for]').forEach((el) => {
    const show = el.dataset.for === type;
    el.hidden = !show;
    el.querySelectorAll('input').forEach((i) => { i.required = show; });
  });
}

function saveOfferFromForm() {
  const f = $('offerForm');
  const type = f.type.value;
  const promo = { type };
  if (type === 'price') promo.price = Number(f.price.value);
  if (type === 'second_discount') promo.rate = Number(f.rate.value) / 10;
  if (type === 'multi') { promo.qty = Number(f.qty.value); promo.total = Number(f.total.value); }
  const product = f.product.value.trim();
  const offer = {
    id: 'u' + Date.now(),
    chain: f.chain.value,
    product,
    keywords: product.split(/\s+/),
    category: '',
    original: Number(f.original.value),
    promo,
    start: todayStr(),
    end: f.end.value || '',
    source: '我回報'
  };
  const mine = load(LS.userOffers, []);
  mine.push(offer);
  save(LS.userOffers, mine);
  renderStores();
  renderResults();
}

// ---------- 事件 ----------
function bindEvents() {
  $('searchForm').addEventListener('submit', (e) => {
    e.preventDefault();
    state.query = $('q').value;
    $('q').blur();
    renderStores();
    renderResults();
  });
  $('q').addEventListener('input', () => {
    state.query = $('q').value;
    renderStores();
    renderResults();
  });
  $('alertClose').addEventListener('click', () => { $('alert').hidden = true; });
  $('locate').addEventListener('click', () => {
    if (state.me) state.map.setView(state.me, 16);
    else startGeo();
  });

  $('results').addEventListener('click', (e) => {
    const w = e.target.closest('[data-watch]');
    if (w) {
      const name = w.dataset.watch;
      if (state.watch.has(name)) state.watch.delete(name); else state.watch.add(name);
      save(LS.watch, [...state.watch]);
      renderStores();
      renderResults();
      return;
    }
    const d = e.target.closest('[data-del]');
    if (d) {
      save(LS.userOffers, load(LS.userOffers, []).filter((o) => o.id !== d.dataset.del));
      renderStores();
      renderResults();
    }
  });

  const stroll = $('strollMode');
  stroll.checked = state.settings.stroll;
  stroll.addEventListener('change', async () => {
    state.settings.stroll = stroll.checked;
    save(LS.settings, state.settings);
    if (stroll.checked) {
      await askNotificationPermission();
      checkProximity();
    }
  });
  const dist = $('alertDistance');
  dist.value = String(state.settings.distance);
  dist.addEventListener('change', () => { state.settings.distance = Number(dist.value); save(LS.settings, state.settings); });
  const watchOnly = $('watchOnly');
  watchOnly.checked = state.settings.watchOnly;
  watchOnly.addEventListener('change', () => { state.settings.watchOnly = watchOnly.checked; save(LS.settings, state.settings); });

  $('addOffer').addEventListener('click', openOfferDialog);
  $('promoType').addEventListener('change', syncPromoFields);
  $('offerForm').addEventListener('submit', (e) => {
    if (e.submitter && e.submitter.value === 'save') {
      if (!$('offerForm').reportValidity()) { e.preventDefault(); return; }
      saveOfferFromForm();
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && state.settings.stroll) checkProximity();
  });
}

// ---------- 啟動 ----------
async function loadOffers() {
  try {
    const res = await fetch('data/offers.json', { cache: 'no-cache' });
    const json = await res.json();
    state.offers = json.offers || [];
  } catch (e) {
    state.offers = [];
  }
}

async function main() {
  initMap();
  bindEvents();
  await loadOffers();
  renderResults();
  startGeo();
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}

main();
