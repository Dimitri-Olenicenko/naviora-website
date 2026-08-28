# naviora-website — DEPLOYED TREE (source of truth)

**This repository IS production.** GitHub Pages serves the root of `main` at `https://olenicenko.com/naviora-website/`.
A push to `main` is live within a minute; there is no build step, no staging, no release tag.

## Read before touching anything

1. **Do not regenerate this tree from the Studio `app/` source.** The Next.js source in the Studio harness
   (`clients/naviora/projects/website-2026/app`) is a stale August-17 snapshot — 28 listings vs 37 here, 2 vs 30 root
   pages. A plain `next build` + deploy from `app/` would silently delete 9 listings and 28 detail pages. Edit the
   built files in this tree directly, or re-align `app/` first and diff the export against this tree before deploying.
2. **`listings.json` is written by the back office** (Cloudflare Worker `naviora-backoffice`, `POST /publish` → GitHub
   Contents API commit "Back office: update listings"). Every publish is a commit; `git revert` is the rollback.
3. **Uploaded media lives only in the R2 bucket `naviora-media`** (public URL base in the worker config). It is NOT in
   this repo and has no backup yet — do not delete objects without a copy.
4. **The `en_*.html` / `hy_*.html` files at the root and the `_tools/` scrapers are raw developer material** carried over
   from the original site scrape. They embed the source developer's third-party trackers and are crawlable; they are
   scheduled for removal (delivery-gate findings 2026-08-28) — do not link to them.
5. **Branch protection, tags and CI do not exist yet** (see the Studio delivery-gate records). Until they do: never
   force-push, never commit from an unreviewed script, never commit a secret (the back-office password, the session
   secret and the GitHub token are Cloudflare `wrangler secret`s and must stay there).

## Where the rest lives

- Design spec, copy baseline, worker source, security and delivery-gate records: Studio harness
  `clients/naviora/projects/website-2026/` (private).
- Back-office setup: `backoffice-worker/SETUP.md` in the Studio tree (private) — the back office page here
  (`backoffice/index.html`) only talks to the worker; it holds no credentials.

_Added 2026-08-28 as the in-repo divergence safeguard requested by the version-control health check; no content change._
