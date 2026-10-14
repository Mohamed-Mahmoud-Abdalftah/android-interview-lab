import { readdir, readFile, stat } from 'node:fs/promises';
import { extname, join, relative, resolve } from 'node:path';
import { siteBase } from './site-base.mjs';

const root = resolve(import.meta.dirname, '..');
const dist = join(root, 'dist');
const base = siteBase();

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  }));
  return nested.flat();
}

async function exists(path) {
  try { return (await stat(path)).isFile(); } catch { return false; }
}

function outputPath(urlPath) {
  const withoutBase = base === '/' ? urlPath : urlPath.startsWith(base) ? urlPath.slice(base.length) : urlPath;
  const decoded = decodeURIComponent(withoutBase).replace(/^\/+/, '');
  if (!decoded) return join(dist, 'index.html');
  if (urlPath.endsWith('/')) return join(dist, decoded, 'index.html');
  if (extname(decoded)) return join(dist, decoded);
  return join(dist, decoded, 'index.html');
}

const files = await walk(dist);
const htmlFiles = files.filter((path) => path.endsWith('.html'));
const errors = [];
const required = [
  'index.html',
  'study-path/index.html',
  'modules/index.html',
  'question-bank/index.html',
  'lessons/kot-001/index.html',
  'lessons/ext-dsa-01/index.html',
  'lessons/ext-pos-01/index.html',
  'pagefind/pagefind.js',
  'data/academy.json',
  'data/interview-lab.json',
  'lab/index.html',
  'lab/explore/index.html',
  'lab/review/index.html',
  'lab/practice/index.html',
  'lab/questions/kot-01/index.html',
  'lab/questions/pay-15/index.html',
  'ar/index.html',
  'ar/lab/index.html',
  'ar/lab/questions/kot-01/index.html',
  'ar/lab/questions/pay-15/index.html',
];

for (const name of required) {
  if (!(await exists(join(dist, name)))) errors.push(`missing required output: ${name}`);
}

const homeEn = await readFile(join(dist, 'index.html'), 'utf8');
const homeAr = await readFile(join(dist, 'ar/index.html'), 'utf8');
if (!/<html[^>]+lang="en"[^>]+dir="ltr"/.test(homeEn)) errors.push('English root home page must render lang="en" and dir="ltr"');
if (!/<html[^>]+lang="ar-EG"[^>]+dir="rtl"/.test(homeAr)) errors.push('Arabic home page must render lang="ar-EG" and dir="rtl"');
if (!homeEn.includes('Android Interview Lab')) errors.push('English home page is missing the product title');
if (!homeAr.includes('Android Interview Lab')) errors.push('Arabic home page is missing the product title');

for (const htmlPath of htmlFiles) {
  const html = await readFile(htmlPath, 'utf8');
  const route = `${base}${relative(dist, htmlPath).replace(/index\.html$/, '').replaceAll('\\', '/')}`;
  for (const match of html.matchAll(/\bhref=(?:"([^"]+)"|'([^']+)')/g)) {
    const href = match[1] ?? match[2];
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) continue;
    let url;
    try { url = new URL(href, `http://academy.local${route}`); } catch { continue; }
    if (url.origin !== 'http://academy.local') continue;
    if (base !== '/' && !url.pathname.startsWith(base)) {
      errors.push(`${relative(dist, htmlPath)} -> unprefixed path ${url.pathname}`);
      continue;
    }
    if (!(await exists(outputPath(url.pathname)))) {
      errors.push(`${relative(dist, htmlPath)} -> ${url.pathname}`);
    }
  }
}

const labPages = htmlFiles.filter((name) => relative(dist, name).startsWith('lab/questions/'));
if (labPages.length !== 485) errors.push(`expected 485 canonical question routes; found ${labPages.length}`);
const labPagesAr = htmlFiles.filter((name) => relative(dist, name).startsWith('ar/lab/questions/'));
if (labPagesAr.length !== 485) errors.push(`expected 485 Arabic canonical question routes; found ${labPagesAr.length}`);
if (htmlFiles.length < 1300) errors.push(`expected at least 1300 rendered pages; found ${htmlFiles.length}`);

if (errors.length) {
  console.error(`Static site verification failed with ${errors.length} issue(s):`);
  errors.slice(0, 50).forEach((error) => console.error(`- ${error}`));
  process.exitCode = 1;
} else {
  console.log(`Static site verified: ${htmlFiles.length} HTML pages, bilingual EN/AR routes, and internal links.`);
}
