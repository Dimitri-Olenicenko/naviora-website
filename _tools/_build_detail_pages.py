"""
Generate detail pages for listings that have none, and remove the orphaned
pages left behind by deleted listings.

The site's React bundle only knows the routes that existed at build time, so
new listings appear in the grid (which fetches listings.json at runtime) but
their detail pages 404. This writes standalone pages that match the site's
look without depending on the React app: they are plain HTML using the site's
own stylesheet, so they render correctly and survive hydration because there
is no hydration to survive.

Idempotent.
"""
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "/naviora-website"

COUNTRY = {
    "dubai": ("Дубай", "dubai"),
    "abudhabi": ("Абу-Даби", "abudhabi"),
    "armenia": ("Ереван", "armenia"),
    "georgia": ("Тбилиси", "georgia"),
}
PURPOSE = {"residential": "Жилая", "commercial": "Коммерческая"}
TYPE_RU = {"apartment": "Апартаменты", "villa": "Вилла", "office": "Офис",
           "retail": "Ритейл", "townhouse": "Таунхаус"}
MARKET_RU = {"offplan": "Первичный рынок", "secondary": "Вторичный рынок"}


def css_href(sample: str) -> str:
    """Reuse the stylesheet the built site already ships."""
    m = re.search(r'href="([^"]*\.css)"', sample)
    return m.group(1) if m else f"{BASE}/_next/static/css/app.css"


def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def money(n) -> str:
    return f"$ {n:,}".replace(",", " ")


def page(item: dict, css: str) -> str:
    cname, cslug = COUNTRY[item["country"]]
    purpose = PURPOSE.get(item["purpose"], item["purpose"])
    url = f'{BASE}/{cslug}/{item["purpose"]}/{item["slug"]}/'
    imgs = item.get("images") or []

    gallery = ""
    if imgs:
        main = esc(imgs[0])
        thumbs = "".join(
            '<div style="aspect-ratio:4/3;overflow:hidden;background:#eef0f7">'
            f'<img src="{esc(u)}" alt="" loading="lazy" '
            'style="width:100%;height:100%;object-fit:cover;cursor:pointer" '
            'onclick="document.getElementById(\'nv-main-img\').src=this.src"></div>'
            for u in imgs[1:7]
        )
        gallery = (
            '<div style="margin-bottom:2.5rem">'
            '<div style="aspect-ratio:16/9;overflow:hidden;background:#eef0f7;margin-bottom:.75rem">'
            f'<img id="nv-main-img" src="{main}" alt="{esc(item["title"])}" '
            'style="width:100%;height:100%;object-fit:cover"></div>'
            + (f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));'
               f'gap:.75rem">{thumbs}</div>' if thumbs else "")
            + "</div>"
        )

    specs = [("Площадь", f'от {item["sizeSqm"]} м²' if item.get("sizeSqm") else None),
             ("Спальни", f'{item["bedrooms"]}' if item.get("bedrooms") else None),
             ("Тип объекта", TYPE_RU.get(item.get("type"), item.get("type"))),
             ("Район", item.get("district")),
             ("Застройщик", item.get("developer")),
             ("Сдача", item.get("handover")),
             ("План оплаты", item.get("paymentPlan"))]
    spec_rows = "".join(
        f'<div style="display:flex;justify-content:space-between;gap:1.5rem;padding:.85rem 0;'
        f'border-bottom:1px solid rgba(13,27,42,.08)">'
        f'<dt style="color:#66758a;font-size:.85rem">{esc(k)}</dt>'
        f'<dd style="margin:0;text-align:right;font-weight:600">{esc(v)}</dd></div>'
        for k, v in specs if v)

    hi = "".join(
        f'<li style="display:flex;gap:.75rem;padding:.6rem 0"><span aria-hidden="true" '
        'style="margin-top:.55rem;flex:none;width:7px;height:7px;background:#c9a84c"></span>'
        f'<span style="color:rgba(13,27,42,.8)">{esc(h)}</span></li>'
        for h in (item.get("highlights") or []))

    deck = ""
    if item.get("pdfUrl"):
        deck = (
            '<section style="margin-top:2.5rem">'
            '<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:1rem">'
            '<span style="font-size:.72rem;letter-spacing:.16em;color:#8a6e2a;font-weight:700">05</span>'
            '<h2 style="font-size:1.25rem;margin:0">Презентация</h2></div>'
            f'<a href="{esc(item["pdfUrl"])}" target="_blank" rel="noopener noreferrer" '
            'style="display:inline-flex;align-items:center;gap:.5rem;border-bottom:1px solid #c9a84c;'
            'padding-bottom:2px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;'
            'font-size:.82rem;color:#8a6e2a;text-decoration:none">Скачать презентацию — PDF →</a>'
            '</section>')

    ld = {
        "@context": "https://schema.org", "@type": "RealEstateListing",
        "name": item["title"], "url": f"https://olenicenko.com{url}",
        "description": item.get("shortDescription", ""),
    }
    if item.get("priceUsd"):
        ld["offers"] = {"@type": "Offer", "price": item["priceUsd"],
                        "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock"}
    if item.get("lat") and item.get("lng"):
        ld["geo"] = {"@type": "GeoCoordinates",
                     "latitude": item["lat"], "longitude": item["lng"]}

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(item['title'])} — {esc(item.get('district',''))}, {esc(cname)} | Naviora Group</title>
<meta name="description" content="{esc((item.get('shortDescription') or '')[:180])}">
<link rel="canonical" href="https://olenicenko.com{url}">
<link rel="icon" href="{BASE}/favicon.png">
<link rel="stylesheet" href="{css}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
body{{margin:0;background:#fff;color:#0d1b2a;
 font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 line-height:1.6;-webkit-font-smoothing:antialiased}}
