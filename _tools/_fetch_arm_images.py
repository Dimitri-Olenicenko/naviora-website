"""Download the Armconstruct project renders.

Each project page loads images from a folder named after the project
(`/storage/Five towers/...`). The pages also pull in `/storage/icons/` and
`/storage/imports/` — shared UI furniture and stock that appears on every
page — so those are skipped; otherwise every listing would show the same
generic photos.
"""
import json
import glob
import os
import re
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPE = os.path.join(ROOT, "_scrape", "arm")
DEST = os.path.join(ROOT, "assets", "projects")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SKIP = ("icons", "imports", "flags")

# scrape filename -> listings.json slug
SLUG = {
    "five-towers": "five-towers",
    "atlantis-prime": "atlantis-prime",
    "atlantis-yerevan": "atlantis-yerevan",
    "komitas-60-arabkir-district": "komitas-60",
    "davit-bek-290-nor-norq": "davit-bek-290",
    "slavik-chiloyan-17": "slavik-chiloyan-17",
    "zoravar-andranik-1216": "zoravar-andranik-121-6",
}


def folder_of(url):
    m = re.search(r"/storage/([^/]+)/", url)
    return urllib.parse.unquote(m.group(1)).lower() if m else ""


def main():
    os.makedirs(DEST, exist_ok=True)
    manifest = {}

    for f in sorted(glob.glob(os.path.join(SCRAPE, "*.json"))):
        name = os.path.basename(f)[:-5]
        if name.startswith("_"):
            continue
        slug = SLUG.get(name)
        if not slug:
            continue

        d = json.load(open(f, encoding="utf-8"))
        urls = [u for u in d.get("images", [])
                if "/storage/" in u and folder_of(u) not in SKIP]
        # Keep the biggest-looking renders first, drop obvious thumbnails.
        urls = [u for u in urls if not re.search(r"(thumb|small|-\d{2}x\d{2}\.)", u, re.I)]
        urls = sorted(set(urls))

        if not urls:
            print(f"  {slug:26} no project-specific images")
            manifest[slug] = []
            continue

        out = os.path.join(DEST, slug)
        os.makedirs(out, exist_ok=True)
        saved = []
        for u in urls[:10]:
            ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower() or ".webp"
            fn = f"{slug}-{len(saved)+1}{ext}"
            dst = os.path.join(out, fn)
            if not os.path.exists(dst):
                try:
                    req = urllib.request.Request(u, headers={"User-Agent": UA})
                    data = urllib.request.urlopen(req, timeout=45).read()
                    if len(data) < 8000:      # skip icons/spacers that slipped through
                        continue
                    open(dst, "wb").write(data)
                except Exception:
                    continue
            saved.append(f"/naviora-website/assets/projects/{slug}/{fn}")

        manifest[slug] = saved
        print(f"  {slug:26} {len(saved)} images")

    json.dump(manifest, open(os.path.join(SCRAPE, "_images.json"), "w",
                             encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\ntotal {sum(len(v) for v in manifest.values())} images")


if __name__ == "__main__":
    main()
