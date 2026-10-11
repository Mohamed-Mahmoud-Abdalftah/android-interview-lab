# Change log

## 2026-10-10 — Hardening, RTL, Day 2, and full gap audit

- Replaced the custom assertion runner with JUnit Jupiter tests, including a regression that expects the unsafe Java platform-type dereference to throw. Expanded the runnable Kotlin/JVM lab for Day 2 equality, aliasing, snapshots, and stable cache keys; 21 JUnit invocations passed in a fresh clean build.
- Expanded the validator and its regression suite for front matter, conceptual prerequisites, registries, answer follow-ups, coverage, evidence, Markdown/HTML links, inventory, and common RTL structural mistakes. The Python suite passed 34 tests.
- Added reproducible source-only ZIP packaging, exact question/scenario/challenge/mock allocation, editorial review guidance, conceptual dependency mapping, and pending-source status for unauthored items.
- Applied semantic RTL markup to existing Arabic teaching prose; added an authoring guide, lesson template, mixed-language fixture, and local VS Code/Obsidian CSS support. GitHub Markdown API structure was inspected; graphical previews remain unverified.
- Authored KOT-002, KOT-Q006–010 with complete answers, SCN-002, LAB-002, Day 2 revision and optional English speaking. Reconciled their manifest, coverage and navigation entries.
- Audited the complete filesystem in [FULL-GAP-AUDIT](FULL-GAP-AUDIT.md); recorded the 46 missing core lessons, nine empty educational modules, long-term library gaps, and absent Android SDK/capstone implementation.
- Began Module 05 with UI-001, UI-Q001–005 and complete answers, SCN-010, LAB-009, revision and speaking practice. Four JVM tests cover row identity/content and list snapshot; AndroidX rendering and Fragment binding remain unbuilt. The clean JVM suite now has 55. 38 core lessons remain.
- Began Module 09 with INT-004, a blank personal STAR evidence worksheet, INT-Q001–005 and complete coaching answers, SCN-009, revision and speaking practice. The prose unit makes no executable or personal-experience claim. 39 core lessons remain.
- Began Module 08 with SYS-001, SYS-Q001–005 and full answers, SCN-008, LAB-008, revision and speaking practice. Seven pair-search JUnit tests cover indices, duplicates, overflow, sorted precondition and nonmutation; the clean suite now has 51. 40 core lessons remain.
- Began Module 03 with AND-001, AND-Q001–005 and complete answers, SCN-007, LAB-007, revision and speaking practice. Added four pure JVM view-owner tests; the clean suite now has 44. Android platform behavior remains documentation-based without an SDK build. 41 core lessons remain.
- Began Module 04 with ARC-001, ARC-Q001–005 and complete answers, SCN-006, LAB-006, revision and speaking practice. Added four NoteWriter/SaveNote JUnit tests; the clean suite now has 40. 42 core lessons remain.
- Began Module 02 with COR-001, COR-Q001–005 and complete answers, SCN-005, LAB-005, revision and speaking practice. Pinned coroutines core/test 1.11.0 and added three controlled-scheduler JUnit tests; 36 now pass cleanly. 43 core lessons remain.
- Added KOT-004 functions/lambdas/closures, KOT-Q016–020 with full answers, SCN-004, LAB-004, revision and speaking material. Six deferred-callback JUnit tests bring the clean JVM suite to 33 passing invocations. 44 core lessons remain.
- Continued to KOT-003 with constructor-order and invariant explanations, KOT-Q011–015 with full answers, SCN-003, LAB-003, revision and speaking material. Added six JUnit constructor tests; the clean JVM suite now executes 27 passing tests. The remaining core count is 45.

## 2026-10-10 — First batch

- Added 48-day 96-hour schedule, roadmap, prerequisite map, coverage matrix, and honest machine-readable catalog.
- Authored KOT-001, five separate question/answer pairs, SCN-001, LAB-001, a Day 1 speaking guide, and revision card.
- Added a standalone Kotlin/JVM Gradle lab with a Java platform-type fake and seven behavior checks; first Gradle run exposed a test-discovery mismatch and data-class copy warning, both addressed before the passing run.
- Added source register, local validation script and its initial tests, build evidence, quality gates, limitations, and continuation checkpoint.
