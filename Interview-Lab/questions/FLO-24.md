---
id: "FLO-24"
question: "How do you test Flow/StateFlow with runTest and Turbine?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 137
editorial_status: "reviewed"
---

# FLO-24

## Original interview question

How do you test Flow/StateFlow with runTest and Turbine?

## What the interviewer evaluates

Design deterministic runTest and Turbine assertions for emissions, cancellation and conflation.

## Explanation in Arabic

`runTest` بيخلينا نتحكم في virtual time لاختبار `debounce` و`delay` من غير `Thread.sleep`. Turbine تدي `awaitItem`, `expectNoEvents`, `cancelAndIgnoreRemainingEvents` علشان نثبت sequence ونقفل collection. StateFlow عندها initial value وconflation، فلا نفترض إن كل update سريع هيتشاف؛ نتحكم في scheduler أو نختبر آخر state حسب العقد.

## Why it matters and how it works

Inject dispatchers so operators use the test scheduler; advance time and run queued tasks deliberately. Test both cold subscription counts and hot initial/replay behavior. Turbine is a separate test dependency; document version through the project catalog. Device lifecycle and real transport behavior require integration tests.

## Worked example

JVM test illustration assumes `kotlinx-coroutines-test`, `app.cash.turbine:turbine` and kotlin-test; it checks a simple cold flow.

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class StreamTest {
    @Test fun valuesInOrder() = runTest {
        flowOf(1, 2).test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            awaitComplete()
        }
    }
}
```

## Trade-offs and decision criteria

Turbine improves readable stream assertions but does not fix an uncontrolled real dispatcher. Virtual time is fast and precise for coroutine scheduling, not a proof of Android process death or real network timing. Test semantics, not implementation details such as exact internal buffering.

## Failure modes

A test that never cancels a StateFlow turbine can hang because StateFlow never completes. Using `Thread.sleep` for debounce creates flaky timing. Expecting every rapid StateFlow assignment ignores equality/conflation behavior.

## Production perspective

A search ViewModel test advances 299 ms to assert no request, then the next millisecond to assert one query, delivers an old response after a new query and verifies it never renders. Separate instrumented tests drive START/STOP and rotation.

## Interview answer — short

“I use runTest and a test scheduler to control time, and Turbine to assert emissions and close collectors. I account for StateFlow’s initial value and conflation. I keep real lifecycle and transport guarantees for integration tests.”

## Interview answer — structured

“Flow tests should control timing and collection. `runTest` lets me advance virtual time for debounce and timeout; Turbine makes it straightforward to await an item, assert no event or complete, and cancel an endless collector. I inject dispatchers so work stays on the same scheduler. For StateFlow I expect an initial value and latest-state semantics, not every rapid intermediate value. I test cold flows for repeated subscriptions and hot flows for late subscribers, then use Android integration tests for lifecycle behavior.”

## Interview answer — deep senior

“I set up tests around the stream contract: what does a first collector receive, what happens if a second subscribes, which values may be conflated, and what happens after cancellation? `runTest` provides a virtual scheduler, but production `Dispatchers.IO` can escape it unless injected. I use Turbine to make terminal and non-terminal expectations explicit and always cancel a StateFlow collector. For debounce I advance time to just before and after the threshold; for `flatMapLatest` I hold an old fake request, start a new one and release the old response to ensure it cannot replace new state. For `SharedFlow` I test no-subscriber and replay cases. Device tests cover actual lifecycle/Room/HTTP integration that virtual time cannot prove.”

## Deep-dive talking points

Test subscription count, initial value, late subscriber, virtual time and cancellation cleanup.

## Follow-up questions

- [FLO-15](../flo-15/): How test debounce? **Answer:** advance virtual time around its threshold.
- [FLO-06](../flo-06/): Should every StateFlow value appear? **Answer:** no; equality and conflation can suppress or skip intermediate updates.

## Self-check rubric

Can I write a terminal and endless-stream test, control time, close collectors and name a device test?

## References and reviewed-on date

- [Kotlin coroutines test API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — runTest and scheduler.
- [Turbine project](https://github.com/cashapp/turbine) — Flow testing assertions.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
