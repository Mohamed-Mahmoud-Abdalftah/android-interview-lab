---
id: "PAY-09"
question: "How do you isolate a hardware/EMV SDK behind a clean interface?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 479
editorial_status: "reviewed"
---

# PAY-09

## Original interview question

How do you isolate a hardware/EMV SDK behind a clean interface?

## What the interviewer evaluates

- SDK adapter boundary and domain-owned state.
- Callback races, device disconnect and test fakes.

## Explanation in Arabic

كيف تقوم بعزل حزم الـ SDK الخاصة بالعتاد وقراءة البطاقات الذكية (Hardware / EMV SDKs) وراء واجهة برمجية نظيفة وقابلة للاختبار؟

1. طبيعة الـ EMV SDKs التجارية السيئة:
   - حزم الـ SDK الخاصة بماكينات الدفع (مثل Pax, Verifone, Ingenico, Sunmi) غالباً ما تملك أسوأ تصميم برمجي ممكن:
     * تعتمد على كائنات أحادية ثابتة عامة (`TerminalHelper.getInstance()`).
     * تستخدم استدعاءات C/C++ معقدة (JNI) ومصفوفات بايت خام (TLV - Tag Length Value).
     * تستخدم Callbacks قديمة وغير متزامنة وتسبب تسريبات ذاكرة.
     * يستحيل تشغيلها على محاكي أندرويد العادي لعدم وجود هاردوير حقيقي، مما يعطل كتابة الـ Unit Tests.

2. نمط التصميم المعماري للعزل (The Hardware Adapter Pattern):
   - **1. واجهة نظيفة معتمدة على الكوتلن (Domain Interface)**:
     * تعريف `CardReaderManager` تتعامل مع نماذج نظيفة (`CardData`, `ReaderEvent`) وتستخدم Kotlin `Flow` للأحداث المتدفقة.
   - **2. محول العتاد الحقيقي (Concrete Hardware Adapter)**:
     * كلاس `PaxCardReaderAdapter` هو الوحيد الذي يرى الـ SDK، ويقوم بتحويل الـ Callbacks إلى `callbackFlow` مع إدارة آمنة للـ Coroutine Scope وحذف المستمعات عند الإغلاق.
   - **3. قارئ وهمي كامل للاختبارات (FakeCardReaderManager)**:
     * يتيح للمطورين محاكاة تمرير البطاقة، وإدخال الـ PIN، ومحاكاة أعطال العتاد بضغطة زر داخل المحاكي دون الحاجة لماكينة حقيقية.

## Practical walkthrough

كود معماري يوضح عزل الـ EMV SDK وراء Kotlin Flow و Interface نظيف:
```kotlin
// 1. الواجهة العامة في طبقة الـ Domain (نظيفة 100% وخالية من كود العتاد):
sealed interface CardReaderEvent {
    object WaitingForCard : CardReaderEvent
    object CardInserted : CardReaderEvent
    object PinRequired : CardReaderEvent
    data class CardReadSuccess(val cardToken: String, val maskedPan: String) : CardReaderEvent
    data class ReaderError(val errorCode: Int, val message: String) : CardReaderEvent
}

interface CardReaderManager {
    fun startCardInteraction(amountCents: Long): Flow<CardReaderEvent>
    suspend fun cancelInteraction()
}

// 2. المحول الفعلي الذي يعزل الـ SDK الخبيثة باستخدام callbackFlow:
class VendorEmvCardReaderAdapter(private val vendorSdk: ProprietaryVendorSdk) : CardReaderManager {
    override fun startCardInteraction(amountCents: Long): Flow<CardReaderEvent> = callbackFlow {
        val listener = object : ProprietaryEmvListener {
            override fun onCardDetected() { trySend(CardReaderEvent.CardInserted) }
            override fun onPinRequested() { trySend(CardReaderEvent.PinRequired) }
            override fun onEmvComplete(tlvData: ByteArray) {
                val parsedToken = parseTlvToToken(tlvData)
                trySend(CardReaderEvent.CardReadSuccess(parsedToken, "4111****1111"))
                close()
            }
            override fun onError(code: Int, msg: String) {
                trySend(CardReaderEvent.ReaderError(code, msg))
                close()
            }
        }
        vendorSdk.registerListener(listener)
        vendorSdk.startTransaction(amountCents)
        awaitClose { vendorSdk.unregisterListener(listener); vendorSdk.abort() }
    }
    override suspend fun cancelInteraction() { vendorSdk.abort() }
}
```

## Why it matters and how it works

A domain port owns stable operation identity and an explicit outcome type including Unknown. The vendor adapter handles threading, lifecycle, callback ordering and error mapping. The repository persists attempt state before invoking the SDK and reconciles against backend/provider authority after ambiguous events.

## Worked example

Conceptual Kotlin contract: `interface TerminalGateway { suspend fun authorize(id: String, amountMinor: Long): TerminalOutcome; suspend fun status(id: String): TerminalOutcome }` where `TerminalOutcome` includes Approved, Declined and Unknown. The adapter wraps vendor callbacks with cancellation and timeout rules; this signature alone is not a complete EMV implementation.

### Kotlin/Android sketch

