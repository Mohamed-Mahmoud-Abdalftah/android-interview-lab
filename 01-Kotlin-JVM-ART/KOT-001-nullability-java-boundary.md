---
id: KOT-001
title: Nullability at a Java boundary
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 55
prerequisite_ids: []
learning_outcomes:
  - Distinguish String, String?, and an inferred Java platform type
  - Trace safe calls, Elvis expressions, and smart casts
  - Validate an unannotated Java SDK result at its boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/null-safety.html
  - https://kotlinlang.org/docs/java-interop.html
  - https://kotlinlang.org/docs/typecasts.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt
  - ../projects/kotlin-jvm-labs/src/main/java/academy/LegacyProfileApi.java
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt
question_ids: [KOT-Q001, KOT-Q002, KOT-Q003, KOT-Q004, KOT-Q005]
---

# KOT-001 — Nullability at a Java boundary

**Assumptions:** You can read a Kotlin function and a Java static method. No Android SDK is needed. Start with the [Day 1 lab](../projects/kotlin-jvm-labs/README.md), then read the [worked incident](../Real-World-Scenarios/SCN-001-legacy-profile-null.md). Interview answers are visible from the [question index](../Interview-Question-Bank/BY-TOPIC.md).

## Mental model (مصري)

<p dir="rtl" lang="ar">تخيّل <code dir="ltr">String</code> كعلبة المفروض جواها نص، و<code dir="ltr">String?</code> كعلبة ممكن تبقى فاضية. Kotlin بيجبرك تفحص التانية قبل ما تستخدم النص. إنما لما القيمة جاية من Java API من غير nullability annotations، المترجم مش عارف العقد الحقيقي؛ النوع اللي هتشوفه في الشرح أو الـ IDE هو <code dir="ltr">String!</code>. ده <strong>platform type</strong>، وممكن تتعامل معاه كأنه nullable أو non-nullable، فمسؤولية التحقق عند الحد الفاصل عليك. الـ <code dir="ltr">!</code> وصف من الأدوات، مش syntax تكتبها في Kotlin. <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Kotlin Java interoperability</a> (checked 2026-10-10).</p>

<h2 dir="rtl" lang="ar" id="المصطلحات-الدقيقة-وليه-بتفرق">المصطلحات الدقيقة وليه بتفرق</h2>

<ul dir="rtl" lang="ar">
<li><code dir="ltr">String</code>: إعلان في Kotlin إن القيمة المفروض غير null. الكود العادي في Kotlin مش هيقدر يمرّر null له؛ دي حماية وقت الـ compile، مع استثناءات معروفة عند Java interop أو أخطاء التهيئة.</li>
<li><code dir="ltr">String?</code>: القيمة ممكن تكون null. استدعاء <code dir="ltr">.length</code> عليها مباشرة هيترفض؛ لازم تفحصها، أو تستخدم <code dir="ltr">?.</code>، أو تختار fallback مقصود.</li>
<li><code dir="ltr">String!</code>: نوع <strong>platform type</strong> بيستنتجه Kotlin لما Java ما يكونش موضح nullability بشكل معروف. ممكن يرجع null وقت التشغيل. لو كتبت <code dir="ltr">val raw: String?</code> عند الاستلام، بتخلي عدم اليقين ظاهر في باقي الكود. علامة <code dir="ltr">!</code> للعرض في الـ IDE، مش syntax في ملف Kotlin. <a dir="ltr" href="https://kotlinlang.org/docs/null-safety.html">Kotlin null safety</a>، <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Java interop</a> (اتراجعوا 2026-10-10).</li>
<li><strong>Smart cast</strong>: بعد فحص القيمة، الـ compiler يقدر يتعامل معاها كنوع أضيق لو يقدر يثبت إنها مش هتتغير قبل الاستخدام. ما تفترضش ده مع property قابلة للتغيير أو getter ممكن يرجّع نتيجة مختلفة. <a dir="ltr" href="https://kotlinlang.org/docs/typecasts.html">Kotlin type checks and casts</a> (اتراجع 2026-10-10).</li>
</ul>

