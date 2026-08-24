"""Add a finance/ROI block and a location block to every listing page.

Two page types exist and both are covered here:
  - 28 pages this toolchain generates (they carry the nv-generated marker)
  - 10 pages Next.js exported, whose React content is rebuilt on hydration

For the exported pages nothing can be written into the HTML — React discards
it — so the blocks are built by a script that runs after hydration and
re-inserts them if React re-renders. That is the same approach already used
for the VR video/deck sections, and it is the only one that survives here.

Nothing existing is removed. The blocks are appended after the last content
section, before "Похожие объекты" where that exists.

On the numbers: no yield, rent or service charge is invented. The facts row
shows only what the listing publishes (price, price per m², payment plan,
handover). The calculator derives income from the *visitor's own* assumed
rate against our real price, and says so — an honest computation from a
stated assumption, not a claim about the asset. Where a developer has
actually published a yield we show it and label it as theirs.

Idempotent.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COUNTRY_SLUG = {"dubai": "dubai", "abudhabi": "abudhabi",
                "armenia": "armenia", "georgia": "georgia"}
MARK = "nv-finance-block"

STYLE = """<style id="nv-fin-style">
.nv-fin-sec{margin-top:3rem}
.nv-fin-head{display:flex;align-items:baseline;gap:1rem;margin-bottom:1.25rem}
.nv-fin-num{font-size:.72rem;letter-spacing:.16em;color:#0037FF;font-weight:700}
.nv-fin-h{font-size:1.25rem;margin:0;font-weight:600;letter-spacing:.02em;text-transform:uppercase}
.nv-fin-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
 gap:1px;background:rgba(20,20,20,.12);border:1px solid rgba(20,20,20,.12)}
