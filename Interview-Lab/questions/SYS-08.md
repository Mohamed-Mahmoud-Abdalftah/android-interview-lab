---
id: "SYS-08"
question: "Design a feature flags and staged rollout system."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 337
editorial_status: "reviewed"
---

# SYS-08

## Original interview question

Design a feature flags and staged rollout system.

## What the interviewer evaluates

Design feature flags and staged rollout with typed defaults, kill switches and server trust.

## Explanation in Arabic

كيف تصمم نظام Feature Flags و Staged Rollout يدعم الطرح التدريجي، الإلغاء الفوري (Kill Switch)، والعمل Offline؟

1. أهداف نظام الـ Feature Flags في تطبيقات الموبايل:
   - **فصل النشر عن الإطلاق (Decouple Deployment from Release)**: دمج الكود الجديد باستمرار في الفرع الرئيسي ونشره في الـ APK وهو معطل، ثم تفعيله بضغطة زر من لوحة التحكم.
   - **الإطلاق التدريجي (Staged Rollout & Percentage Targeting)**: تفعيل الميزة لـ 5% من المستخدمين، ثم 25%، ثم 100% مع مراقبة تقارير الأعطال (Crashes) ومعدل الأداء.
   - **مفتاح الإيقاف الطارئ (Remote Kill Switch)**: تعطيل أي ميزة بها ثغرة أمنية أو خطأ قاتل فوراً في ثوانٍ دون الحاجة لإطلاق تحديث جديد على متجر التطبيقات.

2. المعمارية الهندسية لنظام الـ Flags:
   - **التخزين الهجين (Multi-Layer Flag Evaluation)**:
     * **Default In-App Values (القيم المدمجة في الكود)**: تُستخدم في أول فتحة للتطبيق أو عند غياب الاتصال بالإنترنت.
     * **Disk-Cached Values (DataStore / SharedPreferences)**: تحتفظ بآخر قيم تم جلبها من السيرفر لتعمل بشكل فوري ومستقر عند فتح التطبيق (No UI Blocking).
     * **Remote Sync (Firebase Remote Config / LaunchDarkly)**: جلب القيم الجديدة في الخلفية وتطبيقها في أوقات آمنة.

3. مشكلة التبديل أثناء عمل الواجهة (Mid-Session Flag Changes):
   - **فخ خطير**: تفعيل Flag أثناء استخدام المستخدم للتطبيق، مما يؤدي إلى تغيير شكل الواجهة فجأة أو تعارض في البيانات!
   - **الحل**: تفعيل سياسة **Fetch Now, Activate on Next Launch** أو تثبيت قيم الـ Flags للجلسة الحالية (Session-Bound Flags) لمنع التذبذب.

## Practical walkthrough

تصميم نظام Feature Flags احترافي مع قيم افتراضية وتخزين محلي ومفتاح إلغاء طارئ:
```kotlin
enum class FeatureKey(val defaultValue: Boolean) {
    NEW_CHECKOUT_FLOW(false),
    BIOMETRIC_AUTH(true),
    DYNAMIC_DISCOUNT_BANNER(false)
}

class FeatureFlagManager @Inject constructor(
    private val dataStore: DataStore<Preferences>,
    private val remoteConfigClient: FirebaseRemoteConfig
) {
    // ذاكرة سريعة في الـ RAM لتقييم الـ Flags بشكل متزامن وبدون I/O delay في الـ Composables
    private val activeFlags = ConcurrentHashMap<FeatureKey, Boolean>()

    suspend fun initialize() {
        // 1. تحميل القيم المدمجة الافتراضية أولاً
        FeatureKey.values().forEach { key -> activeFlags[key] = key.defaultValue }

        // 2. تحميل آخر قيم مخزنة محلياً من DataStore
        val cachedPrefs = dataStore.data.first()
        FeatureKey.values().forEach { key ->
            val stored = cachedPrefs[booleanPreferencesKey(key.name)]
            if (stored != null) activeFlags[key] = stored
        }
    }

    fun isEnabled(key: FeatureKey): Boolean = activeFlags[key] ?: key.defaultValue

    suspend fun fetchAndCacheLatest() {
        try {
            // 3. جلب أحدث القيم من السيرفر وحفظها في DataStore للجلسة القادمة (Activate on Next Launch)
            val updated = remoteConfigClient.fetch().await()
            // حفظ التحديثات في القرص بدون كسر الجلسة الحالية
        } catch (e: Exception) {
            // الفشل الشبكي لا يؤثر إطلاقاً على عمل التطبيق
        }
    }
}
```

## Why it matters and how it works

Config fetch can fail or arrive late; choose bootstrap defaults and apply changes at safe state boundaries. A security-sensitive flag should fail closed where appropriate and be enforced server-side. Rollout should have cohort stickiness, audit trail and rapid disable path; stale cached flags need expiry semantics.

