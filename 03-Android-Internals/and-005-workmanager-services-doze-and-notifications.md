---
id: AND-005
title: WorkManager, services, Doze and notifications
module: 03-Android-Internals
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-003, AND-004]
learning_outcomes:
  - Diagnose a concrete Android runtime failure from evidence
  - Explain the platform contract in Egyptian Arabic and spoken English
  - Review unsafe code and defend a bounded correction
  - Design JVM and Android tests without overstating evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started
  - https://developer.android.com/develop/background-work/services/fgs
  - https://developer.android.com/training/monitoring-device-state/doze-standby
  - https://developer.android.com/develop/ui/views/notifications/notification-permission
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [AND-Q021, AND-Q022, AND-Q023, AND-Q024, AND-Q025]
---

# AND-005 — WorkManager, services, Doze and notifications

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">Upload بدأ من screen scope فاتقطع بعد الخروج. الفريق نقله foreground service لكل الحالات، فظهر notification مزعج وبدأ يصطدم بقيود البدء من الخلفية. المطلوب اختيار mechanism من durability وurgency وuser visibility.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">In-process coroutine لشغل قصير مربوط بعمر ظاهر. WorkManager لشغل durable deferrable لازم يكمل بعد restart بقيود واضحة. Expedited work للحالات المؤهلة تحت quota. Foreground service لشغل user-visible مستمر بnotification وtype مناسب، مش escape hatch. Doze يؤجل شغل وتوقيتات؛ notification permission تؤثر العرض حسب الإصدار.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">اكتب contract: هل لازم ينجو من process death؟ هل المستخدم شايفه الآن؟ هل له deadline؟ هل retry آمنة؟ بعدها اختار mechanism، خزّن input صغير وstable، واجعل worker idempotent لأن التنفيذ ممكن يتكرر.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>القرار والدليل</th></tr></thead><tbody><tr><td>1</td><td>Upload بدأ من screen scope فاتقطع بعد الخروج. الفريق نقله foreground service لكل الحالات، فظهر notification مزعج وبدأ يصطدم بقيود البدء من الخلفية. المطلوب اختيار mechanism من durability وurgency وuser visibility.</td></tr>
<tr><td>2</td><td>In-process coroutine لشغل قصير مربوط بعمر ظاهر. WorkManager لشغل durable deferrable لازم يكمل بعد restart بقيود واضحة. Expedited work للحالات المؤهلة تحت quota. Foreground service لشغل user-visible مستمر بnotification وtype مناسب، مش escape hatch. Doze يؤجل شغل وتوقيتات؛ notification permission تؤثر العرض حسب الإصدار.</td></tr>
<tr><td>3</td><td>اكتب contract: هل لازم ينجو من process death؟ هل المستخدم شايفه الآن؟ هل له deadline؟ هل retry آمنة؟ بعدها اختار mechanism، خزّن input صغير وstable، واجعل worker idempotent لأن التنفيذ ممكن يتكرر.</td></tr>
<tr><td>4</td><td>متخزنش bytes كبيرة في WorkRequest input؛ خزّن URI/ID آمنة والصلاحية المطلوبة. صنّف retry، حط unique work policy عن قصد، واظهر progress من source of truth.</td></tr></tbody></table>

## كود غلط، ليه غلط، وتصحيحه — Wrong and corrected implementation

```kotlin
fun upload() { appScope.launch { api.upload(file) } } // no durable handoff
```

<p dir="rtl" lang="ar">الكود الغلط بيخلط platform contract مع افتراض محلي، ومفيهوش ownership أو failure policy واضحة. النتيجة ممكن تنجح في happy path وتفشل بعد recreation أو input خارجية أو ضغط production.</p>

```kotlin
fun chooseWorkMechanism(visible: Boolean, durable: Boolean, urgent: Boolean) = when {
    visible -> FOREGROUND_SERVICE
    durable && urgent -> EXPEDITED_WORK
    durable -> DURABLE_WORK
    else -> IN_PROCESS
}
```

## مثال Production حقيقي وبدائل

<p dir="rtl" lang="ar">متخزنش bytes كبيرة في WorkRequest input؛ خزّن URI/ID آمنة والصلاحية المطلوبة. صنّف retry، حط unique work policy عن قصد، واظهر progress من source of truth. قبل rollout حدد metric صحة، وجرّب failure وrecreation، وخلي logging بأقل بيانات ومن غير secrets. اختار أبسط boundary تحقق العقد؛ ما تزودش component أو thread أو persistence من غير سبب.</p>

## Tests and failure cases

- Pure JVM test للعقد أو reducer لما يكون مستقل عن Android.
- Android recreation/lifecycle test لما النتيجة تعتمد على framework owner.
- Negative inputs عند كل exported أو restored boundary.
- Process death, account switch, cancellation, duplicate delivery, and stale completion where relevant.
- Release evidence names the device/API/build and never upgrades a JVM model into device proof.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة مختصرة:</strong> In-process coroutine لشغل قصير مربوط بعمر ظاهر. WorkManager لشغل durable deferrable لازم يكمل بعد restart بقيود واضحة. Expedited work للحالات المؤهلة تحت quota. Foreground service لشغل user-visible مستمر بnotification وtype مناسب، مش escape hatch. Doze يؤجل شغل وتوقيتات؛ notification permission تؤثر العرض حسب الإصدار.</p>

**English, 20 seconds:** “Choose from lifetime and user visibility. Durable deferred upload fits WorkManager; an active user-visible transfer may justify FGS; screen-only work can stay in its owner scope.”

**English, 60–90 seconds:** “Choose from lifetime and user visibility. Durable deferred upload fits WorkManager; an active user-visible transfer may justify FGS; screen-only work can stay in its owner scope. In production I start from the owning component and the platform boundary, then trace recreation, external input, cancellation, and late delivery. I keep small restoration or command data separate from durable business state, validate untrusted boundaries, and choose evidence that can distinguish the competing causes. I test pure policy on the JVM and use an Android integration or device trace for framework behavior.”

## Senior follow-ups

1. **Choose between viewModelScope, WorkManager, expedited work, and a foreground service for an upload.** Choose from lifetime and user visibility. Durable deferred upload fits WorkManager; an active user-visible transfer may justify FGS; screen-only work can stay in its owner scope.
2. **Why is returning Result.retry for every exception dangerous?** Permanent authentication or validation failures will loop and waste battery. Classify transient transport failures, cap attempts, use backoff, and expose terminal state.
3. **What must be true before choosing a foreground service?** The work is ongoing and user-visible, the app is allowed to start it in that context, it declares the correct type, and it posts the required notification promptly.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">جاوب الأسئلة من AND-Q021 إلى AND-Q025 بصوتك قبل فتح الإجابة. الاعتقاد إن happy path أو rotation واحدة تثبت Android lifecycle غلط؛ افصل كل owner وentry point وfailure. راجع المصادر الرسمية المتحققة بتاريخ 2026-10-11.</p>

حل [LAB-025](../Coding-Challenges/LAB-025-work-mechanism-selection.md) ثم راجع الاختبارات.


حلّل [SCN-027](../Real-World-Scenarios/SCN-027-upload-screen-scope.md) من غير ما تقرأ الإصلاح الأول.

**Evidence limit:** Official Android behavior is sourced, but this host has no Android SDK/emulator. Pure policy code is marked separately from device evidence.
