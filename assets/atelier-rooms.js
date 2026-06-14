/* ============================================================================
   ATELIER — rotating room background (soft / mood layer)
   Base engine by Claude Design (the design language).
   ADDED here, per REVIEW Move 1: the `data-mood="paper"` PUBLICATION tier — one
   step more muted than archival, so the photograph becomes a warm tonal
   atmosphere with a soft diagonal of light, never an identifiable building.
   Archival stays as-is for the cockpit's internal research; the two never drift.
   ============================================================================ */
(function () {
  var ROOMS = ['room-1.jpg','room-2.jpg','room-3.jpg','room-4.jpg','room-5.jpg','room-6.jpg','room-7.jpg','room-8.jpg','room-9.jpg'];

  var base = 'assets/rooms/';
  try {
    var me = document.currentScript && document.currentScript.src;
    if (me) base = me.slice(0, me.lastIndexOf('/') + 1) + 'rooms/';
  } catch (e) {}
  ROOMS = ROOMS.map(function (f) { return base + f; });

  var FADE_MS = 2800;
  var HOLD_MS = 18000;
  var KEY = 'atelier-room-ix';

  var css =
    '#atelier-bg{position:fixed;inset:0;z-index:0;overflow:hidden;background:#d8c9b1;}' +
    '#atelier-bg .rm{position:absolute;inset:-4%;background-size:cover;background-position:center;' +
      'filter:blur(3px) saturate(1.16) contrast(1.05) brightness(1.04);transform:scale(1.05);' +
      'transition:opacity ' + FADE_MS + 'ms ease;will-change:opacity;}' +
    '#atelier-bg:after{content:"";position:absolute;inset:0;pointer-events:none;' +
      'background:' +
        'linear-gradient(112deg,rgba(242,235,225,0.62) 0%,rgba(242,235,225,0.46) 40%,rgba(242,235,225,0.38) 66%,rgba(240,230,216,0.48) 100%),' +
        'radial-gradient(135% 130% at 82% 16%,rgba(60,42,20,0) 38%,rgba(48,32,16,0.16) 100%),' +
        'radial-gradient(120% 120% at 8% 96%,rgba(255,240,214,0.20),rgba(255,240,214,0) 50%);}' +
    /* archival — the cockpit's own research pages (unchanged) */
    'body[data-mood="archival"] #atelier-bg{background:#e3d9c7;}' +
    'body[data-mood="archival"] #atelier-bg .rm{' +
      'filter:blur(9px) saturate(0.5) contrast(0.96) brightness(1.08);}' +
    'body[data-mood="archival"] #atelier-bg:after{' +
      'background:' +
        'linear-gradient(180deg,rgba(245,240,231,0.88) 0%,rgba(244,238,228,0.84) 50%,rgba(242,235,224,0.86) 100%),' +
        'radial-gradient(120% 120% at 8% 0%,rgba(255,244,222,0.28),rgba(255,244,222,0) 55%);}' +
    /* paper — the PUBLICATION tier (REVIEW Move 1): a breath of warm room under
       paper, a soft diagonal of light, no legible architecture. veil ~0.92. */
    'body[data-mood="paper"] #atelier-bg{background:#e6dccb;}' +
    'body[data-mood="paper"] #atelier-bg .rm{' +
      'filter:blur(20px) saturate(0.32) brightness(1.10);}' +
    'body[data-mood="paper"] #atelier-bg:after{' +
      'background:' +
        'linear-gradient(150deg,rgba(246,241,232,0.90) 0%,rgba(244,238,228,0.93) 46%,rgba(243,236,225,0.94) 72%,rgba(245,238,226,0.90) 100%),' +
        'radial-gradient(130% 120% at 84% 8%,rgba(255,246,226,0.34),rgba(255,246,226,0) 58%);}' +
    '@media (prefers-reduced-motion: reduce){#atelier-bg .rm{transition:none;}}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  function start() {
    var bg = document.createElement('div');
    bg.id = 'atelier-bg';
    document.body.insertBefore(bg, document.body.firstChild);

    var pinned = document.body.getAttribute('data-room');
    var ix;
    if (pinned !== null && pinned !== '') {
      ix = (parseInt(pinned, 10) - 1 + ROOMS.length) % ROOMS.length;
    } else {
      var last = parseInt(sessionStorage.getItem(KEY), 10);
      ix = isNaN(last) ? Math.floor(Math.random() * ROOMS.length) : (last + 1) % ROOMS.length;
    }

    function place(i, fade) {
      var d = document.createElement('div');
      d.className = 'rm';
      d.style.backgroundImage = 'url("' + ROOMS[i] + '")';
      d.style.opacity = fade ? '0' : '1';
      bg.appendChild(d);
      if (fade) {
        requestAnimationFrame(function () {
          requestAnimationFrame(function () { d.style.opacity = '1'; });
        });
        setTimeout(function () {
          while (bg.children.length > 1) bg.removeChild(bg.firstChild);
        }, FADE_MS + 120);
      }
      try { sessionStorage.setItem(KEY, String(i)); } catch (e) {}
    }

    var pre = new Image();
    pre.onload = pre.onerror = function () { place(ix, false); };
    pre.src = ROOMS[ix];

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce && ROOMS.length > 1) {
      setInterval(function () {
        ix = (ix + 1) % ROOMS.length;
        var img = new Image();
        img.onload = function () { place(ix, true); };
        img.src = ROOMS[ix];
      }, HOLD_MS);
    }

    window.AtelierRooms = {
      rooms: ROOMS,
      next: function () { ix = (ix + 1) % ROOMS.length; place(ix, true); }
    };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
