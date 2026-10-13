---
id: "CIC-14"
question: "How do you use staged rollout, crash-rate gates, and rollback plans?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 433
editorial_status: "reviewed"
---

# CIC-14

## Original interview question

How do you use staged rollout, crash-rate gates, and rollback plans?

## What the interviewer evaluates

- Staged rollout as blast-radius control, not true uninstall rollback.
- Crash/ANR and business metric gates.

## Explanation in Arabic

كيف تدير عملية الإطلاق التدريجي (Staged Rollout)، وبوابات معدل الأعطال (Crash-Rate Gates)، وخطط التراجع (Rollback Plans) في أندرويد؟

1. معضلة التراجع (Rollback) في أندرويد:
   - على عكس خوادم الويب، **لا يمكنك عمل Rollback فوري لإصدار أندرويد قديم** لأن نظام أندرويد يرفض تثبيت نسخة ذات `versionCode` أقل من المثبتة على جهاز المستخدم.
   - بمجرد تثبيت التحديث على هواتف المستخدمين، لا يمكنك سحبه إجبارياً إلا بطرح تحديث جديد تماماً برقم أعلى.

2. استراتيجية الإطلاق التدريجي (Staged Rollout):
   - طرح التطبيق بنسب تصاعدية مدروسة: **1% -> 5% -> 20% -> 50% -> 100%** على مدار عدة أيام.
   - الهدف: حصر نطاق الضرر (Blast Radius) في شريحة ضئيلة من المستخدمين إذا ظهرت كارثة غير متوقعة.

3. بوابات جودة المراقبة (Crash-Rate Gates):
   - مراقبة مؤشرات **Android Vitals** و **Firebase Crashlytics** فور بدء كل مرحلة:
   - **Crash-free users**: يجب ألا يقل عن 99.9%.
   - **User-perceived crash rate**: معيار جوجل في Vitals هو أقل من 1.09% (لتفادي معاقبة التطبيق في محركات بحث المتجر).
   - إذا تجاوز معدل الأعطال النسبة المقبولة، يتم **إيقاف الطرح فوراً (Halt Rollout)**.

4. خطة الاستجابة للكوارث (Disaster Recovery Plan):
   - **الخط الدفاعي الأول (Feature Flags)**: إيقاف الميزة المسببة للكراش سحابياً عبر Firebase Remote Config فوراً، دون الحاجة لتحديث التطبيق.
   - **الخط الدفاعي الثاني (Emergency Hotfix)**: إذا كان الكراش في كود التهيئة (Application.onCreate) ولا تعمل معه الأعلام، يتم عمل Hotfix فوري وزيادة الـ `versionCode` وطرحه للمتجر بنسبة 100%.

## Practical walkthrough

مخطط منطقي لإدارة الطرح التدريجي ومراقبة الـ Crash Rate:
```kotlin
// معالجة الأخطاء الحرجة بالاعتماد على Remote Config كخط دفاع أول:
class FeatureManager(private val remoteConfig: FirebaseRemoteConfig) {
    fun isNewCheckoutFlowEnabled(): Boolean {
        // إذا رصدنا كراشات في الإنتاج، نغير القيمة إلى false في الكونسول
        // فيتم تعطيل الميزة فوراً لجميع المستخدمين خلال دقائق:
        return remoteConfig.getBoolean("enable_new_checkout_flow")
    }
}
```
جدول مراحل الطرح التدريجي القياسي:
| اليوم | النسبة | الشرط للانتقال للمرحلة التالية |
|---|---|---|
| اليوم 1 | 1% | استقرار Vitals و Crash-free > 99.9% لمدة 24 ساعة |
| اليوم 2 | 5% | لا توجد كراشات OOM أو فواتير متكررة |
| اليوم 3 | 20% | فحص استقرار الخوادم الخلفية والـ API latency |
| اليوم 4 | 50% | استمرار المؤشرات الخضراء |
| اليوم 5 | 100% | إطلاق كامل لجميع المستخدمين |

## Why it matters and how it works

Play rollout percentage controls distribution to eligible users. Monitoring must segment by version, device/ABI and cohort and compare against baseline. Server API compatibility and remote flags allow mitigation while app update propagates.

## Worked example

New payment SDK v4 goes to 1% of terminals. Gate expansion on crash-free sessions, authorization success, unknown-to-resolved time and reversal queue age. If one ABI crashes, halt rollout and disable new authorization for that cohort while reconciliation continues.

