---
id: KOT-003
title: Classes, constructors, initialization order
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-002]
learning_outcomes:
  - Trace primary and secondary constructor initialization in source order
  - Distinguish constructor parameters from stored properties
  - Preserve invariants using init blocks and controlled factories
  - Explain why open-member calls during base-class construction are unsafe
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/classes.html
  - https://kotlinlang.org/docs/inheritance.html
  - https://kotlinlang.org/docs/visibility-modifiers.html
  - https://kotlinlang.org/docs/properties.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/Construction.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt
question_ids: [KOT-Q011, KOT-Q012, KOT-Q013, KOT-Q014, KOT-Q015]
---

# KOT-003 — Classes, constructors, initialization order

**Prerequisite:** [KOT-002](kot-002-val-var-types-equality-and-identity.md) explained a binding versus an object and why a generated data-class copy can share state. Today asks when a newly allocated object's fields become safe to use. You need basic Kotlin functions and nullable types from [KOT-001](KOT-001-nullability-java-boundary.md); no Android SDK is required.

**Two-hour path:** 55 minutes this lesson, 20 minutes trace with [Construction.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/Construction.kt), 25 minutes [LAB-003](../Coding-Challenges/LAB-003-construction-boundary.md), 10 minutes [question answers](../Interview-Question-Bank/BY-TOPIC.md), and optional 10-minute [English practice](../Speaking-Shadowing/DAY-03.md). This is study, not a timed assessment.

## Mental model

<p dir="rtl" lang="ar">الكائن وهو بيتعمل مش بيظهر كامل فجأة. الـ constructor الأساسي يستقبل inputs، وبعدها property initializers وكتل <code dir="ltr">init</code> تشتغل بترتيب ظهورها في جسم الـ class. الـ secondary constructor لازم يمرّ على الأساسي الأول؛ جسمه يشتغل بعد ما التهيئة الأساسية تخلص. لو أي خطوة رمت exception، ما تعتمدش على الخطوات اللي بعدها. عشان كده validation جوه <code dir="ltr">init</code> أو factory لازم تحصل قبل نشر الكائن لباقي التطبيق. <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Kotlin classes</a> (اتراجع 2026-10-10).</p>

<p dir="rtl" lang="ar">اربطها بـ Android بشكل عملي: repository يبني إعدادات اتصال أو domain model من رد خارجي. لو constructor سمح بـ host فاضي أو port خارج المدى، باقي الطبقات هتضطر تفحص كل مرة. الـ class تقدر تحافظ على invariant، لكن factory اللي بترجع <code dir="ltr">null</code> أو typed result أحسن للمدخلات المتوقع تكون غلط. مثال المعمل desktop JVM، مش Android network implementation.</p>

## Precise terms and mechanism

<ul dir="rtl" lang="ar">
<li><strong>Primary constructor:</strong> في header بتاع الـ class. <code dir="ltr">class User(val id: String, name: String)</code> يخزّن <code dir="ltr">id</code> كـ property؛ <code dir="ltr">name</code> parameter عادي، لازم تعيّنه لـ property لو محتاجه بعد التهيئة. <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Classes</a>.</li>
<li><strong>Property initializer و<code dir="ltr">init</code>:</strong> بيتنفذوا بترتيبهم في body أثناء إنشاء الكائن. ممكن تستخدم <code dir="ltr">require</code> لعقد يعتبر input غير صالح خطأ عند construction. <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Classes</a>.</li>
<li><strong>Secondary constructor:</strong> لازم يفوض للـ primary constructor مباشرة أو عبر secondary آخر. الـ primary property initializers و<code dir="ltr">init</code> يحصلوا قبل body بتاع secondary. <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Classes</a>.</li>
<li><strong>Visibility:</strong> الـ constructor افتراضيًا public. <code dir="ltr">class X private constructor(...)</code> بيقيد مسار الإنشاء، و<code dir="ltr">internal</code> معناه نطاق module مش package. راجع generated members أو serializers قبل افتراض إن إخفاء constructor وحده يقفل كل مسار. <a dir="ltr" href="https://kotlinlang.org/docs/visibility-modifiers.html">Visibility modifiers</a>.</li>
</ul>

