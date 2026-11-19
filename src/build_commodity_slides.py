"""Write slides_commodities.html: the quinine slides and the rubber-and-rice slides.

  q1  Quinine: from Ceylon's hills to Canada                (one line, with the record behind each station)
  q2  Ceylon flooded London with bark                       (bars, 1880-1900)
  q3  And quinine became cheap in Canada                    (two unit values, indexed to 1880)
  r1  the trade video, full screen
  r2  One colony, three geographies                         (tea, rubber, coconut)
  r3  Ghost acres of ghost acres                            (what Ceylon drew in to send those out)

Figures come from ../quinine_chain/quinine_chain_data.tsv and are shown rounded: they are extracted readings
not yet checked against the pages, so the slides state trends, not exact values.
Edit this file and rerun; then `python3 render_slides.py slides_commodities.html [--dark]`.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS = ["The base", "The question", "Quinine", "Rubber and rice", "People and plants", "The invitation"]


def where(i):
    dots = "".join(f'<circle cx="{6 + 36 * k}" cy="10" r="{6 if k == i else 4}" fill="var(--{"accent" if k == i else "neutral"})"/>' for k in range(6))
    return (f'  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{dots}'
            f'<text x="204" y="15">{SECTIONS[i]}</text></svg>\n')


def slide(sid, sec, title, rows, aria, note="", extra=""):
    body = "\n".join("    " + r for r in rows)
    n = f'  <div class="note" style="top:566px"><p>{note}</p></div>\n' if note else ""
    return (f'<section class="slide" id="{sid}">\n  <p class="label">{SECTIONS[sec]}</p>\n  <h2>{title}</h2>\n'
            f'  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">\n{body}\n  </svg>\n{extra}{n}{where(sec)}</section>\n')


def st(x, y, name, dy=-26, anchor="middle", r=8, dx=0):
    return f'<circle class="st" cx="{x}" cy="{y}" r="{r}"/><text class="stn" x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{name}</text>'


data = list(csv.DictReader(open(HERE.parent / "quinine_chain" / "quinine_chain_data.tsv", encoding="utf-8"), delimiter="\t"))
num = lambda v: float(v) if v else None

# q1: the quinine line -----------------------------------------------------------------------------------------
q1 = ['<path class="line" stroke="var(--bark)" d="M170 330 H1090"/>',
      '<text class="ln" x="320" y="312" text-anchor="middle" fill="var(--bark)">cinchona bark</text>',
      '<text class="ln" x="630" y="312" text-anchor="middle" fill="var(--bark)">cinchona bark</text>',
      '<text class="ln" x="935" y="312" text-anchor="middle" fill="var(--bark)">quinine</text>',
      st(170, 330, "Ceylon’s estates", dy=-62), st(480, 330, "London bark sales", dy=-62),
      st(780, 330, "Stratford works", dy=-62), st(1090, 330, "Canada", dy=-62)]
SRC = [(170, "<b>Blue Books</b>bark exported, by destination"), (480, "<b>British trade tables</b>bark landed from Ceylon"),
       (780, "<b>The Tropical Agriculturist</b>Howards &amp; Sons, “principal buyer”"),
       (1090, "<b>Canadian trade tables</b>quinine imported; a purchase of “Howard’s quinine” in 1899")]
q1x = "".join(f'  <p class="src" style="left:{x - 120}px">{t}</p>\n' for x, t in SRC)

# q2: bark landed in Britain from Ceylon ------------------------------------------------------------------------
X0, X1, YB, YT = 130, 1150, 510, 250
bark = {int(r["year"]): num(r["uk_bark_from_ceylon_cwt"]) for r in data}
mx = max(v for v in bark.values() if v)
xs = lambda y: X0 + (y - 1880) * (X1 - X0) / 20
q2 = [f'<path d="M{X0 - 24} {YB} H{X1 + 24}" stroke="var(--neutral)" stroke-width="2"/>']
for y, v in bark.items():
    if v: q2.append(f'<rect x="{xs(y) - 15:.0f}" y="{YB - (YB - YT) * v / mx:.0f}" width="30" height="{(YB - YT) * v / mx:.0f}" rx="3" fill="var(--bark)"/>')
for y in (1880, 1885, 1890, 1895, 1900): q2.append(f'<text class="yr" x="{xs(y):.0f}" y="{YB + 28}" text-anchor="middle" style="font-size:18px">{y}</text>')
q2 += [f'<text class="stn" x="{xs(1880) - 15:.0f}" y="{YB - 66}">about 10,000</text>',
       f'<text class="stn" x="{xs(1886):.0f}" y="{YT - 14}" text-anchor="middle">about 115,000 cwt in 1886</text>',
       f'<text class="stn" x="{xs(1900) + 15:.0f}" y="{YB - 40}" text-anchor="end">under 10,000 again</text>']

# q3: unit values, 1880 = 100 -----------------------------------------------------------------------------------
YT3 = 240
ys = lambda v: YB - (YB - YT3) * v / 100


def path(key):
    d, pen = [], False
    for r in data:
        v = num(r[key])
        if v is None: pen = False; continue
        d.append(f'{"L" if pen else "M"}{xs(int(r["year"])):.0f} {ys(v):.0f}'); pen = True
    return " ".join(d)


q3 = [f'<path d="M{X0 - 24} {YB} H{X1 + 24}" stroke="var(--neutral)" stroke-width="2"/>',
      f'<path d="M{X0 - 24} {ys(100):.0f} H{X1 + 24}" stroke="var(--rule)" stroke-width="2" stroke-dasharray="2 8"/>',
      f'<text class="yr" x="{X0 - 30}" y="{ys(100) - 10:.0f}" style="font-size:16px">1880 level</text>',
      f'<path class="line" stroke="var(--bark)" stroke-width="5" d="{path("bark_value_index_1880_100")}"/>',
      f'<path class="line" stroke="var(--ring)" stroke-width="5" d="{path("quinine_value_index_1880_100")}"/>']
for y in (1880, 1885, 1890, 1895, 1900): q3.append(f'<text class="yr" x="{xs(y):.0f}" y="{YB + 28}" text-anchor="middle" style="font-size:18px">{y}</text>')
q3 += [f'<text class="ln" x="{xs(1884) + 16:.0f}" y="{ys(64):.0f}" fill="var(--bark)">bark in London</text>',
       f'<text class="ln" x="{xs(1881):.0f}" y="{YB - 36}" fill="var(--ring)">quinine entering Canada</text>',
       f'<text class="stn" x="{xs(1893):.0f}" y="{ys(46):.0f}" style="font-size:24px">down by about four-fifths</text>',
       f'<text class="yr" x="{xs(1893):.0f}" y="{ys(46) + 26:.0f}" style="font-size:18px">in ten years, on both sides of the Atlantic</text>']

# r2: one colony, three geographies -----------------------------------------------------------------------------
r2 = ['<path class="line" stroke="var(--tea)" d="M210 380 L290 300 H1100"/>', '<path class="line" stroke="var(--rubber)" d="M210 380 H1020 L1100 300"/>',
      '<path class="line" stroke="var(--coconut)" d="M210 380 L290 460 H1150"/>',
      '<text class="ln" x="330" y="282" fill="var(--tea)">tea</text>', '<text class="ln" x="330" y="362" fill="var(--rubber)">rubber</text>',
      '<text class="ln" x="330" y="442" fill="var(--coconut)">coconut products</text>',
      st(640, 300, "London", dy=-18),
      st(640, 380, "London, to 1915", dy=-18), st(880, 380, "United States, from 1916", dy=-18),
      '<text class="yr" x="1100" y="410" text-anchor="end">nearly all of Canada’s crude rubber came through the United States</text>',
      '<rect class="st" x="1091" y="286" width="18" height="28" rx="9"/><text class="stn" x="1100" y="268" text-anchor="middle">Canada</text>',
      st(580, 460, "Germany", dy=34), st(790, 460, "Italy", dy=34), st(1010, 460, "Denmark, Norway", dy=34),
      '<circle class="st" cx="210" cy="380" r="16" stroke-width="4"/><text class="stn" x="196" y="346" text-anchor="end" style="font-size:24px">Ceylon</text>']

# r3: what Ceylon drew in to send those out --------------------------------------------------------------------
r3 = ['<path class="line" stroke="var(--rubber)" d="M640 370 L560 290 H190"/>', '<path class="line" stroke="var(--tea)" d="M640 370 L560 450 H190"/>',
      '<path class="line" stroke="var(--rice)" d="M640 370 L720 290 H1090"/>', '<path class="line" stroke="var(--bark)" d="M640 370 H1090"/>',
      '<path class="line" stroke="var(--neutral)" d="M640 370 L720 450 H1090"/>',
      '<text class="ln" x="370" y="272" text-anchor="middle" fill="var(--rubber)">rubber out</text>',
      '<text class="ln" x="370" y="482" text-anchor="middle" fill="var(--tea)">tea out</text>',
      '<text class="ln" x="900" y="272" text-anchor="middle" fill="var(--rice)">rice in · food</text>',
      '<text class="ln" x="900" y="352" text-anchor="middle" fill="var(--bark)">oilseed cake, bone in · soil</text>',
      '<text class="ln" x="900" y="432" text-anchor="middle" fill="var(--second)">coal and oil in · energy</text>',
      st(190, 290, "United States", dy=-20, anchor="start", dx=-8), st(190, 450, "Britain, Canada", dy=36, anchor="start", dx=-8),
      st(1090, 290, "Burma", dy=-20, anchor="end", dx=8), st(1090, 370, "India", dy=6, anchor="start", dx=18),
      st(1090, 450, "Borneo, Sumatra, Persia", dy=36, anchor="end", dx=8),
      '<circle class="st" cx="640" cy="370" r="16" stroke-width="4"/><text class="stn" x="640" y="304" text-anchor="middle" style="font-size:24px">Ceylon</text>']

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Quinine, rubber and rice: draft slides</title>
<!-- Draft slides for the commodity sections, each 1280 x 720. Add ?dark for the dark version.
     Written by build_commodity_slides.py; edit that file, not this one. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>

""" + slide("q1", 2, "Quinine: from Ceylon’s hills to Canada", q1,
            "One line with four stations: Ceylon's estates, London bark sales, the Stratford works, Canada. It carries cinchona bark as far as Stratford and quinine after it. Beneath each station is the source that records it.",
            "No single source records this line. It appears when four of them are joined.", q1x) + "\n" + \
    slide("q2", 2, "Ceylon flooded London with bark", q2,
          "Bars for cinchona bark landed in Britain from Ceylon each year from 1880 to 1900: about 10,000 hundredweight in 1880, about 115,000 at the peak in 1886, and under 10,000 again by the late 1890s.",
          "By 1885 nearly all of London’s bark came from Ceylon. Then the price collapsed and the planters turned to tea.") + "\n" + \
    slide("q3", 2, "And quinine became cheap in Canada", q3,
          "Two lines from 1880 to 1900, each starting at 100: the value of Ceylon bark in London and the value of quinine entering Canada. Both fall by about four-fifths within ten years and stay low.",
          "Canada took nine times as much quinine in 1890 as in 1880, for about the same money.") + """
<!-- r1: the trade video, edge to edge -->
<section class="slide video" id="r1">
  <video controls muted playsinline preload="none" poster="../trade_video/still_44.png" aria-label="Animated map of Ceylon's trade, 1913 to 1928, by partner and commodity">
    <source src="../trade_video/ceylon_trade.mp4" type="video/mp4">
  </video>
</section>

""" + slide("r2", 3, "One colony, three geographies", r2,
            "Three lines leave Ceylon. Tea runs to London and on to Canada. Rubber runs to London until 1915 and to the United States from 1916, then turns up to join tea at Canada: nearly all of Canada's crude rubber came through the United States. Coconut products run to Germany, Italy, Denmark and Norway.",
            "Tea stayed imperial. Rubber went to America, and reached Canada from there. Coconut went to the Continent.") + "\n" + \
    slide("r3", 3, "Ghost acres of ghost acres", r3,
          "Ceylon as an interchange. Rubber goes out to the United States and tea to Britain and Canada. Coming in: rice from Burma, for food; oilseed cake and bone from India, for soil; coal and oil from Borneo, Sumatra and Persia, for energy.",
          "Rice was a quarter to a third of everything Ceylon imported. Its rubber land grew by half a million acres; its own rice land did not.") + """
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');</script>
</body>
</html>
"""
(HERE / "slides_commodities.html").write_text(HTML, encoding="utf-8")
print("wrote", HERE / "slides_commodities.html")
