"""Scan the fetched pages for project links, images and embedded media."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPE = os.path.join(ROOT, "_scrape")

KEYS = ("project", "building", "residen", "complex", "tower", "shenq",
        "obiekt", "house", "villa", "skyline")


def scan(name):
    path = os.path.join(SCRAPE, name + ".html")
    if not os.path.exists(path):
        print(f"  !! not fetched: {name}")
        return
    html = open(path, encoding="utf-8", errors="ignore").read()

    print(f"\n{'='*70}\n{name}  ({len(html)//1024} KB)\n{'='*70}")

    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if title:
        print("title:", re.sub(r"\s+", " ", title.group(1)).strip()[:80])

    links = sorted(set(re.findall(r'href=["\']([^"\'#]+)', html)))
    hits = [l for l in links if any(k in l.lower() for k in KEYS)]
    print(f"\nproject-ish links ({len(hits)} of {len(links)}):")
    for l in hits[:40]:
        print("   ", l[:92])

    pdfs = [l for l in links if ".pdf" in l.lower()]
    if pdfs:
        print(f"\nPDFs ({len(pdfs)}):")
        for p in pdfs[:25]:
            print("   ", p[:92])

    vids = set(re.findall(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})", html))
    vids |= set(re.findall(r"vimeo\.com/(?:video/)?(\d{6,})", html))
    if vids:
        print(f"\nvideos ({len(vids)}): {', '.join(sorted(vids))}")

    coords = re.findall(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", html)
    coords += re.findall(r'"lat"\s*:\s*"?(-?\d+\.\d{3,})"?\s*,\s*"lng"\s*:\s*"?(-?\d+\.\d{3,})', html)
    if coords:
        print(f"\ncoords found: {sorted(set(coords))[:12]}")

    imgs = sorted(set(re.findall(r'(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp))', html, re.I)))
    print(f"\nimages: {len(imgs)}")
    for i in imgs[:6]:
        print("   ", i[:92])


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["armconstruct", "skyline", "vrge"]):
        scan(n)
