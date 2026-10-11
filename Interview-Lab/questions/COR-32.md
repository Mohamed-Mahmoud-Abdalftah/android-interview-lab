---
id: "COR-32"
question: "How do you test concurrent cancellation, supervision, and a timeout deterministically?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 113
editorial_status: "reviewed"
---

# COR-32

## Original interview question

How do you test concurrent cancellation, supervision, and a timeout deterministically?

## What the interviewer evaluates

Design deterministic coroutine tests for cancellation, supervision and timeout with virtual time and controlled fakes.

## Explanation in Arabic

اختبار concurrency بالـ`Thread.sleep` عشوائي وممكن ينجح بالصدفة. `runTest` مع `TestDispatcher` يسمح نتحكم في virtual time، و`CompletableDeferred` أو fake API يحدد ترتيب الأحداث. نختبر إن sibling اتلغى عند فشل required call، وإن supervisor حفظ مستقلين، وإن timeout انتهى عند الزمن المحدد؛ ونفصل ده عن test حقيقي لdriver blocking أو Android lifecycle.

## Why it matters and how it works

`runTest` skips/advances delays under its scheduler. Inject dispatchers so code does not escape to real IO/Default unexpectedly. `advanceTimeBy` moves virtual time and `runCurrent` executes queued tasks; `advanceUntilIdle` drains work. Verify state and cancellation signals rather than only elapsed wall time. Real HTTP and device timing require separate integration tests.

## Worked example

JVM example requires `kotlinx-coroutines-test`; it checks a timeout without real sleeping.

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.test.Test
import kotlin.test.assertNull

class TimeoutTest {
    @Test fun timeoutIsVirtual() = runTest {
        val result = withTimeoutOrNull(1_000) { delay(2_000); "late" }
        assertNull(result)
    }
}
```

## Trade-offs and decision criteria

Virtual time gives fast reproducible coroutine scheduling, but it cannot prove a legacy SDK responds to thread interruption or Android process death. Use controlled fake barriers for race paths; use integration/device tests for transport, lifecycle and platform behavior.

## Failure modes

Code that hard-codes `Dispatchers.IO` may run outside the test scheduler and make a test hang or become nondeterministic. A test that asserts only a returned error can miss a still-running sibling. Capture cancellation in the fake and assert the Job tree reaches quiescence.

## Production perspective

A repository suite injects one test scheduler, tests three-call all-or-nothing failure positions, partial-success supervision and timeout boundaries. A separate instrumented test checks Fragment collection stops at STOP; transport tests verify real SDK cancel behavior.

## Interview answer — short

“I use `runTest`, injected test dispatchers and controlled fakes, then advance virtual time rather than sleeping. I assert sibling cancellation, supervised partial results and timeout outcomes. I keep real SDK and Android lifecycle behavior for integration/device tests.”

## Interview answer — structured

“Deterministic concurrency tests control both scheduling and dependency responses. `runTest` supplies a virtual clock; I inject dispatchers and use fakes with `CompletableDeferred` gates to force one API failure while peers are pending. For all-or-nothing I assert the peers receive cancellation and no partial state is emitted. For supervision I assert healthy children complete and cancellation still stops all. For timeout I advance virtual time to the boundary and assert the result or exception without real `sleep`. I then test transport and lifecycle contracts separately because virtual time cannot verify them.”

## Interview answer — deep senior

“I structure the suite around observable invariants. All child jobs must finish or cancel when the operation returns; a failed required call must not publish partial data; independent calls should preserve healthy results; a parent cancellation must stop retries. `runTest` and a shared `TestCoroutineScheduler` let me advance delays and execute queued continuations deterministically. Controlled fakes expose start/cancel signals so I can force interleavings, including a failure just before timeout and cancellation during retry delay. I avoid unconfined production dispatchers in the unit under test or inject them, since real IO escapes the virtual clock. Finally I add focused integration tests for an actual blocking SDK, WorkManager recovery and Android lifecycle, where scheduler simulation is insufficient. `runTest` skips/advances delays under its scheduler.”

## Deep-dive talking points

Explain scheduler ownership, fake barriers, assertions beyond return values and the boundary of virtual-time evidence.

## Follow-up questions

- [COR-25](../cor-25/): What must all-or-nothing test assert? **Answer:** sibling cancellation and no partial UI commit.
- [COR-26](../cor-26/): What must supervision test assert? **Answer:** one failure leaves healthy siblings running while parent cancellation still stops all.

## Self-check rubric

Can I force an interleaving, advance virtual time, assert Job cleanup and name one device-level gap?

## References and reviewed-on date

- [Kotlin coroutines test API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — virtual-time scheduler and runTest.
- [Android coroutine testing guidance](https://developer.android.com/kotlin/coroutines/test) — dispatcher injection and Android tests.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
