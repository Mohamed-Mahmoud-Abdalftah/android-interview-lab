---
id: "COR-24"
question: "What is the risk of GlobalScope or creating a scope inside each repository method?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 105
editorial_status: "reviewed"
---

# COR-24

## Original interview question

What is the risk of GlobalScope or creating a scope inside each repository method?

## What the interviewer evaluates

Explain detached lifetime and why a fresh repository scope per method loses caller ownership.

## Explanation in Arabic

`GlobalScope` أو `CoroutineScope(...)` جديد جوه كل repository method بيقطع صلة الشغل بالـcaller: الشاشة تتقفل والطلب يفضل جاري، وممكن الخطأ ما يوصلش لحد. الـrepository الأفضل غالبًا يقدّم suspend function تورّث `Job` من الـcaller. لو شغل لازم يعيش بعد الشاشة، يبقى له owner محقون واضح؛ ولو لازم ينجو من process death يبقى state محفوظة وscheduler دائم.

## Practical walkthrough

لو repository function عملت `GlobalScope.launch` ورجعت فورًا، الشاشة ممكن تختفي والطلب يكمل ويكتب بيانات user قديم بعد logout. الأفضل الدالة تبقى `suspend` وتورّث Job المستدعي؛ لو لازم شغل يكمل بعد الشاشة، مرر scope مملوكة بوضوح على مستوى التطبيق ومعها shutdown وerror reporting. لو لازم تكمل بعد process death، خزّن العملية وجدولها بشكل دائم.

## Why it matters and how it works

Structured child jobs allow the caller to await completion and cancel obsolete work. Detached scopes return before work finishes and need separate exception handling/shutdown. A repository may legitimately own a shared application scope for a specific in-process operation, but ownership must be explicit and testable.

## Worked example

Illustrative repository contract; `remote.fetch` is a main-safe suspending API, and the caller chooses `viewModelScope` or another owner.

```kotlin
interface RemoteProfile { suspend fun fetch(id: String): String }

class ProfileRepository(private val remote: RemoteProfile) {
    suspend fun load(id: String): String = remote.fetch(id)
}
```

## Trade-offs and decision criteria

A suspend API gives the caller control over lifetime and failure. Injecting an application scope is reasonable for independent in-process work such as cache warming, with a supervisor, logger and shutdown. WorkManager plus persistence is required for restartable work under OS scheduling.

## Failure modes

Fresh scopes per invocation can leak network calls after navigation, race with logout and hide errors. A `GlobalScope.launch` payment update may be killed with the process and has no reliable completion channel. Returning from a method does not mean its detached child succeeded.

## Production perspective

A profile ViewModel calls `repository.load` in `viewModelScope`; navigation cancels it. A cache warmer uses an injected application-owned scope. Payment reconciliation persists an operation ID and schedules durable work, then exposes status from storage.

## Interview answer — short

“`GlobalScope` and per-call scopes detach work from its caller. I prefer suspend repository APIs that inherit the caller Job so cancellation and errors propagate. Longer-lived work needs an explicit owner; process-durable work needs persistent state and a scheduler.”

## Interview answer — structured

“The repository should not silently decide that every request lives for the process lifetime. A suspend function lets a ViewModel call it in `viewModelScope`, await its result and cancel it when the screen is gone. Creating a new scope in the repository loses that relationship; it also needs its own exception path and shutdown. If work intentionally outlives one screen, I inject a named application scope. If it must recover after process death, I persist the request and use WorkManager or another suitable durable mechanism.”

## Interview answer — deep senior

“I evaluate ownership separately from execution context. A repository can switch a blocking operation to IO without replacing the caller’s Job. `GlobalScope` or a fresh Job per method severs structured cancellation and completion: the method may return while a request still runs, the result can update stale session state, and failure may be reported only as uncaught. An application-level scope can be valid for shared in-process tasks if it is injected, supervised as appropriate, observed and cancelled at shutdown or logout. It cannot survive process death. For a payment or upload I store a stable operation ID and required inputs, schedule restartable work, and let UI collect persisted status. Tests cancel the caller and verify no late state mutation. A repository suspend function normally inherits the caller's Job, so navigation or logout can stop obsolete work and the caller observes completion. A scope created inside each method breaks that contract: the function can return while work continues and failure may have no useful consumer. If a cache warming task truly belongs to the application, I inject one owned scope with supervision, error reporting and shutdown. If it must survive process death, I persist intent and schedule recovery.”

## How to answer in the interview

- **Why:** hidden scopes hide completion, cancellation, and failures.
- **How:** keep suspend repository APIs under the caller's Job unless work has a deliberate longer-lived owner.
- **Trade-off:** an application scope survives navigation but not process death.
- **Failure case:** stale session writes or uncaught GlobalScope launch errors.
- **Production solution:** inject an owned scope or persist and schedule durable operations.

## Deep-dive talking points

Compare job inheritance, injected owner lifetime, logout and process death; distinguish `withContext(IO)` from creating a new Job.

## Follow-up questions

- [COR-06](../cor-06/): Which scope owns screen work? **Answer:** `viewModelScope` or view lifecycle scope, depending on the operation.
- [COR-30](../cor-30/): How preserve critical work? **Answer:** durable state plus a restartable scheduler.

## Self-check rubric

Can I name the owner, explain error/cancellation propagation and design a durable alternative for process death?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured ownership.
- [Android background work](https://developer.android.com/develop/background-work/background-tasks/persistent) — persistent scheduling.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