<p dir="rtl" lang="ar">عند حدود Java/vendor API أو network أو DB، وضّح <code dir="ltr">nullable</code> صراحة لو العقد مش مضمون. لو غياب القيمة خطأ في الـ domain، ما تنشرش <code dir="ltr">?.</code> في كل الشاشة وتخفي السبب؛ ارفض القيمة وارجع خطأ مفهوم. <code dir="ltr">!!</code> مش علاج لتحذير الـ compiler: استخدمها فقط لو فيه invariant مثبت ومكان الفشل واضح. وكمان nullability لوحدها لا تكتشف نص فاضي، ID غلط، state قديمة، أو رد سيرفر غير صالح.</p>

## Mechanism and trace

<p dir="rtl" lang="ar"><strong>عقد اللغة</strong> بيفرق بين nullable وnon-null؛ وتوثيق Java interop بيقول إن فحص الـ platform type أقل صرامة. <strong>اللي اتلاحظ في المعمل</strong>: <code dir="ltr">Ada</code> للـ ID المعروف و<code dir="ltr">Guest</code> للمفقود. تفاصيل bytecode اللي الـ compiler بيطلّعها implementation detail؛ ما تبنيش صحة الحل على تعليمة بعينها. <a dir="ltr" href="https://kotlinlang.org/docs/null-safety.html">Null safety</a>، <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Java interop</a> (اتراجعوا 2026-10-10).</p>

<p dir="rtl" lang="ar">الأسطر الجاية مقتطف من داخل <code dir="ltr">ProfileName.parse</code>؛ لذلك <code dir="ltr">return ProfileName(normalized)</code> بيستدعي الـ private constructor من داخل الـ class نفسها.</p>

```kotlin
val raw: String? = LegacyProfileApi.nameFor("ada") // Java returns " Ada "
val normalized = raw?.trim()?.takeIf { it.isNotEmpty() } ?: return null
return ProfileName(normalized)
```

<table dir="rtl" lang="ar">
<thead><tr><th>الخطوة</th><th>القيمة / الفرع</th><th>السبب</th></tr></thead>
<tbody>
<tr><td dir="ltr">Java call</td><td dir="ltr"><code dir="ltr">&quot; Ada &quot;</code></td><td>الـ fake SDK بيرجع النص ده.</td></tr>
<tr><td dir="ltr"><code dir="ltr">raw?.trim()</code></td><td dir="ltr"><code dir="ltr">&quot;Ada&quot;</code></td><td>الـ safe call بيشغّل <code dir="ltr">trim</code> لأن <code dir="ltr">raw</code> مش null.</td></tr>
<tr><td dir="ltr"><code dir="ltr">takeIf</code></td><td dir="ltr"><code dir="ltr">&quot;Ada&quot;</code></td><td>النص مش فاضي.</td></tr>
<tr><td dir="ltr">Elvis <code dir="ltr">?:</code></td><td>الفرع الشمال</td><td>فرع <code dir="ltr">return null</code> مش هيتنفذ.</td></tr>
<tr><td dir="ltr">constructor</td><td dir="ltr"><code dir="ltr">ProfileName(&quot;Ada&quot;)</code></td><td>القيمة بعد التحقق دخلت نوع الـ domain.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">مع <code dir="ltr">&quot;missing&quot;</code>، Java بترجع null: أول safe call نتيجتها null، والاستدعاء اللي بعدها مش بيشتغل، وElvis بيخرج من <code dir="ltr">parse</code> بـ null، فـ <code dir="ltr">safeLabelFromLegacy</code> بتختار <code dir="ltr">&quot;Guest&quot;</code>. مع <code dir="ltr">&quot;blank&quot;</code>، <code dir="ltr">trim</code> بتعمل <code dir="ltr">&quot;&quot;</code>، و<code dir="ltr">takeIf</code> بترجع null، فنفس الـ fallback. هنا <code dir="ltr">?: return null</code> بتخرج من <strong>الدالة الحالية</strong>؛ <code dir="ltr">return</code> ينفع يتستخدم كتعبير في Kotlin.</p>

## Beginner example, wrong version, corrected version

<p dir="rtl" lang="ar">ده مثال Kotlin صغير وكامل، بعيد عن Java interop:</p>

```kotlin
fun displayLength(name: String?): Int = name?.length ?: 0
```

