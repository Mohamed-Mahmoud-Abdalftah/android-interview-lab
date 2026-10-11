# Roadmap

## Core: 96 learner hours

[All 48 days and minute budgets](STUDY-SCHEDULE-48-DAYS.md). The progression is Kotlin foundations → coroutines/Flow → Android internals → architecture/DI → Views/Compose → data/build/security/performance → system design/DSA → integration and senior communication. Each week retains DSA, debugging, testing, and optional English practice. Sixteen core days are authored and 32 remain planned; [coverage](COVERAGE-MATRIX.md) is the exact per-day record.

**Must Learn:** the core day's ability to trace behavior, build or review a small example, justify a trade-off, and name a test. **Should Learn:** adjacent variants and production evidence beyond the two-hour day. **Optional Deep Dive:** specialist APIs, extensive algorithms, and platform/compiler internals in the extended path. A learner can progress after demonstrating the competency, rather than reading a target page count.

## Extended: 4–8+ further weeks if useful

Advanced ART/JNI, deep concurrency, Navigation migration by pinned version, harder graphs/DP, Staff architecture, and fake POS/EMV/NFC scenarios are represented in [coverage](COVERAGE-MATRIX.md). An educational payment simulator must use fake server/device interfaces and no real PAN/PIN, keys, funds, or certification claim. The 300-question, 50-scenario, 30-challenge, and 8 mock-pack totals are cumulative library targets, not required within 96 hours. No timed mock is launched in Learning Mode.

## Six practice styles

| Style | Distinct focus | Current material |
|---|---|---|
| Product Android | Kotlin boundary, lifecycle, Compose, code review | [KOT-Q001](Interview-Question-Bank/Questions/KOT-Q001.md) |
| Algorithms-heavy | Invariant, complexity, coding constraints | [Dijkstra lab](Coding-Challenges/LAB-013-dijkstra-shortest-path.md) |
| Architecture/system design | Requirements, alternatives, observability | [KOT-Q004](Interview-Question-Bank/Questions/KOT-Q004.md) as a small boundary decision |
| Production debugging | Evidence, competing causes, rollout | [SCN-001](Real-World-Scenarios/SCN-001-legacy-profile-null.md) |
| Mobile security/POS | Threat boundary and fake payment state | [Security](06-Production-Engineering/pro-003-security-and-threat-modeling.md) and [POS](10-Optional-POS-Specialist/ext-pos-01.md) |
| Behavioral/English | Factual STAR stories and natural spoken explanation | [Day 1 speaking](Speaking-Shadowing/DAY-01.md) |

Each style should point to the same factual lesson ID rather than duplicate the teaching. [Prerequisite map](PREREQUISITE-MAP.md) shows the learning dependencies.
