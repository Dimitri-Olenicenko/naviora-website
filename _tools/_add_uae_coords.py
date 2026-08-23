"""Add the UAE map pins that resolved to the named building itself.

Only building-level fixes are written. The research also produced community
centroids, masterplan points and one site-office pin for seven more projects;
those are deliberately left out, because a marker on a community centroid
looks authoritative while pointing at the wrong plot. Two of them (River Cove
and The Terraces) share one coordinate — Sobha embeds the same Sobha City
masterplan point on both pages — so publishing them would stack two markers
on a single pixel.

Traps found and avoided, recorded here so nobody re-adopts them later:
  - Sobha's own pages carry a Google Maps short link that resolves to their
    Dubai head office (25.1762, 55.3113), not the Abu Dhabi project.
  - "The Residences at DIFC Zabeel District" does not exist on Maps; the
    nearby DIFC Living is a different building.
  - "Fahid Beach Club" and "Fahid Experience Center" are a beach club and a
    sales centre, not Aldar's Beach House.

Manchester City Yas Residences — the Yas Island vs Al Raha Beach question is
settled in favour of Yas Island, which is what the original brief said.
Ohana's own project page states the development is "Set within one of Abu
Dhabi's most dynamic districts on Yas Island" and gives its location as "Yas
Canal, Abu Dhabi"; its masterplan lists Ferrari World at 6 minutes. Reverse
-geocoding the pin against OpenStreetMap also returns جزيرة ياس (Yas Island).
Yas Canal is a waterway *on* Yas Island, so "on Yas Canal" and "on Yas
Island" agree rather than conflict. The district text is left as Yas Island.

Idempotent.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> (lat, lng). Each of these is the named building/place record itself,
# cross-checked by reverse-geocoding the pin against OpenStreetMap.
PINS = {
    "samana-barari-avenue":           (25.0918203, 55.3107432),
    "azizi-emerald":                  (25.2331875, 55.3218125),
    "aeon-creek-harbour":             (25.2063979, 55.3518043),
    "09-life-residences":             (25.0969029, 55.3720924),
    "manchester-city-yas-residences": (24.4782240, 54.6190080),
    "fairmont-marina-residences":     (24.4814131, 54.3209175),
    # Al Reem offices — refine the earlier approximate pins.
    "radiant-atrium-towers":          (24.4940790, 54.4006880),
    "addax-port-office-tower":        (24.4989329, 54.4031167),
    "radiant-height":                 (24.4963445, 54.4046392),
}

# Yas Canal is the waterfront setting within Yas Island, per Ohana's own page.
DISTRICT_FIX = {
    "manchester-city-yas-residences": "Yas Island, Yas Canal",
}


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))

    pinned = moved = fixed = 0
    for x in listings:
        slug = x["slug"]
        if slug in PINS:
            lat, lng = PINS[slug]
            if not x.get("lat"):
                pinned += 1
            elif (round(x["lat"], 5), round(x["lng"], 5)) != (round(lat, 5), round(lng, 5)):
                moved += 1
            x["lat"], x["lng"] = lat, lng
        if slug in DISTRICT_FIX:
            x["district"] = DISTRICT_FIX[slug]
            x["address"] = f'{DISTRICT_FIX[slug]}, Абу-Даби'
            fixed += 1

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    total = len(listings)
    have = sum(1 for x in listings if x.get("lat"))
    missing = [x["slug"] for x in listings if not x.get("lat")]
    print(f"newly pinned: {pinned}, refined: {moved}, district corrected: {fixed}")
    print(f"pinned {have} of {total}")
    print(f"\nstill unpinned ({len(missing)}) — only community/masterplan "
          f"points available:")
    for s in missing:
        print(f"  {s}")


if __name__ == "__main__":
    main()
