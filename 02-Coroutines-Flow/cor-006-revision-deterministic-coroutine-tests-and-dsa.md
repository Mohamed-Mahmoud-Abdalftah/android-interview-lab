---
id: COR-006
title: Revision: deterministic coroutine tests and DSA
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 60
prerequisite_ids: [COR-003, COR-004]
learning_outcomes:
  - Explain the runtime contract under interview pressure
  - Trace success failure cancellation and ownership
  - Review wrong code and defend a corrected design
  - Design deterministic tests and name evidence limits
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/kotlin/coroutines/test
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
  - https://kotlinlang.org/docs/collections-overview.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [COR-Q026, COR-Q027, COR-Q028, COR-Q029, COR-Q030]
---

# COR-006 — Revision: deterministic coroutine tests and DSA

**Interview target:** اشرح الـcontract، ارسم execution trace، راجع failure path، ثم اقترح test يفرق بين الأسباب المتنافسة. الاسم من غير trace مش إجابة senior.

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المشكلة العملية في الوحدة دي: test يستخدم scheduler مختلفة، أو production dispatcher ثابتة، أو assert قبل runCurrent، أو hot flow collection تفضل معلقة، أو test تثبت timing بدل behavior. المطلوب في المقابلة مش ذكر operator؛ المطلوب تربط الـsymptom بالـowner والـordering والـfailure policy، وبعدها تختار إصلاح تقدر تختبره.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">اختبار coroutine deterministic يتحكم في scheduler والـdispatcher والـinputs؛ ما يستناش wall clock. runTest يتابع coroutines على test scheduler، وadvanceTimeBy يحرك virtual time، وrunCurrent يشغل المهام الجاهزة. dispatcher injection تمنع production Dispatchers من الهروب خارج سيطرة الاختبار. جزء DSA يراجع invariant للـhash map بدل حفظ الحل.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ابدأ من الـJob أو collection owner. كل child أو collector له lifetime، وكل value لها ordering وdelivery contract. الـguarantee الموثقة في الـAPI غير implementation detail وغير behavior خاص بـAndroid lifecycle. لما operation تعدّي boundary خارجية زي network أو database، إلغاء coroutine مش معناه rollback للعمل الخارجي.</p>

## Trace خطوة بخطوة — Execution trace

<ol dir="rtl" lang="ar">
<li>الاختبار ينشئ TestScope وStandardTestDispatcher على scheduler واحدة.</li>
<li>ينادي subject؛ الشغل يتجدول لكنه لا يجري سحريًا.</li>
<li>runCurrent يشغل الموجود عند الزمن الحالي؛ advanceTimeBy يحرك deadline.</li>
<li>assertions تفحص states والـJobs، ثم runTest يتأكد إن مفيش coroutine معلقة.</li>
</ol>

<p dir="rtl" lang="ar">في المقابلة، سمّي المالك والعملية والـboundary قبل اختيار operator. فرّق بين نتيجة business، exception تقنية، وإلغاء بسبب انتهاء العمر. بعدين قول إيه اللي الاختبار يقدر يثبته وإيه اللي محتاج Android أو network integration.</p>

## Wrong and corrected implementation

```kotlin
@Test fun retryWorks() = runBlocking {
    subject.retry()
    Thread.sleep(3_000)
    assertEquals(Success, subject.state.value)
}
```

<p dir="rtl" lang="ar"><strong>المشكلة:</strong> test يستخدم scheduler مختلفة، أو production dispatcher ثابتة، أو assert قبل runCurrent، أو hot flow collection تفضل معلقة، أو test تثبت timing بدل behavior.</p>

```kotlin
@Test fun retryWorks() = runTest {
    subject = Subject(dispatcher = StandardTestDispatcher(testScheduler))
    subject.retry()
    advanceTimeBy(3_000)
    runCurrent()
    assertEquals(Success, subject.state.value)
}
```

<p dir="rtl" lang="ar">التصحيح هنا يوضح intent، لكنه مش وصفة تتنسخ من غير requirements. راجع lifetime، ordering، backpressure، retry safety، وprivacy قبل production.</p>

## مثال Production حقيقي

