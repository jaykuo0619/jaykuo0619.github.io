/* Tile animations, shared by the KUØ WORKS home page and the Jay Kuo portfolio home page.
   Each drawing is optional: the script animates whichever of these it finds.
     .sign[data-l]  FindToilet sign: points to the next restroom (distance counts, arrow turns, access colour changes)
     .cal           OurDays day counter: only the digits that change roll up, like a flip clock
     .fan           PartyTable cards: dealt, then gathered and fanned again with the red card lifted
     .phw           Founder photo: comes up like a print, crop marks snap on, then a slow drift
   A drawing starts as soon as it is on screen and pauses when it leaves. With reduced motion nothing moves
   (body.anim is never set, so every drawing simply shows its final state). */
(function () {
  // One tile at a time with a mouse or trackpad: each scroll gesture glides to the next (or previous) row of
  // tiles. A tile taller than the window scrolls normally until its end. Touch screens use CSS snapping instead.
  var main = document.querySelector('main.tiles');
  var fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!main || !fine) return;
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var busy = false, quietTimer = 0, releaseAt = 0;
  var tiles = function () { return main.querySelectorAll(':scope > .tile'); };
  function release() { busy = false; }
  function holdUntilQuiet() { clearTimeout(quietTimer); quietTimer = setTimeout(release, Math.max(160, releaseAt - Date.now() + 160)); }
  function stops() {
    var y = window.scrollY, max = document.documentElement.scrollHeight - window.innerHeight, seen = {}, list = [0];
    Array.prototype.forEach.call(tiles(), function (t, i) {
      if (i === 0) return;
      var top = Math.round(t.getBoundingClientRect().top + y);
      if (!seen[top]) { seen[top] = 1; list.push(Math.min(top, max)); }
    });
    if (list[list.length - 1] < max) list.push(max);
    return list;
  }
  function tileAt(y) {
    var best = null;
    Array.prototype.forEach.call(tiles(), function (t) { var r = t.getBoundingClientRect(); if (r.top + y <= y + 2) best = r; });
    return best;
  }
  window.addEventListener('wheel', function (e) {
    if (e.ctrlKey || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
    if (busy) { e.preventDefault(); holdUntilQuiet(); return; }  // swallow the rest of this gesture (trackpad inertia)
    if (Math.abs(e.deltaY) < 3) return;
    var y = window.scrollY, h = window.innerHeight, dir = e.deltaY > 0 ? 1 : -1, cur = tileAt(y);
    // inside a tile taller than the window: scroll it normally until its edge is reached
    if (cur && cur.height > h + 4 && ((dir > 0 && cur.bottom > h + 2) || (dir < 0 && cur.top < -2))) return;
    var list = stops(), target = null, k;
    if (dir > 0) { for (k = 0; k < list.length; k++) if (list[k] > y + 2) { target = list[k]; break; } }
    else { for (k = list.length - 1; k >= 0; k--) if (list[k] < y - 2) { target = list[k]; break; } }
    if (target === null) return;
    e.preventDefault();
    busy = true; releaseAt = Date.now() + (still ? 150 : 650);
    window.scrollTo({ top: target, behavior: still ? 'auto' : 'smooth' });
    holdUntilQuiet();
  }, { passive: false });
})();

(function () {
  if (!window.IntersectionObserver || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) return;
  document.body.classList.add('anim');
  function loop(ms, step) { var t = 0, k = 0; return { on: function () { if (t) return; k = setTimeout(step, 350); t = setInterval(step, ms); }, off: function () { clearTimeout(k); clearInterval(t); t = 0; } }; }
  var ctl = new Map();

  var sign = document.querySelector('.sign[data-l]');
  if (sign) {
    var num = sign.querySelector('.num'), lbl = sign.querySelector('.lbl'), dot = sign.querySelector('.dot'), arrow = sign.querySelector('.arrow');
    var labels = sign.getAttribute('data-l').split('|'), stops = [[120, '#0A84FF', -45], [260, '#34C759', 10], [85, '#FF9F0A', -110]], i = 0;
    var count = function (from, to) { var t0 = performance.now(); (function f(now) { var k = Math.min(1, (now - t0) / 800); num.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(f); })(t0); };
    ctl.set(sign, loop(2400, function () {
      var a = stops[i], b = stops[i = (i + 1) % stops.length];
      count(a[0], b[0]); dot.style.backgroundColor = b[1]; arrow.style.transform = 'rotate(' + b[2] + 'deg)';
      lbl.classList.add('out'); setTimeout(function () { lbl.textContent = labels[i]; lbl.classList.remove('out'); }, 300);
    }));
  }

  var cal = document.querySelector('.cal');
  if (cal) {
    var n = cal.querySelector('.n'), day = 1024;
    var fmt = function (v) { return v.toLocaleString('en-US'); };
    var digits = function (str) { return str.split('').map(function (c) { return '<span class="d">' + c + '</span>'; }).join(''); };
    n.innerHTML = digits(fmt(day));
    ctl.set(cal, loop(1800, function () {
      var a = fmt(day), b = fmt(day + 1), ds = n.querySelectorAll('.d'); day += 1;
      if (a.length !== b.length) { n.innerHTML = digits(b); return; }
      for (var k = 0; k < b.length; k++) if (a[k] !== b[k]) ds[k].innerHTML = '<span class="r"><i>' + a[k] + '</i><i>' + b[k] + '</i></span>';
      setTimeout(function () { n.querySelectorAll('.r').forEach(function (r) { r.parentNode.textContent = r.lastChild.textContent; }); }, 600);
    }));
  }

  var fan = document.querySelector('.fan');
  if (fan) {
    var step = 0;
    ctl.set(fan, loop(1600, function () {
      step = (step + 1) % 3;
      fan.classList.toggle('gather', step === 1); fan.classList.toggle('lift', step === 2);
    }));
  }

  var ph = document.querySelector('.phw');
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var c = ctl.get(e.target);
      if (e.isIntersecting) { e.target.classList.add('on'); c && c.on(); } else { c && c.off(); }
    });
  }, { threshold: 0.15 });
  [sign, cal, fan, ph].forEach(function (el) { if (el) io.observe(el); });
})();
