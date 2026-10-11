---
id: KOT-002
title: val/var, types, equality and identity
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-001]
learning_outcomes:
  - Distinguish a read-only binding from a mutable object and a read-only collection interface
  - Predict inferred types and choose explicit boundary types when they clarify a contract
  - Trace structural equality, reference identity, and data-class generated members
  - Explain why mutable hash keys and shallow copies can break cache and UI assumptions
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/basic-syntax.html
  - https://kotlinlang.org/docs/properties.html
  - https://kotlinlang.org/docs/equality.html
  - https://kotlinlang.org/docs/data-classes.html
  - https://kotlinlang.org/docs/collections-overview.html
  - https://kotlinlang.org/docs/java-interop.html
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html
  - https://developer.android.com/develop/ui/compose/state
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileSemantics.kt
  - ../projects/kotlin-jvm-labs/src/main/java/academy/LegacyProfileApi.java
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileSemanticsTest.kt
question_ids: [KOT-Q006, KOT-Q007, KOT-Q008, KOT-Q009, KOT-Q010]
---

# KOT-002 — val/var, types, equality and identity

**Before you start:** [KOT-001](KOT-001-nullability-java-boundary.md) established how to make a Java boundary explicit. Today follows one value after that boundary: who can reassign it, who can mutate it, and what equality means when a UI or cache compares it. The [question bank](../Interview-Question-Bank/BY-TOPIC.md) keeps answers visible during Learning Mode.

**Time budget:** 45 minutes lesson and trace, 25 minutes guided questions, 30 minutes [lab](../Coding-Challenges/LAB-002-profile-tags-and-keys.md), and 10 minutes optional revision. [Spoken English practice](../Speaking-Shadowing/DAY-02.md) is an optional extra 10 minutes; it is not an exam.

## Mental model

<p dir="rtl" lang="ar">تخيّل المتغير اسم على ورقة بيدلّك على كائن. <code dir="ltr">val</code> معناها إن الاسم ده ما ينفعش تشير بيه لكائن تاني بعد التهيئة؛ مش وعد إن الكائن نفسه ما بيتغيرش. <code dir="ltr">var</code> بتسمح تعيد ربط الاسم. لو الاسم بيشاور على <code dir="ltr">MutableList</code>، تقدر تضيف للقائمة حتى لو الاسم <code dir="ltr">val</code>. و<code dir="ltr">List</code> في Kotlin واجهة قراءة فقط، مش ضمان إن حد تاني ما معهوش مرجع قابل للتعديل لنفس البيانات. ده فرق مهم لما <span dir="ltr">ViewModel</span> يبعت حالة للواجهة أو لما تخزن مفتاح في cache. <a dir="ltr" href="https://kotlinlang.org/docs/basic-syntax.html">Basic syntax</a>، <a dir="ltr" href="https://kotlinlang.org/docs/collections-overview.html">Collections</a> (اتراجعوا 2026-10-10).</p>

<ul dir="rtl" lang="ar">
<li><strong>ربط الاسم:</strong> <code dir="ltr">val tags = mutableListOf("vip")</code> يمنع <code dir="ltr">tags = otherList</code>، لكن يسمح <code dir="ltr">tags.add("new")</code>.</li>
<li><strong>صلاحية الواجهة:</strong> <code dir="ltr">val visible: List&lt;String&gt; = tags</code> يمنع <code dir="ltr">visible.add(...)</code> من خلال الاسم ده؛ تعديل <code dir="ltr">tags</code> يفضل ظاهر في <code dir="ltr">visible</code>.</li>
<li><strong>لقطة منفصلة:</strong> نسخ العناصر إلى قائمة جديدة يقطع alias القايمة الخارجية وقت النسخ، لكن النسخة سطحية لو العناصر نفسها كائنات قابلة للتعديل.</li>
</ul>

## Mechanism and trace

