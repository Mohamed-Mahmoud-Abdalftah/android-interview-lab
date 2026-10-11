---
id: COR-005
title: Latest operators, buffering and stale writes
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
  - https://kotlinlang.org/docs/flow.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/collect-latest.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flat-map-latest.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [COR-Q021, COR-Q022, COR-Q023, COR-Q024, COR-Q025]
---

# COR-005 — Latest operators, buffering and stale writes

**Interview target:** اشرح الـcontract، ارسم execution trace، راجع failure path، ثم اقترح test يفرق بين الأسباب المتنافسة. الاسم من غير trace مش إجابة senior.

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المشكلة العملية في الوحدة دي: conflate تضيع progress مطلوب، buffer غير محدودة تستهلك memory، أو latest cancellation تتفهم غلط كـrollback لعملية server بدأت بالفعل. المطلوب في المقابلة مش ذكر operator؛ المطلوب تربط الـsymptom بالـowner والـordering والـfailure policy، وبعدها تختار إصلاح تقدر تختبره.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">latest operators تلغي الشغل القديم لما value جديدة توصل، لكنها تعتمد إن الشغل القديم قابل للإلغاء. buffer يسمح للمنتج يسبق consumer ضمن capacity، وconflate يحتفظ بالأحدث ويهمل الوسط. ولا واحدة منهم تمنع stale database write لو side effect غير cancellable أو بدأ commit بالفعل؛ ساعتها تحتاج generation أو idempotency عند boundary.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ابدأ من الـJob أو collection owner. كل child أو collector له lifetime، وكل value لها ordering وdelivery contract. الـguarantee الموثقة في الـAPI غير implementation detail وغير behavior خاص بـAndroid lifecycle. لما operation تعدّي boundary خارجية زي network أو database، إلغاء coroutine مش معناه rollback للعمل الخارجي.</p>

## Trace خطوة بخطوة — Execution trace

<ol dir="rtl" lang="ar">
<li>المستخدم يكتب a فتبدأ request 41.</li>
<li>يكتب ab؛ flatMapLatest تلغي collection القديمة وتبدأ request 42.</li>
<li>لو client يتعاون، 41 تتوقف. لو commit حصل، response 41 قد ترجع.</li>
<li>generation gate تقبل 42 فقط؛ UI لا تستبدل النتيجة الجديدة بالقديمة.</li>
</ol>

<p dir="rtl" lang="ar">في المقابلة، سمّي المالك والعملية والـboundary قبل اختيار operator. فرّق بين نتيجة business، exception تقنية، وإلغاء بسبب انتهاء العمر. بعدين قول إيه اللي الاختبار يقدر يثبته وإيه اللي محتاج Android أو network integration.</p>

## Wrong and corrected implementation

```kotlin
queryFlow.collect { query ->
    val result = api.search(query)
    _state.value = result // an older request can win
}
```

<p dir="rtl" lang="ar"><strong>المشكلة:</strong> conflate تضيع progress مطلوب، buffer غير محدودة تستهلك memory، أو latest cancellation تتفهم غلط كـrollback لعملية server بدأت بالفعل.</p>

```kotlin
queryFlow.flatMapLatest(api::searchFlow)
    .collectLatest { result -> render(result) }
// Add a request generation at non-cancellable write boundaries.
```

<p dir="rtl" lang="ar">التصحيح هنا يوضح intent، لكنه مش وصفة تتنسخ من غير requirements. راجع lifetime، ordering، backpressure، retry safety، وprivacy قبل production.</p>

## مثال Production حقيقي

<p dir="rtl" lang="ar">request لكلمة قصيرة بطيئة ترجع بعد request لكلمة أطول، فتستبدل state الجديدة. استخدم controlled responses لإثبات الترتيب، ثم flatMapLatest للشغل القابل للإلغاء وrequest generation عند publish boundary. راقب cancelled، stale-dropped، latency، وما تعتبرش cancellation rollback للسيرفر. في production، ضيف identity للطلب أو الـJob في trace، وصنّف النهاية إلى success أو failure متوقعة أو cancellation أو stale drop. متسجلش payload حساسة، وحط rollout signal يقدر يوقف النشر لو correctness اتدهورت.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives

