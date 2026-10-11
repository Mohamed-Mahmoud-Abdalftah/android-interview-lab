# Kotlin/JVM labs

JDK 17, Gradle 9.6.1, Kotlin JVM plugin 2.4.20, and JUnit Jupiter 5.14.4. These versions are for this standalone JVM lab, not an Android build.

From this directory run `./gradlew clean test check run --no-daemon`. Gradle discovers the JUnit Jupiter tests in `src/test/kotlin`; `check` also runs `test`. The Day 1 suite covers seven behavior cases and one expected exception at the unsafe Java boundary. Expected `run` output: `Ada`, then `Guest`.

The unannotated Java method models a vendor SDK returning unexpected null. [`ProfileName.kt`](src/main/kotlin/academy/ProfileName.kt) handles it at the boundary. The exercise is to predict why `LegacyProfileApi.nameFor("missing").length` compiles in Kotlin and what happens at runtime; then explain why `safeLabelFromLegacy` avoids that failure.

## Day 2: equality, aliasing, and mutable Java collections

[`ProfileSemantics.kt`](src/main/kotlin/academy/ProfileSemantics.kt) contains a mutable `ProfileDraft`, its list-detaching `detachedCopy()`, an immutable `ProfileKey` for map lookups, and a function that normalizes and snapshots tags returned by the unannotated Java method. [`ProfileSemanticsTest.kt`](src/test/kotlin/academy/ProfileSemanticsTest.kt) runs the examples as JUnit tests. Try [LAB-002](../../Coding-Challenges/LAB-002-profile-tags-and-keys.md) before reading the implementation.

`val` fixes a reference, not the contents of a mutable list. A data-class `copy()` is shallow; `detachedCopy()` copies the tag list because its elements are immutable strings. A Kotlin `List` return type offers read-only access to Kotlin callers, but should not be described as deeply immutable. For cache keys, use `ProfileKey` with `val` constructor properties. Java's `Map` contract leaves behavior unspecified if a key changes in a way that affects equality while it is in a map, so the tests verify lookup with equal immutable keys instead of asserting a particular failure from a mutated key. See the official [Kotlin data-class](https://kotlinlang.org/docs/data-classes.html), [equality](https://kotlinlang.org/docs/equality.html), [collections](https://kotlinlang.org/docs/collections-overview.html), [Java interoperability](https://kotlinlang.org/docs/java-interop.html), and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) references.

