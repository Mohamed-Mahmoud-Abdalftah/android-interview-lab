---
id: "PAT-16"
question: "You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 207
editorial_status: "reviewed"
---

# PAT-16

## Original interview question

You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?

## What the interviewer evaluates

Use adapters and a stable boundary to switch vendor callbacks without leaking vendor types or result semantics.

## Concept and technical explanation

Swapping vendor SDKs with disparate callback architectures requires establishing a strict Anti-Corruption Layer (ACL) using the Adapter and Facade patterns bounded by clean architectural seams. Third-party vendors invariably expose conflicting callback styles, including single-listener interfaces, multi-callback delegates, broadcast intents, or bespoke event dispatchers. By defining an application-owned, domain-level interface and implementing an Adapter that translates vendor-specific event protocols into standard Kotlin Coroutines and asynchronous Flows, the application isolates vendor volatility completely. Placing this adapter inside an independent Gradle compilation module guarantees that switching vendor providers requires changing only the boundary implementation without modifying domain or presentation code.

## Practical walkthrough (English)

Isolating and adapting incompatible vendor SDKs behind an Anti-Corruption Layer:
```kotlin
// 1. DOMAIN BOUNDARY: Application-owned interface (Pure Kotlin, zero vendor types)
interface LocationTracker {
    val locationStream: Flow<GeoCoordinates>
    suspend fun getCurrentLocation(): Result<GeoCoordinates>
}

// 2. ADAPTER FOR VENDOR A (Push-based listener interface)
class VendorALocationAdapter @Inject constructor(
    private val vendorAClient: VendorASdkClient
) : LocationTracker {
    override val locationStream: Flow<GeoCoordinates> = callbackFlow {
        val listener = object : VendorAListener {
            override fun onNewCoord(lat: Double, lng: Double) { trySend(GeoCoordinates(lat, lng)) }
            override fun onFailed(err: String) { close(VendorException(err)) }
        }
        vendorAClient.startTracking(listener)
        awaitClose { vendorAClient.stopTracking() }
    }

    override suspend fun getCurrentLocation(): Result<GeoCoordinates> =
        locationStream.firstOrNull()?.let { Result.success(it) } ?: Result.failure(TimeoutException())
}

// 3. ADAPTER FOR VENDOR B (Delegate-based with distinct callbacks)
class VendorBLocationAdapter @Inject constructor(
    private val vendorBEngine: VendorBEngine
) : LocationTracker {
    override val locationStream: Flow<GeoCoordinates> = callbackFlow {
        val delegate = VendorBDelegate { event ->
            if (event.type == VendorBEvent.GPS_FIX) trySend(GeoCoordinates(event.latitude, event.longitude))
        }
        vendorBEngine.addDelegate(delegate)
        awaitClose { vendorBEngine.removeDelegate(delegate) }
    }

    override suspend fun getCurrentLocation(): Result<GeoCoordinates> = suspendCancellableCoroutine { cont ->
        vendorBEngine.requestSingleUpdate { fix -> cont.resume(Result.success(GeoCoordinates(fix.lat, fix.lng))) }
    }
}
```

## Explanation in Arabic

تبديل مكتبات خارجية (Vendor SDKs) ذات أنظمة استدعاءات (Callbacks) مختلفة: ما هي الأنماط والحدود المعمارية المناسبة؟

1. طبيعة المشكلة عند التعامل مع مكتبات خارجية:
   - شركة ترغب في استبدال مزود التحقق من الهوية (KYC SDK أو OCR Scanner) من Vendor A إلى Vendor B.
   - Vendor A يعتمد على Java Callbacks قديمة مع `onSuccess(String json)` و `onError(int code)`.
   - Vendor B يطلب تشغيل Activity عبر `startActivityForResult` ويعيد كائنات مخصصة معقدة.
   - إذا كانت هذه الـ SDKs مستوردة مباشرة داخل الـ ViewModels أو الـ Composables، فإن استبدال المزود سيتطلب إعادة كتابة التطبيق بالكامل وإعادة اختبار كل الشاشات!

