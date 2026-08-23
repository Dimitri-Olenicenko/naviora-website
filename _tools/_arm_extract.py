"""Pull the per-project latitude/longitude out of the Armconstruct pages.

The coordinates are embedded in a Vue/Inertia props blob where the quotes are
HTML-escaped (`latitude&quot;:&quot;40.220040&quot;`), which is why a naive
`"lat":` regex finds nothing and the only visible Google Maps link is the
company's own head office (40.2005, 44.5097) repeated in the footer of every
page. Unescaping first exposes the real per-project pins.
"""
import html
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_scrape", "arm")

SLUGS = ["five-towers", "atlantis-prime", "atlantis-yerevan",
         "davit-bek-290-nor-norq", "komitas-60-arabkir-district",
         "slavik-chiloyan-17", "zoravar-andranik-1216"]

# The head-office pin; it appears on every page and must never be used
# as a project location.
OFFICE = (40.2005303, 44.509709)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "ignore")


def extract(raw):
    txt = html.unescape(raw)
    out = {}

    pairs = re.findall(
        r'"latitude"\s*:\s*"?(-?\d+\.\d+)"?.{0,120}?"longitude"\s*:\s*"?(-?\d+\.\d+)"?',
        txt, re.S)
    pins = []
    for la, lo in pairs:
        la, lo = float(la), float(lo)
        if abs(la - OFFICE[0]) < 1e-4 and abs(lo - OFFICE[1]) < 1e-4:
            continue                      # head office, not the project
        if not (39.5 < la < 41.5 and 43.5 < lo < 46.5):
            continue                      # outside Armenia
        if (la, lo) not in pins:
            pins.append((la, lo))
    out["pins"] = pins

    # Price, floors, unit count and handover as published on the page.
    m = re.search(r"Starting from:\s*([\d,\. ]+)\s*֏", txt)
    out["price_amd"] = m.group(1).replace(",", "").replace(" ", "") if m else None

    m = re.search(r'"deadline"\s*:\s*"([^"]+)"', txt) or \
        re.search(r'"delivery_date"\s*:\s*"([^"]+)"', txt)
    out["deadline"] = m.group(1) if m else None

    out["videos"] = sorted(set(re.findall(
        r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})", txt)))
    out["pdfs"] = sorted(set(re.findall(r'https?://[^"\'\s<>]+\.pdf', txt)))
    out["images"] = sorted(set(re.findall(
        r'https://armconstruct\.am/storage/[^"\'\s<>\\]+\.(?:webp|jpg|jpeg|png)', txt)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    result = {}
    for s in SLUGS:
        try:
            raw = fetch(f"https://armconstruct.am/en/projects/{s}")
        except Exception as e:
            print(f"  !! {s}: {str(e)[:50]}")
            continue
        d = extract(raw)
        result[s] = d
        pin = d["pins"][0] if d["pins"] else None
        print(f"{s:30} pin={pin} price={d['price_amd']} "
              f"vid={len(d['videos'])} pdf={len(d['pdfs'])} img={len(d['images'])}")
        if len(d["pins"]) > 1:
            print(f"{'':30} (+{len(d['pins'])-1} more pins: {d['pins'][1:4]})")

    json.dump(result, open(os.path.join(OUT, "_extracted.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {OUT}\\_extracted.json")


if __name__ == "__main__":
    main()
