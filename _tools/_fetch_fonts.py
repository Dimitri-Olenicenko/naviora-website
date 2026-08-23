"""Self-host the display serif, with Cyrillic coverage.

The compiled CSS asks for "Gerbera" and "Suisse Intl" but the build ships no
@font-face for either — document.fonts.size is 0 on the live site — so every
visitor has been reading Arial/Helvetica. Naming a font you do not serve is
the same as not choosing one.

Playfair Display is used for headings because it actually ships Cyrillic
(unicode-range U+0400-045F), which the references the research measured —
Tiempos Headline, Heldane — do not. On a Russian-language site that is not a
stylistic preference but a hard requirement.

Files are downloaded and served from assets/fonts rather than linked to
fonts.gstatic.com: one less third-party connection on first paint, no
dependency on Google staying reachable, and no visitor data leaving our host.
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "fonts")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# family -> (google css url, weights we keep)
FAMILIES = {
    "playfair": (
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600"
        "&display=swap&subset=cyrillic,latin",
        "Playfair Display",
    ),
}

# Only these two ranges matter for a Russian site with Latin project names.
WANTED_RANGES = ("cyrillic", "latin")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=45).read()


def main():
    os.makedirs(DEST, exist_ok=True)
    faces = []

    for key, (css_url, family) in FAMILIES.items():
        css = get(css_url).decode("utf-8", "ignore")

        # Each @font-face is preceded by a /* subset */ comment.
        blocks = re.split(r"/\*\s*([a-z-]+)\s*\*/", css)
        # blocks = ['', 'cyrillic', '<face>', 'vietnamese', '<face>', ...]
        for i in range(1, len(blocks) - 1, 2):
            subset, body = blocks[i], blocks[i + 1]
            if subset not in WANTED_RANGES:
                continue
            m_url = re.search(r"src:\s*url\((https://[^)]+\.woff2)\)", body)
            m_w = re.search(r"font-weight:\s*(\d+)", body)
            m_r = re.search(r"unicode-range:\s*([^;]+);", body)
            if not (m_url and m_w):
                continue

            weight = m_w.group(1)
            name = f"{key}-{weight}-{subset}.woff2"
            path = os.path.join(DEST, name)
            if not os.path.exists(path):
                open(path, "wb").write(get(m_url.group(1)))
            faces.append({
                "family": family,
                "weight": weight,
                "file": name,
                "range": m_r.group(1).strip() if m_r else None,
                "size": os.path.getsize(path),
            })
            print(f"  {name:34} {os.path.getsize(path)/1024:5.1f} KB  {subset}")

    total = sum(f["size"] for f in faces)
    print(f"\n{len(faces)} font files, {total/1024:.0f} KB total")

    # Emit the @font-face block for the CSS patcher to append.
    out = []
    for f in faces:
        out.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
            "font-display:swap;src:url('/naviora-website/assets/fonts/%s') "
            "format('woff2');%s}" % (
                f["family"], f["weight"], f["file"],
                f"unicode-range:{f['range']};" if f["range"] else ""))
    open(os.path.join(DEST, "_faces.css"), "w", encoding="utf-8").write(
        "\n".join(out))
    print("wrote assets/fonts/_faces.css")


if __name__ == "__main__":
    main()
