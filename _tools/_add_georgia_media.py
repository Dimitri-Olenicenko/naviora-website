"""Attach the VR Holding presentations and videos to the Georgia listings.

Presentations come from the Google Drive links behind each project's
"Download Presentation" button on vr.ge (the href is in the served HTML but
the button is styled as an overlay, so it is easy to miss). Each project
publishes three language variants; the English one was identified by
rendering page 2 of each and reading it, since the decks are image-only PDFs
with no extractable text.

Video IDs were verified live through the YouTube oEmbed endpoint.

Idempotent.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> (youtube id or None, brochure basename or None)
MEDIA = {
    "vr-shekvetili-forest-beach":    ("iysxeXK6Kwc", "vr-shekvetili-forest-beach"),
    "vr-krtsanisi-resort-residence": ("f2GmxSxcqwo", "vr-krtsanisi-resort-residence"),
    "vr-vake-sky-tower":             ("Qg98xW1adOo", "vr-vake-sky-tower"),
    "vr-multifunctional-building":   ("ZbjPm9Gn_qM", "vr-multifunctional-building"),
    "sairme-villa-residence":        ("zMlOu1tD1AY", "sairme-villa-residence"),
    "vr-resort-tbilisi":             ("LSZ5PfXRdTs", "vr-resort-tbilisi"),
    "vr-apartments-tbilisi":         ("y5o3twCzjOE", None),
    "vr-royal-townhouse":            ("PBaZzU8gpKo", None),
}

# Only pins that resolve to the actual site in OSM. Krtsanisi and Vake
# returned district centroids, which would drop the marker a few hundred
# metres away on an unrelated block, so they stay unpinned.
COORDS = {
    "vr-shekvetili-forest-beach": (41.9526199, 41.7647164),   # Paragraph Resort, adjacent site
    "sairme-villa-residence":     (41.7226579, 44.7645417),   # Sairme St, Saburtalo
}


def main():
    path = os.path.join(ROOT, "listings.json")
    listings = json.load(open(path, encoding="utf-8"))
    brochure_dir = os.path.join(ROOT, "assets", "brochures")

    vids = pdfs = pins = 0
    for x in listings:
        slug = x["slug"]
        if slug in MEDIA:
            vid, doc = MEDIA[slug]
            if vid and x.get("videoId") != vid:
                x["videoId"] = vid
                vids += 1
            if doc and os.path.exists(os.path.join(brochure_dir, doc + ".pdf")):
                x["brochure"] = f"/naviora-website/assets/brochures/{doc}.pdf"
                pdfs += 1
        if slug in COORDS and not x.get("lat"):
            x["lat"], x["lng"] = COORDS[slug]
            pins += 1

    json.dump(listings, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    ge = [x for x in listings if x["country"] == "georgia"]
    print(f"videos attached: {vids}")
    print(f"brochures attached: {pdfs}")
    print(f"coordinates set: {pins}")
    print(f"\ngeorgia listings ({len(ge)}):")
    for x in ge:
        print(f"  {x['title'][:34]:36} vid={'Y' if x.get('videoId') else '-'} "
              f"pdf={'Y' if x.get('brochure') else '-'} "
              f"pin={'Y' if x.get('lat') else '-'} img={len(x.get('images', []))}")


if __name__ == "__main__":
    main()
