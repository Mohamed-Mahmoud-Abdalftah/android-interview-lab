---
id: "COR-12"
question: "Compare Job and SupervisorJob."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 93
editorial_status: "reviewed"
---

# COR-12

## Original interview question

Compare Job and SupervisorJob.

## What the interviewer evaluates

Whether the candidate can distinguish a Job hierarchy element from the `supervisorScope` builder and reason about child failure.

## Explanation in Arabic

`Job` العادي بيكوّن علاقة parent/child: فشل child غير ناتج عن cancellation عادة يلغي parent وبالتالي الإخوة. `SupervisorJob` بيخلي فشل child ما يلغيش باقي الأطفال، لكن إلغاء الـSupervisorJob نفسه ينزل لكل الأطفال. الاتنين Job عناصر في context؛ `supervisorScope` boundary مؤقتة suspend وبتستنى أولادها، مش مجرد اسم تاني لـ`SupervisorJob`.

## Practical walkthrough

في app-level owner عندك مزامنة analytics وتهيئة cache: لو واحدة فشلت مش لازم توقف التانية، فـ`SupervisorJob` مناسب. لكن لازم لكل `launch` error handler أو catch/report واضح، لأن العزل مش معنى إن الأخطاء اختفت. ولو المستخدم عمل logout، إلغاء الـSupervisorJob نفسه يلغي كل أولاده. اختيار `Job` عادي يعني فشل child يلغي الأسرة كلها.

## Why it matters and how it works

A root `CoroutineScope(SupervisorJob() + dispatcher)` is useful for an owner with independent long-lived tasks. Each launched child still needs a failure policy; `SupervisorJob` does not catch exceptions. A parent Job passed to `SupervisorJob(parent)` retains downward cancellation from the parent. An ordinary Job is appropriate for fail-together groups.

## Worked example

Android/JVM conceptual owner; `handler` logs uncaught `launch` errors, but production should also surface task-specific failures and cancel the scope at shutdown.

```kotlin
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class AppTaskOwner {
    private val handler = CoroutineExceptionHandler { _, error ->
        report(error)
    }
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)
    fun start(task: suspend () -> Unit) { scope.launch { task() } }
    fun close() = scope.cancel()
    private fun report(error: Throwable) { /* log to app telemetry */ }
}
```

## Trade-offs and decision criteria

Use an ordinary Job for operations whose children form one consistent outcome; use SupervisorJob when independent tasks should not cancel one another. The latter can keep the owner running after one failure, but may conceal a persistent outage unless errors are observed and surfaced.

## Failure modes

A supervisor only prevents propagation to siblings. If `launch` fails without local handling or a suitable handler, the exception can still be reported as uncaught. If the owner forgets `close`, the scope can retain resources for the process lifetime.

## Production perspective

An application task owner runs independent cache warmers. Each job reports its failure; other warmers continue. On logout the owner cancels all tasks and creates a new session-owned scope. Critical work still goes through persistent scheduling rather than relying on this scope.

## Interview answer — short

“A normal Job links failures through the parent tree. SupervisorJob allows one child to fail without cancelling siblings, while parent cancellation still cancels them all. It is a context element for an owned scope; `supervisorScope` is a suspending boundary with similar child isolation.”

## Interview answer — structured

“I use Job when children collectively represent one operation, so failure should cancel the group. SupervisorJob changes the failure direction: a child can fail while siblings continue, but cancellation of the supervisor or its parent still cancels children. In Android, a deliberately application-owned scope may use SupervisorJob for independent work, provided it has an exception and shutdown policy. I use `supervisorScope` inside a suspend function when I need a bounded partial-success operation and a return value, rather than allocating a long-lived new scope.”

## Interview answer — deep senior

“Supervision is about a specific edge in the Job tree. With a normal Job, a child exception generally cancels the parent and its siblings. SupervisorJob prevents that upward failure propagation from a direct child; it does not ignore explicit parent cancellation. I would use a SupervisorJob in an injected in-process owner only when independent tasks legitimately continue after peer failure. Each `launch` still needs an error path, and `async` failures must be awaited or converted to results. `supervisorScope` is often preferable inside repository APIs because it suspends until its children finish and preserves call ownership. For logout or session replacement, I cancel the owning scope; for work that must survive OS process death, I persist an operation and use durable scheduling. A `SupervisorJob` changes sibling-failure policy, not ownership. Its parent can cancel all children, and the owner must eventually cancel the supervisor itself. Because failure no longer automatically destroys peer tasks, the application must observe and report each failed `launch`. I would use a supervised app-level coordinator for independent cache or sync jobs, but a normal Job or lexical scope for a transaction whose pieces must succeed together.”

## How to answer in the interview

- **Why:** parent Job policy controls sibling fate.
- **How:** Job propagates ordinary child failure upward; SupervisorJob isolates direct children but still propagates parent cancellation downward.
- **Trade-off:** isolation increases responsibility to observe errors.
- **Failure case:** a supervised launch crashes through an unhandled exception.
- **Production solution:** own the scope, report task failure, and cancel it at shutdown or logout.

## Deep-dive talking points

Draw the Job tree and mark where failure propagation stops; compare root ownership, child `async` observation and parent cancellation.

## Follow-up questions

- [COR-11](../cor-11/): Does `supervisorScope` return immediately? **Answer:** no, it waits for its children.
- [COR-14](../cor-14/): Does a handler replace task-specific error handling? **Answer:** no, it observes uncaught failure rather than returning a usable result.

## Self-check rubric

Can I distinguish element and builder, predict sibling fate, name error observation, and define scope shutdown?

## References and reviewed-on date

- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — Job and supervision.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — Job hierarchy.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
