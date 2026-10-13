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

To swap vendor SDKs with mismatched callbacks without breaking the app, establish a strict Anti-Corruption Layer (ACL). Define a clean domain interface representing your app's required capability. Implement the Adapter pattern to translate vendor-specific callbacks into standard Kotlin suspending functions or Flows via suspendCancellableCoroutine, keeping all vendor dependencies isolated inside a dedicated module.

## Interview answer — structured

When swapping third-party SDKs, the fatal mistake is allowing vendor-specific types, exceptions, and callback signatures to bleed into ViewModels and UI logic. If Vendor A uses listeners and Vendor B returns intents, changing vendors causes a ripple effect across the entire codebase.

We solve this using three architectural boundaries:
1. **Domain Contract**: We define a clean interface in our domain layer (`DocumentScanner` or `PaymentGateway`) expressing the business need using pure Kotlin types, completely agnostic of any vendor.
2. **Adapter & Anti-Corruption Layer (ACL)**: Each vendor SDK gets an Adapter that implements this domain contract. The adapter bridges the callback mechanism into modern coroutines using `suspendCancellableCoroutine`, handles vendor lifecycle requirements, and maps vendor error codes into typed domain errors.
3. **Physical Module Boundary**: We isolate each vendor SDK in its own Gradle module. The main application module depends on the domain interface, not the vendor SDK, guaranteeing at compile time that no vendor classes can leak into the rest of the application.

## Interview answer — deep senior

When engineering an Anti-Corruption Layer for vendor SDKs in enterprise Android apps, multiple edge cases must be handled beyond simple signature mapping:

1. **Thread Hopping & Synchronization**: Vendor callbacks frequently fire on arbitrary background threads or private SDK loopers. The Adapter is responsible for ensuring continuation resumption occurs on appropriate dispatchers (`Dispatchers.Default` for parsing, or handling Android UI thread constraints).

2. **Cancellation & Resource Cleanup**: If the calling coroutine cancels (e.g. user navigates back while the scanner is running), `suspendCancellableCoroutine.invokeOnCancellation` must instruct the vendor SDK to stop camera hardware, free native memory, or deregister listeners. Otherwise, you leak camera sensors and background threads.

3. **Unified Error Semantics**: Vendor A might return HTTP 400 for expired documents, while Vendor B throws an unhandled `SdkInvalidStateException`. The Adapter catches all vendor exceptions, translating them into a unified sealed class hierarchy (`ScanFailure.DocumentExpired`, `ScanFailure.Timeout`, `ScanFailure.SecurityViolation`). The UI only ever responds to domain errors, remaining 100% resilient when swapping vendors.

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
