---
id: COR-001
title: suspend, dispatchers and structured scopes
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-004]
learning_outcomes:
  - Explain why a suspend function is not automatically asynchronous or off the main thread
  - Trace parent and child completion and cancellation in a structured scope
  - Choose a dispatcher boundary for blocking work and inject it for deterministic tests
  - Distinguish launch, async, withContext and runBlocking by their contracts
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/coroutines-basics.html
  - https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/coroutine-scope.html
  - https://developer.android.com/kotlin/coroutines/coroutines-best-practices
  - https://developer.android.com/kotlin/coroutines
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileCard.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileCardTest.kt
question_ids: [COR-Q001, COR-Q002, COR-Q003, COR-Q004, COR-Q005]
---

# COR-001 — suspend, dispatchers and structured scopes

**Starting point:** [KOT-004](../01-Kotlin-JVM-ART/kot-004-functions-lambdas-and-closures.md) introduced function values and callback timing. A coroutine scope adds an explicit lifetime and cancellation relationship around suspending work. This is the first reviewed unit in the coroutines module, not completion of the six-day module.

**Two-hour route:** 55 minutes lesson and trace, 20 minutes [questions with visible answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes [LAB-005](../Coding-Challenges/LAB-005-profile-card-scope.md), 10 minutes [revision](../Flashcards-Revision/COR-001.md), optional 10 minutes [English speaking](../Speaking-Shadowing/DAY-07.md). All answers remain visible in Learning Mode.

## Mental model

<p dir="rtl" lang="ar">كلمة <code dir="ltr">suspend</code> معناها إن function تقدر تتوقف من غير ما تحجز thread وهي مستنية عملية suspending، وتكمل بعدين. الكلمة لوحدها مش بتفتح thread جديد، ومش بتضمن إن كل سطر جوه function غير blocking. لو ناديت blocking API على main thread من <code dir="ltr">suspend fun</code>، ممكن تفضل تجمّد الواجهة. الـ dispatcher يحدد أين يتنفذ جزء من الشغل، والـ scope يحدد مين يملك الشغل ده وإمتى يستناه أو يلغيه. <a dir="ltr" href="https://kotlinlang.org/docs/coroutines-basics.html">Kotlin coroutine basics</a>، اتراجع 2026-10-10.</p>

<ul dir="rtl" lang="ar">
<li><code dir="ltr">withContext(dispatcher) { ... }</code> ينقل تنفيذ block للسياق المحدد ويرجع النتيجة بعد ما يخلص؛ الـ caller يوقف suspension بدل block للـ thread عند suspension حقيقي.</li>
<li><code dir="ltr">coroutineScope { ... }</code> ينشئ نطاق أطفال مرتبطين بالـ caller وينتظر انتهاءهم. فشل طفل عادي يلغي الإخوة ويظهر للـ caller، مع تفاصيل التوقيت حسب التنفيذ.</li>
<li><code dir="ltr">launch</code> يرجع <code dir="ltr">Job</code> لشغل من غير result مباشرة؛ <code dir="ltr">async</code> يرجع <code dir="ltr">Deferred&lt;T&gt;</code> تستنى قيمته بـ <code dir="ltr">await()</code>.</li>
<li><code dir="ltr">runBlocking</code> جسر عند boundary متزامنة ويوقف thread اللي ناداه؛ ما تستخدموش لمجرد إنك جوه Android main thread.</li>
</ul>

## Mechanism and execution trace

<p dir="rtl" lang="ar">المعمل بيجمع اسم profile وعدد badges من عمليتين مستقلتين. الـ caller يبعت dispatcher؛ function تستخدم <code dir="ltr">withContext</code> ثم <code dir="ltr">coroutineScope</code> وتبدأ child <code dir="ltr">async</code> لكل مصدر. ترجع <code dir="ltr">ProfileCard</code> بعد النتيجتين فقط. لو parent اتلغى، الأطفال المعلقين يتلغوا من نفس الشجرة. الكود الحقيقي في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileCard.kt">ProfileCard.kt</a>، والاختبارات في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileCardTest.kt">ProfileCardTest.kt</a>. <a dir="ltr" href="https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/coroutine-scope.html">coroutineScope contract</a>.</p>

```kotlin
suspend fun loadProfileCard(
    profile: suspend () -> String,
    badges: suspend () -> Int,
    dispatcher: CoroutineDispatcher,
): ProfileCard = withContext(dispatcher) {
    coroutineScope {
        val name = async { profile() }
        val badgeCount = async { badges() }
        ProfileCard(name.await(), badgeCount.await())
    }
}
```

<table dir="rtl" lang="ar">
<thead><tr><th>اللحظة</th><th>الـ parent</th><th>الأطفال والنتيجة</th></tr></thead>
<tbody>
<tr><td dir="ltr">1</td><td>يدخل <code dir="ltr">withContext</code> على dispatcher المتحقن.</td><td>لسه مفيش card.</td></tr>
<tr><td dir="ltr">2</td><td>يدخل <code dir="ltr">coroutineScope</code>.</td><td><code dir="ltr">async(profile)</code> و<code dir="ltr">async(badges)</code> طفلان مرتبطان.</td></tr>
<tr><td dir="ltr">3</td><td>ينتظر <code dir="ltr">name.await()</code> ثم <code dir="ltr">badgeCount.await()</code>.</td><td>لو badges خلصت الأول، تفضل نتيجتها جاهزة؛ ترتيب الـ await لا يساوي ترتيب التنفيذ.</td></tr>
<tr><td dir="ltr">4</td><td>يرجع بعد اكتمال الاثنين.</td><td><code dir="ltr">ProfileCard("Ada", 2)</code>.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">اختبار <code dir="ltr">CompletableDeferred</code> يثبت إن النتيجة لا تكتمل بعد profile وحدها، ثم تكتمل بعد badges. الاختبار بيستخدم <code dir="ltr">StandardTestDispatcher(testScheduler)</code> و<code dir="ltr">runCurrent()</code> عشان يتحكم في الشغل الجاهز من غير <code dir="ltr">Thread.sleep</code>. ده إثبات لسلوك المعمل المحدد؛ ترتيب thread names أو مكسب السرعة مش جزء من الاختبار.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط شائع:</strong> تعمل <code dir="ltr">GlobalScope.launch</code> من repository وتسيب caller يرجع. ساعتها مالك الطلب مش واضح، والـ UI ممكن تنتهي والطلب يفضل شغال أو يرجع متأخر. وغلط تاني إنك تحط blocking I/O في <code dir="ltr">suspend fun</code> وتظن إن الكلمة وحدها نقلته من main thread.</p>

```kotlin
// Conceptual anti-pattern, intentionally not compiled in the lab:
fun refresh() {
    GlobalScope.launch { blockingRead(); publishToScreen() }
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> خلّي صاحب العمر يطلق coroutine في scope مملوكة له، وخلي data-layer suspend function آمنة للاستدعاء من main بنقل الجزء الـ blocking إلى dispatcher مناسب مثل <code dir="ltr">Dispatchers.IO</code> أو dispatcher متحقن. المعمل يحقن dispatcher، ويجمع أطفال تحت <code dir="ltr">coroutineScope</code>. في Android، <code dir="ltr">viewModelScope</code> مثال لمالك عمر مناسب لشغل متعلق بالـ ViewModel؛ ده توجيه Android رسمي، لكنه غير مبني هنا بدون SDK. <a dir="ltr" href="https://developer.android.com/kotlin/coroutines/coroutines-best-practices">Android coroutine best practices</a>.</p>

## Boundaries and alternatives

<p dir="rtl" lang="ar">الـ dispatcher مش بديل عن contract بتاع API. لو suspend API نفسها main-safe، قد لا تحتاج <code dir="ltr">withContext(IO)</code> حول كل call؛ لو API blocking فعلًا، انقلها في الطبقة المالكة لها. <code dir="ltr">Dispatchers.Default</code> مناسب عادةً لحساب CPU، و<code dir="ltr">Dispatchers.IO</code> لعمل blocking I/O؛ ما تقيسش الأداء من الاسم فقط. Android main dispatcher يتوفر بتكامل Android coroutines، والمشروع ده JVM مستقل من غير main UI loop. <a dir="ltr" href="https://developer.android.com/kotlin/coroutines">Android coroutines guide</a>.</p>

<p dir="rtl" lang="ar">إضافة <code dir="ltr">suspend</code> على function synchronous لا تجعلها automatically concurrent؛ هي تسمح باستدعاء suspend functions. <code dir="ltr">async</code> مناسب لما نتيجتين مستقلتين مطلوبتين؛ لو الثانية تعتمد على الأولى، التسلسل أوضح. لو المطلوب عزل فشل طفل بحيث لا يلغي الآخر، ده عقد supervision مختلف في COR-002، ولا تغيره خفية هنا. استخدام <code dir="ltr">runBlocking</code> في production UI ممكن يوقف main thread؛ في الاختبارات نستخدم <code dir="ltr">runTest</code> وجدولة متحكم فيها.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">ثلاثة اختبارات JUnit تثبت: parent ينتظر المصدرين، خطأ الطفل يظهر بدل card ناقصة، وإلغاء parent ينفذ <code dir="ltr">finally</code> في الطفلين المعلقين. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> داخل معمل JVM وراجع <a dir="ltr" href="../BUILD-VERIFICATION.md">دليل البناء</a>. dependency المحققة محليًا هي <code dir="ltr">kotlinx-coroutines-core/test 1.11.0</code> مع Kotlin 2.4.20 وJDK 17؛ ده لا يثبت compatibility لـ Android plugin أو جهاز.</p>

<p dir="rtl" lang="ar">حالات لازم تتفحص قبل production: مصدر يتجاهل cancellation لأنه blocking؛ مورد لازم يتقفل في <code dir="ltr">finally</code>؛ response قديمة تصل بعد اختيار جديد؛ double refresh؛ exception logging عند owner؛ والفرق بين إلغاء الشاشة وإلغاء ViewModel. اختبارات المعمل لا تشغّل Android lifecycle ولا network حقيقية. لو فشل طفل قبل ما التاني يبدأ، مسار cleanup مختلف عن إلغاء طفل بدأ فعلًا؛ اختبار الإلغاء هنا يبدأ الاثنين قبل الإلغاء.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> <code dir="ltr">suspend</code> تسمح للشغل يقف ويكمل من غير حجز thread أثناء suspension، لكنها مش تصريح إن الكود بيشتغل في الخلفية. الـ dispatcher يحدد التنفيذ، والـ scope تحدد الملكية والعمر. في مثال card، الاتنين <code dir="ltr">async</code> أطفال للـ caller؛ parent ينتظرهم، وفشل أو إلغاء parent يتحرك عبر الشجرة. اختبرنا ده بجدولة قابلة للتحكم بدل sleep.</p>

**English, about 20 seconds:** “Suspend does not move work to a background thread by itself. I use a dispatcher at the blocking boundary and keep child tasks in a caller-owned scope, so completion and cancellation have a clear parent.”

**English, about 60–90 seconds:** “A suspending function may pause without blocking a thread at suspension points, but synchronous blocking code remains blocking. In our profile card loader, two independent reads run as async children inside coroutineScope on an injected dispatcher. The parent returns only when both values are ready; a child failure propagates instead of producing a partial card, and parent cancellation reaches waiting children. Tests use a controlled scheduler and CompletableDeferred gates, so they assert behavior rather than wall-clock timing. In Android I would use a lifecycle-appropriate scope such as viewModelScope for ViewModel work and keep blocking data calls main-safe at the data layer. That Android integration still needs an SDK build and lifecycle test.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل <code dir="ltr">suspend</code> معناها background thread؟</strong> لأ. هي contract للـ suspension؛ thread/dispatcher تحددهما context والـ API اللي ناديتها.</li>
<li><strong>ليه <code dir="ltr">coroutineScope</code> داخل <code dir="ltr">withContext</code>؟</strong> عشان ownership والانتظار واضحين في المثال. <code dir="ltr">withContext</code> نفسها structured block، لكن النطاق الصريح يوضّح إن الـ <code dir="ltr">async</code> أطفال لنفس العملية.</li>
<li><strong>هل cancellation توقف blocking I/O فورًا؟</strong> لأ بالضرورة؛ الـ API لازم تتعاون مع cancellation أو توفر طريقة لإلغاء العمل الفعلي. ده يحتاج اختبار تكامل مناسب.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“أي <code dir="ltr">suspend fun</code> asynchronous.” غلط: ممكن تكمل synchronously لحد suspension أو تعمل blocking call.</li>
<li>“<code dir="ltr">await()</code> الأول يجعل العملية الأولى تبدأ قبل الثانية.” غلط: الاثنين بدأوا عند <code dir="ltr">async</code>؛ ترتيب الانتظار مش ترتيب التشغيل.</li>
<li>“<code dir="ltr">GlobalScope</code> مناسب لكل refresh.” غلط: يقطع ملكية الطلب عن الشاشة أو caller.</li>
<li>“اختبار scheduler يثبت UI lifecycle.” غلط: يثبت سلوك pure JVM هنا فقط.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات سريعة:</strong> هل ترجع card بعد أول source؟ لأ. هل إلغاء parent يصل للأطفال المعلقين؟ نعم في الاختبار. هل <code dir="ltr">runBlocking</code> مناسب على Android main thread؟ لأ في المسار العادي لأنه يحجز thread. راجع <a dir="ltr" href="../Flashcards-Revision/COR-001.md">البطاقات</a> وحل <a dir="ltr" href="../Real-World-Scenarios/SCN-005-orphan-refresh.md">السيناريو</a>.</p>

**Evidence limit:** The local Kotlin/JVM tests exercise coroutine behavior with version 1.11.0 and a controlled test dispatcher. Android scope/lifecycle guidance is sourced to Android Developers but not compiled or observed on a device here.
