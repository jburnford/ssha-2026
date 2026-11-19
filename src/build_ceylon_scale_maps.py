"""Two still maps of the same Ceylon careers: inside the island, and across the empire.

Reads the Ceylon graph tables (officials from the Colonial Office List biographies and their postings):
  sri_lanka_history/spine/graph/postings.tsv.gz, places.tsv.gz
Writes images/ceylon_local.png and images/ceylon_global.png (dark map ground, like the atlas and the videos),
and ceylon_scale_counts.tsv with the counts behind the slides.

Circles are sized by postings (local) or by officials (global). Lines on the global map join Ceylon to each
other place its officials also served in; they are connections, not routes.
"""
import csv, gzip, json, collections
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
G = Path("/home/jic823/ceylon/sri_lanka_history/spine/graph")
CEY, UK = "wd:Q918153", "wd:Q84"


def tsv(p):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


places = {r["id"]: r for r in tsv(G / "places.tsv.gz")}
post = collections.defaultdict(list)
for r in tsv(G / "postings.tsv.gz"):
    post[r["person"]].append(r)

local = collections.Counter(); abroad = collections.Counter(); lab = {}
stay = move = cey_postings = 0
for p, rs in post.items():
    cols = {r["colony"] for r in rs if r["colony"]}
    if CEY not in cols: continue
    other = cols - {CEY, UK}
    if other: move += 1
    else: stay += 1
    for c in other:
        abroad[c] += 1; lab[c] = next(r["colony_label"] for r in rs if r["colony"] == c)
    for r in rs:
        if r["colony"] == CEY:
            cey_postings += 1
            if r["place"] and r["place"] != CEY:
                local[r["place"]] += 1; lab[r["place"]] = r["place_label"]


def pts(counter):
    out = []
    for i, n in counter.most_common():
        pl = places.get(i, {})
        if pl.get("lat") and pl.get("lon"):
            out.append({"label": lab[i], "n": n, "lat": float(pl["lat"]), "lon": float(pl["lon"])})
    return out


L, A = pts(local), pts(abroad)
cey = places[CEY]
with open(HERE / "ceylon_scale_counts.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["measure", "value"])
    for k, v in [("officials with a Ceylon posting (biographies)", stay + move), ("served only in Ceylon (or Ceylon and the United Kingdom)", stay),
                 ("also served in another colony or territory", move), ("Ceylon postings", cey_postings),
                 ("Ceylon postings naming a place inside the island", sum(local.values())), ("places inside the island", len(local)),
                 ("places inside the island with a coordinate", len(L)), ("other places served", len(abroad)), ("other places with a coordinate", len(A))]:
        w.writerow([k, v])
    w.writerow([]); w.writerow(["kind", "place", "count"])
    for d in L: w.writerow(["inside Ceylon (postings)", d["label"], d["n"]])
    for d in A: w.writerow(["beyond Ceylon (officials)", d["label"], d["n"]])

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body{margin:0;background:#15161a}#map{width:%(w)spx;height:%(h)spx;background:#15161a}
.leaflet-control-attribution{display:none}
@font-face{font-family:'Atkinson Next';src:url('fonts/AtkinsonHyperlegibleNext-Bold.woff') format('woff');font-weight:700}
.lb{font:700 %(fs)spx 'Atkinson Next',Arial,sans-serif;color:#E8DFCB;white-space:nowrap;text-shadow:0 0 4px #15161a,0 0 4px #15161a,0 0 6px #15161a}
</style></head><body><div id="map"></div><script>
const D=%(data)s, MODE=%(mode)s, CEY=%(cey)s;
const map=L.map('map',{zoomControl:false,attributionControl:false,zoomSnap:0});
const tiles=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',{maxZoom:10}).addTo(map);
window.loaded=false; tiles.on('load',()=>{window.loaded=true;});
const BLUE='#6699D3';
if(MODE==='local'){
  map.setView([7.86,80.72],8);
  const mx=Math.max(...D.map(d=>d.n));
  D.forEach(d=>L.circleMarker([d.lat,d.lon],{radius:4+22*Math.sqrt(d.n/mx),color:'#E8DFCB',weight:1,fillColor:BLUE,fillOpacity:.72}).addTo(map));
  D.filter(d=>!/Province/.test(d.label)).filter(d=>d.label!=='Kegalle').slice(0,8).forEach(d=>L.marker([d.lat,d.lon],{icon:L.divIcon({className:'lb',html:d.label,iconAnchor:[-(8+22*Math.sqrt(d.n/mx)),9]})}).addTo(map));
}else{
  map.setView([10,22],2);
  const mx=Math.max(...D.map(d=>d.n));
  function arc(a,b){const pts=[],n=40;const mid=[(a[0]+b[0])/2+Math.abs(a[1]-b[1])*0.12,(a[1]+b[1])/2];
    for(let i=0;i<=n;i++){const t=i/n;pts.push([(1-t)*(1-t)*a[0]+2*(1-t)*t*mid[0]+t*t*b[0],(1-t)*(1-t)*a[1]+2*(1-t)*t*mid[1]+t*t*b[1]]);}return pts;}
  D.forEach(d=>L.polyline(arc(CEY,[d.lat,d.lon]),{color:BLUE,weight:0.6+3.2*d.n/mx,opacity:.55}).addTo(map));
  D.forEach(d=>L.circleMarker([d.lat,d.lon],{radius:2.5+9*Math.sqrt(d.n/mx),color:'#E8DFCB',weight:1,fillColor:BLUE,fillOpacity:.85}).addTo(map));
  L.circleMarker(CEY,{radius:9,color:'#15161a',weight:2,fillColor:'#E8DFCB',fillOpacity:1}).addTo(map);
  L.marker(CEY,{icon:L.divIcon({className:'lb',html:'Ceylon',iconAnchor:[-13,9]})}).addTo(map);
}
</script></body></html>"""

(HERE / "images").mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for mode, data, w, h in (("local", L, 520, 740), ("global", A, 840, 600)):
        html = HERE / f"_map_{mode}.html"
        html.write_text(PAGE % {"w": w, "h": h, "data": json.dumps(data), "mode": json.dumps(mode), "fs": 21 if mode == "local" else 16,
                                "cey": json.dumps([float(cey["lat"]), float(cey["lon"])])}, encoding="utf-8")
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.goto(html.as_uri()); pg.wait_for_function("window.loaded===true", timeout=60000); pg.wait_for_timeout(1500)
        out = HERE / "images" / f"ceylon_{mode}.png"; pg.screenshot(path=str(out)); print("wrote", out)
        html.unlink()
    b.close()
print("stayed", stay, "moved", move, "| local places", len(local), "mapped", len(L), "| other places", len(abroad), "mapped", len(A))
