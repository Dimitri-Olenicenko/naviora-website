/**
 * Render a page with a real browser and dump everything worth harvesting:
 * text, images, PDFs, videos, map coordinates.
 *
 * These three sites all build their project pages client-side, so plain
 * curl returns a shell. Usage:  node scrape.mjs <url> <outfile.json>
 */
import puppeteer from 'puppeteer';
import fs from 'fs';

const [, , url, out] = process.argv;
if (!url || !out) {
  console.error('usage: node scrape.mjs <url> <out.json>');
  process.exit(1);
}

const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 1000 });
await page.setUserAgent(
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
);

// Map tiles and analytics are requested lazily; capture any coordinates
// that leak through network calls since the DOM often hides them.
const netCoords = new Set();
const netPdfs = new Set();
page.on('request', (r) => {
  const u = r.url();
  const m = u.match(/(-?\d{2}\.\d{4,}),\s*(-?\d{2}\.\d{4,})/);
  if (m) netCoords.add(`${m[1]},${m[2]}`);
  if (/\.pdf(\?|$)/i.test(u)) netPdfs.add(u);
});

try {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 90000 });
} catch {
  // networkidle2 times out on sites with polling; the DOM is usually ready.
}
await new Promise((r) => setTimeout(r, 3500));

// Trigger lazy-loaded galleries and maps.
await page.evaluate(async () => {
  for (let y = 0; y < document.body.scrollHeight; y += 700) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 220));
  }
  window.scrollTo(0, 0);
});
await new Promise((r) => setTimeout(r, 2500));

const data = await page.evaluate(() => {
  const abs = (u) => { try { return new URL(u, location.href).href; } catch { return null; } };
  const html = document.documentElement.outerHTML;

  const imgs = new Set();
  document.querySelectorAll('img').forEach((el) => {
    for (const a of ['src', 'data-src', 'data-lazy-src', 'data-original']) {
      const v = el.getAttribute(a);
      if (v && !/^data:/.test(v)) { const u = abs(v); if (u) imgs.add(u); }
    }
    (el.getAttribute('srcset') || '').split(',').forEach((s) => {
      const u = abs(s.trim().split(/\s+/)[0]);
      if (u && !/^data:/.test(u)) imgs.add(u);
    });
  });
  document.querySelectorAll('*').forEach((el) => {
    const bg = getComputedStyle(el).backgroundImage || '';
    const m = bg.match(/url\(["']?([^"')]+)/);
    if (m && !/^data:/.test(m[1])) { const u = abs(m[1]); if (u) imgs.add(u); }
  });

  const links = new Set();
  document.querySelectorAll('a[href]').forEach((a) => {
    const u = abs(a.getAttribute('href'));
    if (u) links.add(u);
  });

  const vids = new Set();
  const rxY = /(?:youtube(?:-nocookie)?\.com\/(?:embed\/|watch\?v=)|youtu\.be\/)([\w-]{11})/g;
  let m;
  while ((m = rxY.exec(html))) vids.add(m[1]);
  document.querySelectorAll('iframe[src], video source[src], video[src]').forEach((f) => {
    const u = abs(f.getAttribute('src'));
    if (u) vids.add(u);
  });

  const coords = new Set();
  const rxs = [
    /!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/g,
    /["'](?:lat|latitude)["']?\s*[:=]\s*["']?(-?\d+\.\d{3,})["']?\s*,\s*["']?(?:lng|lon|longitude)["']?\s*[:=]\s*["']?(-?\d+\.\d{3,})/gi,
    /@(-?\d+\.\d{4,}),(-?\d+\.\d{4,})/g,
  ];
  for (const rx of rxs) while ((m = rx.exec(html))) coords.add(`${m[1]},${m[2]}`);

  return {
    url: location.href,
    title: document.title,
    text: document.body.innerText.replace(/\n{3,}/g, '\n\n').trim(),
    headings: [...document.querySelectorAll('h1,h2,h3')]
      .map((h) => h.innerText.trim()).filter(Boolean).slice(0, 60),
    images: [...imgs],
    links: [...links],
    videos: [...vids],
    coords: [...coords],
  };
});

data.netCoords = [...netCoords];
data.netPdfs = [...netPdfs];
data.pdfs = [...new Set([...data.links.filter((l) => /\.pdf(\?|$)/i.test(l)), ...netPdfs])];

fs.writeFileSync(out, JSON.stringify(data, null, 2), 'utf8');
console.log(
  `${data.title.slice(0, 52)} | text=${data.text.length} imgs=${data.images.length} ` +
  `pdf=${data.pdfs.length} vid=${data.videos.length} coord=${data.coords.length}`
);

await browser.close();
