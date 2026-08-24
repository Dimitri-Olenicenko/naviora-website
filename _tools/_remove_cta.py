"""Remove the "Заинтересовал объект?" CTA block from every listing page.

It appeared from two places:
  - the finance injector (removed at source)
  - the Next.js-exported pages, which carry their own copy inside the
    hydration payload

For the exported pages the block is rebuilt by React on hydration, so deleting
the markup from the HTML is not enough — it comes straight back. It is hidden
with CSS instead, scoped to the section that contains that heading, so nothing
else on the page is affected.

The listing pages already offer a contact route in the sidebar; this block was
a second ask on the same screen.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "_next", "static", "chunks")
MARK = "/* nv-hide-listing-cta */"

RULE = """
%s
/* The "Заинтересовал объект?" panel on listing detail pages. It is the dark
   sidebar card (div.hairline.bg-deep inside the aside), rebuilt by React on
   hydration — so it is hidden rather than deleted. :has() scopes it to the
   card that actually carries that heading; the header button, the footer and
   the contacts page are untouched. Verified against the live DOM rather than
   assumed: heading is H2.t-h3 inside DIV.hairline.bg-deep inside ASIDE. */
aside div.bg-deep:has(> h2.t-h3),
#nv-cta-sec {
  display: none !important;
}
""" % MARK

COUNTRIES = ("dubai", "abudhabi", "armenia", "georgia")
HEADING = "Заинтересовал объект"


def strip_static(html: str) -> tuple[str, int]:
    """Drop the block from the served HTML where it is plain markup."""
    n = 0
    # our own injected section, if a stale copy is still on disk
    html, k = re.subn(r'<section class="nv-cta" id="nv-cta-sec">.*?</section>',
                      "", html, flags=re.S)
    n += k
    return html, n


def main():
    # 1. CSS, which is what actually removes it from the React-rendered pages
    done = 0
    for name in sorted(os.listdir(CSS_DIR)):
        if not name.endswith(".css"):
            continue
        path = os.path.join(CSS_DIR, name)
        css = open(path, encoding="utf-8", errors="replace").read()
        if MARK in css:
            continue
        open(path, "a", encoding="utf-8").write(RULE)
        done += 1
    print(f"stylesheets patched: {done}")

    # 2. Static copies on disk
    stripped = pages = 0
    for country in COUNTRIES:
        for purpose in ("residential", "commercial"):
            base = os.path.join(ROOT, country, purpose)
            if not os.path.isdir(base):
                continue
            for slug in os.listdir(base):
                f = os.path.join(base, slug, "index.html")
                if not os.path.isfile(f):
                    continue
                html = open(f, encoding="utf-8", errors="replace").read()
                if HEADING not in html:
                    continue
                pages += 1
                new, k = strip_static(html)
                if new != html:
                    open(f, "w", encoding="utf-8").write(new)
                    stripped += k

    print(f"pages containing the block: {pages}")
    print(f"static copies removed: {stripped}")
    print("the rest are React-rendered and are hidden by the CSS above")


if __name__ == "__main__":
    main()
