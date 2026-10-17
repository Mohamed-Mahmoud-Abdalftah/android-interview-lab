---
id: "SYS-22"
question: "A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 351
editorial_status: "reviewed"
---

# SYS-22

## Original interview question

A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?

## What the interviewer evaluates

Contain accidental activation of broken security-sensitive feature flag.

## Concept and technical explanation

When a remote feature flag inadvertently enables a broken, vulnerable, or security-sensitive execution path in production mobile applications, engineering teams must execute a defense-in-depth containment protocol. Relying solely on client-side flag updates is insufficient because clients may be offline, caching old values, or running behind restrictive firewalls. Rapid containment requires a multi-layered response spanning both client and backend infrastructure. At the edge network, backend API gateways must immediately reject requests originating from the compromised path with HTTP 403 Forbidden or 410 Gone, instantly neutralizing exploitation regardless of client app state. Concurrently, an emergency kill switch is pushed to active mobile clients via high-priority silent Firebase Cloud Messaging (FCM) messages, forcing instant local cache invalidation. Furthermore, if the compromised path exposes user session credentials or authentication state, the mobile client must clear local auth tokens and trigger a forced re-authentication sequence to protect customer data.

## Practical walkthrough (English)

Implementing multi-layered containment with instant remote push revocation and session invalidation:
```kotlin
// 1. Emergency containment push receiver handling instant security revocation
class SecurityRevocationReceiver : FirebaseMessagingService() {
    @Inject lateinit var killSwitchManager: KillSwitchManager
    @Inject lateinit var sessionManager: SessionManager

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val payload = remoteMessage.data
        if (payload["action"] == "SECURITY_CONTAINMENT_REVOKE") {
            val compromisedFlag = payload["flag_key"] ?: return
            val requiresSessionPurge = payload["purge_session"]?.toBoolean() ?: false

            // Step 1: Force-kill the feature flag in local storage and memory
            killSwitchManager.applyEmergencyKill(compromisedFlag, killFeature = true)

            // Step 2: Invalidate sensitive credentials if security path was breached
            if (requiresSessionPurge) {
                sessionManager.clearSessionAndForceLogin()
            }
        }
    }
}

// 2. Client session manager clearing sensitive credentials and navigating to safe login
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val encryptedPrefs: SharedPreferences
) {
    fun clearSessionAndForceLogin() {
        encryptedPrefs.edit().clear().commit() // Synchronous commit to prevent race conditions
        val loginIntent = Intent(context, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        context.startActivity(loginIntent)
    }
}
```

## Explanation in Arabic

مفتاح ميزة (Feature Flag) تم تفعيله بالخطأ ففتح مساراً يحتوي على ثغرة أمنية حرجة. كيف تحتوي الأثر (Contain the Impact) هندسياً وعملياتياً؟

1. خطة الطوارئ لاحتواء الكارثة (Emergency Containment Playbook):
   - **الخطوة 0: الدفاع السيرفري الفوري (Backend & Gateway First)**: لا تنتظر تطبيق الموبايل! أول وأسرع إجراء هو **إغلاق الـ Endpoint المصابة أو فرض قواعد فحص صارمة على مستوى الـ API Gateway / WAF** فوراً. حتى لو كان التطبيق يرسل الطلب المصاب، السيرفر سيرفضه ويعيد `403 Forbidden`.
   - **الخطوة 1: قلب مفتاح الـ Feature Flag عن بُعد (Remote Kill Switch)**: تحويل قيمة الـ Flag إلى `false` في لوحة تحكم الـ Remote Config (Firebase / LaunchDarkly) مع إجبار تفريغ الكاش على الـ CDN.
   - **الخطوة 2: إرسال إشعار تفريغ صامت (Silent Push Invalidation)**: إرسال High-Priority FCM Push لجميع الأجهزة النشطة لإجبارها على تحديث الـ Config فوراً ومسح الـ In-Memory Cache.
   - **الخطوة 3: إبطال الجلسات المخترقة (Session Revocation)**: إذا كانت الثغرة تسمح بتسريب توكنز أو تجاوز صلاحيات، يقوم السيرفر بقطع جميع الجلسات التي مرت عبر هذا المسار وإجبار أصحابها على إعادة تسجيل الدخول.

2. التحقيق الجنائي والوقاية المستقبلية (Post-Mortem & Prevention):
   - إجراء Post-Mortem هندسي بدون لوم (Blameless Post-Mortem).
   - منع تفعيل الـ Flags الحساسة أمنياً بدون موافقة ثنائية (Four-Eyes Principle / Peer Approval) في لوحة التحكم.
   - ربط فحوصات الأمان الآلية في CI لمنع إطلاق أي كود يتجاوز الـ Auth حتى لو تم تفعيل الـ Flag.

## Practical walkthrough

تصميم نظام استجابة طوارئ للـ Feature Flags مع إمكانية الإبطال الفوري عبر Silent Push:
```kotlin
class EmergencyFlagPushReceiver : FirebaseMessagingService() {
    @Inject lateinit var featureFlagManager: FeatureFlagManager
    @Inject lateinit var sessionManager: SessionManager

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // 1. استقبال أمر طوارئ مشفر وموقع من السيرفر
        val action = remoteMessage.data["action"]
        val targetFlag = remoteMessage.data["flag_key"]

        if (action == "EMERGENCY_KILL_FLAG" && targetFlag != null) {
            // 2. إلغاء تفعيل الميزة فوراً في الـ Storage والـ Memory:
            featureFlagManager.forceOverrideFlag(targetFlag, value = false)
            
            // 3. إذا كان المسار يمس أمان الجلسة: مسح التوكنز وتوجيه المستخدم لتسجيل الدخول
            if (remoteMessage.data["revoke_session"] == "true") {
                sessionManager.forceLogoutDueToSecurityIncident()
            }
        }
    }
}
```