The JUnit dependency BOM and launcher follow the [JUnit 5.14.4 Gradle guide](https://docs.junit.org/5.14.4/running-tests/build-support.html). JUnit 5 supports Java 8 and later per its [versioned overview](https://docs.junit.org/5.14.4/overview.html); Gradle's [JVM test guide](https://docs.gradle.org/current/userguide/java_testing.html) documents `useJUnitPlatform()`.

## Day 3: constructor order and invariant boundary

[`Construction.kt`](src/main/kotlin/academy/Construction.kt) records primary/secondary constructor order and defines a guarded `EndpointConfig` factory. [`ConstructionTest.kt`](src/test/kotlin/academy/ConstructionTest.kt) checks six cases: source-order interleaving, secondary delegation, early validation failure, invalid host/port, and normalized valid input. [LAB-003](../../Coding-Challenges/LAB-003-construction-boundary.md) is the exercise. The unsafe open-dispatch hierarchy in the lesson is a source-review sketch, not an executed reference implementation. The [official classes](https://kotlinlang.org/docs/classes.html) and [inheritance](https://kotlinlang.org/docs/inheritance.html) guides support the order claims.

## Day 4: deferred callback timing

[`DeferredRequest.kt`](src/main/kotlin/academy/DeferredRequest.kt) reads a profile ID through a provider at invocation time. [`DeferredRequestTest.kt`](src/test/kotlin/academy/DeferredRequestTest.kt) covers six cases: no eager read, changed selection, null/blank, trimming, repeated invocations and exception propagation. Try [LAB-004](../../Coding-Challenges/LAB-004-deferred-profile-request.md) first. The example is synchronous; it does not model lifecycle or network response ordering.

## Day 7: structured coroutines

[ProfileCard.kt](src/main/kotlin/academy/ProfileCard.kt) starts two independent async children inside a parent-owned scope on an injected dispatcher. [ProfileCardTest.kt](src/test/kotlin/academy/ProfileCardTest.kt) uses coroutines-test 1.11.0, one test scheduler and CompletableDeferred gates for three cases: waiting for both children, failure propagation and parent cancellation. Try [LAB-005](../../Coding-Challenges/LAB-005-profile-card-scope.md). This is a JVM test, not an Android lifecycle or network test.

## Day 19: narrow architecture port

[SaveNote.kt](src/main/kotlin/academy/SaveNote.kt) defines a writer-only port and a use case that validates before delegating. [SaveNoteTest.kt](src/test/kotlin/academy/SaveNoteTest.kt) verifies normalization, no write for invalid input, and failure propagation in four JUnit cases. Try [LAB-006](../../Coding-Challenges/LAB-006-save-note-port.md). This fake does not verify Room durability or Android wiring.

## Day 13: view ownership model

[ViewSession.kt](src/main/kotlin/academy/ViewSession.kt) is a pure JVM attach/detach model, not an Android LifecycleOwner. [ViewSessionTest.kt](src/test/kotlin/academy/ViewSessionTest.kt) verifies four cases: no renderer, attached delivery, no delivery after detach, and a new renderer after rebinding. Try [LAB-007](../../Coding-Challenges/LAB-007-view-session-owner.md). Activity, Fragment, process death and memory leaks require Android integration tests not available in this lab.

## Day 37: pair-search invariants

[PairSearch.kt](src/main/kotlin/academy/PairSearch.kt) implements a map-based original-index search and a validated sorted two-pointer values search. [PairSearchTest.kt](src/test/kotlin/academy/PairSearchTest.kt) checks seven cases including overflow, duplicates, nonmutation and invalid sortedness. Try [LAB-008](../../Coding-Challenges/LAB-008-pair-search-invariants.md). Expected map complexity relies on suitable hash distribution, not a universal constant-time guarantee.

## Day 25: row comparison policy

[NoteRow.kt](src/main/kotlin/academy/NoteRow.kt) is a pure JVM row comparison and list snapshot model, not AndroidX DiffUtil. [NoteRowTest.kt](src/test/kotlin/academy/NoteRowTest.kt) checks four cases: same ID/new title, different ID/same title, content change and detached outer list. Try [LAB-009](../../Coding-Challenges/LAB-009-note-row-diff-policy.md). RecyclerView rendering and Fragment binding need an Android SDK test.

## Day 20: editor state reducer

[EditorReducer.kt](src/main/kotlin/academy/EditorReducer.kt) models immutable editor state and request identity. [EditorReducerTest.kt](src/test/kotlin/academy/EditorReducerTest.kt) covers six transitions including a late completion from an older save. Try [LAB-010](../../Coding-Challenges/LAB-010-editor-state-reducer.md). This is a pure JVM model; it does not instantiate Android ViewModel, collect StateFlow, or persist data.

## Day 33: trusted return-link shape

[TrustedReturnLink.kt](src/main/kotlin/academy/TrustedReturnLink.kt) parses one narrow HTTPS payment-return contract. [TrustedReturnLinkTest.kt](src/test/kotlin/academy/TrustedReturnLinkTest.kt) covers six accepted and hostile URL groups. Try [LAB-011](../../Coding-Challenges/LAB-011-trusted-payment-return-link.md). These tests do not verify Android manifests, domain association, server authorization, or payment state.

## Specialist POS: terminal attempt outcomes

[TerminalAttempt.kt](src/main/kotlin/academy/TerminalAttempt.kt) models one payment attempt with approved, declined, and unknown terminal outcomes. [TerminalAttemptTest.kt](src/test/kotlin/academy/TerminalAttemptTest.kt) covers seven transition groups. Try [LAB-012](../../Coding-Challenges/LAB-012-terminal-attempt-state-machine.md). No NFC hardware, EMV kernel, payment provider, or certification is exercised.

## DSA live coding: weighted shortest path

[ShortestPath.kt](src/main/kotlin/academy/ShortestPath.kt) implements Dijkstra with lazy stale-entry removal, parent reconstruction and overflow protection. [ShortestPathTest.kt](src/test/kotlin/academy/ShortestPathTest.kt) covers seven graph and numeric cases. Try [LAB-013](../../Coding-Challenges/LAB-013-dijkstra-shortest-path.md).

## Day 21: offline repository transitions

[OfflineNotesRepository.kt](src/main/kotlin/academy/OfflineNotesRepository.kt) is an in-memory local-first coordination model. [OfflineNotesRepositoryTest.kt](src/test/kotlin/academy/OfflineNotesRepositoryTest.kt) covers six write, retry, acceptance and conflict cases. Try [LAB-014](../../Coding-Challenges/LAB-014-offline-note-repository.md). It does not persist through process death or run Room, WorkManager, Flow or HTTP.

## Day 31: migration coverage audit

[MigrationCoveragePlanner.kt](src/main/kotlin/academy/MigrationCoveragePlanner.kt) checks that every supported installed schema has a declared forward path to a release target. [MigrationCoveragePlannerTest.kt](src/test/kotlin/academy/MigrationCoveragePlannerTest.kt) covers seven graph, validation and release-matrix cases. Try [LAB-015](../../Coding-Challenges/LAB-015-migration-coverage-planner.md). The planner does not execute SQL or test Room, SQLite files, WAL, DataStore, process death or Android integration.

## Day 5: variance and runtime type boundaries

[RuntimeTypeRegistry.kt](src/main/kotlin/academy/RuntimeTypeRegistry.kt) combines typed keys, explicit runtime tokens, one guarded internal cast, and covariant/contravariant interfaces. [RuntimeTypeRegistryTest.kt](src/test/kotlin/academy/RuntimeTypeRegistryTest.kt) covers seven token, boundary and variance cases. Try [LAB-016](../../Coding-Challenges/LAB-016-runtime-type-registry.md). It does not validate nested generic shapes, persistence, serialization, Java signatures or class-loader isolation.

Source and verification status are recorded in [`../../BUILD-VERIFICATION.md`](../../BUILD-VERIFICATION.md). There is no Android SDK dependency or live payment code.
