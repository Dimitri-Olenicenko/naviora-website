"""
Convert the Naviora site copy to Mark Fingerman's personal voice.

Brand, colours and logo stay as Naviora — only the copy and structure change.

Removes:  the Ecosystem section (04), the investment-services section,
          the /about/ page, and the now-dead footer links to both.
Renames:  "Naviora в цифрах"      -> "Mark Fingerman в цифрах"
          "Связаться с командой"  -> "Связаться с Марком"
Renumbers: 05 ИЗБРАННЫЕ ОБЪЕКТЫ   -> 04  (after Ecosystem is removed)

Idempotent: re-running makes no further changes.
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
report = {"ecosystem": 0, "services": 0, "stats": 0, "contact": 0,
          "footer_about": 0, "footer_eco": 0, "renumber": 0, "vertical_stat": 0}


def strip_section(html: str, anchor: str) -> tuple[str, bool]:
    """Remove the <section> element containing `anchor`, matching nesting."""
    i = html.find(anchor)
    if i == -1:
        return html, False
    start = html.rfind("<section", 0, i)
    if start == -1:
        return html, False
    depth, pos = 0, start
    while pos < len(html):
        nxt_open = html.find("<section", pos)
        nxt_close = html.find("</section>", pos)
        if nxt_close == -1:
            return html, False
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + 8
        else:
            depth -= 1
            pos = nxt_close + 10
            if depth == 0:
                return html[:start] + html[pos:], True
    return html, False


def process(path: str) -> bool:
    html = open(path, encoding="utf-8", errors="replace").read()
    orig = html

    # --- remove whole sections (homepage only) ---------------------------
    html, hit = strip_section(html, "Экосистема Naviora")
    report["ecosystem"] += hit
    html, hit = strip_section(html, "Инвестиции в доходную недвижимость")
    report["services"] += hit

    # --- rename headings --------------------------------------------------
    if "Naviora в цифрах" in html:
        html = html.replace("Naviora в цифрах", "Mark Fingerman в цифрах")
        report["stats"] += 1
    if "Связаться с командой" in html:
        html = html.replace("Связаться с командой", "Связаться с Марком")
        report["contact"] += 1

    # --- drop the "4 / Вертикалей в экосистеме" stat ----------------------
    # The ecosystem is gone, so the stat that counts its verticals is stale.
    m = re.search(r"<div[^>]*>(?:(?!<div)[\s\S]){0,400}?Вертикал[^<]*</div>", html)
    if m:
        start = html.rfind("<div", 0, m.start())
        depth, pos = 0, start
        while pos < len(html):
            o = html.find("<div", pos)
            c = html.find("</div>", pos)
            if c == -1:
                break
            if o != -1 and o < c:
                depth += 1
                pos = o + 4
            else:
                depth -= 1
                pos = c + 6
                if depth == 0:
                    html = html[:start] + html[pos:]
                    report["vertical_stat"] += 1
                    break

    # --- footer: remove the whole Экосистема column ----------------------
    m = re.search(r'<div><div[^>]*>Экосистема</div>[\s\S]{0,900}?</ul></div>', html)
    if m:
        html = html[:m.start()] + html[m.end():]
        report["footer_eco"] += 1

    # --- footer/nav: remove links to the deleted About page ---------------
    n = len(re.findall(r'<li><a[^>]*href="[^"]*/about/"[^>]*>О компании</a></li>', html))
    if n:
        html = re.sub(r'<li><a[^>]*href="[^"]*/about/"[^>]*>О компании</a></li>', "", html)
        report["footer_about"] += n
    n2 = len(re.findall(r'<a[^>]*href="[^"]*/about/"[^>]*>О компании</a>', html))
    if n2:
        html = re.sub(r'<a[^>]*href="[^"]*/about/"[^>]*>О компании</a>', "", html)
        report["footer_about"] += n2

    # --- renumber: 05 ИЗБРАННЫЕ ОБЪЕКТЫ becomes 04 -----------------------
    # The number sits in its own <span> immediately before the title span.
    if "ИЗБРАННЫЕ ОБЪЕКТЫ" in html:
        html, k = re.subn(
            r'(<span[^>]*>)05(</span><span[^>]*>ИЗБРАННЫЕ ОБЪЕКТЫ)',
            r"\g<1>04\g<2>", html)
        report["renumber"] += k

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return True
    return False


changed = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "_next", "node_modules")]
    for fn in filenames:
        if fn.endswith(".html"):
            if process(os.path.join(dirpath, fn)):
                changed += 1

print(f"files changed: {changed}")
for k, v in report.items():
    print(f"  {k:16} {v}")
