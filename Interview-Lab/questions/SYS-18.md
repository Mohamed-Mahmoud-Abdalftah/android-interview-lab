---
id: "SYS-18"
question: "How do you support version skew between older apps and newer backend contracts?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 347
editorial_status: "reviewed"
---

# SYS-18

## Original interview question

How do you support version skew between older apps and newer backend contracts?

## What the interviewer evaluates

Handle older APKs against newer backend contracts with versioned compatibility.

## Explanation in Arabic

كيف تدير انحراف وتفاوت الإصدارات (Version Skew) بين إصدارات التطبيق القديمة في السوق وتحديثات الـ Backend الجديدة؟

1. حقيقة الـ Version Skew في عالم الموبايل:
   - على الويب: مجرد نشر كود الـ Frontend الجديد يُجبر جميع المستخدمين على استخدام أحدث إصدار عند عمل Refresh.
   - في الموبايل: هناك مستخدمون ما زالوا يستخدمون إصدارات تم تنزيلها قبل 6 أشهر أو سنة كاملة! بعضهم لا يملك مساحة لتحديث التطبيق، وبعضهم ألغى التحديث التلقائي.
   - **القاعدة الهندسية الأولى**: **الـ Backend يجب أن يدعم التوافقية العكسية (Backward Compatibility) لعدة إصدارات سابقة دائماً**.

2. القواعد الذهبية لتطور الـ Backend APIs:
   - **ممنوع حذف أو إعادة تسمية الحقول القديمة**: إذا أردت استبدال حقل `userName` بـ `fullName`، احتفظ بالحقلين معاً في الـ JSON حتى يتم إيقاف الإصدارات القديمة رسمياً.
   - **الحقول الجديدة تكون اختيارية (Optional/Nullable)**: لا تجعل الحقول الجديدة إجبارية حتى لا تفشل الإصدارات القديمة.
   - **نمط القارئ المتسامح (Tolerant Reader Pattern)**: تكوين مكتبات السيريالايزيشن في الموبايل (Moshi / Kotlinx Serialization) لتجاهل الحقول المجهولة (`ignoreUnknownKeys = true`).

3. سياسة التحديث الإجباري والتدريجي (Force Update & Soft Update):
   - إرجاع هيدر في استجابات الـ API مثل `X-Minimum-Supported-Version: 2.4.0`.
   - إذا كان إصدار العميل أقل من الحد الأدنى، يعرض التطبيق شاشة **Force Update** تمنع الاستخدام وتوجه المستخدم لـ Google Play (باستخدام In-App Update API).

## Practical walkthrough

تنفيذ فحص إصدار التطبيق والتعامل مع التحديث الإجباري عبر In-App Updates أو شاشة الحظر:
```kotlin
class AppVersionInterceptor(
    private val currentVersionCode: Long,
    private val onForceUpdateRequired: () -> Unit
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            // 1. إرسال إصدار التطبيق في كل طلب لتتبع الـ Telemetry من جهة السيرفر
            .header("X-App-Version", currentVersionCode.toString())
            .header("X-Platform", "android")
            .build()

        val response = chain.proceed(request)

        // 2. إذا أعاد السيرفر رمز 426 Upgrade Required أو هيدر الحد الأدنى المدعوم:
        val minSupported = response.header("X-Min-Supported-Version")?.toLongOrNull() ?: 0L
        if (response.code == 426 || (minSupported > currentVersionCode)) {
            // تفعيل مسار التحديث الإجباري ومنع العمليات الحساسة
            onForceUpdateRequired()
        }

        return response
    }
}
```

## Why it matters and how it works

Old clients may not know new enum values or required fields; robust parsing and explicit unknown states help. Backend rollout should precede client use of new fields, then remove old behavior only after telemetry confirms migration. Security fixes may require forced upgrade with careful user/data policy.

## Worked example

Conceptual API response parsing strategy; actual serializer configuration is library-specific.

```kotlin
sealed interface ServerMode {
    data object Standard : ServerMode
    data object NewCheckout : ServerMode
    data class Unknown(val wireValue: String) : ServerMode
}
// Preserve unknown values safely; do not assume old APK can execute new protocol.
```

## Trade-offs and decision criteria

