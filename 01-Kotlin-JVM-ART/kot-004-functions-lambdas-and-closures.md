---
id: KOT-004
title: Functions, lambdas and closures
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-002]
learning_outcomes:
  - Distinguish a function declaration, function value, lambda, and local function
  - Trace capture of a mutable binding versus a fixed snapshot
  - Choose when a callback should read current state and when it should preserve an event value
  - Explain higher-order function boundaries, Java SAM interop, and callback failure behavior
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/functions.html
  - https://kotlinlang.org/docs/lambdas.html
  - https://kotlinlang.org/docs/java-interop.html
  - https://kotlinlang.org/docs/inline-functions.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/DeferredRequest.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt
question_ids: [KOT-Q016, KOT-Q017, KOT-Q018, KOT-Q019, KOT-Q020]
---

# KOT-004 — Functions, lambdas and closures

**Starting point:** [KOT-002](kot-002-val-var-types-equality-and-identity.md) distinguished a binding from the object it references. Today a function can carry references to values beyond its creation point. Day 3's constructor material is the chronological [previous lesson](kot-003-classes-constructors-initialization-order.md), but its details are not a conceptual prerequisite here.

**Two-hour route:** 55 minutes lesson and trace, 20 minutes guided [questions and visible answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes [LAB-004](../Coding-Challenges/LAB-004-deferred-profile-request.md), 10 minutes [revision](../Flashcards-Revision/KOT-004.md), and optional 10-minute [English speaking](../Speaking-Shadowing/DAY-04.md). Nothing is scored unless the learner later opts in.

## Mental model

<p dir="rtl" lang="ar">الـ function وصف لشغل بيتنفذ لما حد يناديها. لما تبعتها كقيمة، تقدر تخلي قرار التنفيذ عند caller تاني. الـ lambda طريقة مختصرة لكتابة function value. الـ closure معناها إن function اتعملت في مكان وقدرت تستخدم متغيرات من النطاق الخارجي حتى بعد ما تخرج من المكان ده. السؤال المهم في Android callbacks: هل عايز قيمة وقت إنشاء الـ callback، ولا أحدث قيمة وقت تشغيلها؟ الإجابتين صح حسب العقد؛ الغلط إنك تخلطهم من غير قصد. <a dir="ltr" href="https://kotlinlang.org/docs/functions.html">Kotlin functions</a>، <a dir="ltr" href="https://kotlinlang.org/docs/lambdas.html">Lambdas</a> (اتراجعوا 2026-10-10).</p>

<ul dir="rtl" lang="ar">
<li><code dir="ltr">fun normalize(id: String): String</code> declaration باسم ونوع رجوع واضح.</li>
<li><code dir="ltr">val action: (String) -&gt; Unit = { id -&gt; println(id) }</code> function value نوعها يستقبل <code dir="ltr">String</code> ويرجع <code dir="ltr">Unit</code>.</li>
<li><code dir="ltr">fun retryLater(block: () -&gt; Unit)</code> higher-order function لأنها تستقبل function.</li>
<li><code dir="ltr">fun localCheck(...)</code> داخل function تانية تقدر تخفي تفاصيل helper وتستخدم قيم outer scope.</li>
</ul>

## Mechanism and execution trace

<p dir="rtl" lang="ar">في Kotlin parameters بتاعة function read-only داخل body؛ لو مرّرت object قابل للتعديل، المرجع اتنسخ لكن الاتنين يشاوروا لنفس object. الـ closure اللي تمسك <code dir="ltr">var</code> local تقدر تشوف قيمتها بعد reassignment، بينما <code dir="ltr">val snapshot = current</code> جوه factory يثبت قيمة اللحظة دي. ده مش snapshot متزامن بين threads؛ التزامن والـ lifecycle محتاجين آلية مستقلة. <a dir="ltr" href="https://kotlinlang.org/docs/functions.html">Function parameters and local functions</a>، <a dir="ltr" href="https://kotlinlang.org/docs/lambdas.html">Closure examples</a>.</p>

```kotlin
var current = "old"
val snapshot = current
val fixed: () -> String = { snapshot }
val live: () -> String = { current }
current = "new"
println(fixed()) // old
println(live())  // new
```

<table dir="rtl" lang="ar">
<thead><tr><th>الخطوة</th><th>حالة الربط</th><th>النتيجة</th></tr></thead>
<tbody>
<tr><td dir="ltr">1</td><td><code dir="ltr">current = "old"</code></td><td>القيمة الحالية قديمة.</td></tr>
<tr><td dir="ltr">2</td><td><code dir="ltr">snapshot</code> تاخد النص الحالي.</td><td>النص <code dir="ltr">"old"</code> محفوظ في binding منفصلة.</td></tr>
<tr><td dir="ltr">3</td><td><code dir="ltr">fixed</code> تستخدم <code dir="ltr">snapshot</code>، و<code dir="ltr">live</code> تستخدم <code dir="ltr">current</code>.</td><td>لسه مفيش lambda اتنفذت.</td></tr>
<tr><td dir="ltr">4</td><td><code dir="ltr">current = "new"</code>.</td><td>إعادة الربط تغير ما تراه <code dir="ltr">live</code>.</td></tr>
<tr><td dir="ltr">5</td><td>استدعاء الاثنين.</td><td dir="ltr"><code dir="ltr">fixed() = "old"; live() = "new"</code></td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">الـ compiler ممكن يولّد تمثيل مختلف للـ closure حسب target والتحسين؛ لا تعتمد على شكل object أو تخصيص ذاكرة معين إلا بعد قياس. العقد اللي يهمنا هنا: المتغير المتاح للـ lambda عند الاستدعاء، ووقت تنفيذ body، مش bytecode بعينه. <code dir="ltr">inline</code> أداة لها قواعد non-local return و<code dir="ltr">noinline/crossinline</code> وتكلفة code size؛ ما تضفهاش لمجرد إن lambda موجودة من غير حاجة موثقة أو قياس. <a dir="ltr" href="https://kotlinlang.org/docs/inline-functions.html">Kotlin inline functions</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>الحالة الواقعية:</strong> شاشة profile بتحضّر callback لـ زر إعادة تحميل. المستخدم ممكن يغيّر profile قبل ما يضغط. لو المطلوب أحدث profile وقت الضغط، التقاط ID وقت إنشاء الـ callback غلط. لو المطلوب إرسال event للـ profile اللي كان ظاهر وقت إنشاء العنصر، snapshot ممكن تكون صح؛ اكتب العقد قبل الاختيار.</p>

```kotlin
// Wrong for a "reload current profile" button:
val idAtSetup = currentProfileId
val reload = { repository.load(idAtSetup) }
```

<p dir="rtl" lang="ar">المقتطف ده conceptual Android-style؛ <code dir="ltr">repository</code> وstate مش موجودين في المعمل، فمش بندّعي إنه اتبنى. لو <code dir="ltr">currentProfileId</code> اتغيّر، الزر يطلب ID قديم. التصحيح القابل للتشغيل هو <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/DeferredRequest.kt">createDeferredProfileRequest</a>: تستقبل provider function، ولا تقراها وقت إنشاء callback؛ كل invocation تقرا قيمة واحدة، تعمل <code dir="ltr">trim</code>، وتتجنب إرسال null/blank. الاستثناء من <code dir="ltr">request</code> يمرّ للـ caller بدل تحويله بصمت إلى <code dir="ltr">false</code>.</p>

```kotlin
var selected: String? = "old"
val sent = mutableListOf<String>()
val reload = createDeferredProfileRequest({ selected }, { sent.add(it) })
selected = "new"
reload() // true; sent == ["new"]
```

<p dir="rtl" lang="ar">الترتيب: factory ترجع lambda من غير قراءة provider؛ بعد تغيير <code dir="ltr">selected</code>، الاستدعاء يقرأ <code dir="ltr">"new"</code> مرة واحدة، يمرره لـ <code dir="ltr">request</code> ويرجع true. لو القيمة null/blank، لا تنادي <code dir="ltr">request</code> وترجع false. لو request رمت exception، ما فيش try/catch يخفيها. الـ bool هنا معناها إن الطلب اتسلّم للـ callback، <strong>مش</strong> إن network نجحت. ده مثال synchronous فقط؛ Android lifecycle/cancellation ومسارات async مخططة في <a dir="ltr" href="../STUDY-SCHEDULE-48-DAYS.md">COR-001</a> لاحقًا.</p>

## Boundaries and alternatives

<p dir="rtl" lang="ar">لو عايز فعلًا قيمة وقت الحدث، خُد <code dir="ltr">val eventId = currentProfileId</code> عند الحدث ومرّرها؛ ما تقراش global state بعد تأخير طويل. لو المطلوب الأحدث وقت التنفيذ، provider مناسبة لكن لازم تعرف مين يملكها وهل قراءتها thread-safe. function reference مثل <code dir="ltr">::normalize</code> مفيدة لما التوقيع يطابق المطلوب. trailing lambda syntax تغيّر شكل النداء فقط، مش وقت التنفيذ؛ الـ higher-order function نفسها ممكن تنادي callback فورًا أو تخزنها. اقرأ عقدها. <a dir="ltr" href="https://kotlinlang.org/docs/lambdas.html">Higher-order functions and lambdas</a>.</p>

<p dir="rtl" lang="ar">Kotlin تقدر تستخدم Java SAM interfaces مع lambdas عند التوافق، لكن Java API ممكن تعمل callback على thread مختلف أو تحتفظ بيه أطول من Activity. لا تفترض إن syntax المختصرة تحدد thread أو lifecycle. في Android، سجل callback عند owner واضح وفك التسجيل لما ينتهي، وما تحتفظش بمرجع Activity داخل singleton بلا سبب. دي قواعد تصميم مرتبطة بعقد الـ API؛ المعمل الحالي JVM فقط ولا يختبر leak أو lifecycle. <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Java interoperability</a>.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">ستة اختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt">JUnit</a> تثبت: factory لا تقرأ provider ولا ترسل؛ invocation تقرأ أحدث ID؛ null/blank لا ترسل؛ trimming؛ كل invocation تقرأ مرة جديدة؛ وفشل request لا يتحول إلى false. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> من معمل JVM، وشوف <a dir="ltr" href="../BUILD-VERIFICATION.md">دليل البناء</a>. الاختبارات لا تثبت سلامة threads، ترتيب network responses، أو cancellation؛ دي موضوعات COR-001 وما بعده.</p>

<p dir="rtl" lang="ar">حالات إضافية قبل production: provider ترمي exception، current state تتغير أثناء تنفيذ request، callback تتسجل مرتين، owner ينتهي قبل الاستدعاء، وطلب قديم يرجع بعد طلب جديد. الحل الحالي يعالج snapshot/stale selection عند لحظة الاستدعاء فقط، وما يمنعش stale response أو تسريب callback محتجزة.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـ lambda function value، والـ closure بتخليها تستخدم متغيرات من براها. لو خدت <code dir="ltr">val snapshot</code> قبل إنشاء callback، هتشتغل على قيمة ثابتة. لو callback بتقرأ provider وقت النداء، هتشوف القيمة الحالية. أختار على حسب معنى الحدث، وأختبر التوقيت والحالات الغلط. الـ callback لو اتبعتت لـ Java أو Android API لازم أعرف مين محتفظ بيها، إمتى هتتنده، وعلى أي thread.</p>

**English, about 20 seconds:** “A lambda can capture values from its surrounding scope. I decide whether the callback should retain an event-time snapshot or read current state when invoked. I test that timing and keep lifecycle and threading ownership explicit.”

**English, about 60–90 seconds:** “A higher-order function accepts or returns a function value. A closure can use a value from its outer scope, so moving a read across the callback boundary changes behavior. In our reload example, capturing a profile ID while the button is created can send a stale ID after selection changes. The corrected callback reads one current ID per invocation, validates it, and delegates. That does not guarantee network success, avoid out-of-order responses, or make the state thread-safe. For an event that must preserve the original identity, I would intentionally capture a snapshot instead. With a Java or Android callback API, I inspect invocation timing, thread and lifetime before registering it.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل trailing lambda معناها async؟</strong> لأ. شكل النداء منفصل عن توقيت التنفيذ؛ higher-order function ممكن تنادي الـ lambda فورًا أو تخزنها. اقرأ التنفيذ والعقد. <a dir="ltr" href="https://kotlinlang.org/docs/lambdas.html">Lambdas</a>.</li>
<li><strong>هل provider الحالية تمنع race لو state بتتغير من thread تاني؟</strong> لأ. هي بتعمل قراءة واحدة عند invocation، لكن ملكية state والتزامن والـ stale response محتاجين تصميم واختبارات مستقلة.</li>
<li><strong>هل <code dir="ltr">inline</code> يخلي كل callback أسرع تلقائيًا؟</strong> لأ. قد يزيل بعض allocations/call overhead عند استعمال مناسب، لكن له قيود وتكلفة code size؛ ما فيش benchmark هنا. <a dir="ltr" href="https://kotlinlang.org/docs/inline-functions.html">Inline functions</a>.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“الـ lambda بتتنفذ أول ما تتكتب.” غلط: التنفيذ وقت invocation حسب الـ caller.</li>
<li>“closure دايمًا بتاخد snapshot للـ var.” غلط: المثال يفرق بين captured binding وsnapshot منفصلة.</li>
<li>“قراءة ID الحالي تمنع أي stale data.” غلط: رجوع network out of order محتاج request ownership أو generation guard.</li>
<li>“function parameter ممكن أعيد إسناده.” غلط: parameter read-only داخل body، لكن object mutable ممكن يتعدل.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات سريعة:</strong> <code dir="ltr">fixed()</code> بعد التغيير ترجع <code dir="ltr">"old"</code>، و<code dir="ltr">live()</code> ترجع <code dir="ltr">"new"</code>. هل <code dir="ltr">reload()</code> ترجع true لو request نجحت على الشبكة؟ <strong>لأ، معناها callback اتنادت بس.</strong> راجع <a dir="ltr" href="../Flashcards-Revision/KOT-004.md">البطاقات</a> بكرة وأيام 7 و14 و30 حسب الحاجة، وحل <a dir="ltr" href="../Real-World-Scenarios/SCN-004-stale-profile-callback.md">السيناريو</a> بعد trace المعمل.</p>

**Evidence limit:** Kotlin 2.4.20/JDK 17 tests verify the synchronous callback example. The Android callback sketch is conceptual. No coroutine dispatcher, lifecycle, real network, benchmark or Java SAM adapter is executed in this unit.
