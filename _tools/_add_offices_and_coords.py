"""
Add three Abu Dhabi office projects (all on Al Reem Island, inside ADGM) and
set map coordinates.

Coordinate policy: only HIGH-confidence pins are written. The research returned
21 district-level pins, and a district centroid can land a marker in the wrong
place — this repo's history includes one that sat 9km offshore. An approximate
pin is worse than no pin, so those are left null until each developer's own
map link is resolved.

Two prior claims were NOT reproducible and are deliberately excluded:
  - "from AED 1.7M" for Radiant Atrium (that figure belongs to Radiant Square)
  - a "60/40 payment plan" for Radiant Atrium (published nowhere)

Idempotent.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AED = 3.6725
SQFT = 0.092903

OFFICES = [
    dict(slug="radiant-atrium-towers", title="Radiant Atrium Towers",
         developer="Radiant Enterprises Real Estate", district="Al Reem Island, City of Lights",
         market="offplan", price_aed=10500000, size_sqft=532, handover="Q1 2029",
         lat=24.4939983, lng=54.4005613,
         short="Офисная башня на Al Reem Island в периметре ADGM: 133 офиса на 24 этажах, "
               "площади от 532 до 2 520 кв. футов. Свободная планировка, фрихолд для иностранных "
               "покупателей.",
         highlights=["133 офиса на 24 этажах",
                     "Площади от 532 до 2 520 кв. футов",
                     "Al Reem Island — с 2023 года в юрисдикции ADGM",
                     "Фрихолд, инвестиционная зона Абу-Даби",
                     "Сдача Q1 2029"],
         plan="Уточняется у застройщика",
         note="Цена указана по единственному опубликованному лоту."),

    dict(slug="addax-port-office-tower", title="Addax Port Office Tower",
         developer="Addax", district="Al Reem Island", market="secondary",
         price_aed=2400000, size_sqft=1625, handover="Сдан",
         lat=24.4990673, lng=54.4031393,
         short="Готовая офисная башня на Al Reem Island — самое глубокое предложение офисов "
               "в Абу-Даби. Площади от 1 625 до 17 894 кв. футов, около 16 лотов в продаже.",
         highlights=["Готовое здание, офисы в продаже сейчас",
                     "Площади от 1 625 до 17 894 кв. футов",
                     "Около 16 лотов на рынке — крупнейший выбор в эмирате",
                     "Al Reem Island, юрисдикция ADGM",
                     "Фрихолд для иностранных покупателей"],
         plan="Вторичный рынок — оплата по договору"),

    dict(slug="radiant-height", title="Radiant Height",
         developer="Radiant Enterprises Real Estate", district="Al Reem Island",
         market="secondary", price_aed=2900000, size_sqft=1894, handover="Сдан",
         lat=24.4996841, lng=54.4030025,
         short="Готовое офисное здание на Al Reem Island. Площади от 1 894 до 2 758 кв. футов, "
               "диапазон цен 2,9–5,0 млн AED.",
         highlights=["Готовое здание, офисы в продаже",
                     "Площади 1 894 – 2 758 кв. футов",
                     "Диапазон 2,9 – 5,0 млн AED",
                     "Al Reem Island, юрисдикция ADGM",
                     "Фрихолд для иностранных покупателей"],
         plan="Вторичный рынок — оплата по договору"),
]

# Only pins the research graded HIGH confidence.
COORDS = {
    "radiant-atrium-towers": (24.4939983, 54.4005613),
    "addax-port-office-tower": (24.4990673, 54.4031393),
    "radiant-height": (24.4996841, 54.4030025),
}


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    by = {x["slug"]: i for i, x in enumerate(listings)}
    added = 0

    for o in OFFICES:
        item = {
            "id": f'abudhabi-{o["slug"]}',
            "slug": o["slug"],
            "country": "abudhabi",
            "purpose": "commercial",
            "market": o["market"],
            "type": "office",
            "title": o["title"],
            "developer": o["developer"],
            "district": o["district"],
            "city": "Абу-Даби",
            "priceUsd": round(o["price_aed"] / AED),
            "sizeSqm": round(o["size_sqft"] * SQFT),
            "bedrooms": 0,
            "handover": o["handover"],
            "images": [],
            "featured": False,
            "shortDescription": o["short"],
            "highlights": o["highlights"],
            "priceFrom": True,
            "sizeFrom": True,
            "paymentPlan": o["plan"],
            "lat": o["lat"],
            "lng": o["lng"],
            "address": f'{o["district"]}, Абу-Даби',
        }
        if o["slug"] in by:
            listings[by[o["slug"]]] = item
        else:
            listings.append(item)
            added += 1

    pinned = 0
    for x in listings:
        if x["slug"] in COORDS and not x.get("lat"):
            x["lat"], x["lng"] = COORDS[x["slug"]]
            pinned += 1

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    no_pin = [x["slug"] for x in listings
              if x["country"] in ("dubai", "abudhabi") and not x.get("lat")]
    print(f"offices added: {added}")
    print(f"coordinates set: {pinned}")
    print(f"listings now: {len(listings)}")
    print(f"\nstill without a pin ({len(no_pin)}) — district-level only, withheld:")
    for s in no_pin:
        print(f"  {s}")


if __name__ == "__main__":
    main()
