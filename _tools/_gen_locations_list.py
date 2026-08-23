"""Write the list of listings still missing a map pin, as a checklist.

The site publishes a marker only where the named building itself resolved.
Everything below is a project where the best available answer was a district
centroid, which would drop the pin on an unrelated block — so it is left
empty until someone can supply the real location.
"""
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "LOCATIONS-NEEDED.md")

COUNTRY = {"dubai": "Дубай", "abudhabi": "Абу-Даби",
           "armenia": "Ереван", "georgia": "Тбилиси"}


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"), encoding="utf-8"))
    missing = [x for x in listings if not x.get("lat")]
    pinned = [x for x in listings if x.get("lat")]

    lines = [
        "# Locations still needed",
        "",
        f"_Generated {date.today().isoformat()} — "
        f"{len(pinned)} of {len(listings)} listings are pinned._",
        "",
        "Each project below shows no map marker on the site. A district centroid",
        "was available for all of them, but publishing one puts the pin on the",
        "wrong building, so the field is deliberately empty.",
        "",
        "**To fill one in:** open the developer's project page, find the embedded",
        "Google Maps link, and read the coordinates out of the `!8m2!3d<lat>!4d<lon>`",
        "part of the URL. Paste the pair into the table and re-run",
        "`_tools/_add_offices_and_coords.py`.",
        "",
    ]

    for country, label in COUNTRY.items():
        rows = [x for x in missing if x["country"] == country]
        if not rows:
            continue
        lines += [f"## {label} ({len(rows)})", "",
                  "| Проект | Застройщик | Район | lat, lng |",
                  "|---|---|---|---|"]
        for x in rows:
            lines.append(
                f'| {x["title"]} | {x.get("developer") or "—"} '
                f'| {x.get("district") or "—"} |  |')
        lines.append("")

    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"wrote LOCATIONS-NEEDED.md — {len(missing)} projects")
    for country, label in COUNTRY.items():
        n = sum(1 for x in missing if x["country"] == country)
        if n:
            print(f"  {label:10} {n}")


if __name__ == "__main__":
    main()