<p dir="rtl" lang="ar"><strong>الأنواع المستنتجة:</strong> <code dir="ltr">val count = 1</code> نوعها <code dir="ltr">Int</code>؛ كتابة <code dir="ltr">val count: Int = 1</code> مش شرط هنا. لكن النوع المعلن مهم عند boundary: <code dir="ltr">val label: CharSequence = "Ada"</code> يعلن عقد أوسع من <code dir="ltr">String</code>، و<code dir="ltr">val raw: List&lt;String?&gt;? = LegacyProfileApi.tagsFor(id)</code> يعلن صراحة احتمال غياب القائمة أو عنصر فيها لو عقد Java غير موثوق. ما تستنتجش من type inference إن Java ضمنت nullability أو immutability. <a dir="ltr" href="https://kotlinlang.org/docs/basic-syntax.html">Kotlin variables</a>، <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Java interop</a> (اتراجعوا 2026-10-10).</p>

```kotlin
val tags = mutableListOf("vip")
val readOnly: List<String> = tags
tags += "beta"
// readOnly now exposes ["vip", "beta"]; only the readOnly reference is restricted.
```

<p dir="rtl" lang="ar">السطر الأول أنشأ قائمة قابلة للتعديل وربطها باسم <code dir="ltr">val</code>. السطر التاني أنشأ <strong>alias</strong> لنفس القائمة بواجهة قراءة فقط؛ ما نسخش البيانات. السطر التالت عدّل الكائن من خلال المرجع الأول. السطر الرابع وصف النتيجة: القراءة من <code dir="ltr">readOnly</code> تشوف العنصر الجديد. ده سلوك مرجعي، مش bug في الـ compiler. لو القائمة جاية من Java، خُد snapshot عند الحد الفاصل لما العقد يتطلب نتيجة مستقلة. <a dir="ltr" href="https://kotlinlang.org/docs/collections-overview.html">Kotlin collections overview</a>.</p>

<p dir="rtl" lang="ar"><strong>المساواة:</strong> <code dir="ltr">a == b</code> بتسأل عن <code dir="ltr">equals()</code> مع تعامل آمن مع null. <code dir="ltr">a === b</code> بتسأل هل الاتنين نفس المرجع. <code dir="ltr">data class</code> عادة بتولّد <code dir="ltr">equals()</code> و<code dir="ltr">hashCode()</code> من properties اللي في الـ primary constructor. <code dir="ltr">class</code> عادية من غير override تورث مساواة مرجعية من <code dir="ltr">Any</code>. ما تعتمدش على <code dir="ltr">===</code> لمقارنة محتوى <code dir="ltr">String</code> أو قيم boxed؛ هو سؤال هوية، مش بديل أسرع لـ <code dir="ltr">==</code>. للمصفوفات، استخدم <code dir="ltr">contentEquals()</code> لو المطلوب مقارنة العناصر. <a dir="ltr" href="https://kotlinlang.org/docs/equality.html">Kotlin equality</a> (اتراجع 2026-10-10).</p>

```kotlin
data class ProfileKey(val tenantId: String, val profileId: String)

val first = ProfileKey("shop", "p-7")
val second = ProfileKey("shop", "p-7")
val alias = first
println(first == second)  // true: constructor values match
println(first === second) // false: separate objects
println(first === alias)  // true: one object, two references
println(first.hashCode() == second.hashCode()) // true: equal objects must hash alike
```

<table dir="rtl" lang="ar">
<thead><tr><th>السطر</th><th>النتيجة</th><th>ليه؟</th></tr></thead>
<tbody>
<tr><td dir="ltr"><code dir="ltr">first == second</code></td><td dir="ltr"><code dir="ltr">true</code></td><td>الـ <code dir="ltr">data class</code> قارنت <code dir="ltr">tenantId</code> و<code dir="ltr">profileId</code>.</td></tr>
<tr><td dir="ltr"><code dir="ltr">first === second</code></td><td dir="ltr"><code dir="ltr">false</code></td><td>اتعمل إنشاء لكائنين منفصلين؛ النتيجة دي تخص المثال ده.</td></tr>
<tr><td dir="ltr"><code dir="ltr">first === alias</code></td><td dir="ltr"><code dir="ltr">true</code></td><td><code dir="ltr">alias</code> أخد نفس المرجع.</td></tr>
<tr><td dir="ltr"><code dir="ltr">hashCode()</code></td><td dir="ltr"><code dir="ltr">true</code></td><td>عقد المساواة يفرض نفس hash للكائنين المتساويين؛ العكس مش مضمون.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">لو كتبت <code dir="ltr">data class ScreenRow(val id: String) { var selected = false }</code>، الـ <code dir="ltr">selected</code> اللي في جسم الـ class <strong>مش</strong> داخلة في الـ generated <code dir="ltr">equals()</code> أو <code dir="ltr">copy()</code>. صفّين بنفس <code dir="ltr">id</code> وقيم <code dir="ltr">selected</code> مختلفة ممكن يبقوا <code dir="ltr">==</code>. لو الـ UI محتاجة الاختيار جزء من معنى الحالة، حطّه في الـ primary constructor أو عرّف model مختلف. والـ <code dir="ltr">copy()</code> بتاعة data class سطحية: المرجع الداخلي لقائمة قابلة للتعديل ممكن يفضل مشترك. <a dir="ltr" href="https://kotlinlang.org/docs/data-classes.html">Kotlin data classes</a> (اتراجع 2026-10-10).</p>

