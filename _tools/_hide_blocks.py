"""
Hide the Партнёрство / Адрес / Юридическое лицо blocks on the contacts page,
and the Партнёрство entry on the homepage.

Why hiding rather than deleting: these blocks also exist in the React
hydration payload. Editing that payload by hand produced malformed JSON and
took the whole contacts page down ("This page couldn't load"). Marking the
elements and hiding them with CSS achieves the same visible result with no
risk to hydration — and a small script re-marks them after React renders,
so they stay hidden.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STYLE = '<style id="nv-hide">[data-nv-hide]{display:none!important}</style>'

SCRIPT = (
    '<script id="nv-hide-js">'
    '(function(){'
    'var L=["\\u041f\\u0430\\u0440\\u0442\\u043d\\u0451\\u0440\\u0441\\u0442\\u0432\\u043e",'   # Партнёрство
    '"\\u0410\\u0434\\u0440\\u0435\\u0441"];'                                                    # Адрес
    'function mark(){'
    'document.querySelectorAll("dt").forEach(function(dt){'
    'if(L.indexOf((dt.textContent||"").trim())>-1){'
    'var w=dt.closest("div"); if(w) w.setAttribute("data-nv-hide","");}});'
    'document.querySelectorAll("h2").forEach(function(h){'
    'if((h.textContent||"").trim()==="\\u042e\\u0440\\u0438\\u0434\\u0438\\u0447\\u0435\\u0441\\u043a\\u043e\\u0435 \\u043b\\u0438\\u0446\\u043e"){'  # Юридическое лицо
    'var w=h.closest("div"); if(w) w.setAttribute("data-nv-hide","");}});}'
    'mark();'
    'document.addEventListener("DOMContentLoaded",mark);'
    'new MutationObserver(mark).observe(document.documentElement,{childList:true,subtree:true});'
    '})();'
    '</script>'
)

changed = 0
for rel in ("contacts/index.html", "index.html"):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    html = open(path, encoding="utf-8", errors="replace").read()
    orig = html

    if 'id="nv-hide"' not in html:
        html = html.replace("</head>", STYLE + "</head>", 1)
    if 'id="nv-hide-js"' not in html:
        html = html.replace("</body>", SCRIPT + "</body>", 1)

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        print(f"  + {rel}")
        changed += 1

print(f"files updated: {changed}")
