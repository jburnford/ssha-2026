"""Write slides_closing.html: the last section, methods going forward.

  e1  Building the Ceylonese side of the graph   (one dot per person read from Ferguson's Directory 1920-21, by kind, origin and whether new)
  m0  A seed is more than a name           (what the graph knows of one person, and where that finds him)
  m1  People from both directions          (Wikidata down, the sources up, and where they meet)
  a1  The graph and the reading build each other   (the live atlas: people extracted and placed, and the stages still to come)
  m2  the same message as a loop diagram, held out of the deck   (the loop: seeds, search, an open model checks, hard cases, back to the graph)

Edit this file and rerun; then `python3 render_slides.py slides_closing.html [--dark]` and `python3 build_deck.py`.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTION, SEC = "Going forward", 5


def where():
    dots = "".join(f'<circle cx="{6 + 36 * k}" cy="10" r="{6 if k == SEC else 4}" fill="var(--{"accent" if k == SEC else "neutral"})"/>' for k in range(6))
    return (f'  <svg class="where" width="420" height="20"><path d="M6 10 H186" stroke="var(--neutral)" stroke-width="3"/>{dots}'
            f'<text x="204" y="15">{SECTION}</text></svg>\n')


def slide(sid, title, rows, aria, note):
    body = "\n".join("    " + r for r in rows)
    return (f'<section class="slide" id="{sid}">\n  <p class="label">{SECTION}</p>\n  <h2>{title}</h2>\n'
            f'  <svg class="map" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{aria}">\n{body}\n  </svg>\n'
            f'  <div class="note" style="top:590px"><p>{note}</p></div>\n{where()}</section>\n')


def st(x, y, name, sub="", dy=-22, anchor="middle", dx=0, r=8, sub_dy=22):
    t = f'<circle class="st" cx="{x}" cy="{y}" r="{r}"/><text class="stn" x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{name}</text>'
    if sub: t += f'<text class="yr" x="{x + dx}" y="{y + dy + sub_dy}" text-anchor="{anchor}">{sub}</text>'
    return t


# m0: a seed is more than a name (Charles Alwis Hewavitharana) ------------------------------------------------
ATTR = [(232, "spellings", "Hewavitarne · Hewavitarane · Hewavitarna · Hewavitarana · Hewawitarne"),
        (316, "family", "Don Carolis · Anagarika Dharmapala · Edmund"),
        (400, "roles and years", "physician · committee member · 1909–1929 · detained 1915"),
        (484, "place", "Colombo")]
m0 = []
for y, kind, text in ATTR:
    bend = f"H{620 - abs(y - 358)} L620 358" if y != 358 else "H620"
    m0.append(f'<path class="line" stroke="var(--neutral)" stroke-width="5" d="M110 {y} {bend}"/>')
    m0.append(f'<text class="ln" x="110" y="{y - 34}" fill="var(--second)">{kind}</text><text class="stn" x="110" y="{y - 12}" style="font-size:17px">{text}</text>')
m0 += ['<path class="line" stroke="var(--career)" d="M620 358 L740 238 H980"/>', '<path class="line" stroke="var(--career)" d="M620 358 L660 318 H980"/>',
       '<path class="line" stroke="var(--tea)" d="M620 358 L660 398 H980"/>',
       '<path class="line" stroke="var(--neutral)" stroke-width="5" stroke-dasharray="2 11" d="M620 358 L740 478 H980"/>',
       st(980, 238, "The Tropical Agriculturist", "found, about 47 times", dy=-4, anchor="start", dx=20),
       st(980, 318, "Wikidata", "found, with his family", dy=-4, anchor="start", dx=20),
       st(980, 398, "Ferguson’s Directory", "1920–21: president, manager, director", dy=-4, anchor="start", dx=20),
       '<circle class="st" cx="980" cy="478" r="8" style="stroke:var(--neutral)"/><text class="stn" x="1000" y="474" style="fill:var(--second)">Gazettes</text><text class="yr" x="1000" y="496">next</text>',
       '<circle class="st" cx="620" cy="358" r="16" stroke-width="4"/>',
       '<text class="stn" x="724" y="446" style="font-size:22px">one person</text>']

# e1: building the Ceylonese side of the graph, drawn from the directory sample itself --------------------------
# One dot is one person read from the sampled pages of Ferguson's Ceylon Directory for 1920-21
# (../ner_test/directory_elites.tsv, the Opus agent's close reading). Rows are kinds of people; British and
# European people stack to the left of the centre line and Ceylonese people to the right; colour says whether
# the graph already had them (in the Colonial Office List, in the journal only) or whether they are new.
import csv, collections
KIND = {"government_official": "Officials and councils", "executive_council": "Officials and councils", "legislative_council": "Officials and councils",
        "municipal_or_local_board": "Officials and councils", "jp_magistrate": "Justices of the peace", "headman": "Headmen",
        "lawyer": "Lawyers and doctors", "medical": "Lawyers and doctors", "merchant_or_firm": "Merchants and brokers", "broker": "Merchants and brokers",
        "landed_proprietor": "Merchants and brokers", "newspaper_press": "The press", "association_officer": "Associations",
        "religious": "Religion and schools", "educational": "Religion and schools", "clerk_or_employee": "Clerks and others", "other": "Clerks and others"}
ORDER_K = ["Officials and councils", "Justices of the peace", "Headmen", "Lawyers and doctors", "Merchants and brokers", "The press",
           "Associations", "Religion and schools", "Clerks and others"]
STATUS = [("list", "var(--career)", "already in the Colonial Office List"), ("journal", "var(--tea)", "named in the journal"), ("new", "var(--coconut)", "new to the graph")]
people, seen = collections.defaultdict(list), set()
for r in csv.DictReader(open(HERE.parent / "ner_test" / "directory_elites.tsv", encoding="utf-8"), delimiter="\t"):
    if r["entity_type"] != "person" or not r["volume_tag"].startswith("FergusonsCeylonDirectory1920"): continue
    kind = KIND.get(r["category"]); o = r["origin_judgement"]
    side = "B" if o.startswith("British") else None if o == "unclear" else "C"
    if not kind or not side: continue
    key = (r["group_id"] or r["record_id"], kind)
    if key in seen: continue
    seen.add(key)
    g = r["graph_status"]; status = 0 if g.startswith("col") else 1 if g.startswith("profile") else 2
    people[(kind, side)].append(status)
N_PEOPLE = sum(len(v) for v in people.values())
N_NEW_C = sum(v.count(2) for (k, sd), v in people.items() if sd == "C"); N_C = sum(len(v) for (k, sd), v in people.items() if sd == "C")
CX, ROWS_N, PITCH, RAD, TOP, RH = 680, 6, 6.3, 2.55, 196, 44
e1 = [f'<path d="M{CX} {TOP - 14} V{TOP + RH * len(ORDER_K) - 8}" stroke="var(--rule)" stroke-width="2"/>',
      f'<text class="ln" x="{CX - 16}" y="{TOP - 26}" text-anchor="end" fill="var(--second)">British and European</text>',
      f'<text class="ln" x="{CX + 16}" y="{TOP - 26}" fill="var(--second)">Ceylonese</text>']
for k, kind in enumerate(ORDER_K):
    y0 = TOP + k * RH
    e1.append(f'<text class="stn" x="96" y="{y0 + 23}" style="font-size:17px">{kind}</text>')
    for side, sign in (("B", -1), ("C", 1)):
        for n, status in enumerate(sorted(people[(kind, side)])):
            col, row = divmod(n, ROWS_N)
            e1.append(f'<circle cx="{CX + sign * (12 + col * PITCH):.1f}" cy="{y0 + 3 + row * PITCH:.1f}" r="{RAD}" fill="{STATUS[status][1]}"/>')
ky = TOP + RH * len(ORDER_K) + 16
e1.append('<g class="key">' + "".join(f'<circle cx="{410 + 268 * i}" cy="{ky}" r="6" fill="{c}"/><text x="{424 + 268 * i}" y="{ky + 5}">{t}</text>'
                                      for i, (_, c, t) in enumerate(STATUS)) + '</g>')
print("e1: people drawn", N_PEOPLE, "| Ceylonese", N_C, "of whom new", N_NEW_C,
      "|", {k: (len(people[(k, "B")]), len(people[(k, "C")])) for k in ORDER_K})

# a1: the people added to the atlas, at the extraction stage ----------------------------------------------------
# The picture is the live atlas (jimclifford.ca/sri_lanka_history/#people-place=q35381), captured 18 Nov 2026:
# people named at Colombo in the Blue Book staff lists 1863-1917 and Ferguson's Directory. They are extracted
# and placed, not yet de-duplicated or tied to identifiers, and the slide says so with three stations.
a1 = ['<text class="big" x="864" y="196">about 12,500</text>',
      '<text class="stn" x="864" y="226" style="font-weight:400">records name a person at Colombo alone</text>',
      '<text class="yr" x="864" y="252">Blue Books 1863–1917, Ferguson’s Directory</text>',
      '<path class="line" stroke="var(--career)" d="M876 316 V360"/>',
      '<path class="line" stroke="var(--neutral)" stroke-width="5" stroke-dasharray="2 11" d="M876 360 V636"/>',
      '<circle cx="876" cy="316" r="10" fill="var(--accent)" stroke="var(--ring)" stroke-width="3"/>',
      '<text class="stn" x="902" y="314">Read from the page and placed</text><text class="yr" x="902" y="336">done: this is what the atlas shows</text>',
      '<circle class="st" cx="876" cy="396" r="9" style="stroke:var(--neutral)"/>',
      '<text class="stn" x="902" y="394">One person, not forty records</text><text class="yr" x="902" y="416">next: join the same name across years</text>',
      '<circle class="st" cx="876" cy="476" r="9" style="stroke:var(--neutral)"/>',
      '<text class="stn" x="902" y="474">Tied to an identifier</text><text class="yr" x="902" y="496">next: link to Wikidata, or mint</text>',
      '<circle class="st" cx="876" cy="556" r="9" style="stroke:var(--neutral)"/>',
      '<text class="stn" x="902" y="554">Seeds for the next source</text><text class="yr" x="902" y="576">then: they help read the Gazettes</text>',
      '<circle class="st" cx="876" cy="636" r="9" style="stroke:var(--neutral)"/>',
      '<text class="stn" x="902" y="634">Entities connected to the seeds</text><text class="yr" x="902" y="656">then: other people, institutions and places</text>']
a1x = ('  <img class="atlas" src="images/atlas_people_colombo.png" alt="The Ceylon Historical Atlas showing a relief map around Colombo with a panel headed People named at this place: Colombo, listing 11,316 Blue Book name-and-volume records and 1,147 directory roles, 12,463 records in all">\n')

# m1: both directions ------------------------------------------------------------------------------------------
m1 = ['<path class="line" stroke="var(--career)" d="M110 270 H1150"/>',
      '<path class="line" stroke="var(--career)" d="M540 270 L630 360"/>',
      '<path class="line" stroke="var(--tea)" d="M110 450 H1150"/>',
      '<path class="line" stroke="var(--tea)" d="M540 450 L630 360"/>',
      '<path class="line" stroke="var(--ring)" d="M630 360 H1150"/>',
      '<text class="ln" x="110" y="232" fill="var(--career)">from Wikidata down</text>',
      '<text class="ln" x="110" y="498" fill="var(--tea)">from the sources up</text>',
      st(300, 270, "everyone tied to the island", dy=34),
      st(220, 450, "Directories", dy=-20), st(350, 450, "the journal", dy=-20), st(480, 450, "Gazettes", dy=-20),
      st(1150, 270, "only in Wikidata", "what our sources lack", dy=-44, anchor="end"),
      st(1150, 450, "only in the sources", "new entries to mint", dy=34, anchor="end"),
      st(1150, 360, "in the graph", dy=-20, anchor="end"),
      '<circle class="st" cx="630" cy="360" r="15" stroke-width="4"/>',
      '<text class="stn" x="660" y="342" style="font-size:22px">linked</text>']

# m2: the loop --------------------------------------------------------------------------------------------------
X0, X1, Y0, Y1, R = 300, 1040, 215, 481, 70
YM = (Y0 + Y1) // 2
loop = (f"M{X0 + R} {Y0} H{X1 - R} Q{X1} {Y0} {X1} {Y0 + R} V{Y1 - R} Q{X1} {Y1} {X1 - R} {Y1} H{X0 + R} Q{X0} {Y1} {X0} {Y1 - R} V{Y0 + R} Q{X0} {Y0} {X0 + R} {Y0} Z")
def arrow(x, y, d):                                           # a chevron cut into the line, showing the direction of travel
    pts = {"r": f"{x - 6},{y - 8} {x + 6},{y} {x - 6},{y + 8}", "l": f"{x + 6},{y - 8} {x - 6},{y} {x + 6},{y + 8}"}[d]
    return f'<polyline points="{pts}" fill="none" stroke="var(--ground)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
m2 = [f'<path class="line" stroke="var(--career)" d="{loop}"/>',
      f'<path class="line" stroke="var(--ring)" stroke-width="4" stroke-dasharray="2 10" d="M{X1} {YM} H{840 - (YM - Y0)} L840 {Y0}"/>',
      arrow(670, Y0, "r"), arrow(670, Y1, "l"),
      st(500, Y0, "Seeds", "names, spellings, dates, places", dy=-42),
      st(840, Y0, "Search the raw pages", "a million of them", dy=-42),
      st(X1, YM, "An open model checks", "each match, in context", dy=-4, anchor="start", dx=22),
      st(840, Y1, "Hard cases", "a stronger model, then the historian", dy=32),
      st(500, Y1, "New people, links, events", "each with its evidence", dy=32),
      f'<circle class="st" cx="880" cy="{YM}" r="7"/><text class="stn" x="880" y="{YM + 32}" text-anchor="middle" style="font-size:16px">tighten the rule, rerun</text>',
      f'<circle class="st" cx="{X0}" cy="{YM}" r="16" stroke-width="4"/>',
      f'<text class="stn" x="{X0 - 26}" y="{YM - 4}" text-anchor="end" style="font-size:22px">The graph</text>',
      f'<text class="yr" x="{X0 - 26}" y="{YM + 20}" text-anchor="end">people, places,</text><text class="yr" x="{X0 - 26}" y="{YM + 40}" text-anchor="end">crops, estates</text>']

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Going forward: draft closing slides</title>
<!-- Draft closing slides, each 1280 x 720. Add ?dark for the dark version.
     Written by build_closing_slides.py; edit that file, not this one. -->
<link rel="stylesheet" href="slides.css">
</head>
<body>

""" + slide("a1", "The graph and the text mining build each other", a1,
            "The live atlas beside five stages. The atlas shows a map around Colombo and a panel of people named at that place. About 12,500 records name a person at Colombo alone, from the Blue Books of 1863 to 1917 and Ferguson's Directory. Stage one, read from the page and placed, is done. Stage two, joining the same person across years, stage three, tying each person to an identifier, stage four, using them as seeds to read the next source, and stage five, finding the other people, institutions and places connected to those seeds, come next.",
            "Every source read adds to the graph, and every addition makes the next source easier to read.").replace('style="top:590px"', 'style="top:608px;font-size:21px;width:760px"').replace('<h2>The graph and the text mining build each other</h2>\n', '<h2>The graph and the text mining build each other</h2>\n' + a1x) + "\n" + \
    slide("e1", "Building the Ceylonese side of the graph", e1,
            "A chart in which each dot is one person read from sampled pages of Ferguson's Ceylon Directory for 1920 to 1921. Nine rows are kinds of people: officials and councils, justices of the peace, headmen, lawyers and doctors, merchants and brokers, the press, associations and societies, religion and schools, clerks and others. British and European people stack to the left of a centre line and Ceylonese people to the right. Blue dots were already in the Colonial Office List, green dots were named in the journal, and orange dots are new to the graph. The left side is small and partly blue; the right side is large and almost all orange.",
            f"About {round(N_PEOPLE, -2):,} people read from 26 pages of Ferguson’s Directory, 1920–21. Four in five of the Ceylonese were new to the graph.").replace('style="top:590px"', 'style="top:632px;font-size:20px;width:1120px"') + "\n" + \
    slide("m0", "A seed is more than a name", m0,
            "Charles Alwis Hewavitharana as a seed. Four lines carry what the graph knows of him: five printed spellings of his name; his family, Don Carolis, Anagarika Dharmapala and Edmund; his roles and years, physician, committee member, 1909 to 1929, detained in 1915; and his place, Colombo. They meet at one station, one person, and run on to where he is found: The Tropical Agriculturist, about 47 times; Wikidata, with his family; Ferguson's Directory for 1920 to 1921, as president, manager and director; and, still to come, the Gazettes.",
            "The directory adds what the graph lacked: he leads the Buddhist Theosophical Society, manages two colleges and sits on two company boards.") + "\n" + \
    slide("m1", "People from both directions", m1,
            "Two lines. One comes down from Wikidata: everyone tied to the island. One comes up from the sources: the Directories, the journal, the Gazettes. A branch from each meets at a station marked linked, and runs on into the graph. Each line also runs on alone: people only in Wikidata show what the sources lack, and people only in the sources are new entries to mint.",
            "Where the two meet, a person is linked. What only the sources hold is new to the world’s shared record.") + "\n" + \
    slide("m2", "The graph and the reading build each other", m2,
          "A loop line. From the graph: seeds of names, spellings, dates and places; a search of the raw pages; an open model checks each match in context; hard cases go to a stronger model and then the historian; new people, links and events return to the graph. A dotted line inside runs from the checking back to the search: tighten the rule and rerun.",
          "Every source read adds to the graph, and every addition makes the next source easier to read.") + """
<script>if (location.search.includes('dark')) document.documentElement.classList.add('dark');</script>
</body>
</html>
"""
(HERE / "slides_closing.html").write_text(HTML, encoding="utf-8")
print("wrote", HERE / "slides_closing.html")
