"""Render every .slide in a stacked slide file to PNG (light, and dark with --dark), at twice the pixel density.

    python3 render_slides.py slides_02_06.html [--dark]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
src = HERE / (sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "slides_02_06.html")
dark = "--dark" in sys.argv
out = HERE / "png"; out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
    pg.goto(src.as_uri() + ("?dark" if dark else ""))
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(400)
    for el in pg.query_selector_all(".slide"):
        name = out / f"{el.get_attribute('id')}_{'dark' if dark else 'light'}.png"
        el.screenshot(path=str(name)); print("wrote", name)
    b.close()
