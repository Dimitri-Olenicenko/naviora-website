# -*- coding: utf-8 -*-
"""Detail-page template v2 — the structure the design research recommends.

What changes against v1, each tied to a measured finding:

  - FULL-BLEED HERO. v1 boxed the lead image inside a grid column: measured
    692x389 in a 1440 viewport — 48% width. Every premium reference lets the
    image carry the page (Luxhabitat's detail hero measures 1152x732;
    Christie's runs 1440x500 full-bleed). The hero is now edge-to-edge with a
    thumbnail film-strip under it.
  - LOCATION-FIRST HEADER. Luxury platforms lead with place, hold the price
    quiet (Savills sets price 28px w400). v1 put the badge first and the
    district under the title; v2 goes eyebrow(location) -> title -> price row.
  - KEY-FACTS BAND. v1 buried specs mid-page as narrow <dl> rows — the
    spreadsheet look the research warns about. v2 puts a scannable cell band
    directly under the header, same visual grammar as the finance grid.
  - ONE HEADING LANGUAGE. v1 mixed sentence-case template headings with the
    injector's uppercase ones. v2 uses the site's own convention throughout
    (numbered eyebrow + uppercase, as the Next.js pages do).
  - FINANCE, MAP AND SIMILAR ARE NATIVE, in a deliberate order — finance
    right after the property story, not appended after the documents by a
    script. The blocks reuse the injector's element ids (#nv-fin-sec,
    #nv-loc-sec, #nv-rel-sec), so the runtime injector sees them present and
    correctly does nothing.
  - AIR. Section gap 3.5rem/56px against v1's 2.5rem — the Luxhabitat rhythm.

Colours are strictly the site's own: signal #0037FF, ink #141414, the
existing muted grey and hairline. No palette change — structure only.
"""
import html as _html
import json


def esc(s):
    return _html.escape(str(s or ""), quote=True)


def fingerprint(item):
    """djb2 over the compact JSON, bit-identical to fp() in nv-detail.js.

    The baked page carries this on <body>; the runtime sync recomputes it
    against the live listings.json and redraws only when they differ. A
    false mismatch is harmless — it just re-renders identical markup — so a
    best-effort match with JSON.stringify is sufficient.
    """
    s = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
    h = 5381
    for ch in s:
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    if h >= 2 ** 31:
        h -= 2 ** 32
    return str(h)


def money(n):
    if not n:
        return "Цена по запросу"
    return f"$ {n:,}".replace(",", " ")


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
BASE = "/naviora-website"
MARKER = "<!-- nv-generated-detail-page -->"

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#141414;
 font-family:'Gerbera','Suisse Intl','Helvetica Neue','Segoe UI',Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
