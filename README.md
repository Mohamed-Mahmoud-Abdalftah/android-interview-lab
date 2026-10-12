# Android Interview Mastery Academy

## Android Interview Lab status

**Live site:** [Android Interview Lab](https://mohamed-mahmoud-abdalftah.github.io/android-interview-lab/).

This checkout contains the supplied **485-question, 21-topic Android Interview Lab**. All original IDs and English wording are preserved in individual records and 485 static routes. All 485 records now have authored explanations, examples, three English answer depths, follow-ups, rubrics, and references; no source-only pages remain. The `reviewed` field records automated editorial checks and agent technical review, not external human approval. The earlier academy's 300 Q&A pairs use different IDs and remain available separately.

From `site/`, run `pnpm install --frozen-lockfile`, `pnpm dev`, or `pnpm build && pnpm check:dist && pnpm test:e2e`. Run `python3 scripts/validate_interview_lab.py --require-complete` at the repository root for actual editorial coverage. See [verification](docs/VERIFICATION_REPORT.md), [content rules](docs/CONTENT_GUIDELINES.md), and [deployment](docs/DEPLOYMENT.md).

A study-first, local Senior Android engineering curriculum for an experienced Kotlin/Android engineer, including optional Staff and payment-device depth. The **core learner workload is 48 days × about 2 hours = 96 hours**; authoring all later material is a larger, separate effort. [START-HERE](START-HERE.md) opens a real Day 1 lesson and runnable JVM lab.

**Current state (2026-10-11):** The 48-day curriculum is authored and reviewed: 48 core lessons, six specialist topics, 300 complete question/answer pairs, 50 scenarios, 30 coding challenges and eight mock-interview packs. The executable Kotlin/JVM models have 125 passing JUnit tests. The [manifest](CONTENT-MANIFEST.json), [coverage](COVERAGE-MATRIX.md) and [verification record](BUILD-VERIFICATION.md) contain the exact evidence and environment limits.

The local RTL study website lives in [site](site/README.md). From that directory run `pnpm install --frozen-lockfile`, then `pnpm dev`; `pnpm verify` regenerates canonical content, builds the static site and checks every internal link.

## Navigate

- [Start learning](START-HERE.md) · [48-day schedule](STUDY-SCHEDULE-48-DAYS.md) · [roadmap](ROADMAP.md)
- [Day 1 lesson](01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md) · [Day 2 lesson](01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md) · [Day 3 lesson](01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md) · [Day 4 lesson](01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md) · [Day 5 lesson](01-Kotlin-JVM-ART/kot-005-generics-variance-erasure-and-reified.md) · [Day 6 lesson](01-Kotlin-JVM-ART/kot-006-revision-jvm-dex-art-boundary-and-big-o.md) · [Day 7 lesson](02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md) · [Day 13 lesson](03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md) · [Day 19 lesson](04-Architecture-DI/arc-001-solid-and-useful-patterns.md) · [Day 25 lesson](05-Views-Compose/ui-001-views-recyclerview-and-fragment-binding.md) · [Day 31 lesson](06-Production-Engineering/pro-001-room-migrations-wal-and-datastore.md) · [Day 37 lesson](08-Mobile-System-Design/sys-001-arrays-maps-two-pointers-and-invariants.md) · [Day 46 lesson](09-Leadership-English/int-004-senior-ownership-and-behavioral-star.md) · [question bank](Interview-Question-Bank/BY-TOPIC.md) · [scenarios](Real-World-Scenarios/SCN-018-quadratic-import-freeze.md) · [labs](Coding-Challenges/LAB-017-duplicate-scan-complexity.md)
- [Prerequisites](PREREQUISITE-MAP.md) · [revision](Flashcards-Revision/KOT-001.md) · [optional English](Speaking-Shadowing/DAY-01.md) · [progress](PROGRESS-TRACKER.md)
- [Quality gates](QUALITY-GATES.md) · [RTL authoring](RTL-STYLE-GUIDE.md) · [sources](SOURCE-REGISTER.md) · [build evidence](BUILD-VERIFICATION.md) · [actual file inventory](FILE-INVENTORY.md) · [limitations](ISSUES-AND-LIMITATIONS.md)

Learning Mode keeps answers visible. Assessment and timed simulation start only if explicitly requested. Technical explanations are in accessible Egyptian Arabic with English technical terms; code and interview answers use conventional English.

The JVM sample uses a fake Java SDK and no Android/payments integration. Android capstone implementation is pending compatible SDK/toolchain validation. No hiring outcome, benchmark improvement, payment certification, or CI status is claimed.
