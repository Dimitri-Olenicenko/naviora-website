"""
Post-build SEO patch for the Mark Fingerman static export.

The Next.js source for this site is not available, so these fixes are applied
to the exported HTML. They are idempotent: re-running will not duplicate tags.
If the site is ever rebuilt from source, port these into the source instead.
"""
import json
import os
import re

BASE = "https://olenicenko.com/naviora-website"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

listings = json.load(open(os.path.join(ROOT, "listings.json"), encoding="utf-8"))
by_slug = {l["slug"]: l for l in listings}

COUNTRY_NAME = {
    "dubai": ("Дубай", "AE"),
    "abudhabi": ("Абу-Даби", "AE"),
    "armenia": ("Ереван", "AM"),
    "georgia": ("Тбилиси", "GE"),
}

patched_canonical = 0
patched_jsonld = 0
skipped = 0


def page_url(relpath: str) -> str:
    """Map a file path to its canonical URL."""
    d = os.path.dirname(relpath).replace(os.sep, "/")
    return f"{BASE}/" if d in ("", ".") else f"{BASE}/{d}/"


for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "_next", "node_modules")]
    for fn in filenames:
        if not fn.endswith(".html"):
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        if rel.startswith("404"):
            continue

        html = open(full, encoding="utf-8", errors="replace").read()
        orig = html
        url = page_url(rel)

        # --- canonical -----------------------------------------------------
        if 'rel="canonical"' not in html:
            tag = f'<link rel="canonical" href="{url}"/>'
            html = html.replace("</head>", tag + "</head>", 1)
            patched_canonical += 1

        # --- JSON-LD -------------------------------------------------------
        if "application/ld+json" not in html:
            slug = os.path.basename(os.path.dirname(full))
            item = by_slug.get(slug)
            if item:
                city, cc = COUNTRY_NAME.get(item.get("country"), ("", ""))
                node = {
                    "@context": "https://schema.org",
                    "@type": "RealEstateListing",
                    "name": item.get("title"),
                    "url": url,
                    "description": item.get("shortDescription"),
                }
                addr = {"@type": "PostalAddress"}
                if item.get("address"):
                    addr["streetAddress"] = item["address"]
                if item.get("district"):
                    addr["addressLocality"] = item["district"]
                elif city:
                    addr["addressLocality"] = city
                if cc:
                    addr["addressCountry"] = cc
                if len(addr) > 1:
                    node["address"] = addr
                if item.get("lat") and item.get("lng"):
                    node["geo"] = {
                        "@type": "GeoCoordinates",
                        "latitude": item["lat"],
                        "longitude": item["lng"],
                    }
                if item.get("priceUsd"):
                    node["offers"] = {
                        "@type": "Offer",
                        "price": item["priceUsd"],
                        "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock",
                    }
                if item.get("developer"):
                    node["provider"] = {"@type": "Organization", "name": item["developer"]}
            elif rel == "index.html":
                node = {
                    "@context": "https://schema.org",
                    "@type": "RealEstateAgent",
                    "name": "Mark Fingerman",
                    "url": f"{BASE}/",
                    "areaServed": ["Dubai", "Abu Dhabi", "Yerevan", "Tbilisi"],
                }
            else:
                node = None

            if node:
                script = (
                    '<script type="application/ld+json">'
                    + json.dumps(node, ensure_ascii=False, separators=(",", ":"))
                    + "</script>"
                )
                html = html.replace("</head>", script + "</head>", 1)
                patched_jsonld += 1

        if html != orig:
            open(full, "w", encoding="utf-8").write(html)
        else:
            skipped += 1

print(f"canonical added : {patched_canonical}")
print(f"json-ld  added  : {patched_jsonld}")
print(f"unchanged       : {skipped}")