## Worked example

Conceptual typed flag contract; transport/storage are app-specific.

```kotlin
data class FlagSnapshot(
    val version: Long,
    val expiresAtEpochMs: Long,
    val newCheckoutUi: Boolean = false,
)
interface FlagRepository {
    suspend fun refresh(): FlagSnapshot
    fun current(): FlagSnapshot
}
// Backend authorization cannot depend on newCheckoutUi.
```

## Trade-offs and decision criteria

Flags reduce release coupling but add combinatorial states and stale-config risk. Remote kill switch is useful only if app can fetch it in time; a backend block is stronger for security-sensitive operations. Remove obsolete flags after rollout.

## Failure modes

A default-on sensitive path can expose users offline before config fetch. A flag that changes payment protocol mid-transaction can corrupt state unless pinned per operation. Cohort drift makes A/B results unreliable. Client flag can be modified on rooted device.

## Production perspective

A checkout feature rolls out to 1%, then 10%, with crash/ANR/payment error guardrails. Backend supports both protocols, operations pin their variant, and a server-side deny switch stops broken charges independent of client cache.

## Interview answer — short

Design feature flags using a tiered evaluation model: bundled in-app defaults for zero-latency fallback, persistent local storage for offline tolerance, and background remote fetching. Apply an activate-on-next-launch policy to prevent mid-session UI inconsistencies, and configure high-priority remote kill switches for emergency mitigations.

## Interview answer — structured

A production feature flag and staged rollout infrastructure separates deployment from release while insulating the app from network latency:

1. **Multi-Layered Flag Evaluation**:
   - **Static Defaults**: Hardcoded compile-time defaults ensure instant fallback if network or disk fails.
   - **Local Disk Cache**: Persistent values stored in DataStore allow instant synchronous evaluation on app cold start without blocking UI rendering.
   - **Remote Provider (Firebase Remote Config / LaunchDarkly)**: Fetches remote updates in the background based on user targeting cohorts and percentage rollouts.

2. **Activate-On-Next-Launch Policy**:
   - Never mutate feature flags dynamically while the user is navigating an active flow. Changing flags mid-session causes jarring UI rebuilds, state fragmentation, or mid-transaction crashes. Fetch updates in the background, cache them locally, and activate on the next application restart.

3. **Emergency Remote Kill Switch**:
   - Reserve a high-priority bypass channel for critical operational kill switches (e.g. disabling a broken payment gateway). Critical kill-switch flags can be observed reactively to terminate broken components immediately.

## Interview answer — deep senior

From an architectural governance and technical debt standpoint, feature flag systems require strict lifecycle management:

1. **Flag Expiration & Technical Debt Cleanup**: Flags that remain in codebases indefinitely create exponential combinatorial testing permutations and dead code paths. Enforce an expiration SLA (e.g., maximum 60 days). Once a feature is rolled out to 100% and proven stable, schedule technical debt tickets to delete the flag checks, retire remote configurations, and inline the permanent implementation.

2. **Consistent Hashing for Percentage Rollouts**: Rollout buckets must be deterministic. Calculate user cohorts using consistent hashing over the `userId` combined with the `flagKey`: `hash(userId + flagKey) % 100 < rolloutPercentage`. This guarantees that an individual user remains in their assigned bucket across app restarts without state drift.

3. **A/B Testing & Metric Correlation**: Correlate feature flag exposure events directly with analytics pipelines. When a user evaluates a flag, emit an exposure log so data platforms can measure business metric lift (conversion, retention, crashes) between control and treatment groups.

## How to answer in the interview

- **Why:** flags are distributed, possibly stale configuration.
- **How:** use typed snapshots, stable cohorts, TTL, and per-operation pinning.
- **Trade-off:** rapid rollout adds policy and version-skew complexity.
- **Failure case:** mid-transaction flag flip or client-only security gate.
- **Production solution:** monitored canary, safe default, server authorization, and rollback owner.

## Deep-dive talking points

Trace offline default, mid-flight change, old app and server-side containment.

## Follow-up questions

- **Interviewer:** "What is the danger of evaluating remote feature flags synchronously during app launch?"
  **Answer:** "If the network is slow or the remote config server experiences downtime, app cold start blocks, leading to user drop-off or Android OS ANR crashes."

- **Interviewer:** "How do you test a feature protected by a feature flag in automated UI tests?"
  **Answer:** "Inject a mock or fake FeatureFlagManager in test configurations that returns deterministic boolean overrides for targeted flags."

## Self-check rubric

Can I define safe default, guardrails, kill path and backend authorization?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — source of truth and state ownership.
- [Android app security](https://developer.android.com/privacy-and-security/security-tips) — client trust limits.

Technically reviewed against primary documentation on 2026-10-13.
