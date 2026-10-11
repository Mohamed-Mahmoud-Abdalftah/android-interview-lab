---
id: COR-002
title: Job hierarchy, exceptions and supervision
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 60
prerequisite_ids: [COR-001]
learning_outcomes:
  - Trace failure and cancellation through a parent-child Job tree
  - Explain launch, async, await and CoroutineExceptionHandler without folklore
  - Choose coroutineScope or supervisorScope from the product contract
  - Preserve CancellationException while converting recoverable child failures to data
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://kotlinlang.org/docs/exception-handling.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/supervisor-scope.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/
  - https://developer.android.com/kotlin/coroutines/coroutines-best-practices
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [COR-Q006, COR-Q007, COR-Q008, COR-Q009, COR-Q010]
---

# COR-002 — Job hierarchy, exceptions and supervision

**Interview target:** في آخر الدرس لازم تعرف ترسم شجرة الـJobs، وتتوقع مين هيتلغي عند كل exception، وتدافع عن اختيارك بين fail-fast وpartial success. احفظش أسماء APIs من غير contract.

## Mental model — الاستثناء بيتحرك في شجرة ملكية

<p dir="rtl" lang="ar">كل coroutine متوصلة بـparent عن طريق <code dir="ltr">Job</code> بتدخل في شجرة ملكية. الـparent بيستنى أولاده قبل ما يكتمل. في النطاق العادي، فشل child بـexception غير <code dir="ltr">CancellationException</code> يفشل الـparent؛ والـparent يلغي باقي أولاده. السلوك ده مناسب لما العملية وحدة واحدة: لو تحميل الحساب فشل، ماينفعش نرجع شاشة تدّعي إن العملية نجحت بنص بيانات.</p>

<p dir="rtl" lang="ar">الـsupervision يغيّر اتجاه انتشار <strong>فشل الطفل</strong>: child يفشل من غير ما يسقط إخوته تلقائيًا. لكنه مش بيحوّل الإلغاء لنجاح، ومش بيبلع exception لو محدش تعامل معاها. استخدمه لما الـproduct contract يسمح بنتائج مستقلة، زي dashboard فيها offers وnotifications وloyalty؛ تعطل notifications ما يمنعش عرض الباقي.</p>

| السؤال قبل اختيار API | لو الإجابة نعم | القرار الأقرب |
|---|---|---|
| هل كل النتائج لازم تنجح كـtransaction منطقية واحدة؟ | فشل واحدة يبطل الكل | `coroutineScope` وfail-fast |
| هل كل child مستقلة ومسموح partial result واضح؟ | اعرض الناجح وخطأ كل جزء | `supervisorScope` مع معالجة صريحة |
| هل اللي حصل cancellation من المالك؟ | العملية كلها انتهى عمرها | أعد رمي `CancellationException` |
| هل محتاج result من child؟ | لازم failure يبقى ظاهر عند الاستهلاك | `async` ثم `await` داخل boundary واضحة |

## Mechanism and execution trace — fail-fast مقابل partial success

```text
Screen Job
└── loadDashboard()
    ├── profile async
    ├── offers async
    └── notifications async
```

<p dir="rtl" lang="ar"><strong>المسار العادي:</strong> عند <code dir="ltr">t0</code> يبدأ الثلاث أطفال. عند <code dir="ltr">t1</code> يفشل offers بـ<code dir="ltr">IOException</code>. في <code dir="ltr">coroutineScope</code> الفشل يلغي profile وnotifications، والـcaller يستقبل الفشل بعد cleanup. في <code dir="ltr">supervisorScope</code> الأخوات يكملوا، لكن لازم offers تتحول لحالة خطأ معلنة أو exception تتلاحظ عند <code dir="ltr">await</code>.</p>

<p dir="rtl" lang="ar"><strong>مسار الإلغاء:</strong> المستخدم يقفل الشاشة عند <code dir="ltr">t1</code>. الـowner يلغي parent. سواء النطاق عادي أو supervisor، كل الأطفال يتلغوا. لو catch عام حوّل <code dir="ltr">CancellationException</code> إلى <code dir="ltr">ChildResult(error=...)</code> فالعملية هتكمل بعد انتهاء عمرها؛ ده bug مش resilience.</p>

