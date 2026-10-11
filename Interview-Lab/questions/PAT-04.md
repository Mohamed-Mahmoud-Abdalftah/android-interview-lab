---
id: "PAT-04"
question: "Explain Adapter, Facade, Decorator, and Proxy."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 195
editorial_status: "reviewed"
---

# PAT-04

## Original interview question

Explain Adapter, Facade, Decorator, and Proxy.

## What the interviewer evaluates

Differentiate interface conversion, simplified subsystem API, behavior wrapping and controlled access.

## Explanation in Arabic

Adapter تغيّر interface vendor SDK عشان تناسب contract داخلي؛ Facade تقدم API أبسط فوق subsystem معقد؛ Decorator يلف object بنفس contract ويضيف behavior زي metrics؛ Proxy يقف مكان object للتحكم في الوصول/التأخير/caching. الأربعة structural لكن الهدف مختلف. مثال Android: callback SDK adapter إلى suspend/domain result، payments facade تجمع 3 calls، logging decorator حول repository، caching proxy يقرر هل ينادي remote. ما تعملش wrapper واحد ينفّذ كل ده بلا وضوح، ولا تعتبر proxy security boundary لو client غير موثوق.

## Why it matters and how it works

Structural patterns control how objects are composed and presented. Selection depends on what changes: incompatible interface, complex subsystem, added cross-cutting behavior, or access to a remote/expensive object.

## Worked example

Conceptual flow: `VendorCallbackAdapter` maps success/error callbacks to `PaymentOutcome`; `CheckoutFacade` exposes `submitAndVerify`; `MetricsGateway` delegates the same `Gateway` API while timing calls; `CachedGatewayProxy` may return fresh cached data. Each needs its own failure and cancellation contract.

## Trade-offs and decision criteria

Wrappers can isolate vendor churn but add stack depth and debugging complexity. A simple adapter is often enough; adding facade/decorator/proxy simultaneously without a real need is ceremony. A proxy cache must define freshness and authority.

## Failure modes

A decorator logs raw card details, leaking sensitive data. Or a proxy returns stale “Paid” status as authoritative. Cross-cutting behavior must honor privacy and server truth; contract tests should catch altered outcomes.

## Production perspective

A checkout integration isolates vendor SDK callbacks in an adapter, provides a small facade to application policy, and adds a metrics decorator that logs only safe codes. Repository still reconciles server status.

## Interview answer — short

Adapter translates an interface, Facade simplifies a subsystem, Decorator adds behavior while preserving a contract, and Proxy controls access or defers work. I choose the wrapper by its specific responsibility.

## Interview answer — structured

If a third-party SDK exposes callbacks but my domain expects a suspend result, I use an Adapter. If several SDK steps should be one application operation, a Facade can hide their coordination. A Decorator can add metrics without changing the gateway contract; a Proxy can mediate caching or remote access. They may be composed, but I keep each responsibility clear and test that wrappers preserve error, cancellation and security semantics.

## Interview answer — deep senior

The patterns look similar because each can contain another object, so intent is the discriminator. An Adapter makes incompatible APIs work together. A Facade offers a deliberately smaller entry point to a subsystem. A Decorator preserves the same contract while layering behavior; a Proxy also presents the same contract but controls access, location or laziness. In Android, a vendor callback adapter must handle duplicate callbacks and cancellation. A metrics decorator must not log PII, and a cache proxy must not present stale financial status as final server truth. I use contract tests across the wrapped and unwrapped implementations to ensure behavior does not shift unexpectedly. If one wrapper begins doing selection, retry, UI navigation and logging, I split it before the name of a pattern masks the mixed ownership.

## Deep-dive talking points

Distinguish intent for four wrappers; test outcome preservation, cancellation and cache authority.

## Follow-up questions

- [PAT-12](../pat-12/): Which pattern simplifies an unreliable SDK? **Answer:** a Facade over carefully designed adapters and recovery logic.
- [KOT-15](../kot-15/): How can Kotlin reduce decorator forwarding? **Answer:** interface delegation with explicit overrides.

## Self-check rubric

Given a vendor callback, metrics requirement and cache, select wrapper roles and state one failure per role.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — structural patterns.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — forwarding mechanics.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