```kotlin
sealed interface TerminalOutcome {
    data class Approved(val providerRef: String) : TerminalOutcome
    data class Declined(val code: String) : TerminalOutcome
    data object Unknown : TerminalOutcome
}
interface TerminalGateway {
    suspend fun authorize(operationId: String, amountMinor: Long): TerminalOutcome
    suspend fun status(operationId: String): TerminalOutcome
}
// Vendor adapter implements this port; Unknown covers ambiguous transport loss.
// Cancellation of a callback wait must not be interpreted as issuer decline.
```

## Trade-offs and decision criteria

Abstraction improves testing and vendor replacement but can hide provider-specific capabilities if too generic. Keep a capability model or provider-specific extension for certified functions rather than forcing all SDKs into false equivalence.

## Failure modes

A callback arrives twice or after the UI screen closes. If UI owns it, it may duplicate a charge or lose an approval. Adapter correlates callback ID, repository commits guarded transitions, and backend reconciles unknown results.

## Production perspective

Run contract tests against fake adapter plus hardware test matrix by model, ABI and SDK version. Preserve raw vendor references only in restricted audit storage, never card data in logs. Certification constraints are documented.

## Interview answer — short

Isolate proprietary hardware and EMV SDKs behind an abstract domain interface (CardReaderManager) using the Adapter pattern. Bridge legacy C/JNI callbacks into idiomatic Kotlin Coroutines Flows via callbackFlow, and provide a full-fidelity Fake implementation for unit testing and emulator-based development.

## Interview answer — structured

Proprietary POS hardware and EMV chip-reader SDKs exhibit severe architectural anti-patterns that require strict isolation.

First, **Defects of Commercial Payment SDKs**. Next, vendor SDKs (Pax, Verifone, Sunmi, Ingenico) frequently mandate static singletons, untyped byte arrays (EMV TLV tags), blocking native JNI calls, and undocumented lifecycle memory leaks. Leaking vendor classes into UI or domain modules irreparably couples the application to specific hardware revisions.
**The Hardware Adapter Pattern**. With Pure Domain Abstraction, define a clean `CardReaderManager` interface exposing idiomatic Kotlin sealed interfaces (`CardReaderEvent.WaitingForCard`, `CardReaderEvent.PinRequired`, `CardReaderEvent.Success`).
Reactive Bridge via `callbackFlow is the adapter encapsulates vendor callbacks into a cold Kotlin `Flow`. Using `awaitClose { vendorSdk.abort() }` guarantees hardware teardown and unregisters memory-leaking listeners when the subscriber cancels. **Decoupled Testability via In-Memory Fakes**.
Finally, because proprietary native `.so` binaries fail to link on host JVMs or standard Android x86 emulators, an in-memory `FakeCardReaderManager` is essential. It enables full UI automated testing and CI verification without requiring physical $500 hardware terminals.


## Interview answer — deep senior

From an EMV Level 2 kernel compliance and POS threading perspective, adapter implementation requires systems discipline.

First, with Threading and JNI Isolation, vendor EMV kernels often invoke callbacks directly from arbitrary OS native POS threads. The adapter must sanitize thread contexts, dispatching events onto controlled background coroutine dispatchers (`Dispatchers.IO`) before touching Android framework state. Next, with Hardware Re-Entrancy & Mutexes, most physical EMV readers crash or lock up permanently if `startTransaction` is invoked while a previous card read session is in progress. The adapter must wrap hardware invocations in an internal `Mutex` with timeout protection to prevent concurrent native state collisions.
Finally, with Multi-Vendor Dependency Injection, in white-label POS applications supporting multiple hardware vendors (e.g. Running on both Pax A920 and Sunmi V2s), use Dagger/Hilt qualifier annotations or build flavor bindings to inject the matching adapter dynamically based on device build manufacturer (`Build.MANUFACTURER`).


## How to answer in the interview

- **Why:** SDK callbacks and threading should not leak into checkout logic.
- **How:** define a small port with explicit Unknown and adapt vendor events behind it.
- **Trade-off:** abstraction cannot erase hardware or certification rules.
- **Failure case:** mapping disconnect to decline or losing the original reference.
- **Production solution:** contract tests, real-device validation, and versioned error mapping.

## Deep-dive talking points

Prompt for narrow port, cancellation versus payment cancellation, duplicate callbacks, capability differences and hardware tests.

## Follow-up questions

- **Interviewer:** "Why is `callbackFlow` the ideal Kotlin construct for wrapping hardware SDK callbacks?"
  **Answer:** "Because it converts asynchronous multi-event callbacks into a reactive Flow while ensuring guaranteed hardware cleanup via `awaitClose` upon cancellation."

- **Interviewer:** "How do you run automated UI tests for POS flows without physical payment terminals?"
  **Answer:** "By injecting a `FakeCardReaderManager` that simulates card taps, chip reads, and timeouts programmatically in memory on standard emulators."

## Self-check rubric

Can I design an SDK port without erasing provider-specific constraints or conflating coroutine cancellation with payment cancellation?

## References and reviewed-on date

- [Android app architecture data layer](https://developer.android.com/topic/architecture/data-layer) — repository/data-source boundaries.
- [Kotlin cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cooperative cancellation.

Technically reviewed against primary documentation on 2026-10-13.
