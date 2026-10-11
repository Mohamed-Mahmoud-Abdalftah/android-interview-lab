---
id: AND-004
title: Looper, Handler, Binder and ANR evidence
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
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs
  - https://developer.android.com/reference/android/os/Looper
  - https://developer.android.com/reference/android/os/Handler
  - https://source.android.com/docs/core/architecture/aidl/binder-threading
example_paths: []
question_ids: [AND-Q016, AND-Q017, AND-Q018, AND-Q019, AND-Q020]
---

# AND-004 — Looper, Handler, Binder and ANR evidence

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">التطبيق بيظهر ANR في release بس، والفريق شايف network logs في نفس الدقيقة فافترض إن الشبكة السبب. المطلوب تربط trace بالـmain thread والـbinder waits والـlock owner بدل correlation سطحي.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Looper تسحب Messages وRunnables من MessageQueue على thread واحدة. main thread مسؤولة عن input وlifecycle والرسم؛ blocking طويل يمنع الاستجابة. Binder IPC ممكن ينفذ على thread pool، لكن synchronous call من main تفضل توقف main. ANR نوع symptom له timing وcomponent؛ الدليل stack traces وPerfetto وsystem report.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">عند ANR ثبت timestamp وprocess وcomponent. اقرأ main-thread stack: CPU loop، monitor contention، binder call، I/O، ولا انتظار future. اتبع lock أو binder للthread المالكة. قارن traces متعددة؛ top frame واحدة ممكن تكون مكان انتظار مش السبب الأصلي.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>القرار والدليل</th></tr></thead><tbody><tr><td>1</td><td>التطبيق بيظهر ANR في release بس، والفريق شايف network logs في نفس الدقيقة فافترض إن الشبكة السبب. المطلوب تربط trace بالـmain thread والـbinder waits والـlock owner بدل correlation سطحي.</td></tr>
<tr><td>2</td><td>Looper تسحب Messages وRunnables من MessageQueue على thread واحدة. main thread مسؤولة عن input وlifecycle والرسم؛ blocking طويل يمنع الاستجابة. Binder IPC ممكن ينفذ على thread pool، لكن synchronous call من main تفضل توقف main. ANR نوع symptom له timing وcomponent؛ الدليل stack traces وPerfetto وsystem report.</td></tr>
<tr><td>3</td><td>عند ANR ثبت timestamp وprocess وcomponent. اقرأ main-thread stack: CPU loop، monitor contention، binder call، I/O، ولا انتظار future. اتبع lock أو binder للthread المالكة. قارن traces متعددة؛ top frame واحدة ممكن تكون مكان انتظار مش السبب الأصلي.</td></tr>
<tr><td>4</td><td>خلي blocking boundary main-safe، قلّل critical sections، ومتستخدمش async عشوائي يخفي ordering. اجمع evidence من ANR trace وPerfetto وStrictMode في debug، وحدد rollout metric قبل الإصلاح.</td></tr></tbody></table>

## كود غلط، ليه غلط، وتصحيحه — Wrong and corrected implementation

```kotlin
Handler(Looper.getMainLooper()).post {
    val data = blockingSocket.read()
    render(data)
}
```

<p dir="rtl" lang="ar">الكود الغلط بيخلط platform contract مع افتراض محلي، ومفيهوش ownership أو failure policy واضحة. النتيجة ممكن تنجح في happy path وتفشل بعد recreation أو input خارجية أو ضغط production.</p>

```kotlin
scope.launch {
    val data = repository.readMainSafe()
    render(data) // main only for the small UI update
}
```

## مثال Production حقيقي وبدائل

<p dir="rtl" lang="ar">خلي blocking boundary main-safe، قلّل critical sections، ومتستخدمش async عشوائي يخفي ordering. اجمع evidence من ANR trace وPerfetto وStrictMode في debug، وحدد rollout metric قبل الإصلاح. قبل rollout حدد metric صحة، وجرّب failure وrecreation، وخلي logging بأقل بيانات ومن غير secrets. اختار أبسط boundary تحقق العقد؛ ما تزودش component أو thread أو persistence من غير سبب.</p>

## Tests and failure cases

- Pure JVM test للعقد أو reducer لما يكون مستقل عن Android.
- Android recreation/lifecycle test لما النتيجة تعتمد على framework owner.
- Negative inputs عند كل exported أو restored boundary.
- Process death, account switch, cancellation, duplicate delivery, and stale completion where relevant.
- Release evidence names the device/API/build and never upgrades a JVM model into device proof.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة مختصرة:</strong> Looper تسحب Messages وRunnables من MessageQueue على thread واحدة. main thread مسؤولة عن input وlifecycle والرسم؛ blocking طويل يمنع الاستجابة. Binder IPC ممكن ينفذ على thread pool، لكن synchronous call من main تفضل توقف main. ANR نوع symptom له timing وcomponent؛ الدليل stack traces وPerfetto وsystem report.</p>

**English, 20 seconds:** “The Looper processes one queued message at a time. A long Runnable prevents later input, lifecycle, and frame work from running until it returns.”

**English, 60–90 seconds:** “The Looper processes one queued message at a time. A long Runnable prevents later input, lifecycle, and frame work from running until it returns. In production I start from the owning component and the platform boundary, then trace recreation, external input, cancellation, and late delivery. I keep small restoration or command data separate from durable business state, validate untrusted boundaries, and choose evidence that can distinguish the competing causes. I test pure policy on the JVM and use an Android integration or device trace for framework behavior.”

## Senior follow-ups

1. **Trace how a long Runnable causes input latency on the main thread.** The Looper processes one queued message at a time. A long Runnable prevents later input, lifecycle, and frame work from running until it returns.
2. **Why can a fast service still cause an ANR through Binder?** A synchronous Binder call blocks the caller. From main, queueing, remote contention, or nested locks can exceed the response budget even when average service time is low.
3. **Given one ANR stack, how do you avoid blaming the top frame incorrectly?** Classify whether the frame is running, blocked, waiting on Binder, or waiting on a lock. Follow ownership and compare repeated traces and timeline evidence.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">جاوب الأسئلة من AND-Q016 إلى AND-Q020 بصوتك قبل فتح الإجابة. الاعتقاد إن happy path أو rotation واحدة تثبت Android lifecycle غلط؛ افصل كل owner وentry point وfailure. راجع المصادر الرسمية المتحققة بتاريخ 2026-10-11.</p>

اكتب test matrix قبل استخدام adb أو emulator؛ الوحدة دي لا تدّعي Android execution محليًا.


حلّل [SCN-026](../Real-World-Scenarios/SCN-026-anr-release-network-l.md) من غير ما تقرأ الإصلاح الأول.

**Evidence limit:** Official Android behavior is sourced, but this host has no Android SDK/emulator. Pure policy code is marked separately from device evidence.