.nv-fin-cell{background:#fff;padding:1.15rem 1.25rem}
.nv-fin-cell span{display:block;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
 color:#6b6f76;margin-bottom:.45rem}
.nv-fin-cell b{font-size:1.15rem;font-weight:600;letter-spacing:-.01em;color:#141414}
.nv-fin-cell.is-accent b{color:#0037FF}
.nv-calc{margin-top:1.25rem;border:1px solid rgba(20,20,20,.12);padding:1.5rem;background:#FAFAF9}
.nv-calc-t{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:#6b6f76;
 margin-bottom:1rem;font-weight:700}
.nv-calc-in{display:flex;flex-wrap:wrap;gap:1.25rem;margin-bottom:1.25rem}
.nv-calc-in label{font-size:.8rem;color:#6b6f76;display:flex;flex-direction:column;gap:.4rem}
.nv-calc-in input{width:120px;padding:.6rem .7rem;border:1px solid rgba(20,20,20,.2);
 font-size:1rem;font-weight:600;color:#141414;background:#fff}
.nv-calc-in input:focus{outline:2px solid #0037FF;outline-offset:1px}
.nv-calc-out{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;
 padding-top:1.25rem;border-top:1px solid rgba(20,20,20,.12)}
.nv-calc-out div span{display:block;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;
 color:#6b6f76;margin-bottom:.35rem}
.nv-calc-out div b{font-size:1.3rem;font-weight:600;color:#0037FF;letter-spacing:-.01em}
.nv-note{font-size:.78rem;line-height:1.5;color:#6b6f76;margin:1.1rem 0 0}
.nv-loc-map{width:100%;height:340px;border:1px solid rgba(20,20,20,.12);display:block}
.nv-loc-foot{font-size:.85rem;color:#6b6f76;margin:.8rem 0 0}
.nv-loc-foot a{color:#0037FF;text-decoration:none;font-weight:600}
.nv-rel-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2rem}
.nv-rel{text-decoration:none;color:inherit;border:1px solid rgba(20,20,20,.12);
 display:flex;flex-direction:column;transition:transform .2s ease,border-color .2s ease}
.nv-rel:hover{transform:translateY(-2px);border-color:rgba(20,20,20,.3)}
.nv-rel-i{aspect-ratio:4/3;overflow:hidden;background:#f2f2f0}
.nv-rel-i img{width:100%;height:100%;object-fit:cover;display:block;
 transition:transform .7s cubic-bezier(.16,1,.3,1)}
.nv-rel:hover .nv-rel-i img{transform:scale(1.03)}
.nv-rel-b{padding:1rem 1.1rem 1.2rem}
.nv-rel-t{font-weight:600;font-size:.98rem;line-height:1.3;margin-bottom:.3rem;color:#141414}
.nv-rel-d{font-size:.8rem;color:#6b6f76;margin-bottom:.6rem}
.nv-rel-p{font-size:1.05rem;font-weight:600;color:#141414}
@media(max-width:640px){.nv-calc-in input{width:100%}.nv-calc-in label{flex:1 1 100%}
 }
</style>"""

SCRIPT = """<script id="nv-finance-block">
(function () {
  var D = __NV_DATA__;
  if (!D) return;

  function money(n) {
    return '$ ' + Math.round(n).toLocaleString('ru-RU').replace(/\\u00a0/g, ' ');
  }

  // What this listing should show, given its data. Used as the guard so
  // build() is a no-op once the sections exist — including for a listing
  // with no price, which gets the map only.
  function present() {
    var ok = true;
    if (D.price && !document.getElementById('nv-fin-sec')) ok = false;
    if (D.lat && D.lng && !document.getElementById('nv-loc-sec')) ok = false;
    if (D.similar && D.similar.length && !document.getElementById('nv-rel-sec')) ok = false;
    return ok;
  }

  function cell(label, value, accent) {
    return '<div class="nv-fin-cell' + (accent ? ' is-accent' : '') + '"><span>' +
      label + '</span><b>' + value + '</b></div>';
  }

  function build() {
    var host = document.querySelector('main') || document.body;
    if (!host) return;
    if (present()) return;

    // Anchor: insert before "Похожие объекты" if the page has it, else append.
    var rel = null;
    var heads = host.querySelectorAll('h2');
    for (var i = 0; i < heads.length; i++) {
      if (/похожие/i.test(heads[i].textContent || '')) {
        rel = heads[i].closest('section') || heads[i].parentElement;
        break;
      }
    }

    var html = '';

    if (D.price) {
      var facts = cell('Цена', money(D.price));
      if (D.sqm) facts += cell('Цена за м²', money(D.price / D.sqm), true);
      if (D.plan) facts += cell('План оплаты', D.plan);
      if (D.handover) facts += cell('Срок сдачи', D.handover);
      if (D.yield) {
        facts += cell('Доходность застройщика', D.yield + '%', true);
        facts += cell('Доход в год при этой ставке', money(D.price * D.yield / 100), true);
      }

      html +=
        '<section class="nv-fin-sec" id="nv-fin-sec">' +
        '<div class="nv-fin-head"><span class="nv-fin-num">05</span>' +
        '<h2 class="nv-fin-h">Финансы и доходность</h2></div>' +
        '<div class="nv-fin-grid">' + facts + '</div>' +
        '<div class="nv-calc">' +
        '<div class="nv-calc-t">Калькулятор доходности</div>' +
        '<div class="nv-calc-in">' +
        '<label>Ставка аренды, % годовых<input id="nv-y" type="number" value="' +
          (D.yield || 7) + '" min="1" max="20" step="0.5"></label>' +
        '<label>Загрузка, %<input id="nv-o" type="number" value="90" min="10" max="100" step="5"></label>' +
        '</div><div class="nv-calc-out">' +
        '<div><span>Доход в год</span><b id="nv-a">—</b></div>' +
        '<div><span>Доход в месяц</span><b id="nv-m">—</b></div>' +
        '<div><span>Окупаемость</span><b id="nv-p">—</b></div>' +
        '</div><p class="nv-note">Расчёт строится от указанной вами ставки и ' +
        'цены объекта (' + money(D.price) + '). Это не гарантия доходности и не ' +
        'оферта: фактическая аренда зависит от рынка, отделки, загрузки и ' +
        'сервисных сборов.</p></div></section>';
    }

    if (D.lat && D.lng) {
      var d = 0.004;
      var bbox = (D.lng - d) + ',' + (D.lat - d / 2) + ',' + (D.lng + d) + ',' + (D.lat + d / 2);
      html +=
        '<section class="nv-fin-sec" id="nv-loc-sec">' +
        '<div class="nv-fin-head"><span class="nv-fin-num">06</span>' +
        '<h2 class="nv-fin-h">Расположение</h2></div>' +
        '<iframe class="nv-loc-map" loading="lazy" title="Карта объекта" src="' +
        'https://www.openstreetmap.org/export/embed.html?bbox=' + bbox +
        '&layer=mapnik&marker=' + D.lat + ',' + D.lng + '"></iframe>' +
        '<p class="nv-loc-foot">' + (D.address || '') +
        ' · <a href="https://www.google.com/maps/search/?api=1&query=' +
        D.lat + ',' + D.lng + '" target="_blank" rel="noopener noreferrer">' +
        'Открыть в Google Maps →</a></p></section>';
    }

    // Similar listings. Same country and purpose keeps them comparable
    // rather than merely filling the space.
    if (D.similar && D.similar.length && !document.getElementById('nv-rel-sec')) {
      var cards = '';
      for (var s = 0; s < D.similar.length; s++) {
        var r = D.similar[s];
        cards +=
          '<a class="nv-rel" href="' + r.href + '">' +
          '<div class="nv-rel-i"><img src="' + r.img + '" alt="" loading="lazy"></div>' +
          '<div class="nv-rel-b"><div class="nv-rel-t">' + r.title + '</div>' +
          '<div class="nv-rel-d">' + (r.district || '') + '</div>' +
          '<div class="nv-rel-p">' + (r.price ? money(r.price) : 'Цена по запросу') +
          '</div></div></a>';
      }
      html +=
        '<section class="nv-fin-sec" id="nv-rel-sec">' +
        '<div class="nv-fin-head"><span class="nv-fin-num">07</span>' +
        '<h2 class="nv-fin-h">Похожие объекты</h2></div>' +
        '<div class="nv-rel-grid">' + cards + '</div></section>';
    }

    if (!html) return;   // nothing to add for this listing

    var wrap = document.createElement('div');
    wrap.innerHTML = html;
    var target = rel ? rel.parentElement : host;
    while (wrap.firstChild) {
      if (rel) target.insertBefore(wrap.firstChild, rel);
      else target.appendChild(wrap.firstChild);
    }

    var y = document.getElementById('nv-y');
    var o = document.getElementById('nv-o');
    if (!y) return;

    function calc() {
      var rate = parseFloat(y.value) || 0;
      var occ = (parseFloat(o.value) || 0) / 100;
      var annual = D.price * (rate / 100) * occ;
      document.getElementById('nv-a').textContent = annual ? money(annual) : '—';
      document.getElementById('nv-m').textContent = annual ? money(annual / 12) : '—';
      document.getElementById('nv-p').textContent =
        annual ? (D.price / annual).toFixed(1) + ' лет' : '—';
    }
    y.addEventListener('input', calc);
    o.addEventListener('input', calc);
    calc();
  }

  build();
  // React rebuilds its tree on hydration and can re-render later; re-insert
  // if our section disappears.
  // React rebuilds its tree after hydration on the exported pages and
  // takes our sections with it, so watch and re-insert. present() makes
  // this safe: once the sections are back the callback does nothing, so
  // our own insertion cannot retrigger it.
  var pending = false;
  new MutationObserver(function () {
    if (pending || present()) return;
    pending = true;
    requestAnimationFrame(function () { pending = false; build(); });
  }).observe(document.body, { childList: true, subtree: true });
})();
</script>"""


def main():
    listings = json.load(open(os.path.join(ROOT, "listings.json"),
                              encoding="utf-8"))
    done = skipped = 0

    for x in listings:
        cslug = COUNTRY_SLUG[x["country"]]
        path = os.path.join(ROOT, cslug, x["purpose"], x["slug"], "index.html")
        if not os.path.isfile(path):
            continue

        # Up to three comparable listings: same country and purpose first,
        # widening to same country only if that pool is empty. Listings with
        # no image are skipped — a card with an empty frame looks broken.
        pool = [y for y in listings
                if y["slug"] != x["slug"] and y["country"] == x["country"]
                and y["purpose"] == x["purpose"] and y.get("images")]
        if not pool:
            pool = [y for y in listings
                    if y["slug"] != x["slug"] and y["country"] == x["country"]
                    and y.get("images")]
        similar = [{
            "href": f'/naviora-website/{COUNTRY_SLUG[y["country"]]}/'
                    f'{y["purpose"]}/{y["slug"]}/',
            "img": y["images"][0],
            "title": y["title"],
            "district": y.get("district"),
            "price": y.get("priceUsd"),
        } for y in pool[:3]]

        data = {
            "base": "/naviora-website",
            "similar": similar,
            "price": x.get("priceUsd"),
            "sqm": x.get("sizeSqm"),
            "plan": x.get("paymentPlan"),
            "handover": x.get("handover"),
            "yield": x.get("yieldPct"),
            "lat": x.get("lat"),
            "lng": x.get("lng"),
            "address": x.get("address") or x.get("district"),
        }
        if not (data["price"] or data["lat"] or data["similar"]):
            skipped += 1
            continue

        html = open(path, encoding="utf-8", errors="replace").read()

        # Drop any previous copy so re-running replaces rather than stacks.
        import re
        html = re.sub(r'<style id="nv-fin-style">.*?</style>', "", html, flags=re.S)
        html = re.sub(r'<script id="nv-finance-block">.*?</script>', "", html, flags=re.S)

        payload = STYLE + SCRIPT.replace(
            "__NV_DATA__", json.dumps(data, ensure_ascii=False))
        html = html.replace("</body>", payload + "\n</body>", 1)
        open(path, "w", encoding="utf-8").write(html)
        done += 1

    print(f"pages with finance/location blocks: {done}")
    print(f"skipped (no price and no pin): {skipped}")


if __name__ == "__main__":
    main()
