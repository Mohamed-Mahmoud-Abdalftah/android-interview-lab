---
id: COR-004
title: Flow cold/hot, StateFlow and SharedFlow
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 60
prerequisite_ids: [COR-001]
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
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/
  - https://developer.android.com/kotlin/flow/stateflow-and-sharedflow
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [COR-Q016, COR-Q017, COR-Q018, COR-Q019, COR-Q020]
---

# COR-004 — Flow cold/hot, StateFlow and SharedFlow

**Interview target:** اشرح الـcontract، ارسم execution trace، راجع failure path، ثم اقترح test يفرق بين الأسباب المتنافسة. الاسم من غير trace مش إجابة senior.

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المشكلة العملية في الوحدة دي: double collection يعمل duplicate requests، أو StateFlow تستخدم event فتتعاد، أو SharedFlow buffer تضيع events من غير contract، أو sharing scope تعيش أطول من feature. المطلوب في المقابلة مش ذكر operator؛ المطلوب تربط الـsymptom بالـowner والـordering والـfailure policy، وبعدها تختار إصلاح تقدر تختبره.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">الـcold Flow وصف لشغل يبدأ من جديد لكل collector. StateFlow hot وعندها current value واحدة؛ collector جديد ياخد أحدث state. SharedFlow hot broadcast بسياسة replay وbuffer لازم تتصمم بوضوح. اختار primitive من معنى البيانات: state قابلة للقراءة دلوقتي، event لحظي، أو query تتعاد لكل جمع.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ابدأ من الـJob أو collection owner. كل child أو collector له lifetime، وكل value لها ordering وdelivery contract. الـguarantee الموثقة في الـAPI غير implementation detail وغير behavior خاص بـAndroid lifecycle. لما operation تعدّي boundary خارجية زي network أو database، إلغاء coroutine مش معناه rollback للعمل الخارجي.</p>

## Trace خطوة بخطوة — Execution trace

<ol dir="rtl" lang="ar">
<li>Collector A يجمع cold flow فتبدأ network chain A.</li>
<li>Collector B يجمع نفس الوصف فتبدأ chain B مستقلة.</li>
<li>تحويلها بـstateIn يبدأ sharing coroutine مملوكة لـscope.</li>
<li>WhileSubscribed يحدد إمتى upstream تبدأ وتتوقف؛ إلغاء collector لا يلغي hot flow نفسها.</li>
</ol>

<p dir="rtl" lang="ar">في المقابلة، سمّي المالك والعملية والـboundary قبل اختيار operator. فرّق بين نتيجة business، exception تقنية، وإلغاء بسبب انتهاء العمر. بعدين قول إيه اللي الاختبار يقدر يثبته وإيه اللي محتاج Android أو network integration.</p>

## Wrong and corrected implementation

```kotlin
val navigation = MutableStateFlow<Route?>(null)
// A new collector can receive an old navigation command again.
```

<p dir="rtl" lang="ar"><strong>المشكلة:</strong> double collection يعمل duplicate requests، أو StateFlow تستخدم event فتتعاد، أو SharedFlow buffer تضيع events من غير contract، أو sharing scope تعيش أطول من feature.</p>

```kotlin
private val _state = MutableStateFlow(ScreenState())
val state = _state.asStateFlow()
// Durable state stays in StateFlow; transient effects get an explicit policy.
```

<p dir="rtl" lang="ar">التصحيح هنا يوضح intent، لكنه مش وصفة تتنسخ من غير requirements. راجع lifetime، ordering، backpressure، retry safety، وprivacy قبل production.</p>

## مثال Production حقيقي

<p dir="rtl" lang="ar">كل recomposition أو collector جديد بيجمع cold flow فتتكرر request، وفي نفس الوقت navigation معمولة StateFlow فتتعاد بعد rotation. افصل state عن effect، شارك upstream في scope مناسبة بسياسة WhileSubscribed، واربط collection بعمر الـview. اختبر عدد subscriptions وإعادة الإنشاء وغياب subscriber. في production، ضيف identity للطلب أو الـJob في trace، وصنّف النهاية إلى success أو failure متوقعة أو cancellation أو stale drop. متسجلش payload حساسة، وحط rollout signal يقدر يوقف النشر لو correctness اتدهورت.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives

