---
id: AND-003
title: Tasks, intents, PendingIntent and export
module: 03-Android-Internals
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-001]
learning_outcomes:
  - Diagnose a concrete Android runtime failure from evidence
  - Explain the platform contract in Egyptian Arabic and spoken English
  - Review unsafe code and defend a bounded correction
  - Design JVM and Android tests without overstating evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/guide/components/activities/tasks-and-back-stack
  - https://developer.android.com/guide/components/intents-filters
  - https://developer.android.com/privacy-and-security/risks/pending-intent
  - https://developer.android.com/guide/topics/manifest/activity-element
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [AND-Q011, AND-Q012, AND-Q013, AND-Q014, AND-Q015]
---

# AND-003 — Tasks, intents, PendingIntent and export

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">Deep link خارجية بتفتح شاشة payment result مباشرة، وPendingIntent mutable بتسمح لجهة تانية تغير extras. المشكلة هنا مش navigation بس؛ دي trust boundary بتدخل process بتاعتك.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Intent رسالة غير موثوقة لحد ما تثبت العكس. task/back stack تحدد history وتجربة Back، وlaunchMode/flags تغير إعادة استخدام Activity. exported component توسع سطح الهجوم. PendingIntent capability باسم تطبيقك؛ mutability وexplicit target والrequest identity جزء من الأمان.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">Android يحل intent مقابل filters ثم ينشئ أو يعيد route حسب task flags. عند boundary افحص action وscheme وhost وpath والـpayload، وبعدها حوّلها command داخلية typed. ما تعتمدش على UI السابقة إنها عملت validation.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>القرار والدليل</th></tr></thead><tbody><tr><td>1</td><td>Deep link خارجية بتفتح شاشة payment result مباشرة، وPendingIntent mutable بتسمح لجهة تانية تغير extras. المشكلة هنا مش navigation بس؛ دي trust boundary بتدخل process بتاعتك.</td></tr>
<tr><td>2</td><td>Intent رسالة غير موثوقة لحد ما تثبت العكس. task/back stack تحدد history وتجربة Back، وlaunchMode/flags تغير إعادة استخدام Activity. exported component توسع سطح الهجوم. PendingIntent capability باسم تطبيقك؛ mutability وexplicit target والrequest identity جزء من الأمان.</td></tr>
<tr><td>3</td><td>Android يحل intent مقابل filters ثم ينشئ أو يعيد route حسب task flags. عند boundary افحص action وscheme وhost وpath والـpayload، وبعدها حوّلها command داخلية typed. ما تعتمدش على UI السابقة إنها عملت validation.</td></tr>
<tr><td>4</td><td>خلّي components غير exported افتراضيًا، واستخدم explicit intents داخل التطبيق. لو boundary لازم exported، وثّق caller/authentication وvalidate كل input. اختبر back stack كـuser journey مش flags منفصلة.</td></tr></tbody></table>

## كود غلط، ليه غلط، وتصحيحه — Wrong and corrected implementation

```kotlin
val intent = Intent(Intent.ACTION_VIEW, uri)
startActivity(intent) // untrusted shape and no resolver/error policy
```

<p dir="rtl" lang="ar">الكود الغلط بيخلط platform contract مع افتراض محلي، ومفيهوش ownership أو failure policy واضحة. النتيجة ممكن تنجح في happy path وتفشل بعد recreation أو input خارجية أو ضغط production.</p>

```kotlin
fun acceptsReturnIntent(i: IntentEnvelope) =
    i.action == "academy.PAYMENT_RETURN" && i.scheme == "https" &&
    i.host == "pay.academy.example" && i.immutable
```

## مثال Production حقيقي وبدائل

<p dir="rtl" lang="ar">خلّي components غير exported افتراضيًا، واستخدم explicit intents داخل التطبيق. لو boundary لازم exported، وثّق caller/authentication وvalidate كل input. اختبر back stack كـuser journey مش flags منفصلة. قبل rollout حدد metric صحة، وجرّب failure وrecreation، وخلي logging بأقل بيانات ومن غير secrets. اختار أبسط boundary تحقق العقد؛ ما تزودش component أو thread أو persistence من غير سبب.</p>

## Tests and failure cases

- Pure JVM test للعقد أو reducer لما يكون مستقل عن Android.
- Android recreation/lifecycle test لما النتيجة تعتمد على framework owner.
- Negative inputs عند كل exported أو restored boundary.
- Process death, account switch, cancellation, duplicate delivery, and stale completion where relevant.
- Release evidence names the device/API/build and never upgrades a JVM model into device proof.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة مختصرة:</strong> Intent رسالة غير موثوقة لحد ما تثبت العكس. task/back stack تحدد history وتجربة Back، وlaunchMode/flags تغير إعادة استخدام Activity. exported component توسع سطح الهجوم. PendingIntent capability باسم تطبيقك؛ mutability وexplicit target والrequest identity جزء من الأمان.</p>

**English, 20 seconds:** “Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points.”

**English, 60–90 seconds:** “Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points. In production I start from the owning component and the platform boundary, then trace recreation, external input, cancellation, and late delivery. I keep small restoration or command data separate from durable business state, validate untrusted boundaries, and choose evidence that can distinguish the competing causes. I test pure policy on the JVM and use an Android integration or device trace for framework behavior.”

## Senior follow-ups

1. **Explain why launchMode is not a substitute for modeling navigation state.** Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points.
2. **An exported Activity trusts extras because only your notification creates the Intent. Review this assumption.** Exported boundaries can be invoked externally. Validate action, origin shape, required fields, sizes, and authorization again inside the component.
3. **Choose mutable or immutable PendingIntent for a notification action and explain identity collisions.** Use immutable unless the receiving workflow requires a documented fill-in field. Build stable request identity so two actions do not unexpectedly replace each other.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">جاوب الأسئلة من AND-Q011 إلى AND-Q015 بصوتك قبل فتح الإجابة. الاعتقاد إن happy path أو rotation واحدة تثبت Android lifecycle غلط؛ افصل كل owner وentry point وfailure. راجع المصادر الرسمية المتحققة بتاريخ 2026-10-11.</p>

حل [LAB-024](../Coding-Challenges/LAB-024-task-and-back-stack-semantics.md) ثم راجع الاختبارات.


حلّل [SCN-025](../Real-World-Scenarios/SCN-025-deep-link-payment-result-pen.md) من غير ما تقرأ الإصلاح الأول.

**Evidence limit:** Official Android behavior is sourced, but this host has no Android SDK/emulator. Pure policy code is marked separately from device evidence.
