---
id: "ARC-18"
question: "How do you keep a ViewModel main-safe and testable?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 163
editorial_status: "reviewed"
---

# ARC-18

## Original interview question

How do you keep a ViewModel main-safe and testable?

## What the interviewer evaluates

Explain main-safe boundaries, scope ownership, injected dispatchers, immutable state and deterministic tests.

## Explanation in Arabic

ViewModel يفضل يستقبل main-safe suspend APIs من data/domain؛ لو repository عنده blocking I/O أو CPU heavy، هو اللي يستخدم dispatcher مناسب بـ`withContext`، مش ViewModel ترش `Dispatchers.IO` على كل call بلا فهم. ViewModel يطلق screen work في `viewModelScope` ويكشف immutable `StateFlow<UiState>`، ويتعامل مع cancellation والـerrors من غير swallowing. اختبارات ViewModel تحقن fake repo وtest dispatcher/scheduler، وتتحقق من state transitions. لو شغل لازم يكمل بعد خروج الشاشة، استخدم durable scheduling/persistence بدل ViewModel scope.

## Why it matters and how it works

Android guidance places main-safety responsibility on suspend callers below the ViewModel and recommends lifecycle-aware scopes for screen work. Injecting dispatchers or abstractions lets tests control execution timing. State holders should not block Main.

## Worked example

Illustrative repository boundary requiring kotlinx-coroutines:
```kotlin
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
class ParsingRepository(private val cpu: CoroutineDispatcher) {
    suspend fun parse(raw: String): Int = withContext(cpu) { raw.toInt() }
}
```
This is a small example of dispatcher ownership, not proof that `toInt()` itself needs background execution.

## Trade-offs and decision criteria

Switch dispatcher only for genuinely blocking or expensive work; unnecessary context switches add complexity. ViewModel tests with fakes are fast, but integration tests still need real repository/database behavior. `viewModelScope` is wrong for durable operations after process death.

## Failure modes

A ViewModel calls `Thread.sleep` on Main inside `launch`, causing ANR despite being in a coroutine. Another failure is `runCatching` swallowing cancellation and emitting an error after navigation. Audit actual blocking APIs and rethrow cancellation.

## Production perspective

A search ViewModel collects repository results in `viewModelScope`; repository guarantees main-safe blocking boundaries and returns typed outcomes. Unit tests use fake search responses and a test dispatcher; process-death-sensitive upload uses WorkManager plus persisted state.

## Interview answer — short

I keep ViewModels main-safe by calling main-safe data/domain APIs, using lifecycle-owned coroutines, and exposing immutable state. Blocking work is moved at its owning boundary, and tests inject fakes and controlled dispatchers.

## Interview answer — structured

A ViewModel should coordinate screen state, not decide where every database or parsing call runs. Repository and use-case APIs should be safe to call from Main; if they wrap blocking work, they switch to an injected dispatcher internally. I use `viewModelScope` for screen-lifetime work, expose read-only `StateFlow`, and propagate cancellation. In tests I inject a fake repository and a test scheduler so state transitions are deterministic. Durable work belongs outside ViewModel lifetime. In a test, I would provide a fake repository and controlled coroutine dispatcher, then assert loading, success, error and cancellation states without sleeping. I would also verify that a blocking driver is switched at the repository boundary rather than blindly wrapping every ViewModel call in IO.

## Interview answer — deep senior

Main safety is an API contract. A suspend function is not automatically off Main, so I inspect the operations it performs and place `withContext` around genuinely blocking or CPU-intensive work at the repository boundary. Injected dispatchers permit deterministic tests and avoid hardcoded environment choices. The ViewModel owns UI event handling and immutable state production, with `viewModelScope` cancelling obsolete screen work. It should not hold an Activity or process-wide mutable singleton. I test success, errors, rapid query changes, cancellation and restoration. A network request that must complete after process death needs persisted work and an appropriate scheduler, not a long-lived ViewModel or `GlobalScope`. This keeps both frames and tests predictable. Main safety should be documented and tested at the API boundary. A suspend function may execute entirely on Main, so its implementation must move blocking or heavy work when necessary. The ViewModel owns screen scope and state, but it should not catch cancellation as a normal error or keep an Activity reference. For process-death-sensitive work I persist intent and use suitable durable scheduling. Integration tests still verify the real database/network adapter, because a fake ViewModel test cannot prove those parts.

## Deep-dive talking points

Explain main safety as an API promise, not a keyword; trace cancellation, dispatcher injection and durable-work ownership.

## Follow-up questions

- [COR-02](../cor-02/): Does `suspend` mean background? **Answer:** no; the callee must manage blocking work.
- [ARC-20](../arc-20/): How do you test ViewModel state? **Answer:** fake dependencies plus controlled coroutine scheduler and state assertions.

## Self-check rubric

Diagnose a Main-thread blocking suspend call, show where to switch dispatcher, and name a deterministic ViewModel test seam.

## References and reviewed-on date

- [Android coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — main-safe suspend APIs and dispatcher injection.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — state-holder responsibilities.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