```kotlin
suspend fun <T> supervisedBatch(
    tasks: List<suspend () -> T>,
): List<ChildResult<T>> = supervisorScope {
    tasks.map { task ->
        async {
            runCatching { task() }.fold(
                onSuccess = { ChildResult(value = it) },
                onFailure = {
                    if (it is CancellationException) throw it
                    ChildResult(error = it.message ?: "unknown")
                },
            )
        }
    }.awaitAll()
}
```

<p dir="rtl" lang="ar">الكود ده بيطبق contract محدد: ordinary failure لكل task تتحول لنتيجة مستقلة، لكن cancellation تفضل control signal وتطلع للمالك. ترتيب الناتج هو ترتيب input لأن <code dir="ltr">awaitAll</code> يرجع نتائج الـDeferreds بالترتيب، مش ترتيب اكتمال الشبكة.</p>

## Wrong and corrected implementation — catch مش دايمًا handling

```kotlin
// Wrong: swallows cancellation and keeps the operation alive.
suspend fun loadWidget(): WidgetResult = try {
    WidgetResult.Success(remote.load())
} catch (error: Throwable) {
    WidgetResult.Failure(error.message.orEmpty())
}
```

<p dir="rtl" lang="ar">المشكلة إن <code dir="ltr">Throwable</code> يشمل cancellation. بعد إلغاء الشاشة، catch يرجع Failure عادي؛ الكود اللي بعده ممكن يسجل analytics أو يكتب state لشاشة ماتت. كمان التعامل مع <code dir="ltr">OutOfMemoryError</code> كأنه network failure قرار خطر.</p>

```kotlin
suspend fun loadWidget(): WidgetResult = try {
    WidgetResult.Success(remote.load())
} catch (cancelled: CancellationException) {
    throw cancelled
} catch (error: IOException) {
    WidgetResult.Failure("network")
}
```

<p dir="rtl" lang="ar">التصحيح يمسك failure متوقعة عند boundary تعرف معناها، ويرمي cancellation تاني. في Kotlin الحديثة تقدر تستخدم <code dir="ltr">ensureActive()</code> في catch واسع لو عندك سبب قوي للcatch، لكن الأفضل تضيق نوع الخطأ من البداية.</p>

## `launch`, `async`, and `CoroutineExceptionHandler`

<p dir="rtl" lang="ar"><code dir="ltr">launch</code> بيرجع Job من غير value. لو root launch فشل ومافيش parent يتعامل، exception تعتبر uncaught وقد تصل إلى <code dir="ltr">CoroutineExceptionHandler</code>. إنما child launch داخل structured scope يبلّغ parent؛ تركيب handler على child مش هيمنع parent من الفشل.</p>

<p dir="rtl" lang="ar"><code dir="ltr">async</code> بيحفظ النتيجة أو الفشل داخل <code dir="ltr">Deferred</code>، والـconsumer يلاحظ الفشل عند <code dir="ltr">await</code>. ده لا يعني إنك تقدر تنسى await: exception غير الملحوظة تفضل design bug، والـstructured parent ممكن يفشل أصلًا حسب الشجرة. الـhandler آخر boundary للـuncaught exception وlogging؛ مش بديل لـ<code dir="ltr">try/catch</code> في business flow ومش recovery mechanism.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">اختبار المعمل الأول يشغل ثلاث tasks: نجاح، failure، نجاح. يثبت إن supervision حافظ على نتيجتي الإخوة وسجل خطأ المهمة الثانية في مكانها. الاختبار الثاني يبدأ task معلقة، يلغي الـparent، ثم يثبت إن <code dir="ltr">await</code> رمت <code dir="ltr">CancellationException</code> وإن العملية اتعلمت cancelled. أول نسخة من المعمل فشلت فعلًا لأنها استخدمت <code dir="ltr">runCatching</code> من غير إعادة رمي cancellation؛ الاختبار كشف العيب واتصلح.</p>

