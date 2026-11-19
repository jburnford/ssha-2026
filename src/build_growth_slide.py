"""Write slides_growth.html: one slide (n1) that builds, source by source, the people and institutions now held for Ceylon.

Seven stages along a line: the Colonial Office List biographies, The Tropical Agriculturist, the Blue Books, Ferguson's
Directory, Wikidata, and two rounds of reading the wider library (2,385 volumes) from seeds: first Wikidata people, then
people who stand in two or more of our own sources. Each dot is 100 names as extracted; the same
person or body can appear under several sources until they are merged, so the totals are names, not individuals.
The journal is counted only where a name stands in two or more articles (about three-quarters of its name strings
stand in one article only, and include spelling variants and bodies outside Ceylon). Counts are rounded and come from: spine/graph/_counts.json and names.tsv.gz (journal), bluebook/extracted (Blue Books),
../kg_build/dir_counts.json (directory), ../wikidata_people_scope (Wikidata), ../kg_build/seeded_combined.json (scripts/seeded_combine.py).
In the deck the stages play one after another (anim.js playStages); r replays.

    python3 build_growth_slide.py && python3 render_slides.py slides_growth.html [--dark] && python3 build_deck.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KG = HERE.parent / "kg_build"
SECTION, SEC = "Going forward", 5
d = json.load(open(KG / "dir_counts.json")); s = json.load(open(KG / "seeded_combined.json"))["rounds"]
r100 = lambda n: int(round(n, -2))
# (station, sub-label, people, bodies, colour, what the bodies are)
STAGES = [("Colonial Office List", "biographies", 1100, 100, "var(--career)", "offices and departments"),
          ("Tropical Agriculturist", "the journal", 10500, 11500, "var(--tea)", "firms, societies and estates"),
          ("Blue Books", "staff lists", 40100, 700, "var(--rice)", "departments"),
          ("Ferguson’s Directory", "1920–21, one volume", r100(d["people"]), r100(d["bodies"]), "var(--coconut)", "firms, societies, councils, clubs"),
          ("Wikidata", "people of the island", 2000, 0, "var(--rubber)", ""),
          ("Library, round 1", "Wikidata seeds", r100(s["seeded"]["new_candidates"]["person"]), r100(s["seeded"]["new_candidates"]["organisation"]), "var(--bark)", "organisations not in the graph"),
          ("Library, round 2", "our own seeds", r100(s["seeded2"]["new_candidates"]["person"]), r100(s["seeded2"]["new_candidates"]["organisation"]), "var(--iol)", "more, from seeds in two of our sources")]
UNIT = 100
# The last beat: what the few new bodies from the wider library are. Each was found beside a person Wikidata already
# knows (kg_build/seeded/seed_edges.tsv); the year is the volume it was found in, not the year it was founded.
FOUND = [("1898", "Maha Bodhi Society", "Anagarika Dharmapala,", "secretary", 1),
         ("1905", "Ceylon Social Reform Society", "Ananda Coomaraswamy,", "president", 1),
         ("1905", "Buddhist Young Men’s Association", "G. F. Perera, railway clerk,", "secretary", 2),
         ("1907", "Railway Benefit Association", "R. A. Reyhardt, railway clerk,", "committee", 2),
         ("1909", "Colombo Malay Club", "M. L. Warish, railway clerk,", "committee", 2),
         ("1922", "Young Lanka League", "Victor Corea,", "president", 1),
         ("1922", "Government Clerks’ Benefit Association", "P. F. de Livera, Treasury clerk,", "committee", 2),
         ("1944", "Ceylon Labour Party", "A. E. Goonesinha,", "chairman", 1)]
ROUND = {1: "var(--bark)", 2: "var(--iol)"}       # round 1 beside a Wikidata person, round 2 beside a person from two of our own sources
PITCH, RDOT = 12.5, 4.6
PX, BX, BASE = 96, 740, 634           # left edge of the people field, of the bodies field, and the floor both stand on
PCOLS, BCOLS = 40, 28


def field(x0, cols, counts):
    """Dots stacked from the floor up, row by row, one colour per stage; returns svg and the stage each row tops out at."""
    out, k = [], 0
    for st, n in enumerate(counts):
        dots = round(n / UNIT)
        for j in range(dots):
            col, row = k % cols, k // cols
            out.append(f'<circle class="pile" data-s="{st}" style="animation-delay:{j * 900 // max(dots, 1)}ms" cx="{x0 + col * PITCH + RDOT:.1f}" cy="{BASE - row * PITCH - RDOT:.1f}" r="{RDOT}" fill="{STAGES[st][4]}"/>')
            k += 1
    return out


def main():
    out = []
    X0, X1, Y = 160, 1130, 214
    step = (X1 - X0) / (len(STAGES) - 1)
    out.append(f'<path class="line" d="M{X0} {Y}H{X1}" stroke="var(--neutral)"/>')
    pt = bt = 0
    for i, (name, sub, p, b, colour, what) in enumerate(STAGES):
        x = X0 + i * step; pt += p; bt += b
        anc, tx = "middle", x
        out.append(f'<g data-s="{i}"><path d="M{X0 + (i - 1) * step if i else x} {Y}H{x}" stroke="{colour}" stroke-width="8" stroke-linecap="round"/>'
                   f'<circle class="st" cx="{x:.0f}" cy="{Y}" r="9" style="stroke:{colour}"/>'
                   f'<text class="stn" x="{tx:.0f}" y="{Y - 22}" text-anchor="{anc}" style="font-size:16px">{name}</text>'
                   f'<text class="yr" x="{tx:.0f}" y="{Y + 30}" text-anchor="{anc}">{sub}</text></g>')
        # running totals and what this stage added: one set per stage, only the current one shown
        add_b = f"+{b:,} {what}" if b else "identifiers, not new institutions"
        out.append(f'<g data-only="{i}"><text class="big" x="{PX}" y="296">about {r100(pt):,}</text><text class="ln" x="{PX + 262}" y="296" fill="var(--second)">names of people</text>'
                   f'<text class="yr" x="{PX}" y="320" style="fill:{colour};font-weight:700">+{p:,} from {name.replace("Library, round", "the library, round")}</text>'
                   f'<text class="big" x="{BX}" y="296">about {r100(bt):,}</text><text class="ln" x="{BX + 262}" y="296" fill="var(--second)">names of institutions</text>'
                   f'<text class="yr" x="{BX}" y="320" style="fill:{colour};font-weight:700">{add_b}</text></g>')
    out += field(PX, PCOLS, [st[2] for st in STAGES]) + field(BX, BCOLS, [st[3] for st in STAGES])
    out.append(f'<path d="M{PX} {BASE + 5}H{PX + PCOLS * PITCH}M{BX} {BASE + 5}H{BX + BCOLS * PITCH}" stroke="var(--neutral)" stroke-width="1.5"/>')
    last = len(STAGES)                                    # one more beat after the six sources
    halo = 'style="paint-order:stroke;stroke:var(--ground);stroke-width:5px;stroke-linejoin:round'
    g = [f'<g data-s="{last}">', f'<path class="line" d="M120 492H1150" stroke="var(--neutral)"/>']
    for k, (yr, body, who, role, rnd) in enumerate(FOUND):
        x = 150 + k * (1120 - 150) / (len(FOUND) - 1); up = k % 2 == 0
        g.append(f'<circle class="st" cx="{x:.0f}" cy="492" r="8" style="stroke:{ROUND[rnd]}"/>')
        w = body.split(" "); cut = (len(w) + 1) // 2 if len(w) < 5 else 3
        rows = [(" ".join(w[:cut]), "stn"), (" ".join(w[cut:]), "stn"), (who, "yr"), (f"{role}, {yr}", "yr")]      # the body, then the person, kept together
        yy = 492 - 92 if up else 492 + 38
        for text, cls in rows:
            g.append(f'<text class="{cls}" x="{x:.0f}" y="{yy}" text-anchor="middle" {halo}{";font-size:16px" if cls == "stn" else ""}">{text}</text>'); yy += 20
    g.append('</g>'); out += g
    out.append(f'<g data-only="{last}"><text class="big" x="{PX}" y="296">Few, but central</text>'
               f'<text class="yr" x="{PX}" y="320" style="font-weight:700"><tspan fill="var(--bark)">found beside a person Wikidata already knows</tspan>'
               f'<tspan fill="var(--second)">  ·  </tspan><tspan fill="var(--iol)">found beside a clerk or official from two of our own sources</tspan></text></g>')
    out.append(f'<text class="yr" x="{PX}" y="{BASE + 26}">Each dot is 100 names as extracted (journal: names in two or more articles). The same person can stand under several sources until merged.</text>')
    aria = ("A line with seven stations, one for each source added to the Ceylon graph: the Colonial Office List biographies, The Tropical Agriculturist, the Blue Books, "
            "Ferguson's Directory, Wikidata, and two rounds of reading the wider library from seeds. Below, two fields of dots grow as each source is added, one of people's names and one of institutions' names; "
            f"each dot is 100 names. Together they reach about {r100(pt):,} names of people and about {r100(bt):,} names of institutions.")
    dots = "".join(f'<circle cx="{6 + 36 * i}" cy="10" r="{6 if i == SEC else 4}" fill="var(--{"accent" if i == SEC else "neutral"})"/>' for i in range(6))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Going forward: what each source added</title>
<!-- Written by build_growth_slide.py; edit that file, not this one. Add ?dark for the dark version. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>
<section class="slide stages" id="n1">
  <p class="label">{SECTION}</p>
  <h2>Each source adds people and institutions to the base</h2>
  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">
{chr(10).join(out)}
  </svg>
  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{dots}<text x="204" y="15">{SECTION}</text></svg>
</section>
<script>
// still view (and the PNG): every stage shown, with the final totals
document.querySelectorAll('[data-only]').forEach(e => {{ if (+e.dataset.only !== {len(STAGES)}) e.style.display = 'none'; }});
document.getElementById('n1').classList.add('finale');
if (location.search.includes('dark')) document.documentElement.classList.add('dark');
</script>
</body>
</html>
"""
    (HERE / "slides_growth.html").write_text(html, encoding="utf-8")
    print("wrote slides_growth.html | people", pt, "bodies", bt, "|", [(st[0], st[2], st[3]) for st in STAGES])


if __name__ == "__main__":
    main()
