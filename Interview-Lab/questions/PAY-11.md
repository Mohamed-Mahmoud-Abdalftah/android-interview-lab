---
id: "PAY-11"
question: "How would you test SDK callback timeout and device disconnection?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 481
editorial_status: "reviewed"
---

# PAY-11

## Original interview question

How would you test SDK callback timeout and device disconnection?

## What the interviewer evaluates

- Deterministic callback/time control plus real device disconnection tests.
- Lost response, duplicate callback and late success cases.

## Explanation in Arabic

كيف تقوم باختبار مهلة الاستدعاءات (SDK Callback Timeout) وفصل العتاد المفاجئ (Device Disconnection) برمجياً دون الحاجة لأجهزة حقيقية؟

1. تحدي اختبارات العتاد في بيئة الـ CI:
   - يستحيل توصيل ماكينة POS حقيقية بكل سيرفر في GitHub Actions لنزع كابل الـ USB يدوياً أثناء الاختبارات!
   - إذا اعتمدت على الاختبار اليدوي، فلن تتمكن من تغطية حالات نادرة مثل: ماذا لو استجاب البنك بعد 29.9 ثانية؟ ماذا لو فُصل قارئ البطاقات اللاسلكي أثناء إدخال الـ PIN؟

2. استراتيجية الاختبار الهندسي عبر الـ Fake Test Double:
   - بفضل عزل الـ SDK وراء واجهة `CardReaderManager` (كما صممنا في PAY-09)، يمكننا بناء `FakeCardReaderManager` يحتوي على **مقابض تحكم بالاختبار (Test Knobs)**.
   - **مقابض الاختبار الأساسية**:
     * `simulateTimeout()`: محاكاة عدم رد الهاردوير نهائياً لتفعيل مؤقت الـ Timeout.
     * `simulateHardwareDisconnect()`: إطلاق حدث فصل فوري أثناء المعالجة.
     * `simulateBadChipError()`: محاكاة تلف الشريحة الإلكترونية.

3. اختبار الوقت الافتراضي باستخدام `runTest` في Kotlin Coroutines:
   - استخدام `runTest` للتحكم في الوقت الافتراضي (Virtual Time) عبر `advanceTimeBy(30_000)`.
   - التحقق من أنه بعد 30 ثانية تحديداً، قام النظام بإلغاء الجلسة، وتحديث الحالة إلى `UNKNOWN`، وإدراج طلب Reversal في قاعدة بيانات Room!

## Practical walkthrough

اختبار كامل في كوتلن يحاكي انقطاع العتاد ونفاد الوقت ويتحقق من إطلاق الـ Reversal:
```kotlin
class PaymentOrchestratorTest {
    private val fakeCardReader = FakeCardReaderManager()
    private val paymentDao = FakePaymentDao()
    private val orchestrator = PaymentOrchestrator(fakeCardReader, paymentDao)

    @Test
    fun `card reader timeout enqueues reversal and aborts transaction`() = runTest {
        // 1. ضبط الـ Fake لمحاكاة الصمت التام (عدم الرد):
        fakeCardReader.shouldSimulateTimeout = true

        val job = launch {
            orchestrator.processCardPayment(amountCents = 10000)
        }

        // 2. تقديم الوقت الافتراضي لـ 30 ثانية لتجاوز مهلة الـ Timeout:
        advanceTimeBy(30_001)

        // 3. التحقق من أن النظام رصد الـ Timeout وعكس العملية:
        val pendingReversals = paymentDao.getAllPendingReversals()
        assertEquals(1, pendingReversals.size)
        assertEquals(10000, pendingReversals.first().amountCents)
        assertEquals("TIMEOUT_REVERSAL", pendingReversals.first().reason)
        job.cancel()
    }

    @Test
    fun `abrupt usb disconnect during pin entry emits reader error`() = runTest {
        val events = mutableListOf<CardReaderEvent>()
        val collectJob = launch {
            fakeCardReader.startCardInteraction(5000).collect { events.add(it) }
        }

        fakeCardReader.emitEvent(CardReaderEvent.PinRequired)
        // محاكاة فصل الكابل فجأة أثناء كتابة الـ PIN:
        fakeCardReader.simulateDisconnection()

        val lastEvent = events.last()
        assertTrue(lastEvent is CardReaderEvent.ReaderError)
        assertEquals(999, (lastEvent as CardReaderEvent.ReaderError).errorCode)
        collectJob.cancel()
    }
}
```

## Why it matters and how it works

A domain test can inject a fake clock and scripted SDK callbacks to assert state transitions and durable outbox writes. The adapter contract must distinguish transport failure from authoritative decline. Hardware tests verify actual vendor semantics and recovery references.

## Worked example

Test sequence: persist attempt, invoke authorize, deliver no callback until timeout, assert UNKNOWN with same operation ID; then deliver late Approved and assert guarded transition or reconciliation. Restart repository from database and verify status lookup, not a second charge.

### Kotlin/Android sketch

