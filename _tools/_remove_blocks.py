"""
Remove from the site:
  1. the empty "Экосистема" column left in the footer
  2. the Партнёрство and Адрес entries on the contacts page
  3. the whole "Юридическое лицо" card (company + licence)

Patches both the exported HTML and the compiled React chunks — editing only
the HTML lets React re-render the old content on hydration.

Targets exact markup rather than walking the DOM tree: an earlier tree-walking
version removed neighbouring entries by mistake.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS = os.path.join(ROOT, "_next", "static", "chunks")
report = {}


def bump(k, n=1):
    report[k] = report.get(k, 0) + n


# --- 1. contacts page HTML -------------------------------------------------

PARTNERSHIP = (
    '<div><dt class="t-micro text-mut">Партнёрство</dt><dd class="mt-1">'
    '<a href="mailto:fingermanmark2017@gmail.com" class="break-all text-ink outline-none '
    'hover:text-signal focus-visible:text-signal">fingermanmark2017@gmail.com</a>'
    '<span class="block text-mut">— стратегические коллаборации</span></dd></div>'
)

ADDRESS = (
    '<div><dt class="t-micro text-mut">Адрес</dt>'
    '<dd class="mt-1 text-ink">2304 Bay View Tower, Marasi Drive<br/>'
    'Business Bay, Dubai, UAE</dd></div>'
)

LEGAL = (
    '<div class="hairline p-6"><h2 class="t-h3 text-deep">Юридическое лицо</h2>'
    '<dl class="t-sm mt-4 space-y-2 text-ink/70">'
    '<div class="flex flex-wrap justify-between gap-x-4 gap-y-1 border-b border-dotted '
    'border-line pb-2"><dt>Компания</dt>'
    '<dd class="text-ink sm:text-right">Mark Fingerman</dd></div>'
    '<div class="flex flex-wrap justify-between gap-x-4 gap-y-1"><dt>Лицензия</dt>'
    '<dd class="t-num text-ink">1126816</dd></div></dl></div>'
)


def patch_html(path: str) -> bool:
    html = open(path, encoding="utf-8", errors="replace").read()
    orig = html
    for frag, key in ((PARTNERSHIP, "partnership"), (ADDRESS, "address"), (LEGAL, "legal_card")):
        if frag in html:
            html = html.replace(frag, "")
            bump(key)
    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return True
    return False


# --- 2. compiled chunks ----------------------------------------------------

def patch_chunks():
    for fn in sorted(os.listdir(CHUNKS)):
        if not fn.endswith(".js"):
            continue
        p = os.path.join(CHUNKS, fn)
        s = open(p, encoding="utf-8", errors="replace").read()
        orig = s

        # Footer: drop the now-empty Экосистема column.
        s = s.replace('(0,t.jsx)(m,{title:"Экосистема",links:d}),', "")
        s = s.replace(',(0,t.jsx)(m,{title:"Экосистема",links:d})', "")
        if s != orig:
            bump("footer_eco_column")

        # Contacts page component: remove the three data entries by label.
        for label, key in (("Партнёрство", "chunk_partnership"),
                           ("Адрес", "chunk_address"),
                           ("Юридическое лицо", "chunk_legal")):
            pat = 'children:"%s"' % label
            while pat in s:
                i = s.index(pat)
                # Walk back to the enclosing jsx element call for this entry.
                start = max(s.rfind('(0,t.jsxs)("div"', 0, i),
                            s.rfind('(0,t.jsx)("div"', 0, i))
                if start == -1:
                    break
                m = re.compile(r'\(0,t\.jsxs?\)').match(s, start)
                if not m:
                    break
                op = s.index("(", m.end())
                depth, k, end = 0, op, None
                in_str, quote, esc = False, "", False
                while k < len(s):
                    ch = s[k]
                    if in_str:
                        if esc:
                            esc = False
                        elif ch == "\\":
                            esc = True
                        elif ch == quote:
                            in_str = False
                    else:
                        if ch in "\"'`":
                            in_str, quote = True, ch
                        elif ch == "(":
                            depth += 1
                        elif ch == ")":
                            depth -= 1
                            if depth == 0:
                                end = k + 1
                                break
                    k += 1
                if end is None:
                    break
                tail = end
                while tail < len(s) and s[tail] in " \n":
                    tail += 1
                if tail < len(s) and s[tail] == ",":
                    tail += 1
                s = s[:start] + s[tail:]
                bump(key)

        if s != orig:
            open(p, "w", encoding="utf-8").write(s)
            print(f"  patched chunk {fn}")


changed = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "_next", "node_modules", "_tools")]
    for f in fn:
        if f.endswith(".html") and patch_html(os.path.join(dp, f)):
            changed += 1

patch_chunks()

print(f"html files changed: {changed}")
for k, v in sorted(report.items()):
    print(f"  {k:22} {v}")
