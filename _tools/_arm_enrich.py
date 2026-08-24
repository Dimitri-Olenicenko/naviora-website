"""Extract the Armconstruct facts that were scraped but never parsed.

The project pages carry an "End Date" field plus a block of site statistics
(green area, parking, security). The original importer only took price and
description, so seven Armenian listings shipped with an empty handover date
while the date was sitting in the scrape all along.

Nothing here is researched or inferred — every value is read out of the page
text captured in _scrape/arm/.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPE = os.path.join(ROOT, "_scrape", "arm")

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

MONTHS_RU = {
    "January": "январь", "February": "февраль", "March": "март",
    "April": "апрель", "May": "май", "June": "июнь", "July": "июль",
    "August": "август", "September": "сентябрь", "October": "октябрь",
    "November": "ноябрь", "December": "декабрь",
}


def parse(path):
    d = json.load(open(path, encoding="utf-8"))
    t = re.sub(r"\s+", " ", d.get("text", ""))
    out = {}

    m = re.search(r"End Date\s+([A-Z][a-z]+)\s+(20\d\d)", t)
    if m:
        month, year = m.group(1), m.group(2)
        out["handover"] = f"{MONTHS_RU.get(month, month).capitalize()} {year}"
        out["_raw"] = f"{month} {year}"

    m = re.search(r"Green Areas\s+([\d\s]+)", t)
    if m:
        out["green"] = m.group(1).strip()
    m = re.search(r"Parking Area\s+([\d\s]+)", t)
    if m:
        out["parking"] = m.group(1).strip()

    # the lowest published unit price, in AMD
    prices = [int(x.replace(",", "")) for x in re.findall(r"([\d,]{7,})\s*֏", t)]
    if prices:
        out["price_amd"] = min(prices)
    return out


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    by = {x["slug"]: x for x in listings}
    AMD = 383.0

    hand = price = extra = 0
    for f in sorted(glob.glob(os.path.join(SCRAPE, "*.json"))):
        name = os.path.basename(f)[:-5]
        slug = SLUG.get(name)
        if not slug or slug not in by:
            continue
        got = parse(f)
        x = by[slug]

        if got.get("handover") and not x.get("handover"):
            x["handover"] = got["handover"]
            hand += 1
            print(f"  {slug:26} handover <- {got['_raw']}")

        if got.get("price_amd") and not x.get("priceUsd"):
            x["priceUsd"] = round(got["price_amd"] / AMD)
            x["priceFrom"] = True
            x["priceNote"] = "AMD→USD @ 383"
            price += 1
            print(f"  {slug:26} price    <- {got['price_amd']:,} AMD")

        # site statistics belong in the highlights, where they are useful
        hl = x.get("highlights") or []
        add = []
        if got.get("green"):
            add.append(f'Озеленение — {got["green"]} м²')
        if got.get("parking"):
            add.append(f'Парковка — {got["parking"]} мест')
        new = [a for a in add if a not in hl]
        if new:
            x["highlights"] = hl + new
            extra += len(new)

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\nhandover dates added: {hand}")
    print(f"prices added: {price}")
    print(f"highlight facts added: {extra}")

    still = [x["slug"] for x in listings
             if x["country"] == "armenia" and not x.get("handover")]
    if still:
        print(f"still without handover: {', '.join(still)}")


if __name__ == "__main__":
    main()
