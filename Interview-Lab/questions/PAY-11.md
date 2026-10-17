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

## Concept and technical explanation

Testing asynchronous hardware SDK callback timeouts, physical disconnections, and partial failure modes requires deterministic test doubles, synthetic clock control, and fault-injection pipelines:
- The Physical vs Virtual Testing Dilemma:
  - Waiting for physical hardware to experience a genuine timeout or manually yanking USB cables is non-deterministic, agonizingly slow, and impossible to scale across automated Continuous Integration (CI) build pipelines.
  - Relying exclusively on physical hardware leaves edge cases untested until they fail catastrophically in production retail environments.
- Architectural Testing Strategy:
  1. Unit and State Machine Testing via Fakes (Virtualization):
     - Leverage the Hexagonal `CardReaderPort` abstraction.
     - Implement a `FakeCardReaderPort` that provides test controls: `simulateTimeout()`, `simulateUsbDisconnect()`, `simulateCorruptedTlv()`.
     - Use `kotlinx.coroutines.test.StandardTestDispatcher` and `TestScope` to advance virtual time deterministically (`advanceTimeBy(30_000L)`), verifying that state machines immediately transition to `IN_DOUBT` and enqueue ISO 8583 reversal tasks without waiting 30 physical seconds.
  2. Integration Testing via Fault-Injection Native Proxies:
     - Wrap vendor JNI bindings in an interceptable proxy that injects IOExceptions, drops listener callbacks, or delays responses on local emulator builds.
  3. Hardware-in-the-Loop (HIL) Smoke Testing:
     - A small, dedicated lab test rack running physical Android POS terminals connected to programmable USB relays that physically sever data lines to validate hardware recovery circuits under real firmware conditions.

## Practical walkthrough (English)

Testing hardware callback timeouts deterministically using a Fake Card Reader in Kotlin:
```kotlin
class FakeCardReaderPort : CardReaderPort {
    private val eventFlow = MutableSharedFlow<CardReaderEvent>(replay = 1)
    var delayDurationMs: Long = 0L
    var shouldSimulateDisconnect: Boolean = false

    override fun monitorCardEvents(): Flow<CardReaderEvent> = eventFlow.asSharedFlow()

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult {
        if (shouldSimulateDisconnect) {
            eventFlow.emit(CardReaderEvent.HardwareError(code = -101, message = "USB_DISCONNECTED"))
            throw IOException("Device detached unexpectedly")
        }
        if (delayDurationMs > 0) {
            delay(delayDurationMs) // Controlled via TestDispatcher virtual time
        }
        return TransactionInitResult.Success
    }

    override suspend fun cancelOperation(): Boolean = true
}

// Deterministic Unit Test verifying State Machine behavior on Timeout
class PaymentStateMachineTest {
    private val testDispatcher = StandardTestDispatcher()
    private val testScope = TestScope(testDispatcher)
    private val fakeReader = FakeCardReaderPort()
    private val fakeReversalDao = FakeReversalDao()

    @Test
    fun `when reader times out, transaction transitions to IN_DOUBT and queues reversal`() = testScope.runTest {
        val coordinator = PaymentCoordinator(fakeReader, fakeReversalDao, timeoutMs = 10_000L)
        fakeReader.delayDurationMs = 15_000L // Exceeds threshold

        val job = launch { coordinator.initiateCardPayment(amountCents = 5000L) }

        // Fast-forward virtual time by 11 seconds instantly
        testDispatcher.scheduler.advanceTimeBy(11_000L)

        val transaction = coordinator.getCurrentTransaction()
        assertEquals(TransactionStatus.IN_DOUBT, transaction.status)
        assertTrue(fakeReversalDao.hasPendingReversal(transaction.id))

        job.cancel()
    }
}
```

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

Test SDK timeouts and device disconnections deterministically by utilizing a FakeCardReader implementing the domain port, controlling virtual time via kotlinx-coroutines-test. Inject synthetic disconnects and delays to verify that the state machine enters the in-doubt state and commits a persistent reversal without physical delays, validating on hardware using programmable USB relays.

## Interview answer — structured

Testing hardware SDK callback timeouts and physical disconnections requires a multi-tiered strategy combining deterministic software fakes with automated hardware-in-the-loop validation.
Relying solely on physical POS terminals for timeout testing is slow and unreliable because physical timeouts take tens of seconds and cannot be triggered reliably in CI environments.
Our primary testing tier relies on the CardReaderPort abstraction. We implement a FakeCardReader that allows test cases to trigger simulated hardware disconnections and delayed responses on command.
Using kotlinx-coroutines-test and virtual TestDispatchers, unit tests fast-forward time instantly, proving that when an EMV callback exceeds the timeout threshold, the payment state machine transitions to In-Doubt and enqueues an atomic reversal record in Room.
For the secondary integration tier, we use native test proxies to simulate JNI crashes. Finally, a physical hardware-in-the-loop rack equipped with programmable USB switches cuts connection cables programmatically to verify that recovery workers execute accurately on physical firmware.

## Interview answer — deep senior

From a test engineering, mission-critical fault injection, and hardware-in-the-loop architectural perspective, validating hardware failure modes demands absolute determinism and zero dependency on human manual intervention.
In embedded Android POS systems, edge-case failures like a customer yanking an NFC card during APDU exchange or a loose USB cable disconnecting mid-EMV pinpad authorization represent the primary causes of terminal freezes and un-reconciled transactions. Attempting to test these edge cases manually on physical desks produces non-repeatable results and fails to integrate into automated GitHub Actions or GitLab CI runners.
The senior testing architecture employs a robust three-tier testing pyramid.
At the base tier, we execute lightning-fast deterministic unit tests on local JVMs using FakeCardReaderPort. By leveraging Kotlin coroutine TestScope and StandardTestDispatcher, we simulate an un-responsive vendor SDK that hangs for forty seconds. Virtual clock manipulation via advanceTimeBy fast-forwards through the timeout window in under two milliseconds. The test asserts that the coordinator cleanly cancels the coroutine, logs the hardware timeout event, updates the Room database status to IN_DOUBT, and registers an ISO 8583 0400 reversal record in the persistent queue.
At the integration tier, we inject synthetic faults directly into the JNI bridge using custom dynamic mock libraries, verifying that native SIGSEGV signals and C++ hardware exceptions are caught and mapped to domain exceptions rather than crashing the Android zygote process.
At the apex tier, hardware-in-the-loop test benches utilize programmable USB power relays to electronically sever the hardware data lines while automated Appium or UI Automator scripts drive a real payment swipe. This multi-layered verification framework ensures complete operational resilience before software reaches retail stores.

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
