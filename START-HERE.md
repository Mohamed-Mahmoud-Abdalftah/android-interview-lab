# Start here — Day 1, Learning Mode

**Today: 120 minutes.** No pretest, timer, hidden answer, or score. You can begin even if Kotlin feels familiar: try to predict the Java boundary failure before reading the trace.

1. **55 min explanation:** Read [KOT-001](01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md). Pause at the table and trace `"ada"`, `"missing"`, and `"blank"` yourself.
2. **20 min guided code reading:** Open the [Java fake](projects/kotlin-jvm-labs/src/main/java/academy/LegacyProfileApi.java), [safe Kotlin boundary](projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt), and [JUnit tests](projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt). Explain each branch aloud.
3. **25 min hands-on:** Run the [lab](Coding-Challenges/LAB-001-profile-name.md), then compare the [hypothetical debugging case](Real-World-Scenarios/SCN-001-legacy-profile-null.md). If the build cannot run on your machine, trace the seven safe-behavior cases and the expected unsafe exception on paper; record that the local build is unrun.
4. **10 min review:** Read two of the [five questions with visible answers](Interview-Question-Bank/BY-TOPIC.md); keep the others for spaced review. Mark one weak point in [progress](PROGRESS-TRACKER.md).
5. **Optional 10 min speaking:** Use [Day 1 guided English](Speaking-Shadowing/DAY-01.md). If skipped, use the minutes for review.

**Exit check (unscored):** Explain why the unsafe Java call compiles, trace the blank branch, and name one test that catches the issue. If you cannot do those yet, revisit the trace before Day 2. [Full schedule](STUDY-SCHEDULE-48-DAYS.md) and [next authored batch](CONTINUE-HERE.md) are separate: the schedule is usable even while later lessons remain planned.

## Day 2 is ready when you are

Read [KOT-002](01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md), trace the alias and equality examples, then try [LAB-002](Coding-Challenges/LAB-002-profile-tags-and-keys.md). The [question index](Interview-Question-Bank/BY-TOPIC.md) shows KOT-Q006–010 beside their complete answers. The [mutable cache-key scenario](Real-World-Scenarios/SCN-002-mutable-cache-key.md), [revision cards](Flashcards-Revision/KOT-002.md), and [optional spoken practice](Speaking-Shadowing/DAY-02.md) reinforce the same concepts. No assessment is required before proceeding.

## Day 3

After Day 2, read [KOT-003](01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md) and predict the constructor trace before opening the [JUnit cases](projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt). Try [LAB-003](Coding-Challenges/LAB-003-construction-boundary.md), then use [KOT-Q011–015 with visible answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-003](Real-World-Scenarios/SCN-003-open-constructor-dispatch.md), [revision](Flashcards-Revision/KOT-003.md), and [optional English](Speaking-Shadowing/DAY-03.md). The exercise is unscored.

## Day 4

Read [KOT-004](01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md) and predict the fixed/live callback trace. Implement [LAB-004](Coding-Challenges/LAB-004-deferred-profile-request.md) before opening its [JUnit tests](projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt). Use [KOT-Q016–020 and visible answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-004](Real-World-Scenarios/SCN-004-stale-profile-callback.md), [revision](Flashcards-Revision/KOT-004.md), and [optional English](Speaking-Shadowing/DAY-04.md). No score is required.

## Day 7 — first coroutines lesson

After [KOT-004](01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md), read [COR-001](02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md). Trace the parent/child timeline, try [LAB-005](Coding-Challenges/LAB-005-profile-card-scope.md), then use [COR-Q001–005 and visible answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-005](Real-World-Scenarios/SCN-005-orphan-refresh.md), [revision](Flashcards-Revision/COR-001.md), and [optional speaking](Speaking-Shadowing/DAY-07.md). Days 5–6 remain planned; this path is conceptually supported by Day 4, while the schedule order is separate.

## Day 19 — first architecture lesson

After [KOT-003](01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md), read [ARC-001](04-Architecture-DI/arc-001-solid-and-useful-patterns.md). Try [LAB-006](Coding-Challenges/LAB-006-save-note-port.md), then use [ARC-Q001–005 and answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-006](Real-World-Scenarios/SCN-006-note-save-success-lie.md), [revision](Flashcards-Revision/ARC-001.md), and [optional English](Speaking-Shadowing/DAY-19.md). Earlier Android modules are still planned; do not treat the schedule gap as learner completion.

## Day 20 — MVVM, state and stale events

After [AND-001](03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md), read [ARC-002](04-Architecture-DI/arc-002-mvvm-udf-state-and-events.md). Implement [LAB-010](Coding-Challenges/LAB-010-editor-state-reducer.md), then work through [ARC-Q006–010](Interview-Question-Bank/BY-TOPIC.md), [SCN-011](Real-World-Scenarios/SCN-011-stale-editor-save-result.md), [revision](Flashcards-Revision/ARC-002.md), and [speaking practice](Speaking-Shadowing/DAY-20.md).

## Day 13 — first Android internals lesson

After [KOT-002](01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md), read [AND-001](03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md). Try [LAB-007](Coding-Challenges/LAB-007-view-session-owner.md), then [AND-Q001–005 and answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-007](Real-World-Scenarios/SCN-007-fragment-view-leak.md), [revision](Flashcards-Revision/AND-001.md), and [optional English](Speaking-Shadowing/DAY-13.md). The JVM exercise does not replace an Android lifecycle test.

## Day 37 — first algorithms unit

After [KOT-002](01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md), read [SYS-001](08-Mobile-System-Design/sys-001-arrays-maps-two-pointers-and-invariants.md), write both invariants, then try [LAB-008](Coding-Challenges/LAB-008-pair-search-invariants.md). Use [SYS-Q001–005 with answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-008](Real-World-Scenarios/SCN-008-overflow-batch-pair.md), [revision](Flashcards-Revision/SYS-001.md), and [optional English](Speaking-Shadowing/DAY-37.md). This unit starts the algorithms track but does not complete system design.

## Day 46 — senior ownership and behavioral practice

Read [INT-004](09-Leadership-English/int-004-senior-ownership-and-behavioral-star.md), fill the [blank personal evidence worksheet](09-Leadership-English/STAR-EVIDENCE-WORKSHEET.md) only with true facts, then use [INT-Q001–005 and visible coaching answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-009](Real-World-Scenarios/SCN-009-conflicting-release-owners.md), [revision](Flashcards-Revision/INT-004.md), and [optional speaking](Speaking-Shadowing/DAY-46.md). The scenario is hypothetical and is not a personal story.

## Day 25 — first Views lesson

After [AND-001](03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md), read [UI-001](05-Views-Compose/ui-001-views-recyclerview-and-fragment-binding.md). Try [LAB-009](Coding-Challenges/LAB-009-note-row-diff-policy.md), then [UI-Q001–005 with answers](Interview-Question-Bank/BY-TOPIC.md), [SCN-010](Real-World-Scenarios/SCN-010-stale-recyclerview-binding.md), [revision](Flashcards-Revision/UI-001.md), and [optional English](Speaking-Shadowing/DAY-25.md). The JVM policy tests do not execute AndroidX or render a Fragment view.
