# Verification report — 2026-10-12

## Coverage and review

`scripts/import_interview_lab.py` found 485 source questions, 485 unique IDs, and 21 topics. `python3 scripts/validate_interview_lab.py --require-complete` found 485 records, 485 marked reviewed, zero source-only, zero missing and zero automated quality errors. Every record preserves its verbatim canonical English question and includes the 14 required educational sections. There are 178 Kotlin fenced examples; 36 selected exact JVM-compatible fences are compiled by the Gradle suite. Android-dependent and conceptual snippets are labeled; they are not claimed to compile in this JVM harness.

Automated duplicate checks reject exact repeated Arabic explanations and Kotlin examples, copied long explanatory sentences in spoken answers, and stray text after the technical-review footer. A separate three-word-shingle comparison found no English deep-answer or Arabic explanation pair above 0.10 Jaccard overlap. One mid-topic question from each of the 21 topics was spot reviewed for relevance, examples, failure reasoning and citations. A further global footer scan removed 78 duplicate question lines, and the TST-09/19/20 examples were rewritten as executable JUnit tests. This is agent review and automated editorial evidence, not independent human review of all 485 answers.

## Executed checks

| Check | Observed result |
|---|---|
| Canonical source and complete editorial gate | 485/485, zero source-only and zero errors |
| Python validators | 51 unit tests pass; `scripts/validate.py` passes after inventory regeneration |
| Website JavaScript unit tests | 13 pass |
| Kotlin/JVM | `./gradlew clean test check run --no-daemon` succeeds; 128 JUnit tests pass, 36 exact canonical Kotlin fences compile |
| Fresh site dependencies | `pnpm install --frozen-lockfile` succeeds |
| Lint and Astro typecheck | Both pass; Astro reports zero errors, warnings or hints |
| Project-subpath production build | 1,390 static HTML pages, Pagefind search index and sitemap generated |
| Built route/link check | `GITHUB_REPOSITORY=test/android-interview-lab pnpm check:dist` passes with no broken internal links |
| Browser E2E and accessibility | 12 Playwright tests pass in installed Chrome under `/android-interview-lab/`; four WCAG A/AA axe scans report no violations on tested pages |
| External references | 979 citations, 291 distinct URLs: 291 reachable, zero confirmed broken or unverified in the final crawl; `reports/external-links.json` |
| Dependency audit | `pnpm audit --audit-level moderate` reports no known vulnerabilities after locking `postcss-selector-parser` 7.1.6 through `postcss-nested` 7.0.2; the full build and browser suite pass with this override |

The Playwright suite covers topic and exact/Arabic search, deep links, answer sections, persistence, flashcards, mock answer hiding/resume/recap, export/import, invalid import, 404, 320px RTL/LTR, first-visit offline reading and interaction, and accessibility on representative pages. The offline test caught a first-visit caching gap: the initial document and assets loaded before service-worker control. The current client primes those resources after service-worker activation; unopened pages still require a connection. An initial local browser run used a root-path build and failed eight study-flow tests; rebuilding with the required project base path made all 12 pass. The suite does not visit every route interactively. The static link checker covers all built internal links. Android device instrumentation, payment terminal certification, and production traffic testing were not performed; conclusions about those environments are explicitly limited in the content.

## Reproduce

```sh
python3 scripts/validate_interview_lab.py --require-complete
PYTHONPATH=scripts python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/validate.py
python3 scripts/check_interview_links.py
cd site
pnpm install --frozen-lockfile
pnpm lint && pnpm typecheck
GITHUB_REPOSITORY=test/android-interview-lab PUBLIC_SITE_URL=https://test.github.io pnpm build
GITHUB_REPOSITORY=test/android-interview-lab pnpm check:dist
pnpm test:e2e
cd ../projects/kotlin-jvm-labs
./gradlew clean test check run --no-daemon
```

The external-link crawl is network dependent. The GitHub Pages workflow repeats the offline deterministic release gates on each push to `main`. The first Pages deployment completed on 2026-10-12; the published home and a canonical question URL returned HTTP 200. See `docs/DEPLOYMENT.md` for the repository and live URL.
