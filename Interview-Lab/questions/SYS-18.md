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

## Concept and technical explanation

Supporting version skew between legacy installed Android applications and evolving backend contracts is a fundamental requirement of mobile systems architecture. Unlike web browsers where users instantly execute the newest published assets upon refreshing a webpage, mobile clients exist across hundreds of disparate binary versions simultaneously. Some users disable automatic Play Store updates, running client versions that are months or years old. Backend APIs must adhere to additive change policies, strictly forbidding the removal or renaming of response fields, changing JSON property types, or converting optional parameters into required attributes. Mobile JSON serializers like Moshi or Kotlinx Serialization must be configured defensively to ignore unknown keys and provide safe default values for missing fields. When breaking backend redesigns become mandatory, teams introduce versioned URL namespaces, transmit client version headers on every request, and utilize non-dismissible force-update mechanisms to sunset unsupported legacy clients safely.

## Practical walkthrough (English)

Implementing resilient client-side version headers and defensive deserialization:
```kotlin
// 1. OkHttp interceptor transmitting client version telemetry on every outbound request
class ClientVersionInterceptor @Inject constructor(
    @ApplicationContext private val context: Context
) : Interceptor {
    private val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
    private val appVersionCode = PackageInfoCompat.getLongVersionCode(packageInfo)
    private val appVersionName = packageInfo.versionName

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .header("X-App-Version-Code", appVersionCode.toString())
            .header("X-App-Version-Name", appVersionName)
            .header("X-Client-Platform", "android")
            .build()

        val response = chain.proceed(request)

        // Handle HTTP 426 Upgrade Required for retired application binaries
        if (response.code == 426) {
            EventBus.publish(ForceUpdateRequiredEvent)
        }
        return response
    }
}

// 2. Defensive Kotlinx Serialization entity handling missing or newly added backend fields
@Serializable
data class AccountProfileDto(
    @SerialName("user_id") val userId: String,
    @SerialName("display_name") val displayName: String,
    // Additive field with default fallback protecting older clients from null pointer crashes
    @SerialName("membership_tier") val membershipTier: String = "STANDARD",
    // New complex nested object safely modeled as nullable
    @SerialName("loyalty_rewards") val loyaltyRewards: LoyaltyRewardsDto? = null
)
```

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

We handle mobile version skew by enforcing additive backend contract policies and configuring client JSON serializers to ignore unknown fields with safe default fallbacks. We transmit version headers on every HTTP call and implement non-dismissible force-update dialogs for retired binary versions.

## Interview answer — structured

Supporting version skew is vital because mobile users operate across hundreds of legacy app releases that cannot be updated simultaneously.
I enforce an additive contract evolution rule on backend APIs. Server teams must never rename or delete active JSON fields, change data types, or introduce mandatory request parameters without creating a new API version.
On the Android client, we configure JSON serializers like Kotlinx Serialization or Moshi to ignore unrecognized keys and assign safe defaults for new optional fields.
Every outbound HTTP request includes custom headers carrying the app version code, version name, and platform identifier. This allows backend routing layers to track active client distributions and apply version-specific adapters.
When legacy contracts must be deprecated, the backend returns an HTTP 426 Upgrade Required status or a structured force-update envelope.
The mobile app catches this response, halts critical workflows, and displays a non-dismissible dialog directing the user to update the app on the Google Play Store.

## Interview answer — deep senior

From a staff engineering perspective, managing mobile version skew requires robust coordination between backend release cadences, database schemas, and client sunset policies.
A frequent source of production bugs is enum deserialization crashes. When a backend team adds a new enum value to an existing endpoint, older mobile clients crash with serialization exceptions if the serializer attempts to parse an unknown string. We prevent this by avoiding raw enums in network DTOs, opting instead for sealed classes with an unknown fallback or configuring serializers with custom default enum annotators.
When a breaking backend architectural change is unavoidable, we utilize the dual-write and parallel-run pattern. The backend supports both legacy and modern contract schemas simultaneously for an established migration window, such as six months, tracking traffic volume by client version header until legacy adoption falls below an acceptable threshold like zero point five percent.
Furthermore, local database schemas must maintain backward compatibility with cloud contracts. If a database entity expects a non-null string that a legacy app version cached, but a newer backend payload sends null, the repository mapping layer must defensively sanitize the entity before persisting it to SQLite, avoiding database constraint failures.
Finally, we build flexible remote update prompts. Soft updates display a dismissible banner encouraging users to install performance improvements, whereas hard updates block the UI entirely when cryptographic protocols or security tokens become obsolete, ensuring unsupported binaries cannot compromise user accounts.

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