<p dir="rtl" lang="ar">استخدم الـprimitive لما contract البيانات يطابقها، مش عشان هي الأشهر. لو كل value لازم تتعالج، متستخدمش policy تسقط الوسط. لو العملية side effect غير قابلة للrollback، متعتمدش على cancellation وحدها. ولو lifetime قصيرة، متحطش الشغل في scope أطول من المالك. الحل الأبسط sequential أفضل لو مفيش استقلال حقيقي أو latency تستفيد من concurrency.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">بوابات controlled لطلبين ترجع القديم بعد الجديد، assertion إن generation القديمة مرفوضة، واختبارات overflow policy وside-effect idempotency.</p>

- Test the happy path and the first observable intermediate state.
- Force the failure at a named boundary; do not mock away the behavior under discussion.
- Cancel the owner and assert that no stale output appears later.
- Record the JVM/Android evidence boundary explicitly.

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> latest operators تلغي الشغل القديم لما value جديدة توصل، لكنها تعتمد إن الشغل القديم قابل للإلغاء. buffer يسمح للمنتج يسبق consumer ضمن capacity، وconflate يحتفظ بالأحدث ويهمل الوسط. ولا واحدة منهم تمنع stale database write لو side effect غير cancellable أو بدأ commit بالفعل؛ ساعتها تحتاج generation أو idempotency عند boundary.</p>

**English, 20 seconds:** “Latest operators cancel obsolete coroutine work, but cancellation is not transaction rollback. I use them for superseded UI work, then add request generations or idempotency at boundaries where an old side effect can still complete. Buffer and conflate are semantic choices, not automatic performance fixes.”

**English, 60–90 seconds:** “I begin with ownership and product semantics, then choose the coroutine or Flow primitive. I trace the successful path, ordinary failure, parent cancellation, and a late result. I keep recoverable errors explicit, preserve cancellation, and test scheduling with controlled gates rather than sleep. I also state the evidence boundary: a JVM test proves the pure contract, while lifecycle, transport, or device behavior needs the matching integration test.”

## Senior follow-ups

1. **What exactly does collectLatest cancel when a new value arrives, and what can still escape?** It cancels the previous collector action and waits for its cancellation before running the next. Blocking or already-committed external work may continue, so I do not treat cancellation as rollback.
2. **A progress stream emits 1 through 100 faster than rendering. Compare buffer and conflate.** Buffer lets the producer get ahead until capacity fills, preserving queued values. Conflate lets a slow collector skip intermediates and process the latest. I use conflate only when intermediate progress has no business meaning.
3. **Design type-ahead search with debounce, distinctUntilChanged, and flatMapLatest. Name the remaining risks.** I normalize input, debounce UI noise, remove equal queries, and switch to the latest search Flow. I still handle cancellation cooperation, cache policy, errors, loading state, and stale writes outside the cancellable pipeline.

## Misconceptions and revision

- API names are not a failure policy; draw the owner and child relationships.
- Cancellation is not rollback for an external side effect.
- A passing happy-path test is not evidence for ordering or cleanup.
- Buffering, retry, and supervision must preserve the product contract.

## Hands-on lab and further learning

<p dir="rtl" lang="ar">ابدأ باختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>، وبعدها راجع implementation. غيّر test واحدة بحيث تكشف الحل الغلط قبل ما تعدّل الكود. مصادر الدرس فوق رسمية ومتراجعة بتاريخ 2026-10-11؛ Android-specific behavior لسه محتاج SDK integration.</p>

**Practice:** answer COR-Q021–COR-Q025, solve [LAB-021](../Coding-Challenges/LAB-021-reject-a-stale-versioned-result.md), and investigate [SCN-022](../Real-World-Scenarios/SCN-022-old-search-results-overwrite-the-latest-query.md).

**Evidence limit:** The linked Kotlin/JVM tests exercise the pure decision model. Android lifecycle and real transport behavior are sourced but not executed without the Android toolchain.
