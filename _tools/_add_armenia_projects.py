"""Add the real Armconstruct and Skyline projects to listings.json.

Armconstruct: 7 projects taken from armconstruct.am/en/projects/<slug>.
Coordinates come from geocoding each project's published street address, NOT
from the coordinates embedded in the page — those are a mix of the company's
head office (40.2005, 44.5097, repeated in every footer) and nearby landmark
markers (Dalma Mall, Opera, Tumo). Using them would put every project on top
of the sales office.

Skyline: from the research pass. The site's own contact page gives a sales
office on Sasna Tsrer street, 2.3 km from the actual build; the pin here is
the permit address (Orbeli Brothers 23, Arabkir) instead.

Prices are the developer's published "starting from" in AMD, converted at the
rate below. Where no price is published the listing carries none rather than
an invented one.

Idempotent.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMD = 383.0          # AMD per USD, Aug 2026
RATE_NOTE = "AMD→USD @ 383"

P = [
    dict(slug="five-towers", title="Five Towers",
         developer="Armconstruct", district="Ajapnyak, Gevorg Chaush 95",
         lat=40.2114372, lng=44.4629873, price_amd=40_600_000, size=52,
         beds=1, market="offplan", handover="",
         short="Комплекс из пяти корпусов по 23 этажа. В четырёх из пяти зданий "
               "предусмотрено по три коммерческих этажа — магазины, супермаркеты и "
               "сервисы прямо в комплексе.",
         highlights=["Пять корпусов по 23 этажа",
                     "Три коммерческих этажа в четырёх зданиях",
                     "Детский сад и бизнес-центр на территории",
                     "Теннисный корт, футбольное поле, современный зал",
                     "Зарядные станции для электромобилей"]),

    dict(slug="atlantis-prime", title="Atlantis Prime",
         developer="Armconstruct", district="Arabkir, Malkhasyants lane 3",
         lat=40.2110339, lng=44.5075671, price_amd=42_600_000, size=59,
         beds=1, market="offplan", handover="",
         short="Премиальный комплекс в Арабкире рядом с Atlantis Yerevan: 17 надземных "
               "этажей, панорамное остекление в пол, виды на Арарат, проспект Комитаса "
               "и Разданское ущелье.",
         highlights=["17 надземных этажей, премиум-класс",
                     "Панорамные окна в пол",
                     "Виды на Арарат и Разданское ущелье",
                     "Рядом с Atlantis Yerevan, район Арабкир",
                     "56 квартир уже забронировано"]),

    dict(slug="atlantis-yerevan", title="Atlantis Yerevan",
         developer="Armconstruct", district="Arabkir, Malkhasyants lane 6",
         lat=40.2112377, lng=44.5086793, price_amd=None, size=None,
         beds=2, market="offplan", handover="",
         short="Три корпуса премиум-класса в Арабкире с крупными витражными окнами. "
               "Проект позиционируется и как жильё, и как инвестиционный объект.",
         highlights=["Три корпуса премиум-класса",
                     "Большие витражные панорамные окна",
                     "Район Арабкир, Malkhasyants 6",
                     "Полная отделка от застройщика",
                     "Закрытая территория с инфраструктурой"]),

    dict(slug="komitas-60", title="Komitas 60",
         developer="Armconstruct", district="Arabkir, Komitas Avenue 60",
         lat=40.2057990, lng=44.5234798, price_amd=550_000_000, size=None,
         beds=3, market="offplan", handover="",
         short="Премиальный жилой комплекс на проспекте Комитаса — одной из главных "
               "магистралей Еревана, в сложившемся районе Арабкир.",
         highlights=["Проспект Комитаса — центральная локация",
                     "Премиум-класс, район Арабкир",
                     "Сложившаяся городская инфраструктура",
                     "Собственная коммерческая часть"]),

    dict(slug="davit-bek-290", title="Davit Bek 290",
         developer="Armconstruct", district="Nor Nork, 5th massif",
         lat=40.1844287, lng=44.5624304, price_amd=None, size=None,
         beds=2, market="offplan", handover="",
         short="Комплекс в самом высоком жилом районе Еревана — 5-й массив Нор Норка. "
               "Высокая сейсмоустойчивость, чистый воздух, виды на Арарат и церковь "
               "Сурб Саркис.",
         highlights=["Самая высокая жилая точка Еревана",
                     "Высокая сейсмоустойчивость",
                     "Виды на Арарат и Сурб Саркис",
                     "291 квартира уже продана",
                     "Пересечение улиц Микояна и Давид Бека"]),

    dict(slug="slavik-chiloyan-17", title="Slavik Chiloyan 17",
         developer="Armconstruct", district="Arabkir, Slavik Chiloyan 17",
         lat=40.2005717, lng=44.5097329, price_amd=None, size=None,
         beds=2, market="offplan", handover="",
         short="Жилой комплекс в Арабкире на улице Славика Чилояна.",
         highlights=["Район Арабкир", "Застройщик Armconstruct",
                     "Собственная территория"]),

    dict(slug="zoravar-andranik-121-6", title="Zoravar Andranik 121/6",
         developer="Armconstruct", district="Malatia-Sebastia, Zoravar Andranik 121/6",
         lat=40.1661068, lng=44.4456212, price_amd=None, size=None,
         beds=2, market="offplan", handover="",
         short="Премиальный жилой комплекс в районе Малатия-Себастия на улице "
               "Зоравара Андраника.",
         highlights=["Район Малатия-Себастия", "Премиум-класс",
                     "Застройщик Armconstruct"]),

    # Skyline — figures from the research pass, every one traceable to the
    # developer's own pages or the construction permit.
    dict(slug="skyline-yerevan", title="Skyline Yerevan",
         developer="Renshin LLC", district="Arabkir, Orbeli Brothers 23/27/29",
         lat=40.1936935, lng=44.4943577, price_amd=36_400_000, size=26,
         beds=0, market="offplan", handover="Q4 2028",
         short="Крупнейший проект «город в городе» в Ереване: 35 000 м² участка, "
               "более 250 000 м² застройки, пять корпусов, 20 000 м² озеленения. "
               "Архитектура Laguarda.Low (Нью-Йорк), конструктив Arup, интерьеры "
               "1508 London.",
         highlights=["35 000 м² участка, 250 000+ м² застройки",
                     "Пять корпусов, более 2 га озеленения",
                     "Школа и детский сад, 12 точек ретейла и ресторанов",
                     "7 офисных и коворкинг-пространств",
                     "Электрошаттлы до центра каждые 30 минут",
                     "Рассрочка 20/80 без процентов до декабря 2028",
                     "Цена от 1 500 000 драм/м² (1 400 000 при полной оплате)"],
         plan="20% первый взнос / 80% равными платежами до декабря 2028 (без процентов)"),
]


def load_images():
    """Images downloaded by _fetch_arm_images.py plus the Skyline set."""
    imgs = {}
    man = os.path.join(ROOT, "_scrape", "arm", "_images.json")
    if os.path.exists(man):
        imgs.update(json.load(open(man, encoding="utf-8")))
    sky = os.path.join(ROOT, "_scrape", "skyline_images.json")
    if os.path.exists(sky):
        imgs["skyline-yerevan"] = json.load(open(sky, encoding="utf-8"))
    return imgs


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    by = {x["slug"]: i for i, x in enumerate(listings)}
    images = load_images()
    added = updated = 0

    for p in P:
        item = {
            "id": f'armenia-{p["slug"]}',
            "slug": p["slug"],
            "country": "armenia",
            "purpose": "residential",
            "market": p["market"],
            "type": "apartment",
            "title": p["title"],
            "developer": p["developer"],
            "district": p["district"],
            "city": "Ереван",
            "priceUsd": round(p["price_amd"] / AMD) if p["price_amd"] else None,
            "priceNote": RATE_NOTE if p["price_amd"] else "Цена по запросу",
            "sizeSqm": p["size"],
            "bedrooms": p["beds"],
            "handover": p["handover"],
            "images": images.get(p["slug"], []),
            "featured": p["slug"] == "skyline-yerevan",
            "shortDescription": p["short"],
            "highlights": p["highlights"],
            "priceFrom": bool(p["price_amd"]),
            "sizeFrom": bool(p["size"]),
            "paymentPlan": p.get("plan", "Уточняется у застройщика"),
            "lat": p["lat"],
            "lng": p["lng"],
            "address": f'{p["district"]}, Ереван',
        }
        if p["slug"] in by:
            listings[by[p["slug"]]] = item
            updated += 1
        else:
            listings.append(item)
            added += 1

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"armenia: added {added}, updated {updated}")
    print(f"listings now: {len(listings)}")
    priced = sum(1 for p in P if p["price_amd"])
    print(f"with published price: {priced} of {len(P)} "
          f"(the rest show 'по запросу' rather than a guess)")


if __name__ == "__main__":
    main()