## Why it matters and how it works

Incident sequence: server-side deny/kill, client disable, assess exposure and revoke credentials if needed, preserve evidence, notify according to policy, patch and staged re-enable. Use safe default and short TTL for future flags, but never let a flag grant backend privilege. Version skew means older clients need server enforcement.

## Worked example

Conceptual server/client guard, not actual authorization code; backend check is mandatory.

```kotlin
data class FeatureDecision(val enabledForUi: Boolean)
fun mayShowButton(config: FeatureDecision) = config.enabledForUi
// Backend independently authorizes every sensitive request;
// disabling the server route contains offline or modified clients.
```

## Trade-offs and decision criteria

A hard server block minimizes exposure but can interrupt valid in-flight users; provide clear error/Pending handling. Client disable improves UX but propagates slowly. Emergency app release is slower but may be needed for local data leak; choose containment by threat model.

## Failure modes

Only switching remote config to false leaves cached/offline clients on vulnerable path. Deleting logs prematurely loses incident evidence. Rotating credentials without coordinating workers can produce confusing retries. Re-enabling without regression tests repeats incident.

## Production perspective

A fintech team blocks a vulnerable transfer endpoint, halts rollout, identifies affected operation IDs, reconciles ledger, revokes exposed tokens if necessary and ships patched client. Metrics confirm requests are denied server-side before staged re-enable.

## Interview answer — short

We contain a broken security path by blocking incoming requests at the backend API gateway, pushing an emergency kill switch via high-priority silent FCM to invalidate local flag caches, and wiping active session tokens on affected clients to force re-authentication and protect user data.

## Interview answer — structured

Containing an accidental activation of a broken security-sensitive path requires an immediate defense-in-depth containment strategy across client and server.
The primary containment action occurs at the backend gateway. Infrastructure teams deploy an immediate rule rejecting all HTTP calls to the vulnerable endpoints with HTTP 403 Forbidden. This instantly blocks exploitation even if mobile clients continue sending requests with cached flags.
Concurrently on the mobile side, we dispatch high-priority silent FCM data messages to all active installs.
The app receiver catches this command, immediately overrides the flag in memory and disk storage, and routes the user away from the compromised UI.
If the security flaw potentially exposed authentication tokens or user credentials, the containment command triggers an automated session purge, clearing tokens from EncryptedSharedPreferences and navigating the user to a clean login screen.
Finally, we invalidate edge CDN caches and update remote configuration servers to ensure newly launching apps download the safe configuration.

## Interview answer — deep senior

From a staff mobile security perspective, incident response requires automated playbooks that eliminate human delay during production breaches.
Mobile clients cannot be trusted to patch themselves instantly because users may maintain offline app sessions or disable background push services. Therefore, our architectural containment model mandates that the backend is always the authoritative security boundary. When a security-sensitive feature flag is revoked, API gateways immediately block requests, revoke associated OAuth access tokens, and reject refresh attempts until clients present credentials validated under the secure flow.
On the client side, our feature flag manager incorporates a hard-coded security circuit breaker. If the local client detects that a feature flag marked with a security-critical tag is missing its cryptographic server signature or fails payload checksum validation, the manager rejects the flag and defaults to the disabled state.
To ensure silent emergency pushes reach dormant devices, we utilize high-priority data-only FCM messages that invoke a BackgroundBroadcastReceiver without displaying user-facing notifications.
Finally, after containment is verified through real-time traffic drop dashboards, we conduct a forensic blameless post-mortem. We add automated CI verification checks ensuring that feature flags governing security boundaries require two-person cryptographic sign-off before being toggled on remote configuration consoles, eliminating single-operator human error.

## How to answer in the interview

- **Why:** security containment cannot rely on cached client config.
- **How:** stop server effects first, then disable UI and scope affected operations.
- **Trade-off:** deny rule may block legitimate transfers temporarily.
- **Failure case:** only flipping a client flag leaves old APKs exposed.
- **Production solution:** audited incident response, reconciliation, and staged fixed rollout.

## Deep-dive talking points

Trace offline/tampered client, backend deny and in-flight transaction reconciliation.

## Follow-up questions

- **Interviewer:** "Why is backend gateway mitigation prioritized over flipping the client feature flag?"
  **Answer:** "Backend gateway changes take effect globally within seconds, whereas client flag updates depend on network polling, app restarts, and cached local configs."

- **Interviewer:** "What is a Blameless Post-Mortem?"
  **Answer:** "An incident review focused on identifying systemic process and tooling failures rather than punishing individuals, designing safeguards to prevent recurrence."

## Self-check rubric

Can I contain at server, preserve evidence and handle in-flight operations honestly?

## References and reviewed-on date

- [Android security guidance](https://developer.android.com/privacy-and-security/security-tips) — client-side security considerations.
- [Android architecture guide](https://developer.android.com/topic/architecture) — authority boundaries.

Technically reviewed against primary documentation on 2026-10-13.