<p dir="rtl" lang="ar">المثال الجاي فيه <strong>bug مقصود</strong> وهو مختصر؛ ما تنقلوش للـ production:</p>

```kotlin
fun unsafeLength(id: String): Int = LegacyProfileApi.nameFor(id).length
```

<p dir="rtl" lang="ar">ليه بيفشل؟ ناتج Java من غير annotation هو platform type، فـ Kotlin بيقبل <code dir="ltr">.length</code>. الـ fake Java بيرجع null مع <code dir="ltr">&quot;missing&quot;</code>، وساعتها البرنامج يفشل وقت التشغيل. <code dir="ltr">try/catch (Exception)</code> واسع ويرجع صفر هيخفي عقد SDK مكسور، وممكن يخفي أخطاء تانية. إضافة <code dir="ltr">!!</code> بتنقل الفشل لوقت التشغيل من غير recovery.</p>

<p dir="rtl" lang="ar">في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt">الحل القابل للتشغيل</a> بنستقبل <code dir="ltr">String?</code> صراحة، نرفض النص الفاضي، ونختار UI fallback موثّق. <code dir="ltr">ProfileName</code> constructor بتاعها private، وهي <strong>مش</strong> data class: <code dir="ltr">copy()</code> المتولدة ممكن تتجاوز شرط الـ <code dir="ltr">parse</code> في نسخة Kotlin دي. في مشروع حقيقي، قرر هل الاسم الناقص يستحق fallback ولا validation error ولا data-quality incident. ما تستخدمش UI fallback بصمت لو القيمة هوية مطلوبة في عملية دفع.</p>

## Boundaries and alternatives

<p dir="rtl" lang="ar"><code dir="ltr">raw?.trim()</code> مناسبة لو النص اختياري. لو property ممكن تتغير بين قرايتين، خُد <code dir="ltr">val snapshot = mutableOwner.name</code> وبعدها افحص الـ snapshot. لو الحقل مطلوب، <code dir="ltr">requireNotNull(raw)</code> مناسبة فقط لما الفشل الصريح هو العقد المتفق عليه؛ في input قابل للتعافي typed error أحسن غالبًا. Java annotations بتحسّن المعلومات وقت الـ compile لو عقد الـ vendor صادق والـ compiler بيتعرف عليها. النوع nullable بيتعامل مع الغياب، مش النص الفاضي أو تغيّر state بشكل غير متزامن.</p>

<p dir="rtl" lang="ar">المعمل ده على <strong>desktop JVM</strong>. Android build لاحقًا بيحوّل الكود لـ DEX ويشتغل تحت ART؛ النتيجة هنا ما تثبتش سلوك Android runtime. ما عملناش benchmark ولا ادّعاء تحسين performance.</p>

## Tests and failure cases

<p dir="rtl" lang="ar"><a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt"><code dir="ltr">LabChecksTest.kt</code></a> فيها تمانية حالات JUnit: ID معروف مع <code dir="ltr">trim</code>، ونتائج Java مفقودة/فاضية/مجهولة، و<code dir="ltr">null</code> وwhitespace مباشرة، وnormalization، واختبار بيتوقع <code dir="ltr">NullPointerException</code> من الـ dereference غير الآمن. أمر <code dir="ltr">./gradlew clean check run --no-daemon</code> بيشغّل الاختبارات والتطبيق؛ حالة تشغيله موثّقة في <a dir="ltr" href="../BUILD-VERIFICATION.md">BUILD-VERIFICATION</a>. لو عقد المنتج بيهتم بـ Unicode whitespace أو تغيير سلوك الـ vendor، ضيف لها اختبارات في batch لاحقة.</p>

## Interview explanation (مصري)

<p dir="rtl" lang="ar">&quot;Kotlin بيفرق بين <code dir="ltr">String</code> و<code dir="ltr">String?</code> وقت الـ compile. بس لو Java SDK مرجعش nullability annotation، الناتج platform type، فممكن <code dir="ltr">.length</code> تتقبل وتكسر وقت التشغيل. بحط <code dir="ltr">String?</code> صراحة عند الـ boundary، أعمل validation مرة واحدة، وبعدها أتعامل مع domain type مضمون. والـ fallback قرار product، مش حل تلقائي لكل null.&quot;</p>