## Trade-offs and decision criteria

Small cohorts limit exposure but produce noisy statistics and slower detection of rare issues. Aggressive automatic gates need robust baselines and false-positive handling. Human release judgment remains useful for high-risk migrations.

## Failure modes

A team halts rollout and assumes issue is gone, but installed users still crash or hold pending payments. Keep backend mitigation, support path and compatible hotfix. Never disable reversal workers to stop new payments.

## Production perspective

Release runbook defines thresholds, observation windows, owner and escalation. Record artifact/version, decisions and cohort metrics for incident review.

## Interview answer — short

Manage releases via staged rollouts (1% to 100%) to contain blast radius, gating progression behind Android Vitals and Crashlytics metrics (crash-free users > 99.9%). Since Android prohibits downward versionCode rollbacks, mitigate critical incidents by halting rollouts, toggling remote feature flags, or releasing an expedited hotfix with an incremented versionCode.

## Interview answer — structured

A disciplined mobile release rollout framework consists of three operational pillars:

1. **Staged Rollout Cadence**:
   - Releases progress through controlled cohorts: 1% -> 5% -> 20% -> 50% -> 100% over a 4 to 5-day cycle. This limits the blast radius of latent device-specific or OS-version bugs to a fraction of the user base.

2. **Automated Quality Gates & Android Vitals**:
   - Progression between stages requires meeting strict thresholds:
     - Crash-free user rate $\ge 99.9%$.
     - User-perceived crash rate in Android Vitals below Google's 1.09% bad-behavior threshold.
     - ANR rate below 0.47%.
   - If any metric breaches thresholds, the staged rollout is immediately halted in Google Play Console.

3. **Multi-Tiered Rollback Strategy**:
   - Android OS strictly rejects installing an APK with a lower `versionCode` than the active installed build, making client-side rollbacks impossible.
   - **Tier 1 (Instant)**: Kill-switch the faulty code path via server-side Feature Flags (Firebase Remote Config).
   - **Tier 2 (Hotfix)**: If startup crashes prevent remote config fetches, branch a hotfix from the release tag, revert the culprit commit, increment `versionCode`, and expedite a 100% hotfix release.

## Interview answer — deep senior

From an organizational resilience and SRE perspective, release gating requires clear runbooks and automated alerting:

1. **The 'Halting vs. Halved' Rollout Myth**: When you halt a staged rollout in Google Play Console, users who already received the update remain on that buggy version; halting only stops new users from downloading it. Teams must actively support the cohort stuck on the buggy version until the hotfix is published.

2. **In-App Force Updates (Flexible vs. Immediate)**: When a severe zero-day vulnerability or corrupt local database migration occurs, a standard store update is insufficient because users may not update for weeks. Integrating the Google Play In-App Updates API with an `AppUpdateType.IMMEDIATE` flow forces a blocking full-screen update dialog on app launch for broken client versions.

3. **Server-Side API Compatibility**: When rolling out a new app version over 5 days, backend APIs must support both old and new payload schemas simultaneously. Never deploy breaking API changes until the client staged rollout reaches 100% and adoption curves stabilize.

## How to answer in the interview

- **Why:** staging buys detection time.
- **How:** watch technical and business gates by version/device.
- **Trade-off:** release reach versus exposure.
- **Failure case:** crash aggregate hides one ABI failure.
- **Production solution:** halt, contain and ship corrected version.

## Deep-dive talking points

Prompt for cohort segmentation, financial metrics, installed-user limit and mixed-version compatibility.

## Follow-up questions

- **Interviewer:** "Why can't you simply deploy the previous APK version to Google Play if a release fails?"
  **Answer:** "Google Play and the Android OS Package Manager enforce strictly monotonic versionCode increments; downgrading versionCode causes an installation failure on user devices."

- **Interviewer:** "What happens to users who already downloaded a faulty build if you halt a staged rollout?"
  **Answer:** "They remain on the faulty build; halting only prevents new users from downloading it, which is why feature flags or immediate hotfixes are required."

## Self-check rubric

Declare staged rollout percentage, cohort metrics and stop thresholds before release; halt distribution on regression and describe the higher-version fix path for already installed users.

## References and reviewed-on date

- [Android staged releases](https://developer.android.com/studio/publish) — release workflow.
- [Android vitals](https://developer.android.com/topic/performance/vitals) — crash/ANR monitoring.

Technically reviewed against primary documentation on 2026-10-13.
