# 48-day core study schedule

Eight weeks × six study days × about two hours = **96 hours**. Learning Mode is the default: read answers openly; timed mocks and scores require an explicit opt-in. A day is a plan, not a claim that every future lesson file already exists. Day 1 is [fully available](01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md); later IDs are planned in [CONTENT-MANIFEST](CONTENT-MANIFEST.json).

Daily default: **45 min explanation + 25 min guided reading/trace + 30 min hands-on + 10 min review + optional 10 min English speaking = 120 min**. If skipping speaking, use those ten minutes for review. Day 1 uses **55 + 20 + 25 + 10 + optional 10** to fit its lesson. Revision days use **30 + 20 + 35 + 25 + optional 10**. Do not stack all optional reading on top of the two hours.

Tags: **Must Learn** = core outcome; **Should Learn** = useful if time remains; **Optional Deep Dive** belongs to the extended path. All day rows below are Must Learn at the specified practical depth. See [ROADMAP](ROADMAP.md) for tier decisions.

## Week 1: Kotlin foundations and JVM boundary

**Study sequence:** Starts with basic coding fluency; see the [conceptual prerequisite map](PREREQUISITE-MAP.md).
**Competency:** Explain nullable/platform types, language building blocks, and complexity without confusing JVM with Android ART.
**Suggested free reading/listening:** [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html) and [null safety](https://kotlinlang.org/docs/null-safety.html). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Trace a Java-null input and explain why a Kotlin-only non-null parameter is different.
**Worked example preview:** The fake Java `nameFor("missing")` yields null → `ProfileName.parse` returns null → the optional label becomes `Guest`. This full trace is in KOT-001.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 1 | KOT-001 | Kotlin nullability and unannotated Java | Trace null/blank SDK results; LAB-001 and SCN-001 | 55/20/25/10/+10 |
| 2 | KOT-002 | val/var, types, equality and identity | Predict == versus === and mutation effects | 45/25/30/10/+10 |
| 3 | KOT-003 | Classes, constructors, initialization order | Trace property initialization and an open-member trap | 45/25/30/10/+10 |
| 4 | KOT-004 | Functions, lambdas and closures | Implement a callback adapter; explain capture | 45/25/30/10/+10 |
| 5 | KOT-005 | Generics, variance, erasure and reified | Review a producer/consumer API | 45/25/30/10/+10 |
| 6 | KOT-006 | Revision: JVM, DEX/ART boundary and Big-O | Re-explain Day 1; solve a small array task | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 2: Coroutines and Flow

**Study sequence:** Follows Week 1; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Trace scope ownership, cancellation, exception propagation, and cold/hot collection.
**Suggested free reading/listening:** [Kotlin coroutines overview](https://kotlinlang.org/docs/coroutines-overview.html) and [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Predict a cancellation path and write a deterministic test plan.
**Worked example preview:** A parent scope owns a child job; draw what is canceled when the parent is canceled, then test with one controlled scheduler. This is a preview, not a finished lesson.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 7 | COR-001 | suspend, dispatchers and structured scopes | Trace caller suspension versus thread blocking | 45/25/30/10/+10 |
| 8 | COR-002 | Job hierarchy, exceptions and supervision | Draw child failure propagation | 45/25/30/10/+10 |
| 9 | COR-003 | Cooperative cancellation and cleanup | Test cancellation with controlled scheduler | 45/25/30/10/+10 |
| 10 | COR-004 | Flow cold/hot, StateFlow and SharedFlow | Choose state versus event stream | 45/25/30/10/+10 |
| 11 | COR-005 | Latest operators, buffering and stale writes | Reproduce an out-of-order response | 45/25/30/10/+10 |
| 12 | COR-006 | Revision: deterministic coroutine tests and DSA | Explain virtual time; solve a hash-map task | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 3: Android platform internals

**Study sequence:** Follows Week 2; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Distinguish rotation, process death, background restrictions, and main-thread blocking.
**Suggested free reading/listening:** [Android Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Draw a restoration timeline and select evidence for an ANR.
**Worked example preview:** After rotation, a new Activity instance may use retained state; after process death, in-memory state is gone and must be restored from saved/persistent data. Exact Android restoration details are deferred to the lesson.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 13 | AND-001 | Activity, Fragment and view lifecycle | Trace view destruction separately from Fragment | 45/25/30/10/+10 |
| 14 | AND-002 | Configuration change and process death | Design saved-state recovery | 45/25/30/10/+10 |
| 15 | AND-003 | Tasks, intents, PendingIntent and export | Review one manifest exposure | 45/25/30/10/+10 |
| 16 | AND-004 | Looper, Handler, Binder and ANR evidence | Build an ANR triage timeline | 45/25/30/10/+10 |
| 17 | AND-005 | WorkManager, services, Doze and notifications | Choose a background-work mechanism | 45/25/30/10/+10 |
| 18 | AND-006 | Revision: adb evidence and DSA | Write a reproduction matrix; solve stack task | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 4: Architecture, DI and offline data

**Study sequence:** Follows Week 3; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Compare layered designs, state ownership, repository contracts, and Hilt scopes.
**Suggested free reading/listening:** [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data-layer guide](https://developer.android.com/topic/architecture/data-layer). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Defend two viable designs for one offline feature and test the chosen boundary.
**Worked example preview:** An offline task edit first updates the local source of truth, then syncs later; compare that with a network-first UI and name the conflict risk.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 19 | ARC-001 | SOLID and useful patterns | Refactor a coupled Android class | 45/25/30/10/+10 |
| 20 | ARC-002 | MVVM, UDF, state and events | Define UI state and one-off event policy | 45/25/30/10/+10 |
| 21 | ARC-003 | Repository, source of truth and offline-first | Draw cache and sync boundaries | 45/25/30/10/+10 |
| 22 | ARC-004 | Hilt scopes, qualifiers and DI tests | Find an accidental singleton session | 45/25/30/10/+10 |
| 23 | ARC-005 | Modules, contracts and ADRs | Compare two module boundaries | 45/25/30/10/+10 |
| 24 | ARC-006 | Revision: architecture code review and DSA | Write a short ADR and test plan | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 5: Views and Compose

**Study sequence:** Follows Week 4; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Explain View lifecycle, Compose state/effects, navigation ownership, and accessibility.
**Suggested free reading/listening:** [Android Compose state guide](https://developer.android.com/develop/ui/compose/state). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Trace one state update and diagnose a wrong effect key.
**Worked example preview:** A state value changes, so composables that read that state may recompose; explain why a wrong effect key can restart work unexpectedly.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 25 | UI-001 | Views, RecyclerView and Fragment binding | Fix a view-lifecycle leak | 45/25/30/10/+10 |
| 26 | UI-002 | Compose state and recomposition | Trace state hoisting | 45/25/30/10/+10 |
| 27 | UI-003 | Compose effects and lifecycle collection | Diagnose an effect-key bug | 45/25/30/10/+10 |
| 28 | UI-004 | Navigation ownership and back stack | Compare Navigation 2/3 only after version check | 45/25/30/10/+10 |
| 29 | UI-005 | Adaptive UI, RTL, a11y and performance | Inspect semantics and font-scale behavior | 45/25/30/10/+10 |
| 30 | UI-006 | Revision: UI tests and DSA | Design one accessible UI test; solve sliding window | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 6: Data, security, build and reliability

**Study sequence:** Follows Week 5; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Reason about Room migrations, networking failures, R8, release checks, and threat boundaries.
**Suggested free reading/listening:** [Android data layer](https://developer.android.com/topic/architecture/data-layer), [AGP migration](https://developer.android.com/build/migrate-to-built-in-kotlin), and [OWASP MASVS](https://mas.owasp.org/). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Write a failure-path release checklist with evidence sources.
**Worked example preview:** A network timeout does not establish whether a server committed the operation; compare safe retry with an idempotency contract and an unknown-outcome state.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 31 | PRO-001 | Room, migrations, WAL and DataStore | Plan a migration and recovery test | 45/25/30/10/+10 |
| 32 | PRO-002 | HTTP, timeouts, retries and token refresh | Separate timeout from unknown server outcome | 45/25/30/10/+10 |
| 33 | PRO-003 | Security and threat modeling | Review exported component and PII logging | 45/25/30/10/+10 |
| 34 | PRO-004 | Gradle, AGP 9, D8/R8 and signing | Verify a compatible toolchain before sample build | 45/25/30/10/+10 |
| 35 | PRO-005 | Profiling, startup and incident evidence | Define baseline and measurement method | 45/25/30/10/+10 |
| 36 | PRO-006 | Revision: release health and DSA | Write rollback criteria; solve binary search | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 7: System design and algorithmic depth

**Study sequence:** Follows Week 6; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Use invariants for coding tasks and draw client/backend boundaries in a mobile design.
**Suggested free reading/listening:** [Android data layer](https://developer.android.com/topic/architecture/data-layer) and [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Produce one tested algorithm and a trade-off table for sync.
**Worked example preview:** For a sorted array pair-sum, move one pointer based on whether the current sum is too small or large; state the invariant before coding.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 37 | SYS-001 | Arrays, maps, two pointers and invariants | Prove an O(n) solution | 45/25/30/10/+10 |
| 38 | SYS-002 | Trees, graphs, heaps and basic DP | Trace BFS and one recurrence | 45/25/30/10/+10 |
| 39 | SYS-003 | Mobile auth and session state design | Assign client/backend/OS responsibilities | 45/25/30/10/+10 |
| 40 | SYS-004 | Offline notes sync design | Compare conflict strategies | 45/25/30/10/+10 |
| 41 | SYS-005 | Messaging and realtime tracking design | Explain failure and observability boundaries | 45/25/30/10/+10 |
| 42 | SYS-006 | Revision: design review and concurrency | Present two designs and a controlled test | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Week 8: Integration and senior explanation

**Study sequence:** Follows Week 7; revisit weak IDs as needed. Individual conceptual prerequisites are in the [map](PREREQUISITE-MAP.md).
**Competency:** Review incidents, architecture decisions, testing, and spoken explanations without a mandatory mock.
**Suggested free reading/listening:** [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [coroutine testing](https://developer.android.com/kotlin/coroutines/test). Verify current accessibility before relying on specific videos; the linked official reading in [SOURCE-REGISTER](SOURCE-REGISTER.md) is the current checked set.
**Exit criterion:** Explain an end-to-end design, its failure mode, tests, and rollback.
**Worked example preview:** For a crash, record the environment and signature, reproduce, separate competing hypotheses, test a bounded fix, and define rollout monitoring.

| Day | ID | Focus | Guided example / small deliverable | Minutes |
|---:|---|---|---|---:|
| 43 | INT-001 | Capstone integration and tests | Review domain/data/UI interfaces | 45/25/30/10/+10 |
| 44 | INT-002 | Production incident response | Work a hypothetical crash from evidence | 45/25/30/10/+10 |
| 45 | INT-003 | Performance and security review | Prioritize measured risks | 45/25/30/10/+10 |
| 46 | INT-004 | Senior ownership and behavioral STAR | Draft a factual story template; no invented metrics | 45/25/30/10/+10 |
| 47 | INT-005 | English technical explanation practice | Record a 20s and 90s explanation privately | 45/25/30/10/+10 |
| 48 | INT-006 | Final revision and readiness evidence | Use checklist; optional mock only by request | 30/20/35/25/+10 |

Week review: explain one concept aloud, revisit the previous weak card, and record one concrete gap in [PROGRESS-TRACKER](PROGRESS-TRACKER.md).

## Spaced revision and continuation

Review a new concept next day, then around days 3, 7, 14, and 30; shorten the interval if you cannot trace or explain it. The schedule interleaves Kotlin, DSA, debugging, testing, and spoken explanation instead of confining them to one week. Core time excludes the cumulative 300-question and specialist libraries; see [ROADMAP](ROADMAP.md).
