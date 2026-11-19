"""Write slides_transition.html: three slides for the turn from the base to the builds.

  t1  A base world for others to build on          (the Minecraft image)
  t2  Wikidata gives every builder the same coordinates
  t3  Use the place as it was, and mint it if it is missing

Edit this file and rerun; then `python3 render_slides.py slides_transition.html [--dark]`.
The style (line colours, stations, type) is in slides.css.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

WHERE = ('  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>'
         '<circle cx="6" cy="10" r="6" fill="var(--accent)"/>'
         + "".join(f'<circle cx="{x}" cy="10" r="4" fill="var(--neutral)"/>' for x in (42, 78, 114, 150, 186))
         + '<text x="204" y="15">The base</text></svg>\n')


def slide(sid, title, rows, aria, note):
    body = "\n".join("    " + r for r in rows)
    return (f'<section class="slide" id="{sid}">\n  <p class="label">The base</p>\n  <h2>{title}</h2>\n'
            f'  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">\n{body}\n  </svg>\n'
            f'  <div class="note" style="top:566px"><p>{note}</p></div>\n{WHERE}</section>\n')


# t1: the base, and what is built on it -------------------------------------------------------------------------
t1 = ['<path class="line thick" stroke="var(--career)" d="M110 470 H1170"/>',
      '<text class="ln" x="110" y="512" fill="var(--career)">the base · places as they were · people · years</text>']
BUILDS = [(260, 300, "var(--tea)", "Ceylon", "Blue Books, journal, trade", False),
          (520, 240, "var(--rubber)", "Canada78", "census, Indian Affairs, trade", False),
          (780, 330, "var(--bark)", "Commodity web", "tea, quinine, rubber, rice", False),
          (1040, 280, "var(--neutral)", "your build", "", True)]
for x, top, col, name, sub, open_ in BUILDS:
    dash = ' stroke-dasharray="2 11" stroke-width="5"' if open_ else ""
    ring = ' style="stroke:var(--neutral)"' if open_ else ""
    fill = ' style="fill:var(--second)"' if open_ else ""
    t1.append(f'<path class="line" stroke="{col}"{dash} d="M{x} 470 V{top}"/>')
    t1.append(f'<circle class="st" cx="{x}" cy="470" r="9"/><circle class="st" cx="{x}" cy="{top}" r="9"{ring}/>')
    t1.append(f'<text class="stn" x="{x + 20}" y="{top + 2}"{fill}>{name}</text>')
    if sub: t1.append(f'<text class="yr" x="{x + 20}" y="{top + 26}">{sub}</text>')

# t2: five sources meet at one identifier -----------------------------------------------------------------------
SOURCES = [("The Colonial and India Office Lists", "var(--career)"), ("Ceylon Blue Books", "var(--bark)"),
           ("The Tropical Agriculturist", "var(--tea)"), ("British trade tables", "var(--rubber)"),
           ("Canadian trade tables", "var(--rice)")]
t2 = []
for i, (name, col) in enumerate(SOURCES):
    ys, yb = 210 + 75 * i, 342 + 9 * i               # where the line starts, and where it runs in the bundle
    bend = f"H{500 - abs(ys - yb)} L500 {yb} " if ys != yb else ""
    t2.append(f'<path class="line" stroke="{col}" stroke-width="6" d="M110 {ys} {bend}H1150"/>')
    t2.append(f'<text class="ln" x="110" y="{ys - 14}" fill="{col}">{name}</text>')
t2 += ['<rect class="st" x="668" y="330" width="22" height="60" rx="11" stroke-width="4"/>',
       '<text class="stn" x="679" y="296" text-anchor="middle" style="font-size:26px">British Ceylon, 1795–1948</text>',
       '<text class="yr" x="679" y="428" text-anchor="middle" style="font-size:18px">one Wikidata identifier: Q918153</text>',
       '<rect class="st" x="1139" y="330" width="22" height="60" rx="11"/>',
       '<text class="stn" x="1150" y="296" text-anchor="middle">one graph</text>']

# t3: the place as it was ----------------------------------------------------------------------------------------
t3 = ['<path class="line" stroke="var(--career)" d="M110 300 H1170"/>',
      '<path class="line" stroke="var(--bark)" d="M110 450 H1170"/>',
      '<text class="ln" x="110" y="262" fill="var(--career)">The Lists and the Blue Books</text>',
      '<text class="ln" x="110" y="496" fill="var(--bark)">Encyclopaedia Britannica, 1771–1860</text>',
      '<path class="line" stroke="var(--ring)" stroke-width="4" stroke-dasharray="2 10" d="M640 300 V450"/>',
      '<circle class="st" cx="640" cy="300" r="13" stroke-width="4"/>',
      '<text class="stn" x="640" y="262" text-anchor="middle" style="font-size:24px">British Ceylon, 1795–1948</text>',
      '<circle class="st" cx="640" cy="450" r="13" stroke-width="4"/>',
      '<text class="stn" x="640" y="496" text-anchor="middle" style="font-size:24px">Sri Lanka, the modern state</text>',
      '<text class="yr" x="662" y="381" style="font-size:18px">a bridge had to be added</text>']

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The base world and Wikidata: draft transition slides</title>
<!-- Draft slides for the turn from the base to the builds, each 1280 x 720. Add ?dark for the dark version.
     Written by build_transition_slides.py; edit that file, not this one. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>

""" + slide("t1", "A base world for others to build on", t1,
            "A thick ground line labelled the base: places as they were, people, years. Four lines rise from it like buildings: Ceylon, Canada78, the commodity web, and a dotted one labelled your build.",
            "Like the base world in Minecraft: the terrain is shared, and anyone can build on it.") + "\n" + \
    slide("t2", "Wikidata gives every builder the same coordinates", t2,
          "Five lines, one for each source, arrive from different places and run together through a single station, British Ceylon 1795 to 1948, with one Wikidata identifier, then continue as one graph.",
          "Five sources name the same colony. One identifier lets them meet at the same station.") + "\n" + \
    slide("t3", "Use the place as it was, and mint it if it is missing", t3,
          "Two parallel lines that do not share a station. The Lists and Blue Books stop at British Ceylon, 1795 to 1948. Britannica stops at Sri Lanka, the modern state. A dotted link joins the two stations: a bridge had to be added.",
          "Britannica’s Ceylon was linked to the modern state, so it never met the Lists. The rule for the base: the place of the period, and a new Wikidata entry where none exists.") + """
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');</script>
</body>
</html>
"""
(HERE / "slides_transition.html").write_text(HTML, encoding="utf-8")
print("wrote", HERE / "slides_transition.html")
