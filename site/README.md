# Android Interview Mastery website

Astro 7.3.8 + Starlight 0.42.6 static website. The academy Markdown files one directory above `site/` are the canonical educational sources. `scripts/sync-content.mjs` derives Starlight pages and navigation data before every dev/build run; do not edit generated lesson, question, answer, scenario, lab, revision or speaking pages directly.

## Run locally

Requirements: Node.js 22.12+ and pnpm 11+. From this directory:

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:4321`. A production preview uses:

```sh
pnpm build
pnpm preview
```

The production build is written to `site/dist/`. Opening HTML through `file://` is unsupported because client routing and Pagefind search need a local HTTP origin. Once dependencies are installed, studying, progress storage and search need no backend, account or API key.

## Checks

```sh
pnpm test
pnpm build
pnpm check:dist
pnpm test:e2e
```

The browser tests use installed Google Chrome and serve the built snapshot under `/android-interview-lab/`; run `pnpm build` first. The interview lab stores progress under `android-interview-lab-v1` in browser `localStorage`; its dashboard exports/imports a validated versioned JSON file. The academy has a separate `android-academy-progress-v1` store. Nothing is uploaded by these study features.
