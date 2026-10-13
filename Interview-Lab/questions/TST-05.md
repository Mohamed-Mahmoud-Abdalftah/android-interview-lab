---
id: "TST-05"
question: "What is runTest? How are virtual time and TestScope used?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "A"
phase: 4
priority: "P1"
order: 400
editorial_status: "reviewed"
---

# TST-05

## Original interview question

What is runTest? How are virtual time and TestScope used?

## What the interviewer evaluates

- runTest lifecycle and virtual-time scheduler semantics.
- What virtual time can and cannot control.

## Explanation in Arabic

`runTest` يخلق `TestScope` و`TestCoroutineScheduler` علشان نتحكم في coroutine scheduling والـ`delay` افتراضيًا بدل نوم حقيقي. `runCurrent()` يشغّل الشغل الجاهز الآن، و`advanceTimeBy()` يقدّم الساعة الافتراضية، وبعدها قد تحتاج `runCurrent()` عشان تنفّذ tasks على نفس اللحظة. لو ViewModel والـfake يستخدموا dispatchers مختلفة بسchedulers منفصلة، ترتيب الأحداث يبقى غير متوقع؛ شارك scheduler أو حقن dispatcher مناسب.

## Practical walkthrough

الاختبار يثبت Loading قبل release للـfake، وبعدها Success. `runTest` لا يسيطر تلقائيًا على callback حقيقي من SDK أو thread مستقل أو network؛ لازم fake أو adapter قابل للتحكم. ولا تستخدم `advanceUntilIdle()` قبل فحص intermediate state، لأنه ممكن يخفي المرحلة اللي تحاول تختبرها.

## Why it matters and how it works

A TestScope owns a TestCoroutineScheduler. TestDispatchers sharing that scheduler make scheduled delays deterministic. `runTest` waits for child coroutines under its rules and reports uncaught exceptions; dispatchers not replaced with test dispatchers may still use wall-clock time.

## Worked example

This JVM test runs with `kotlinx-coroutines-test` and JUnit 5. The injected dispatcher shares `runTest`'s scheduler, so both the intermediate state and the exact delay boundary are observable:

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

@OptIn(ExperimentalCoroutinesApi::class)
class VirtualTimeExampleTest {
    @Test fun eventAppearsOnlyAfterDelay() = runTest {
        val events = mutableListOf<String>()
        val dispatcher = StandardTestDispatcher(testScheduler)
        launch(dispatcher) {
            delay(1_000)
            events += "done"
        }

        runCurrent()
        assertEquals(emptyList<String>(), events)
        advanceTimeBy(999)
        runCurrent()
        assertEquals(emptyList<String>(), events)
        advanceTimeBy(1)
        runCurrent()
        assertEquals(listOf("done"), events)
    }
}
```

في Android استبدل `Dispatchers.Main` بقاعدة اختبار، واحقن أي dispatcher تاني يستخدمه الكود؛ المثال هنا JVM ولا يختبر SDK أو شبكة حقيقية.

## Trade-offs and decision criteria

Virtual time makes retry/backoff tests fast, but using it for real database/network calls gives false confidence. StandardTestDispatcher needs explicit scheduler progress; UnconfinedTestDispatcher starts tasks eagerly and changes ordering.

## Failure modes

A test hangs because a ViewModel uses production Main dispatcher or starts work in a scope outside the shared scheduler. Replace `Dispatchers.Main` with a test dispatcher and inject remaining dispatchers; always reset Main in teardown.

## Production perspective

Use a main-dispatcher test rule and shared scheduler across ViewModel collaborators. Verify exact retry time and cancellation, then add integration tests for actual HTTP timeouts.

## Interview answer — short

“runTest provides a TestScope with virtual time for coroutine delays. I share its scheduler with injected TestDispatchers and advance it deliberately; real I/O remains outside that control.”

## Interview answer — structured

“I use runTest for suspend and Flow logic so delay-based behavior can be checked without sleeping. TestScope owns the scheduler, and StandardTestDispatcher queues work until I call runCurrent, advanceTimeBy or advanceUntilIdle. I inject test dispatchers and replace Main for ViewModel tests. I do not assume runTest virtualizes real network or code launched on an unrelated dispatcher. I check intermediate states before advancing the scheduler to idle.”

## Interview answer — deep senior

“I use `runTest` to make coroutine timing explicit. It gives a test scope with a scheduler that can run queued work and skip virtual delays; `runCurrent` executes tasks ready at the current time, while `advanceTimeBy` moves the clock. For a retry policy I can assert one call at t=0, no second call just before the backoff, and exactly one next call after the scheduled boundary without sleeping a real second. If a ViewModel uses `StandardTestDispatcher`, I inject one using the test scheduler so its work is visible to the same control. I do not blindly call `advanceUntilIdle` before asserting Loading because it may run the repository completion and erase the intermediate state I wanted to observe. I also distinguish virtual time from control of all external work: a vendor callback, socket or unmanaged thread still needs a fake or integration setup. Finally, I check that child jobs complete or are canceled; a test that leaves background collection running can hang or leak. The scheduler makes a contract deterministic, but the contract must still be chosen deliberately.”

## How to answer in the interview

- **Why:** wall-clock sleeps make retries slow and unstable.
- **How:** describe TestScope, runCurrent and virtual-time advancement with exact call counts.
- **Trade-off:** virtual time controls coroutines on its scheduler, not vendor callbacks.
- **Failure case:** advanceUntilIdle skips the Loading state you intended to assert.
- **Production solution:** inject dispatchers and gates for deterministic state tests.

## Deep-dive talking points

Prompt for scheduler sharing, `runCurrent` versus `advanceTimeBy`, escaping real dispatchers and intermediate assertions.

## Follow-up questions

- [TST-06](../tst-06/): Which dispatcher queues launch work? **Answer:** StandardTestDispatcher until scheduler progress.
- [TST-10](../tst-10/): How test backoff? **Answer:** advance virtual time in steps and assert attempts.

## Self-check rubric

Explain TestScope and its scheduler, show runCurrent versus advanceTimeBy, assert the event before and after virtual time advances, and identify a real external callback that virtual time alone cannot control.

## References and reviewed-on date

- [Kotlin coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) — runTest and scheduler.
- [Android coroutine testing](https://developer.android.com/kotlin/coroutines/test) — test dispatchers.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
