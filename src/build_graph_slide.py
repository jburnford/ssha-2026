"""Write slides_graph.html: one slide (g1) drawing the people graph built from the people extracted on 18-19 November 2026.

Reads ../kg_build/nodes.tsv and edges.tsv (run ../kg_build/build_people_graph.py first). Every dot is one person listed
under one body (a society, firm, court, newspaper, estate district or garden); bodies are grouped by place; a line joins
the dots of a person the extraction already found under two bodies. Nothing here is de-duplicated or tied to identifiers.

    python3 build_graph_slide.py && python3 render_slides.py slides_graph.html [--dark] && python3 build_deck.py
"""
import csv, math, collections, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KG = HERE.parent / "kg_build"
S = 2.5                           # spacing of dots inside a body
BOUNDS = (40, 176, 968, 652)     # left, top, right, bottom of the drawing
SECTION, SEC = "Going forward", 5
COL = {"Ceylonese": "var(--coconut)", "British or European": "var(--career)", "unclear": "var(--neutral)"}


def rd(name):
    return list(csv.DictReader(open(KG / name, encoding="utf-8"), delimiter="\t"))


def pack(items, anchor, placed, bounds=None, aspect=1.0, pad=2.0):
    """Greedy spiral packing: put each (key, radius), largest first, at the free spot nearest its anchor."""
    out = {}
    for key, r in sorted(items, key=lambda kr: -kr[1]):
        ax, ay = anchor(key) if callable(anchor) else anchor
        for t in range(0, 60000):
            d = 1.6 * math.sqrt(t); th = t * 2.399963
            x, y = ax + d * math.cos(th) * aspect, ay + d * math.sin(th)
            if bounds and not (bounds[0] + r <= x <= bounds[2] - r and bounds[1] + r <= y <= bounds[3] - r): continue
            if all((x - px) ** 2 + (y - py) ** 2 >= (r + pr + pad) ** 2 for px, py, pr in placed):
                placed.append((x, y, r)); out[key] = (x, y); break
        else:
            raise SystemExit(f"could not place {key}")
    return out


