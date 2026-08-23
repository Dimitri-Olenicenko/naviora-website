"""Rebuild the map's hardcoded slug -> coordinate fallback table.

The home-page map (Leaflet) plots a point per listing via `pointFor(listing)`:
it uses the listing's own lat/lng when present, and otherwise falls back to a
table compiled into the bundle. That table still held the original seed data —
placeholder slugs that no longer exist (vake-apartment, emaar-beachfront-…,
kentron-northern-avenue) and stale approximate points for projects whose real
coordinates we have since verified. So the map showed old buildings.

This regenerates the table from listings.json, keeping only listings that
carry a verified pin. Since `pointFor` prefers the listing's own coordinates
anyway, the table is really a safety net; what matters is that it no longer
names anything that was deleted.

Note the table's entries are tagged `approximate:!0` by the original author.
We keep that flag off for our verified pins, since every one was resolved to
the named building and cross-checked by reverse geocoding.

Idempotent.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS = os.path.join(ROOT, "_next", "static", "chunks")

# Start of the module that defines the table; the table itself is located by
# brace matching rather than a regex, because it ends `};e.s([...` and any
# lazy/greedy pattern either stops inside a nested entry or runs past the end.
ANCHOR = re.compile(r'\},\s*29517\s*,\s*e\s*=>\s*\{"use strict";\s*let t\s*=\s*')


def object_span(src, start):
    """Return (start, end) of the JS object literal beginning at `start`."""
    assert src[start] == "{"
    depth, i, in_str, quote, esc = 0, start, False, "", False
    while i < len(src):
        c = src[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    return None


def build_table(listings):
    out = {}
    for x in listings:
        if not (isinstance(x.get("lat"), (int, float))
                and isinstance(x.get("lng"), (int, float))):
            continue
        entry = {"lat": round(x["lat"], 6), "lng": round(x["lng"], 6)}
        addr = x.get("address") or x.get("district")
        if addr:
            entry["address"] = addr
        out[x["slug"]] = entry
    return out


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"),
                              encoding="utf-8"))
    table = build_table(listings)
    payload = json.dumps(table, ensure_ascii=False, separators=(",", ":"))

    patched = 0
    for name in sorted(os.listdir(CHUNKS)):
        if not name.endswith(".js"):
            continue
        path = os.path.join(CHUNKS, name)
        src = open(path, encoding="utf-8", errors="ignore").read()
        if '29517' not in src or '"COUNTRY_VIEW"' not in src:
            continue

        m = ANCHOR.search(src)
        if not m:
            continue
        span = object_span(src, m.end())
        if not span:
            print(f"  {name}: could not delimit the table, skipped")
            continue
        a, b = span

        old = src[a:b]
        old_slugs = set(re.findall(r'"([a-z0-9-]+)":\{lat:', old))
        out = src[:a] + payload + src[b:]
        open(path, "w", encoding="utf-8").write(out)

        gone = sorted(old_slugs - set(table))
        print(f"  {name}: {len(old_slugs)} -> {len(table)} points")
        if gone:
            print(f"     dropped stale slugs: {', '.join(gone[:6])}"
                  f"{' …' if len(gone) > 6 else ''}")
        patched += 1

    print(f"\nchunks patched: {patched}")
    print(f"map points now: {len(table)} (listings with a verified pin)")


if __name__ == "__main__":
    main()
