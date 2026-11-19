"""Assemble the drafted slides into one deck, deck.html, in running order.

Reads the slide files beside this script and writes deck.html: one slide on screen at a time, scaled to the
window. Keys: right/space/PageDown next, left/PageUp back, Home/End, d toggles dark, f full screen, r replays
the year-by-year network slide and the source-by-source build-up slide.
The address keeps the slide number (deck.html#7); add ?dark to start dark.

Change ORDER to reorder or drop slides, then rerun. Serve the folder above this one so the videos resolve:

    cd /home/jic823/ceylon && python3 -m http.server 4330
    http://localhost:4330/ssha_talk/deck.html
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = [("front_slide.html", None),
         ("slides_02_06.html", ["s02", "s03", "s04", "s05"]),
         ("slides_ceylon.html", ["c1", "c2"]),
         ("slides_people.html", ["p3", "p1"]),                # Woolf on the island map, then the Ceylon career video
         ("slides_ceylon.html", ["c3", "c4"]),
         ("slides_transition.html", ["t1", "t2", "t3"]),
         ("slides_02_06.html", ["s06"]),
         ("slides_commodities.html", ["q1", "q2", "q3", "r1", "r2", "r3"]),
         ("slides_people.html", ["p2"]),
         ("slides_closing.html", ["e1", "a1"]),
         ("slides_graph.html", ["g1"]),
         ("slides_growth.html", ["n1"])]  # m2 (loop diagram), m0 (one man as a seed) and m1 (both directions) are held out


def sections(html):
    return {m.group(2): m.group(0) for m in re.finditer(r'<section class="(slide[^"]*)" id="([^"]+)">.*?</section>', html, re.S)}


def front():
    html = (HERE / "front_slide.html").read_text(encoding="utf-8")
    body = re.search(r'<div class="slide">(.*)</div>\s*<script>', html, re.S).group(1)
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    css = re.sub(r"@font-face\s*{[^}]*}", "", css)
    css = re.sub(r"(?:^|\n)\s*(:root|html\.dark|html, body|\.slide)\s*{[^}]*}", "", css)      # shared rules come from slides.css
    scoped = []
    for sel, rule in re.findall(r"([^{}]+){([^}]*)}", css):
        sel = ", ".join(".front " + s.strip() for s in sel.split(",") if s.strip())
        scoped.append(f"{sel} {{{rule}}}")
    return f'<section class="slide front" id="front">{body}</section>', "\n".join(scoped)


def main():
    cache, slides = {}, []
    front_html, front_css = front()
    for name, ids in ORDER:
        if ids is None:
            slides.append(front_html); continue
        if name not in cache: cache[name] = sections((HERE / name).read_text(encoding="utf-8"))
        for i in ids: slides.append(cache[name][i])
    css = (HERE / "slides.css").read_text(encoding="utf-8")
    anim = (HERE / "anim.js").read_text(encoding="utf-8")
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mapping the Colonial Administrative State (draft deck)</title>
<!-- Written by build_deck.py from the slide files in this folder; edit those, not this. {len(slides)} slides. -->
<style>
{css}
:root {{ --station-ring: var(--ring); }}
html, body {{ margin: 0; height: 100%; background: var(--ground); overflow: hidden; }}
#stage {{ position: absolute; left: 50%; top: 50%; width: 1280px; height: 720px; transform-origin: 0 0; }}
#stage > .slide {{ position: absolute; left: 0; top: 0; margin: 0; display: none; }}
#stage > .slide.on {{ display: block; }}
#count {{ position: fixed; right: 14px; bottom: 10px; font: 14px "Atkinson Next", Arial, sans-serif; color: var(--second); opacity: .7; }}
/* front slide, scoped */
.front {{ --station: var(--ground); }}
{front_css}
.front .label, .front h1, .front .sub, .front .who, .front .foot {{ position: static; }}
.front .words {{ position: absolute; }} .front .foot {{ position: absolute; }}
</style>
</head>
<body>
<div id="stage">
{chr(10).join(slides)}
</div>
<div id="count"></div>
<script>
{anim}
if (location.search.includes('dark')) document.documentElement.classList.add('dark');
const S = [...document.querySelectorAll('#stage > .slide')], stage = document.getElementById('stage'), count = document.getElementById('count');
let i = Math.min(S.length - 1, Math.max(0, (parseInt(location.hash.slice(1)) || 1) - 1));
function fit() {{ const k = Math.min(innerWidth / 1280, innerHeight / 720); stage.style.transform = `scale(${{k}}) translate(-50%, -50%)`; }}
function show(n) {{
  i = Math.min(S.length - 1, Math.max(0, n));
  S.forEach((s, j) => {{ s.classList.toggle('on', j === i); const v = s.querySelector('video'); if (v) {{ if (j === i) {{ v.currentTime = 0; v.play().catch(() => {{}}); }} else v.pause(); }}
    if (s.querySelector('.clock')) {{ if (j === i) playYears(s); else stopYears(s); }}
    if (s.classList.contains('stages')) {{ if (j === i) playStages(s); else stopStages(s); }} }});
  history.replaceState(null, '', '#' + (i + 1)); count.textContent = (i + 1) + ' / ' + S.length;
}}
addEventListener('resize', fit);
addEventListener('keydown', e => {{
  if (['ArrowRight', 'PageDown', ' ', 'Enter'].includes(e.key)) {{ show(i + 1); e.preventDefault(); }}
  else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) {{ show(i - 1); e.preventDefault(); }}
  else if (e.key === 'Home') show(0); else if (e.key === 'End') show(S.length - 1);
  else if (e.key === 'd') document.documentElement.classList.toggle('dark');
  else if (e.key === 'r' && S[i].querySelector('.clock')) playYears(S[i]);
  else if (e.key === 'r' && S[i].classList.contains('stages')) playStages(S[i]);
  else if (e.key === 'f') (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen());
}});
addEventListener('click', e => {{ if (e.target.closest('video, a')) return; show(i + (e.clientX < innerWidth / 3 ? -1 : 1)); }});
fit(); show(i);
</script>
</body>
</html>
"""
    (HERE / "deck.html").write_text(page, encoding="utf-8")
    print("wrote", HERE / "deck.html", "|", len(slides), "slides")


if __name__ == "__main__":
    main()
