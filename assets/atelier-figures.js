/* ============================================================================
   ATELIER FIGURES:the shared instrument-design figure renderer.
   Per REVIEW ("hairline measures, machined ticks, tokenised stroke/fill:never
   chunky bars, never a default chart library's palette"). One renderer, shared
   across every Applied Intelligence note. Every stroke and fill is a var(--…)
   token. Inline SVG, viewBox-scaled, prints, no dependency.

   Usage: drop an element with a JSON config and the renderer fills it.
     <figure class="fig" data-atelier-figure='{"type":"measure", ...}'></figure>
   Types: "measure" (a scale with marked values), "bars" (hairline rows),
   "scatter" (two hairline axes). Captions are rendered by the note, not here.
   ============================================================================ */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }
  function tint(t) {
    return t === 'work' ? 'var(--work)' : t === 'calm' ? 'var(--calm)' :
           t === 'hold' ? 'var(--hold)' : t === 'pos' ? 'var(--pos)' :
           t === 'neg' ? 'var(--neg)' : 'var(--ink)';
  }
  var INK3 = 'var(--ink-3)', LINE = 'var(--line)', LINE2 = 'var(--line-2)';
  var SANS = 'var(--sans)', SERIF = 'var(--serif)', MONO = 'var(--mono)';

  // ---- a horizontal scale with machined ticks and one or more marked values ----
  // cfg: {type:'measure', min, max, unit, ticks:[..], marks:[{at,label,value,tint}]}
  function measure(box, cfg) {
    var W = 720, H = 132, padL = 16, padR = 16, axisY = 86;
    var min = cfg.min != null ? cfg.min : 0, max = cfg.max != null ? cfg.max : 100;
    var x = function (v) { return padL + (W - padL - padR) * (v - min) / (max - min); };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img' });
    // baseline
    svg.appendChild(el('line', { x1: padL, y1: axisY, x2: W - padR, y2: axisY, style: 'stroke:' + LINE2 + ';stroke-width:1' }));
    // machined ticks
    var ticks = cfg.ticks || [min, (min + max) / 2, max];
    ticks.forEach(function (t) {
      svg.appendChild(el('line', { x1: x(t), y1: axisY, x2: x(t), y2: axisY + 7, style: 'stroke:' + LINE + ';stroke-width:1' }));
      var lab = el('text', { x: x(t), y: axisY + 22, style: 'fill:' + INK3 + ';font:11px ' + SANS + ';font-variant-numeric:tabular-nums;text-anchor:middle' });
      lab.textContent = (t === Math.round(t) ? t : t.toFixed(0)) + (cfg.unit && t === max ? cfg.unit : '');
      svg.appendChild(lab);
    });
    // marked values: a taller tick + tabular value above + serif label
    (cfg.marks || []).forEach(function (m) {
      var c = tint(m.tint);
      svg.appendChild(el('line', { x1: x(m.at), y1: axisY - 26, x2: x(m.at), y2: axisY, style: 'stroke:' + c + ';stroke-width:1.5' }));
      var v = el('text', { x: x(m.at), y: axisY - 34, style: 'fill:' + c + ';font:500 19px ' + SERIF + ';font-variant-numeric:tabular-nums;text-anchor:middle' });
      v.textContent = m.value != null ? m.value : m.at + (cfg.unit || '');
      svg.appendChild(v);
      var l = el('text', { x: x(m.at), y: axisY + 40, style: 'fill:var(--ink-2);font-style:italic;font:italic 13px ' + SERIF + ';text-anchor:middle' });
      l.textContent = m.label || '';
      svg.appendChild(l);
    });
    box.appendChild(svg);
  }

  // ---- hairline rows: a thin token rule per row to its value (never a filled bar) ----
  // cfg: {type:'bars', max, unit, rows:[{label, value, valueLabel, tint}]}
  function bars(box, cfg) {
    var rows = cfg.rows || [], max = cfg.max != null ? cfg.max : Math.max.apply(null, rows.map(function (r) { return r.value; }));
    var W = 720, rowH = 34, padL = 168, padR = 64, top = 14;
    var H = top + rows.length * rowH + 26;
    var x = function (v) { return padL + (W - padL - padR) * v / max; };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img' });
    // baseline + end tick
    svg.appendChild(el('line', { x1: padL, y1: top - 4, x2: padL, y2: top + rows.length * rowH, style: 'stroke:' + LINE2 + ';stroke-width:1' }));
    rows.forEach(function (r, i) {
      var y = top + i * rowH + rowH / 2, c = tint(r.tint);
      // row label (serif, right-aligned into the rule)
      var lab = el('text', { x: padL - 14, y: y + 4, style: 'fill:var(--ink);font:15px ' + SERIF + ';text-anchor:end' });
      lab.textContent = r.label;
      svg.appendChild(lab);
      // the hairline measure
      svg.appendChild(el('line', { x1: padL, y1: y, x2: x(r.value), y2: y, style: 'stroke:' + c + ';stroke-width:1.5' }));
      // end tick
      svg.appendChild(el('line', { x1: x(r.value), y1: y - 5, x2: x(r.value), y2: y + 5, style: 'stroke:' + c + ';stroke-width:1.5' }));
      // value (tabular, after the tick)
      var v = el('text', { x: x(r.value) + 10, y: y + 4, style: 'fill:var(--ink-2);font:13px ' + SANS + ';font-variant-numeric:tabular-nums' });
      v.textContent = r.valueLabel != null ? r.valueLabel : r.value + (cfg.unit || '');
      svg.appendChild(v);
    });
    box.appendChild(svg);
  }

  // ---- a small scatter on two hairline axes (open marks, no fill) ----
  // cfg: {type:'scatter', x:{label,min,max,unit}, y:{label,min,max,unit}, points:[{x,y,label,tint}]}
  function scatter(box, cfg) {
    var W = 720, H = 440, padL = 60, padR = 28, padT = 20, padB = 54;
    var ax = cfg.x, ay = cfg.y;
    var X = function (v) { return padL + (W - padL - padR) * (v - ax.min) / (ax.max - ax.min); };
    var Y = function (v) { return (H - padB) - (H - padB - padT) * (v - ay.min) / (ay.max - ay.min); };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img' });
    // axes
    svg.appendChild(el('line', { x1: padL, y1: H - padB, x2: W - padR, y2: H - padB, style: 'stroke:' + LINE2 + ';stroke-width:1' }));
    svg.appendChild(el('line', { x1: padL, y1: padT, x2: padL, y2: H - padB, style: 'stroke:' + LINE2 + ';stroke-width:1' }));
    function ticks(a, axis) {
      var n = 4; for (var i = 0; i <= n; i++) {
        var v = a.min + (a.max - a.min) * i / n;
        if (axis === 'x') {
          svg.appendChild(el('line', { x1: X(v), y1: H - padB, x2: X(v), y2: H - padB + 6, style: 'stroke:' + LINE + ';stroke-width:1' }));
          var t = el('text', { x: X(v), y: H - padB + 20, style: 'fill:' + INK3 + ';font:10.5px ' + SANS + ';font-variant-numeric:tabular-nums;text-anchor:middle' });
          t.textContent = (v % 1 ? v.toFixed(1) : v) + (a.unit && i === n ? a.unit : ''); svg.appendChild(t);
        } else {
          svg.appendChild(el('line', { x1: padL - 6, y1: Y(v), x2: padL, y2: Y(v), style: 'stroke:' + LINE + ';stroke-width:1' }));
          var t2 = el('text', { x: padL - 10, y: Y(v) + 3.5, style: 'fill:' + INK3 + ';font:10.5px ' + SANS + ';font-variant-numeric:tabular-nums;text-anchor:end' });
          t2.textContent = (v % 1 ? v.toFixed(1) : v) + (a.unit && i === n ? a.unit : ''); svg.appendChild(t2);
        }
      }
    }
    ticks(ax, 'x'); ticks(ay, 'y');
    // axis labels (italic serif)
    var xl = el('text', { x: (padL + W - padR) / 2, y: H - 12, style: 'fill:var(--ink-2);font:italic 12.5px ' + SERIF + ';text-anchor:middle' }); xl.textContent = ax.label; svg.appendChild(xl);
    var yl = el('text', { x: 16, y: (padT + H - padB) / 2, style: 'fill:var(--ink-2);font:italic 12.5px ' + SERIF + ';text-anchor:middle', transform: 'rotate(-90 16 ' + ((padT + H - padB) / 2) + ')' }); yl.textContent = ay.label; svg.appendChild(yl);
    // points: open circle + serif label
    (cfg.points || []).forEach(function (p) {
      var c = tint(p.tint);
      svg.appendChild(el('circle', { cx: X(p.x), cy: Y(p.y), r: 4.5, style: 'fill:none;stroke:' + c + ';stroke-width:1.5' }));
      var t = el('text', { x: X(p.x) + 9, y: Y(p.y) + 4, style: 'fill:var(--ink);font:13px ' + SERIF + '' }); t.textContent = p.label || ''; svg.appendChild(t);
    });
    box.appendChild(svg);
  }

  var RENDER = { measure: measure, bars: bars, scatter: scatter };
  function run() {
    document.querySelectorAll('[data-atelier-figure]').forEach(function (box) {
      if (box.__rendered) return; box.__rendered = true;
      var cfg; try { cfg = JSON.parse(box.getAttribute('data-atelier-figure')); } catch (e) { return; }
      var fn = RENDER[cfg.type]; if (fn) fn(box, cfg);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  window.AtelierFigures = { render: run, measure: measure, bars: bars, scatter: scatter };
})();
