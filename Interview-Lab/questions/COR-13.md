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

## Concept and technical explanation

When a child coroutine fails with an uncaught exception, the behavior of its parent and siblings is governed entirely by the parent's Job type within structured concurrency. In a standard Job hierarchy (such as inside coroutineScope or plain launch), an uncaught exception in a child is propagated upward to the parent immediately. The parent cancels all other active sibling coroutines with a CancellationException, terminates itself, and rethrows the original triggering exception to its own parent or caller. This fail-fast mechanism prevents orphaned tasks and state inconsistencies. Conversely, in a supervised hierarchy (such as supervisorScope or a scope backed by a SupervisorJob), upward cancellation is severed: the parent ignores the child's failure and remains active, and surviving siblings continue their execution unaffected. However, in both models, if the failure cause is a CancellationException, it represents normal cooperative cancellation and never cancels the parent or siblings.

## Practical walkthrough (English)

Demonstrating parent and sibling fate in standard versus supervised hierarchies:
```kotlin
// 1. Standard Hierarchy: Child failure cancels parent and siblings immediately
runBlocking {
    val parentJob = launch {
        val child1 = launch {
            delay(500)
            println("Child 1 completed") // Never executes!
        }
        val child2 = launch {
            delay(50)
            throw IllegalStateException("Child 2 failed unexpectedly") // Triggers cascade
        }
    }
    parentJob.join() // Parent fails and throws IllegalStateException
}

// 2. Supervised Hierarchy: Sibling isolation
runBlocking {
    supervisorScope {
        val child1 = launch {
            delay(200)
            println("Child 1 survived and completed successfully!") // Prints successfully
        }
        val child2 = launch {
            delay(50)
            // Error logged by CEH; child1 continues unaffected:
            throw IllegalStateException("Child 2 failed")
        }
    }
}
```

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

In a standard Job hierarchy, an uncaught exception in a child immediately cancels the parent, which cancels all sibling coroutines (fail-fast). In a supervised hierarchy (SupervisorJob or supervisorScope), the parent survives, siblings continue running undisturbed, and only the failing child terminates. CancellationException never cancels parents or siblings in either hierarchy.

## Interview answer — structured

Predicting the fate of a parent and sibling coroutines upon child failure is a core structured concurrency requirement.

The outcome depends strictly on whether the parent node is a standard Job or a SupervisorJob. In a standard Job tree, failure propagation is immediate and bidirectional. An uncaught exception causes the child to invoke cancellation on its parent, which instantly cancels all sibling coroutines with CancellationException before cancelling itself and escalating the error upward. This fail-fast approach guarantees that dependent operations do not waste CPU cycles or produce corrupted partial state.

In production, supervised trees decouple sibling fates. Under a SupervisorJob or supervisorScope, the parent intercepts the child's termination without transitioning to a cancelled state, allowing remaining siblings to complete their operations successfully. This isolation is mandatory in user-facing dashboards where independent network calls should not terminate one another.

An essential exception to this rule is CancellationException. When a child coroutine is cancelled via CancellationException, it unbinds cleanly without affecting its parent or siblings under both standard and supervised hierarchies.


## Interview answer — deep senior

At the internal coroutines runtime level, when a coroutine encounters an uncaught throwable, its completion handler invokes notifyParent with the failure cause. The parent JobSupport evaluates whether the throwable is a CancellationException. If the throwable is an operational failure like IOException or NullPointerException, a standard Job marks itself as Cancelling, constructs a parent-originated CancellationException wrapping the root cause, and traverses its child NodeList to notify all sibling ChildHandles. Each sibling continuation is resumed with this CancellationException, tearing down their respective stack frames cooperatively.
Once all siblings acknowledge cancellation and finish their active blocks, the parent aggregates any secondary exceptions that occurred during teardown into suppressed exceptions attached to the primary root cause. The parent then completes exceptionally and passes the aggregated exception to its outer continuation or uncaught exception handler.
Under a SupervisorJob, the childCancelled callback intercepts the notification and returns false. The parent neither transitions into Cancelling nor touches the NodeList of siblings. Because the parent refuses to handle the error, the responsibility for the uncaught exception shifts back to the child coroutine. If the child was created using launch, the exception is dispatched to the thread's CoroutineExceptionHandler. If the child was created with async, the exception is cached inside the Deferred result until await is called.
Staff engineers design architectures around these mechanics: wrapping parallel async operations in coroutineScope when results are mutually dependent, and using supervisorScope with individual try-catch blocks when partial rendering is acceptable.

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
