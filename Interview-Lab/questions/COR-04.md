---
id: "COR-04"
question: "What is structured concurrency, and why is it valuable?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 85
editorial_status: "reviewed"
---

# COR-04

## Original interview question

What is structured concurrency, and why is it valuable?

## What the interviewer evaluates

Whether the candidate can explain the parent-child tree, completion waiting, cancellation propagation and why detached work is dangerous.

## Explanation in Arabic

`structured concurrency` معناها إن كل coroutine جديدة ليها owner واضح في شجرة `Job`. الأب ما يخلصش غير لما أولاده يخلصوا، وإلغاء الأب يلغيهم. ده بيمنع requests قديمة تفضل شغالة بعد خروج المستخدم من الشاشة، وبيخلّي الفشل والانتظار قابلين للتتبع بدل شغل سايب في الخلفية.

## Why it matters and how it works

`coroutineScope` creates a suspending boundary: it returns after all children finish. A failing child normally cancels siblings and the scope, and cancellation moves down the tree. `supervisorScope` changes sibling failure propagation, not parent cancellation. A separate `CoroutineScope` with a new Job breaks the hierarchy intentionally and needs its own owner.

## Worked example

Kotlin/JVM illustration using `kotlinx-coroutines-core`; `fetchA` and `fetchB` are caller-supplied suspend functions.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

suspend fun combine(
    fetchA: suspend () -> String,
    fetchB: suspend () -> String,
): String = coroutineScope {
    val a = async { fetchA() }
    val b = async { fetchB() }
    a.await() + b.await()
}
```

## Trade-offs and decision criteria

Structure gives predictable lifetime and failure handling, but all-or-nothing sibling cancellation may not suit independent widgets. Use supervision for intentionally independent children and handle each failure. Use durable scheduling for work that must outlive process lifetime.

## Failure modes

Launching into `GlobalScope` inside `combine` makes the function return without its children and lets work outlive the caller. Swallowing `CancellationException` also breaks cooperative shutdown; cancellation must propagate.

## Production perspective

A product-details request concurrently loads price and availability that must agree on one screen snapshot. The ViewModel calls a structured repository function. If either fails, both are cancelled and the UI receives one error state; stale results cannot update the screen after navigation away.

## Interview answer — short

“Structured concurrency gives coroutines an explicit parent-child lifetime. The parent waits for children, cancellation propagates downward, and ordinary child failure cancels the group. It makes UI work cancellable with its owner and exposes failures to the caller.”

## Interview answer — structured

“I use structured concurrency to make the lifetime of asynchronous work visible in the call tree. In `coroutineScope`, children inherit a parent Job and the function does not return until they finish. If an ordinary child fails, sibling work is cancelled and the error reaches the caller. That is right for all-or-nothing data assembly. For independent features I choose a supervised boundary and handle each result separately. On Android, `viewModelScope` owns screen requests; a repository should generally expose suspend functions and avoid detached scopes. Structure gives predictable lifetime and failure handling, but all-or-nothing sibling cancellation may not suit independent widgets. Use supervision for intentionally independent children and handle each failure. Use durable scheduling for work that must outlive process lifetime.”

## Interview answer — deep senior

“The important contract is ownership, not just concise syntax. A child Job is part of parent completion; cancelling the parent cancels descendants, while ordinary failure in a child cancels its parent and siblings. That lets a ViewModel cancel obsolete requests and lets a caller know that `combine` has truly completed. I use `coroutineScope` for dependent parallel calls and model one failure state. If partial success is valid, a `supervisorScope` can isolate sibling failures, but every child still needs an outcome and cancellation must be rethrown. A process can die regardless of scope, so critical persistence requires a durable queue or WorkManager rather than a detached coroutine. `coroutineScope` creates a suspending boundary: it returns after all children finish. A failing child normally cancels siblings and the scope, and cancellation moves down the tree. `supervisorScope` changes sibling failure propagation, not parent cancellation. A separate `CoroutineScope` with a new Job breaks the hierarchy intentionally and needs its own owner. Launching into `GlobalScope` inside `combine` makes the function return without its children and lets work outlive the caller. Swallowing `CancellationException` also breaks cooperative shutdown; cancellation must propagate. A product-details request concurrently loads price and availability that must agree on one screen snapshot. The ViewModel calls a structured repository function.”

## Deep-dive talking points

Trace a tree with one failing child, then compare normal and supervised siblings. Separate scope lifetime from process durability.

## Follow-up questions

- [COR-11](../cor-11/): Does supervision keep siblings alive? **Answer:** yes for child failure inside the supervised boundary, but parent cancellation still cancels all.
- [COR-24](../cor-24/): Why avoid `GlobalScope`? **Answer:** its lifetime is detached from the caller and failures become harder to own.

## Self-check rubric

Can I draw the Job tree, predict completion and cancellation, choose all-or-nothing or partial success, and name a durability boundary?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — parent-child structure.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — failure propagation.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
