"""Replace the stale seed listings baked into the compiled JS bundle.

The app fetches listings.json at runtime, but it ships a fallback array
compiled into `3idq3it8di6ul.js` — 28 placeholder listings illustrated with
Unsplash stock photos. That fallback is what renders first paint, so the
homepage was showing stock imagery and "3 объекта" counts that no longer
match the real catalogue, before (and sometimes instead of) the fetched data.

The seed lives in a single `a.exports=JSON.parse('[...]')` call, so it can be
swapped for the real catalogue without touching any surrounding code.

Idempotent: re-running rewrites the seed from the current listings.json.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK = os.path.join(ROOT, "_next", "static", "chunks", "3idq3it8di6ul.js")


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"),
                              encoding="utf-8"))
    src = open(CHUNK, encoding="utf-8", errors="ignore").read()
    before = len(src)

    m = re.search(r"a\.exports=JSON\.parse\('", src)
    if not m:
        print("!! seed array not found — chunk layout changed, aborting")
        return

    start = m.end()
    # Walk to the closing quote of the JSON string literal, honouring escapes.
    i, depth, end = start, 0, None
    while i < len(src):
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1

    if end is None:
        print("!! could not find the end of the seed array, aborting")
        return

    old = src[start:end]
    payload = json.dumps(listings, ensure_ascii=False, separators=(",", ":"))
    # The array sits inside a single-quoted JS string literal.
    payload = payload.replace("\\", "\\\\").replace("'", "\\'")

    out = src[:start] + payload + src[end:]
    open(CHUNK, "w", encoding="utf-8").write(out)

    print(f"seed listings: {old.count(chr(34) + 'slug' + chr(34))} -> {len(listings)}")
    print(f"unsplash refs: {old.count('images.unsplash')} -> "
          f"{payload.count('images.unsplash')}")
    print(f"chunk {before/1024:.1f} KB -> {len(out)/1024:.1f} KB")


if __name__ == "__main__":
    main()
