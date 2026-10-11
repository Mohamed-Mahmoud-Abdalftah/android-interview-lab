# Build and validation evidence

## Current integrated verification — 2026-10-11

After the 48-day curriculum, specialist topics and mock packs were completed, the source inventory was regenerated before packaging. Every command below was observed in the current workspace; structural and browser checks still do not certify untested Android-device behavior.

From `projects/kotlin-jvm-labs/`, `./gradlew clean test check run --no-daemon` exited **0**, `BUILD SUCCESSFUL in 8s`; `run` printed `Ada` and `Guest`. Gradle XML reported **125 tests, 0 skipped, 0 failed, 0 errors.** `CompletionModelsTest` added 17 passing cases. Its first cancellation assertion exposed a real defect: broad `runCatching` converted `CancellationException` into data. The implementation now rethrows cancellation, and the controlled test observes the cancelled `Deferred`. This suite is Kotlin/JVM evidence; no Android SDK or device test ran.

`python3 -m unittest discover -s scripts -p 'test_*.py' -v` exited **0** with **45 tests passed**. Seven interview-quality tests verify the complete **300 question + 300 answer** bank, reject generic boilerplate and meta-prompts, keep Arabic out of the English model-answer sections, require the 160 rebuilt prompts to read as spoken interviewer questions, require a concrete mechanism in all 205 rebuilt answers, reject long copy-pasted paragraphs, and pin representative reasoning for Looper, Cold Flow, Hilt, interval merging and POS recovery. The package-source and validator suites verify that `node_modules` and every derived website copy, including mock packs, are excluded while reproducible site source stays in the archive.

The interview rebuild replaced **160 generated/meta prompts** with natural interviewer wording and rewrote **205 templated model answers** around the actual mechanism, failure, correction, adversarial test, wrong answer, answered follow-ups and separate English delivery. The DSA/live-coding set now includes concrete input contracts, Kotlin solutions, invariants and complexity traces. A coverage audit found **0 mechanism fallbacks**. `python3 scripts/validate.py` exited **0** with **Validation: 0 error(s)** against an inventory of **954 source files**.

From `site/`, `pnpm verify` exited **0**. Content sync generated **865 canonical Markdown files** with **48/48 core lessons ready**, five Node tests passed, Astro/Starlight built **872 HTML pages**, Pagefind indexed them, and `check-dist.mjs` verified the required lesson, question, scenario, lab and mock-interview routes, `lang="ar-EG"`, root RTL direction and every internal link. Browser QA used the local preview at desktop and **390×844**: the dashboard, lesson layout and question bank had no horizontal page overflow; the question filter returned the two Dijkstra matches; Practice Mode hid answers until reveal; and Pagefind returned StateFlow results. VS Code, Obsidian and a live hosted site were not visually inspected.

`python3 scripts/package_source.py` is rerun after the final inventory and validation gates. The source packager excludes generated/cache/ZIP/PYC entries and retains the official Gradle Wrapper JAR; its regression test compares two builds byte-for-byte.

## JUnit migration checkpoint — 2026-10-10

After replacing the assertion main with JUnit Jupiter 5.14.4, `./gradlew clean test check run --no-daemon` was executed in `projects/kotlin-jvm-labs/` and exited **0** with `BUILD SUCCESSFUL`. Gradle reported eight `PASSED` tests; `run` printed `Ada` and `Guest`. The generated `TEST-academy.LabChecksTest.xml` reported **tests=8, skipped=0, failures=0, errors=0**. A separate `./gradlew check --no-daemon --rerun-tasks` also executed all eight tests and exited **0**. JUnit dependencies resolved to Jupiter 5.14.4 and Platform launcher/engine 1.14.4. The unsafe Java platform-type dereference is asserted to throw `NullPointerException` in one educational regression test. Dependency setup follows the [official JUnit Gradle guide](https://docs.junit.org/5.14.4/running-tests/build-support.html).

The earlier `verifyLab` rows below are historical Batch 1 evidence, **not the current test setup**.

**Host observation on 2026-10-10:** macOS workspace; `java -version` reported Amazon Corretto OpenJDK `17.0.15`. A local Gradle `9.6.1` installation and Kotlin JVM plugin `2.4.20` were used; the official [Kotlin compatibility table](https://kotlinlang.org/docs/gradle-configure-project.html) lists that pairing within its supported range. The Gradle wrapper was generated from that installed distribution. This evidence covers the standalone JVM lab, **not** an Android APK or device.

| Sequence | Command / observed result |
|---|---|
| Red, before implementation | `gradle verifyLab --no-daemon` failed in `compileTestKotlin`: unresolved `safeLabelFromLegacy` and `ProfileName` in `LabChecks.kt`. |
| First integration attempt | `./gradlew clean check run --no-daemon` printed `Ada` and `Guest`, but Gradle `test` failed because the assertion-main test sources had no JUnit-discoverable tests. Compiler also warned that a private data-class constructor was exposed by generated `copy`. |
| Corrected JVM run | `./gradlew clean check run --no-daemon` exited **0**. Output included `run` → `Ada`, `Guest`; `test SKIPPED` by explicit design; `verifyLab` → `7 behavior checks passed`; `BUILD SUCCESSFUL in 7s`. |
| Validator unit tests | `python3 -m unittest discover -s scripts -p 'test_*.py' -v` exited **0**, five tests passed after the validator was implemented. Its initial red run failed with `ModuleNotFoundError: No module named 'validate'`; a later added duplicate-front-matter test failed as expected before its implementation. |

**Verification classes:** KOT-001 and LAB-001 code linked to `ProfileName.kt`: `tested` by eight JUnit invocations, including one expected exception from the intentionally unsafe Java expression. KOT-002 and LAB-002 code linked to `ProfileSemantics.kt`: `tested` by thirteen further invocations. KOT-003 and LAB-003 code linked to `Construction.kt`: `tested` by six further invocations. SCN-001's corrected boundary is covered by fake-SDK checks; its rollout plan is conceptual and unexecuted. SCN-002/003 are hypothetical investigations with no executed production reproducer. This historical checkpoint predates the later completed curriculum; prose examples without linked executable evidence still make no compilation claim.

**Not run:** CI, real Android SDK, emulator/device, production vendor SDK, Android capstone build, benchmarks, and payment simulator. This directory is not a Git repository, so there is no tested commit SHA.

## Historical first-batch final audit — 2026-10-10

Fresh `./gradlew clean check run --no-daemon` exited **0** with `Ada`, `Guest`, `7 behavior checks passed`, and `BUILD SUCCESSFUL in 5s`. Gradle's JUnit `test` task was explicitly skipped; the assertion runner passed. `python3 -m unittest discover -s scripts -p 'test_*.py' -v` exited **0**, **5 tests passed**. `python3 scripts/validate.py` exited **0**, **Validation: 0 error(s)**. An inventory script counted **51 source/artifact files** including [FILE-INVENTORY](FILE-INVENTORY.md) and excluding generated build/caches, **48 schedule days**, **5 question files and 5 answer files**, and **61 manifest entries: 8 reviewed, 53 planned**. The 8 reviewed entries are one lesson, five questions, one scenario, and one coding challenge; answer files are attached to their question entries.
