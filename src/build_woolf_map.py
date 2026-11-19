"""Still map of Leonard Woolf's postings inside Ceylon, 1905-1911, as recorded in the Colonial Office List.

Places and coordinates come from the Ceylon graph (sri_lanka_history/spine/graph/places.tsv.gz). The List
gives "Cent. Prov." for 1907; it is drawn at Kandy, the province's seat. Writes images/woolf_ceylon.png.
"""
import csv, gzip, json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
G = Path("/home/jic823/ceylon/sri_lanka_history/spine/graph")
STOPS = [("Q215277", "Jaffna", "1905"), ("Q1280127", "Mannar", "1906"), ("Q203197", "Kandy", "1907"), ("Q1025283", "Hambantota", "1908–11")]

with gzip.open(G / "places.tsv.gz", "rt", encoding="utf-8") as f:
    places = {r["qid"]: r for r in csv.DictReader(f, delimiter="\t") if r["qid"]}
pts = []
for q, name, yr in STOPS:
    p = places[q]
    pts.append({"name": name, "yr": yr, "lat": float(p["lat"]), "lon": float(p["lon"])})

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>@font-face{font-family:'Atkinson Next';src:url('fonts/AtkinsonHyperlegibleNext-Bold.woff') format('woff');font-weight:700}
html,body{margin:0;background:#15161a}#map{width:520px;height:740px;background:#15161a}.leaflet-control-attribution{display:none}
.lb{font:700 22px 'Atkinson Next',Arial,sans-serif;color:#E8DFCB;white-space:nowrap;text-shadow:0 0 4px #15161a,0 0 4px #15161a,0 0 6px #15161a}
.lb span{font-weight:700;color:#9FC0EA;font-size:18px}</style></head><body><div id="map"></div><script>
const P=%s;
const map=L.map('map',{zoomControl:false,attributionControl:false,zoomSnap:0}).setView([7.86,81.15],8);
const tiles=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',{maxZoom:10}).addTo(map);
window.loaded=false; tiles.on('load',()=>{window.loaded=true;});
L.polyline(P.map(p=>[p.lat,p.lon]),{color:'#6699D3',weight:7,lineJoin:'round',lineCap:'round'}).addTo(map);
P.forEach(p=>{L.circleMarker([p.lat,p.lon],{radius:10,color:'#E8DFCB',weight:4,fillColor:'#15161a',fillOpacity:1}).addTo(map);
  L.marker([p.lat,p.lon],{icon:L.divIcon({className:'lb',html:p.name+' <span>'+p.yr+'</span>',iconAnchor:[-20,13]})}).addTo(map);});
</script></body></html>"""

(HERE / "images").mkdir(exist_ok=True)
html = HERE / "_map_woolf.html"
html.write_text(PAGE % json.dumps(pts), encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 520, "height": 740}, device_scale_factor=2)
    pg.goto(html.as_uri()); pg.wait_for_function("window.loaded===true", timeout=60000); pg.wait_for_timeout(1500)
    out = HERE / "images" / "woolf_ceylon.png"; pg.screenshot(path=str(out)); print("wrote", out)
    b.close()
html.unlink()
print(pts)
