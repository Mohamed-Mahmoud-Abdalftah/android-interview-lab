---
id: COR-003
title: Cooperative cancellation and cleanup
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 60
prerequisite_ids: [COR-002]
learning_outcomes:
  - Explain the runtime contract under interview pressure
  - Trace success failure cancellation and ownership
  - Review wrong code and defend a corrected design
  - Design deterministic tests and name evidence limits
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://kotlinlang.org/docs/cancellation-and-timeouts.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html
  - https://developer.android.com/kotlin/coroutines/coroutines-best-practices
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [COR-Q011, COR-Q012, COR-Q013, COR-Q014, COR-Q015]
---

# COR-003 — Cooperative cancellation and cleanup

**Interview target:** اشرح الـcontract، ارسم execution trace، راجع failure path، ثم اقترح test يفرق بين الأسباب المتنافسة. الاسم من غير trace مش إجابة senior.

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المشكلة العملية في الوحدة دي: الـloop الثقيلة تتجاهل cancellation، أو catch عام يبلع CancellationException، أو cleanup طويل داخل NonCancellable يؤخر إغلاق الشاشة. المطلوب في المقابلة مش ذكر operator؛ المطلوب تربط الـsymptom بالـowner والـordering والـfailure policy، وبعدها تختار إصلاح تقدر تختبره.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">الإلغاء في coroutines تعاوني: طلب الإلغاء يغيّر حالة الـJob، والكود يوقف لما يوصل suspension point قابلة للإلغاء أو يعمل فحص صريح. loop حسابية طويلة من غير تعليق أو فحص ممكن تكمل بعد إلغاء الشاشة. cleanup يتحط في finally، وNonCancellable يتستخدم لأصغر جزء لازم يخلص فعلًا.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ابدأ من الـJob أو collection owner. كل child أو collector له lifetime، وكل value لها ordering وdelivery contract. الـguarantee الموثقة في الـAPI غير implementation detail وغير behavior خاص بـAndroid lifecycle. لما operation تعدّي boundary خارجية زي network أو database، إلغاء coroutine مش معناه rollback للعمل الخارجي.</p>

## Trace خطوة بخطوة — Execution trace

<ol dir="rtl" lang="ar">
<li>الـowner يبدأ import تحت Job مملوكة له.</li>
<li>المستخدم يخرج؛ الـJob تصبح cancelling.</li>
<li>الـloop تصل إلى ensureActive أو yield فترمي CancellationException.</li>
<li>finally يقفل المورد، والـparent يلاحظ cancelled بدل success كاذب.</li>
</ol>

<p dir="rtl" lang="ar">في المقابلة، سمّي المالك والعملية والـboundary قبل اختيار operator. فرّق بين نتيجة business، exception تقنية، وإلغاء بسبب انتهاء العمر. بعدين قول إيه اللي الاختبار يقدر يثبته وإيه اللي محتاج Android أو network integration.</p>

## Wrong and corrected implementation

```kotlin
suspend fun import(rows: List<Row>) {
    for (row in rows) expensiveParse(row) // no suspension/checkpoint
}
```

<p dir="rtl" lang="ar"><strong>المشكلة:</strong> الـloop الثقيلة تتجاهل cancellation، أو catch عام يبلع CancellationException، أو cleanup طويل داخل NonCancellable يؤخر إغلاق الشاشة.</p>

```kotlin
suspend fun import(rows: List<Row>) {
    try {
        for (row in rows) {
            currentCoroutineContext().ensureActive()
            expensiveParse(row)
        }
    } finally {
        closeParser()
    }
}
```

<p dir="rtl" lang="ar">التصحيح هنا يوضح intent، لكنه مش وصفة تتنسخ من غير requirements. راجع lifetime، ordering، backpressure، retry safety، وprivacy قبل production.</p>

## مثال Production حقيقي

<p dir="rtl" lang="ar">تطبيق استيراد يقرأ 80 ألف row في loop حسابية على Default. المستخدم يقفل الشاشة لكن CPU يفضل عالي والنتيجة القديمة تظهر لما يفتح حساب تاني. تتبع owner والـJob ومواضع suspension. أصلحها بفحص cancellation عند batch boundary، generation للنتيجة، وfinally يقفل parser. اختبر حد أقصى لعدد rows بعد الإلغاء بدل الاعتماد على sleep. في production، ضيف identity للطلب أو الـJob في trace، وصنّف النهاية إلى success أو failure متوقعة أو cancellation أو stale drop. متسجلش payload حساسة، وحط rollout signal يقدر يوقف النشر لو correctness اتدهورت.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives

