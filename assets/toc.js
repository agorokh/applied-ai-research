/* ============================================================================
   ATELIER TOC:the shared table-of-contents scrollspy + reading-progress bar.
   Extracted (issue #919) from the per-note inline copies so the cached-offset
   logic lives in exactly one place. Behaviour is identical to the inline block
   shipped in #917: section offsets are measured once (and again on resize/load),
   never recomputed per scroll tick, so scrolling triggers no layout reflow.

   Requires on the page: a progress element #pbar and a nav.toc whose anchors
   point at in-page section ids. Include at the very end of <body>, after the
   content it observes:
     <script src="../assets/toc.js"></script>
   The guard below makes the module a no-op on any page lacking those elements,
   so it is safe to include anywhere.
   ============================================================================ */
(function () {
  const bar = document.getElementById('pbar');
  const links = [...document.querySelectorAll('.toc a')];
  // Resolve a TOC link's in-page target safely. Only same-page hash anchors are
  // scrollspy targets; a non-selector href (external link, cross-page path,
  // empty, or bare "#") must not throw a DOMException that halts the module.
  function target(a) {
    const href = a.getAttribute('href');
    if (!href || href.charAt(0) !== '#' || href === '#') return null;
    try { return document.querySelector(href); } catch (e) { return null; }
  }
  const targets = links.map(a => ({ a, t: target(a) })).filter(o => o.t);
  if (!bar || !targets.length) return;
  let offsets = [];
  function measure() {
    const sd = window.scrollY || document.documentElement.scrollTop;
    offsets = targets.map(o => o.t.getBoundingClientRect().top + sd);
  }
  function onScroll() {
    const sd = window.scrollY || document.documentElement.scrollTop;
    const sh = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (sh ? sd / sh * 100 : 0) + '%';
    const y = sd + 130; let cur = targets[0];
    for (let i = 0; i < targets.length; i++) { if (offsets[i] <= y) cur = targets[i]; }
    links.forEach(a => a.classList.remove('on'));
    if (cur) cur.a.classList.add('on');
  }
  document.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', () => { measure(); onScroll(); }, { passive: true });
  window.addEventListener('load', () => { measure(); onScroll(); });
  links.forEach(a => a.addEventListener('click', e => {
    const t = target(a);
    if (t) { e.preventDefault(); window.scrollTo({ top: window.scrollY + t.getBoundingClientRect().top - 28, behavior: 'smooth' }); }
  }));
  measure();
  onScroll();
})();
