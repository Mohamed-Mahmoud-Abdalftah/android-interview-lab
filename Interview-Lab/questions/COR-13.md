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

سلوك الأب والإخوة عند فشل أحد الأبناء (Child Coroutine Failure) بيعتمد بنسبة 100% على **نوع الـ Parent Job**:

1. في حالة الـ Standard Job (أو داخل `coroutineScope`):
   - **تسلسل الانهيار (Cascading Teardown):**
     1. الابن بيرمي Uncaught Exception.
     2. الابن يرسل إشعار إلغاء للأب (`parent.childCancelled(cause)`).
     3. الأب يلغي نفسه فوراً.
     4. الأب يرسل إشارات إلغاء لجميع الأبناء الآخرين (Siblings)، ويتم إلغاؤهم بـ `CancellationException`.
     5. الأب يجمع أي Exceptions حدثت في الإخوة كـ Suppressed Exceptions ويرمي الاستثناء الأصلي للأعلى.
   - الهدف: الحفاظ على اتساق البيانات (Consistency)؛ لا نترك عمليات نصف مكتملة في الخلفية.

2. في حالة الـ `SupervisorJob` (أو داخل `supervisorScope`):
   - **عزل الفشل (Failure Isolation):**
     1. الابن يرمي Exception.
     2. الأب (Supervisor) يتجاهل الإلغاء ويظل حياً ونشطاً (`isActive = true`).
     3. باقي الإخوة (Siblings) يستمرون في العمل بدون أي تأثر.
     4. الابن الفاشل فقط هو الذي ينتهي، واستثناؤه يتم توجيهه للـ `CoroutineExceptionHandler` الخاص به أو إلى الـ Thread Uncaught Exception Handler.

## Practical walkthrough

في شاشة عرض تفاصيل الطلب (Order Details):
- بنطلب 3 خدمات: 1. معلومات الشحن، 2. معلومات الفاتورة، 3. توصيات منتجات إضافية.
- **تحليل السيناريو المعماري:**
  * الشحن والفاتورة: عمليتان حرجتان؛ لو فشل الشحن، لا فائدة من الفاتورة. هنا نستخدم `coroutineScope` العادي لكي يلغي العملية الأخرى فوراً عند الفشل (Fail-Fast).
  * توصيات المنتجات: خدمة غير حرجة؛ لو فشلت لا نريد إلغاء الشحن والفاتورة. هنا نضعها داخل `supervisorScope` أو نفصلها لكي لا يؤثر فشلها على العمليات الحيوية.

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

In a standard Job hierarchy, if a child coroutine fails with an uncaught exception, it cancels its parent, which immediately cancels all other siblings (fail-fast). In a SupervisorJob or supervisorScope, the failure is isolated: the parent remains active and siblings continue executing undisturbed.

## Interview answer — structured

What happens to the parent and siblings depends entirely on whether the parent is a standard Job or a SupervisorJob.

In a standard Job hierarchy—such as inside a standard `coroutineScope`—the behavior is 'fail-fast'. When a child coroutine encounters an uncaught exception (other than CancellationException), it notifies its parent. The parent cancels itself, and that cancellation cascades downwards to immediately cancel all sibling coroutines. This prevents partial state corruption, ensuring that if one critical step in an operation fails, related parallel tasks are cleaned up.

In contrast, under a `SupervisorJob` or `supervisorScope`, child failure is strictly isolated. The supervisor parent does not cancel itself when a child fails, and active sibling coroutines continue running to completion. The failed child terminates independently, and its exception must be handled locally or by a CoroutineExceptionHandler attached to that child.

## Interview answer — deep senior

At the internal implementation level, when a child throws an unhandled exception, it calls `parent.childCancelled(e)`. A standard `JobSupport` parent returns `true` to acknowledge the cancellation, transitions its state to Cancelling, and iterates through its `NodeList` of child handles, calling `child.cancel(CancellationException(cause))` on every active child.

If another sibling also throws an exception while being cancelled, the parent attaches that second exception as a suppressed exception (`Throwable.addSuppressed()`) to the root cause, ensuring that no diagnostic failure information is lost in stack traces.

In Android architecture, recognizing this distinction determines whether you use `coroutineScope` or `supervisorScope`. If parallel sub-tasks are interdependent (e.g., merging two API responses into a single combined UI entity), use `coroutineScope`. If the sub-tasks are independent UI components (e.g., separate dashboard cards), use `supervisorScope` so one failed widget doesn't blank out the entire screen.

## How to answer in the interview

- **Why:** failure propagation starts at the child, not at await.
- **How:** ordinary child failure cancels its parent and siblings; cancellation of a child alone is not treated as ordinary failure.
- **Trade-off:** this protects required aggregates but rejects partial success.
- **Failure case:** a late catch cannot undo parent cancellation.
- **Production solution:** map failures at an intentional boundary and test sibling cleanup.

## Deep-dive talking points

Draw failure arrows for normal and supervised trees, then account for side effects already accepted by a server.

## Follow-up questions

- **Interviewer:** "Does a child failing with `CancellationException` cancel its parent or siblings?"
  **Answer:** "No! `CancellationException` is special. It signifies normal, cooperative task termination. When a child throws `CancellationException`, it terminates itself without notifying the parent as an error, so the parent and sibling coroutines continue running normally."

- **Interviewer:** "If an `async` child fails inside `coroutineScope`, does it cancel siblings before `await()` is called?"
  **Answer:** "Yes! Even if you never call `await()`, an uncaught exception in an `async` child inside a standard `coroutineScope` immediately cancels the parent scope and all sibling coroutines."

- **Interviewer:** "How do you inspect suppressed exceptions from cancelled siblings?"
  **Answer:** "When catching the parent's exception, you can inspect `exception.suppressed` or `exception.suppressedExceptions` array, which contains any secondary exceptions thrown by siblings during their cancellation unwinding."

## Self-check rubric

Can I predict normal and supervised sibling fate, explain cleanup waiting, and separate client cancellation from server rollback?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — parent and child failure semantics.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured completion.

Technically reviewed against primary documentation on 2026-10-13.
