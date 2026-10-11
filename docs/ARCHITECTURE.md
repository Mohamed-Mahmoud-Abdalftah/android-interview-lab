# Architecture

The existing Astro 7/Starlight academy remains the site shell and legacy curriculum. `CONTENT-MANIFEST.json` plus root academy Markdown generate its original lessons and 300 Q&A pairs via `site/scripts/sync-content.mjs`.

The new immutable question bank is parsed by `scripts/import_interview_lab.py` into `reports/source-manifest.json` and individual `Interview-Lab/questions/<ID>.md` records. The site sync reads those records and generates 485 canonical question pages plus 21 topic pages under `site/src/content/docs/lab/`. It does not erase hand-authored Lab utility pages. Each source record carries an editorial status. `scripts/validate_interview_lab.py` checks source fidelity and reviewed-section coverage independently from the older academy validator.

Static site search is supplied by Starlight/Pagefind. The Lab explorer loads only question metadata and a short Arabic explanation excerpt for reviewed pages. Per-question content is prerendered, so the browser does not hydrate all 485 answers. Browser-local study, review, and practice state is implemented in `site/public/scripts/lab-state.mjs` and `interview-lab.js`; no backend or sign-in is required. The review schedule uses local calendar days and documented intervals. Export/import uses versioned JSON.

`site/scripts/site-base.mjs` computes root or GitHub project base paths. `site/scripts/prefix-base.mjs` fixes remaining root-relative links in the built HTML, and `site/scripts/check-dist.mjs` checks every rendered internal link under the active base. The release workflow refuses deployment while canonical reviewed-answer coverage is below 485.
