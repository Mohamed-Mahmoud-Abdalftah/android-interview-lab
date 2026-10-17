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

## Concept and technical explanation

A feature flag and staged rollout architecture enables continuous integration, trunk-based development, dark launching, A/B experimentation, and emergency operational kill switches without publishing new APKs. Core system components include: strongly typed flag definitions (Boolean, String, JSON, and Multivariant), a multi-tiered evaluation hierarchy (local compile-time defaults, cached server configs, and runtime debug overrides), deterministic percentage hashing using stable client identifiers (such as hashing the user ID combined with the feature key modulo 100), offline caching in Proto DataStore or EncryptedSharedPreferences, and operational kill switches capable of instantly deactivating malfunctioning code paths via high-priority silent pushes or startup configuration polling.

## Practical walkthrough (English)

Implementing a typed feature flag manager with deterministic rollout hashing and kill switches:
```kotlin
// 1. Strongly typed feature flag definitions with default fallbacks
enum class FeatureFlag(val key: String, val defaultValue: Boolean) {
    NEW_CHECKOUT_FLOW("new_checkout_flow_enabled", defaultValue = false),
    BIOMETRIC_AUTH("biometric_auth_v2_enabled", defaultValue = true),
    DARK_MODE_V2("dark_mode_v2_enabled", defaultValue = false)
}

// 2. Feature Flag Manager with deterministic user hashing and local caching
class FeatureFlagManager @Inject constructor(
    private val localConfigStore: SharedPreferences,
    private val sessionManager: SessionManager
) {
    // Kill switches that take immediate precedence
    private val killSwitches = ConcurrentHashMap<String, Boolean>()

    fun isFeatureEnabled(flag: FeatureFlag): Boolean {
        // Priority 1: Emergency Kill Switch
        killSwitches[flag.key]?.let { isKilled ->
            if (isKilled) return false
        }

        // Priority 2: Cached remote configuration
        if (localConfigStore.contains(flag.key)) {
            return localConfigStore.getBoolean(flag.key, flag.defaultValue)
        }

        // Priority 3: Bundled compile-time default
        return flag.defaultValue
    }

    // Deterministic rollout bucket calculation (0-99%) based on stable User ID
    fun isUserInRolloutBucket(flagKey: String, rolloutPercentage: Int): Boolean {
        val userId = sessionManager.getUserId() ?: return false
        val hash = (userId + flagKey).hashCode().absoluteValue % 100
        return hash < rolloutPercentage
    }

    fun applyEmergencyKillSwitch(flagKey: String) {
        killSwitches[flagKey] = true
    }

    fun updateRemoteFlags(flags: Map<String, Boolean>) {
        localConfigStore.edit().apply {
            flags.forEach { (key, value) -> putBoolean(key, value) }
            apply()
        }
    }
}
```

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

We design feature flags using strongly typed definitions evaluated through a multi-tiered provider system. The system evaluates local build-time defaults, cached remote configs, and debug overrides. Staged percentage rollouts use deterministic hashing on user IDs to ensure stable feature assignment. Critical flags support emergency kill switches fetched at startup or via silent push, allowing instant feature deactivation without requiring new app releases.

## Interview answer — structured

A production feature flag architecture separates software deployment from feature release, enabling safe staged rollouts and emergency remediation.
We model all feature flags as strongly typed enums or value classes with compile-time default values to prevent null pointer exceptions if the network is unreachable.
The evaluation engine resolves flags across a tiered hierarchy: developer debug overrides take precedence during testing, followed by cached server-delivered configurations, falling back to bundled hardcoded defaults.
For staged rollouts, we calculate a deterministic hash of the user ID combined with the feature key, mapping the result to a percentile between zero and one hundred.
This guarantees that a user assigned to a ten percent rollout bucket consistently experiences the feature across app restarts and device rotations without requiring persistent server state.
To mitigate production incidents, our architecture includes a remote kill switch mechanism.
By sending a high-priority silent push or polling lightweight config endpoints on startup, we can deactivate a malfunctioning feature globally within seconds, completely isolating production issues without waiting for Play Store review cycles.

## Interview answer — deep senior

At enterprise scale, the primary hazards of feature flagging are technical debt accumulation, stale flag pollution, and subtle race conditions during startup.
If an app evaluates flags dynamically during mid-session flows, a user could see a screen change its layout or business rules while interacting with it, creating severe UI confusion.
We address this by establishing flag evaluation lifecycles: flags are classified as startup-bound, session-bound, or dynamic.
Startup-bound flags, such as new architecture migrations or core database schemas, are evaluated once during Application initialization from cached disk storage (such as Proto DataStore) and frozen for the remainder of the process.
Session-bound flags are refreshed upon cold startup or user login and held immutable throughout the active user session.
Furthermore, stale flags represent dead code paths that complicate unit tests and bloat bytecode.
We enforce automated flag governance: every feature flag definition in code includes an expiration date and owner metadata.
If a flag remains in the codebase beyond its target deprecation date, our CI lint check fails the build, prompting engineers to clean up the code branch and remove obsolete conditions.
Finally, we integrate flag evaluation events directly into our analytics pipeline, tagging every crash report and business event with the active variant bucket to ensure statistically sound A/B experimentation without client attribution bias.
This disciplined approach guarantees operational agility without sacrificing codebase maintainability.

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
