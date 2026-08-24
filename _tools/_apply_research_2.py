"""Apply the second research pass: verified pins, Addax images, Radiant Heights.

Only findings that survived independent verification are written.

ADOPTED
  - Addax Port Office Tower: OSM way 464072869 "Addax office tower", commercial,
    60 levels, 266m — matches the tower's published specs. Reverse-geocodes to
    Al Reem Island. Two gallery images from addaxtower.com inspected by eye and
    confirmed to show the real building (curved blue-glass tower on the Al Reem
    waterfront), unlike that site's slider, which is downtown Los Angeles stock.
  - Radiant Heights: OSM way 1000775184, residential, 32 levels, 120m, on Matar
    bin Thani al Rumaithi St, Al Reem. The listing was carrying the singular
    "Radiant Height" and an approximate pin; both corrected. Research also
    established that radiantenterprises.ae is a *different* company (Mussaffah
    industrial work), which is why the name never appeared in their portfolio —
    the developer attribution is therefore removed rather than left wrong.

DELIBERATELY NOT ADOPTED
  - The Brooks (24.9982731, 55.4279656): Sobha's own short link resolves that
    exact point to "Sobha Sanctuary" — the community, not the plot. A community
    centroid presented as a building pin is the error this project has already
    made once.
  - River Cove and The Terraces: Sobha embeds a byte-identical marker on both
    pages. Two towers cannot share one coordinate, and publishing it twice puts
    two markers on one pixel.
  - Hayat 6, Athlon, Serro 2, DIFC Zabeel, Beach House Fahid, Al Ghadeer
    Gardens: not found. Those developer pages are client-rendered, so the
    coordinates are absent from the HTML rather than absent from the world.

Idempotent.
"""
import json
import os
import shutil
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

PINS = {
    "addax-port-office-tower": (24.499065, 54.403142),
    "radiant-height": (24.496524, 54.404621),
}

# Verified by eye against the OSM building record before being adopted.
ADDAX_IMAGES = [
    "https://addaxtower.com/storage/gallaries/"
    "e8tWMyqpOO0BLO4kuecURNt99fyrfVVSyCUNBf24.jpg",
    "https://addaxtower.com/storage/gallaries/"
    "9Q4Q0B21TI52LTiUIdRrHLbhzuV5ZXChNikxXyj3.jpg",
]

# Facts confirmed from the OSM building records.
FACTS = {
    "addax-port-office-tower": [
        "60 этажей, высота 266 м",
        "Al Reem Island — юрисдикция ADGM",
    ],
    "radiant-height": [
        "32 этажа, высота 120 м",
        "Matar bin Thani al Rumaithi St, Al Reem Island",
    ],
}


def fetch_images(slug, urls):
    dest = os.path.join(ROOT, "assets", "projects", slug)
    os.makedirs(dest, exist_ok=True)
    out = []
    for u in urls:
        name = f"{slug}-{len(out)+1}.jpg"
        path = os.path.join(dest, name)
        if not os.path.exists(path):
            cached = os.path.join(ROOT, "_scrape",
                                  "ax_" + u.split("/")[-1][:8] + ".jpg")
            if os.path.exists(cached):
                shutil.copy2(cached, path)
            else:
                try:
                    req = urllib.request.Request(
                        u, headers={"User-Agent": UA,
                                    "Referer": "https://addaxtower.com/"})
                    data = urllib.request.urlopen(req, timeout=45).read()
                    if len(data) < 20000:
                        continue
                    open(path, "wb").write(data)
                except Exception:
                    continue
        out.append(f"/naviora-website/assets/projects/{slug}/{name}")
    return out


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    by = {x["slug"]: x for x in listings}

    pinned = imaged = renamed = 0

    for slug, (lat, lng) in PINS.items():
        x = by.get(slug)
        if not x:
            continue
        x["lat"], x["lng"] = lat, lng
        pinned += 1
        for f in FACTS.get(slug, []):
            if f not in (x.get("highlights") or []):
                x.setdefault("highlights", []).append(f)
        print(f"  {slug:26} pinned {lat}, {lng}")

    # Addax images
    x = by.get("addax-port-office-tower")
    if x and not x.get("images"):
        imgs = fetch_images("addax-port-office-tower", ADDAX_IMAGES)
        if imgs:
            x["images"] = imgs
            imaged = len(imgs)
            print(f"  addax                      {imaged} verified images")

    # "Radiant Height" is actually "Radiant Heights", and the developer
    # attribution was wrong — radiantenterprises.ae is a different company.
    x = by.get("radiant-height")
    if x and x.get("title") != "Radiant Heights":
        x["title"] = "Radiant Heights"
        x["developer"] = ""
        x["district"] = "Al Reem Island, Matar bin Thani al Rumaithi St"
        x["address"] = "Al Reem Island, Абу-Даби"
        renamed = 1
        print("  radiant-height             -> Radiant Heights, developer cleared")

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    have = sum(1 for x in listings if x.get("lat"))
    noimg = [x["slug"] for x in listings if not x.get("images")]
    print(f"\npinned {have} of {len(listings)}")
    print(f"images added: {imaged}, renamed: {renamed}")
    print(f"still without images ({len(noimg)}): {', '.join(noimg) or 'none'}")


if __name__ == "__main__":
    main()