Backward compatibility increases backend maintenance cost but avoids breaking offline/slow-updating users. Forced upgrade simplifies support only when justified and may strand users without network or store access. Versioned contracts require deprecation policy.

## Failure modes

A server that changes a field from optional string to required nested object can crash old clients. A new enum value may hit exhaustive `when` parsing. Removing an endpoint before old app usage drops creates widespread 404/401 confusion.

## Production perspective

A bank deploys additive transaction-status fields first, updates Android parser with Unknown handling, stages new UI and tracks old-version traffic. A critical security protocol change uses an explicit supported-version gate and migration/help path.

## Interview answer — short

Support mobile version skew by enforcing strict backward compatibility on backends, using the Tolerant Reader pattern (ignoreUnknownKeys) on clients, appending client version headers to all requests, and managing end-of-life versions gracefully via HTTP 426 and Google Play In-App Updates.

## Interview answer — structured

Managing version skew is a defining challenge of mobile platform engineering, as hundreds of disparate app versions coexist indefinitely in the wild:

1. **Backend Evolution Rules (Additive Only)**:
   - Never remove existing JSON fields or alter data types in active API versions. Schema evolution must be strictly additive.
   - When introducing newer data models, deprecate old fields with graceful sunset schedules (e.g. 12-month deprecation policy) while monitoring active version telemetry.

2. **Tolerant Reader Configuration**:
   - Configure client parsers (Kotlinx Serialization or Moshi) with `ignoreUnknownKeys = true`. When backends introduce new fields for newer releases, older clients parse payloads smoothly without deserialization exceptions.

3. **Version Identification Headers**:
   - Attach semantic client headers (`X-App-Version: 3.2.1`, `X-Build-Number: 450`) to every HTTP request. Backends use these headers for telemetry, routing, and phased contract migrations.

4. **Graduated Update Strategy (Soft vs. Force Update)**:
   - **Soft Update**: For non-breaking improvements, display a dismissible in-app update prompt using Google Play's `AppUpdateManager` (Flexible flow).
   - **Force Update**: For breaking security changes or decommissioned APIs, the server responds with `HTTP 426 Upgrade Required`. The client presents an unskippable full-screen blocker routing the user directly to the Play Store.

## Interview answer — deep senior

From an enterprise API lifecycle perspective, managing version skew requires operational discipline across organizational boundaries:

1. **URL vs. Header API Versioning**: Major architectural contract shifts require formal API versioning (e.g., `/v2/checkout` alongside `/v1/checkout`). Backends maintain adapter translation layers mapping deprecated `/v1` requests to new internal microservice schemas, allowing older apps to function until their active user share drops below target deprecation thresholds (e.g. < 0.2%).

2. **Feature Flags as Contract Gateways**: When shipping client changes that depend on newly deployed backend features, protect client code with feature flags. Deploy the mobile code dormant, verify backend stability across multi-region clusters, and activate the mobile flag remotely only once backend coverage is 100% verified.

3. **Automated Backward Compatibility CI Checks**: Run contract testing in backend CI against historical mobile DTO schemas. If a backend PR removes a field or alters a nullable constraint expected by any app version released within the last year, the backend CI build fails automatically.

## How to answer in the interview

- **Why:** old binaries coexist with new server contracts for months.
- **How:** add fields, tolerate unknown values, negotiate capability, then retire safely.
- **Trade-off:** compatibility layers increase server complexity.
- **Failure case:** old app crashes on new enum or loses pending writes.
- **Production solution:** version matrix, telemetry, explicit upgrade response, and recovery of local work.

## Deep-dive talking points

Draw old/new app by old/new server matrix and a deprecation timeline.

## Follow-up questions

- **Interviewer:** "What is Google Play In-App Update API Flexible vs Immediate flow?"
  **Answer:** "Flexible allows the user to continue using the app while the download occurs in the background; Immediate blocks the UI until the update completes and restarts the app."

- **Interviewer:** "Why should enum values in API models always include an UNKNOWN fallback on the client?"
  **Answer:** "If the backend adds a new enum constant, older clients without an UNKNOWN fallback will crash during JSON deserialization."

## Self-check rubric

Can I support old clients, parse unknowns and plan safe contract removal?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — robust persistent model boundaries.
- [Android modularization guide](https://developer.android.com/topic/modularization) — stable API boundaries.

Technically reviewed against primary documentation on 2026-10-13.
