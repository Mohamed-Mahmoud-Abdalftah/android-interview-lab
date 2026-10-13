---
id: "ARC-21"
question: "A ViewModel contains 1,000 lines of networking, mapping, and business logic. How do you refactor it incrementally?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 166
editorial_status: "reviewed"
---

# ARC-21

## Original interview question

A ViewModel contains 1,000 lines of networking, mapping, and business logic. How do you refactor it incrementally?

## What the interviewer evaluates

Show a safe incremental refactor with characterization tests, seam extraction and behavior preservation.

## Explanation in Arabic

ViewModel 1000 سطر ما تتقصّش في PR واحدة عمياء. أولًا اعمل inventory: network calls، DTO mapping، business rules، UI state transitions، Android lifecycle. ثبّت behavior باختبارات characterization للحالات المهمة، خصوصًا errors وcancellation. بعدين اطلع network/Room coordination لـRepository main-safe، وموديلات/mappers عند data boundary. لو business rule معقدة أو reused اطلع UseCase. خلي ViewModel مسؤولة عن event -> state بس. غيّر vertical slice واحدة، قارن outputs، واتأكد إن retry/process-death semantics ما اتغيروش بالخطأ.

## Practical walkthrough

ViewModel فيها 1000 سطر: اعمل characterization tests للمسارات الحرجة، ثم استخرج DTO mapping إلى data، business validation/use case، وnetwork/cache إلى repository على مراحل. لا تغير architecture والbehavior معًا بلا checkpoints. احتفظ UiState/event API مؤقتًا حتى UI لا تنكسر، ثم قلل dependencies. قس defects/test time ولا تجعل refactor توقف release.

## Why it matters and how it works

Incremental extraction reduces risk while establishing ownership. Tests capture observable behavior before moving code. The goal is thinner state holder and stable data/domain contracts, not merely fewer lines.

## Worked example

Refactor sequence: (1) assert `Loading -> Content/Error` for a representative API response; (2) introduce `ProfileRepository` behind existing ViewModel call; (3) move DTO-to-domain mapping; (4) move shared eligibility into use case; (5) replace direct Retrofit in ViewModel; (6) remove dead code after tests and telemetry agree. Each step is reviewable.

## Trade-offs and decision criteria

A big-bang rewrite may look clean but creates migration risk and lost edge cases. An incremental adapter can temporarily duplicate a call path; remove it after parity is established. Avoid extracting a use case for every helper before identifying real business responsibilities.

## Failure modes

Moving network code into a new repository but keeping `Response<Dto>` as the return type leaves UI coupled. Another failure is changing exception handling so a timeout becomes empty content. Test observable states, cancellation, and retry before and after.

## Production perspective

A mature retail app has a giant search ViewModel. Team extracts repository refresh and cache policy, adds domain search filters shared with catalog, and tracks crash/error metrics by phase. UI remains functional during staged rollout.

## Interview answer — short

I refactor a giant ViewModel incrementally: characterize behavior, identify UI/data/business responsibilities, extract one boundary at a time, and keep state transitions and failure semantics tested throughout.

## Interview answer — structured

I would first list what the class does and write tests around visible behavior, especially loading, errors, cancellation and retries. Then I move transport and persistence coordination into a main-safe repository, mapping DTOs there. Reused business rules can become focused use cases. The ViewModel remains the screen state holder. I do this in small vertical steps, keeping the app buildable and comparing behavior after each move, rather than replacing 1,000 lines in one risky rewrite. A useful first PR might introduce tests and a repository seam without changing UI output. A second moves one endpoint and mapper; a third extracts reused policy. Small steps let reviewers compare states and error categories at each point.

## Interview answer — deep senior

The first step is not to choose folder names but to preserve the contract. I characterize current state transitions and identify hidden coupling: Retrofit calls, Room entities, formatting, and business policy. I create a repository API with domain-friendly outcomes and move one data path behind it, then verify parity. A shared rule moves to a use case only if it has a coherent independent responsibility. I also inspect coroutine ownership: repository methods must be main-safe, ViewModel work should stay screen-scoped, and durable operations need persistence. During migration, I watch telemetry and keep a rollback path. I remove old code only after tests and observed behavior confirm the new path. The result is a ViewModel that handles events and immutable UI state, not a smaller class with the same coupling hidden in helpers. I would keep an explicit migration map of old responsibilities to new owners and avoid changing every endpoint at once. If the ViewModel currently owns a retry timer or in-flight request ID, moving code can change cancellation and process-death behavior even when happy-path tests pass. I add characterization tests for those edges and monitor production error rates during rollout. Only after the new path proves parity do I delete old branches. The goal is localized change and reliable state, not a line-count target.

## How to answer in the interview

- **Why:** large VM hides multiple responsibilities.
- **How:** extract one behavior with regression test.
- **Trade-off:** incremental migration versus rewrite speed.
- **Failure case:** big bang loses edge cases.
- **Production solution:** ship slices with metrics and rollback.

## Deep-dive talking points

Describe characterization tests, an extraction sequence, parity criteria, coroutine ownership, and a rollback strategy.

## Follow-up questions

- [ARC-05](../arc-05/): Where does each part move? **Answer:** screen state stays ViewModel; reusable rules to Domain; data-source work to Repository.
- [ARC-22](../arc-22/): What must the new repository avoid? **Answer:** returning API DTOs directly to UI.

## Self-check rubric

Propose three small PR steps, one behavior test, and one hidden coupling to remove.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — layer and state-holder guidance.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository role.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
