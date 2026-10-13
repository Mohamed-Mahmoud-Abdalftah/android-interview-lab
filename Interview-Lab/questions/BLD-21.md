---
id: "BLD-21"
question: "How would you safely roll out and then roll back a bad Android release?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 395
editorial_status: "reviewed"
---

# BLD-21

## Original interview question

How would you safely roll out and then roll back a bad Android release?

## What the interviewer evaluates

- Set staged exposure and objective gates before promotion.
- Distinguish halting distribution from downgrading installed users.
- Choose remote mitigation or higher-version fix with provenance.

## Explanation in Arabic

كيف تقوم بطرح تحديث جديد للتطبيق بشكل آمن (Staged Rollout)، وكيف تتراجع عنه (Rollback) فوراً إذا ظهرت مشكلة كارثية؟

1. الطرح التدريجي الآمن (Staged Rollout Strategy):
   - **ممنوع نشر تحديث لـ 100% من المستخدمين مرة واحدة**!
   - استخدم جدول النشر التدريجي في Google Play Console:
     `1% (اليوم 1) -> 5% (اليوم 2) -> 20% (اليوم 3) -> 50% (اليوم 4) -> 100% (اليوم 5)`.
   - أثناء الطرح، راقب **Android Vitals** ومعدل الـ Crash Rate والـ ANRs في Crashlytics. إذا زاد معدل الانهيار عن 0.5%، أوقف الطرح فوراً.

2. الحقيقة الصادمة حول التراجع (The Rollback Reality in Android):
   - **نظام أندرويد لا يدعم التراجع (Downgrade Rollback) للعميل**! لا يمكن للمستخدم تثبيت إصدار قديم (`versionCode 100`) فوق إصدار أحدث (`versionCode 101`)؛ نظام Android OS سيرفض التثبيت لحماية بيانات المستخدم من التلف.

3. كيف تنفذ التراجع عملياً (The Three-Tier Rollback Plan):
   - **1. إيقاف الطرح فوراً (Halt Rollout)**: يمنع وصول التحديث لباقي الـ 95% من المستخدمين.
   - **2. تفعيل مفتاح الإلغاء عن بُعد (Remote Kill Switch / Feature Flag)**: تعطيل الميزة التالفة فورياً عبر Remote Config للمستخدمين الذين قاموا بتنزيل التحديث بالفعل.
   - **3. إطلاق تحديث طارئ (Expedited Hotfix Release)**: بناء إصدار جديد برقم أعلى (`versionCode 102`) يحتوي على كود التراجع (Revert Commit) وطلب مراجعة مستعجلة من Google Play.

## Practical walkthrough

إدارة سيناريو الطوارئ وإيقاف الطرح ونشر التحديث التصحيحي عبر Fastlane / Play Console:
```bash
# 1. إيقاف الطرح التدريجي فوراً عبر Fastlane Supply:
bundle exec fastlane supply halt --track production

# 2. التراجع عن الـ Commit المتسبب في الكارثة في Git:
git revert HEAD --no-edit

# 3. زيادة versionCode وبناء Hotfix جديد برقم أعلى:
# (مثلاً: versionCode 102 أعلى من النسخة المعطوبة 101)
./gradlew :app:bundleRelease

# 4. رفع الـ Hotfix فوراً ونشره بنسبة 100% مع طلب فحص أولوية:
bundle exec fastlane supply --aab app-release.aab --track production --rollout 1.0
```

## Why it matters and how it works

Staged rollout limits initial exposure and provides telemetry before wider distribution. Halting stops additional delivery under Play controls but does not reverse an already installed binary. Android update ordering by versionCode prevents a lower-code APK from normally replacing a higher one. Server-side flags may disable a risky path rapidly, while critical binary bugs need a signed higher-code release.

## Worked example

Release 431 reaches 5% and increases checkout unknown outcomes. The release owner halts staged rollout, turns off a new optional checkout UI behind a pretested flag, and reconciles pending orders server-side. Engineers retrace crashes with 431 mapping, prepare 432 from pinned toolchain with a regression test, validate internal track, then stage 432 while monitoring payment success and duplicates. Users already on 431 receive an update rather than an attempted downgrade.

## Trade-offs and decision criteria

Slow rollout reduces blast radius but delays delivery; thresholds need sample size and segment checks. A kill switch is fast but only works for behavior designed to be remotely disabled and must not bypass security. A hotfix is slower yet necessary for crashes or migrations. A fully rolled-out halt can change what Play offers to eligible users, but installed users still need a safe path forward.

