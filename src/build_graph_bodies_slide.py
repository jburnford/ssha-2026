"""Write slides_graph_bodies.html: one slide (g1), the graph of bodies in Ferguson's Ceylon Directory 1920-21 joined by shared people.

Reads ../kg_build/dir_bodies.tsv, dir_body_links.tsv, dir_counts.json (run ../kg_build/build_directory_graph.py first).
Each disc is a body (department, firm, society, council, club, court) with five or more named people; its area is the
number of people; its colour is the share judged Ceylonese from their names. A line joins two bodies that print the
same name. As extracted by an open model: namesakes are not separated and nothing is tied to identifiers.
The slide in the deck (places, gardens, estates, from the sampled pages) is build_graph_slide.py; this one is held out.

    python3 build_graph_bodies_slide.py && python3 render_slides.py slides_graph_bodies.html [--dark] && python3 build_deck.py
"""
import csv, json, math, collections
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent
KG = HERE.parent / "kg_build"
SECTION, SEC = "Going forward", 5
BOX = (60, 190, 950, 648)          # left, top, right, bottom of the drawing
MIN = 5
LABELS = {}                        # body key -> (text, dx, dy, anchor); set after looking at a render
NOTES = [("ceylon chamber of commerce", "Ceylon Chamber of Commerce", "{m} names, nearly all European"),
         ("low country products association", "Low-Country Products Association", "{m} names, nearly all Ceylonese"),
         ("legislative council", "Legislative Council", "where the two worlds meet"),
         ("ceylon agricultural society", "Ceylon Agricultural Society", "mostly Ceylonese, {d} ties"),
         ("government medical service", "Government Medical Service", "largely Ceylonese staff"),
         ("ceylon association in london", "Ceylon Association in London", "the London end of the estates")]


def rd(name):
    return list(csv.DictReader(open(KG / name, encoding="utf-8"), delimiter="\t"))


