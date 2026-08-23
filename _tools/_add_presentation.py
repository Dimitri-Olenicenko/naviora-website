"""
Add a "Презентация" block linking to the developer's official project PDF.

Links point at VR Holding's own public Google Drive files (verified HTTP 200).
They are not copied or re-hosted — if the developer updates a deck, the link
follows. The trade-off is that if they move or unshare a file the link dies,
so re-check periodically.

Inserted as plain HTML after the last section, and marked so it survives
hydration the same way the hidden blocks do. The React payload is NOT edited —
doing that broke two pages earlier.

Idempotent.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> (Google Drive file id, label)
DECKS = {
    "vr-shekvetili-forest-beach": (
        "1SHShW369Va1OfCMhMXmccS0i6-129wvz", "VR Shekvetili Forest~Beach"),
    "vr-krtsanisi-resort-residence": (
        "1PVzWRZ2JEwsGJiHEqvC1t1gV7KlXILdb", "VR Krtsanisi Resort Residence"),
    "vr-vake-sky-tower": (
        "1Vo1dHd9PrTs-6Zs6-Zgu52wHvT4fkEQQ", "VR Vake Sky Tower"),
}


def block(num: str, file_id: str, label: str) -> str:
    url = f"https://drive.google.com/file/d/{file_id}/view"
    return (
        '<section class="mt-10" data-nv-deck aria-labelledby="deck-heading">'
        f'<div class="band"><span class="t-micro">{num}</span>'
        '<h2 id="deck-heading" class="t-h3">Презентация</h2></div>'
        '<div class="hairline border-t-0 p-6">'
        f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
        'style="display:inline-flex;align-items:center;gap:.5rem;'
        'border-bottom:1px solid #C9A84C;padding-bottom:2px;'
        'font-weight:600;text-transform:uppercase;letter-spacing:.06em;'
        'font-size:.82rem;color:#8a6e2a;text-decoration:none">'
        f'Презентация проекта — PDF →</a>'
        f'<p class="t-sm" style="margin-top:.75rem;opacity:.7">'
        f'Официальные материалы застройщика · {label}</p>'
        '</div></section>'
    )


def next_num(html: str) -> str:
    import re
    nums = [int(n) for n in re.findall(
        r'<span[^>]*class="t-micro"[^>]*>(\d{2})</span>', html)]
    body = [n for n in nums if n < 90]
    # sections on these pages run 01..04 then a sidebar "05 Похожие объекты";
    # slot the deck in just before that sidebar number.
    return f"{max(body[:-1]) + 1:02d}" if len(body) > 1 else "05"


changed = 0
for slug, (file_id, label) in DECKS.items():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "_next", "_tools")]
        if os.path.basename(dp) != slug or "index.html" not in fn:
            continue
        path = os.path.join(dp, "index.html")
        html = open(path, encoding="utf-8", errors="replace").read()
        if "data-nv-deck" in html:
            print(f"  = already has deck: {slug}")
            continue

        anchor = "</section></div><aside"
        i = html.find(anchor)
        if i == -1:
            print(f"  !! insertion point not found: {slug}")
            continue

        num = next_num(html)
        html = (html[:i + len("</section>")]
                + block(num, file_id, label)
                + html[i + len("</section>"):])
        open(path, "w", encoding="utf-8").write(html)
        print(f"  + {slug}: section {num}")
        changed += 1

print(f"pages updated: {changed}")