2. الأنماط المعمارية والحدود الواقية (Boundaries):
   - **Anti-Corruption Layer (ACL) / Facade Pattern**: طبقة حماية عازلة تحول مفاهيم وأخطاء الـ Vendor الفوضوية إلى نماذج بيانات نقية خاصة بالنطاق الداخلي للتطبيق (Domain Models).
   - **Adapter Pattern**: محول مخصص لكل Vendor يحول أسلوب الاستدعاء الخاص به (Callbacks أو Intents) إلى `suspend fun` أو `Flow` باستخدام `suspendCancellableCoroutine`.
   - **Domain Interface (Contract)**: واجهة نقية (`IdentityVerificationGateway`) في طبقة الـ Domain لا تحتوي على أي إشارة لأي نوع أو كلاس من الـ SDK الخارجي.
   - **Modularization**: وضع كود الـ SDK داخل Gradle module مستقل، بحيث لا تستطيع موديولات الـ UI والـ Features استيراده حتى عن طريق الخطأ.

## Practical walkthrough

بناء Anti-Corruption Layer و Adapter لعزل استدعاءات الـ Vendor المختلفة وتحويلها إلى واجهة نقية:
```kotlin
// 1. العقد الصافي في طبقة الـ Domain (لا يعلم شيئاً عن أي Vendor):
interface DocumentScanner {
    suspend fun scanPassport(): Result<PassportData>
}

// 2. Adapter لمزود يعتمد على Callbacks قديمة (Legacy Vendor A):
class VendorAScannerAdapter(private val vendorASdk: LegacyVendorASdk) : DocumentScanner {
    override suspend fun scanPassport(): Result<PassportData> = suspendCancellableCoroutine { continuation ->
        val listener = object : VendorAListener {
            override fun onScanCompleted(vendorModel: VendorADocResult) {
                // تحويل الموديل الخاص بالـ Vendor إلى موديل الدومين النظيف:
                val domainModel = PassportData(vendorModel.docNumber, vendorModel.expiryDate)
                continuation.resume(Result.success(domainModel))
            }
            override fun onScanFailed(errorCode: Int, message: String) {
                continuation.resume(Result.failure(VendorScanException(errorCode, message)))
            }
        }
        
        vendorASdk.startScan(listener)
        continuation.invokeOnCancellation { vendorASdk.cancel() }
    }
}

// 3. عند التبديل إلى Vendor B، نكتب فقط Adapter جديد بدون لمس أي ViewModel أو UI:
class VendorBScannerAdapter(private val modernVendorB: VendorBClient) : DocumentScanner {
    override suspend fun scanPassport(): Result<PassportData> {
        return runCatching {
            val result = modernVendorB.capture()
            PassportData(result.passportNo, result.validUntil)
        }
    }
}
```

## Why it matters and how it works

Adapters translate incompatible interfaces; a facade or repository exposes a stable application contract. DI supplies the active vendor. Migration is safe only when behaviors and failure semantics are compared, not just method names.

## Worked example

Conceptual contract: `suspend fun verify(requestId: String): VerificationOutcome`. Vendor A adapter resumes once from callbacks and unregisters on cancellation; Vendor B adapter maps status codes and may query server for uncertain outcomes. Both pass one contract suite.

## Trade-offs and decision criteria

A generic gateway adds indirection but localizes vendor churn. If vendors differ in capabilities, expose optional capabilities explicitly rather than falsifying a single contract. A facade should not become a vendor switch with every SDK detail.

## Failure modes

Vendor A fires success twice after retry; adapter resumes/handles twice and UI navigates twice. Guard callback completion, persist request identity, and let server decide final status. Cancellation of waiting does not necessarily cancel remote work.

## Production perspective

A bank app swaps identity SDKs behind a verification boundary with staged rollout and metrics on error mapping. Tests compare accepted, rejected, timeout and cancellation; no identity data is logged raw.

## Interview answer — short

To swap vendor SDKs with conflicting callbacks cleanly, establish an Anti-Corruption Layer using the Adapter pattern behind an application-owned domain interface. The Adapter bridges mismatched vendor listeners, delegates, and threading models into standardized Kotlin suspending functions and Flow streams via callbackFlow. Isolating the vendor SDK inside its own Gradle module ensures that swapping vendors touches only the adapter implementation, keeping domain and presentation layers completely decoupled.

