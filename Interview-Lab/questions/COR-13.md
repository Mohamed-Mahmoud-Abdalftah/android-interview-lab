---
id: "COR-13"
question: "What happens to a parent and siblings when a child coroutine fails?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 94
editorial_status: "reviewed"
---

# COR-13

## Original interview question

What happens to a parent and siblings when a child coroutine fails?

## What the interviewer evaluates

Can the candidate predict ordinary child failure, sibling cancellation, parent failure and supervision exceptions?

## Explanation in Arabic

في شجرة `Job` عادية، child يرمي exception غير `CancellationException` غالبًا يلغي الـparent وباقي الـsiblings. الأب يستنى الأطفال يخلصوا cleanup قبل ما يكتمل بالفشل. ده مناسب لو النتائج لازم تبقى متسقة؛ لكنه غلط لو كل widget مستقل. `SupervisorJob` أو `supervisorScope` تغيّر علاقة فشل الإخوة، مع استمرار إلغاء الـparent لكل الأطفال.

## Practical walkthrough

لو `async` واحد فشل قبل ما تعمل `await` للتاني، parent العادي يبدأ cancel للإخوة فورًا؛ `await` مش الزر اللي يبدأ انتشار الفشل. ده مهم في تجميع بيانات checkout: لا تعرض جزء ناجح وكأنه نتيجة كاملة. أما `CancellationException` الناتجة من إلغاء طلب بسبب خروج المستخدم فهي إلغاء طبيعي، مش business error تكرر بسببه الطلب.

## Why it matters and how it works

Failure propagates upward through a normal Job, and cancellation flows downward. `CancellationException` represents normal cancellation and does not ordinarily fail a parent. A supervised direct child failure does not cancel siblings, but that child still needs an error path. A failed supervisor block itself cancels its children.

## Worked example

Illustrative JVM code; `fetchA` and `fetchB` are independently cancellable suspend APIs. `coroutineScope` makes the aggregate all-or-nothing.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

suspend fun requiredPair(
    fetchA: suspend () -> String,
    fetchB: suspend () -> String,
): Pair<String, String> = coroutineScope {
    val a = async { fetchA() }
    val b = async { fetchB() }
    a.await() to b.await()
}
```

## Trade-offs and decision criteria

Keep normal propagation for a logically atomic aggregate. Supervise independent components and return per-component results. Do not treat coroutine cancellation as rollback of a server-side effect; compensate or reconcile if required.

## Failure modes

If `fetchA` fails, `fetchB` is cancelled but might already have sent a request or changed server state. Catching only around `b.await()` cannot prevent earlier parent cancellation. A blocking sibling might delay scope completion because it ignores cancellation.

## Production perspective

A checkout screen needs price and tax from one calculation version. Failure of either invalidates the total, so the repository returns one failure and cancels other child work. For independent news and weather cards, it uses supervision and records separate outcomes.

## Interview answer — short

“In a normal structured scope, an uncaught child failure cancels the parent and siblings. Parent cancellation also cancels children. A `CancellationException` is cancellation, not a domain failure. Supervision changes sibling failure propagation but still requires explicit handling.”

## Interview answer — structured

“I predict the Job tree rather than reason about each coroutine in isolation. Under an ordinary Job, one child’s non-cancellation exception cancels the parent, which cancels its other children; the scope waits for cleanup and exposes the failure. That is useful for all-or-nothing aggregates. Under supervision, direct sibling jobs can continue, but their failures must be converted into outcomes or reported. Parent cancellation still reaches all children. I also separate cancelling client work from rolling back external side effects.”

## Interview answer — deep senior

“The exact outcome depends on the boundary. In `coroutineScope`, a child failure is propagated to the scope; siblings receive cancellation and the scope waits for them to finish before throwing. Catching around `await` after the failure may not save the parent because failure propagation already happened. A `CancellationException` usually marks normal cancellation and should be rethrown rather than logged as a defect. `supervisorScope` isolates direct child failure, yet an exception from its own block cancels children. For a production aggregate, I decide whether partial success is valid, design API idempotency and reconciliation separately, and test slow sibling cancellation so the UI does not hang indefinitely. I would draw the Job tree in the interview and mark two different events: explicit cancellation of a child versus failure with an ordinary exception. A child cancelled on purpose does not normally fail the parent, while an ordinary failure does, and siblings are cancelled. The first exception is primary; cleanup failures may be suppressed. For a checkout aggregate I would verify no partial quote is published and that all sibling requests have finished or cancelled before returning.”

## How to answer in the interview

- **Why:** failure propagation starts at the child, not at await.
- **How:** ordinary child failure cancels its parent and siblings; cancellation of a child alone is not treated as ordinary failure.
- **Trade-off:** this protects required aggregates but rejects partial success.
- **Failure case:** a late catch cannot undo parent cancellation.
- **Production solution:** map failures at an intentional boundary and test sibling cleanup.

## Deep-dive talking points

Draw failure arrows for normal and supervised trees, then account for side effects already accepted by a server.

## Follow-up questions

- [COR-11](../cor-11/): When do siblings survive? **Answer:** direct siblings under a supervisor can continue after one child fails.
- [COR-15](../cor-15/): Does `async` hide failure? **Answer:** it stores it for `await`, but normal child failure can still cancel the parent.

## Self-check rubric

Can I predict normal and supervised sibling fate, explain cleanup waiting, and separate client cancellation from server rollback?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — parent and child failure semantics.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured completion.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
