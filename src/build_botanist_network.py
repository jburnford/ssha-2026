"""Lay out the network around Henry Trimen and Daniel Morris in The Tropical Agriculturist.

Nodes: the two botanists; every article that names either (small dots); the people most often named in the
same articles; the places and commodities most often named in them. An edge joins an article to each of those
it names. Everything comes from the Ceylon graph's journal index (sri_lanka_history/spine/graph), which was made
by an earlier entity-extraction run and is not checked article by article.

Writes botanist_network.inc.svg (a fragment the people slides include) and botanist_network_counts.tsv.
Rerun build_people_slides.py afterwards.
"""
import csv, gzip, collections, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
G_DIR = Path("/home/jic823/ceylon/sri_lanka_history/spine/graph")
TRIMEN, MORRIS = "TAP-P-000001", "TAP-P-000002"
N_PEOPLE, N_PLACES = 22, 16
SKIP_PEOPLE = {"Carl Linnaeus", "J. D. Hooker"}             # a naming authority; a second profile of Joseph Hooker
SKIP_PLACES = {"ceylon", "india", "england", "europe", "america", "south america", "australia", "china", "southern india",
               "united states", "africa", "asia", "east", "west", "great britain", "britain", "tropics"}
COMMODITY = {"coffee": "coffee", "tea": "tea", "cacao": "cacao", "cocoa": "cacao", "chocolate": "cacao", "rubber": "rubber",
             "indiarubber": "rubber", "india rubber": "rubber", "caoutchouc": "rubber", "para rubber": "rubber", "cinchona": "cinchona",
             "cinchona bark": "cinchona", "quinine": "quinine", "sugar": "sugar", "tobacco": "tobacco", "cotton": "cotton",
             "cinnamon": "cinnamon", "cardamoms": "cardamoms", "coconut": "coconut", "coconuts": "coconut"}


