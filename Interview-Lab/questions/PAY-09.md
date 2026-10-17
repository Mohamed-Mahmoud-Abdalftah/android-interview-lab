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

## Concept and technical explanation

Isolating vendor-specific point-of-sale hardware and EMV chip kernels behind a domain-level abstraction layer protects core business logic from vendor lock-in, lifecycle leaks, and threading chaos:
- The Architectural Hazard of Proprietary SDKs:
  - Hardware vendors (Pax, Ingenico, Verifone, Sunmi) provide proprietary SDKs that rely heavily on native C/C++ libraries via JNI, global singletons, mutable listener callbacks, and raw hardware threads.
  - Directly referencing vendor SDK classes inside ViewModels or Activities creates tight coupling, complicates JVM unit testing, and risks memory leaks if hardware callbacks outlive the UI lifecycle.
- The Hexagonal Ports-and-Adapters Pattern:
  - 1. Domain Port (Interface): A pure Kotlin interface defined in the domain layer (e.g., `interface CardReaderPort`). It exposes business-level inputs and outputs without importing any vendor symbols.
  - 2. Vendor Adapter: An isolated infrastructure module (e.g., `class PaxHardwareAdapter : CardReaderPort`) that translates domain calls into vendor SDK commands and wraps multi-threaded vendor callbacks into idiomatic Kotlin `Flow<ReaderEvent>`.
  - 3. Domain Model Translation: Maps low-level EMV Tag-Length-Value (TLV) hexadecimal strings into type-safe domain entities (`CardData`, `EmvTags`), filtering sensitive parameters at the boundary.
- Concurrency and Lifecycle Isolation:
  - The adapter manages dedicated background dispatchers (`Dispatchers.IO` or a single-threaded hardware executor) to prevent slow chip-card UART/USB operations from blocking the Android Main thread. It scopes hardware operations to a robust application-level lifecycle, ignoring UI teardown.

## Practical walkthrough (English)

Designing a clean hardware abstraction layer for card readers in Kotlin:
```kotlin
// 1. Pure Domain Port: Completely decoupled from vendor SDK symbols
interface CardReaderPort {
    fun monitorCardEvents(): Flow<CardReaderEvent>
    suspend fun startTransaction(amountCents: Long): TransactionInitResult
    suspend fun cancelOperation(): Boolean
}

sealed interface CardReaderEvent {
    data object WaitingForCard : CardReaderEvent
    data class CardInserted(val cardType: String) : CardReaderEvent
    data object ProcessingChip : CardReaderEvent
    data class PinRequested(val remainingAttempts: Int) : CardReaderEvent
    data class CardDataExtracted(val maskedPan: String, val emvTlvData: String) : CardReaderEvent
    data class HardwareError(val code: Int, val message: String) : CardReaderEvent
}

// 2. Vendor-Specific Infrastructure Adapter (e.g., Pax SDK)
class PaxCardReaderAdapter(
    private val paxNativeSdk: PaxDeviceService,
    private val hardwareDispatcher: CoroutineDispatcher = Dispatchers.IO
) : CardReaderPort {

    override fun monitorCardEvents(): Flow<CardReaderEvent> = callbackFlow {
        val listener = object : PaxNativeListener {
            override fun onCardDetected(type: Int) {
                trySend(CardReaderEvent.CardInserted(if (type == 1) "CHIP" else "NFC"))
            }
            override fun onError(code: Int, msg: String) {
                trySend(CardReaderEvent.HardwareError(code, msg))
            }
        }

        paxNativeSdk.registerListener(listener)
        awaitClose { paxNativeSdk.unregisterListener(listener) }
    }.flowOn(hardwareDispatcher)

    override suspend fun startTransaction(amountCents: Long): TransactionInitResult =
        withContext(hardwareDispatcher) {
            val result = paxNativeSdk.startEmv(amountCents)
            if (result.isSuccess) TransactionInitResult.Success else TransactionInitResult.Failure(result.error)
        }

    override suspend fun cancelOperation(): Boolean = withContext(hardwareDispatcher) {
        paxNativeSdk.abort()
    }
}
```

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

Isolate hardware and EMV SDKs using the Hexagonal Ports-and-Adapters pattern. Define a pure Kotlin interface in the domain layer that exposes reactive Flows of reader events, implemented by a vendor-specific adapter module. This confines proprietary JNI libraries, TLV parsing, and background hardware dispatching to the infrastructure layer, enabling instant mock testing and multi-vendor portability.

## Interview answer — structured

Isolating proprietary hardware and EMV SDKs behind a clean architectural interface is vital for maintainability and testability in POS development.
Hardware manufacturers like Pax, Verifone, and Sunmi provide disparate SDKs with idiosyncratic callback interfaces, native C libraries, and distinct error codes. Directly invoking these vendor classes in UI components couples the codebase to specific hardware, prevents automated JVM unit testing, and complicates future hardware migrations.
We resolve this by applying the Hexagonal Ports-and-Adapters pattern. The domain layer defines a clean, technology-agnostic interface, such as CardReaderPort, which models interactions using sealed Kotlin event classes and Flows.
The infrastructure layer houses vendor-specific adapters that encapsulate the proprietary SDK. The adapter executes hardware I/O on a dedicated background dispatcher, translates low-level EMV Tag-Length-Value buffers into domain models, and converts vendor callbacks into structured coroutine streams.
This separation allows engineering teams to swap hardware suppliers without touching business logic and permits comprehensive unit testing using simulated card readers.

## Interview answer — deep senior

From an enterprise POS system architecture and certified payment terminal engineering standpoint, hardware abstraction is a mandatory prerequisite for multi-tenant scalability and hardware lifecycle management.
In commercial payment deployments, an organization frequently runs software across diverse hardware fleets: countertop terminals from Verifone, mobile smart POS devices from Pax, and mPOS Bluetooth dongles from Ingenico. If the application codebase directly imports vendor-specific classes, supporting multiple devices requires cumbersome build flavor branching or messy conditional statements littered throughout the presentation layer.
The senior architectural solution establishes a robust Hardware Abstraction Layer adhering to the Ports and Adapters paradigm. The domain port declares contract methods such as startTransaction, cancelOperation, and a reactive Flow of reader events.
Inside the infrastructure module, the adapter encapsulates the vendor SDK. This adapter handles several critical responsibilities: converting imperative vendor C-style listeners into backpressure-aware reactive callbackFlows, sanitizing raw EMV Tag-Length-Value hexadecimal strings into validated domain models, and managing hardware thread confinement.
Hardware SDKs often spawn unmanaged OS threads that interact with low-level UART serial ports. The adapter forces all hardware communication onto a controlled background thread pool, preventing UI thread starvation.
Furthermore, this architectural boundary dramatically accelerates software velocity. In continuous integration environments, automated test suites execute against a FakeCardReaderPort that simulates card insertions, chip read failures, and PIN timeouts in milliseconds on headless JVMs, guaranteeing high reliability before deploying firmware updates to physical hardware fleets.

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
