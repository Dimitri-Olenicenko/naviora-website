"""
Inject the Видео and Презентация sections AFTER React has hydrated.

Why: these pages are React components compiled into a JS chunk. Anything added
to the exported HTML is discarded on hydration — with JS off the sections were
present, with JS on they vanished. Editing the hydration payload instead is not
an option either: doing that broke two pages earlier today (malformed JSON).

So the sections are built by a script that runs after hydration and re-inserts
them if React ever re-renders. The static HTML copies are removed to avoid a
hydration mismatch.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> {videos: [(id, caption)], deck: (drive_id, label)}
MEDIA = {
    "vr-vake-sky-tower": {
        "videos": [("Qg98xW1adOo", "VR Vake Sky Tower — презентация проекта"),
                   ("_QALYuZ5WfU", "Night View 360° — панорама"),
                   ("rnCvO9X-mwY", "Fashion Avenue")],
        "deck": ("1Vo1dHd9PrTs-6Zs6-Zgu52wHvT4fkEQQ", "VR Vake Sky Tower"),
    },
    "vr-krtsanisi-resort-residence": {
        "videos": [("f2GmxSxcqwo", "VR Krtsanisi Resort Residence — презентация"),
                   ("2-C2F2mxFPM", "Ход строительства"),
                   ("wIG1M4tQR1c", "Строительство премиум-фазы")],
        "deck": ("1PVzWRZ2JEwsGJiHEqvC1t1gV7KlXILdb", "VR Krtsanisi Resort Residence"),
    },
    "vr-shekvetili-forest-beach": {
        "videos": [("iysxeXK6Kwc", "VR Shekvetili Forest~Beach — презентация"),
                   ("yMusyW6A780", "Строительство первой очереди"),
                   ("x9Kouz1BdXQ", "Первая очередь — ход работ")],
        "deck": ("1SHShW369Va1OfCMhMXmccS0i6-129wvz", "VR Shekvetili Forest~Beach"),
    },
}

SCRIPT_TMPL = """<script id="nv-media">
(function(){
  var V = %(videos)s;
  var DECK = %(deck)s;

  function card(v){
    var fig = document.createElement('figure');
    fig.style.cssText = 'margin:0;min-width:0';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('data-yt', v[0]);
    btn.setAttribute('aria-label', 'Смотреть: ' + v[1]);
    btn.style.cssText = 'display:block;width:100%%;max-width:100%%;position:relative;'
      + 'overflow:hidden;background:#0d1b2a;border:0;padding:0;cursor:pointer;text-align:left';
    var img = document.createElement('img');
    img.src = 'https://i.ytimg.com/vi/' + v[0] + '/hqdefault.jpg';
    img.alt = ''; img.loading = 'lazy';
    img.style.cssText = 'display:block;width:100%%;height:auto;aspect-ratio:16/9;object-fit:cover';
    var play = document.createElement('span');
    play.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center';
    play.innerHTML = '<span style="display:flex;height:4rem;width:4rem;align-items:center;'
      + 'justify-content:center;border-radius:9999px;background:rgba(201,168,76,.92)">'
      + '<svg width="22" height="26" viewBox="0 0 22 26" fill="none" aria-hidden="true">'
      + '<path d="M21 13 L0 26 L0 0 Z" fill="#0d1b2a"/></svg></span>';
    btn.appendChild(img); btn.appendChild(play);
    btn.addEventListener('click', function(){
      var f = document.createElement('iframe');
      f.width = '100%%'; f.style.cssText = 'aspect-ratio:16/9;border:0;width:100%%';
      f.allow = 'accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture';
      f.allowFullscreen = true; f.title = v[1];
      f.src = 'https://www.youtube-nocookie.com/embed/' + v[0] + '?autoplay=1&rel=0';
      btn.replaceWith(f);
    });
    var cap = document.createElement('figcaption');
    cap.className = 't-sm'; cap.textContent = v[1];
    cap.style.cssText = 'margin-top:.75rem;opacity:.75';
    fig.appendChild(btn); fig.appendChild(cap);
    return fig;
  }

  function section(num, title, id){
    var s = document.createElement('section');
    s.className = 'mt-10'; s.setAttribute('data-nv-media', id);
    s.style.minWidth = '0';
    var band = document.createElement('div');
    band.className = 'band';
    band.innerHTML = '<span class="t-micro">' + num + '</span>'
      + '<h2 class="t-h3">' + title + '</h2>';
    var body = document.createElement('div');
    body.className = 'hairline border-t-0 p-6';
    s.appendChild(band); s.appendChild(body);
    return {sec: s, body: body};
  }

  function build(){
    var host = document.querySelector('main .lg\\\\:col-span-2, main > div > div');
    var anchor = document.querySelector('aside');
    if (!anchor || !anchor.parentElement) return;
    var col = anchor.previousElementSibling;
    if (!col) return;

    if (!col.querySelector('[data-nv-media="video"]') && V.length){
      var v = section('04', 'Видео', 'video');
      var grid = document.createElement('div');
      grid.style.cssText = 'display:grid;gap:1.5rem;grid-template-columns:1fr;min-width:0';
      V.forEach(function(x){ grid.appendChild(card(x)); });
      v.body.appendChild(grid);
      col.appendChild(v.sec);
    }

    if (!col.querySelector('[data-nv-media="deck"]') && DECK){
      var d = section('05', 'Презентация', 'deck');
      d.body.innerHTML =
        '<a href="https://drive.google.com/file/d/' + DECK[0] + '/view" target="_blank" '
        + 'rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:.5rem;'
        + 'border-bottom:1px solid #C9A84C;padding-bottom:2px;font-weight:600;'
        + 'text-transform:uppercase;letter-spacing:.06em;font-size:.82rem;color:#8a6e2a;'
        + 'text-decoration:none">Презентация проекта — PDF →</a>'
        + '<p class="t-sm" style="margin-top:.75rem;opacity:.7">'
        + 'Официальные материалы застройщика · ' + DECK[1] + '</p>';
      col.appendChild(d.sec);
    }
  }

  function run(){ try { build(); } catch(e){} }
  run();
  document.addEventListener('DOMContentLoaded', run);
  window.addEventListener('load', function(){ setTimeout(run, 300); setTimeout(run, 1200); });
  new MutationObserver(function(){ run(); })
    .observe(document.documentElement, {childList:true, subtree:true});
})();
</script>"""


def js_arr(videos):
    return "[" + ",".join('["%s","%s"]' % (v, c) for v, c in videos) + "]"


changed = 0
for slug, media in MEDIA.items():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "_next", "_tools")]
        if os.path.basename(dp) != slug or "index.html" not in fn:
            continue
        path = os.path.join(dp, "index.html")
        html = open(path, encoding="utf-8", errors="replace").read()
        orig = html

        # Remove the static copies — React discards them anyway and their
        # presence causes a hydration mismatch warning.
        html = re.sub(r'<section[^>]*aria-labelledby="video-heading".*?</section>', "",
                      html, flags=re.S)
        html = re.sub(r'<section[^>]*data-nv-deck.*?</section>', "", html, flags=re.S)
        html = re.sub(r'<script id="nv-media">.*?</script>', "", html, flags=re.S)
        # Old facade script, superseded by this one.
        html = re.sub(r'<script>document\.querySelectorAll\("\[data-yt\]"\).*?</script>', "",
                      html, flags=re.S)

        script = SCRIPT_TMPL % {
            "videos": js_arr(media["videos"]),
            "deck": '["%s","%s"]' % media["deck"],
        }
        html = html.replace("</body>", script + "</body>", 1)

        if html != orig:
            open(path, "w", encoding="utf-8").write(html)
            print(f"  + {slug}")
            changed += 1

print(f"pages updated: {changed}")
