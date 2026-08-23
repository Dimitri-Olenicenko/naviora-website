"""Replace Unsplash stock photo URLs baked into exported pages.

Some pages Next.js exported carry their listing data inside the hydration
payload, with the old stock-photo URLs embedded. The homepage and grids read
the seed chunk (patched separately), but these pages carry their own copy.

Editing the payload's *structure* breaks hydration — that mistake produced a
"This page couldn't load" error earlier in this project. Substituting one URL
string for another of the same shape does not: the JSON stays valid, the
array keeps its length, and React sees exactly the object it expects.

Each stock URL is replaced with a real image of the same listing, matched by
slug. Pages whose listing has no real images are left untouched rather than
pointed at a broken path.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COUNTRIES = ("dubai", "abudhabi", "armenia", "georgia")
STOCK = re.compile(r"https://images\.unsplash\.com/[^\"'\\ ]+")


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"),
                              encoding="utf-8"))
    by_slug = {x["slug"]: x for x in listings}

    patched = skipped = 0
    for country in COUNTRIES:
        for purpose in ("residential", "commercial"):
            base = os.path.join(ROOT, country, purpose)
            if not os.path.isdir(base):
                continue
            for name in os.listdir(base):
                path = os.path.join(base, name, "index.html")
                if not os.path.isfile(path):
                    continue

                html = open(path, encoding="utf-8", errors="replace").read()
                hits = STOCK.findall(html)
                if not hits:
                    continue

                real = (by_slug.get(name) or {}).get("images") or []
                if not real:
                    skipped += 1
                    print(f"  skip {country}/{purpose}/{name} "
                          f"({len(set(hits))} stock, no real images to use)")
                    continue

                # Map each distinct stock URL onto a real one, cycling if the
                # page references more images than the listing has.
                order = list(dict.fromkeys(hits))
                mapping = {u: real[i % len(real)] for i, u in enumerate(order)}
                for old, new in mapping.items():
                    html = html.replace(old, new)

                open(path, "w", encoding="utf-8").write(html)
                patched += 1
                print(f"  {country}/{purpose}/{name}: "
                      f"{len(order)} stock -> real images")

    # Grid pages carry the same payload for every card they list.
    for country in COUNTRIES:
        for purpose in ("residential", "commercial"):
            path = os.path.join(ROOT, country, purpose, "index.html")
            if not os.path.isfile(path):
                continue
            html = open(path, encoding="utf-8", errors="replace").read()
            hits = STOCK.findall(html)
            if not hits:
                continue
            changed = False
            for old in dict.fromkeys(hits):
                # Find whichever listing on this grid still has real images.
                pool = [x for x in listings
                        if x["country"] == country and x["purpose"] == purpose
                        and x.get("images")]
                if not pool:
                    continue
                html = html.replace(old, pool[0]["images"][0])
                changed = True
            if changed:
                open(path, "w", encoding="utf-8").write(html)
                patched += 1
                print(f"  {country}/{purpose}/ (grid): stock -> real images")

    print(f"\npatched {patched} pages, skipped {skipped}")


if __name__ == "__main__":
    main()