def tsv(name):
    csv.field_size_limit(10**9)
    with gzip.open(G_DIR / name, "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    prof = {r["id"]: r for r in tsv("profiles.tsv.gz")}
    pm = tsv("profile_mentions.tsv.gz")
    arts = {TRIMEN: set(), MORRIS: set()}
    for r in pm:
        if r["profile"] in arts: arts[r["profile"]].add(r["article"])
    all_a = arts[TRIMEN] | arts[MORRIS]
    by_person = collections.defaultdict(set)
    for r in pm:
        if r["article"] in all_a and r["profile"] not in arts and prof[r["profile"]]["name"] not in SKIP_PEOPLE:
            by_person[r["profile"]].add(r["article"])
    people = sorted(by_person, key=lambda p: -len(by_person[p]))[:N_PEOPLE]
    label = {(r["type"], r["key"]): r["label"] for r in tsv("names.tsv.gz")}
    by_place, by_com = collections.defaultdict(set), collections.defaultdict(set)
    for r in tsv("mentions.tsv.gz"):
        if r["article"] not in all_a: continue
        k = r["key"].lower()
        if r["type"] == "PLACE" and k not in SKIP_PLACES: by_place[r["key"]].add(r["article"])
        elif r["type"] == "COMMODITY" and k in COMMODITY: by_com[COMMODITY[k]].add(r["article"])
    places = sorted(by_place, key=lambda p: -len(by_place[p]))[:N_PLACES]

    # Layout, by hand so that it reads: each botanist's articles form a disc (earliest at the centre), the articles
    # naming both sit in a small disc between them, and the people, commodities and places stand in three columns.
    def year(a):
        y = a.split("#")[1][:4] if "#" in a else ""
        return int(y) if y.isdigit() else 9999
    def disc(items, cx, cy, radius):
        items = sorted(items, key=lambda a: (year(a), a)); out_ = {}
        for k, a in enumerate(items):
            r = radius * math.sqrt((k + 0.5) / len(items)); t = k * 2.399963
            out_[a] = (cx + r * math.cos(t), cy + r * math.sin(t))
        return out_
    CT, CM, CB = (190, 372, 148), (1100, 372, 124), (640, 598, 24)
    both = arts[TRIMEN] & arts[MORRIS]
    P = {}
    P.update(disc(arts[TRIMEN] - both, *CT)); P.update(disc(arts[MORRIS] - both, *CM)); P.update(disc(both, *CB))
    P[TRIMEN], P[MORRIS] = CT[:2], CM[:2]
    def column(names, sets, kind, x, top, step):
        order = sorted(names, key=lambda n: -len(sets[n]))
        for k, n in enumerate(order): P[(kind, n)] = (x, top + k * step)
        return order
    people = column(people, by_person, "person", 420, 186, 17.4)
    coms = column(list(by_com), by_com, "commodity", 640, 186, 30)
    places = column(places, by_place, "place", 800, 186, 24)

    out = []
    # every element carries the year it first appears (data-y), so the slide can be played year by year (anim.js)
    last = max(year(a) for a in all_a if year(a) != 9999)
    MONTHLY_TO = 1884                                    # month by month while the network forms, then year by year
    def yr(a):
        """When an article appears, as YYYYMM. After MONTHLY_TO every article of a year appears together (month 12)."""
        y = min(year(a), last); part = a.split("#")[1] if "#" in a else ""
        m = int(part[5:7]) if y <= MONTHLY_TO and len(part) >= 7 and part[5:7].isdigit() else 12
        return y * 100 + m
    seg = collections.defaultdict(list)
    for kind, names, sets in (("person", people, by_person), ("commodity", coms, by_com), ("place", places, by_place)):
        for n in names:
            for a in sets[n]: seg[(kind, yr(a))].append(f"M{P[a][0]:.0f} {P[a][1]:.0f}L{P[(kind, n)][0]:.0f} {P[(kind, n)][1]:.0f}")
    for a in both:
        for b in (TRIMEN, MORRIS): seg[("bot", yr(a))].append(f"M{P[a][0]:.0f} {P[a][1]:.0f}L{P[b][0]:.0f} {P[b][1]:.0f}")
    for kind in ("bot", "place", "commodity", "person"):
        for (k, y), d in sorted(seg.items()):
            if k == kind: out.append(f'<path class="ne ne-{kind}" data-y="{y}" d="{"".join(d)}"/>')
    for a in all_a:
        cls = "both" if a in both else "one"
        out.append(f'<circle class="na na-{cls}" data-y="{yr(a)}" cx="{P[a][0]:.1f}" cy="{P[a][1]:.1f}" r="{2.2 if cls == "both" else 1.9}"/>')

    def node(n, kind, text, aset):
        x, y = P[n]; r = 2.5 + 0.42 * math.sqrt(len(aset))
        per_year = collections.Counter(yr(a) for a in aset); run, cum = 0, []
        for yy in sorted(per_year):
            run += per_year[yy]; cum.append(f"{yy}:{run}")
        return (f'<circle class="nn nn-{kind}" data-c="{",".join(cum)}" data-r="{r:.1f}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>'
                f'<text class="nl" data-y="{min(per_year)}" x="{x + 13:.0f}" y="{y + 4.5:.0f}">{text}</text>')

    for p in people: out.append(node(("person", p), "person", prof[p]["name"], by_person[p]))
    for c in coms: out.append(node(("commodity", c), "commodity", c, by_com[c]))
    for p in places: out.append(node(("place", p), "place", label.get(("PLACE", p), p), by_place[p]))
    first = min(year(a) for a in all_a)
    out.append(f'<text class="clock" data-all="{first}–{last}" x="1184" y="118" text-anchor="end">{first}–{last}</text>')
    for n, name, (cx, cy, rad), cnt in ((TRIMEN, "Henry Trimen", CT, len(arts[TRIMEN])), (MORRIS, "Daniel Morris", CM, len(arts[MORRIS]))):
        out.append(f'<circle class="nn nn-bot" cx="{cx}" cy="{cy}" r="11"/>')
        out.append(f'<text class="nl nl-big" x="{cx}" y="{cy - rad - 30}" text-anchor="middle">{name}</text>')
        out.append(f'<text class="yr" x="{cx}" y="{cy - rad - 10}" text-anchor="middle">named in about {round(cnt, -1)} articles</text>')
    out.append(f'<text class="yr" x="{CB[0] + CB[2] + 12}" y="{CB[1] + 5}">{len(both)} name both</text>')
    for x, head in ((420, "people"), (640, "commodities"), (800, "places")):
        out.append(f'<text class="ln" x="{x - 6}" y="160" fill="var(--second)">{head}</text>')
    (HERE / "botanist_network.inc.svg").write_text("\n".join(out), encoding="utf-8")

    with open(HERE / "botanist_network_counts.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["kind", "name", "articles"])
        w.writerow(["botanist", "Henry Trimen", len(arts[TRIMEN])]); w.writerow(["botanist", "Daniel Morris", len(arts[MORRIS])])
        w.writerow(["articles", "naming both", len(arts[TRIMEN] & arts[MORRIS])]); w.writerow(["articles", "naming either", len(all_a)])
        w.writerow(["people", "named in the same articles (all)", len(by_person)])
        for p in people: w.writerow(["person", prof[p]["name"], len(by_person[p])])
        for p in places: w.writerow(["place", label.get(("PLACE", p), p), len(by_place[p])])
        for c in coms: w.writerow(["commodity", c, len(by_com[c])])
    print("articles", len(all_a), "| both", len(arts[TRIMEN] & arts[MORRIS]), "| people shown", len(people), "of", len(by_person),
          "| places", len(places), "| commodities", len(by_com), "| links drawn", sum(len(v) for v in seg.values()), "| years", first, "to", last)


if __name__ == "__main__":
    main()
