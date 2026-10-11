# Academy continuation instructions

- Canonical educational content stays in the existing root module, question, answer, scenario, lab, flashcard and speaking Markdown files. Do not hand-edit derived pages under `site/src/content/docs/{lessons,questions,answers,scenarios,labs,revision,speaking,reference}`.
- Run `site/scripts/sync-content.mjs` through `pnpm sync`; it derives website pages and `site/src/data/academy.json` from `CONTENT-MANIFEST.json`.
- Preserve Egyptian Arabic RTL prose and explicit LTR isolation for code, paths, commands and English answers.
- A lesson remains reviewed only with complete content, registered questions/answers, scenario, tested lab where applicable, sources and current verification evidence.
- After a coherent unit, run the Kotlin/JVM suite, Python validator suite, `scripts/validate.py`, `pnpm build`, regenerate `FILE-INVENTORY.md`, and rebuild the source ZIP.
- All 48 core units, 6 specialist units, 300 Q&A pairs, 50 scenarios, 30 labs and 8 mock packs are authored. Preserve the manifest relationships and do not downgrade device-dependent limitations into passing Android claims.
