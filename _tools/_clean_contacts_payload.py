"""
Remove the Партнёрство / Адрес / Юридическое лицо entries from the contacts
page's React hydration payload.

The payload serialises elements as  [\"$\",\"div\",null,{...}]  with
double-escaped quotes. Leaving these in means React re-injects the blocks on
hydration even though the visible HTML no longer contains them.

Idempotent.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "contacts", "index.html")

OPEN_DIV = '[\\"$\\",\\"div\\",null,'


def cut_entry(src: str, label: str):
    """Remove the serialised <div> element whose <dt> text is `label`."""
    marker = '\\"children\\":\\"%s\\"' % label
    removed = 0
    while True:
        i = src.find(marker)
        if i == -1:
            return src, removed
        start = src.rfind(OPEN_DIV, 0, i)
        if start == -1:
            return src, removed
        # Match brackets from the opening '[' of this element.
        depth, k, end = 0, start, None
        while k < len(src):
            ch = src[k]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end = k + 1
                    break
            k += 1
        if end is None:
            return src, removed
        tail = end
        if src[tail:tail + 1] == ",":
            tail += 1
        src = src[:start] + src[tail:]
        removed += 1


def main():
    s = open(PATH, encoding="utf-8", errors="replace").read()
    orig = s

    for label in ("Партнёрство", "Адрес", "Юридическое лицо"):
        s, n = cut_entry(s, label)
        if n:
            print(f"  payload: removed {n} × {label}")

    # The legal card is a section, not a dt/dd pair — remove any leftover
    # company / licence values that survived the element cut.
    for frag in ('\\"children\\":\\"Naviora Capital Real Estate L.L.C.\\"',
                 '\\"children\\":\\"1126816\\"'):
        if frag in s:
            # cut the whole enclosing dd element
            i = s.find(frag)
            start = s.rfind('[\\"$\\",\\"dd\\",null,', 0, i)
            if start != -1:
                depth, k, end = 0, start, None
                while k < len(s):
                    if s[k] == "[":
                        depth += 1
                    elif s[k] == "]":
                        depth -= 1
                        if depth == 0:
                            end = k + 1
                            break
                    k += 1
                if end:
                    tail = end
                    if s[tail:tail + 1] == ",":
                        tail += 1
                    s = s[:start] + s[tail:]
                    print("  payload: removed leftover legal value")

    if s != orig:
        open(PATH, "w", encoding="utf-8").write(s)
        print("  written")
    else:
        print("  no change")


if __name__ == "__main__":
    main()
