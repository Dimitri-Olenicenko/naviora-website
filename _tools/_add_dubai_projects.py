"""
Add the nine off-plan Dubai projects to listings.json and copy their images
into assets/projects/<slug>/.

Data is transcribed from the developer-supplied project sheets. Prices are the
lowest published unit price; sizes the smallest published unit. AED converts at
the 3.6725 peg. Where a field was not stated on the sheet it is left empty
rather than guessed — handover dates in particular.

Brochures are NOT copied: they total 319 MB (five are 24-68 MB each), which is
too heavy for a GitHub Pages repo and a bad mobile experience. Decide how to
host them separately.

Idempotent: re-running updates existing entries rather than duplicating.
"""
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "projects", "dubai")
DEST = os.path.join(ROOT, "assets", "projects")
AED = 3.6725
SQFT_TO_SQM = 0.092903

P = [
    dict(folder="office samana", slug="samana-barari-avenue", purpose="commercial",
         type="office", title="Samana Barari Avenue", developer="Samana",
         district="Majan", price_aed=2382454, size_sqft=952.07, bedrooms=0,
         handover="",
         short="Премиальный бизнес-парк в Majan на Sheikh Mohammed bin Zayed Road: "
               "офисы и стрит-ретейл, панорамное остекление, гибкие условия аренды и покупки.",
         highlights=["57 офисов от 952 кв. футов, 17 ретейл-юнитов",
                     "Витрины первой линии с высоким пешеходным трафиком",
                     "Энергоэффективная архитектура, панорамное остекление",
                     "VIP-зона высадки, скоростной интернет, парковка",
                     "Рассрочка 15/85 с платежами после передачи"],
         plan="15% при бронировании / 85% в ходе строительства и после передачи "
              "(5% в течение 9 месяцев, по 1% в месяц)",
         amenities=["Бассейн", "Открытая фитнес-зона", "Зоны отдыха", "Ретейл", "Кафе"]),

    dict(folder="hq rove office", slug="hq-by-rove", purpose="commercial",
         type="office", title="HQ by Rove", developer="Irth Development",
         district="Business Bay", price_aed=3480274, size_sqft=680, bedrooms=0,
         handover="Q1 2029",
         short="Первое офисное здание Дубая под гостиничным брендом Rove. 23 офисных этажа "
               "в Marasi Bay, прямой выход к Dubai Canal, полностью готовые и меблированные офисы.",
         highlights=["Первый в Дубае офис под брендом отеля (Rove)",
                     "23 офисных этажа, панорамные виды, выход к Dubai Canal",
                     "Офисы от 680 кв. футов, возможность объединять юниты",
                     "Loft-офисы с двойной высотой потолков и своими санузлами",
                     "Коворкинг, переговорные, лаунж, кафе, руфтоп"],
         plan="15% при бронировании / 35% в ходе строительства (7 платежей) / 50% при передаче",
         amenities=["Коворкинг", "Переговорные", "Спортзал", "Бассейн", "Руфтоп-терраса",
                    "Nap Pods", "Ивент-пространство", "EV-зарядки"]),

    dict(folder="azizi office", slug="azizi-emerald", purpose="commercial",
         type="office", title="Azizi Emerald", developer="Azizi",
         district="Dubai Healthcare City", price_aed=5248000, size_sqft=1340.66, bedrooms=0,
         handover="Q1 2028",
         short="Офисное здание 68,5 м в Dubai Healthcare City: 11 офисных этажей, "
               "прямой доступ к метро, 8 уровней парковки, ретейл на первом этаже.",
         highlights=["11 офисных этажей, высота здания 68,5 м",
                     "Прямая связь с линией метро",
                     "8 уровней парковки, EV-зарядки, преимущественные места у лифтов",
                     "Рядом Wafi Mall, Museum of the Future, Burj Khalifa",
                     "Рассрочка 40/60"],
         plan="10% при бронировании / 30% в ходе строительства (3 платежа) / 60% при передаче",
         amenities=["Кафе и рестораны", "Парковые зоны", "Ретейл"],
         video="JQBoIAIwdgc"),

    dict(folder="villa dubai sobha", slug="the-brooks-sobha-sanctuary", purpose="residential",
         type="villa", title="The Brooks at Sobha Sanctuary", developer="Sobha",
         district="Sobha Sanctuary", price_aed=7350435, size_sqft=4141, bedrooms=5,
         handover="",
         short="Виллы в Sobha Sanctuary: зелёные коридоры, водные пространства и wellness-"
               "инфраструктура. Садовые и патио-виллы с террасами и smart-home.",
         highlights=["Виллы 5 спален, 4 141 кв. фут",
                     "Лагуна, спа, гидротерапия, медитационные лужайки",
                     "Wellness-петли для ходьбы и велоспорта, лесные тропы",
                     "Коворкинг, ивент-лужайки, зоны для питомцев",
                     "Smart-home, приватные террасы, indoor-outdoor планировки"],
         plan="20% при бронировании / 40% в ходе строительства (4 платежа) / 40% при передаче",
         amenities=["Пляжная лагуна", "Социальный клуб", "Велосети", "Wellness-петля",
                    "Медитационные лужайки", "Парк для питомцев", "Детские зоны"]),

    dict(folder="villa hayat", slug="hayat-6-dubai-south", purpose="residential",
         type="villa", title="Hayat 6", developer="Dubai South Properties",
         district="Dubai South, Madinat Al Mataar", price_aed=5935000, size_sqft=4915, bedrooms=5,
         handover="",
         short="Закрытое комьюнити в Dubai South: таунхаусы и виллы 4–5 спален с частными "
               "садами, крышными террасами и центральным озером.",
         highlights=["Таунхаусы и виллы 4–5 спален от 4 915 кв. футов",
                     "Центральное озеро, бассейны, ландшафтные парки",
                     "Клубный дом, спортзоны, фитнес и wellness",
                     "Районный молл и ретейл-бульвар",
                     "Рассрочка 70/30 с платежами после передачи"],
         plan="5% при бронировании / 35% в ходе строительства / 30% при передаче / "
              "30% в течение 24 месяцев после передачи",
         amenities=["Ландшафтный сад", "Набережная парка", "Ретейл и рестораны",
                    "Фитнес и йога-студия", "Общий бассейн", "Лагуны и озеро"]),

    dict(folder="villa Arabian Ranches 3", slug="athlon-by-aldar", purpose="residential",
         type="villa", title="Athlon by Aldar", developer="ALDAR",
         district="Arabian Ranches 3, Wadi Al Safa 5", price_aed=13582780, size_sqft=6083,
         bedrooms=5, handover="Q4 2028",
         short="Первое в ОАЭ комьюнити с сертификатом LEED Platinum. Более 10 км дорожек "
               "для бега, велоспорта и роликов, центральный парк, клубные дома.",
         highlights=["Первое комьюнити ОАЭ с LEED Platinum",
                     "Более 10 км трасс для бега, велоспорта и роликов",
                     "Готовность 8,32%, сдача Q4 2028",
                     "Виллы 5–6 спален от 6 083 кв. футов",
                     "Сервисный сбор 7 AED/кв. фут, эскроу есть"],
         plan="10% при бронировании / 50% в ходе строительства / 40% при передаче",
         amenities=["Бассейн", "Открытый спортзал", "Падел-теннис", "Баскетбол",
                    "Клубный дом", "Йога-платформа", "Кинолужайка", "Велотрек", "Памп-трек"]),

    dict(folder="emaar villa", slug="serro-2-the-heights", purpose="residential",
         type="villa", title="Serro 2", developer="Emaar",
         district="The Heights, Al Yalayis 5", price_aed=6836888, size_sqft=3340, bedrooms=3,
         handover="Q2 2030",
         short="Виллы 3–5 спален в The Heights: средиземноморские мотивы, белые фасады с "
               "терракотовыми акцентами, wellness-центр и клубный дом в центре комьюнити.",
         highlights=["Виллы 3–5 спален от 3 340 кв. футов",
                     "Wellness-центр и клубный дом",
                     "Средиземноморская архитектура, белый и терракота",
                     "Кухня с отделкой в комплекте",
                     "Сервисный сбор 3–4 AED/кв. фут, эскроу есть"],
         plan="10% при бронировании / 70% в ходе строительства (7 платежей) / 20% при передаче",
         amenities=["Wellness-центр и клубный дом", "Спортивные корты", "Общий бассейн",
                    "Детская площадка", "Ретейл", "Спортзал", "Линейный парк"]),

    dict(folder="difc apartment", slug="residences-difc-zabeel", purpose="residential",
         type="apartment", title="The Residences DIFC Zabeel District",
         developer="Dubai International Financial Centre (DIFC)",
         district="Zabeel, Za'abeel", price_aed=2980000, size_sqft=846, bedrooms=1,
         handover="Q4 2029",
         short="Первый жилой проект в новом районе DIFC Zabeel District: две башни, "
               "квартиры и дуплекс-пентхаусы, прямая связь с Gate District и Museum of the Future.",
         highlights=["Первый жилой проект DIFC Zabeel District",
                     "Две башни, квартиры и дуплекс-пентхаусы",
                     "Связь с Gate District и Museum of the Future через Future Loop",
                     "Пешеходный бульвар, премиальный ретейл, зелёная петля Inner Circle",
                     "Сдача Q4 2029"],
         plan="5% при бронировании / 45% в ходе строительства (8 платежей) / 50% при передаче",
         amenities=["Падел и сквош", "Коворкинг", "Семейный бассейн", "Резорт-бассейн с кабанами",
                    "Клубный дом со спортзалом и йога-студией", "Премиальный ретейл"]),

    dict(folder="eywa", slug="eywa-business-bay", purpose="residential",
         type="apartment", title="Eywa", developer="Revolution",
         district="Business Bay", price_aed=11455773, size_sqft=2973, bedrooms=2,
         handover="Q4 2026",
         short="Архитектурный проект на Dubai Water Canal, вдохновлённый баньяном: висячие сады, "
               "водопады, камни и кристаллы. Планировки по принципам васту, террасы с бассейнами.",
         highlights=["Готовность 60%, сдача Q4 2026",
                     "Террасы с частными бассейнами, виды на канал и скайлайн",
                     "Планировки по принципам васту",
                     "Водопады у входа, висячие сады, каменные сады",
                     "Сервисный сбор 35 AED/кв. фут, эскроу есть"],
         plan="10% при бронировании / 40% в ходе строительства (4 платежа) / 50% при передаче",
         amenities=["4 бассейна", "Спа", "Открытый и закрытый кинотеатры", "Спортзал",
                    "Клубный дом и ресторан", "Библиотека", "Йога-студия", "Детская площадка"]),

    dict(folder="creek apartment", slug="aeon-creek-harbour", purpose="residential",
         type="apartment", title="Aeon", developer="Emaar",
         district="Dubai Creek Harbour, Al Kheeran 1", price_aed=3197888, size_sqft=1289,
         bedrooms=2, handover="Q3 2027",
         short="Башни на набережной Dubai Creek Harbour рядом с центральной площадью: "
               "виды на канал, парки и скайлайн, выход к Creek Beach.",
         highlights=["Готовность 63,55%, сдача Q3 2027",
                     "Виды на Dubai Creek Canal, парки и небоскрёбы",
                     "Рядом Creek Beach — 700 м белого песка",
                     "Квартиры 1–3 спальни, панорамные балконы",
                     "Сервисный сбор 22–23 AED/кв. фут, эскроу есть"],
         plan="10% при бронировании / 80% в ходе строительства / 10% при передаче",
         amenities=["Бассейн", "Спортзал", "Набережная-променад", "Велотрек",
                    "Скейт-парк и корты", "Городской пляж"]),
]


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"), encoding="utf-8"))
    by_slug = {x["slug"]: i for i, x in enumerate(listings)}
    added = updated = imgs = 0

    for p in P:
        src = os.path.join(SRC, p["folder"])
        if not os.path.isdir(src):
            print(f"  !! folder missing: {p['folder']}")
            continue

        # copy images (webp only — brochures stay out of the repo)
        out = os.path.join(DEST, p["slug"])
        os.makedirs(out, exist_ok=True)
        urls = []
        for f in sorted(os.listdir(src)):
            if not f.lower().endswith((".webp", ".jpg", ".jpeg", ".png")):
                continue
            ext = os.path.splitext(f)[1].lower()
            name = f"{p['slug']}-{len(urls)+1}{ext}"
            dst = os.path.join(out, name)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(src, f), dst)
                imgs += 1
            urls.append(f"/naviora-website/assets/projects/{p['slug']}/{name}")

        item = {
            "id": f"dubai-{p['slug']}",
            "slug": p["slug"],
            "country": "dubai",
            "purpose": p["purpose"],
            "market": "offplan",
            "type": p["type"],
            "title": p["title"],
            "developer": p["developer"],
            "district": p["district"],
            "city": "Дубай",
            "priceUsd": round(p["price_aed"] / AED),
            "sizeSqm": round(p["size_sqft"] * SQFT_TO_SQM),
            "bedrooms": p["bedrooms"],
            "handover": p["handover"],
            "images": urls,
            "featured": False,
            "shortDescription": p["short"],
            "highlights": p["highlights"],
            "priceFrom": True,
            "sizeFrom": True,
            "paymentPlan": p["plan"],
            "lat": None,
            "lng": None,
            "address": f"{p['district']}, Дубай",
        }

        if p["slug"] in by_slug:
            listings[by_slug[p["slug"]]] = item
            updated += 1
        else:
            listings.append(item)
            added += 1

    json.dump(listings, open(os.path.join(ROOT, "listings.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"added {added}, updated {updated}, images copied {imgs}")
    print(f"listings now: {len(listings)}")
    missing = [p["slug"] for p in P if not p["handover"]]
    if missing:
        print("no handover date published for: " + ", ".join(missing))
    print("NOTE: lat/lng not set — pins must be verified before they render on the map")


if __name__ == "__main__":
    main()
