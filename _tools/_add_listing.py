"""
Add a project to listings.json from data you have pasted in.

Usage: fill in the DATA block below, then run. The script validates required
fields, converts AED->USD and sqft->sqm, builds the slug/id, and appends
without touching existing entries. Re-running with the same slug updates
that entry instead of duplicating it.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
AED_PER_USD = 3.6725  # AED is pegged to USD

# ---------------------------------------------------------------------------
# 09 Life Residences — transcribed from the project page
# ---------------------------------------------------------------------------
DATA = {
    "country": "dubai",
    "purpose": "residential",
    "market": "offplan",
    "type": "apartment",
    "title": "09 Life Residences",
    "developer": "Deniz Properties",
    "district": "Dubai Land Residence Complex",
    "city": "Дубай",
    "address": "Dubai Land Residence Complex, Dubai Residence Complex, Дубай",
    # Lowest studio price on the page: 683,819 AED
    "price_aed": 683819,
    # Smallest listed unit: 391.38 sqft
    "size_sqft": 391.38,
    "bedrooms": 0,           # entry unit type is studio
    "handover": "",          # NOT on the page — left blank rather than guessed
    "lat": None,             # NOT on the page — needs verifying before publish
    "lng": None,
    "shortDescription": (
        "Современный жилой комплекс в Dubai Land: квартиры с полной меблировкой, "
        "встроенной техникой и системой «умный дом». Студии, 1–3 спальни. "
        "План оплаты с рассрочкой 3 года после передачи."
    ),
    "highlights": [
        "Полная меблировка и встроенная кухонная техника",
        "Система «умный дом» в каждой квартире",
        "Рассрочка 40% на 3 года после передачи",
        "Бассейн, спортзал, сауна, кинозал, баскетбольная площадка",
        "Dubai Land Residence Complex — парки, гольф, велодорожки",
    ],
    "paymentPlan": "20% при бронировании / 40% в ходе строительства (6 платежей) / 40% в течение 3 лет после передачи (12 платежей)",
    "images": [],            # add URLs you are licensed to use
    "featured": False,
    # Reference data from the page, kept for the report layer
    "unit_mix": [
        {"type": "Studio",      "units": 48, "from_sqft": 392},
        {"type": "1 Bedroom",   "units": 52, "from_sqft": 779},
        {"type": "2 Bedrooms",  "units": 19, "from_sqft": 997},
        {"type": "3.5 Bedrooms","units": 8,  "from_sqft": 1570},
    ],
    "amenities": [
        "Swimming Pool", "BBQ Area", "Cinema", "Gym", "Kids Pool",
        "Sitting Area", "Table Games Area", "Basketball Court", "Sauna",
    ],
    "construction_status": "Under Construction",
    "sale_status": "On Sale",
    "floors_formula": "G + 2P + 9 floors + R",
}
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"^-|-$", "", s)


def build(d: dict) -> dict:
    slug = slugify(d["title"])
    item = {
        "id": f'{d["country"]}-{slug}',
        "slug": slug,
        "country": d["country"],
        "purpose": d["purpose"],
        "market": d["market"],
        "type": d["type"],
        "title": d["title"],
        "developer": d["developer"],
        "district": d["district"],
        "city": d["city"],
        "priceUsd": round(d["price_aed"] / AED_PER_USD),
        "sizeSqm": round(d["size_sqft"] * 0.092903),
        "bedrooms": d["bedrooms"],
        "handover": d["handover"],
        "images": d["images"],
        "featured": d["featured"],
        "shortDescription": d["shortDescription"],
        "highlights": d["highlights"],
        "priceFrom": True,
        "sizeFrom": True,
        "paymentPlan": d["paymentPlan"],
        "lat": d["lat"],
        "lng": d["lng"],
        "address": d["address"],
    }
    return item


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    item = build(DATA)

    gaps = [k for k in ("handover", "lat", "lng") if not item.get(k)]
    if not item["images"]:
        gaps.append("images")

    idx = next((i for i, x in enumerate(listings) if x["slug"] == item["slug"]), None)
    if idx is None:
        listings.append(item)
        action = "added"
    else:
        listings[idx] = item
        action = "updated"

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"{action}: {item['title']}  ({item['id']})")
    print(f"  price : {DATA['price_aed']:,} AED -> ${item['priceUsd']:,}")
    print(f"  size  : {DATA['size_sqft']} sqft -> {item['sizeSqm']} sqm")
    print(f"  total : {len(listings)} listings")
    if gaps:
        print(f"  MISSING (fill before publishing): {', '.join(gaps)}")


if __name__ == "__main__":
    main()
