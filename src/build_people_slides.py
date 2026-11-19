"""Write slides_people.html: the people-and-plants section.

  p1  the Ceylon career video, full screen
  p2  Two botanists and the world the journal builds around them   (network: articles, people, places, commodities)
  p3  Leonard Woolf: a career inside the island, and the link out to his novel through Wikidata

Careers are as recorded in the Colonial Office List (extracted records, not checked against the pages).
Wikidata entries read back on 18 November 2026: Trimen Q2462643, Morris Q20733957, Woolf Q703935,
The Village in the Jungle Q19902832 (author: Woolf). Woolf and Trimen are not yet linked in the base.
Edit this file and rerun; then `python3 render_slides.py slides_people.html [--dark]`.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS = ["The base", "The question", "Quinine", "Rubber and rice", "People and plants", "The invitation"]
SEC = 4


def where(i):
    dots = "".join(f'<circle cx="{6 + 36 * k}" cy="10" r="{6 if k == i else 4}" fill="var(--{"accent" if k == i else "neutral"})"/>' for k in range(6))
    return (f'  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{dots}'
            f'<text x="204" y="15">{SECTIONS[i]}</text></svg>\n')


def slide(sid, title, rows, aria, note, extra="", note_style="top:566px", sec=SEC):
    body = "\n".join("    " + r for r in rows)
    return (f'<section class="slide" id="{sid}">\n  <p class="label">{SECTIONS[sec]}</p>\n  <h2>{title}</h2>\n{extra}'
            f'  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">\n{body}\n  </svg>\n'
            f'  <div class="note" style="{note_style}"><p>{note}</p></div>\n{where(sec)}</section>\n')


def st(x, y, name, yr="", dy=-26, anchor="middle", dx=0, r=8):
    y_ = f' <tspan class="yr">{yr}</tspan>' if yr else ""
    return f'<circle class="st" cx="{x}" cy="{y}" r="{r}"/><text class="stn" x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{name}{y_}</text>'


# p2: the network around Trimen and Morris in the journal (made by build_botanist_network.py) --------------------
net = (HERE / "botanist_network.inc.svg").read_text(encoding="utf-8").splitlines()
KEY = [("var(--neutral)", "article", 3), ("var(--career)", "person", 7), ("var(--iol)", "place", 7), ("var(--coconut)", "commodity", 7)]
key = ['<g class="key">'] + [f'<circle cx="{820 + 105 * k}" cy="640" r="{r}" fill="{col}"/><text x="{832 + 105 * k}" y="645">{name}</text>'
                             for k, (col, name, r) in enumerate(KEY)] + ['</g>']
p2 = net + key

# p3: Woolf ------------------------------------------------------------------------------------------------------
STOPS = [(180, "Jaffna", "1905", "police magistrate"), (260, "Mannar", "1906", "acting assistant government agent"),
         (340, "Kandy", "1907", "office assistant to the government agent"), (420, "Hambantota", "1908–11", "assistant government agent")]
p3 = ['<path class="line" stroke="var(--career)" d="M560 180 V420"/>',
      '<path class="line" stroke="var(--ring)" stroke-width="4" stroke-dasharray="2 10" d="M560 420 L640 500 H860"/>',
      '<text class="ln" x="750" y="484" text-anchor="middle" fill="var(--second)">through Wikidata</text>']
for y, name, yr, office in STOPS:
    p3.append(f'<circle class="st" cx="560" cy="{y}" r="9"/><text class="stn" x="584" y="{y - 2}">{name} <tspan class="yr">{yr}</tspan></text><text class="yr" x="584" y="{y + 20}">{office}</text>')
p3 += ['<circle class="st" cx="860" cy="500" r="11" stroke-width="4"/>',
       '<text class="stn" x="884" y="498" style="font-size:22px">The Village in the Jungle</text>',
       '<text class="yr" x="884" y="522">his novel, 1913</text>']
p3x = ('  <div class="maps"><img src="images/woolf_ceylon.png" style="left:96px" '
       'alt="Map of Ceylon with a line joining Jaffna 1905, Mannar 1906, Kandy 1907 and Hambantota 1908 to 1911"></div>\n')

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>People and plants: draft slides</title>
<!-- Draft slides for the people-and-plants section, each 1280 x 720. Add ?dark for the dark version.
     Written by build_people_slides.py; edit that file, not this one. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>

<!-- p1: the Ceylon career video, edge to edge -->
<section class="slide video" id="p1">
  <video controls muted playsinline preload="none" poster="../career_video/final_frame_1880.png" aria-label="Animated map of the career moves of officials who served in Ceylon">
    <source src="../career_video/ceylon_careers_1880.mp4" type="video/mp4">
  </video>
</section>

""" + slide("p2", "Two botanists at the centre of the journal", p2,
            "A network drawn from The Tropical Agriculturist. Henry Trimen and Daniel Morris are the two large nodes. About 1,250 small dots are the articles that name either of them. Around them sit the people most often named in the same articles, such as Thwaites, Marshall Ward, Nock, Hooker and J. E. Howard, the places, such as Peradeniya, Kew, Jamaica and Java, and the commodities, led by coffee, tea, cacao, rubber and cinchona.",
            "About 1,250 articles, and more than 3,000 other people named in them.",
            note_style="top:626px;left:96px;width:700px;font-size:18px") + "\n" + \
    slide("p3", "Leonard Woolf: a career inside the island", p3,
          "Leonard Woolf's postings as a line: Jaffna 1905, Mannar 1906, Kandy 1907, Hambantota 1908 to 1911. A dotted link runs on from Hambantota, through Wikidata, to his novel The Village in the Jungle, 1913.",
          "The List places him at four stations in seven years. His Wikidata identifier leads on from the career to the novel.", p3x, "top:572px;left:456px;width:740px", sec=0) + """
<script src="anim.js"></script>
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');
// click the year on the network slide to play it
document.querySelectorAll('.clock').forEach(c => c.addEventListener('click', () => playYears(c.closest('.slide'))));</script>
</body>
</html>
"""
(HERE / "slides_people.html").write_text(HTML, encoding="utf-8")
print("wrote", HERE / "slides_people.html")
