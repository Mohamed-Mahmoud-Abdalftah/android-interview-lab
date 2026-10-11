# Verification report — 2026-10-11

This report distinguishes a verified partial build from the master prompt's full acceptance criteria.

## Coverage from actual scripts

`scripts/import_interview_lab.py` found 485 source questions, 485 unique IDs, and 21 topics with exact expected counts. The latest `scripts/validate_interview_lab.py` run found 485 records, 395 marked reviewed, 90 source-only, zero missing, and 460 editorial quality errors from copied long sentences in structured/deep English answers. Only 165 records currently pass all automated checks. The 90 source-only records and 230 reviewed records with quality findings block release. Per-question status and exact remaining IDs are in `reports/content-coverage.json`.

## Executed checks

| Check | Result | Evidence |
|---|---|---|
| Canonical source/content validation | Blocked editorially | 485 records; 395 reviewed; 90 source-only; 460 copied-sentence findings |
| Canonical Python unit tests | New quality tests pass, aggregate test fails as intended | Copied-sentence behavior is tested; the existing aggregate validation assertion fails while 460 content findings remain |
| Existing academy Python suite | Pass | 47 tests |
| Site JavaScript unit tests | Pass | 13 tests |
| Kotlin/JVM Gradle suite and canonical snippet compilation | Pass | `BUILD SUCCESSFUL` from `./gradlew clean test check run --no-daemon`; 125 tests, 0 failures/errors; exact Kotlin fences from COR-01, COR-02, FLO-06 and PAY-02 compiled |
| Astro project-subpath build | Pass at current 395-marked-reviewed snapshot | 1,388 HTML pages, Pagefind and sitemap generated; rebuild required after all content changes |
| Built internal-link check | Pass at current 395-marked-reviewed snapshot | `GITHUB_REPOSITORY=test/android-interview-lab pnpm check:dist`; 0 broken internal links; rerun at release |
| Browser smoke, project subpath | Pass for exercised paths | Reviewed question, bookmark/note reload, Arabic search, SRS date, timed mock resume/recap; RTL Arabic text and no horizontal overflow at 320px/390px; no console errors on checked page |
| Full editorial release gate | Fail | 90 canonical answers need authoring and 230 marked-reviewed records have copied-sentence findings |
| GitHub Pages deployment | Not run | No GitHub remote or Pages settings; release gate blocks incomplete publication |

No automated Playwright E2E, full external-link crawl, or Android device/instrumentation pass is claimed. SEC-12 uses Android APIs and was not compiled in the JVM suite. The earlier browser smoke checked selected paths, not all 1,388 rendered pages interactively. The latest Kotlin/JVM suite passed 125 tests, and the academy validator passed; these do not override the failed Interview Lab editorial gate.

## Next deterministic checkpoint

Run `python3 scripts/validate_interview_lab.py` from the repository root. Its reviewed/source-only counts determine what editorial work remains. The site can be rebuilt with `cd site && pnpm build && pnpm check:dist`. Release requires `python3 scripts/validate_interview_lab.py --require-complete` to pass and a verified Pages deployment.
