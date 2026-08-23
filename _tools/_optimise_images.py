"""Resize and re-encode oversized listing images.

The developer CDNs serve full-resolution renders — several are 8 MB PNGs —
which is far more than a gallery on a property page needs and slow on a
phone. Cap the long edge and convert to JPEG, keeping the same filename so
listings.json needs no changes.

PNGs with meaningful transparency are left as PNG; none of the current set
has any, but converting one blind would black out its background.
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "projects")

MAX_EDGE = 1800      # comfortably above the largest slot the gallery renders
QUALITY = 82
THRESHOLD = 600_000  # only touch files big enough to be worth it


def has_alpha(im):
    if im.mode in ("RGBA", "LA"):
        return im.getchannel("A").getextrema()[0] < 255
    return im.mode == "P" and "transparency" in im.info


def main():
    saved = touched = 0
    for dirpath, _, files in os.walk(SRC):
        for name in sorted(files):
            if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            path = os.path.join(dirpath, name)
            before = os.path.getsize(path)
            if before < THRESHOLD:
                continue

            try:
                im = Image.open(path)
                im.load()
            except Exception:
                continue

            w, h = im.size
            if max(w, h) > MAX_EDGE:
                s = MAX_EDGE / max(w, h)
                im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)

            try:
                if has_alpha(im):
                    im.save(path, optimize=True)
                else:
                    im.convert("RGB").save(
                        path, "JPEG", quality=QUALITY, optimize=True,
                        progressive=True)
            except Exception:
                continue

            after = os.path.getsize(path)
            if after < before:
                saved += before - after
                touched += 1
                print(f"  {name:44} {before/1024/1024:5.1f} -> {after/1024/1024:4.1f} MB")

    print(f"\noptimised {touched} images, saved {saved/1024/1024:.0f} MB")


if __name__ == "__main__":
    main()
