import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { siteBase } from './site-base.mjs';

const base = siteBase();
if (base !== '/') {
  const dist = path.join(path.dirname(path.dirname(fileURLToPath(import.meta.url))), 'dist');
  async function walk(folder) {
    for (const entry of await readdir(folder, { withFileTypes: true })) {
      const filename = path.join(folder, entry.name);
      if (entry.isDirectory()) await walk(filename);
      else if (filename.endsWith('.html')) {
        const source = await readFile(filename, 'utf8');
        const result = source.replace(/\b(href|src)=(['"])\/(?!\/)([^'"]*)\2/g, (whole, attr, quote, target) => {
          if (target.startsWith(base.slice(1))) return whole;
          return `${attr}=${quote}${base}${target}${quote}`;
        });
        if (result !== source) await writeFile(filename, result);
      }
    }
  }
  await walk(dist);
  console.log(`Prefixed root-relative HTML links for ${base}`);
}
