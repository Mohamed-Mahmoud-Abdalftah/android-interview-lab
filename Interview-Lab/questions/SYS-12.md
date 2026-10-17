---
id: "SYS-12"
question: "How do you make a reusable Android SDK with a stable public API?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 341
editorial_status: "reviewed"
---

# SYS-12

## Original interview question

How do you make a reusable Android SDK with a stable public API?

## What the interviewer evaluates

Design reusable Android SDK with narrow stable API, lifecycle ownership and compatibility tests.

## Concept and technical explanation

Authoring an enterprise-grade reusable Android SDK requires a fundamentally different engineering mindset than building end-user applications. In an SDK, the consumers are other engineering teams whose app stability, binary size, build speeds, and architectural integrity depend entirely on the library's design. The public API surface must be strictly minimal, exposing only high-level interfaces, immutable configuration models, and explicit callbacks or Flows, while hiding all internal orchestration behind Kotlin internal visibility and package-private constructs. The Kotlin Binary Compatibility Validator (BCV) must be integrated into continuous integration to catch unintended public signature breaks. Furthermore, SDKs must isolate their dependencies, avoiding transitive leakage through Gradle implementation configurations. SDKs must never trigger unhandled runtime exceptions that crash the host application, must publish consumer ProGuard rules that preserve only necessary entry points, and must utilize distinct resource prefixes to prevent resource collisions with host applications.

## Practical walkthrough (English)

Structuring an isolated Android SDK with public interfaces and hidden implementations:
```kotlin
// 1. Minimal, stable public interface exposed to host applications
interface IdentityVerificationSdk {
    fun startVerification(sessionId: String, callback: VerificationCallback)

    companion object {
        // Factory pattern hiding internal class instantiation and lifecycle binding
        fun create(context: Context, configuration: SdkConfiguration): IdentityVerificationSdk {
            return IdentityVerificationSdkImpl(context.applicationContext, configuration)
        }
    }
}

// 2. Immutable public configuration contract
data class SdkConfiguration(
    val apiKey: String,
    val environment: Environment = Environment.PRODUCTION,
    val enableBiometrics: Boolean = true
) {
    enum class Environment { SANDBOX, PRODUCTION }
}

// 3. Callback contract communicating terminal outcomes without throwing exceptions
interface VerificationCallback {
    fun onSuccess(verifiedToken: String)
    fun onFailure(error: SdkError)
}

sealed class SdkError(val code: Int, val message: String) {
    class NetworkFailure(message: String) : SdkError(1001, message)
    class UserCancelled : SdkError(1002, "User aborted verification")
    class InternalError(cause: Throwable) : SdkError(1003, cause.localizedMessage ?: "Unknown error")
}

// 4. Internal implementation hidden from host app autocomplete and classpath
internal class IdentityVerificationSdkImpl(
    private val appContext: Context,
    private val config: SdkConfiguration
) : IdentityVerificationSdk {
    override fun startVerification(sessionId: String, callback: VerificationCallback) {
        // Internal orchestration using hidden network and biometric engines
    }
}
```

## Explanation in Arabic

كيف تصمم مكتبة أندرويد (Reusable Android SDK) بواجهة عامة مستقرة (Stable Public API) ومعايير أمان عالية للتوزيع؟

1. تقليص مساحة السطح العام (Minimizing the Public API Surface):
   - **قاعدة ذهبية**: كل كلاس أو دالة تجعلها `public` تصبح التزاماً للأبد! اجعل كل شيء `internal` أو `private` افتراضياً.
   - **إخفاء كود الـ Implementation**: توفير Interfaces عامة فقط وكلاسات Factory أو Entrypoints محدودة (مثل `PaymentSdk.initialize()`).
   - استخدام أداة **Binary Compatibility Validator (BCV)** في Gradle: تقوم بإنشاء ملف `.dump` بالـ Public API وتفشل الـ Build إذا قام مطور بتغيير أو كسر الـ Binary Compatibility دون زيادة رقم الـ Major Version.

2. منع تسريب التبعيات الخارجية (No Transitive Dependency Leaks):
   - **فخ شائع**: استخدام `api("com.squareup.retrofit2:retrofit:...")` في ملف `build.gradle` الخاص بالـ SDK. هذا يسرب Retrofit لتطبيق العميل ويجبره على استخدام نفس الإصدار مما يسبب Dependency Hell وتعارض في الإصدارات!
   - **الحل**: استخدام `implementation` دائماً للتبعيات الداخلية، وتجنب استخدام كائنات تابعة لمكتبات خارجية في دوال الـ Public API الخاصة بك.

3. التهيئة السلسة (Frictionless Initialization):
   - توفير تهيئة آلية خفيفة عبر AndroidX App Startup (`Initializer<T>`) إذا كان الـ SDK لا يتطلب إعدادات خاصة، مع إتاحة دالة تهيئة يدوية صريحة للتحكم في زمن التشغيل.

## Practical walkthrough

تصميم واجهة عامة احترافية للـ SDK مع عزل التنفيذ الداخلي والتهيئة الآمنة:
```kotlin
// 1. الواجهة العامة المتاحة للمطورين فقط (Public API):
interface PaymentSdk {
    fun startCheckout(amountCents: Long, currency: String, callback: SdkCallback)
    
    companion object {
        fun create(context: Context, apiKey: String): PaymentSdk {
            // إخفاء كلاس التنفيذ الحقيقي تماماً ومنع استدعائه المباشر
            return PaymentSdkInternal(context.applicationContext, apiKey)
        }
    }
}

interface SdkCallback {
    fun onSuccess(transactionId: String)
    fun onError(code: Int, message: String)
}

// 2. الكود الداخلي مغلق تماماً عبر internal لمنع الوصول إليه من خارج موديول الـ SDK:
internal class PaymentSdkInternal(
    private val context: Context,
    private val apiKey: String
) : PaymentSdk {
    // استخدام OkHttp أو Room داخلياً بدون تسريبها لمستخدم الـ SDK
    override fun startCheckout(amountCents: Long, currency: String, callback: SdkCallback) {
        // منطق الدفع الداخلي
    }
}
```

