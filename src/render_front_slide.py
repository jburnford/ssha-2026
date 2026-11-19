"""Render front_slide.html to PNG at 1280 x 720 (light and dark), at twice the pixel density."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch()
    for mode in ("light", "dark"):
        pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
        pg.goto((HERE / "front_slide.html").as_uri() + ("?dark" if mode == "dark" else ""))
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        out = HERE / f"front_slide_{mode}.png"
        pg.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 1280, "height": 720})
        print("wrote", out)
    b.close()
