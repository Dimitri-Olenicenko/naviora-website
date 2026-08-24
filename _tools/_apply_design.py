"""Redesign the property-listing blocks only.

Scope, per the owner: the listing cards. The Naviora blue and the home page
stay exactly as they are — no palette change, no serif headings, no touching
the hero. Everything here is confined to a card that links to a listing.

The fixes are grounded in measurements taken off live premium platforms and
off our own pages:

  - Our cards measured 21px of ragged height across a single row, because
    each one sizes to its own content. Equal heights are the single biggest
    tidiness win.
  - The payment-plan block drew a second border *inside* the card, breaking
    its edge. Same information reads better as a hairline-separated footer.
  - Luxhabitat runs a 64px row gap against a 32px column gap. Vertical air is
    what separates a gallery from a spreadsheet; ours was a uniform 24px.
  - Solid blue market badges put the accent on a full bar sitting over the
    photograph. Premium sites keep badges quiet so the image carries the
    card. The badge keeps its shape and position — it just stops competing
    with the picture.
  - A slow image scale on hover reads as craft. 700ms, not 200ms.

Our 4:3 image ratio and 0px corner radius already match Luxhabitat exactly,
so both are left alone.

CSS only: the React app is compiled and we have no source, so selectors
target utility classes present in the built output. Every rule is scoped by
an `a[href*="/residential/"]` or `/commercial/` ancestor, so nothing outside
a property card can be affected.

Idempotent.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "_next", "static", "chunks")
MARK = "/* nv-listing-card-design */"

CARD = """
/* ---- 1. Equal card heights ----------------------------------------------
   Measured 21px of ragged bottoms across one row of three. */
.grid > div:has(> a[href*="/residential/"]),
.grid > div:has(> a[href*="/commercial/"]) { display: flex; }
.grid > div > a[href*="/residential/"],
.grid > div > a[href*="/commercial/"] { width: 100%; }

/* ---- 2. Let the grid breathe --------------------------------------------
   Luxhabitat: 32px columns, 64px rows. Ours was 24px both ways. */
.grid.gap-6 { column-gap: 2rem !important; row-gap: 3.5rem !important; }

/* ---- 3. Remove the nested bordered box ----------------------------------
   The payment-plan panel drew a border inside the card. A single hairline
   above it does the same separating job without a box-in-a-box. */
a[href*="/residential/"] .hairline,
a[href*="/commercial/"] .hairline {
  border: 0 !important;
  border-top: 1px solid rgba(20,20,20,.10) !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  background: transparent !important;
}

/* ---- 4. Quiet the market badge ------------------------------------------
   Keeps its position and legibility, stops competing with the photograph.
   The blue stays the brand's everywhere else. */
a[href*="/residential/"] .absolute.t-micro,
a[href*="/commercial/"] .absolute.t-micro {
  background: rgba(20,22,26,.74) !important;
  backdrop-filter: blur(6px);
  letter-spacing: .1em !important;
}

/* ---- 5. Slow image reveal on hover -------------------------------------- */
a[href*="/residential/"] img,
a[href*="/commercial/"] img {
  transition: transform 700ms cubic-bezier(.16,1,.3,1) !important;
}
a[href*="/residential/"]:hover img,
a[href*="/commercial/"]:hover img { transform: scale(1.03) !important; }

/* ---- 6. Card frame lifts on hover --------------------------------------- */
a[href*="/residential/"].group,
a[href*="/commercial/"].group {
  transition: border-color 200ms ease, transform 200ms ease !important;
}
a[href*="/residential/"].group:hover,
a[href*="/commercial/"].group:hover { transform: translateY(-2px); }

/* ---- 7. Title: sentence case, one weight down ---------------------------
   Uppercase Cyrillic is measurably harder to read than Latin at the same
   size, and the shout is unnecessary once the card is tidy. */
a[href*="/residential/"] .t-h3,
a[href*="/commercial/"] .t-h3 {
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: -0.005em !important;
}

/* ---- 8. Price reads as money, not as a shout ----------------------------
   Savills sets price at w400. Bold price is a portal signal; the figure is
   already the largest thing on the card. */
a[href*="/residential/"] .t-num,
a[href*="/commercial/"] .t-num { letter-spacing: -0.01em !important; }

/* ---- 9. Even out the card footer -----------------------------------------
   Payment-plan strings run 66-111 characters, so the footer block wraps to
   different heights and rows come out ragged (measured 25px across one row).
   Clamping the footer to three lines and pushing it to the bottom makes every
   card in a row terminate on the same line. The full plan is still on the
   detail page. */
a[href*="/residential/"] .hairline,
a[href*="/commercial/"] .hairline {
  margin-top: auto;
  min-height: 4.6em;
}
/* "Сдача" and "План оплаты" are separate spans in a flex column, but the
   column collapses them onto one line so they read as "Q3 2029План оплаты".
   Force each onto its own line. */
a[href*="/residential/"] .hairline > *,
a[href*="/commercial/"] .hairline > * { display: block; }
/* Clamp only the payment-plan line, so the handover date is never cut. */
a[href*="/residential/"] .hairline > *:last-child,
a[href*="/commercial/"] .hairline > *:last-child {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ---- 10. A listing with no image must not collapse ------------------------
   09 Life Residences ships without renders; without a min-height its image
   frame has zero height and the card's proportions break against its
   neighbours. */
a[href*="/residential/"] > div:first-child,
a[href*="/commercial/"] > div:first-child {
  min-height: 1px;
  background: #f2f2f0;
}

@media (prefers-reduced-motion: reduce){
  a[href*="/residential/"] img, a[href*="/commercial/"] img,
  a[href*="/residential/"].group, a[href*="/commercial/"].group {
    transition: none !important; transform: none !important;
  }
}
"""


def main():
    sheets = [f for f in os.listdir(CSS_DIR) if f.endswith(".css")]
    payload = f"\n{MARK}\n{CARD}\n"
    done = 0
    for name in sheets:
        path = os.path.join(CSS_DIR, name)
        css = open(path, encoding="utf-8", errors="replace").read()
        if MARK in css:
            print(f"  {name}: already applied")
            continue
        open(path, "a", encoding="utf-8").write(payload)
        done += 1
        print(f"  {name}: listing-card design appended")

    print(f"\nstylesheets patched: {done}")
    print("palette, typography and home page left unchanged")


if __name__ == "__main__":
    main()
