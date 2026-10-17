---
id: "PAT-12"
question: "How would Facade simplify an unreliable third-party SDK?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 203
editorial_status: "reviewed"
---

# PAT-12

## Original interview question

How would Facade simplify an unreliable third-party SDK?

## What the interviewer evaluates

Design a facade that normalizes an unreliable SDK without hiding errors or durability needs.

## Concept and technical explanation

The Facade pattern is a structural design pattern that provides a clean, unified, and simplified high-level interface over a complex, disparate, or unreliable subsystem. In enterprise Android engineering, a Facade acts as an essential Anti-Corruption Layer (ACL) positioned between fragile vendor SDKs and clean application domain logic. It encapsulates convoluted configuration lifecycles, converts unpredictable vendor threading models and legacy callback listeners into structured Kotlin Coroutines and Results, centralizes error handling, retry policies, and fallback mechanisms, and prevents leaky third-party vendor dependencies from polluting core architecture layers.

## Practical walkthrough (English)

Encapsulating an unreliable vendor SDK behind a resilient Facade:
```kotlin
// Domain Model & Interface (Pure Kotlin, zero vendor types)
data class UserIdentity(val id: String, val verificationToken: String)
interface IdentityVerificationService {
    suspend fun verifyIdentity(documentImage: ByteArray): Result<UserIdentity>
}

// Resilient Facade wrapping messy vendor SDK
class VendorIdentityFacade @Inject constructor(
    private val vendorSdk: FlakyThirdPartyIdentitySdk,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : IdentityVerificationService {

    override suspend fun verifyIdentity(documentImage: ByteArray): Result<UserIdentity> = withContext(ioDispatcher) {
        suspendCancellableCoroutine { continuation ->
            try {
                vendorSdk.initializeEngine("KEY_123") // Hide noisy multi-step setup
                vendorSdk.startScan(documentImage, object : FlakyVendorCallback {
                    override fun onSuccess(vendorPayload: VendorPayloadBundle) {
                        // Translate vendor-specific types into clean domain model
                        val identity = UserIdentity(vendorPayload.subId, vendorPayload.rawToken)
                        continuation.resume(Result.success(identity))
                    }
                    override fun onError(code: Int, msg: String?) {
                        // Absorb vendor error codes into domain exceptions
                        continuation.resume(Result.failure(DomainVerificationException(code, msg)))
                    }
                })
            } catch (t: Throwable) {
                continuation.resume(Result.failure(t))
            }
            continuation.invokeOnCancellation { vendorSdk.abortCurrentScan() }
        }
    }
}
```

## Explanation in Arabic

كيف يبسط نمط الواجهة (Facade Pattern) التعامل مع مكتبة خارجية غير موثوقة أو فوضوية (Unreliable Third-Party SDK)؟

1. مشكلة التعامل المباشر مع مكتبات الـ Third-Party الفوضوية:
   - مكتبات الدفع، الخرائط، البلوتوث، أو الإعلانات الخارجية غالباً ما تكون سيئة التصميم:
     * تفرض كوداً طويلاً ومعقداً لبدء اتصال بسيط.
     * ترمي استثناءات غير متوقعة، أو تحتوي على Listeners غريبة.
     * إذا قمت باستدعائها في كل مكان في شاشات التطبيق، تصبح رهينة لهذه المكتبة، وتغييرها أو تحديثها مستقبلاً يتطلب تعديل عشرات الشاشات!

2. كيف يحل الـ Facade Pattern هذه الكارثة؟
   - نقوم ببناء كلاس وسيط يسمى **Facade** (مثل `BiometricAuthFacade` أو `MapsLocationFacade`).
   - **يخفي كل التعقيد والقذارة بداخل كود واحد محصور**:
     * يبتلع الاستثناءات العشوائية ويحولها إلى Results آمنة.
     * ينسق الخطوات الخمسة المعقدة للـ SDK ويختصرها في دالة واحدة معلقة: `suspend fun authenticate(): Boolean`.
   - تصبح شاشات التطبيق نظيفة وتتعامل مع الـ Facade فقط. إذا قررت الشركة غداً استبدال الـ SDK بمكتبة أخرى، فالتعديل ينحصر داخل الـ Facade فقط دون المساس بأي شاشة في التطبيق!

## Practical walkthrough

بناء Facade لتبسيط SDK بصمة فوضوي ومعقد:
```kotlin
// كلاس Facade يعزل مكتبة البصمة الفوضوية خلف واجهة نظيفة معلقة:
class BiometricAuthFacade @Inject constructor(
    @ApplicationContext private val context: Context
) {
    suspend fun authenticateUser(title: String, subtitle: String): BiometricResult = suspendCancellableCoroutine { continuation ->
        try {
            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle(title)
                .setSubtitle(subtitle)
                .setNegativeButtonText("Cancel")
                .build()

            // إخفاء كل تعقيد الـ Callbacks والـ Executors داخل الـ Facade:
            val callback = object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    continuation.resume(BiometricResult.Success)
                }
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    continuation.resume(BiometricResult.Error(errString.toString()))
                }
            }
            // تنفيذ طلب البصمة...
        } catch (e: Exception) {
            continuation.resume(BiometricResult.Error(e.localizedMessage ?: "Biometric failed"))
        }
    }
}
```

