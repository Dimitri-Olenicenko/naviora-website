"""Put building renders first in every gallery; demote floor plans.

The Armconstruct scrape pulled floor plans and exterior renders into the same
folder, and alphabetical order put the plans first. The result was listings —
the Five Towers commercial unit worst of all — whose card image was a
line-drawing of a flat rather than a photograph of the building.

Floor plans are flat line art: mostly near-white with almost no colour
saturation. Renders are photographic and saturated. Measuring both separates
them cleanly on this set (plans: 47-81% white, saturation under 13; renders:
0-9% white, saturation 18-44), so classification is by measurement rather
than by filename.

Plans are kept, just moved to the end — they are useful further down a
gallery, only wrong as the headline image.

Idempotent: sorting an already-sorted list changes nothing.
"""
import json
import os
import statistics

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WHITE_MIN = 0.34      # a plan's page is mostly blank
SAT_MAX = 26          # ...and carries very little colour


def looks_like_plan(path):
    try:
        im = Image.open(path).convert("RGB").resize((160, 160))
    except Exception:
        return False
    px = list(im.getdata())
    white = sum(1 for r, g, b in px if r > 228 and g > 222 and b > 210) / len(px)
    sat = statistics.mean(max(r, g, b) - min(r, g, b) for r, g, b in px)
    return white > WHITE_MIN and sat < SAT_MAX


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))

    changed = 0
    for x in listings:
        imgs = x.get("images") or []
        if len(imgs) < 2:
            continue

        renders, plans = [], []
        for u in imgs:
            local = os.path.join(ROOT, u.lstrip("/").replace("naviora-website/", "", 1))
            (plans if os.path.exists(local) and looks_like_plan(local)
             else renders).append(u)

        # If everything scored as a plan, the heuristic is not helping here —
        # leave the original order rather than shuffling blind.
        if not renders:
            continue

        new = renders + plans
        if new != imgs:
            x["images"] = new
            changed += 1
            print(f"  {x['slug']:34} {len(renders)} renders first, "
                  f"{len(plans)} plans moved down")

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\nlistings reordered: {changed}")


if __name__ == "__main__":
    main()
