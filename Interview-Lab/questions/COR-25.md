---
id: "COR-25"
question: "Call 3 dependent APIs concurrently. If one fails, how do you cancel siblings and return a consistent failure?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 106
editorial_status: "reviewed"
---

# COR-25

## Original interview question

Call 3 dependent APIs concurrently. If one fails, how do you cancel siblings and return a consistent failure?

## What the interviewer evaluates

Design three concurrent all-or-nothing API calls, cancellation of siblings and one consistent failure.

## Explanation in Arabic

السؤال بيقول dependent APIs لكن ممكن نعملها parallel فقط لو المقصود إن النتائج الثلاثة كلها مطلوبة للتجميع، ومفيش request محتاج ناتج التاني كـinput. لو B محتاجة ID من A يبقى A تخلص الأول ثم نشغّل المستقلين. في `coroutineScope`، فشل child يلغي الإخوة ونرجّع failure واحدة؛ الإلغاء لا يمسح side effects وصلت للسيرفر.

## Why it matters and how it works

Start independent prerequisites with `async` inside `coroutineScope`, await all, then validate a consistent aggregate before publishing. If there are true data dependencies, split into sequential stages. Parent cancellation cancels children; an ordinary child failure cancels siblings. Use a typed domain result at the outer boundary, with cancellation propagated.

## Worked example

Illustrative Kotlin/JVM: three fetches have no input dependency but the final response needs all three; callers supply cancellable, main-safe suspending APIs.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

data class CheckoutView(val price: Int, val tax: Int, val stock: Int)
suspend fun checkout(
    price: suspend () -> Int,
    tax: suspend () -> Int,
    stock: suspend () -> Int,
): CheckoutView = coroutineScope {
    val p = async { price() }
    val t = async { tax() }
    val s = async { stock() }
    CheckoutView(p.await(), t.await(), s.await())
}
```

## Trade-offs and decision criteria

All-or-nothing is right for a checkout quote where partial data is invalid. Parallel requests improve latency only when they are independent. If B depends on A, await A before launching B; if any call changes server state, design compensation or reconciliation rather than assuming sibling cancellation rolls it back.

## Failure modes

Launching three requests outside a structured scope can leave siblings running after one fails. Publishing price before stock arrives presents an inconsistent quote. A cancelled HTTP request may already have reached a server, so a failure response is not proof of rollback.

## Production perspective

A checkout repository fetches pricing, tax and stock under one request ID, validates quote version/expiry, and emits one immutable success or error. It logs which dependency failed and server correlation IDs; tests force each of the three failure positions and verify sibling cancellation and no partial UI commit.

## Interview answer — short

“I first check whether the APIs are truly independent enough to run in parallel. For three required results, I use `async` inside `coroutineScope`; one failure cancels siblings and the caller gets one failure. True input dependencies run in stages, and cancellation does not imply server rollback.”

## Interview answer — structured

“I would draw the dependency graph. If all three calls can start with existing inputs but all results are needed for a valid checkout quote, I launch them as children of one `coroutineScope` and await them before publishing a single UI state. A child failure cancels the others and propagates to the caller. If tax requires the price response, I await price first and parallelize only later independent calls. I preserve `CancellationException`, map domain failures at the outer boundary, and validate quote version and expiry so the combined result is consistent.”

## Interview answer — deep senior

“For production I separate computational dependency, consistency and side effects. Three reads can overlap if their inputs are known, but a returned quote is committed to UI only after all three succeed and pass version checks. Structured scope failure cancels sibling coroutines, yet remote requests may already have been accepted; I do not claim rollback. If one API is a write, I need idempotency and compensation/reconciliation. I set a deadline, bound parallelism, propagate screen cancellation, and log request IDs rather than sensitive payloads. Tests use controlled fakes to fail each call, verify sibling cancellation, ensure no partial state, and exercise slow cancellation so the UI never remains indefinitely loading.”

## Deep-dive talking points

Draw the dependency DAG, distinguish input-dependence from all-results-needed, and reason about remote side effects.

## Follow-up questions

- [COR-26](../cor-26/): When is partial success valid? **Answer:** for independently useful results with per-result failure UI.
- [COR-11](../cor-11/): Which scope cancels siblings? **Answer:** ordinary `coroutineScope`.

## Self-check rubric

Can I parallelize only independent inputs, return one consistent result, test all failure positions, and avoid false rollback claims?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured concurrent children.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — sibling failure propagation.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