.nv-wrap{{max-width:1120px;margin:0 auto;padding:0 1.5rem}}
.nv-top{{border-bottom:1px solid rgba(13,27,42,.1);background:#f8f6f1}}
.nv-crumb{{font-size:.75rem;color:#66758a;padding:.85rem 0}}
.nv-crumb a{{color:#66758a;text-decoration:none}}
.nv-crumb a:hover{{color:#8a6e2a}}
.nv-grid{{display:grid;grid-template-columns:1fr;gap:2.5rem;padding:2.5rem 0 4rem}}
@media(min-width:960px){{.nv-grid{{grid-template-columns:1fr 340px}}}}
.nv-side{{align-self:start}}
@media(min-width:960px){{.nv-side{{position:sticky;top:1.5rem}}}}
.nv-card{{border:1px solid rgba(13,27,42,.1);padding:1.5rem;background:#fff}}
.nv-badge{{display:inline-block;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;
 font-weight:700;color:#8a6e2a;background:rgba(201,168,76,.12);padding:.25rem .5rem}}
h1{{font-size:clamp(1.6rem,3.4vw,2.4rem);line-height:1.15;margin:.75rem 0 .4rem;letter-spacing:-.02em}}
.nv-price{{font-size:1.9rem;font-weight:700;letter-spacing:-.02em}}
.nv-sec{{margin-top:2.5rem}}
.nv-sec h2{{font-size:1.25rem;margin:0}}
.nv-eyebrow{{font-size:.72rem;letter-spacing:.16em;color:#8a6e2a;font-weight:700}}
.nv-btn{{display:block;text-align:center;background:#c9a84c;color:#0d1b2a;font-weight:700;
 text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;padding:.9rem;text-decoration:none;
 margin-top:1rem}}
.nv-btn:hover{{background:#e4c97a}}
.nv-foot{{border-top:1px solid rgba(13,27,42,.1);background:#0d1b2a;color:#f8f6f1;
 padding:2rem 0;margin-top:3rem;font-size:.85rem}}
.nv-foot a{{color:#c9a84c}}
</style>
</head>
<body>
<div class="nv-top"><div class="nv-wrap"><nav class="nv-crumb">
<a href="{BASE}/">Главная</a> / <a href="{BASE}/{cslug}/{item['purpose']}/">{esc(cname)}</a>
 / <a href="{BASE}/{cslug}/{item['purpose']}/">{esc(purpose)}</a> / {esc(item['title'])}
</nav></div></div>

<main class="nv-wrap"><div class="nv-grid">
<div>
  <span class="nv-badge">{esc(MARKET_RU.get(item.get('market'), ''))}</span>
  <h1>{esc(item['title'])}</h1>
  <p style="color:#66758a;margin:0 0 1.5rem">{esc(item.get('district',''))}, {esc(cname)}</p>
  {gallery}
  <section class="nv-sec">
    <div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:1rem">
      <span class="nv-eyebrow">01</span><h2>Характеристики</h2></div>
    <dl style="margin:0">{spec_rows}</dl>
  </section>
  <section class="nv-sec">
    <div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:1rem">
      <span class="nv-eyebrow">02</span><h2>Описание</h2></div>
    <p style="color:rgba(13,27,42,.8)">{esc(item.get('shortDescription',''))}</p>
  </section>
  {'<section class="nv-sec"><div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:1rem"><span class="nv-eyebrow">03</span><h2>Преимущества</h2></div><ul style="list-style:none;padding:0;margin:0">' + hi + '</ul></section>' if hi else ''}
  {deck}
</div>
<aside class="nv-side"><div class="nv-card">
  <div style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#66758a">Цена от</div>
  <div class="nv-price">{money(item.get('priceUsd', 0))}</div>
  <p style="font-size:.85rem;color:#66758a;margin:.75rem 0 0">
    Пришлём полные материалы, актуальные планировки и условия оплаты.</p>
  <a class="nv-btn" href="{BASE}/contacts/">Запросить подборку</a>
  <div style="margin-top:1.25rem;font-size:.85rem;color:#66758a">
    <div>Телефон</div>
    <a href="tel:+971547928468" style="color:#0d1b2a;text-decoration:none">+971 547 928 468</a>
    <div style="margin-top:.75rem">Почта</div>
    <a href="mailto:info@naviora.group" style="color:#0d1b2a;text-decoration:none">info@naviora.group</a>
  </div>
</div></aside>
</div></main>

<footer class="nv-foot"><div class="nv-wrap">
  <strong>NAVIORA GROUP</strong> · Real Estate Through Numbers<br>
  <a href="{BASE}/{cslug}/{item['purpose']}/">← Все объекты: {esc(cname)}, {esc(purpose).lower()}</a>
</div></footer>
</body>
</html>
"""


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"), encoding="utf-8"))
    slugs = {x["slug"] for x in listings}

    # sample an existing page for the stylesheet path
    css = f"{BASE}/_next/static/css/app.css"
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "_tools", "assets", "projects")]
        if "index.html" in fn and dp.count(os.sep) >= 3:
            css = css_href(open(os.path.join(dp, "index.html"),
                                encoding="utf-8", errors="replace").read())
            break

    made = removed = 0
    for item in listings:
        _, cslug = COUNTRY[item["country"]]
        d = os.path.join(ROOT, cslug, item["purpose"], item["slug"])
        f = os.path.join(d, "index.html")
        if os.path.exists(f):
            continue          # keep the app's own pages
        os.makedirs(d, exist_ok=True)
        open(f, "w", encoding="utf-8").write(page(item, css))
        print(f"  + {cslug}/{item['purpose']}/{item['slug']}")
        made += 1

    # remove pages whose listing no longer exists
    for country, (_, cslug) in COUNTRY.items():
        for purpose in ("residential", "commercial"):
            base = os.path.join(ROOT, cslug, purpose)
            if not os.path.isdir(base):
                continue
            for name in os.listdir(base):
                d = os.path.join(base, name)
                if os.path.isdir(d) and name not in slugs:
                    shutil.rmtree(d)
                    print(f"  - orphan removed: {cslug}/{purpose}/{name}")
                    removed += 1

    print(f"\npages created {made}, orphans removed {removed}")


if __name__ == "__main__":
    main()
