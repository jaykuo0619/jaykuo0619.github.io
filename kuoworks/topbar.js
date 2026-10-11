/* Collapsing top bar, shared by the KUØ WORKS site and the Jay Kuo portfolio.
   Scrolling down past the bar folds it into a small tab at the top left; tapping the tab brings the
   whole bar back. Scrolling on, tapping elsewhere or pressing Esc folds it again. Back at the top it
   is a normal bar. Mark the header with data-collapsible and put the tab text in data-tab. */
(function () {
  var bar = document.querySelector('[data-collapsible]'); if (!bar) return;
  var root = document.documentElement;
  // Phone menu button inside the bar (both sites use the same markup).
  var menu = bar.querySelector('.menu');
  if (menu) {
    menu.addEventListener('click', function () { var o = bar.classList.toggle('open'); menu.setAttribute('aria-expanded', o); });
    bar.querySelectorAll('nav a').forEach(function (a) { a.addEventListener('click', function () { bar.classList.remove('open'); menu.setAttribute('aria-expanded', false); }); });
  }
  var tab = document.createElement('button');
  tab.type = 'button'; tab.className = 'topbar-tab';
  tab.setAttribute('aria-label', bar.getAttribute('data-tab-label') || 'Menu');
  tab.innerHTML = '<span>' + (bar.getAttribute('data-tab') || 'MENU') + '</span>' +
    '<svg viewBox="0 0 18 18" fill="none" stroke-width="1.2" aria-hidden="true"><path d="M2 6h14M2 12h14"/></svg>';
  document.body.appendChild(tab);

  var mini = false, open = false, openY = 0;
  function setOpen(o) {
    open = o; openY = window.scrollY;
    root.classList.toggle('bar-open', o);
    tab.setAttribute('aria-expanded', o);
    // Portfolio bar on phones hides its links behind a menu button; open that list too.
    var m = bar.querySelector('.menu');
    if (m && m.offsetParent !== null) { bar.classList.toggle('open', o); m.setAttribute('aria-expanded', o); }
  }
  function update() {
    var m = window.scrollY > bar.offsetHeight + 40;
    if (m !== mini) { mini = m; root.classList.toggle('bar-mini', m); if (!m && open) setOpen(false); }
    else if (open && Math.abs(window.scrollY - openY) > 80) setOpen(false);
  }
  tab.addEventListener('click', function (e) { e.stopPropagation(); setOpen(true); });
  document.addEventListener('click', function (e) { if (open && !bar.contains(e.target)) setOpen(false); });
  document.addEventListener('keydown', function (e) { if (open && e.key === 'Escape') { setOpen(false); tab.focus(); } });
  bar.querySelectorAll('nav a').forEach(function (a) { a.addEventListener('click', function () { if (open) setOpen(false); }); });
  window.addEventListener('scroll', update, { passive: true });
  update();
})();