## Failure modes

Team uses only aggregate crash rate and misses one ABI or country. Rollout expands before enough sessions accrue. A feature flag disables UI but leaves backend writes unsafe. Database migration is irreversible and previous binary cannot read new schema. The team assumes stopping Play rollout uninstalls a bad version.

## Production perspective

Define release gates, on-call owner and halt playbook before launch. Track metrics by version/device/ABI/region, retain mapping and artifact hash, rehearse remote mitigations, and design schema changes for forward compatibility and recovery.

## Interview answer — short

Roll out safely using Google Play Staged Rollouts (1% -> 5% -> 20% -> 100%) while monitoring Android Vitals. Because Android package manager strictly forbids downgrading versionCode, rollback requires halting the rollout, toggling remote feature flag kill switches, and immediately publishing a hotfix with an incremented versionCode.

## Interview answer — structured

Safely rolling out and rolling back Android releases requires understanding app store release mechanics and OS installation invariants:

1. **Staged Rollout Cadence**:
   - Never release directly to 100% of production. Follow a phased rollout schedule: 1% -> 5% -> 20% -> 50% -> 100% across 5–7 days.
   - Continuously monitor Google Play Android Vitals and Crashlytics dashboards. If the crash-free user rate drops below 99.5% or ANR rate exceeds 0.47%, halt the rollout immediately.

2. **The Android Downgrade Invariant**:
   - The Android OS package manager rejects installing an APK with a lower `versionCode` than the currently installed version (`INSTALL_FAILED_VERSION_DOWNGRADE`). You cannot 'unpublish' a bad release to force users back to an older version.

3. **Incident Containment Protocol**:
   - **Halt Rollout**: Stop the rollout in Google Play Console, preventing the remaining percentage from downloading the defective build.
   - **Remote Kill Switch**: Toggle the offending feature flag off remotely via LaunchDarkly/Firebase to remediate users who already updated.
   - **Emergency Expedited Hotfix**: Revert the bad commit in Git, increment the `versionCode` (e.g. from 201 to 202), build a fresh AAB, and release it directly to 100%.

## Interview answer — deep senior

From an operational release management perspective, incident containment requires post-deployment safeguards:

1. **Google Play Expedited Review Request**: When publishing an emergency hotfix resolving a catastrophic production crash or security regression, submit an expedited review request via the Play Console help portal, reducing review turnaround to under 2 hours.

2. **In-App Immediate Update Enforcement**: When the hotfix is approved, flag the previous broken version in your backend config. When users on the broken version launch the app, trigger Google Play's **Immediate In-App Update** flow (`AppUpdateType.IMMEDIATE`). This full-screen modal forces users to download the hotfix before accessing the app.

3. **Blameless Post-Mortem & CI Hardening**: After incident resolution, conduct a post-mortem to determine why testing missed the defect. Implement automated regression tests and pre-release canary tracks to prevent identical failures.

## How to answer in the interview

- **Why:** bad release can persist on devices.
- **How:** stage with metrics and containment plan.
- **Trade-off:** speed versus exposure.
- **Failure case:** assuming halt downgrades users.
- **Production solution:** fixed higher-version build and data-safe recovery.

## Deep-dive talking points

Discuss gates and sample size, staged halt, installed-user reality, kill switch limits, higher-code fix and migration safety.

## Follow-up questions

- **Interviewer:** "Can an Android user downgrade an app to an older version without losing data?"
  **Answer:** "No; the OS forbids downgrading; the only way to install an older version is to uninstall the current app first, which deletes all local data."

- **Interviewer:** "What is the Google Play badging threshold for Android Vitals crash rate?"
  **Answer:** "Google Play enforces a bad behavior threshold of 1.09% overall crash rate and 0.47% ANR rate; exceeding these hurts store ranking."

## Self-check rubric

Set rollout gates, respond to a failed cohort, distinguish halt from installed-user recovery, and protect data migrations.

## References and reviewed-on date

- [Staged rollouts in Play Console](https://support.google.com/googleplay/android-developer/answer/6346149) — staged halt controls.
- [Halting a fully rolled-out release](https://support.google.com/googleplay/android-developer/answer/16285429) — current Play behavior.
- [Version your app](https://developer.android.com/studio/publish/versioning) — update ordering.

Technically reviewed against primary documentation on 2026-10-13.
