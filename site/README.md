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
```

Progress stays in browser `localStorage` under `android-academy-progress-v1`. The dashboard exports/imports a validated versioned JSON file; nothing is uploaded.
