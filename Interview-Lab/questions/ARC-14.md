---
id: "ARC-14"
question: "Why should UI not call Retrofit or Room DAOs directly?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 159
editorial_status: "reviewed"
---

# ARC-14

## Original interview question

Why should UI not call Retrofit or Room DAOs directly?

## What the interviewer evaluates

Explain why direct UI-to-data-source coupling hurts consistency, lifecycle and testability.

## Explanation in Arabic

لو Compose أو ViewModel نادوا Retrofit service أو Room DAO مباشرة، الشاشة هتعرف HTTP DTOs أو database entities، وتبدأ هي تقرر refresh، retry، وmapping. ده يكبّر Presentation ويخلق شاشتين كل واحدة بتتعامل مع cache بشكل مختلف. Repository تحدد contract لـdata، source of truth، main safety، وتنقل transport details بعيد عن UI. مش معناه لازم UseCase لكل call؛ ViewModel ممكن تنادي repository مباشرة. DAOs/services تفضل داخل data layer مع tests.

## Practical walkthrough

لو Composable تستدعي Retrofit، recomposition قد تعيد request، والUI صارت تعرف HTTP schema وlifecycle. لو ViewModel تستدعي DAO مباشرة، cache/server merge والسياسة تتوزع بين الشاشات. دع UI ترسل event، VM تدير UiState، repository تنسق data. لا يعني ذلك أن كل DB read يحتاج خمس طبقات؛ احمِ boundary التي تحمل state/side effects.

## Why it matters and how it works

A repository provides a consistent app-data API and coordinates sources. UI state holders should consume data/domain APIs and map to UI state, not own transport or persistence mechanics. This reduces change propagation and contradictory data.

## Worked example

Conceptual comparison: bad `ProfileViewModel` calls `api.getUser()` and `dao.insert()` itself; better `ProfileRepository.observeProfile(id)` emits local truth and `refresh(id)` updates that source. ViewModel sets loading/refresh UI state and handles cancellation.

## Trade-offs and decision criteria

Direct access may be acceptable in a throwaway prototype but creates coupling once caching, retries or multiple screens appear. A repository is an abstraction with behavior; avoid a wrapper that simply renames DAO methods without policy or stable contract.

## Failure modes

A UI directly renders a fresh Retrofit response while another screen observes older Room data, violating SSOT. A screen-owned `viewModelScope` refresh also gets cancelled on navigation when a durable sync was required. Put consistency and durable scheduling in appropriate data/work layers.

## Production perspective

A profile feature uses a Room-backed repository with network refresh and clear error categories. UI can be rebuilt from local data after process death, and network transport changes do not alter Compose.

## Interview answer — short

UI should consume a repository or domain API rather than call Retrofit or Room directly, because the data layer owns mapping, source of truth, and consistency. A ViewModel still owns screen state and lifecycle.

## Interview answer — structured

Direct Retrofit or DAO calls make the screen depend on transport or schema details and force it to decide cache, refresh, and error mapping. That logic gets duplicated across screens and is hard to test independently. A repository exposes app data and coordinates local and remote sources. The ViewModel can call the repository directly if no domain use case is needed, then map data into UI state. This keeps UI tests focused on rendering and events. For an offline screen, direct DAO and API calls also encourage two visible truths: one screen renders the response while another renders cached rows. A repository can funnel both through one local observation path and define what happens when refresh fails.

## Interview answer — deep senior

The biggest risk is inconsistent truth. If one screen renders raw network data and another observes Room, the user may see conflicting states. A repository can establish a single observable source, apply refreshes transactionally, and expose stable domain models. It can also make blocking sources main-safe and classify failures. A ViewModel should not become a mini sync engine whose work disappears with the screen if durability is required. I would not add a pass-through repository merely for a diagram; its API should state freshness, error and update behavior. Tests then verify the repository with fake data sources and the ViewModel with a fake repository, so transport changes do not force UI rewrites. I would audit a direct-call design for Main-thread blocking, cancellation, process-death behavior, and duplicate caching policy. A ViewModel’s lifecycle may be too short for durable sync; the data layer can persist state and schedule recovery. The repository API should be more than a method-name wrapper: it should promise domain models, freshness behavior, and typed errors. UI tests then do not need Retrofit or Room at all, while data tests focus on those mechanisms.

## How to answer in the interview

- **Why:** rendering can repeat and data policy must be shared.
- **How:** route effects through owner and repository.
- **Trade-off:** separation versus call-chain overhead.
- **Failure case:** network call in composable body repeats.
- **Production solution:** observable state and adapter tests.

## Deep-dive talking points

Trace one profile refresh through UI and data; compare direct DTO rendering to Room-backed repository observation.

## Follow-up questions

- [ARC-10](../arc-10/): What consistency rule is at risk? **Answer:** screens can observe different sources instead of one source of truth.
- [ARC-18](../arc-18/): Who makes blocking I/O main-safe? **Answer:** data/domain APIs should encapsulate their dispatcher needs.

## Self-check rubric

Explain two coupling risks, one SSOT failure, and a repository contract that fixes them.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repositories and data sources.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — UI/data boundaries.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