<p dir="rtl" lang="ar">Kotlin classes افتراضيًا <code dir="ltr">final</code>، والوراثة محتاجة <code dir="ltr">open</code> أو نوع abstract/interface. أثناء إنشاء subclass، تهيئة الـ base بتحصل قبل تهيئة الـ derived. استدعاء <code dir="ltr">open</code> method/property من base constructor أو <code dir="ltr">init</code> ممكن يدخل override في subclass قبل ما fields بتاعتها تجهز. دي مشكلة ترتيب، مش مجرد nullability annotation ناقصة. <a dir="ltr" href="https://kotlinlang.org/docs/inheritance.html">Kotlin inheritance</a> (اتراجع 2026-10-10).</p>

## Step-by-step execution trace

<p dir="rtl" lang="ar">ده مقتطف من المعمل القابل للتشغيل. <code dir="ltr">events</code> mutable list بنحقنها فقط عشان نشوف الترتيب في الاختبار، مش pattern لتسريب state من constructor إنتاجي.</p>

```kotlin
class ConstructionTimeline(raw: String, private val events: MutableList<String>) {
    private val normalized = raw.trim().also { events += "property:$it" }
    init {
        events += "init"
        require(normalized.isNotEmpty())
    }
    val label = normalized.uppercase().also { events += "label:$it" }
    constructor(raw: String, events: MutableList<String>, prefix: String) : this(raw, events) {
        events += "secondary:$prefix"
    }
}
```

<table dir="rtl" lang="ar">
<thead><tr><th>ترتيب</th><th>عند <code dir="ltr">ConstructionTimeline(" Ada ", events, "member")</code></th><th>الأثر</th></tr></thead>
<tbody>
<tr><td dir="ltr">1</td><td>الـ secondary يفوض للـ primary.</td><td>لسه body بتاع secondary ما اشتغلش.</td></tr>
<tr><td dir="ltr">2</td><td><code dir="ltr">normalized</code> initializer ينفذ.</td><td dir="ltr"><code dir="ltr">property:Ada</code></td></tr>
<tr><td dir="ltr">3</td><td><code dir="ltr">init</code> يفحص القيمة.</td><td dir="ltr"><code dir="ltr">init</code></td></tr>
<tr><td dir="ltr">4</td><td><code dir="ltr">label</code> initializer ينفذ.</td><td dir="ltr"><code dir="ltr">label:ADA</code></td></tr>
<tr><td dir="ltr">5</td><td>body بتاع secondary ينفذ.</td><td dir="ltr"><code dir="ltr">secondary:member</code></td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">لو <code dir="ltr">raw = "   "</code>، أول خطوة تسجل <code dir="ltr">property:</code>، وبعدها <code dir="ltr">init</code> تسجل نفسها ثم <code dir="ltr">require</code> ترمي <code dir="ltr">IllegalArgumentException</code>. لا <code dir="ltr">label</code> ولا secondary body بيتنفذوا. الستة اختبارات في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt">ConstructionTest.kt</a> بتثبت الترتيب والحالات الغلط للنسخة دي؛ تفاصيل heap/bytecode خارج عقد المثال.</p>

## Beginner example, wrong implementation, corrected implementation

<p dir="rtl" lang="ar"><strong>الحد الأدنى:</strong> لو كل المطلوب تخزين ID، <code dir="ltr">class Task(val id: String)</code> كفاية. من غير <code dir="ltr">val</code> أو <code dir="ltr">var</code> في header، الـ parameter مش property متاحة من خارج الـ class. ما تفتحش secondary constructors لمجرد تقليد Java؛ default arguments أو factory ممكن يكونوا أوضح حسب العقد.</p>

```kotlin
// Wrong: the base constructor dispatches to an override before the derived field is initialized.
open class Base {
    init { checkReady() }
    open fun checkReady() {}
}
class Derived : Base() {
    private val token = "ready"
    override fun checkReady() { require(token.length == 5) }
}
```