<p dir="rtl" lang="ar">استخدم الـprimitive لما contract البيانات يطابقها، مش عشان هي الأشهر. لو كل value لازم تتعالج، متستخدمش policy تسقط الوسط. لو العملية side effect غير قابلة للrollback، متعتمدش على cancellation وحدها. ولو lifetime قصيرة، متحطش الشغل في scope أطول من المالك. الحل الأبسط sequential أفضل لو مفيش استقلال حقيقي أو latency تستفيد من concurrency.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">اختبر initial state، equality conflation، collectors جدد، توقف upstream مع subscription policy، والفرق بين غياب subscriber وبين buffer ممتلئة.</p>

- Test the happy path and the first observable intermediate state.
- Force the failure at a named boundary; do not mock away the behavior under discussion.
- Cancel the owner and assert that no stale output appears later.
- Record the JVM/Android evidence boundary explicitly.

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـcold Flow وصف لشغل يبدأ من جديد لكل collector. StateFlow hot وعندها current value واحدة؛ collector جديد ياخد أحدث state. SharedFlow hot broadcast بسياسة replay وbuffer لازم تتصمم بوضوح. اختار primitive من معنى البيانات: state قابلة للقراءة دلوقتي، event لحظي، أو query تتعاد لكل جمع.</p>

**English, 20 seconds:** “I choose a stream from data semantics. Cold Flow restarts per collector. StateFlow represents a current state value and conflates equal updates. SharedFlow broadcasts future emissions with an explicit replay and buffer policy. The sharing scope owns upstream lifetime.”

**English, 60–90 seconds:** “I begin with ownership and product semantics, then choose the coroutine or Flow primitive. I trace the successful path, ordinary failure, parent cancellation, and a late result. I keep recoverable errors explicit, preserve cancellation, and test scheduling with controlled gates rather than sleep. I also state the evidence boundary: a JVM test proves the pure contract, while lifecycle, transport, or device behavior needs the matching integration test.”

## Senior follow-ups

1. **Two collectors collect the same cold Flow and duplicate a network request. Explain the behavior and valid fixes.** A cold Flow executes its upstream separately for every collector. I either keep one collector, move the request behind a cache, or share it with stateIn or shareIn in a scope whose lifetime and start policy match the feature.
2. **Why might assigning an equal data-class value to MutableStateFlow produce no new emission?** StateFlow uses equality-based conflation. If the new value compares equal to the current value, collectors are not notified. State should be immutable and equality must represent every observable field.
3. **Choose replay and buffer behavior for analytics events versus a critical payment result.** Best-effort analytics may tolerate dropping with a measured buffer policy. A payment result is durable business state and should be persisted or represented in state, not trusted to an in-memory SharedFlow with no subscriber.

## Misconceptions and revision

- API names are not a failure policy; draw the owner and child relationships.
- Cancellation is not rollback for an external side effect.
- A passing happy-path test is not evidence for ordering or cleanup.
- Buffering, retry, and supervision must preserve the product contract.

## Hands-on lab and further learning

<p dir="rtl" lang="ar">ابدأ باختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>، وبعدها راجع implementation. غيّر test واحدة بحيث تكشف الحل الغلط قبل ما تعدّل الكود. مصادر الدرس فوق رسمية ومتراجعة بتاريخ 2026-10-11؛ Android-specific behavior لسه محتاج SDK integration.</p>

**Practice:** answer COR-Q016–COR-Q020, solve [LAB-020](../Coding-Challenges/LAB-020-choose-the-stream-from-its-contract.md), and investigate [SCN-021](../Real-World-Scenarios/SCN-021-one-screen-makes-duplicate-requests-and-another-loses-an-event.md).

**Evidence limit:** The linked Kotlin/JVM tests exercise the pure decision model. Android lifecycle and real transport behavior are sourced but not executed without the Android toolchain.