def main():
    nodes = rd("nodes.tsv"); edges = rd("edges.tsv")
    person = {r["id"]: r for r in nodes if r["type"] == "person"}; body = {r["id"]: r for r in nodes if r["type"] == "body"}
    members = collections.defaultdict(list)
    for e in edges: members[e["body"]].append(e["person"])
    by_place = collections.defaultdict(list)
    for b in members: by_place[body[b]["place_or_source"]].append(b)
    rad = {b: S * math.sqrt(len(m)) * 1.02 + 1.2 for b, m in members.items()}

    # bodies inside each place, then places on the slide
    local, prad, pkind = {}, {}, {}
    for pl, bs in by_place.items():
        loc = pack([(b, rad[b]) for b in bs], (0, 0), [], pad=2.5)
        local[pl] = loc; prad[pl] = max(math.hypot(x, y) + rad[b] for b, (x, y) in loc.items()) + 4
        kinds = collections.Counter()
        for b in bs: kinds["garden" if body[b]["kind_or_side"] == "garden" else "estate" if body[b]["kind_or_side"] == "estate district" else "town"] += len(members[b])
        pkind[pl] = kinds.most_common(1)[0][0]
    ANCH = {"town": (300, 420), "estate": (720, 300), "garden": (790, 545)}
    FIX = {"Colombo": (270, 415), "Peradeniya": (820, 545)}
    centre = pack([(pl, r) for pl, r in prad.items()], lambda pl: FIX.get(pl, ANCH[pkind[pl]]), [], BOUNDS, aspect=1.5, pad=4)

    out, dot, bpos = [], {}, {}
    for pl, (cx, cy) in centre.items():
        big = sum(len(members[b]) for b in by_place[pl]) >= 60
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{prad[pl]:.1f}" fill="var(--neutral)" fill-opacity="0.07" stroke="var(--neutral)" stroke-opacity="{0.45 if big else 0.25}" stroke-width="1"/>')
        for b, (lx, ly) in local[pl].items():
            bx, by = cx + lx, cy + ly; bpos[b] = (bx, by)
            ms = sorted(members[b], key=lambda p: (person[p]["kind_or_side"] != "Ceylonese", person[p]["kind_or_side"]))
            for k, p in enumerate(ms):
                r = S * math.sqrt(k + 0.5); t = k * 2.399963
                dot[(p, b)] = (bx + r * math.cos(t), by + r * math.sin(t))
    # bridges: one person, two or more bodies
    mine = collections.defaultdict(list)
    for (p, b) in dot: mine[p].append(b)
    seg = []
    for p, bs in mine.items():
        if len(bs) < 2: continue
        bs = sorted(bs, key=lambda b: bpos[b])
        for a, c in zip(bs, bs[1:]):
            (x1, y1), (x2, y2) = dot[(p, a)], dot[(p, c)]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1
            seg.append(f"M{x1:.0f} {y1:.0f}Q{mx - dy * 0.12:.0f} {my + dx * 0.12:.0f} {x2:.0f} {y2:.0f}")
    out.append(f'<path d="{"".join(seg)}" fill="none" stroke="var(--title)" stroke-opacity="0.2" stroke-width="0.7"/>')
    for side, colour in COL.items():
        d = "".join(f"M{x - 1.25:.1f} {y:.1f}a1.25 1.25 0 1 0 2.5 0a1.25 1.25 0 1 0 -2.5 0" for (p, b), (x, y) in dot.items() if person[p]["kind_or_side"] == side)
        out.append(f'<path d="{d}" fill="{colour}"/>')

    # place names for the larger places
    LBL = {}                      # place -> (dx, dy, anchor) overrides, filled in after looking at the render
    for pl, (cx, cy) in centre.items():
        n = len({p for b in by_place[pl] for p in members[b]})
        if n < 55 and pl not in LBL: continue
        name = {"Elsewhere on the island": "smaller places", "Dept of Agriculture": "Department of Agriculture", "School of Agriculture Peradeniya": "School of Agriculture",
                "Gardens, unit not printed": "other gardens"}.get(pl, pl)
        dx, dy, anc = LBL.get(pl, (0, -prad[pl] - 6, "middle"))
        out.append(f'<text class="nl" x="{cx + dx:.0f}" y="{cy + dy:.0f}" text-anchor="{anc}">{name}</text>')

    counts = json.load(open(KG / "graph_counts.json"))
    json.dump({"centre": {k: [round(v[0]), round(v[1]), round(prad[k])] for k, v in centre.items()},
               "bodies": {body[b]["name"] + " | " + body[b]["place_or_source"]: [round(x), round(y), round(rad[b]), len(members[b])] for b, (x, y) in bpos.items() if len(members[b]) >= 20}},
              open(HERE / "graph_layout.json", "w"), indent=0, ensure_ascii=False)

    badge_n = [0]
    def badge(x, y, k):
        return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="10" fill="var(--title)" stroke="var(--ground)" stroke-width="2"/>'
                f'<text x="{x:.0f}" y="{y + 4.5:.0f}" text-anchor="middle" style="font-size:13px;font-weight:700;fill:var(--ground)">{k}</text>')
    def note(x, y, tx, ty, lines, anchor="start"):
        """A numbered marker in the drawing and the same number beside a short note in the column."""
        badge_n[0] += 1; k = badge_n[0]
        o = [badge(x, y, k), badge(tx + 10, ty - 5, k)]
        for j, l in enumerate(lines): o.append(f'<text class="{"nl" if j == 0 else "yr"}" x="{tx + 28}" y="{ty + 19 * j}">{l}</text>')
        return o
    def at(name, place=None):
        for b, (x, y) in bpos.items():
            if body[b]["name"].startswith(name) and (place is None or body[b]["place_or_source"] == place): return x, y, rad[b], len(members[b])
        raise SystemExit("no body " + name)
    X = 992
    def to(name, place, ty, lines):
        x, y, r, n = at(name, place); return note(x + r * 0.75, y - r * 0.75, X, ty, lines)
    cx, cy = centre["Colombo"]
    NOTES = [note(cx + prad["Colombo"] * 0.72, cy - prad["Colombo"] * 0.66, X, 196, ["Colombo", "about 730 people in 195 societies,", "firms, courts, papers and offices"]),
             to("Low-Country Products Association", "Colombo", 274, ["Low-Country Products Association", "43 officers, all but one Ceylonese"]),
             to("Cacao Dealers", "Kandy", 333, ["Cacao dealers, Kandy", "45 names, nearly all Ceylonese"]),
             to("Dimbula estates", None, 392, ["Planting districts", "estate owners, agents and", "managers, 1890 and 1920"]),
             to("Peradeniya", "Peradeniya", 470, ["The botanic gardens", "directors, clerks and gardeners", "named in The Tropical Agriculturist"])]
    NOTES.append([f'<path d="M{X} 560H1236" stroke="var(--neutral)" stroke-width="1"/>', f'<text class="nl" x="{X}" y="586">Next</text>', f'<text class="yr" x="{X}" y="605">merge the same person across</text>', f'<text class="yr" x="{X}" y="624">sources, then meet the 1,150 or so</text>',
                  f'<text class="yr" x="{X}" y="643">Ceylonese already in Wikidata</text>'])
    ppl, bod, plc, br = counts["people"], counts["bodies"], counts["places"], counts["people_in_two_or_more_bodies"]
    for n in NOTES: out += n
    key = (f'<g transform="translate(96 158)"><circle cx="6" cy="0" r="5" fill="var(--coconut)"/><text class="yr" x="18" y="5">Ceylonese</text>'
           f'<circle cx="118" cy="0" r="5" fill="var(--career)"/><text class="yr" x="130" y="5">British or European</text>'
           f'<path d="M300 0h26" stroke="var(--title)" stroke-opacity="0.5"/><text class="yr" x="334" y="5">the same person in two institutions (about {round(br, -1)} so far)</text></g>')
    aria = (f"A network drawing. About {round(ppl, -2):,} dots, each a person, sit in about {round(bod, -1)} small discs, each an institution such as a society, firm, court, newspaper, "
            f"estate district or garden. The discs are grouped into about {round(plc, -1)} places, the largest Colombo. Fine lines join the dots of about {round(br, -1)} people found in two or more bodies.")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Going forward: the graph build</title>
<!-- Written by build_graph_slide.py; edit that file, not this one. Add ?dark for the dark version. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>
<section class="slide" id="g1">
  <p class="label">{SECTION}</p>
  <h2>TITLE</h2>
  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">
{key}
{chr(10).join(out)}
  </svg>
  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{"".join(f'<circle cx="{6 + 36 * k}" cy="10" r="{6 if k == SEC else 4}" fill="var(--{"accent" if k == SEC else "neutral"})"/>' for k in range(6))}<text x="204" y="15">{SECTION}</text></svg>
</section>
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');</script>
</body>
</html>
""".replace("TITLE", "Two days of reading, drawn as a graph")
    (HERE / "slides_graph.html").write_text(html, encoding="utf-8")
    print("wrote slides_graph.html |", ppl, "people", bod, "bodies", plc, "places", br, "bridges", len(seg), "bridge lines")


if __name__ == "__main__":
    main()