<p dir="rtl" lang="ar">لو هتكتب <code dir="ltr">equals(other: Any?)</code> بنفسك، لازم تعريف المساواة يفضل منطقيًا reflexive وsymmetric وtransitive، ونفس النتيجة طالما الحقول المستخدمة ما اتغيرتش. الكائنين المتساويين لازم يطلعوا نفس <code dir="ltr">hashCode()</code>؛ كائنين بنفس hash ممكن يكونوا مختلفين. ما تعملش override لـ <code dir="ltr">equals()</code> وتسيب <code dir="ltr">hashCode()</code> بالعقد القديم. دي شروط مهمة لأي <code dir="ltr">Set</code> أو <code dir="ltr">Map</code> مبنيين على hashing. <a dir="ltr" href="https://kotlinlang.org/docs/equality.html">Kotlin equality</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>النسخة الغلط:</strong> بنستخدم object مفتاح cache، وبنغيّر field داخل معنى المساواة بعد الإدخال. المثال للتشخيص، مش pattern للمنتج.</p>

```kotlin
data class MutableKey(var profileId: String)
val key = MutableKey("p-7")
val cache = hashMapOf(key to "profile")
key.profileId = "p-8" // changes generated equals/hashCode while key is in the map
```

<p dir="rtl" lang="ar">ما تقولش إن <code dir="ltr">cache[key]</code> لازم ترجع null في كل تشغيل: عقد <span dir="ltr">Java Map</span> بيقول إن سلوك الـ map <strong>غير محدد</strong> لو مفتاح اتغيّر بطريقة تؤثر على <code dir="ltr">equals</code> وهو جواها. التشخيص الصحيح: سجل قيمة المفتاح وقت الإدخال، راجع أي mutation، واكتب reproducer صغير من غير الاعتماد على نتيجة lookup محددة. <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html">Java SE 17 Map contract</a> (اتراجع 2026-10-10).</p>

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> خُد قيمة هوية ثابتة من الـ boundary، وبعدين استخدم <code dir="ltr">ProfileKey</code> بقيم <code dir="ltr">val</code> ونصوص غير قابلة للتعديل. لو البيانات الداخلة قائمة Java قابلة للتغيير، اعمل snapshot قبل ما تسلّمها للـ UI. المثال القابل للتشغيل في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileSemantics.kt">ProfileSemantics.kt</a>، والـ <a dir="ltr" href="../Coding-Challenges/LAB-002-profile-tags-and-keys.md">challenge</a> بيسيب لك فرصة تنفّذ الفكرة بنفسك.</p>

```kotlin
val raw: List<String?>? = LegacyProfileApi.tagsFor("mona")
val snapshot: List<String> = snapshotLegacyTags(raw)
val cacheKey = ProfileKey(tenantId = "shop", profileId = "p-7")
```

<p dir="rtl" lang="ar">الدالة <code dir="ltr">snapshotLegacyTags</code> تشيل null والعناصر الفاضية بعد <code dir="ltr">trim</code>، وتبني قائمة جديدة؛ تعديل قائمة Java الأصلية بعد الاستلام ما يغيّرش النتيجة المرصودة في المعمل. ده snapshot <strong>سطحي</strong> لعناصر <code dir="ltr">String</code>؛ لو العناصر objects قابلة للتعديل، لازم تحدد سياسة نسخ أعمق. و<code dir="ltr">List</code> لسه read-only interface، مش تعهد عام بـ deep immutability. <a dir="ltr" href="https://kotlinlang.org/docs/collections-overview.html">Collections</a>، <a dir="ltr" href="https://kotlinlang.org/docs/data-classes.html">Data-class copies</a>.</p>

