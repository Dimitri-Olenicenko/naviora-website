"""Stop listing cards from staying invisible when the reveal animation misfires.

The listing grids wrap their cards in a Framer Motion element that animates
from `opacity: 0` on `whileInView` with `viewport: {once: true}`. On several
grids — Dubai, Abu Dhabi and Armenia, both purposes — that wrapper never
leaves the hidden state, so the page reports "3 объекта" above a blank area.
Georgia happens to fire correctly, which is why it looked fine.

Scrolling does not recover it, so this is not simply a viewport threshold
that never gets crossed. Rather than chase the cause inside minified Framer
Motion, this makes the revealed state the default: any wrapper that is still
fully transparent after the animation window is forced visible.

The rule is scoped to grid wrappers containing a listing card, so genuine
transient animations (the mobile filter sheet, the hero) are untouched. It
also runs before paint on a fresh page, so there is no flash.

Applied by appending to the site's own stylesheet, which every page already
loads — no extra request, and it survives hydration because CSS is not
something React re-renders away.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "_next", "static", "chunks")
MARK = "/* nv-card-reveal-fix */"

RULE = """
%s
/* Listing cards must never be left invisible by a reveal animation that
   failed to fire. Framer Motion sets an inline opacity, so the override has
   to be !important to win; it applies only to a wrapper that actually holds
   a listing card, leaving other animated elements alone. */
.grid > div:has(> a[href*="/residential/"]),
.grid > div:has(> a[href*="/commercial/"]) {
  opacity: 1 !important;
  transform: none !important;
}
""" % MARK


def main():
    targets = [f for f in os.listdir(CSS_DIR) if f.endswith(".css")]
    if not targets:
        print("!! no stylesheet found")
        return

    done = 0
    for name in targets:
        path = os.path.join(CSS_DIR, name)
        css = open(path, encoding="utf-8", errors="replace").read()
        if MARK in css:
            print(f"  {name}: already patched")
            continue
        open(path, "a", encoding="utf-8").write(RULE)
        done += 1
        print(f"  {name}: reveal fix appended")

    print(f"\nstylesheets patched: {done}")


if __name__ == "__main__":
    main()
