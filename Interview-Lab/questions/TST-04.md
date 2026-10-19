---
id: "TST-04"
question: "What makes a class testable?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 399
editorial_status: "reviewed"
---

# TST-04

## Original interview question

What makes a class testable?

## What the interviewer evaluates

Identify hidden inputs and side effects, choose a useful seam for time and I/O, and explain how to test observable behavior without claiming every class needs an interface or every test can run on the JVM.

## Concept and technical explanation

A class is easier to test when its inputs and collaborators are explicit and its results can be observed through a stable contract. External time, network, disk, randomness and coroutine scheduling are common sources of nondeterminism. Constructor injection can expose the collaborators a test needs to replace; a narrow interface or function boundary is useful when it captures real behavior, not because every concrete class needs a matching interface. Pure decision logic can be tested directly. Android framework integration still needs an appropriate integration or device test.

A suspending API makes completion and failure observable to its caller. If a class launches its own work, the owner should supply or clearly own its `CoroutineScope`; otherwise the caller cannot reliably wait for or cancel it. Inject a `CoroutineDispatcher` where switching execution context matters, and use `runTest` with a `TestDispatcher` sharing its scheduler. `StandardTestDispatcher` queues new work; a test may need `runCurrent` or `advanceUntilIdle`. Neither virtual time nor a fake repository proves that the real adapter works.

## Practical walkthrough (English)

An order processor fetches an order, compares its expiry with an injected `Clock`, saves the status, and returns the same status. The caller awaits one suspending operation. A JVM test can supply a fixed clock, fake API and fake store, and a `StandardTestDispatcher(testScheduler)`. It checks the exact expiry boundary and saved result. A separate adapter test verifies real database behavior and transaction semantics.

## Explanation in Arabic

الكلاس يبقى أسهل في الاختبار لما الـ Inputs والـ Dependencies تكون واضحة والنتيجة تقدر تلاحظها من الـ Public Behavior. الوقت والـ Network والـ Disk وجدولة الـ Coroutines مصادر شائعة لنتائج متقلبة. أحقن `Clock` أو Repository لما ده يساعدني أتحكم في الحد الخارجي، لكن مش لازم أعمل Interface لكل كلاس. الـ Pure Function التي لا تعتمد على حالة مخفية أختبرها مباشرة، بينما تكامل Android Framework محتاج اختبار مناسب له.

لو الدالة `suspend` بترجّع نتيجة، الـ Caller يقدر ينتظر النجاح أو الفشل. لو الكلاس بيعمل `launch` بنفسه، لازم يكون الـ Scope مملوكًا بوضوح أو متاحًا للاختبار والإلغاء. لما الكود يغيّر الـ Dispatcher، أقدر أحقنه وأستخدم `runTest` و`TestDispatcher` على Scheduler واحدة. `StandardTestDispatcher` بتصفّ الشغل؛ مش بتشغّله كله فورًا، وقد أحتاج `runCurrent` أو `advanceUntilIdle` قبل الـ Assert.

## Practical walkthrough

عندي `OrderProcessor` بيجيب الطلب، يقارن `expiresAt` بوقت `Clock` محقونة، يحفظ `EXPIRED` أو `PROCESSED` ويرجّع نفس النتيجة. في Unit Test أمرر `Clock.fixed` وFake API وFake Store، و`StandardTestDispatcher(testScheduler)`. أختبر حالة الوقت عند الحد الفاصل وأتأكد إن القيمة اتخزنت فعلًا. بعد كده أعمل Integration Test منفصل للتعامل الحقيقي مع قاعدة البيانات؛ نجاح الـ Fake وحدها ما يثبتش سلوك الـ Transaction.

## Why it matters and how it works

Explicit collaborators remove hidden input. A fixed clock makes expiry cases repeatable. A suspending result lets the caller await the operation and observe an error. A shared test scheduler controls coroutine work that uses injected test dispatchers. The remaining real I/O boundary needs its own test.

## Worked example

This standalone JVM example compiles in the Kotlin lab. The order is expired when the current instant reaches the expiry instant; that boundary is a business decision rather than a testability rule.

```kotlin
import java.time.Clock
import java.time.Instant
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext

data class Order(val id: String, val expiresAt: Instant)
interface OrderApi { suspend fun fetch(id: String): Order }
interface OrderStore { suspend fun saveStatus(id: String, status: String) }

class OrderProcessor(
    private val api: OrderApi,
    private val store: OrderStore,
    private val clock: Clock,
    private val ioDispatcher: CoroutineDispatcher,
) {
    suspend fun process(id: String): String = withContext(ioDispatcher) {
        val order = api.fetch(id)
        val status = if (!clock.instant().isBefore(order.expiresAt)) "EXPIRED" else "PROCESSED"
        store.saveStatus(id, status)
        status
    }
}
```

## Trade-offs and decision criteria

Adding a seam has a maintenance cost. Keep deterministic policy simple; inject a clock or scheduler when behavior depends on them. A concrete collaborator can be fine if it is already easy to construct and test. Fake-based unit tests give fast feedback; focused integration tests cover serialization, persistence and framework behavior.

