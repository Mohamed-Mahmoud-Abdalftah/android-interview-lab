---
id: "PAT-12"
question: "How would Facade simplify an unreliable third-party SDK?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 203
editorial_status: "reviewed"
---

# PAT-12

## Original interview question

How would Facade simplify an unreliable third-party SDK?

## What the interviewer evaluates

Design a facade that normalizes an unreliable SDK without hiding errors or durability needs.

## Explanation in Arabic

Facade تقدّم API صغير مستقر فوق SDK معقد: `submitPayment`, `queryStatus`, `cancelIfAllowed` بدل callbacks/options موزعة في ViewModels. جوّاها adapters تحول callback لtyped outcome، dedupe للcallback المكرر، timeout handling، request ID، وlogging آمن. لكن Facade ما تعلنش success من callback محلي لو server status لسه unknown؛ ترجع `PendingVerification` وتعمل reconciliation. لازم تراعي cancellation: إلغاء coroutine مش بالضرورة يلغي transaction على server. facade مش excuse لإخفاء كل أخطاء SDK تحت `Boolean`.

## Why it matters and how it works

A facade simplifies a subsystem boundary while presenting stable semantics. For an unreliable vendor SDK, the value is normalization of callbacks, errors and ownership; durable transaction status still requires repository/backend design.

## Worked example

Conceptual API: `PaymentFacade.submit(requestId, amount): SubmitOutcome` returns `Confirmed`, `Rejected`, or `PendingVerification`; `observeStatus(requestId)` exposes backend-confirmed updates. Internal adapter handles duplicate callbacks and SDK exceptions; caller sees no vendor types.

## Practical walkthrough

third-party SDK ممكن callback ترجع success code ثم status endpoint تتأخر، أو timeout بعد server accept. Facade تعرض `submit(requestId): SubmitOutcome` و`observeStatus(requestId)` بدل ما كل ViewModel تكرر vendor quirks. جوهها Adapter لكل callback وretry/reconciliation policy موثقة، لكن ما تحولش unknown لـsuccess/failure لمجرد API سهلة. `PendingVerification` تفضل حالة صريحة، وrequest ID محفوظة قبل submit. لو SDK method مش cancellable، facade توضح إن cancellation توقف انتظار caller بس وقد تحتاج status query. اختبر callback مرتين، late callback، process death، 401، وحالات server mismatch.

## Trade-offs and decision criteria

A facade reduces caller complexity but can become a God Object if it owns UI navigation, server secrets, analytics and every provider. Keep domain policy and UI state outside; use separate adapters for each SDK.

## Failure modes

SDK invokes success callback twice; facade emits two navigation events and user sees duplicate confirmation. Make callback completion idempotent locally, but still reconcile server state. Timeout must not be mapped to final rejection without evidence.

## Production perspective

A fintech app wraps a flaky provider SDK, persists request IDs, and monitors callback anomalies. Backend status is authoritative; facade reports safe error codes and telemetry omits card data.

## Interview answer — short

A Facade can give callers one stable API over a messy SDK, normalizing callbacks and errors. For payments I preserve uncertain outcomes and reconcile with the server rather than hiding failures behind a Boolean.

## Interview answer — structured

I would define a small domain-facing facade for the operations callers truly need, then hide vendor callbacks and configuration behind it. The facade maps duplicate callbacks, exceptions and timeouts into typed outcomes with documented cancellation behavior. It should not own UI navigation or pretend that local SDK success proves a server transaction. An uncertain submit returns a request ID for verification, and the repository/backend supplies final status. I test callback order, duplicates and process-death recovery around the boundary.

## Interview answer — deep senior

An unreliable SDK creates two kinds of complexity: interface complexity and semantic uncertainty. A Facade reduces the first by exposing a small application contract; internal adapters handle callback shape, threading and error codes. It must not erase the second. A timeout can occur after a successful server commit, and cancelling a coroutine may only stop waiting, not undo the payment. I would carry a persisted request ID, return a pending outcome, and query authoritative server status. Duplicate callbacks should be collapsed within the current process while server idempotency protects business effects. I keep analytics and UI effects outside the facade or in dedicated collaborators, avoid logging sensitive payloads, and run contract tests against a fake SDK that invokes callbacks in surprising orders.

I would give callers one stable domain operation, not a pile of vendor callbacks. The facade can validate input, call the SDK through an adapter, and expose Confirmed, Rejected, or PendingVerification with a request ID. It simplifies sequencing but must not erase uncertainty. If the SDK times out after sending a payment, the facade should persist or expose the identity needed to query status; it should not return definite failure and invite another charge. I would separate a short-lived UI call from durable reconciliation, document cancellation limits of the vendor API, and contract-test duplicate or late callbacks. Swapping vendors then affects the adapter, while the rest of the app keeps its domain contract.

## How to answer in the interview

- **Why:** Shield callers from SDK quirks without hiding meaningful outcomes.
- **How:** Facade exposes submit/status; adapter maps vendor callbacks to domain result.
- **Trade-off:** Keep uncertain state and cancellation limits visible.
- **Failure case:** Timeout mapped to failure and duplicate charge on retry.
- **Production solution:** Persist request identity and contract-test late/duplicate callbacks.

## Deep-dive talking points

Define facade operations, callback normalization, cancellation, duplicate callbacks and backend reconciliation.

## Follow-up questions

- [PAT-04](../pat-04/): Facade versus Adapter? **Answer:** facade simplifies a subsystem; adapter changes an incompatible interface.
- [PAT-16](../pat-16/): How swap vendor SDKs? **Answer:** vendor adapters behind a stable facade/repository contract.

## Self-check rubric

Model duplicate callback, timeout and cancellation without declaring false payment success.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Facade and Adapter patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository boundary.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