<p dir="rtl" lang="ar">استخدم الـprimitive لما contract البيانات يطابقها، مش عشان هي الأشهر. لو كل value لازم تتعالج، متستخدمش policy تسقط الوسط. لو العملية side effect غير قابلة للrollback، متعتمدش على cancellation وحدها. ولو lifetime قصيرة، متحطش الشغل في scope أطول من المالك. الحل الأبسط sequential أفضل لو مفيش استقلال حقيقي أو latency تستفيد من concurrency.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">اختبر إلغاء parent بعد batch معلومة، وتأكد إن مفيش عناصر اتعالجت بعدها، وإن finally اتنفذ مرة واحدة، وإن الفشل business لا يتصنف cancellation.</p>

- Test the happy path and the first observable intermediate state.
- Force the failure at a named boundary; do not mock away the behavior under discussion.
- Cancel the owner and assert that no stale output appears later.
- Record the JVM/Android evidence boundary explicitly.

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الإلغاء في coroutines تعاوني: طلب الإلغاء يغيّر حالة الـJob، والكود يوقف لما يوصل suspension point قابلة للإلغاء أو يعمل فحص صريح. loop حسابية طويلة من غير تعليق أو فحص ممكن تكمل بعد إلغاء الشاشة. cleanup يتحط في finally، وNonCancellable يتستخدم لأصغر جزء لازم يخلص فعلًا.</p>

**English, 20 seconds:** “Cancellation is cooperative. Suspending APIs usually check it, but CPU loops need explicit checkpoints such as ensureActive or yield. I keep cleanup in finally, rethrow CancellationException, and restrict NonCancellable to a small bounded cleanup operation.”

**English, 60–90 seconds:** “I begin with ownership and product semantics, then choose the coroutine or Flow primitive. I trace the successful path, ordinary failure, parent cancellation, and a late result. I keep recoverable errors explicit, preserve cancellation, and test scheduling with controlled gates rather than sleep. I also state the evidence boundary: a JVM test proves the pure contract, while lifecycle, transport, or device behavior needs the matching integration test.”

## Senior follow-ups

1. **A CPU-heavy loop is inside a suspend function but ignores cancellation. Explain why and choose checkpoints without destroying throughput.** A suspend modifier does not insert cancellation checks into ordinary CPU instructions. I add ensureActive at a measured batch boundary or yield when fairness is needed, then test how much work completes after cancellation.
2. **Review a repository that catches Exception and returns Result.failure. What cancellation bug can it create?** CancellationException is an Exception. Mapping it to a normal failure can continue retries or publish stale state after the owner is gone. I rethrow it before mapping expected domain or transport failures.
3. **A team wraps a network upload in withContext(NonCancellable) so cleanup finishes. Review the decision.** NonCancellable around the upload defeats the owner's cancellation and can delay shutdown. I keep the upload cancellable and reserve NonCancellable for a short bounded cleanup such as closing or recording a local terminal marker.

## Misconceptions and revision

- API names are not a failure policy; draw the owner and child relationships.
- Cancellation is not rollback for an external side effect.
- A passing happy-path test is not evidence for ordering or cleanup.
- Buffering, retry, and supervision must preserve the product contract.

## Hands-on lab and further learning

<p dir="rtl" lang="ar">ابدأ باختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>، وبعدها راجع implementation. غيّر test واحدة بحيث تكشف الحل الغلط قبل ما تعدّل الكود. مصادر الدرس فوق رسمية ومتراجعة بتاريخ 2026-10-11؛ Android-specific behavior لسه محتاج SDK integration.</p>

**Practice:** answer COR-Q011–COR-Q015, solve [LAB-019](../Coding-Challenges/LAB-019-bounded-cooperative-batches.md), and investigate [SCN-020](../Real-World-Scenarios/SCN-020-an-import-keeps-using-cpu-after-the-screen-closes.md).

**Evidence limit:** The linked Kotlin/JVM tests exercise the pure decision model. Android lifecycle and real transport behavior are sourced but not executed without the Android toolchain.
