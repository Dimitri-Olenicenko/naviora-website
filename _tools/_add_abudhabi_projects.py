"""
Add the Abu Dhabi projects to listings.json and copy their images.

Transcribed from the developer-supplied project sheets. Prices are the lowest
published unit price (AED at the 3.6725 peg); sizes the smallest published unit.

Note: Fairmont Marina Residences is COMPLETED (Q2 2021, 100% ready), so it is
marked market="secondary" — the others are off-plan.

Idempotent.
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "projects", "abu dhabi")
DEST = os.path.join(ROOT, "assets", "projects")
AED = 3.6725
SQFT_TO_SQM = 0.092903

P = [
    dict(folder="man apart", slug="manchester-city-yas-residences", purpose="residential",
         type="apartment", title="Manchester City Yas Residences by Ohana",
         developer="Ohana Developments", district="Yas Island", market="offplan",
         price_aed=3150000, size_sqft=1313, bedrooms=2, handover="Q4 2029",
         short="Первое в мире жильё под брендом Manchester City на Yas Island. Набережная "
               "Yas Canal, футбольная академия клуба на территории, более половины площади — "
               "зелёные зоны и wellness.",
         highlights=["Брендированный проект Manchester City",
                     "Академия Manchester City на территории комплекса",
                     "Квартиры, таунхаусы, твин-виллы и виллы 2–5 спален",
                     "Более 50% территории — зелёные зоны и рекреация",
                     "Набережная Yas Canal, кристальная лагуна"],
         plan="10% при бронировании / 30% в ходе строительства / 60% при передаче",
         video="_BIqCNPBkuI"),

    dict(folder="fair month apt", slug="fairmont-marina-residences", purpose="residential",
         type="apartment", title="Fairmont Marina Residences",
         developer="National Investment", district="Al Kasir", market="secondary",
         price_aed=4246232, size_sqft=1520.51, bedrooms=2, handover="Сдан (Q2 2021)",
         short="Брендированные резиденции Fairmont на набережной Персидского залива: башни-"
               "близнецы с аркой, доступ к инфраструктуре курорта Fairmont Marina и привилегии "
               "в 110+ отелях Fairmont, Raffles и Swissôtel.",
         highlights=["Готов — сдан в 2021, 100% готовности",
                     "Меблированные резиденции, кухня в комплекте",
                     "Инфинити-бассейн, спа Willow Stream, теннис",
                     "Привилегии в 110+ отелях Fairmont / Raffles / Swissôtel",
                     "Рассрочка 20/80 на 3 года после передачи"],
         plan="20% при бронировании / 80% в течение 3 лет после передачи (13,33% каждые 6 мес.)"),

    dict(folder="aldar apt", slug="beach-house-fahid", purpose="residential",
         type="apartment", title="The Beach House Fahid", developer="ALDAR",
         district="Fahid Island", market="offplan",
         price_aed=4920508, size_sqft=1474, bedrooms=2, handover="Q3 2029",
         short="Прибрежный комплекс на Fahid Island в нескольких шагах от берега: два "
               "резорт-бассейна, коворкинг-лаунжи, променад Coral Drive с ретейлом и ресторанами.",
         highlights=["Остров Fahid — новая закрытая локация Абу-Даби",
                     "Два резорт-бассейна, два спортзала",
                     "Променад Coral Drive, бутиковый ретейл",
                     "Полуменблированные квартиры, кухня с техникой",
                     "Сервисный сбор 32 AED/кв. фут"],
         plan="10% при бронировании / 30% в ходе строительства / 60% при передаче"),

    dict(folder="sobha apt", slug="river-cove-sobha-city-ad", purpose="residential",
         type="apartment", title="River Cove Residences at Sobha City",
         developer="Sobha", district="Al Bahya", market="offplan",
         price_aed=3942900, size_sqft=1546.24, bedrooms=2, handover="",
         short="Две башни вдоль променада в Sobha City: виды на каналы и озеленение, "
               "панорамное остекление, балконы. Квартиры и дуплексы 1–4 спальни.",
         highlights=["Две башни вдоль набережного променада",
                     "Панорамное остекление от пола до потолка",
                     "Беговые и велодорожки, открытые спортзалы",
                     "Зоны медитации и тай-чи, йога-дек",
                     "Амфитеатр, площадки для детей, общественные лаунжи"],
         plan="20% при бронировании / 40% в ходе строительства (8 платежей) / 40% при передаче"),

    dict(folder="sob villa", slug="the-terraces-sobha-city-ad", purpose="residential",
         type="villa", title="The Terraces at Sobha City", developer="Sobha",
         district="Al Bahya", market="offplan",
         price_aed=5092314, size_sqft=2578, bedrooms=3, handover="Q4 2029",
         short="Садовые виллы в Sobha City: приватные сады, приподнятые террасы, "
               "виды на озеленение и водные элементы. Отдельные виллы с лифтом и бассейном.",
         highlights=["Садовые виллы с приватными садами и террасами",
                     "Отдельные виллы с лифтом, бассейном и крытой парковкой",
                     "Парки, велодорожки, мультиспортивные корты",
                     "Зоны медитации и йоги, амфитеатр",
                     "Сервисный сбор 5 AED/кв. фут"],
         plan="20% при бронировании / 40% в ходе строительства (8 платежей) / 40% при передаче"),

    dict(folder="another villa abu aldar", slug="al-ghadeer-gardens", purpose="residential",
         type="villa", title="Al Ghadeer Gardens", developer="ALDAR",
         district="Al Ghadeer", market="offplan",
         price_aed=3356071, size_sqft=2198, bedrooms=4, handover="Q4 2030",
         short="Виллы и таунхаусы 2–4 спальни на границе Абу-Даби и Дубая: резорт-бассейн, "
               "водная горка, падел-корт, школа на территории комьюнити.",
         highlights=["На границе Абу-Даби и Дубая, рядом Al Maktoum International",
                     "Виллы и таунхаусы 2–4 спальни от 2 198 кв. футов",
                     "Резорт-бассейн, splash pad, водная горка",
                     "Падел-корт, спортплощадки, ивент-лужайка",
                     "Школа и комьюнити-центр со спортзалом на территории"],
         plan="5% при бронировании / 50% в ходе строительства (6 платежей) / 45% при передаче"),
]


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    by_slug = {x["slug"]: i for i, x in enumerate(listings)}
    added = updated = imgs = 0

    for p in P:
        src = os.path.join(SRC, p["folder"])
        if not os.path.isdir(src):
            print(f"  !! folder missing: {p['folder']}")
            continue

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
            "id": f"abudhabi-{p['slug']}",
            "slug": p["slug"],
            "country": "abudhabi",
            "purpose": p["purpose"],
            "market": p["market"],
            "type": p["type"],
            "title": p["title"],
            "developer": p["developer"],
            "district": p["district"],
            "city": "Абу-Даби",
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
            "address": f"{p['district']}, Абу-Даби",
        }

        if p["slug"] in by_slug:
            listings[by_slug[p["slug"]]] = item
            updated += 1
        else:
            listings.append(item)
            added += 1

    json.dump(listings, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"added {added}, updated {updated}, images copied {imgs}")
    print(f"listings now: {len(listings)}")
    no_hand = [p["slug"] for p in P if not p["handover"]]
    if no_hand:
        print("no handover published: " + ", ".join(no_hand))


if __name__ == "__main__":
    main()