## Android production boundary and alternatives

<p dir="rtl" lang="ar">في شاشة Android افتراضية، repository بيقرأ tags من SDK Java، والـ <span dir="ltr">ViewModel</span> بيكوّن <code dir="ltr">UiState</code>. لو الواجهة مستلمة alias لقائمة قابلة للتعديل واتغيّرت في الخلفية، ممكن تعرض بيانات مختلفة من غير انتقال state واضح. ولو الاختيار <code dir="ltr">selected</code> متساب برّه مساواة الـ state، مقارنة states ممكن ما تلاحظش تغيير مهم. اطلب state value جديد بمحتوى واضح، وخلي تحديثات UI تمر بمسار state الملاحظ في التقنية المستخدمة؛ في Compose، التعديل على <code dir="ltr">ArrayList</code> عادية لوحده مش observable state. ده مثال تصميم إنتاجي محتمل، <strong>مش</strong> Android integration متبنية أو متاختبرة في هذا المعمل. <a dir="ltr" href="https://developer.android.com/develop/ui/compose/state">Android Compose state</a> (اتراجع 2026-10-10).</p>

<p dir="rtl" lang="ar">بدائل القرار حسب العقد: <code dir="ltr">val</code> لمرجع واحد واكتب تحديثات صريحة؛ <code dir="ltr">var</code> لو إعادة الربط نفسها جزء من السلوك؛ <code dir="ltr">MutableList</code> داخل مالك واحد لو التعديل مطلوب؛ <code dir="ltr">List</code> للقراءة مع snapshot عند حدود الثقة. لو قيمة مفتاح cache لازم تتبدل، ابني مفتاح جديد وانقل الإدخال بطريقة محددة، ما تغيّرش مفتاحًا قائمًا. كل اختيار له تكلفة نسخ وملكية؛ المعمل ده ما قاسش أداء ولا استهلاك ذاكرة.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">اختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileSemanticsTest.kt">ProfileSemanticsTest.kt</a> بتغطي فرق المرجع عن المحتوى، عقد hash للـ keys المتساوية، aliasing في <code dir="ltr">copy()</code>، استقلال <code dir="ltr">detachedCopy()</code>، وboundary Java مع null/blank وتعديل القائمة الأصلية. الهدف إثبات سلوك المثال اللي بين أيدينا، مش إثبات إن كل Java SDK بتعمل نفس الشيء. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> من <code dir="ltr">projects/kotlin-jvm-labs</code>؛ سجل النتيجة الفعلية في <a dir="ltr" href="../BUILD-VERIFICATION.md">BUILD-VERIFICATION</a>.</p>

<p dir="rtl" lang="ar">حالات راجعها قبل ما تعتبر الحل مناسب: null من Java، عنصر null، whitespace فقط، القائمة الأصلية بتتغير بعد النسخ، عنصر داخلي mutable بدل <code dir="ltr">String</code>، مفتاح tenant مختلف بنفس profile ID، وdata class فيها property مهمة خارج الـ constructor. المعمل JVM فقط؛ مفيش Android device أو SDK حقيقي داخل دليل الاختبار.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالعامية في المقابلة:</strong> <code dir="ltr">val</code> بتثبت الـ reference مش الكائن. لو معايا <code dir="ltr">MutableList</code> أقدر أغير محتواها، ولو طلّعتها كـ <code dir="ltr">List</code> حد تاني ممكن يكون لسه ماسك mutable alias. <code dir="ltr">==</code> بيمشي على <code dir="ltr">equals</code>، و<code dir="ltr">===</code> بيفحص نفس الكائن. عشان cache key ما يتلخبطش، أخليه قيمة ثابتة لها <code dir="ltr">equals/hashCode</code> متوافقين، وآخد snapshot من Java input قبل ما أنشر state.</p>

**English, about 20 seconds:** “A Kotlin `val` prevents reassignment, but it does not freeze the referenced object. I use `==` for value equality and `===` when I specifically need reference identity. For cache keys and UI state, I prefer stable values and take a snapshot of mutable Java input.”