```kotlin
// Domain test: fake maps an elapsed SDK timeout to Unknown; not an issuer.
@Test fun timeoutStaysUnknownUntilLookup() = runTest {
    val fake = ScriptedGateway(initial = TerminalOutcome.Unknown)
    val repo = PaymentRepository(fake, inMemoryAttempts())
    val id = "op-42"
    repo.start(id, amountMinor = 1_250)
    assertEquals(PaymentState.Unknown, repo.state(id))
    fake.lookupResult = TerminalOutcome.Approved("provider-7")
    repo.reconcile(id)
    assertTrue(repo.state(id) is PaymentState.Approved)
}
// ScriptedGateway/PaymentRepository are test doubles/app contracts.
// Imports: kotlinx.coroutines.test.runTest; org.junit.Test/Assert.*.
// Separate tests inject late and duplicate callbacks and a fake clock.
```

## Trade-offs and decision criteria

Fakes are fast and exhaustive for ordering but cannot model all firmware, power and EMV behavior. Real terminal tests are slower and may need a provider sandbox or certification environment; include both.

## Failure modes

A test only checks that UI shows an error after timeout; it misses duplicate charge risk. Another test cancels a coroutine and assumes SDK payment canceled. Assert server-side identity and reversal/reconciliation obligations explicitly.

## Production perspective

Keep a failure matrix by device model, firmware, ABI, SDK version and network mode. Release smoke tests run on actual hardware where possible and preserve redacted operation IDs for support.

## Interview answer — short

Test SDK timeouts and hardware disconnects programmatically using a configurable FakeCardReaderManager implementing the domain interface. Use Kotlin Coroutines runTest and advanceTimeBy() to simulate virtual timeouts and trigger simulated disconnections, asserting that the state machine enqueues the reversal and fails gracefully.

## Interview answer — structured

Verifying peripheral hardware failures deterministically requires software-mediated fault injection.

First, **The Configurable Test Double Architecture**. Next, because proprietary payment kernels cannot run in cloud CI environments, implement a full-fidelity `FakeCardReaderManager`. Expose explicit programmatic fault hooks: `simulateTimeout()`, `simulateDisconnection()`, and `simulateTamperEvent()`.
**Virtual Time Testing with `runTest`**. In Kotlin Coroutines, test timeout logic using `runTest`. Calling `advanceTimeBy(30_000L)` instantly advances virtual time without delaying CI execution by real clock seconds. Assert that the underlying timeout handler triggers, cancels the active peripheral flow, marks the transaction as `UNKNOWN`, and persists a reversal payload.
**Simulating Asynchronous Disconnection Events**. Finally, emit abrupt disconnection errors mid-transaction (e.g. Between `PinRequired` and `CardReadSuccess`). Verify that the presentation layer clears confidential screens immediately and logs the hardware fault telemetry without leaving leaked coroutines or corrupted database locks.


## Interview answer — deep senior

From an Android instrumentation and edge-case testing perspective, integration testing extends to OS hardware simulations.

First, with USB Host State Simulation via ADB, on instrumented test devices connected via ADB, developers can simulate USB OTG disconnection by altering Android USB power states via ADB shell: `adb shell am broadcast -a android.hardware.usb.action.USB_DEVICE_DETACHED`. This verifies that Android `BroadcastReceiver` lifecycle handlers fire and gracefully release hardware device handles. Next, with Chaos Fault Injection in Android Services, in high-end fintech teams, an automated Chaos Proxy intercepts IPC Binder calls between the main app and vendor hardware daemon services. The proxy randomly injects a 3% rate of dead-object exceptions (`DeadObjectException`) to continuously verify that client retry and recovery state machines are bulletproof.
Finally, with Verifying WorkManager Escalation, ensure tests verify that when a hardware disconnect causes a timeout reversal, the scheduled `ReversalDispatchWorker` is properly registered with WorkManager and ready for eventual background execution.


## How to answer in the interview

- **Why:** callback timing does not equal issuer truth.
- **How:** script timeout, late approval, duplicate callback, and disconnect around one attempt.
- **Trade-off:** fakes make deterministic tests but cannot prove firmware behavior.
- **Failure case:** cancellation hides an already approved payment.
- **Production solution:** device matrix, crash/restart drills, and provider reconciliation tests.

## Deep-dive talking points

Prompt for fake clock/callback order, persisted-state assertions, cancellation distinction and hardware matrix.

## Follow-up questions

- **Interviewer:** "How does Kotlin's `runTest` accelerate timeout testing in CI pipelines?"
  **Answer:** "It uses virtual time skipping (`advanceTimeBy`), testing a 30-second hardware timeout in a few milliseconds without real-world thread sleep."

- **Interviewer:** "What Android OS exception occurs when an external hardware service process crashes during an IPC call?"
  **Answer:** "`android.os.DeadObjectException`, which the client must catch and handle by restarting the connection."

## Self-check rubric

Can I propose a failure matrix that checks financial state, not just UI exceptions?

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test layers and device tests.
- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cancellation semantics.

Technically reviewed against primary documentation on 2026-10-13.