**English, about 20 seconds:** “Kotlin checks nullable values at compile time, but an unannotated Java result is a platform type. I receive it as `String?`, validate it once at the boundary, and then use a domain value. The fallback depends on whether the field is optional or required.”

**English, about 60–90 seconds:** “I start by asking what the Java API actually promises. If it has no recognized nullability annotation, Kotlin gives me a platform type and allows a direct call even though the result may be null. I convert that uncertainty into an explicit nullable local, then normalize and validate the value. In the sample, a blank or missing display name becomes `Guest`, because the UI contract permits that. For a required identity, I would return a typed error instead of masking the problem. I test the Java boundary with a fake that returns null and blanks, because Kotlin syntax alone cannot prove the vendor contract.”

## Senior follow-ups, with answers

<ol dir="rtl" lang="ar">
<li><strong>هل تحويل <code dir="ltr">String!</code> إلى <code dir="ltr">String</code> يضمن إن Java API آمنة؟</strong> لأ. Kotlin ممكن يضيف runtime assertion، ولو القيمة null هتفشل. <code dir="ltr">String?</code> بتخلي عدم اليقين واضح وبتجبرك تختار فرع. <a dir="ltr" href="https://kotlinlang.org/docs/java-interop.html">Java interop</a>.</li>
<li><strong>ليه <code dir="ltr">if (owner.name != null) owner.name.length</code> ممكن ما تعملش smart cast؟</strong> property قابلة للتغيير أو open ممكن ترجع قيمة مختلفة في القراية التانية. خُد local snapshot، افحصها واستخدمها. ده يحل مشكلة القرايتين، لكنه مش synchronization للتحديثات المتزامنة. <a dir="ltr" href="https://kotlinlang.org/docs/typecasts.html">Type checks and casts</a>.</li>
</ol>

## Misconceptions, revision, and self-check

<ul dir="rtl" lang="ar">
<li>“Kotlin بتمنع كل NPE.” غلط: <code dir="ltr">!!</code> وJava interop وأخطاء التهيئة استثناءات موثقة.</li>
<li>“<code dir="ltr">?.</code> بتصلّح البيانات الغلط.” غلط: بتتعامل مع null، مش validation أو business rules.</li>
<li>“data class وprivate constructor كفاية لأي invariant.” غلط هنا بسبب تحذير compiler عن <code dir="ltr">copy</code> المتولدة؛ استخدم class عادية أو اضبط سلوك النسخ بوضوح.</li>
</ul>

<p dir="rtl" lang="ar"><strong>Flashcards:</strong> <code dir="ltr">String?</code> معناها إيه؟ <strong>ممكن null.</strong> <code dir="ltr">String!</code> معناها إيه؟ <strong>platform type مستنتج من interop، مش syntax.</strong> إمتى smart cast تنفع؟ <strong>لما الـ compiler يقدر يثبت ثبات القيمة من الفحص للاستخدام.</strong></p>

<p dir="rtl" lang="ar"><strong>تأكد من فهمك بشكل اختياري، والإجابة ظاهرة:</strong> <code dir="ltr">safeLabelFromLegacy(&quot;blank&quot;)</code> ترجع إيه؟ <strong><code dir="ltr">Guest</code></strong> لأن <code dir="ltr">trim</code> عملت نص فاضي و<code dir="ltr">takeIf</code> رجّعت null. ليه <code dir="ltr">.length</code> الغلط بتتعمل compile؟ <strong>لأن Java return نوعه platform type.</strong></p>

<p dir="rtl" lang="ar"><strong>مراجعة:</strong> اشرح Java boundary بكرة، وبعدها تقريبًا في أيام 3 و7 و14 و30. لو مش قادر تتبع فرع <code dir="ltr">blank</code> من غير بص، كرر الـ trace قبل موضوع جديد.</p>

<p dir="rtl" lang="ar"><strong>حدود الدليل:</strong> المعمل اختبر fake Java SDK وJDK 17 فقط. ما يثبتش سلوك SDK دفع حقيقي، أو Android runtime، أو إعداد annotations مختلف.</p>
