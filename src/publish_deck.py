"""Copy the built deck and only the files it needs into a folder that GitHub Pages can serve.

    python3 build_deck.py && python3 publish_deck.py [/home/jic823/ssha-2026]

Writes SITE/docs/index.html (the deck, with the video paths pointed at docs/videos/), docs/fonts, docs/images (only the
images the deck uses), docs/videos, and SITE/src (the slide files, style, script and generators, for the record).
PLAN.md, the PNG renders and all extraction data stay out. Commit and push the SITE folder afterwards.
"""
import re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/jic823/ssha-2026")
docs = SITE / "docs"
for d in ("fonts", "images", "videos"): (docs / d).mkdir(parents=True, exist_ok=True)
html = (HERE / "deck.html").read_text(encoding="utf-8")
for ref in sorted(set(re.findall(r'(?:src|poster)="(\.\./(?:career_video|trade_video)/[^"]+)"', html))):
    shutil.copy2(HERE / ref, docs / "videos" / Path(ref).name); html = html.replace(ref, "videos/" + Path(ref).name)
for ref in sorted(set(re.findall(r'(?:src|poster)="(images/[^"]+)"', html))): shutil.copy2(HERE / ref, docs / ref)
for ref in sorted(set(re.findall(r'url\("(fonts/[^"]+)"\)', html))): shutil.copy2(HERE / ref, docs / ref)
left = re.findall(r'(?:src|poster|href)="(\.\./[^"]+)"', html)
assert not left, left
(docs / "index.html").write_text(html.replace("(draft deck)", "(SSHA 2026)"), encoding="utf-8")
(docs / ".nojekyll").write_text("")
src = SITE / "src"; src.mkdir(exist_ok=True)
for f in sorted(HERE.glob("*.py")) + sorted(HERE.glob("slides*.html")) + sorted(HERE.glob("*.css")) + sorted(HERE.glob("*.js")) + [HERE / "front_slide.html", HERE / "botanist_network.inc.svg"]:
    if f.name not in ("build_graph_slide_v1.py",): shutil.copy2(f, src / f.name)
print("site at", docs, "|", sum(p.stat().st_size for p in docs.rglob("*") if p.is_file()) // 1024, "KB |", len(list(docs.rglob("*"))), "files")
