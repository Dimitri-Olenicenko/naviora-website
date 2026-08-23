"""
Compress the developer brochures so they can ship with the site.

The originals total 319 MB (largest 68 MB), which is too heavy for a GitHub
Pages repo and a poor experience on mobile. This downsamples the embedded
images and re-compresses streams with pypdf.

Writes to assets/brochures/<slug>.pdf. Reports the before/after for each file
and skips any where compression achieved nothing useful.
"""
import os
import sys

from pypdf import PdfReader, PdfWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "assets", "brochures")

# folder (under projects/) -> output slug
MAP = {
    "dubai/office samana": "samana-barari-avenue",
    "dubai/hq rove office": "hq-by-rove",
    "dubai/azizi office": "azizi-emerald",
    "dubai/villa dubai sobha": "the-brooks-sobha-sanctuary",
    "dubai/villa hayat": "hayat-6-dubai-south",
    "dubai/villa Arabian Ranches 3": "athlon-by-aldar",
    "dubai/emaar villa": "serro-2-the-heights",
    "dubai/difc apartment": "residences-difc-zabeel",
    "dubai/eywa": "eywa-business-bay",
    "dubai/creek apartment": "aeon-creek-harbour",
    "abu dhabi/man apart": "manchester-city-yas-residences",
    "abu dhabi/fair month apt": "fairmont-marina-residences",
    "abu dhabi/aldar apt": "beach-house-fahid",
    "abu dhabi/sobha apt": "river-cove-sobha-city-ad",
    "abu dhabi/sob villa": "the-terraces-sobha-city-ad",
    "abu dhabi/another villa abu aldar": "al-ghadeer-gardens",
}

QUALITY = 40       # JPEG quality for embedded images
MAX_DIM = 1100     # cap the longest edge of any embedded image


def compress(src: str, dst: str) -> tuple[int, int]:
    before = os.path.getsize(src)
    reader = PdfReader(src)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Downsample embedded images where the library supports it.
    for page in writer.pages:
        try:
            for img in page.images:
                try:
                    im = img.image
                    w, h = im.size
                    if max(w, h) > MAX_DIM:
                        scale = MAX_DIM / max(w, h)
                        im = im.resize((int(w * scale), int(h * scale)))
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
    only = sys.argv[1] if len(sys.argv) > 1 else None
    tot_before = tot_after = 0

    for folder, slug in MAP.items():
        if only and only != slug:
            continue
        src_dir = os.path.join(ROOT, "projects", *folder.split("/"))
        if not os.path.isdir(src_dir):
            print(f"  !! missing folder: {folder}")
            continue
        pdfs = [f for f in os.listdir(src_dir) if f.lower().endswith(".pdf")]
        if not pdfs:
            print(f"  -- no pdf in {folder}")
            continue

        src = os.path.join(src_dir, pdfs[0])
        dst = os.path.join(DEST, slug + ".pdf")
        try:
            b, a = compress(src, dst)
        except Exception as e:
            print(f"  !! failed {slug}: {str(e)[:60]}")
            continue

        # If compression made it bigger, keep the original instead.
        if a >= b:
            import shutil
            shutil.copy2(src, dst)
            a = b
            note = "(kept original — compression gained nothing)"
        else:
            note = f"-{100 - a * 100 // b}%"

        tot_before += b
        tot_after += a
        print(f"  {slug:32} {b/1024/1024:6.1f} -> {a/1024/1024:6.1f} MB  {note}")

    if tot_before:
        print(f"\n  TOTAL {tot_before/1024/1024:.0f} MB -> {tot_after/1024/1024:.0f} MB "
              f"({100 - tot_after * 100 // tot_before}% smaller)")


if __name__ == "__main__":
    main()
