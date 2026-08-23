"""Hide the SkylineGlyph decoration on the country cards.

Each country tile on the home page renders a `SkylineGlyph` — an SVG meant to
suggest that city's skyline, absolutely positioned across the bottom of the
card. At the card's actual size the buildings collapse into a row of small
blue tick marks sitting directly under the "Смотреть объекты" button, which
reads as a stray UI artefact rather than decoration.

The glyph is purely decorative (it already carries pointer-events-none and no
accessible name), so hiding it removes nothing meaningful.

Done in CSS rather than by editing the component: the glyph is rendered by
React from a compiled chunk, so anything removed from the exported HTML comes
straight back on hydration. The selector matches the glyph's own utility
classes, which are stable in the compiled output.

Idempotent.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "_next", "static", "chunks")
MARK = "/* nv-hide-skyline-glyph */"

RULE = """
%s
/* Decorative city-skyline SVG on the country cards. At card size it renders
   as a row of tick marks under the CTA and reads as a glitch. */
a.group.relative.flex.flex-col > svg.pointer-events-none.absolute {
  display: none !important;
}
""" % MARK


def main():
    sheets = [f for f in os.listdir(CSS_DIR) if f.endswith(".css")]
    if not sheets:
        print("!! no stylesheet found")
        return

    done = 0
    for name in sheets:
        path = os.path.join(CSS_DIR, name)
        css = open(path, encoding="utf-8", errors="replace").read()
        if MARK in css:
            print(f"  {name}: already patched")
            continue
        open(path, "a", encoding="utf-8").write(RULE)
        done += 1
        print(f"  {name}: glyph hidden")

    print(f"\nstylesheets patched: {done}")


if __name__ == "__main__":
    main()
