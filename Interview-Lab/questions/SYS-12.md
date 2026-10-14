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

Design a reusable SDK by strictly hiding implementation details behind internal modifiers and clean public interfaces, avoiding leaked transitive dependencies via implementation Gradle scopes, validating binary ABI compatibility in CI with BCV, and supporting graceful zero-friction initialization.

## Interview answer — structured

Architecting a distributed Android SDK requires strict discipline regarding backward compatibility, dependency isolation, and lifecycle consumption.

First, **API Surface Minimization**. Next, expose the smallest viable public API surface. Mark all internal ViewModels, utilities, and models with Kotlin's `internal` visibility modifier.
Hide concrete implementations behind stable interfaces instantiated via companion factory methods. **Preventing Dependency Hell**.
Never leak internal dependencies into client builds. Use Gradle `implementation` instead of `api` for internal networking (Retrofit/OkHttp) or storage libraries. If third-party dependencies are required, consider shading/relocating package namespaces using the Shadow Jar plugin to prevent version collision with host apps.
**Binary Compatibility (ABI) Enforcement**. Follow Semantic Versioning (SemVer). Integrate Jetpack's **Binary Compatibility Validator (BCV)** plugin into CI. Any breaking signature change (changing return types, adding non-default interface methods) alters the public `.dump` file and breaks CI, preventing accidental runtime crashes in consuming apps.
**Non-Intrusive Lifecycle & Initialization**. Finally, avoid heavy blocking work in `Application.onCreate`. Use AndroidX `Initializer` for zero-setup workflows, or provide an explicit `Sdk.initialize(config)` allowing the host app to defer initialization off the critical launch path.


## Interview answer — deep senior

From an enterprise SDK engineering perspective, public libraries must treat the host application as an unpredictable environment.

First, with R8/ProGuard Consumer Rules, bundle optimized `consumer-rules.pro` files within the AAR. This automatically instructs the consuming app's R8 shrinker which public entry points and serialized DTOs must be retained, preventing host builds from stripping necessary SDK reflection classes. Next, with Strict Manifest Merging Hygiene, audit the SDK's `AndroidManifest.xml`. Never declare aggressive permissions (e.g. `ACCESS_FINE_LOCATION`) inside an SDK manifest unless strictly optional, and avoid defining top-level single-instance activities that alter the host app's back stack.
Finally, with Defensive Error Isolation, exceptions inside SDK background routines must be caught and returned through typed error callbacks rather than bubbling unhandled to crash the host app process.


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
