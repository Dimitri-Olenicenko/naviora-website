"""
Apply the Mark Fingerman personalisation to the compiled homepage chunk.

Why this exists: the HTML edits alone were not enough. The homepage is a
React component compiled into _next/static/chunks/276v999593fjv.js, so on
hydration React re-rendered the *old* sections over the edited HTML. The
page looked unchanged in a browser while curl showed it fixed.

This patches the compiled component itself. Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK = os.path.join(ROOT, "_next", "static", "chunks", "276v999593fjv.js")


def find_section_span(src: str, needle: str):
    """Return (start, end) of the (0,t.jsx…)("section", …) call containing needle."""
    i = src.find(needle)
    if i == -1:
        return None
    start = None
    for m in re.finditer(r'\(0,t\.jsxs?\)\("section"', src):
        if m.start() <= i:
            start = m.start()
        else:
            break
    if start is None:
        return None
    # Walk from the call's OPENING argument paren, i.e. the one right after
    # `(0,t.jsx)` / `(0,t.jsxs)` — not the first '(' of that prefix.
    m = re.compile(r'\(0,t\.jsxs?\)').match(src, start)
    p = src.index("(", m.end())
    depth, k = 0, p
    in_str, quote, esc = False, "", False
    while k < len(src):
        ch = src[k]
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
                    return start, k + 1
        k += 1
    return None


def drop_section(src: str, needle: str, label: str) -> str:
    span = find_section_span(src, needle)
    if not span:
        print(f"  !! not found: {label}")
        return src
    a, b = span
    # Remove a trailing comma left behind in the children array.
    tail = b
    while tail < len(src) and src[tail] in " \n":
        tail += 1
    if tail < len(src) and src[tail] == ",":
        tail += 1
    print(f"  - removed {label} ({b - a} bytes)")
    return src[:a] + src[tail:]


def main():
    src = open(CHUNK, encoding="utf-8", errors="replace").read()
    before = len(src)

    if "Экосистема Naviora" not in src and "Mark Fingerman" in src:
        print("  = chunk already patched")
        return

    src = drop_section(src, "Инвестиции в доходную недвижимость", "services section")
    src = drop_section(src, '"ЭКОСИСТЕМА"', "ecosystem section")

    # Headline renames
    for old, new in [
        ("Naviora в цифрах", "Mark Fingerman в цифрах"),
        ("Связаться с командой", "Связаться с Марком"),
    ]:
        n = src.count(old)
        if n:
            src = src.replace(old, new)
            print(f"  ~ renamed {old!r} -> {new!r} ({n})")

    # The "4 / Вертикалей в экосистеме" stat is stale once the section is gone.
    m = re.search(r'\{[^{}]{0,200}?Вертикал[^{}]{0,200}?\}', src)
    if m:
        src = src[:m.start()] + src[m.end():]
        src = re.sub(r",\s*,", ",", src)
        print("  - removed verticals stat")

    # Section 05 ИЗБРАННЫЕ ОБЪЕКТЫ becomes 04 now that ecosystem is gone.
    src, k = re.subn(r'(children:")05("\}\),\(0,t\.jsx\)\("span",\{className:"t-h3",children:"ИЗБРАННЫЕ)',
                     r"\g<1>04\g<2>", src)
    if k:
        print(f"  ~ renumbered ИЗБРАННЫЕ ОБЪЕКТЫ 05 -> 04")

    open(CHUNK, "w", encoding="utf-8").write(src)
    print(f"  chunk: {before} -> {len(src)} bytes")


if __name__ == "__main__":
    main()