## Why it matters and how it works

Public API changes impose compatibility burden; use interfaces/data types cautiously and keep implementation internal. Avoid global singleton state that crosses users or leaks Context. Lifecycle-sensitive operations should accept an owner or expose suspend/Flow APIs with explicit cancellation. Provide dependency injection or factory configuration without forcing host architecture.

## Worked example

Conceptual Kotlin public contract with closeable client; implementation is hidden and must document callback dispatcher.

```kotlin
interface PaymentsClient : AutoCloseable {
    suspend fun status(operationId: String): PaymentStatus
    fun observe(operationId: String): kotlinx.coroutines.flow.Flow<PaymentStatus>
}
interface PaymentsClientFactory {
    fun create(config: PaymentsConfig): PaymentsClient
}
// Public types/config must remain compatible; backend owns authorization.
```

## Trade-offs and decision criteria

A small API is harder to customize but easier to maintain; exposing many internals creates binary-break and R8 risk. Bundling dependencies can increase app size/conflicts. A stable SDK may need adapter modules for Compose/Views rather than forcing either on all hosts.

## Failure modes

Leaking an Activity Context from a singleton SDK causes memory leaks. Public `inline` functions or data classes can create unexpected binary/source compatibility constraints. Reflection without consumer rules may crash only in release. Embedded API secrets can be extracted.

## Production perspective

A payments SDK publishes core Kotlin API, optional UI adapter, consumer R8 rules and a sample app. CI tests min/max supported versions, release minification, cancellation and malicious input. Operational docs specify backend idempotency and status recovery.

## Interview answer — short

We build reusable Android SDKs by keeping the public API minimal, using Kotlin internal visibility to hide implementation details, and enforcing binary compatibility in CI. We isolate transitive dependencies, ship consumer ProGuard rules, prefix all resources, and catch internal failures to prevent host application crashes.

## Interview answer — structured

Designing a production-grade Android SDK requires isolating the library implementation while providing a bulletproof, minimal public contract.
I enforce strict API surface discipline by declaring internal classes and dependencies as internal, exposing only clean interfaces and immutable configuration objects.
We enforce semantic versioning and integrate the Kotlin Binary Compatibility Validator plugin in continuous integration to catch accidental binary or source incompatibilities before merging.
Dependency isolation is critical. In the build script, dependencies use the implementation configuration rather than api to prevent leaking third-party libraries like Retrofit or OkHttp into the host app classpath.
The SDK must never crash the host application. All internal coroutine scopes catch unexpected errors and surface them through structured error callbacks or sealed result types.
Finally, we ship embedded consumer-proguard-rules.pro files so consumer apps automatically retain necessary SDK interfaces while shrinking internal bytecodes, and we prefix all Android resources with a unique namespace to prevent naming collisions.

## Interview answer — deep senior

From a staff architecture perspective, distributing an Android library requires deep consideration of lifecycle independence, initialization overhead, and binary footprint impact.
Historically, SDKs relied on empty ContentProviders for auto-initialization at app startup. While convenient, this practice slows cold startup across all consumer apps. Modern SDK architecture favors explicit lazy initialization via a builder or App Startup Initializer, allowing host apps to control execution timing and pass necessary application contexts.
Managing transitive dependency conflicts is a major maintenance hazard. If an SDK bundles an opinionated JSON serializer or specific coroutines version, it can cause duplicate class runtime crashes in host apps with mismatched dependencies. We mitigate this by either writing zero-third-party dependency core modules relying solely on pure Kotlin and Android framework primitives, or shading critical internal dependencies using Gradle shadow relocation plugins.
Backward compatibility must be preserved across both source and binary levels. Adding a default parameter in a Kotlin public function breaks binary compatibility for Java callers because the compiled bytecode signature changes. We guard against this by applying JvmOverloads annotations and maintaining golden API dump files in version control.
Lastly, the SDK must establish clean memory boundaries, using ApplicationContext to prevent Activity leaks and providing an explicit teardown method to cancel internal background workers when host applications log out or terminate the flow.

## How to answer in the interview

- **Why:** SDK consumers depend on behavior as well as signatures.
- **How:** define stable inputs, errors, threading, cancellation, lifecycle, and version policy.
- **Trade-off:** narrow API limits flexibility but reduces compatibility cost.
- **Failure case:** reflection breaks only in minified consumer builds.
- **Production solution:** sample apps, ABI tests, consumer rules, and deprecation windows.

## Deep-dive talking points

Trace public ABI, lifecycle, host integration, release shrinker and security authority.

## Follow-up questions

- **Interviewer:** "What is the difference between source compatibility and binary compatibility in Kotlin?"
  **Answer:** "Source compatibility means existing source code recompiles without errors; binary compatibility means already-compiled binaries execute against the new library without NoSuchMethodError."

- **Interviewer:** "What is the purpose of consumer-rules.pro in an Android library module?"
  **Answer:** "It bundles ProGuard/R8 rules into the exported AAR that are automatically applied to any application consuming the library."

## Self-check rubric

Can I specify API/lifecycle contracts, test host release builds and protect backend secrets?

## References and reviewed-on date

- [Android library publishing](https://developer.android.com/build/publish-library) — artifacts and consumers.
- [Android architecture guide](https://developer.android.com/topic/architecture) — ownership boundaries.

Technically reviewed against primary documentation on 2026-10-13.