## Interview answer — structured

Swapping vendor SDKs with completely different callback interfaces requires disciplined architectural boundary design to prevent vendor churn from destabilizing the core codebase.
The primary danger when integrating third-party SDKs is letting foreign types and idiosyncratic callback contracts leak into UseCases, Repositories, and ViewModels. One analytics or location vendor might use a single callback interface with multiple methods, while another uses individual functional delegates, and a third relies on Android BroadcastReceivers. If application code couples to these specific mechanics, migrating from Vendor A to Vendor B requires rewriting hundreds of callsites across the entire application.
The definitive architectural pattern to solve this is the Adapter pattern operating within an Anti-Corruption Layer.
First, the engineering team defines an application-owned domain interface that describes the required capability using pure Kotlin types, such as exposing a Flow of domain locations or suspending functions returning Result.
Second, an Adapter class encapsulates the concrete vendor SDK. The adapter is responsible for structural translation: it maps vendor initialization sequences, registers internal vendor listeners, and routes asynchronous events into standard Kotlin primitives using callbackFlow with awaitClose for streams and suspendCancellableCoroutine for one-shot requests.
Third, the adapter is isolated within a dedicated Gradle module, ensuring that dependency injection simply swaps the bound adapter implementation without altering any application logic.

## Interview answer — deep senior

Under the hood, managing asynchronous callback impedance mismatches requires meticulous handling of cancellation, threading, and backpressure translation.
Different vendor SDKs employ radically different threading guarantees: some invoke callbacks on the main UI thread, while others spawn unmanaged background daemon threads. Inside the Adapter, senior engineers normalize threading using flowOn(Dispatchers.IO) or Dispatchers.Default, ensuring that downstream consumers receive predictable execution contexts.
Furthermore, bridging callbacks into Coroutines demands rigorous lifecycle cleanup. When wrapping streaming callbacks inside callbackFlow, the awaitClose block must invoke the vendor's unregistration API. If an unhandled exception or cancellation signal occurs downstream, the Coroutine runtime automatically invokes awaitClose, preventing the vendor SDK from continuing to poll hardware sensors or fire orphaned callbacks.
For one-shot callbacks wrapped via suspendCancellableCoroutine, developers must check continuation.isActive and attach invokeOnCancellation to signal the vendor SDK to abort inflight network requests.
By enforcing this boundary at the Gradle module level using implementation dependencies, the vendor SDK bytecode is physically hidden from other modules, making accidental coupling impossible and allowing seamless provider replacement through a single Hilt @Binds declaration. Moreover, senior engineers implement mock and replay adapters to simulate extreme vendor edge cases, such as simulated satellite signal loss or malformed payload responses, enabling thorough offline automated verification before deploying partner SDKs to production.

## How to answer in the interview

- **Why:** Vendor differences should not rewrite UI/domain behavior.
- **How:** Define outcome contract, adapt each SDK, expose one facade.
- **Trade-off:** Choose suspend one-shot versus Flow stream by callback semantics.
- **Failure case:** Double resume, leaked listener or unknown outcome mapped to failure.
- **Production solution:** Shared adapter contract tests and server status reconciliation.

## Deep-dive talking points

Compare callback semantics, thread, cancellation, duplicates, staged migration and server authority.

## Follow-up questions

- **Interviewer:** "Why should vendor SDKs live in separate Gradle modules?"
  **Answer:** "To enforce architectural boundaries at compile time; feature modules cannot accidentally import vendor classes, making vendor swaps zero-risk for UI code."

- **Interviewer:** "What happens if a vendor callback invokes onSuccess multiple times?"
  **Answer:** "Inside `suspendCancellableCoroutine`, calling `resume` twice throws `IllegalStateException`. The Adapter must guard continuation resumption with an atomic check or use `callbackFlow` if multiple emissions are expected."

## Self-check rubric

Define a common outcome and two vendor adapters; specify four shared contract tests.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Adapter and Facade patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — application data boundary.

Technically reviewed against primary documentation on 2026-10-13.