**English, about 60–90 seconds:** “I separate three questions: can this variable be rebound, can the object be mutated through any alias, and how is equality defined? A `val` holding a mutable list answers only the first question. Kotlin’s read-only `List` interface limits operations through that reference but does not prove the backing object is immutable. A data class derives equality and hashing from primary-constructor properties, and its `copy` is shallow. I therefore keep cache-key fields stable and make a new snapshot when data crosses an untrusted Java or repository boundary. I verify equal keys have equal hashes, show that separate equal objects are not identical, and test source-list mutation after a snapshot. If this were a real Android screen, I would also test the chosen observable state mechanism on the pinned Android stack.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل كل <code dir="ltr">val</code> property مخزنة هي نفس القيمة طول عمر الكائن؟</strong> لأ. <code dir="ltr">val area get() = width * height</code> getter بيتحسب كل قراءة، وممكن يتغير لو <code dir="ltr">width</code> اتغيرت. <code dir="ltr">val</code> يمنع setter للـ property، مش يلزم getter يرجّع قيمة ثابتة. <a dir="ltr" href="https://kotlinlang.org/docs/properties.html">Kotlin properties</a>.</li>
<li><strong>إيه شرط الـ hash المهم، وهل نفس hash يعني objectين متساويين؟</strong> لو <code dir="ltr">a == b</code> لازم <code dir="ltr">a.hashCode() == b.hashCode()</code>. نفس hash وحده مش كفاية؛ collisions ممكنة. ما تغيّرش الحقول الداخلة في المساواة/الـ hash لمفتاح موجود في map. <a dir="ltr" href="https://kotlinlang.org/docs/equality.html">Kotlin equality</a>، <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html">Java Map</a>.</li>
<li><strong>هل <code dir="ltr">data.copy()</code> تعمل deep copy؟</strong> لأ. بتنشئ outer object جديد، لكن property ماسكة mutable list غالبًا تحتفظ بنفس مرجع القائمة. اعمل نسخًا مقصودًا عند حدود الملكية، وفكّر في العناصر المتداخلة كمان. <a dir="ltr" href="https://kotlinlang.org/docs/data-classes.html">Kotlin data classes</a>.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“<code dir="ltr">val</code> يعني immutable object.” غلط: معناها read-only binding/property من ناحية الإسناد، والكائن ممكن يتغير.</li>
<li>“<code dir="ltr">List</code> يعني immutable copy.” غلط: واجهة قراءة فقط وممكن تكون alias لنفس mutable list.</li>
<li>“<code dir="ltr">===</code> أسرع، فاستعملها بدل <code dir="ltr">==</code>.” غلط: معناها مختلف؛ استخدمها فقط لو هوية المرجع هي السؤال.</li>
<li>“كل properties في data class داخلة في <code dir="ltr">equals</code>.” غلط: التوليد الافتراضي بيستخدم primary constructor فقط.</li>
<li>“تعديل cache key يخلي البحث يفشل دايمًا.” غلط: عقد Java Map يترك السلوك غير محدد.</li>
</ul>

<p dir="rtl" lang="ar"><strong>مراجعة سريعة وإجابات ظاهرة:</strong> هل <code dir="ltr">val xs = mutableListOf(1)</code> تسمح <code dir="ltr">xs.add(2)</code>؟ <strong>أيوه.</strong> هل <code dir="ltr">ProfileKey("t", "7") == ProfileKey("t", "7")</code>؟ <strong>أيوه</strong> بقيم constructor نفسها. وهل <code dir="ltr">copy()</code> تنسخ mutable list بعمق؟ <strong>لأ.</strong> كرر trace بكرة، وبعدها تقريبًا أيام 3 و7 و14 و30 لو المفهوم لسه ضعيف. افتح <a dir="ltr" href="../Flashcards-Revision/KOT-002.md">flashcards</a> أو <a dir="ltr" href="../Real-World-Scenarios/SCN-002-mutable-cache-key.md">debugging scenario</a> كتمرين اختياري.</p>

**Evidence limit:** Sources describe language and JDK contracts. The runnable example targets Kotlin 2.4.20/JDK 17, not an Android build. Runtime claims about the lab require the fresh command and XML record in [BUILD-VERIFICATION](../BUILD-VERIFICATION.md); production SDK and UI behavior remain hypotheses until separately tested.