<p dir="rtl" lang="ar">الـ <code dir="ltr">Base.init</code> بيستدعي method قابلة للـ override. التنفيذ الديناميكي يروح لـ <code dir="ltr">Derived.checkReady()</code> قبل ما initializer بتاع <code dir="ltr">token</code> يشتغل؛ على JVM ممكن تشوف failure بسبب قيمة غير مهيأة. ما تعتمدش على exception type أو قيم default داخل subclass كعقد تصميم. تجنب استدعاء أعضاء <code dir="ltr">open</code> في base construction؛ مرّر البيانات المطلوبة كـ constructor parameters واستعمل منطق private/final لتهيئة base، وبعد اكتمال الإنشاء شغّل behavior متعدد الأشكال. <a dir="ltr" href="https://kotlinlang.org/docs/inheritance.html">Derived-class initialization order</a>.</p>

<p dir="rtl" lang="ar"><strong>التصحيح الإنتاجي في المعمل:</strong> <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/Construction.kt">EndpointConfig</a> class عادية بـ private constructor و<code dir="ltr">init</code> يحمي host/port. <code dir="ltr">parse</code> تنظف input متوقع يكون غير صالح وترجع null بدل ما ترمي. الـ constructor نفسه يعيد فحص invariant كخط دفاع لو مسار إنشاء آخر اتضاف لاحقًا. ده قرار مناسب لـ demo configuration؛ لو محتاج تميّز سبب فشل host من port استخدم sealed result أو typed error بدل null.</p>

```kotlin
val valid = EndpointConfig.parse(" example.test ", 443)
val absent = EndpointConfig.parse(null, 443)
// valid?.authority() == "example.test:443"; absent == null
```

## Boundaries, alternatives, and Android relevance

<p dir="rtl" lang="ar"><code dir="ltr">init { require(...) }</code> مناسب لما construction بمدخل غير صالح يعتبر bug في caller. عند network/DB/SDK boundary، فشل validation المتوقع محتاج نتيجة صريحة بدل crash متعمد. الـ factory تمنع نشر object غير صالح، لكن مش ضمان ضد reflection أو deserialization غير متحكم فيه. <code dir="ltr">private constructor</code> ينظم الـ API وقت الـ compile؛ اختبر أي library بتنشئ objects بالانعكاس أو بتتجاوز factories. <a dir="ltr" href="https://kotlinlang.org/docs/visibility-modifiers.html">Visibility</a>، <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Constructors</a>.</p>

<p dir="rtl" lang="ar">في Android مثلًا، ViewModel ممكن تستقبل config من saved state أو repository. كون الـ class اتعمل بنجاح لا يثبت إن host متاح على الشبكة، ولا إن saved state حديثة، ولا إن port مسموح بسياسة التطبيق. validation هنا تتحقق من شكل القيمة فقط. لا تستدعي APIs تتطلب lifecycle أو context من constructor domain object؛ خليك صريح في مالك الـ side effect. المعمل JVM فقط، ومفيش build لجهاز Android.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">الاختبارات بتغطي primary وsecondary traces، إن exception في <code dir="ltr">init</code> توقف التهيئة اللاحقة، وfactory بترفض null/blank host وports خارج <code dir="ltr">1..65535</code>، وبتعمل trim لقيمة صالحة. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> من مجلد <code dir="ltr">projects/kotlin-jvm-labs</code>، وشوف الدليل الفعلي في <a dir="ltr" href="../BUILD-VERIFICATION.md">BUILD-VERIFICATION</a>. الاختبارات ما تغطيش Android process death أو deserialization أو subclass unsafe sketch؛ الأخير مثال تحليلي مقصود، مش كود معتمد.</p>

<p dir="rtl" lang="ar">اسأل عن edge cases قبل توسيع المثال: هل ID فاضي بعد trim؟ هل port صفر أو أكبر من 65535؟ هل الـ secondary constructor ممكن يكرر validation؟ هل property initializer لاحقة نفذت بعد exception؟ وهل قاعدة host تحتاج فحص DNS أو URI parsing بدل مجرد <code dir="ltr">isNotBlank()</code>؟ ما تخلطش صحة الصيغة مع إمكانية الاتصال الحقيقي.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة بالمصري:</strong> الـ primary constructor يبدأ التهيئة، وproperty initializers مع <code dir="ltr">init</code> بيتنفذوا بترتيبهم المكتوب. secondary constructor يفوض للأول قبل body بتاعه. أستخدم <code dir="ltr">init</code> لحماية invariant، وfactory لما input خارجي ممكن يفشل بشكل طبيعي. وفي الوراثة ما أستدعيش <code dir="ltr">open</code> member من base constructor لأن override في subclass ممكن تشتغل قبل fields بتاعتها تجهز.</p>

