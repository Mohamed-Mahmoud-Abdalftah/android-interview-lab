---
id: "MOD-09"
question: "How should feature modules communicate without direct coupling?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 362
editorial_status: "reviewed"
---

# MOD-09

## Original interview question

How should feature modules communicate without direct coupling?

## What the interviewer evaluates

- Select contracts, navigation events or shared state by actual relationship.
- Keep ownership and dependency direction explicit.
- Address result delivery and asynchronous consistency.

## Explanation in Arabic

لا تجعل `:feature:checkout` يستدعي class داخلي في `:feature:catalog`. لو يحتاج data، اعتمد على domain/API contract صغير وتطبيقه في data أو app composition. لو يحتاج فتح شاشة، استخدم navigation contract/route ID بدون استيراد UI implementation. لو يحتاج نتيجة من feature ثانية، عرّف result contract وlifecycle/delivery semantics بدل global event bus مبهم. أحيانًا app shell هو المكان الذي ينسق الميزتين. لا تجعل shared ViewModel أو singleton mutable حلًا تلقائيًا؛ حدّد source of truth واستمراره بعد process death.

## Why it matters and how it works

Direct feature implementation imports create cycles and couple release cadence. A stable API or app-level coordinator converts the relationship into a directed edge. Navigation can pass small identifiers and results through back-stack/saved-state mechanisms where appropriate. Shared domain data belongs in a repository rather than two screens copying mutable objects.

## Worked example

Catalog opens checkout with a product ID. Checkout loads authoritative price and stock through `ProductRepository` contract; app navigation maps `CheckoutDestination(productId)` to the checkout implementation. On completion, checkout returns an order ID or updates the orders repository. Catalog does not call checkout's ViewModel or inspect its Composables.

## Trade-offs and decision criteria

An interface module adds API work but decouples real consumers. App orchestration is explicit but may enlarge top-level wiring. A shared event bus is flexible yet hides ownership and can lose or duplicate events. Direct coupling can be acceptable inside one cohesive feature module; do not split solely to then reconstruct it with adapters.

## Failure modes

Features import each other's DTOs and create a cycle. A global SharedFlow drops a checkout result while no screen collects. A shared singleton holds stale selected product after account switch. Navigation passes an entire mutable cart that cannot restore after process death.

## Production perspective

Document contracts, event ownership and replay/acknowledgment policy. Test deep links, background/foreground transitions and process recreation across feature boundaries. Enforce dependency edges in CI.

## Interview answer — short

“Features communicate through narrow contracts, navigation IDs/results or app-level orchestration; shared durable data has one repository owner.”

## Interview answer — structured

“I choose the seam by what crosses it. For data, checkout depends on a product repository interface rather than catalog UI classes. For destination changes, app navigation passes a small product ID and maps it to checkout. For a result, I define delivery and restoration semantics rather than use an unowned global event bus. This keeps the graph acyclic and lets each feature change its internals independently.”

## Interview answer — deep senior

“I try to keep each feature independently understandable, so I avoid importing another feature's implementation. If Checkout needs product facts, I give it a stable repository or domain contract and let the app graph supply an implementation. It receives a product ID from navigation and reloads authoritative price and availability, instead of trusting a mutable Catalog screen object. If the relationship is an action—opening Checkout or returning an order ID—I use a small navigation contract with clear back-stack result or shared repository semantics. I specify what happens when the receiver is stopped, recreated or deep-linked, because a generic hot event bus can lose a result and a replaying one can duplicate it. App-level orchestration can coordinate two features without either depending on the other's internals. I also watch for false abstraction: if two parts always evolve as one capability, merging them may be simpler. I enforce allowed edges and test the integrated path, including process recreation, to prove the contract works beyond isolated module compilation.”

## Deep-dive talking points

Discuss data contracts, app orchestration, navigation IDs, result delivery, repository source of truth and cycle checks.

## Follow-up questions

- Why pass an ID into checkout? **Answer:** it is restorable and lets checkout reload authoritative data.
- What is risky about a global event bus? **Answer:** ownership, delivery and replay can be unclear across lifecycles.
- When might direct collaboration be okay? **Answer:** when code belongs to one cohesive feature boundary rather than artificial modules.

## Self-check rubric

Specify a data contract, navigation contract, result semantics and integration test.

## References and reviewed-on date

- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature boundaries.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — navigation arguments.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Result strategy depends on the navigation library and product flow.
How should feature modules communicate without direct coupling?
