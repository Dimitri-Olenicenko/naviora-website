/* Mark Fingerman detail-page renderer — the single source of section logic.
 *
 * Why this exists: the backoffice worker commits listings.json to GitHub and
 * the site rebuilds, but detail pages used to bake their data in at build
 * time — so an edit in the backoffice showed on the grids and not on the
 * page itself. This renderer draws every dynamic region from the live
 * listings.json, with the baked HTML serving as the no-JS/SEO fallback.
 *
 * Contract (mirrored by _tools/_template_v2.py, which bakes the same output):
 *   sections appear only when their data exists, numbered in order:
 *   Описание → Преимущества → Финансы → Видео → Документы → Расположение
 *   and the Похожие rail below. Add a field in the backoffice, publish, and
 *   the section appears on next load — no rebuild of the page needed.
 */
(function () {
  "use strict";

  var BASE = "/naviora-website";
  var COUNTRY = { dubai: "Дубай", abudhabi: "Абу-Даби", armenia: "Ереван", georgia: "Тбилиси" };
  var PURPOSE = { residential: "Жилая", commercial: "Коммерческая" };
  var TYPE_RU = { apartment: "Апартаменты", villa: "Вилла", office: "Офис", retail: "Ритейл", townhouse: "Таунхаус" };
  var MARKET_RU = { offplan: "Первичный рынок", secondary: "Вторичный рынок" };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function money(n) {
    if (!n) return "Цена по запросу";
    return "$ " + Math.round(n).toLocaleString("ru-RU").replace(/ /g, " ");
  }
  function fp(x) { // stable fingerprint of the listing object
    var s = JSON.stringify(x), h = 5381, i;
    for (i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return String(h);
  }

  function heroHTML(x) {
    var imgs = x.images || [];
    if (!imgs.length) return "";
    var t = imgs.slice(0, 8).map(function (u, i) {
      return '<img src="' + esc(u) + '" alt="" loading="lazy"' +
        (i === 0 ? ' class="is-on"' : "") + ">";
    }).join("");
    return '<div class="nv-hero"><img id="nv-main-img" src="' + esc(imgs[0]) +
      '" alt="' + esc(x.title) + '"></div>' +
      (imgs.length > 1 ? '<div class="nv-film">' + t + "</div>" : "");
  }

  function headHTML(x) {
    var cname = COUNTRY[x.country] || "";
    var priceRow;
    if (x.priceUsd) {
      var psm = x.sizeSqm ? '<span class="nv-psm">' +
        money(Math.round(x.priceUsd / x.sizeSqm)) + " / м²</span>" : "";
      priceRow = '<div class="nv-price-row"><div class="nv-price"><small>от</small> ' +
        money(x.priceUsd) + "</div>" + psm + "</div>";
    } else {
      priceRow = '<div class="nv-price-row"><div class="nv-price">Цена по запросу</div></div>';
    }
    return '<p class="nv-eyeloc"><span>' + esc(x.district || "") + " · " + esc(cname) +
      '</span> <span class="nv-chip">' + esc(MARKET_RU[x.market] || "") + "</span></p>" +
      "<h1>" + esc(x.title) + "</h1>" + priceRow;
  }

  function factsHTML(x) {
    var c = [];
    if (x.sizeSqm) c.push(["Площадь", "от " + x.sizeSqm + " м²"]);
    if (x.bedrooms) c.push(["Спальни", String(x.bedrooms)]);
    var t = TYPE_RU[x.type] || x.type;
    if (t) c.push(["Тип объекта", t]);
    if (x.handover) c.push(["Сдача", x.handover]);
    if (x.developer) c.push(["Застройщик", x.developer]);
    if (!c.length) return "";
    return '<div class="nv-facts">' + c.map(function (kv) {
      return "<div><span>" + esc(kv[0]) + "</span><b>" + esc(kv[1]) + "</b></div>";
    }).join("") + "</div>";
  }

  function sec(num, title, body, id) {
    return '<section class="nv-sec"' + (id ? ' id="' + id + '"' : "") +
      '><div class="s-head"><span class="s-num">' + num +
      '</span><h2>' + esc(title) + "</h2></div>" + body + "</section>";
  }

  function financeHTML(x) {
    if (!x.priceUsd) return "";
    var cells = [["Цена", money(x.priceUsd), false]];
    if (x.sizeSqm) cells.push(["Цена за м²", money(Math.round(x.priceUsd / x.sizeSqm)), true]);
    if (x.yieldPct) {
      cells.push(["Доходность застройщика", x.yieldPct + "%", true]);
      cells.push(["Доход в год при этой ставке", money(Math.round(x.priceUsd * x.yieldPct / 100)), true]);
    }
    var grid = cells.map(function (c) {
      return '<div class="nv-fin-cell' + (c[2] ? " is-accent" : "") + '"><span>' +
        esc(c[0]) + "</span><b>" + esc(c[1]) + "</b></div>";
    }).join("");
    if (x.paymentPlan) {
      grid += '<div class="nv-fin-cell nv-fin-wide"><span>План оплаты</span><b>' +
        esc(x.paymentPlan) + "</b></div>";
    }
    var y = x.yieldPct || 7;
    return '<div class="nv-fin-grid">' + grid + "</div>" +
      '<div class="nv-calc"><div class="nv-calc-t">Калькулятор доходности</div>' +
      '<div class="nv-calc-in">' +
      '<label>Ставка аренды, % годовых <input id="nv-y" type="number" value="' + y +
      '" min="1" max="20" step="0.5"></label>' +
      '<label>Загрузка, % <input id="nv-o" type="number" value="90" min="10" max="100" step="5"></label>' +
      '</div><div class="nv-calc-out">' +
      '<div><span>Доход в год</span><b id="nv-a">—</b></div>' +
      '<div><span>Доход в месяц</span><b id="nv-m">—</b></div>' +
      '<div><span>Окупаемость</span><b id="nv-p">—</b></div>' +
      '</div><p class="nv-note">Расчёт строится от указанной вами ставки и цены объекта (' +
      money(x.priceUsd) + "). Это не гарантия доходности и не оферта: фактическая аренда " +
      "зависит от рынка, отделки, загрузки и сервисных сборов.</p></div>";
  }

  function videosOf(x) {
    if (x.videos && x.videos.length) return x.videos;      // [{id, caption}]
    if (x.videoId) return [{ id: x.videoId, caption: "" }];
    return [];
  }

  function videoHTML(x) {
    var vs = videosOf(x);
    if (!vs.length) return "";
    return vs.map(function (v) {
      return '<figure style="margin:0 0 1rem">' +
        '<div class="nv-yt" data-yt="' + esc(v.id) + '" role="button" tabindex="0" ' +
        'aria-label="Смотреть видео проекта">' +
        '<img src="https://i.ytimg.com/vi/' + esc(v.id) + '/hqdefault.jpg" alt="" loading="lazy">' +
        '<span class="play" aria-hidden="true"><span></span></span></div>' +
        (v.caption ? '<figcaption style="font-size:.8rem;color:#6b6f76;margin-top:.5rem">' +
          esc(v.caption) + "</figcaption>" : "") + "</figure>";
    }).join("");
  }

  function docHTML(x) {
    var pdf = x.pdfUrl || x.brochure;
    if (!pdf) return "";
    var label = x.brochureLabel || "Скачать презентацию — PDF →";
    return '<div class="nv-doc"><a href="' + esc(pdf) +
      '" target="_blank" rel="noopener noreferrer">' + esc(label) + "</a></div>";
  }

  function locationHTML(x) {
    if (!(x.lat && x.lng)) return "";
    var d = 0.004;
    var bbox = (x.lng - d) + "," + (x.lat - d / 2) + "," + (x.lng + d) + "," + (x.lat + d / 2);
    return '<iframe class="nv-map" loading="lazy" title="Карта: ' + esc(x.title) + '" ' +
      'src="https://www.openstreetmap.org/export/embed.html?bbox=' + bbox +
      "&layer=mapnik&marker=" + x.lat + "," + x.lng + '"></iframe>' +
      '<p class="nv-loc-foot">' + esc(x.address || x.district || "") +
      ' · <a href="https://www.google.com/maps/search/?api=1&query=' + x.lat + "," + x.lng +
      '" target="_blank" rel="noopener noreferrer">Открыть в Google Maps →</a></p>';
  }

  function bodyHTML(x) {
    var n = 0, out = "";
    function nxt() { n += 1; return (n < 10 ? "0" : "") + n; }
    if (x.shortDescription)
      out += sec(nxt(), "Описание", '<p class="nv-desc">' + esc(x.shortDescription) + "</p>");
    if (x.highlights && x.highlights.length)
      out += sec(nxt(), "Преимущества", '<ul class="nv-hl">' +
        x.highlights.map(function (h) { return "<li>" + esc(h) + "</li>"; }).join("") + "</ul>");
    var fin = financeHTML(x);
    if (fin) out += sec(nxt(), "Финансы и доходность", fin, "nv-fin-sec");
    var vid = videoHTML(x);
    if (vid) out += sec(nxt(), videosOf(x).length > 1 ? "Видео проекта" : "Видео проекта", vid);
    var doc = docHTML(x);
    if (doc) out += sec(nxt(), x.brochureLabel ? "Документы" : "Презентация", doc);
    var loc = locationHTML(x);
    if (loc) out += sec(nxt(), "Расположение", loc, "nv-loc-sec");
    return { html: out, next: nxt };
  }

  function relHTML(x, all, num) {
    var pool = all.filter(function (y) {
      return y.slug !== x.slug && y.country === x.country &&
        y.purpose === x.purpose && y.images && y.images.length;
    });
    if (!pool.length) pool = all.filter(function (y) {
      return y.slug !== x.slug && y.country === x.country && y.images && y.images.length;
    });
    if (!pool.length) return "";
    var cards = pool.slice(0, 3).map(function (y) {
      return '<a class="nv-rel" href="' + BASE + "/" + y.country + "/" + y.purpose + "/" + y.slug + '/">' +
        '<div class="nv-rel-i"><img src="' + esc(y.images[0]) + '" alt="" loading="lazy"></div>' +
        '<div class="nv-rel-b"><div class="nv-rel-t">' + esc(y.title) + "</div>" +
        '<div class="nv-rel-d">' + esc(y.district || "") + "</div>" +
        '<div class="nv-rel-p">' + money(y.priceUsd) + "</div></div></a>";
    }).join("");
    return sec(num, "Похожие объекты", '<div class="nv-rel-grid">' + cards + "</div>", "nv-rel-sec");
  }

  function wire(x) {
    var main = document.getElementById("nv-main-img");
    Array.prototype.forEach.call(document.querySelectorAll(".nv-film img"), function (t) {
      t.addEventListener("click", function () {
        if (main) main.src = t.src;
        Array.prototype.forEach.call(document.querySelectorAll(".nv-film img"),
          function (o) { o.classList.remove("is-on"); });
        t.classList.add("is-on");
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll(".nv-yt"), function (box) {
      function play() {
        var id = box.getAttribute("data-yt");
        if (!id || box.dataset.loaded) return;
        box.dataset.loaded = "1";
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1";
        f.title = "Видео проекта";
        f.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
        f.allowFullscreen = true;
        f.setAttribute("style", "position:absolute;inset:0;width:100%;height:100%;border:0");
        box.appendChild(f);
      }
      box.addEventListener("click", play);
      box.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); play(); }
      });
    });
    var y = document.getElementById("nv-y"), o = document.getElementById("nv-o");
    if (y && o && x.priceUsd) {
      var P = x.priceUsd;
      var calc = function () {
        var r = parseFloat(y.value) || 0, c = (parseFloat(o.value) || 0) / 100;
        var a = P * (r / 100) * c;
        document.getElementById("nv-a").textContent = a ? money(a) : "—";
        document.getElementById("nv-m").textContent = a ? money(a / 12) : "—";
        document.getElementById("nv-p").textContent = a ? (P / a).toFixed(1) + " лет" : "—";
      };
      y.addEventListener("input", calc);
      o.addEventListener("input", calc);
      calc();
    }
  }

  function render(x, all) {
    var z;
    z = document.getElementById("nv-hero-zone"); if (z) z.innerHTML = heroHTML(x);
    z = document.getElementById("nv-head"); if (z) z.innerHTML = headHTML(x);
    z = document.getElementById("nv-facts-zone"); if (z) z.innerHTML = factsHTML(x);
    var body = bodyHTML(x);
    z = document.getElementById("nv-body"); if (z) z.innerHTML = body.html;
    z = document.getElementById("nv-side-price"); if (z) z.textContent = money(x.priceUsd);
    z = document.getElementById("nv-rel-zone");
    if (z) z.innerHTML = relHTML(x, all || [], body.next());
    document.title = x.title + " — " + (COUNTRY[x.country] || "") + " | MARK FINGERMAN";
    wire(x);
  }

  // ---- entry: sync a baked page against the live listings.json -------------
  function sync() {
    var root = document.body;
    var slug = root.getAttribute("data-nv-slug");
    if (!slug) return;
    var baked = root.getAttribute("data-nv-fp") || "";
    fetch(BASE + "/listings.json?ts=" + Date.now(), { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (all) {
        var x = null, i;
        for (i = 0; i < all.length; i++) if (all[i].slug === slug) { x = all[i]; break; }
        if (!x) return;                     // listing removed — keep baked page
        if (fp(x) === baked) { wire(x); return; }   // unchanged — just wire up
        render(x, all);                     // data changed in backoffice → redraw
      })
      .catch(function () { /* offline etc. — the baked page stands */ });
  }

  window.NVDetail = { render: render, sync: sync, fp: fp };
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", sync);
  else sync();
})();