.nv-wrap{max-width:1200px;margin:0 auto;padding:0 1.5rem}
.nv-top{border-bottom:1px solid rgba(20,20,20,.1);padding:.8rem 0;font-size:.8rem}
.nv-crumb a{color:#6b6f76;text-decoration:none}
.nv-crumb a:hover{color:#0037FF}

/* full-bleed hero */
.nv-hero{position:relative;width:100%;background:#f2f2f0}
.nv-hero img{display:block;width:100%;height:clamp(340px,56vh,640px);object-fit:cover}
.nv-film{display:flex;gap:.5rem;overflow-x:auto;padding:.6rem 1.5rem;
 max-width:1200px;margin:0 auto;scrollbar-width:thin}
.nv-film img{height:72px;width:104px;object-fit:cover;cursor:pointer;flex:none;
 opacity:.75;transition:opacity .2s ease;border:2px solid transparent}
.nv-film img:hover{opacity:1}
.nv-film img.is-on{opacity:1;border-color:#0037FF}

/* header block — location first, price quiet */
.nv-head{padding:2.2rem 0 0}
.nv-eyeloc{font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;
 color:#6b6f76;display:flex;flex-wrap:wrap;align-items:center;gap:.6rem}
.nv-chip{background:rgba(0,55,255,.08);color:#0037FF;font-weight:700;
 padding:.2rem .55rem;letter-spacing:.1em}
h1{font-size:clamp(1.8rem,3.6vw,2.6rem);line-height:1.12;margin:.55rem 0 .7rem;
 letter-spacing:-.02em}
.nv-price-row{display:flex;flex-wrap:wrap;align-items:baseline;gap:1rem}
.nv-price{font-size:2rem;font-weight:500;letter-spacing:-.015em}
.nv-price small{font-size:1rem;color:#6b6f76;font-weight:400}
.nv-psm{color:#6b6f76;font-size:1rem}

/* key facts band */
.nv-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
 border:1px solid rgba(20,20,20,.12);margin:1.8rem 0 0}
.nv-facts>div{background:#fff;padding:1rem 1.1rem;
 box-shadow:-1px -1px 0 0 rgba(20,20,20,.12)}
.nv-facts span{display:block;font-size:.68rem;letter-spacing:.13em;
 text-transform:uppercase;color:#6b6f76;margin-bottom:.4rem}
.nv-facts b{font-size:1.05rem;font-weight:600;letter-spacing:-.01em}

/* layout */
.nv-grid{display:grid;grid-template-columns:minmax(0,1fr);gap:2.5rem;padding:2.5rem 0 0}
@media(min-width:960px){.nv-grid{grid-template-columns:minmax(0,1fr) 340px;gap:3.5rem}}
.nv-side{align-self:start}
@media(min-width:960px){.nv-side{position:sticky;top:1.5rem}}
.nv-card{border:1px solid rgba(20,20,20,.12);padding:1.5rem;background:#fff}
.nv-btn{display:block;text-align:center;background:#0037FF;color:#fff;font-weight:700;
 text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;padding:.95rem;
 text-decoration:none;margin-top:1.1rem}
.nv-btn:hover{background:#2a5bff}

/* sections — the site's own heading grammar */
.nv-sec{margin-top:3.5rem}
.s-head{display:flex;align-items:baseline;gap:1rem;margin-bottom:1.25rem}
.s-num{font-size:.72rem;letter-spacing:.16em;color:#0037FF;font-weight:700}
.s-head h2{font-size:1.15rem;margin:0;font-weight:600;letter-spacing:.06em;
 text-transform:uppercase}
.nv-desc{color:rgba(20,20,20,.78);line-height:1.7;max-width:64ch}

.nv-hl{list-style:none;padding:0;margin:0;display:grid;
 grid-template-columns:1fr;gap:.1rem}
@media(min-width:720px){.nv-hl{grid-template-columns:1fr 1fr;column-gap:2.5rem}}
.nv-hl li{display:flex;gap:.75rem;padding:.55rem 0;color:rgba(20,20,20,.78)}
.nv-hl li::before{content:"";margin-top:.5rem;flex:none;width:7px;height:7px;
 background:#0037FF}

/* finance */
.nv-fin-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
 border:1px solid rgba(20,20,20,.12)}
.nv-fin-cell{background:#fff;padding:1.1rem 1.2rem;
 box-shadow:-1px -1px 0 0 rgba(20,20,20,.12)}
.nv-fin-cell span{display:block;font-size:.68rem;letter-spacing:.13em;
 text-transform:uppercase;color:#6b6f76;margin-bottom:.42rem}
.nv-fin-cell b{font-size:1.1rem;font-weight:600;letter-spacing:-.01em}
.nv-fin-cell.is-accent b{color:#0037FF}
.nv-fin-wide{grid-column:1/-1}
.nv-fin-wide b{font-size:.98rem;font-weight:500;line-height:1.55}
.nv-calc{margin-top:1.25rem;border:1px solid rgba(20,20,20,.12);padding:1.5rem;
 background:#FAFAF9}
.nv-calc-t{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;
 color:#6b6f76;margin-bottom:1rem;font-weight:700}
.nv-calc-in{display:flex;flex-wrap:wrap;gap:1.25rem;margin-bottom:1.25rem}
.nv-calc-in label{font-size:.8rem;color:#6b6f76;display:flex;flex-direction:column;gap:.4rem}
.nv-calc-in input{width:120px;min-height:44px;padding:.6rem .7rem;
 border:1px solid rgba(20,20,20,.2);
 font-size:1rem;font-weight:600;color:#141414;background:#fff}
.nv-calc-in input:focus{outline:2px solid #0037FF;outline-offset:1px}
.nv-calc-out{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
 gap:1rem;padding-top:1.25rem;border-top:1px solid rgba(20,20,20,.12)}
.nv-calc-out span{display:block;font-size:.68rem;letter-spacing:.12em;
 text-transform:uppercase;color:#6b6f76;margin-bottom:.35rem}
.nv-calc-out b{font-size:1.3rem;font-weight:600;color:#0037FF;letter-spacing:-.01em}
.nv-note{font-size:.78rem;line-height:1.5;color:#6b6f76;margin:1.1rem 0 0}

/* video facade */
.nv-yt{position:relative;width:100%;padding-top:56.25%;cursor:pointer;
 background:#141414;overflow:hidden}
.nv-yt img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.85}
.nv-yt .play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
 width:68px;height:48px;background:#0037FF;border-radius:10px;
 display:flex;align-items:center;justify-content:center}
.nv-yt .play span{border-left:18px solid #fff;border-top:11px solid transparent;
 border-bottom:11px solid transparent;margin-left:4px}

.nv-doc a{display:inline-flex;align-items:center;gap:.5rem;
 border-bottom:1px solid #0037FF;padding-bottom:2px;font-weight:600;
 text-transform:uppercase;letter-spacing:.06em;font-size:.82rem;color:#0037FF;
 text-decoration:none}

.nv-map{width:100%;height:360px;border:1px solid rgba(20,20,20,.12);display:block}
.nv-loc-foot{font-size:.85rem;color:#6b6f76;margin:.8rem 0 0}
.nv-loc-foot a{color:#0037FF;text-decoration:none;font-weight:600}

/* similar */
.nv-rel-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2rem}
.nv-rel{text-decoration:none;color:inherit;border:1px solid rgba(20,20,20,.12);
 display:flex;flex-direction:column;transition:transform .2s ease,border-color .2s ease}
.nv-rel:hover{transform:translateY(-2px);border-color:rgba(20,20,20,.3)}
.nv-rel-i{aspect-ratio:4/3;overflow:hidden;background:#f2f2f0}
.nv-rel-i img{width:100%;height:100%;object-fit:cover;display:block;
 transition:transform .7s cubic-bezier(.16,1,.3,1)}
.nv-rel:hover .nv-rel-i img{transform:scale(1.03)}
.nv-rel-b{padding:1rem 1.1rem 1.2rem}
.nv-rel-t{font-weight:600;font-size:.98rem;line-height:1.3;margin-bottom:.3rem}
.nv-rel-d{font-size:.8rem;color:#6b6f76;margin-bottom:.6rem}
.nv-rel-p{font-size:1.05rem;font-weight:600}


/* Site chrome. Opening a listing used to drop the header and footer entirely
   — no logo, no navigation, no way back. Rebuilt as static markup styled to
   match the grid pages. The React header's country dropdown is a JS widget,
   so it becomes plain links to the same destinations. */
.nv-site-head{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.95);
 backdrop-filter:blur(8px);border-bottom:1px solid rgba(20,20,20,.1)}
.nv-site-wrap{max-width:1200px;margin:0 auto;padding:0 1.5rem;
 display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:64px}
.nv-logo{display:flex;align-items:center;gap:.5rem;text-decoration:none;color:#141414;
 font-weight:700;letter-spacing:.06em;font-size:.95rem;white-space:nowrap}
.nv-nav{display:none;gap:1.6rem}
@media(min-width:860px){.nv-nav{display:flex}}
.nv-nav a{color:#141414;text-decoration:none;font-size:.78rem;font-weight:600;
 letter-spacing:.08em;text-transform:uppercase}
.nv-nav a:hover{color:#0037FF}
.nv-head-cta{background:#0037FF;color:#fff;text-decoration:none;font-weight:700;
 font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;
 padding:.75rem 1.1rem;white-space:nowrap;min-height:44px;
 display:inline-flex;align-items:center}
.nv-head-cta:hover{background:#2a5bff}
.nv-site-foot{background:#000032;color:#fff;margin-top:4rem;padding:3rem 0 1.5rem}
.nv-site-foot .nv-site-wrap{display:block}
.nv-foot-grid{display:grid;grid-template-columns:1fr;gap:2rem}
@media(min-width:720px){.nv-foot-grid{grid-template-columns:2fr 1fr 1fr}}
.nv-foot-brand{font-weight:700;letter-spacing:.06em}
.nv-foot-tag{color:rgba(255,255,255,.55);font-size:.85rem;margin:.4rem 0 0}
.nv-foot-h{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
 color:rgba(255,255,255,.5);margin-bottom:.7rem}
.nv-site-foot a{display:block;color:rgba(255,255,255,.85);text-decoration:none;
 font-size:.88rem;padding:.22rem 0}
.nv-site-foot a:hover{color:#8fa8ff}
.nv-foot-btm{border-top:1px solid rgba(255,255,255,.1);margin-top:2.5rem;
 padding-top:1.2rem;font-size:.8rem;color:rgba(255,255,255,.4)}

.nv-foot{border-top:1px solid rgba(20,20,20,.1);background:#141414;color:#fff;
 padding:2rem 0;margin-top:4rem;font-size:.85rem}
.nv-foot a{color:#8fa8ff}
@media (prefers-reduced-motion:reduce){
 .nv-rel,.nv-rel-i img,.nv-film img{transition:none!important;transform:none!important}}
"""


def facts_band(item):
    cells = []
    if item.get("sizeSqm"):
        cells.append(("Площадь", f'от {item["sizeSqm"]} м²'))
    if item.get("bedrooms"):
        cells.append(("Спальни", str(item["bedrooms"])))
    t = TYPE_RU.get(item.get("type"), item.get("type"))
    if t:
        cells.append(("Тип объекта", t))
    if item.get("handover"):
        cells.append(("Сдача", item["handover"]))
    if item.get("developer"):
        cells.append(("Застройщик", item["developer"]))
    if not cells:
        return ""
    inner = "".join(f"<div><span>{esc(k)}</span><b>{esc(v)}</b></div>"
                    for k, v in cells)
    return f'<div class="nv-facts">{inner}</div>'


def sec(num, title, body, sec_id=""):
    idattr = f' id="{sec_id}"' if sec_id else ""
    return (f'<section class="nv-sec"{idattr}><div class="s-head">'
            f'<span class="s-num">{num}</span><h2>{esc(title)}</h2></div>'
            f"{body}</section>")


def finance(item):
    price = item.get("priceUsd")
    if not price:
        return ""
    cells = [("Цена", money(price), False)]
    if item.get("sizeSqm"):
        cells.append(("Цена за м²", money(round(price / item["sizeSqm"])), True))
    y = item.get("yieldPct")
    if y:
        cells.append(("Доходность застройщика", f"{y}%", True))
        cells.append(("Доход в год при этой ставке", money(round(price * y / 100)), True))
    grid = "".join(
        f'<div class="nv-fin-cell{" is-accent" if a else ""}">'
        f"<span>{esc(k)}</span><b>{esc(v)}</b></div>" for k, v, a in cells)
    if item.get("paymentPlan"):
        grid += (f'<div class="nv-fin-cell nv-fin-wide">'
                 f'<span>План оплаты</span><b>{esc(item["paymentPlan"])}</b></div>')
    calc = f"""
<div class="nv-calc"><div class="nv-calc-t">Калькулятор доходности</div>
<div class="nv-calc-in">
<label>Ставка аренды, % годовых
 <input id="nv-y" type="number" value="{y or 7}" min="1" max="20" step="0.5"></label>
<label>Загрузка, %
 <input id="nv-o" type="number" value="90" min="10" max="100" step="5"></label>
</div>
<div class="nv-calc-out">
<div><span>Доход в год</span><b id="nv-a">—</b></div>
<div><span>Доход в месяц</span><b id="nv-m">—</b></div>
<div><span>Окупаемость</span><b id="nv-p">—</b></div>
</div>
<p class="nv-note">Расчёт строится от указанной вами ставки и цены объекта
({money(price)}). Это не гарантия доходности и не оферта: фактическая аренда
зависит от рынка, отделки, загрузки и сервисных сборов.</p></div>"""
    return f'<div class="nv-fin-grid">{grid}</div>{calc}'


def location(item):
    lat, lng = item.get("lat"), item.get("lng")
    if not (lat and lng):
        return ""
    d = 0.004
    bbox = f"{lng-d},{lat-d/2},{lng+d},{lat+d/2}"
    return (
        f'<iframe class="nv-map" loading="lazy" title="Карта: {esc(item["title"])}" '
        f'src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}'
        f'&amp;layer=mapnik&amp;marker={lat},{lng}"></iframe>'
        f'<p class="nv-loc-foot">{esc(item.get("address") or item.get("district") or "")} · '
        f'<a href="https://www.google.com/maps/search/?api=1&amp;query={lat},{lng}" '
        f'target="_blank" rel="noopener noreferrer">Открыть в Google Maps →</a></p>')


def similar(item, listings):
    pool = [x for x in listings
            if x["slug"] != item["slug"] and x["country"] == item["country"]
            and x["purpose"] == item["purpose"] and x.get("images")]
    if not pool:
        pool = [x for x in listings
                if x["slug"] != item["slug"] and x["country"] == item["country"]
                and x.get("images")]
    if not pool:
        return ""
    _, cslug = COUNTRY[item["country"]]
    cards = ""
    for x in pool[:3]:
        href = f'{BASE}/{cslug}/{x["purpose"]}/{x["slug"]}/'
        cards += (
            f'<a class="nv-rel" href="{href}">'
            f'<div class="nv-rel-i"><img src="{esc(x["images"][0])}" alt="" loading="lazy"></div>'
            f'<div class="nv-rel-b"><div class="nv-rel-t">{esc(x["title"])}</div>'
            f'<div class="nv-rel-d">{esc(x.get("district", ""))}</div>'
            f'<div class="nv-rel-p">{money(x.get("priceUsd"))}</div></div></a>')
    return f'<div class="nv-rel-grid">{cards}</div>'


def page_v2(item, listings):
    cname, cslug = COUNTRY[item["country"]]
    purpose = PURPOSE.get(item["purpose"], item["purpose"])
    imgs = item.get("images") or []
    url = f'{BASE}/{cslug}/{item["purpose"]}/{item["slug"]}/'

    hero = ""
    if imgs:
        thumbs = "".join(
            f'<img src="{esc(u)}" alt="" loading="lazy" data-i="{i}"'
            f'{" class=\"is-on\"" if i == 0 else ""}>'
            for i, u in enumerate(imgs[:8]))
        hero = (f'<div class="nv-hero"><img id="nv-main-img" '
                f'src="{esc(imgs[0])}" alt="{esc(item["title"])}"></div>'
                + (f'<div class="nv-film">{thumbs}</div>' if len(imgs) > 1 else ""))

    price = item.get("priceUsd")
    psm = ""
    if price and item.get("sizeSqm"):
        psm = f'<span class="nv-psm">{money(round(price/item["sizeSqm"]))} / м²</span>'
    price_html = (f'<div class="nv-price-row">'
                  f'<div class="nv-price"><small>от</small> {money(price)}</div>{psm}</div>'
                  if price else
                  '<div class="nv-price-row"><div class="nv-price">Цена по запросу</div></div>')

    # numbered sections in reading order
    n = 0
    body = ""

    def nxt():
        nonlocal n
        n += 1
        return f"{n:02d}"

    if item.get("shortDescription"):
        body += sec(nxt(), "Описание",
                    f'<p class="nv-desc">{esc(item["shortDescription"])}</p>')
    hl = item.get("highlights") or []
    if hl:
        lis = "".join(f"<li>{esc(h)}</li>" for h in hl)
        body += sec(nxt(), "Преимущества", f'<ul class="nv-hl">{lis}</ul>')
    fin = finance(item)
    if fin:
        body += sec(nxt(), "Финансы и доходность", fin, "nv-fin-sec")
    vids = item.get("videos") or ([{"id": item["videoId"], "caption": ""}]
                                   if item.get("videoId") else [])
    if vids:
        v = ""
        for vv in vids:
            v += (f'<figure style="margin:0 0 1rem">'
                  f'<div class="nv-yt" data-yt="{esc(vv["id"])}" role="button" tabindex="0" '
                  f'aria-label="Смотреть видео проекта">'
                  f'<img src="https://i.ytimg.com/vi/{esc(vv["id"])}/hqdefault.jpg" alt="" loading="lazy">'
                  f'<span class="play" aria-hidden="true"><span></span></span></div>'
                  + (f'<figcaption style="font-size:.8rem;color:#6b6f76;margin-top:.5rem">'
                     f'{esc(vv["caption"])}</figcaption>' if vv.get("caption") else "")
                  + "</figure>")
        body += sec(nxt(), "Видео проекта", v)
    pdf = item.get("pdfUrl") or item.get("brochure")
    if pdf:
        label = item.get("brochureLabel") or "Скачать презентацию — PDF →"
        heading = "Документы" if item.get("brochureLabel") else "Презентация"
        body += sec(nxt(), heading,
                    f'<div class="nv-doc"><a href="{esc(pdf)}" target="_blank" '
                    f'rel="noopener noreferrer">{esc(label)}</a></div>')
    loc = location(item)
    if loc:
        body += sec(nxt(), "Расположение", loc, "nv-loc-sec")

    rel = similar(item, listings)
    rel_html = ""
    if rel:
        rel_html = sec(nxt(), "Похожие объекты", rel, "nv-rel-sec")

    ld = {"@context": "https://schema.org", "@type": "RealEstateListing",
          "name": item["title"], "url": f"https://olenicenko.com{url}"}
    if price:
        ld["offers"] = {"@type": "Offer", "price": price, "priceCurrency": "USD"}

    script = ('<script src="' + BASE + '/assets/nv-detail.js" defer></script>'
              )

    return f"""<!DOCTYPE html>
{MARKER}
<!-- nv-template-v2 -->
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(item["title"])} — {esc(cname)} | Mark Fingerman</title>
<meta name="description" content="{esc((item.get('shortDescription') or '')[:155])}">
<link rel="canonical" href="https://olenicenko.com{url}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body data-nv-slug="{esc(item['slug'])}" data-nv-fp="{fingerprint(item)}">
<header class="nv-site-head">
  <div class="nv-site-wrap">
    <a class="nv-logo" href="{BASE}/" aria-label="MARK FINGERMAN">
      <svg viewBox="0 0 44 48" fill="#0037FF" width="22" height="24" aria-hidden="true">
        <polygon points="0,48 0,10 14,0 14,38"></polygon>
        <polygon points="30,48 30,10 44,0 44,38"></polygon>
        <polygon points="12,2 24,44 34,44 22,2"></polygon>
      </svg>
      <span>MARK FINGERMAN</span>
    </a>
    <nav class="nv-nav">
      <a href="{BASE}/{cslug}/residential/">Жилая</a>
      <a href="{BASE}/{cslug}/commercial/">Коммерческая</a>
      <a href="{BASE}/contacts/">Контакты</a>
    </nav>
    <a class="nv-head-cta" href="{BASE}/contacts/">Связаться</a>
  </div>
</header>
<div class="nv-top"><div class="nv-wrap"><nav class="nv-crumb">
<a href="{BASE}/">Главная</a> / <a href="{BASE}/{cslug}/{item['purpose']}/">{esc(cname)}</a>
 / <a href="{BASE}/{cslug}/{item['purpose']}/">{esc(purpose)}</a> / {esc(item['title'])}
</nav></div></div>

<div id="nv-hero-zone">{hero}</div>

<div class="nv-wrap">
<header class="nv-head" id="nv-head">
  <p class="nv-eyeloc"><span>{esc(item.get('district',''))} · {esc(cname)}</span>
  <span class="nv-chip">{esc(MARKET_RU.get(item.get('market'), ''))}</span></p>
  <h1>{esc(item['title'])}</h1>
  {price_html}
</header>
<div id="nv-facts-zone">{facts_band(item)}</div>

<div class="nv-grid">
<div id="nv-body">
{body}
</div>
<aside class="nv-side"><div class="nv-card">
  <div style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#6b6f76">Цена от</div>
  <div id="nv-side-price" style="font-size:1.7rem;font-weight:600;letter-spacing:-.015em;margin-top:.2rem">{money(price)}</div>
  <p style="font-size:.85rem;color:#6b6f76;margin:.75rem 0 0">
    Пришлём полные материалы, актуальные планировки и условия оплаты.</p>
  <a class="nv-btn" href="{BASE}/contacts/">Запросить подборку</a>
  <div style="margin-top:1.25rem;font-size:.85rem;color:#6b6f76">
    <div>Телефон</div>
    <a href="tel:+971547928468" style="color:#141414;text-decoration:none">+971 547 928 468</a>
    <div style="margin-top:.75rem">Почта</div>
    <a href="mailto:info@naviora.group" style="color:#141414;text-decoration:none">info@naviora.group</a>
  </div>
</div></aside>
</div>
</div>

<div class="nv-wrap" id="nv-rel-zone">{rel_html}</div>

<footer class="nv-site-foot">
  <div class="nv-site-wrap nv-foot-grid">
    <div>
      <div class="nv-foot-brand">MARK FINGERMAN</div>
      <p class="nv-foot-tag">Real Estate Through Numbers</p>
    </div>
    <div>
      <div class="nv-foot-h">Направления</div>
      <a href="{BASE}/dubai/residential/">Дубай</a>
      <a href="{BASE}/abudhabi/residential/">Абу-Даби</a>
      <a href="{BASE}/armenia/residential/">Ереван</a>
      <a href="{BASE}/georgia/residential/">Тбилиси</a>
    </div>
    <div>
      <div class="nv-foot-h">Контакты</div>
      <a href="tel:+971547928468">+971 547 928 468</a>
      <a href="mailto:info@naviora.group">info@naviora.group</a>
    </div>
  </div>
  <div class="nv-site-wrap nv-foot-btm">© 2026 Mark Fingerman</div>
</footer>
{script}
</body>
</html>
"""