<p dir="rtl" lang="ar">الاختبار يستخدم runBlocking وdelay حقيقي، والsubject يشغل Dispatchers.IO مباشرة. تحت ضغط CI الـassertion تسبق النتيجة. احقن dispatcher، شارك testScheduler، اثبت Loading قبل الوقت وSuccess بعد advance، وألغ collector الدائم. شغّل الاختبار مكررًا كتشخيص ثم أوقف الاعتماد على retry كحل. في production، ضيف identity للطلب أو الـJob في trace، وصنّف النهاية إلى success أو failure متوقعة أو cancellation أو stale drop. متسجلش payload حساسة، وحط rollout signal يقدر يوقف النشر لو correctness اتدهورت.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives

<p dir="rtl" lang="ar">استخدم الـprimitive لما contract البيانات يطابقها، مش عشان هي الأشهر. لو كل value لازم تتعالج، متستخدمش policy تسقط الوسط. لو العملية side effect غير قابلة للrollback، متعتمدش على cancellation وحدها. ولو lifetime قصيرة، متحطش الشغل في scope أطول من المالك. الحل الأبسط sequential أفضل لو مفيش استقلال حقيقي أو latency تستفيد من concurrency.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">اختبر intermediate state قبل تحريك الوقت، terminal state بعده، cancellation، cleanup، وعدم وجود tasks معلقة. في DSA اختبر empty وduplicates وoverflow وعدم تعديل input.</p>

- Test the happy path and the first observable intermediate state.
- Force the failure at a named boundary; do not mock away the behavior under discussion.
- Cancel the owner and assert that no stale output appears later.
- Record the JVM/Android evidence boundary explicitly.

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> اختبار coroutine deterministic يتحكم في scheduler والـdispatcher والـinputs؛ ما يستناش wall clock. runTest يتابع coroutines على test scheduler، وadvanceTimeBy يحرك virtual time، وrunCurrent يشغل المهام الجاهزة. dispatcher injection تمنع production Dispatchers من الهروب خارج سيطرة الاختبار. جزء DSA يراجع invariant للـhash map بدل حفظ الحل.</p>

**English, 20 seconds:** “A deterministic coroutine test owns the dispatcher, scheduler, and completion gates. I assert intermediate state before advancing virtual time, then advance only the work needed. I avoid sleeps and make every launched coroutine visible to runTest. For DSA I state the invariant before code and test boundaries, not just the happy path.”

**English, 60–90 seconds:** “I begin with ownership and product semantics, then choose the coroutine or Flow primitive. I trace the successful path, ordinary failure, parent cancellation, and a late result. I keep recoverable errors explicit, preserve cancellation, and test scheduling with controlled gates rather than sleep. I also state the evidence boundary: a JVM test proves the pure contract, while lifecycle, transport, or device behavior needs the matching integration test.”

## Senior follow-ups

1. **What does runTest give you that runBlocking plus delay does not?** runTest provides a TestScope, tracks child coroutines, skips compatible delays through virtual time, and reports unfinished work. It makes scheduling controllable instead of coupling assertions to machine speed.
2. **Why should test dispatchers in one test usually share a TestCoroutineScheduler?** A shared scheduler gives one virtual clock and one queue, so advance and runCurrent control all subject work consistently. Separate schedulers can leave work invisible to the test's clock.
3. **How do you test a StateFlow that never completes without hanging the test?** Read value for current state, use take or first for a bounded expectation, or launch a collector in backgroundScope and cancel it. The test must own collector lifetime.

## Misconceptions and revision

- API names are not a failure policy; draw the owner and child relationships.
- Cancellation is not rollback for an external side effect.
- A passing happy-path test is not evidence for ordering or cleanup.
- Buffering, retry, and supervision must preserve the product contract.

## Hands-on lab and further learning

<p dir="rtl" lang="ar">ابدأ باختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>، وبعدها راجع implementation. غيّر test واحدة بحيث تكشف الحل الغلط قبل ما تعدّل الكود. مصادر الدرس فوق رسمية ومتراجعة بتاريخ 2026-10-11؛ Android-specific behavior لسه محتاج SDK integration.</p>

**Practice:** answer COR-Q026–COR-Q030, solve [LAB-022](../Coding-Challenges/LAB-022-a-deterministic-task-queue.md), and investigate [SCN-023](../Real-World-Scenarios/SCN-023-a-retry-test-passes-locally-and-flakes-in-ci.md).

**Evidence limit:** The linked Kotlin/JVM tests exercise the pure decision model. Android lifecycle and real transport behavior are sourced but not executed without the Android toolchain.
