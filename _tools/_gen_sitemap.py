"""Generate sitemap.xml and robots.txt for the Naviora static export."""
import os
from datetime import date

BASE = "https://olenicenko.com/naviora-website"
ROOT = os.path.dirname(os.path.abspath(__file__))
today = date.today().isoformat()

urls = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "_next", "node_modules")]
    if "index.html" not in filenames:
        continue
    rel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
    if rel.startswith("404") or rel.startswith("_not-found"):
        continue
    loc = f"{BASE}/" if rel == "." else f"{BASE}/{rel}/"

    # Depth-based priority: home > country/section > individual listing.
    depth = 0 if rel == "." else rel.count("/") + 1
    priority = {0: "1.0", 1: "0.9", 2: "0.8"}.get(depth, "0.7")
    # The Dubai landing page is a redirect stub — keep it out of the sitemap.
    if rel == "dubai":
        continue
    if rel == "backoffice":
        continue
    if rel == "about":
        continue
    urls.append((loc, priority))

urls.sort(key=lambda x: (-float(x[1]), x[0]))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, pr in urls:
    lines.append(
        f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>{pr}</priority></url>"
    )
lines.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

robots = f"""User-agent: *
Allow: /
Disallow: /naviora-website/backoffice/

Sitemap: {BASE}/sitemap.xml
"""
open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)

print(f"sitemap.xml: {len(urls)} URLs")
print("robots.txt : written (backoffice disallowed)")