def main():
    bodies = {b["key"]: b for b in rd("dir_bodies.tsv") if int(b["members"]) >= MIN}
    links = [(l["body_a"], l["body_b"], int(l["shared_people"])) for l in rd("dir_body_links.tsv") if l["body_a"] in bodies and l["body_b"] in bodies]
    g = nx.Graph()
    for a, b, n in links: g.add_edge(a, b, weight=n)
    comp = max(nx.connected_components(g), key=len); g = g.subgraph(comp).copy()
    pos = nx.spring_layout(g, k=1.9 / math.sqrt(len(g)), iterations=300, seed=7, weight="weight")
    cx = sum(p[0] for p in pos.values()) / len(pos); cy = sum(p[1] for p in pos.values()) / len(pos)
    for k, p in pos.items():                              # pull the stragglers in so the core has room
        dx, dy = p[0] - cx, p[1] - cy; d = math.hypot(dx, dy) or 1e-9; f = d ** 0.55 / d
        pos[k] = (dx * f * 1.35, dy * f)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    def place(p):
        return (BOX[0] + 20 + (p[0] - min(xs)) / (max(xs) - min(xs)) * (BOX[2] - BOX[0] - 40), BOX[1] + 20 + (p[1] - min(ys)) / (max(ys) - min(ys)) * (BOX[3] - BOX[1] - 40))
    P = {k: list(place(p)) for k, p in pos.items()}
    R = {k: 1.45 * math.sqrt(int(bodies[k]["members"])) + 1 for k in P}
    keys = sorted(P, key=lambda k: -R[k])
    for _ in range(60):                                   # push overlapping discs apart
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                dx, dy = P[b][0] - P[a][0], P[b][1] - P[a][1]; d = math.hypot(dx, dy) or 0.01; need = R[a] + R[b] + 1.5
                if d < need:
                    s = (need - d) / 2 / d; P[a][0] -= dx * s; P[a][1] -= dy * s; P[b][0] += dx * s; P[b][1] += dy * s
        for k in keys:
            P[k][0] = min(max(P[k][0], BOX[0] + R[k]), BOX[2] - R[k]); P[k][1] = min(max(P[k][1], BOX[1] + R[k]), BOX[3] - R[k])

    def share(k):
        c, e = int(bodies[k]["ceylonese"]), int(bodies[k]["european"])
        return c / max(c + e, 1)
    def colour(k):
        s = share(k)
        return "var(--coconut)" if s >= 2 / 3 else "var(--career)" if s <= 1 / 3 else "var(--rice)"
    out = []
    for lo, hi, op, wd in ((1, 1, 0.16, 0.6), (2, 3, 0.3, 0.9), (4, 99, 0.5, 1.5)):
        d = "".join(f"M{P[a][0]:.0f} {P[a][1]:.0f}L{P[b][0]:.0f} {P[b][1]:.0f}" for a, b, w in g.edges(data="weight") if lo <= w <= hi)
        out.append(f'<path d="{d}" fill="none" stroke="var(--title)" stroke-opacity="{op}" stroke-width="{wd}"/>')
    for k in reversed(keys):
        out.append(f'<circle cx="{P[k][0]:.1f}" cy="{P[k][1]:.1f}" r="{R[k]:.1f}" fill="{colour(k)}" stroke="var(--ground)" stroke-width="1.2"/>')
    for k, (text, dx, dy, anc) in LABELS.items():
        if k in P: out.append(f'<text class="nl" x="{P[k][0] + dx:.0f}" y="{P[k][1] + dy:.0f}" text-anchor="{anc}" style="font-size:13px">{text}</text>')

    def badge(x, y, n):
        return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="10" fill="var(--title)" stroke="var(--ground)" stroke-width="2"/>'
                f'<text x="{x:.0f}" y="{y + 4.5:.0f}" text-anchor="middle" style="font-size:13px;font-weight:700;fill:var(--ground)">{n}</text>')
    X, y = 978, 196
    for n, (k, *lines) in enumerate(NOTES, 1):
        if k in P: out.append(badge(P[k][0] + R[k] * 0.75 + 4, P[k][1] - R[k] * 0.75 - 4, n))
        out.append(badge(X + 10, y - 5, n))
        if k not in P: raise SystemExit("note body not drawn: " + k)
        for j, l in enumerate(lines):
            out.append(f'<text class="{"nl" if j == 0 else "yr"}" x="{X + 28}" y="{y + 19 * j}">{l.format(m=bodies[k]["members"], d=g.degree(k))}</text>')
        y += 19 * len(lines) + 20

    c = json.load(open(KG / "dir_counts.json"))
    out += [f'<path d="M{X} 566H1236" stroke="var(--neutral)" stroke-width="1"/>',
            f'<text class="nl" x="{X}" y="590">Ferguson’s Ceylon Directory, 1920–21</text>',
            f'<text class="yr" x="{X}" y="609">about {round(c["people"], -2):,} people under {round(c["bodies"], -2):,} bodies;</text>',
            f'<text class="yr" x="{X}" y="628">about {round(c["people_in_two_or_more_bodies"], -2):,} sit in two or more.</text>',
            f'<text class="yr" x="{X}" y="647">Namesakes not yet separated.</text>']
    key = (f'<g transform="translate(96 160)"><circle cx="6" cy="0" r="6" fill="var(--coconut)"/><text class="yr" x="18" y="5">mostly Ceylonese</text>'
           f'<circle cx="170" cy="0" r="6" fill="var(--rice)"/><text class="yr" x="182" y="5">mixed</text>'
           f'<circle cx="250" cy="0" r="6" fill="var(--career)"/><text class="yr" x="262" y="5">mostly British or European</text>'
           f'<path d="M478 0h26" stroke="var(--title)" stroke-opacity="0.6"/><text class="yr" x="512" y="5">a name printed under both</text></g>')
    json.dump({k: [round(P[k][0]), round(P[k][1]), round(R[k]), bodies[k]["name"], bodies[k]["members"], round(share(k), 2), g.degree(k)] for k in keys},
              open(HERE / "graph_layout.json", "w"), indent=0, ensure_ascii=False)
    aria = (f"A network drawing of {len(g)} bodies from Ferguson's Ceylon Directory for 1920 to 1921, each a disc sized by the number of people named under it and coloured by "
            f"whether those people are mostly Ceylonese, mixed, or mostly British or European. {g.number_of_edges():,} lines join bodies that print the same person's name.")
    dots = "".join(f'<circle cx="{6 + 36 * i}" cy="10" r="{6 if i == SEC else 4}" fill="var(--{"accent" if i == SEC else "neutral"})"/>' for i in range(6))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Going forward: the graph build</title>
<!-- Written by build_graph_slide.py; edit that file, not this one. Add ?dark for the dark version. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>
<section class="slide" id="g2">
  <p class="label">{SECTION}</p>
  <h2>One directory, read in an hour by an open model</h2>
  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">
{key}
{chr(10).join(out)}
  </svg>
  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{dots}<text x="204" y="15">{SECTION}</text></svg>
</section>
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');</script>
</body>
</html>
"""
    (HERE / "slides_graph_bodies.html").write_text(html, encoding="utf-8")
    print("wrote slides_graph_bodies.html |", len(g), "bodies drawn of", len(bodies), "|", g.number_of_edges(), "links |", c)


if __name__ == "__main__":
    main()
