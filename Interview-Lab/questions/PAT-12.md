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

A Facade encapsulates an unreliable third-party SDK behind a simplified, resilient application-owned API. It converts cumbersome callbacks into suspending coroutines, absorbs unpredictable exceptions into safe Result types, and acts as an anti-corruption layer so swapping the vendor SDK later touches only the Facade.

## Interview answer — structured

Wrapping an unreliable third-party SDK inside a **Facade** acts as an **Anti-Corruption Layer (ACL)**, protecting the core application from external instability and poor vendor API design.

1. **API Simplification**: Third-party SDKs frequently demand multi-step initialization rituals (setting listeners, configuring flags, handling token exchanges). A Facade condenses 10 steps into a single cohesive, high-level suspending method: `suspend fun scanDocument(): DocumentResult`.

2. **Resilience & Error Containment**: Volatile vendor libraries often throw undocumented runtime exceptions or return obscure integer error codes. The Facade catches vendor exceptions, intercepts error codes, and maps them into safe, typed domain results (`Result<T>`), preventing vendor crashes from taking down the app.

3. **Vendor Insulation (Zero Lock-in)**: By consuming only the Facade, feature ViewModels and Use Cases never import vendor package classes (`com.vendor.sdk.*`). If the vendor doubles their pricing or deprecates their library, swapping to a competitor requires rewriting only the internal implementation of the Facade; the rest of the application remains completely untouched.

## Interview answer — deep senior

In modern Android, Facades excel at **converting legacy Callback APIs into Coroutines and Flows**. Vendors often supply outdated Java listener interfaces (`onSuccess`, `onError`). Inside the Facade, we wrap these callbacks using `suspendCancellableCoroutine` or `callbackFlow`, installing proper cancellation cleanup in `awaitClose { ... }`.

Furthermore, a Facade allows injecting **Feature Flags and Fallback Mechanisms**. If the third-party analytics or crash SDK crashes or hangs, the Facade can evaluate an in-memory killswitch, silently bypassing the vendor call and returning a cached fallback without the UI ever knowing a failure occurred.

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
