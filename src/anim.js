// Reveal over time for a slide whose elements carry data-y (when they appear, as YYYYMM) and whose nodes carry
// data-c ("YYYYMM:cumulative count,...") and data-r (final radius). Used by the network slide.
// Early years step month by month so that each label can be seen arriving; later years step a year at a time.
const STAGGER = 120;                                       // milliseconds between labels that arrive together
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
function playYears(root) {
  const els = [...root.querySelectorAll('[data-y]')], nodes = [...root.querySelectorAll('[data-c]')], clock = root.querySelector('.clock');
  if (!els.length) return;
  stopYears(root);
  const steps = [...new Set(els.map(e => +e.dataset.y))].sort((a, b) => a - b);
  const monthly = new Set(steps.filter(k => k % 100 !== 12).map(k => Math.floor(k / 100)));
  nodes.forEach(n => { n._c = n.dataset.c.split(',').map(p => p.split(':').map(Number)); n._r = +n.dataset.r; });
  let i = -1;
  function draw() {
    const t = i < 0 ? 0 : steps[i];
    let fresh = 0;                                       // labels arriving in this step come in one after another
    els.forEach(e => {
      const on = +e.dataset.y <= t, was = e.style.display !== 'none';
      e.style.display = on ? '' : 'none';
      if (on && !was && e.classList.contains('nl')) {
        e.classList.remove('fresh'); void e.getBBox();
        e.style.animationDelay = (fresh++ * STAGGER) + 'ms'; e.classList.add('fresh');
      }
    });
    nodes.forEach(n => {
      let c = 0; for (const [k, cc] of n._c) { if (k <= t) c = cc; else break; }
      const tot = n._c[n._c.length - 1][1];
      n.setAttribute('r', c ? Math.max(2.5, n._r * Math.sqrt(c / tot)).toFixed(1) : 0);
    });
    if (clock) { const y = Math.floor(t / 100); clock.textContent = !t ? '' : (monthly.has(y) ? MONTHS[t % 100 - 1] + ' ' + y : y); }
    return fresh;
  }
  function step() {
    i++; const fresh = draw();
    if (i >= steps.length - 1) { root._t = null; return; }
    const y = Math.floor(steps[i] / 100);
    const base = monthly.has(y) ? 170 : y < 1905 ? 220 : 70;
    root._t = setTimeout(step, Math.max(base, fresh * STAGGER + (fresh ? 400 : 0)));   // wait for the new labels to arrive
  }
  els.forEach(e => { e.style.display = 'none'; }); draw();
  root._t = setTimeout(step, 600);
}
function stopYears(root) {
  if (root._t) { clearTimeout(root._t); root._t = null; }
  root.querySelectorAll('[data-y]').forEach(e => { e.style.display = ''; e.classList.remove('fresh'); e.style.animationDelay = ''; });
  root.querySelectorAll('[data-c]').forEach(n => n.setAttribute('r', n.dataset.r));
  const c = root.querySelector('.clock'); if (c) c.textContent = c.dataset.all || '';
}

// Stage-by-stage build for a slide with class "stages": elements with data-s appear from their stage on, and of the
// elements with data-only just the current stage's is shown. Used by the source-by-source build-up slide.
const STAGE_MS = 2300;
function playStages(root) {
  stopStages(root);
  const els = [...root.querySelectorAll('[data-s]')], only = [...root.querySelectorAll('[data-only]')];
  const last = Math.max(...els.map(e => +e.dataset.s));
  let i = -1; root.classList.add('playing'); root.classList.remove('finale');
  els.forEach(e => { e.style.display = 'none'; }); only.forEach(e => { e.style.display = 'none'; });
  function step() {
    i++;
    els.forEach(e => { if (+e.dataset.s === i) e.style.display = ''; });
    only.forEach(e => { e.style.display = +e.dataset.only === i ? '' : 'none'; });
    root.classList.toggle('finale', i === last);
    root._s = i < last ? setTimeout(step, i === last - 1 ? STAGE_MS + 1200 : STAGE_MS) : null;
  }
  root._s = setTimeout(step, 700);
}
function stopStages(root) {
  if (root._s) { clearTimeout(root._s); root._s = null; }
  root.classList.remove('playing');
  const only = [...root.querySelectorAll('[data-only]')]; const last = Math.max(...only.map(e => +e.dataset.only));
  root.classList.add('finale');
  root.querySelectorAll('[data-s]').forEach(e => { e.style.display = ''; });
  only.forEach(e => { e.style.display = +e.dataset.only === last ? '' : 'none'; });
}
