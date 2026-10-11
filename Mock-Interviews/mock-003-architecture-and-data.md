---
id: MOCK-003
status: reviewed
---
# MOCK-003 — Architecture and data

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **ARC-Q001:** An Activity validates a note title, writes SQL, retries errors, and displays success. Where would you draw responsibility boundaries, and why?
2. **ARC-Q002:** Explain why SaveNote depends on NoteWriter instead of a Room DAO. What did the fake test prove, and what did it not prove?
3. **ARC-Q003:** Two NoteWriter implementations compile. One atomically upserts; the other stores a note then throws. Are they substitutable? What contract and tests would you add?
4. **ARC-Q004:** Why does SaveNote accept a writer-only port rather than a repository interface with read, delete, sync and observe methods? When might splitting be excessive?
5. **ARC-Q005:** A review proposes a BaseRepository hierarchy, generic UseCase interface, and Hilt module for a single note-save operation. Evaluate this proposal and choose a smaller design.
6. **ARC-Q006:** Trace a save action from the UI through a ViewModel-style state holder and back to the rendered screen. Which layer owns each decision?
7. **ARC-Q007:** What does unidirectional data flow guarantee, and which race conditions can still happen?
8. **ARC-Q008:** Should navigation and snackbar messages be modeled as state or one-shot events? Explain the delivery trade-offs.
9. **ARC-Q009:** What belongs in a screen-level ViewModel, and when would you extract another state holder or domain use case?
10. **ARC-Q010:** A save for title A completes after the user has changed the title to B and started another save. How do you prevent a false success message and protect persisted data?
11. **ARC-Q011:** What does a repository own beyond wrapping a network API or DAO?
12. **ARC-Q012:** In an offline-first app, how can the local database be the source of truth while the server still resolves conflicts?

## Answer key

1. **ARC-Q001:** I would let the UI send an action and display state, keep the product validation in a use case or repository, and let a data adapter own persistence. I would make failures visible instead of reporting success after a catch. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q001.md)
2. **ARC-Q002:** A narrow NoteWriter port keeps the save rule independent of Room and lets a fake verify normalization, no write on invalid input, and failure propagation. It does not prove that the real DAO is durable, transactional, or main-safe. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q002.md)
3. **ARC-Q003:** Compilation alone is insufficient. I need the upsert contract to specify outcomes on success and failure, including atomicity or partial effects. I would run shared contract tests against both adapters and document any weaker guarantee. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q003.md)
4. **ARC-Q004:** The use case needs only upsert, so a narrow port makes its dependency and test surface clear. I would split only when the wider interface creates coupling or competing implementers; extra interfaces without a use can raise navigation cost. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q004.md)
5. **ARC-Q005:** I would start with the product rule and one narrow writer dependency. A generic hierarchy adds inheritance and hidden contracts without a demonstrated need; Hilt may be useful later for Android graph wiring but does not improve the rule itself. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q005.md)
6. **ARC-Q006:** The UI renders immutable state and sends a save action. The ViewModel owns screen state and coordinates the operation, while the repository owns data access. The completion returns to the state holder, which emits a new renderable state. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q006.md)
7. **ARC-Q007:** UDF gives me one traceable direction for actions and state. It does not serialize asynchronous work. I still need request identity, cancellation or conflict policy, and lifecycle ownership. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q007.md)
8. **ARC-Q008:** I choose based on lifetime and replay semantics. Durable user-visible decisions belong in state with explicit acknowledgement. UI effects need a documented delivery policy and lifecycle tests. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q008.md)
9. **ARC-Q009:** A screen ViewModel owns renderable screen state and coordinates product operations. I extract reusable or complex product rules into use cases, and component-specific UI logic into plain state holders with the right lifetime. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q009.md)
10. **ARC-Q010:** I tag each save, snapshot its payload, and accept UI completion only for the current request. Separately, I protect persistence with cancellation where possible, idempotency or version checks, and reconciliation from the source of truth. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q010.md)
11. **ARC-Q011:** A repository owns the data contract and coordination policy: what the app reads, how sources update the source of truth, and how writes, refreshes, and conflicts are handled. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q011.md)
12. **ARC-Q012:** Local storage is the app's read source of truth. The server can remain the cross-device authority; synchronization writes its accepted or conflict result back into local storage. [Complete answer](../Interview-Question-Bank/Model-Answers/ARC-Q012.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
