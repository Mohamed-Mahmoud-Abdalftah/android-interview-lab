---
id: "ARC-24"
question: "Design a cross-feature account/session state without creating circular dependencies."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 169
editorial_status: "reviewed"
---

# ARC-24

## Original interview question

Design a cross-feature account/session state without creating circular dependencies.

## What the interviewer evaluates

Design shared session ownership without feature-to-feature imports or a process-only singleton.

## Explanation in Arabic

Account/session state تخص أكتر من feature، فحط contract ضيق في shared core/session module: `SessionRepository.observeSession()` و`signOut()`. implementation في data/app module تتعامل مع token storage وserver refresh، وfeatures تعتمد على contract بدل checkout يستورد profile أو العكس. UI state لكل feature مشتقة من session stream، وما تخزنش Activity في singleton. بعد process death ارجع من persisted session مع revalidation؛ local token مش دليل server authorization. logout يمسح local credential ويبلّغ server حسب policy، مع race handling للطلبات الجارية.

### Practical walkthrough in Egyptian Arabic

Account/session state بين features لا تترك كل feature يملك mutable copy. عرّف contract صغير مثل `SessionRepository` في core module لا يعتمد على features، والauth implementation تحقنه. Features تراقب identity/version وتعيد تحميل data عند switch/logout. لا تضع Activity Context أو navigation في singleton. اختبر logout أثناء request والعودة من notification لحساب مختلف.

## Why it matters and how it works

Shared state needs one owner and a dependency direction that prevents cycles. A narrow core contract lets features observe session facts while a data implementation owns persistence and refresh. DI composes the graph.

## Worked example

Conceptual module graph: `:core:session-api` defines `SessionState` and `SessionRepository`; `:feature:profile` and `:feature:checkout` depend on that API; `:core:session-data` implements it; `:app` binds implementation. Neither feature imports the other. Token material stays out of `SessionState` exposed to UI.

## Trade-offs and decision criteria

A shared core module adds a dependency hub; keep its API small and stable. An app-level coordinator may suffice for a tiny codebase. Avoid one global mutable object as a shortcut, because tests and process recovery become fragile.

## Failure modes

Checkout reads `ProfileViewModel.currentUser`, creating lifecycle coupling and circular feature dependencies. Or a singleton keeps an in-memory `isLoggedIn` Boolean after token expiry. Use one session owner backed by storage and server validation.

## Production perspective

A multi-feature wallet app exposes `Authenticated(userId)` or `SignedOut` to features; server access checks remain authoritative. Logout invalidates in-flight operations, clears local state, and shows sign-in consistently after recreation.

## Interview answer — short

I put a narrow session contract in a shared core module, implement it in data, and let features observe it without importing one another. Persistent recovery and server validation prevent an in-memory singleton from becoming false authority.

## Interview answer — structured

Cross-feature session state needs one owner. I define a small `SessionRepository` contract and session model in a shared module, with the implementation handling token persistence, refresh and logout. Each feature depends on that contract, so checkout and profile do not depend on each other. DI binds the implementation. The UI derives its own state from session updates, and after process death it reloads rather than trusting a lost in-memory Boolean. Authorization remains server-side. That contract can expose `SignedOut` or `Authenticated(userId)` but should not hand raw tokens to each feature. The implementation owns refresh and persistence, while server checks remain authoritative. I would test logout arriving while checkout is active and while requests are in flight.

## Interview answer — deep senior

The graph is the first design artifact: features point to a small session API, while a data module implements it and app-level composition wires them together. The exposed model contains only safe facts such as signed-in state and user ID, not raw tokens. The owner handles storage, refresh races, expiry, and logout; features observe a stream and react to changes. A process singleton may cache state but cannot be the durable source of truth. After process death, the repository rehydrates from protected storage and validates as needed. I test simultaneous refresh and logout, in-flight requests during sign-out, and feature recreation. This avoids circular Gradle dependencies and prevents a Profile ViewModel from becoming an accidental global account service. To avoid cycles, neither profile nor checkout imports the other; both depend on a shared API with only the session facts they need. DI in the app composition root binds the data implementation. A singleton can cache a current snapshot but is not durable; after process death the repository must rehydrate and validate. I also define how token refresh races with sign-out and whether pending requests are cancelled or rejected. These operational details are where a shared session design succeeds or fails, beyond a clean module diagram.

## How to answer in the interview

- **Why:** cross-feature state can create cycles.
- **How:** central contract with one authoritative owner.
- **Trade-off:** shared core versus coupling.
- **Failure case:** stale account response leaks into new session.
- **Production solution:** session generation and authorization checks.

## Deep-dive talking points

Draw module edges, token ownership, refresh/logout races, process-death recovery and server authority.

## Follow-up questions

- [ARC-10](../arc-10/): Who is session source of truth? **Answer:** a dedicated data owner with server reconciliation, not feature-local flags.
- [DI-16](../di-16/): How does DI wire modules? **Answer:** app composition provides one implementation of the shared contract.

## Self-check rubric

Sketch an acyclic module graph and explain how checkout reacts to logout after rotation and process death.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module dependency design.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository state ownership.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
