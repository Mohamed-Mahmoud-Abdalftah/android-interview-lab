---
id: "TST-09"
question: "How do you test Flow, StateFlow, and SharedFlow with Turbine?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 404
editorial_status: "reviewed"
---

# TST-09

## Original interview question

How do you test Flow, StateFlow, and SharedFlow with Turbine?

## What the interviewer evaluates

- Hot-flow subscription timing and replay/conflation semantics.
- Turbine assertions with deterministic scheduling.

## Explanation in Arabic

اختبار `Flow` يبدأ من contract: cold Flow ما تشتغلش إلا عند collect، أما `StateFlow` فهي hot ولها current value وتمنع emission لقيمة مساوية، و`SharedFlow` hot وسلوك replay/buffer فيها يتحدد بالإعداد. مع Turbine، استهلك `awaitItem()` بالترتيب ثم `awaitComplete()` للـcold أو اترك `test` تلغي collector في النهاية. ابدأ اشتراك `SharedFlow(replay=0)` قبل emission؛ الحدث السابق للـsubscriber لن يُستعاد.

## Practical walkthrough

عشان تختبر `Loading → Success` في ViewModel، fake repository تفضل معلقة بعد Loading وتطلقها بعد assertion؛ لو كتبت قيم StateFlow بسرعة، conflation قد تخفي مرحلة. `runTest` يتحكم في scheduler، لكنه لا يثبت أن UI lifecycle ستستقبل event أثناء STOP؛ ده يحتاج اختبار Route/Android منفصل. لا تغيّر replay لمجرد إسكات test فاشل.

## Why it matters and how it works

Turbine collects a Flow in a test scope. StateFlow may suppress equal updates and conflate fast changes, so a test must not demand every intermediate value unless scheduling ensures collection. SharedFlow with replay zero does not deliver past emissions to a late collector.

## Worked example

This small JVM test makes subscription and equality behavior explicit. It assumes JUnit 5, Turbine, and `kotlinx-coroutines-test` are test dependencies. The `test` block starts collecting before its assertions run; this matters for the replay-zero event.

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class FlowContractTest {
    @Test fun coldAndHotFlows() = runTest {
        flowOf("one", "two").test {
            assertEquals("one", awaitItem())
            assertEquals("two", awaitItem())
            awaitComplete()
        }

        val state = MutableStateFlow("Idle")
        state.test {
            assertEquals("Idle", awaitItem())
            state.value = "Loading"
            assertEquals("Loading", awaitItem())
            state.value = "Loading" // Equal value: no new StateFlow emission.
            expectNoEvents()
        }

        val events = MutableSharedFlow<String>(replay = 0)
        events.test {
            events.emit("Saved")
            assertEquals("Saved", awaitItem())
        }
    }
}
```

For a ViewModel Loading → Success test, keep the fake repository suspended until Loading is observed. A rapid pair of StateFlow writes may conflate, so do not assume this example proves every intermediate ViewModel state will always be delivered.

## Trade-offs and decision criteria

Turbine makes asynchronous assertions readable, but careless `advanceUntilIdle` can collapse intermediate StateFlow states. For one-shot UI events, design delivery and lifecycle explicitly rather than assuming SharedFlow is lossless.

## Failure modes

Emitting to SharedFlow before the test collector starts causes a missed event and apparent flake. Use subscription awareness or replay only if product semantics require it. Do not use replay solely to make the test pass if duplicate delivery is wrong.

## Production perspective

Test collector start, configuration recreation, lifecycle stop/start, equal-value updates and buffer overflow. Use stable fake sources and virtual time; integration UI tests verify actual collection behavior.

## Interview answer — short

“Turbine helps assert Flow emissions, but I account for cold versus hot flow semantics. StateFlow conflates/equality-suppresses updates, and a replay-zero SharedFlow can miss emissions before subscription.”

## Interview answer — structured

“I collect under runTest with a controlled scheduler and assert items in order with Turbine. A cold Flow starts on collection; StateFlow immediately exposes current state and can suppress equal updates; SharedFlow delivery depends on replay and buffer policy. I start collectors before emitting when appropriate, assert no unexpected events, and close the Turbine scope. I separately test lifecycle collection for UI behavior.”

## Interview answer — deep senior

“I test the semantics of the stream, not just a list of expected strings. A cold `Flow` starts when collected and can complete or fail; Turbine lets me assert items and terminal events. A `StateFlow` is already active, exposes its current value immediately and suppresses equal values. I use a controlled fake and test scheduler if I need to observe Loading before Success, because rapid updates can conflate. A replay-zero `SharedFlow` sends to current subscribers; I establish the collector before emitting, and separately test what the product should do if no screen is collecting. With Turbine I consume expected events, assert no extras when appropriate, and let the test scope cancel a hot collector rather than leak it. I also check retry, cancellation and error paths instead of changing dispatcher behavior merely to satisfy a timing assertion. The JVM test proves the Flow contract under its scheduler. It does not prove Activity STOP/START collection, configuration recreation or accessibility feedback; those need focused Android UI tests. For one-time navigation, I decide whether loss or replay is acceptable before choosing SharedFlow, Channel or acknowledged state.”

## How to answer in the interview

- **Why:** cold and hot flows deliver events under different timing rules.
- **How:** demonstrate Turbine assertions for cold completion, StateFlow current/equality and SharedFlow subscription.
- **Trade-off:** replay helps late collectors but can duplicate one-shot actions.
- **Failure case:** emission before replay-zero subscription is lost.
- **Production solution:** test Flow policy on JVM and lifecycle collection on device.

## Deep-dive talking points

Prompt for cold/hot collection, StateFlow equality, SharedFlow replay and collector startup.

## Follow-up questions

- [TST-06](../tst-06/): Which dispatcher can start collectors eagerly? **Answer:** UnconfinedTestDispatcher, used deliberately.
- [TST-18](../tst-18/): What does lifecycle add? **Answer:** collectors stop/restart and may miss or repeat events.

## Self-check rubric

Assert a cold Flow starts at collection, StateFlow exposes its current value and suppresses equal updates, and replay-zero SharedFlow requires an active collector. Use Turbine to consume or cancel all events and explain one lifecycle gap.

## References and reviewed-on date

- [Kotlin StateFlow/SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — StateFlow semantics.
- [Turbine README](https://github.com/cashapp/turbine) — testing API.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