**English, about 20 seconds:** “Kotlin runs property initializers and init blocks in source order during primary construction. A secondary constructor delegates first, then runs its body. I validate invariants before exposing the object, and I avoid calling overridable methods from base constructors.”

**English, about 60–90 seconds:** “I separate three phases: collecting constructor arguments, initializing the base and current class, and running any secondary-constructor body after delegation. In the sample, normalization runs, then the init block validates, then the label initializer runs; a blank input throws before the later steps. A private constructor plus a parsing factory gives external input a non-throwing failure path while the constructor still protects its invariant. In a hierarchy, base initialization precedes derived initialization, so an open call from a base constructor can dispatch into an override that reads uninitialized derived fields. I keep construction logic final and explicit, and test the actual order and failure branches.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل secondary constructor يقدر يتجاوز <code dir="ltr">init</code>؟</strong> لأ، لازم يفوض للـ primary constructor، وتهيئة الـ primary تخلص قبل body بتاعه. لو <code dir="ltr">init</code> رمت exception، جسم secondary ما يوصلوش التنفيذ. <a dir="ltr" href="https://kotlinlang.org/docs/classes.html">Kotlin classes</a>.</li>
<li><strong>هل <code dir="ltr">private constructor</code> وحده يضمن invariant مع data class؟</strong> مش دايمًا؛ generated <code dir="ltr">copy()</code> وسلوك النسخة المحددة مهم، وكمان serializers/reflection حدود ثقة منفصلة. لو invariant مهم، اختبر كل مسارات الإنشاء أو خليك في class عادية/factory محكمة. ارجع لـ <a dir="ltr" href="KOT-001-nullability-java-boundary.md">KOT-001</a> و<a dir="ltr" href="https://kotlinlang.org/docs/data-classes.html">data classes</a>.</li>
<li><strong>إيه البديل لو نتيجة parse محتاجة سبب الفشل؟</strong> بدل <code dir="ltr">null</code> استخدم sealed outcome أو typed error بفرع لـ host وفرع لـ port. التكلفة API أوسع، لكن caller يقدر يقدّم رسالة دقيقة ويقيس أخطاء الإدخال من غير رمي exception متوقع.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“كل properties تتهيأ قبل أي <code dir="ltr">init</code>.” غلط: property initializers و<code dir="ltr">init</code> يشتغلوا بترتيب ظهورهم.</li>
<li>“secondary body يشتغل الأول وبعدين primary.” غلط: التفويض للـ primary أولًا.</li>
<li>“<code dir="ltr">name: String</code> في constructor دايمًا property.” غلط: محتاج <code dir="ltr">val</code> أو <code dir="ltr">var</code> لتخزينه مباشرة.</li>
<li>“Kotlin null safety تمنع استدعاء override غير مهيأة.” غلط: ترتيب الوراثة ممكن يخلي subclass state غير جاهزة.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات ظاهرة:</strong> ماذا يحدث لو <code dir="ltr">require</code> فشلت في <code dir="ltr">init</code>؟ <strong>الإنشاء يفشل والخطوات التالية لا تنفذ.</strong> هل <code dir="ltr">private constructor</code> مفيدة مع input خارجي؟ <strong>أيوه لتنظيم المسار، ومعاها factory ترجع فشلًا واضحًا.</strong> راجع <a dir="ltr" href="../Flashcards-Revision/KOT-003.md">بطاقات Day 3</a> بكرة وأيام 7 و14 و30 حسب الضعف، واقرأ <a dir="ltr" href="../Real-World-Scenarios/SCN-003-open-constructor-dispatch.md">سيناريو التشخيص</a> لو محتاج تطبيق.</p>

**Evidence limit:** The construction tests use Kotlin 2.4.20 on JDK 17. The unsafe open-member example is a documented hazard and illustrative sketch, not a runtime test of a production class. No Android app, lifecycle, or real network endpoint is tested here.
