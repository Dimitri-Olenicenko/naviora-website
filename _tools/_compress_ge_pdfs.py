"""Compress the VR Holding presentation decks for the web.

Same approach as _compress_pdfs.py: these decks are 12-49 MB of full-bleed
renders, which is fine on a desktop download link and painful on a phone.
Reads _scrape/ge/pres/en_<slug>.pdf and writes assets/brochures/<slug>.pdf.
"""
import os
import shutil

from pypdf import PdfReader, PdfWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_scrape", "ge", "pres")
DEST = os.path.join(ROOT, "assets", "brochures")

QUALITY = 40
MAX_DIM = 1100


def compress(src, dst):
    before = os.path.getsize(src)
    reader = PdfReader(src)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        try:
            for img in page.images:
                try:
                    im = img.image
                    w, h = im.size
                    if max(w, h) > MAX_DIM:
                        s = MAX_DIM / max(w, h)
                        im = im.resize((int(w * s), int(h * s)))
                    img.replace(im, quality=QUALITY)
                except Exception:
                    continue
        except Exception:
            pass

    for page in writer.pages:
        try:
            page.compress_content_streams()
        except Exception:
            pass

    writer.compress_identical_objects()
    with open(dst, "wb") as fh:
        writer.write(fh)
    return before, os.path.getsize(dst)


def main():
    os.makedirs(DEST, exist_ok=True)
    tb = ta = 0
    for f in sorted(os.listdir(SRC)):
        if not f.startswith("en_") or not f.endswith(".pdf"):
            continue
        slug = f[3:-4]
        src = os.path.join(SRC, f)
        dst = os.path.join(DEST, slug + ".pdf")
        try:
            b, a = compress(src, dst)
        except Exception as e:
            print(f"  !! {slug}: {str(e)[:60]}")
            continue
        if a >= b:
            shutil.copy2(src, dst)
            a = b
            note = "(kept original)"
        else:
            note = f"-{100 - a * 100 // b}%"
        tb += b
        ta += a
        print(f"  {slug:34} {b/1024/1024:6.1f} -> {a/1024/1024:5.1f} MB  {note}")
    if tb:
        print(f"\n  TOTAL {tb/1024/1024:.0f} -> {ta/1024/1024:.0f} MB "
              f"({100 - ta * 100 // tb}% smaller)")


if __name__ == "__main__":
    main()