## Why it matters and how it works

A facade simplifies a subsystem boundary while presenting stable semantics. For an unreliable vendor SDK, the value is normalization of callbacks, errors and ownership; durable transaction status still requires repository/backend design.

## Worked example

Conceptual API: `PaymentFacade.submit(requestId, amount): SubmitOutcome` returns `Confirmed`, `Rejected`, or `PendingVerification`; `observeStatus(requestId)` exposes backend-confirmed updates. Internal adapter handles duplicate callbacks and SDK exceptions; caller sees no vendor types.

## Trade-offs and decision criteria

A facade reduces caller complexity but can become a God Object if it owns UI navigation, server secrets, analytics and every provider. Keep domain policy and UI state outside; use separate adapters for each SDK.

## Failure modes

SDK invokes success callback twice; facade emits two navigation events and user sees duplicate confirmation. Make callback completion idempotent locally, but still reconcile server state. Timeout must not be mapped to final rejection without evidence.

## Production perspective

A fintech app wraps a flaky provider SDK, persists request IDs, and monitors callback anomalies. Backend status is authoritative; facade reports safe error codes and telemetry omits card data.

## Interview answer — short

A Facade encapsulates an unreliable third-party SDK behind a simplified, resilient domain interface. It acts as an Anti-Corruption Layer that shields the application from messy multi-step configurations, converts unruly callbacks into modern Kotlin suspending functions, translates vendor exceptions into safe Result types, and centralizes retry and fallback policies. If the vendor SDK is later swapped or upgraded, application domain logic remains entirely untouched.

## Interview answer — structured

Wrapping an unreliable vendor SDK behind a Facade solves critical architectural vulnerabilities regarding stability, maintainability, and clean boundaries.
Third-party vendor SDKs are notorious for leaky abstractions: they often mandate complex static initialization sequences, throw undocumented runtime exceptions, execute callbacks on arbitrary background threads, and force the app to import vendor-specific data structures across multiple layers. If ViewModels or UseCases interact directly with such an SDK, vendor bugs and breaking API changes ripple throughout the entire codebase.
A Facade establishes an architectural boundary known in Domain-Driven Design as an Anti-Corruption Layer. The Facade exposes a concise, application-owned interface that satisfies exactly what the domain needs, hiding internal SDK complexity.
Internally, the Facade handles defensive engineering: it converts callback spaghetti into suspending coroutines using suspendCancellableCoroutine, wraps network calls in defensive try-catch blocks to catch undocumented runtime crashes, injects retry logic or circuit breakers for unreliable endpoints, and maps foreign data types into clean domain entities.
This structural isolation guarantees that the host application remains stable, unit-testable using mock facades, and completely decoupled from external vendor lifecycles.

## Interview answer — deep senior

Under the hood, a Facade for a third-party SDK manages thread synchronization, cancellation propagation, and process-level crash containment.
Many legacy vendor libraries spawn uncontrolled background threads or retain Activity references, causing memory leaks and uncatchable background exceptions. Within the Facade, senior engineers wrap vendor invocations inside structured Coroutine scopes, leveraging invokeOnCancellation to signal the vendor SDK to abort ongoing operations and release camera, location, or biometric hardware resources immediately when a ViewModel scope cancels.
Furthermore, the Facade provides a strategic seam for fallback orchestration and dynamic feature flagging. If a remote analytics or identity verification SDK crashes frequently or exceeds latency Service Level Objectives (SLOs), the Facade can evaluate Remote Config flags or local circuit breaker state machines to transparently degrade gracefully, routing requests to a secondary fallback provider or returning a cached offline result without client code ever realizing an outage occurred.
From a modularization perspective, the vendor SDK dependency should be restricted to a private :infrastructure:vendor-name Gradle module using implementation dependencies. The rest of the application depends strictly on the domain interface. This compilation boundary cuts build times and ensures that if the vendor releases a breaking update or must be completely decommissioned, only the isolated Facade module requires modification.

## How to answer in the interview

- **Why:** Shield callers from SDK quirks without hiding meaningful outcomes.
- **How:** Facade exposes submit/status; adapter maps vendor callbacks to domain result.
- **Trade-off:** Keep uncertain state and cancellation limits visible.
- **Failure case:** Timeout mapped to failure and duplicate charge on retry.
- **Production solution:** Persist request identity and contract-test late/duplicate callbacks.

## Deep-dive talking points

Define facade operations, callback normalization, cancellation, duplicate callbacks and backend reconciliation.

## Follow-up questions

- **Interviewer:** "What is an Anti-Corruption Layer (ACL) in Domain-Driven Design?"
  **Answer:** "A translation layer (typically implemented as a Facade and Adapter) that sits between your clean domain model and a messy external system, preventing foreign concepts from polluting your code."

- **Interviewer:** "How does `suspendCancellableCoroutine` help in a Facade?"
  **Answer:** "It bridges asynchronous callback-based third-party SDK APIs into modern Kotlin suspending functions, supporting cooperative cancellation if the calling coroutine scope cancels."

## Self-check rubric

Model duplicate callback, timeout and cancellation without declaring false payment success.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Facade and Adapter patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository boundary.

Technically reviewed against primary documentation on 2026-10-13.
