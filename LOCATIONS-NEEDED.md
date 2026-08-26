# Locations still needed

_Updated 2026-08-26 — 36 of 37 listings are pinned._

Eight of the nine listings that previously showed no marker were resolved
against OpenStreetMap at **community level** (Madinat Al Mataar, Arabian
Ranches 3, Al Yalayis 5, Zabeel 2, Fahid Island, Al Bahyah, Al Ghadeer).

That is the accuracy the map already advertises to the visitor:

> Метки показывают расположение по району, а не точный контур здания.

So these pins are honest at the resolution claimed. Replacing any of them with
a building-exact coordinate from the developer's own page is still an upgrade —
just not a correction.

## Still unpinned (1)

| Проект | Застройщик | Район | Почему |
|---|---|---|---|
| The Brooks at Sobha Sanctuary | Sobha | Sobha Sanctuary | OpenStreetMap has no entry for Sobha Sanctuary. The nearest match is a *different* Sobha community (Hartland 2), which would put the pin in the wrong place, so the field stays empty. |

**To fill it in:** open the developer's project page, find the embedded Google
Maps link, and read the coordinates out of the `!8m2!3d<lat>!4d<lon>` part of
the URL. Put the pair on the listing in `listings.json` (`lat` / `lng`) — a
coordinate on the listing always wins over the fallback table in
`src/data/locations.ts`.

## Two listings share a pin

River Cove Residences and The Terraces are both inside Sobha City, Al Bahya, so
they resolve to the same community centroid and their markers sit on top of each
other. Both remain reachable from the list beside the map, which now shows every
object rather than the first eight.