حالات لازم تتسأل في code review:

1. هل partial data واضحة للمستخدم، ولا بتعرض شاشة تبدو كاملة وهي ناقصة؟
2. هل retries مستقلة لكل child، ولا ممكن تعمل duplicate side effect؟
3. هل exception فيها PII قبل logging؟
4. هل cleanup داخل `finally` سريع وقابل للإلغاء، أم يستخدم `NonCancellable` لمساحة أكبر من اللازم؟
5. هل owner يملك العمر فعلًا، أم scope معمولة يدويًا ومش بتتقفل؟

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية بالمصري:</strong> في structured concurrency الـJob tree بتحدد الملكية: parent يستنى أولاده، وفشل child عادي يفشل parent ويلغي الإخوة. أستخدم supervision بس لو الـproduct يسمح partial success، وأتعامل مع failure لكل child صراحة. cancellation مش error business؛ ما ببلعهاش في catch عام.</p>

**English, 20 seconds:** “A normal coroutine scope is fail-fast: a child failure fails the parent and cancels siblings. I use supervision only when sibling results are independently useful, handle each child failure explicitly, and always preserve cancellation.”

**English, 60–90 seconds:** “I start from the product contract. If several child operations form one logical result, I keep them in a regular coroutineScope so a failure cancels the group. If the UI can honestly show partial data, I use supervisorScope and represent each recoverable child failure in that child’s result. I do not use CoroutineExceptionHandler as recovery; it observes uncaught root failures after the coroutine cannot resume. For async work, I consume the Deferred with await. A broad catch must rethrow CancellationException, otherwise closing the screen can be converted into a normal failure and stale work continues. I verify both sibling isolation and parent cancellation with a controlled coroutine test.”

## Senior follow-ups

1. **هل `supervisorScope` يمنع إلغاء الأطفال لما الـparent يتلغي؟** لا. هو يعزل فشل child عن siblings؛ فشل block نفسه أو إلغاء parent يلغي الأطفال.
2. **ليه ما نحطش `CoroutineExceptionHandler` على كل child؟** لأن child exception تتوجه للparent في structured hierarchy. الـhandler مناسب عند root uncaught boundary للرصد، مش لتغيير business result.
3. **لو اتنين children فشلوا في نفس الوقت مين يظهر؟** أول exception المكتملة للفشل تبقى primary عادة، والباقي قد تظهر suppressed حسب المنصة والتوقيت. ما تبنيش product logic على ترتيب السباق.
4. **إمتى `NonCancellable` مقبول؟** في cleanup صغير لازم يكتمل، زي إغلاق أو flush محدود. استخدامه لطلب شبكة كامل يؤخر cancellation ويكسر توقعات المالك.

## Misconceptions and revision

- “Supervisor يعني errors تختفي.” غلط؛ لازم تستهلك أو تمثل الفشل.
- “Handler يمسك أي exception.” غلط؛ child failures تتعامل معها hierarchy، و`async` يكشفها عند `await`.
- “Cancellation failure عادي.” غلط؛ هي إشارة انتهاء عمر العملية.
- “Partial success دايمًا UX أحسن.” غلط؛ لو البيانات بينها invariant، النتيجة الجزئية ممكن تكون مضللة.

**Practice:** جاوب [COR-Q006](../Interview-Question-Bank/Questions/COR-Q006.md) إلى [COR-Q010](../Interview-Question-Bank/Questions/COR-Q010.md)، ثم نفّذ [LAB-018](../Coding-Challenges/LAB-018-supervised-batch.md) وحلل [SCN-019](../Real-World-Scenarios/SCN-019-dashboard-child-failure.md).

**Evidence limit:** الاختبارات JVM مع `kotlinx-coroutines-test 1.11.0`. مفيش Android lifecycle أو network حقيقية في المعمل، لذلك ربط scope بـViewModel يحتاج Android integration test منفصل.
