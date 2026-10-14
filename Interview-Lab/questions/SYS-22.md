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

Contain a compromised feature flag by immediately blocking the vulnerable path at the backend API Gateway, toggling the remote flag to FALSE across CDNs, dispatching high-priority silent FCM pushes to force local cache invalidation, revoking impacted sessions server-side, and enforcing peer review rules on flag changes.

## Interview answer — structured

Containing an accidental rollout of a security-sensitive code path requires executing a prioritized, multi-tiered incident response playbook.

First, **Immediate Server-Side Gateway Mitigation (Minutes 0–5)**. Next, never rely on mobile clients to patch themselves. Mobile clients may be offline, backgrounded, or caching stale configs. The immediate containment step is blocking or rate-limiting the vulnerable endpoint at the backend API Gateway / WAF level, rejecting compromised requests with `403 Forbidden`.
**Remote Kill Switch Flip (Minutes 5–10)**. Set the flag value to `false` in the remote configuration provider (LaunchDarkly, Firebase Remote Config). Purge edge CDN caches to ensure subsequent client config fetches retrieve the disabled state.
**High-Priority Silent Invalidation (Minutes 10–20)**. Dispatch high-priority silent FCM push messages to active mobile clients. The client's background service immediately clears in-memory flag caches, rewrites persistent storage, and terminates compromised views.
**Session Invalidation & Audit**. Finally, if the flaw exposed unauthorized privilege escalation or data leakage, the backend identifies users who traversed the endpoint, revokes their active refresh tokens, and prompts for credential resets.


## Interview answer — deep senior

From an engineering governance and post-mortem perspective, systemic controls must prevent recurrence.

First, with The Four-Eyes Principle for Sensitive Flags, classify feature flags by risk tier. Operational or UI flags can be flipped by individual engineers; security, auth, and financial flags mandate two-person cryptographic sign-off (Four-Eyes Principle) in release management consoles before propagation. Next, with Default-Deny In-Code Security Assertions, client code protected by feature flags must still adhere to defense-in-depth. If a flag enables a new payment feature, the underlying code must still enforce token validation, biometric challenges, and server nonces. A feature flag should only toggle UI exposure, never disable core cryptographic checks.
Finally, with Canary Phased Ring Deployment, enforce mandatory phased rollout rings: Internal Dogfood (1%) -> Beta (5%) -> General Canary (10%) with automated 24-hour observation windows, preventing accidental 100% blast-radius rollouts.


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