## Failure modes

A method creates a detached `CoroutineScope(Dispatchers.IO)` and returns before its write finishes, so an assertion races with the work and cancellation is unclear. Another test passes with a fake store while the real transaction loses data. A `TestDispatcher` only controls work dispatched through the shared scheduler; it does not magically control unrelated threads or network calls.

## Production perspective

Review whether business decisions can be tested through public behavior, who owns any launched coroutine, and which boundaries still require adapter tests. Cover normal, error, cancellation and expiry-boundary paths. Prefer a small number of meaningful seams to universal interface pairs or a blanket ban on `Dispatchers.IO`.

## Interview answer — short

A class is testable when I can give it the inputs and collaborators it needs, control time or scheduling where they matter, and observe the result or failure. For an order-expiry rule, I would inject a clock and repository, then test a fixed instant. I would not add an interface to every class or assume a fake-based test proves the real database works.

## Interview answer — structured

I start by looking for hidden inputs: a global singleton, `System.currentTimeMillis()`, a network call made in a constructor, or a coroutine launched in an unowned scope. Those make a test depend on the machine, timing or shared state. I expose only the boundaries needed by the behavior. Constructor injection lets a test provide a fixed `Clock` and fake collaborator; an explicit return value or a suspending function makes completion and errors observable.

For example, an `OrderProcessor` can fetch an order, compare `expiresAt` against an injected clock, save a status and return it. A JVM test checks the exact expiry boundary with a fixed clock and fake store. If production code switches dispatchers, I can inject one and use `runTest` with a `TestDispatcher` sharing the test scheduler. I still need a separate test for the real persistence adapter, because a fake does not validate Room transactions.

I would choose the seam that helps a real test or change. Pure logic may need no interface at all, while a ViewModel or Android resource boundary can require framework-aware tests. Testability means controllable behavior and clear ownership, not maximal abstraction or a promise of 100% JVM coverage.

## Interview answer — deep senior

Testability starts with a contract: given these inputs and collaborator responses, what output, state change or failure should the caller observe? I look for nondeterministic inputs such as time, network, randomness and scheduling. I keep policy separate from adapters where that boundary pays for itself, but I do not force every dependency behind an interface. A concrete immutable value is often simpler to pass directly.

For a suspending order operation, I make the caller await `process(id)` instead of hiding work in a new `CoroutineScope`. I inject a `Clock` to test the instant just before and at expiry. I inject the dispatcher only if the class actually switches execution context. In a coroutine test I pass `StandardTestDispatcher(testScheduler)` so `runTest` and the code under test share a scheduler. Since that dispatcher queues tasks, I use `runCurrent` or `advanceUntilIdle` where necessary. If code switches to a real dispatcher or does actual I/O, virtual time will not control that work; I must handle it explicitly.

I then test the contract at multiple levels. Unit tests with fakes cover expiry, failures and cancellation behavior quickly. Integration tests exercise the real database or network adapter, including transactions and serialization. Device tests cover behavior tied to Android framework services. A fake passing cannot prove the real implementation is correct, and a high coverage percentage cannot prove the assertions are useful.

The failure signal in review is usually hidden ownership: constructor side effects, mutable global state, or fire-and-forget coroutines whose completion no caller can observe. I fix that boundary first. The result is a class whose behavior can be explained and tested without pretending that all tests are synchronous or that a JVM test covers the full application.

## How to answer in the interview

Name hidden inputs, show one fixed-time test seam, explain how a caller observes completion, and state which real adapter still needs integration testing. Mention the cost of extra abstractions.

## Deep-dive talking points

Clock and I/O boundaries; owned versus detached coroutine scope; shared `TestCoroutineScheduler`; queued `StandardTestDispatcher` work; fake versus real-adapter tests.

## Follow-up questions

- **Interviewer:** "Why inject a dispatcher?"
  **Answer:** "If the class switches context internally, a test dispatcher sharing `runTest`'s scheduler lets me control that work. It does not make unrelated real threads or network calls virtual."

- **Interviewer:** "Does `StandardTestDispatcher` execute launched work immediately?"
  **Answer:** "No. It queues new work on its scheduler. I use `runCurrent`, `advanceUntilIdle`, or suspension points as appropriate before asserting."

- **Interviewer:** "Can a pure JVM test prove a Room transaction is correct?"
  **Answer:** "A fake can verify policy calls, but transaction semantics need a test against the real adapter in a suitable environment."

## Self-check rubric

Identify hidden time or I/O, describe a controllable public contract, test the exact expiry boundary, explain test-scheduler ownership, and name an integration limit.

## References and reviewed-on date

- [Android: Testing Kotlin coroutines](https://developer.android.com/kotlin/coroutines/test) — dispatcher injection, shared schedulers and scope ownership.
- [Kotlin: `StandardTestDispatcher`](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-standard-test-dispatcher.html) — queued execution semantics.
- [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals) — testable architecture and test doubles.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
