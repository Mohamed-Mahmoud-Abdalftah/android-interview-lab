---
id: "COR-29"
question: "A blocking SDK call does not respond to coroutine cancellation. What can you do?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 110
editorial_status: "reviewed"
---

# COR-29

## Original interview question

A blocking SDK call does not respond to coroutine cancellation. What can you do?

## What the interviewer evaluates

Reason about blocking SDK cancellation, interruption, resource closure and uncertain external effects.

## Explanation in Arabic

لو SDK synchronous حجز thread ومابيسمعش coroutine cancellation، `withTimeout` أو `cancel` هيعلّموا الـJob لكن النداء ممكن يفضل شغال لحد ما يرجع. ننقله من Main إلى dispatcher مناسب، ونستخدم SDK `cancel`/`close` إن موجود. `runInterruptible` على JVM ممكن يرسل thread interrupt لكود بيحترمه، لكن مش ضمان لكل native/SDK، ولا معناه إن server side effect اتلغت.

## Practical walkthrough

لو SDK بيقرأ ملف ومش بيرد على cancel، نقل النداء لـ`IO` يمنع تجميد UI لكنه مش يوقفه. جرّب cancel/close الرسمية للـSDK، أو `runInterruptible` فقط لو موثق إنه يحترم thread interrupt. لو native call مستحيل إيقافه، حدّ عدد العمال وامنع نشر النتيجة المتأخرة. في write side effects، اسأل عن الحالة قبل إعادة المحاولة.

## Why it matters and how it works

Cancellation is cooperative at coroutine suspension points. For blocking JVM code, `runInterruptible(Dispatchers.IO)` couples Job cancellation to thread interruption, subject to the call responding correctly. Otherwise isolate the driver, cap concurrent calls, set native/client timeouts, and discard stale results. External writes need idempotency/reconciliation.

## Worked example

JVM illustration assumes `BlockingSdk.read` is documented interruptible; if it is not, do not claim prompt cancellation.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runInterruptible

interface BlockingSdk { fun read(id: String): ByteArray }

suspend fun readSdk(sdk: BlockingSdk, id: String): ByteArray =
    runInterruptible(Dispatchers.IO) { sdk.read(id) }
```

## Trade-offs and decision criteria

Use `runInterruptible` only with a library whose blocking behavior responds safely to interruption. A dedicated SDK cancel method may be better. A thread pool cap protects the app when calls are uninterruptible, but latency remains. Prefer an async maintained API when possible.

## Failure modes

Wrapping an uninterruptible call in `withTimeout` does not stop the thread promptly. Calling `Thread.stop` is unsafe. Retrying a timed-out write can duplicate side effects. A cancelled caller must not publish a late result to obsolete UI state.

## Production perspective

A document scanner SDK blocks during OCR. The repository runs it off Main, calls its cancel API on screen exit, limits concurrent scans and verifies no late result is shown. If the SDK cannot cancel, product UX shows a bounded wait and telemetry captures slow calls; payment-like side effects are reconciled separately.

## Interview answer — short

“Coroutine cancellation cannot forcibly stop arbitrary blocking code. I use the SDK’s cancel or close API, or `runInterruptible` only if the JVM call honors interruption. I keep it off Main, bound concurrency, discard late UI results and reconcile uncertain remote effects.”

## Interview answer — structured

“I would inspect the SDK’s actual cancellation contract. A coroutine timeout marks its Job cancelled, but a synchronous call can hold its thread until completion. On the JVM, `runInterruptible` can interrupt an interruption-aware blocking API; otherwise I invoke the SDK’s own cancel/close method if it has one. I run it off Main, set transport/native timeouts and limit active calls. I still check the caller’s state before publishing a result, and I never assume cancelling a payment call undid its server-side transaction.”

## Interview answer — deep senior

“The exact fix depends on what the SDK can stop. A cancellable callback API should be adapted with cancellation registration; an interruptible blocking JVM call can use `runInterruptible`, whose effectiveness depends on the driver honoring interrupts. An uninterruptible native call cannot be made promptly cancellable by a coroutine wrapper, so I isolate it from Main, cap calls, set whatever SDK deadline exists, and report a vendor defect if it threatens ANRs or thread exhaustion. The screen Job may cancel while the call continues; I discard late results and avoid retaining Activity references. For remote writes I persist an operation ID and reconcile server status after timeout, because local cancellation has no rollback guarantee. Tests include cancellation during the block and delayed completion. My response depends on the SDK's documented stop mechanism. If it has a cancel handle, wire coroutine cancellation to it; if the JVM call honors interrupts, `runInterruptible` can be appropriate. If the call ignores both, place it on bounded workers, enforce a caller deadline, and prevent the stale return from updating UI, while accepting that the thread may remain occupied. A timed-out write may have reached the server, so retry needs status reconciliation.”

## How to answer in the interview

- **Why:** cancelling a Job does not forcibly terminate arbitrary blocking code.
- **How:** use the SDK's cancel API, or runInterruptible for truly interruptible JVM calls.
- **Trade-off:** isolation and worker caps protect the app while a stuck call may still consume a thread.
- **Failure case:** timeout mistaken for server rollback.
- **Production solution:** bounded execution and reconciliation for side effects.

## Deep-dive talking points

Trace cancellation signal, thread interruption, SDK cancel API, late callback and server-side effect.

## Follow-up questions

- [COR-17](../cor-17/): Does timeout force stop? **Answer:** no, the block must cooperate or respond to interruption.
- [COR-31](../cor-31/): What if the SDK runs on Main? **Answer:** it blocks UI dispatch and can cause ANR.

## Self-check rubric

Can I identify SDK capability, protect Main, bound resources and handle late/uncertain results?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — cooperative timeout and runInterruptible note.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main safety.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
