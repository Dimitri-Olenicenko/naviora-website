"""Download remotely-hosted listing images into assets/ and repoint listings.json.

Two problems this fixes:

1. Some listings hotlink VR Holding's own CDN (vr.ge / digitaloceanspaces).
   Those URLs carry upload timestamps and will rot the moment the developer
   reorganises their media library, leaving empty galleries on our site.

2. One listing — the Five Towers commercial unit — carried Unsplash stock
   photos of unrelated buildings. Generic stock on a specific investment
   listing misrepresents the asset, so those are dropped rather than
   localised; the listing falls back to the Armconstruct renders of the same
   development, which are real photographs of the actual project.

Idempotent: images already living under assets/ are left alone.
"""
import json
import os
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "projects")
BASE = "/naviora-website"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Stock-photo hosts: never localise, always drop.
STOCK = ("images.unsplash.com", "unsplash.com", "pexels.com", "istockphoto")


def ext_of(url):
    p = urllib.parse.urlparse(url).path
    e = os.path.splitext(p)[1].lower()
    return e if e in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))

    fetched = dropped = kept = failed = 0

    for x in listings:
        imgs = x.get("images") or []
        if not imgs:
            continue
        out_dir = os.path.join(DEST, x["slug"])
        new = []

        for u in imgs:
            if u.startswith("/"):
                new.append(u)
                kept += 1
                continue
            if any(s in u for s in STOCK):
                dropped += 1
                continue

            os.makedirs(out_dir, exist_ok=True)
            fn = f'{x["slug"]}-r{len(new)+1}{ext_of(u)}'
            dst = os.path.join(out_dir, fn)
            rel = f'{BASE}/assets/projects/{x["slug"]}/{fn}'

            if os.path.exists(dst) and os.path.getsize(dst) > 8000:
                new.append(rel)
                kept += 1
                continue
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                data = urllib.request.urlopen(req, timeout=60).read()
                if len(data) < 8000:
                    failed += 1
                    continue
                open(dst, "wb").write(data)
                new.append(rel)
                fetched += 1
            except Exception:
                failed += 1

        if new != imgs:
            x["images"] = new
            note = []
            if len(new) < len(imgs):
                note.append(f"-{len(imgs)-len(new)}")
            print(f'  {x["slug"]:34} {len(imgs)} -> {len(new)} {" ".join(note)}')

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    remote = sum(1 for x in listings for u in (x.get("images") or [])
                 if not u.startswith("/"))
    empty = [x["slug"] for x in listings if not x.get("images")]
    print(f"\ndownloaded {fetched}, already local {kept}, "
          f"stock dropped {dropped}, failed {failed}")
    print(f"still remote: {remote}")
    if empty:
        print(f"listings with no images ({len(empty)}): {', '.join(empty)}")


if __name__ == "__main__":
    main()
