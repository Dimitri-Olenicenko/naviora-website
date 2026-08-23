"""
Add a "Видео" section to listing pages.

Uses a click-to-load facade rather than a live iframe: the poster is a static
thumbnail and the YouTube player is only injected on click. This keeps
YouTube's ~1MB player and its cookies off the initial page load.

Video IDs are the developer's own uploads, verified reachable via oEmbed.
Idempotent: re-running will not duplicate the section.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> (section number, [(video_id, caption), ...])
VIDEOS = {
    "vr-vake-sky-tower": [
        ("Qg98xW1adOo", "VR Vake Sky Tower — презентация проекта"),
        ("_QALYuZ5WfU", "Night View 360° — панорама"),
        ("rnCvO9X-mwY", "Fashion Avenue"),
    ],
    "vr-krtsanisi-resort-residence": [
        ("f2GmxSxcqwo", "VR Krtsanisi Resort Residence — презентация"),
        ("2-C2F2mxFPM", "Территория комплекса"),
        ("wIG1M4tQR1c", "Инфраструктура"),
    ],
    "vr-shekvetili-forest-beach": [
        ("iysxeXK6Kwc", "VR Shekvetili Forest~Beach — презентация"),
        ("yMusyW6A780", "Café del Mar Georgia"),
        ("x9Kouz1BdXQ", "Пляж и территория"),
    ],
    "five-towers-arabkir-unit-1": [],  # no video published by Armconstruct
}


def facade(vid: str, caption: str) -> str:
    """One click-to-play video card."""
    return (
        '<figure class="m-0 min-w-0">'
        f'<button type="button" class="group relative block w-full max-w-full overflow-hidden bg-deep text-left" '
        f'data-yt="{vid}" aria-label="Смотреть: {caption}">'
        f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy" '
        'class="aspect-video w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"/>'
        '<span class="absolute inset-0 flex items-center justify-center">'
        '<span class="flex h-16 w-16 items-center justify-center rounded-full bg-signal/90 '
        'transition-transform duration-200 group-hover:scale-110">'
        '<svg width="22" height="26" viewBox="0 0 22 26" fill="none" aria-hidden="true">'
        '<path d="M21 13 L0 26 L0 0 Z" fill="#0d1b2a"/></svg>'
        '</span></span></button>'
        f'<figcaption class="t-sm mt-3 text-ink/70">{caption}</figcaption>'
        '</figure>'
    )


SCRIPT = (
    '<script>'
    'document.querySelectorAll("[data-yt]").forEach(function(b){'
    'b.addEventListener("click",function(){'
    'var f=document.createElement("iframe");'
    'f.width="100%";f.style.aspectRatio="16/9";f.style.border="0";'
    'f.allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture";'
    'f.allowFullscreen=true;f.title=b.getAttribute("aria-label")||"video";'
    'f.src="https://www.youtube-nocookie.com/embed/"+b.dataset.yt+"?autoplay=1&rel=0";'
    'b.replaceWith(f);});});'
    '</script>'
)


def build_section(num: str, items) -> str:
    cards = "".join(facade(v, c) for v, c in items)
    # min-w-0 on the grid stops implicit-min-content sizing from pushing the
    # column wider than the viewport on narrow screens.
    cols = "sm:grid-cols-2" if len(items) > 1 else ""
    return (
        '<section class="mt-10 min-w-0" aria-labelledby="video-heading">'
        f'<div class="band"><span class="t-micro">{num}</span>'
        '<h2 id="video-heading" class="t-h3">Видео</h2></div>'
        '<div class="hairline border-t-0 p-6">'
        f'<div class="grid min-w-0 gap-6 {cols}">{cards}</div></div>'
        '</section>'
    )


def next_section_number(html: str) -> str:
    nums = [int(n) for n in re.findall(r'<span[^>]*class="t-micro"[^>]*>(\d{2})</span>', html)]
    body = [n for n in nums if n < 90]
    return f"{(max(body) + 1) if body else 4:02d}"


changed = 0
for slug, items in VIDEOS.items():
    if not items:
        continue
    hits = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "_next")]
        if os.path.basename(dp) == slug and "index.html" in fn:
            hits.append(os.path.join(dp, "index.html"))
    if not hits:
        print(f"  !! page not found for {slug}")
        continue

    for path in hits:
        html = open(path, encoding="utf-8", errors="replace").read()
        if 'aria-labelledby="video-heading"' in html:
            print(f"  = already has video: {slug}")
            continue

        anchor = "</section></div><aside"
        i = html.find(anchor)
        if i == -1:
            print(f"  !! insertion point not found: {slug}")
            continue

        num = next_section_number(html)
        block = build_section(num, items)
        html = html[:i + len("</section>")] + block + html[i + len("</section>"):]
        if "data-yt" in html and SCRIPT not in html:
            html = html.replace("</body>", SCRIPT + "</body>", 1)

        open(path, "w", encoding="utf-8").write(html)
        print(f"  + {slug}: section {num}, {len(items)} video(s)")
        changed += 1

print(f"pages updated: {changed}")
