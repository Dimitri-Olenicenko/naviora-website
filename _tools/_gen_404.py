# -*- coding: utf-8 -*-
"""Generate 404.html — the fallback that makes NEW backoffice listings work.

GitHub Pages serves 404.html for any path with no file. When the backoffice
publishes a brand-new listing, its grid card appears immediately (grids read
listings.json at runtime) but its detail URL has no static page until the
next generation run — it used to dead-end.

This 404 checks whether the path looks like /country/purpose/slug/, fetches
the live listings.json, and if the slug exists renders the full v2 detail
page client-side with the same shared renderer every real page uses. Only
when the slug genuinely does not exist does it show a not-found message.

The page keeps the honest 404 status code, which is correct: the moment the
static generator next runs, the real 200 page takes over.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _template_v2 import CSS, BASE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>NAVIORA GROUP</title>
<style>{CSS}</style>
</head>
<body data-nv-slug="" data-nv-fp="">
<div class="nv-top"><div class="nv-wrap"><nav class="nv-crumb">
<a href="{BASE}/">Главная</a> <span id="nv-crumb-tail"></span>
</nav></div></div>

<div id="nv-hero-zone"></div>

<div class="nv-wrap">
<header class="nv-head" id="nv-head">
  <h1 id="nv-404-msg" style="font-size:1.5rem">Загружаем объект…</h1>
</header>
<div id="nv-facts-zone"></div>

<div class="nv-grid">
<div id="nv-body"></div>
<aside class="nv-side" id="nv-side-zone" style="display:none"><div class="nv-card">
  <div style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#6b6f76">Цена от</div>
  <div id="nv-side-price" style="font-size:1.7rem;font-weight:600;letter-spacing:-.015em;margin-top:.2rem"></div>
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

<div class="nv-wrap" id="nv-rel-zone"></div>

<footer class="nv-foot"><div class="nv-wrap">
  <strong>NAVIORA GROUP</strong> · Real Estate Through Numbers ·
  <a href="{BASE}/">на главную</a>
</div></footer>

<script src="{BASE}/assets/nv-detail.js" defer></script>
<script>
(function () {{
  var m = location.pathname.match(
    /\\/naviora-website\\/(dubai|abudhabi|armenia|georgia)\\/(residential|commercial)\\/([a-z0-9-]+)\\/?$/);
  function notFound() {{
    document.getElementById('nv-404-msg').textContent = 'Страница не найдена';
    var b = document.getElementById('nv-body');
    b.innerHTML = '<p class="nv-desc">Такого объекта нет или адрес изменился. ' +
      '<a href="{BASE}/" style="color:#0037FF">Вернуться на главную →</a></p>';
  }}
  if (!m) {{ notFound(); return; }}
  fetch('{BASE}/listings.json?ts=' + Date.now(), {{ cache: 'no-store' }})
    .then(function (r) {{ return r.json(); }})
    .then(function (all) {{
      var x = null;
      for (var i = 0; i < all.length; i++)
        if (all[i].slug === m[3]) {{ x = all[i]; break; }}
      if (!x) {{ notFound(); return; }}
      document.getElementById('nv-side-zone').style.display = '';
      var wait = function () {{
        if (window.NVDetail) {{ window.NVDetail.render(x, all); }}
        else setTimeout(wait, 40);
      }};
      wait();
    }})
    .catch(notFound);
}})();
</script>
</body>
</html>
"""


def main():
    out = os.path.join(ROOT, "404.html")
    io.open(out, "w", encoding="utf-8").write(HTML)
    print(f"404.html written ({len(HTML)//1024} KB)")


if __name__ == "__main__":
    main()
