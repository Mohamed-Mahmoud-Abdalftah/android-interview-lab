---
id: SYS-001
title: Arrays, maps, two pointers and invariants
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-002]
learning_outcomes:
  - State a loop invariant for a one-pass pair search and a sorted two-pointer search
  - Preserve original indices while handling duplicates and no-solution cases
  - Prevent Int overflow from fabricating a pair
  - Compare expected hash-map complexity with deterministic sorted-input complexity
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/arrays.html
  - https://kotlinlang.org/docs/collections-overview.html
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/PairSearch.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/PairSearchTest.kt
question_ids: [SYS-Q001, SYS-Q002, SYS-Q003, SYS-Q004, SYS-Q005]
---

# SYS-001 — Arrays, maps, two pointers and invariants

**Starting point:** [KOT-002](../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md) covered mutable collections, equality and stable map keys. This unit is a live-coding foundation within the mobile system-design week; it does not count as a complete system-design case study or fill all DSA practice.

**Two-hour route:** 55 minutes explanation/trace, 20 minutes [questions and visible answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes [LAB-008](../Coding-Challenges/LAB-008-pair-search-invariants.md), 10 minutes [revision](../Flashcards-Revision/SYS-001.md), optional 10 minutes [English](../Speaking-Shadowing/DAY-37.md). No hidden test or timer.

## Mental model

<p dir="rtl" lang="ar">قبل ما تكتب كود two-sum، اسأل العقد: نرجع original indices ولا values؟ input مترتبة ولا لأ؟ هل pair تستخدم عنصرين مختلفين؟ نختار أول حل بأي معنى؟ الـ invariant جملة تظل صحيحة قبل وبعد كل خطوة وتساعدك تثبت الحل بدل حفظ pattern. في input غير مرتبة مع original indices، map تحفظ أول index لكل قيمة شفناها. في input مرتبة والهدف values، نقدر نحرك طرفين من غير map. <a dir="ltr" href="https://kotlinlang.org/docs/arrays.html">Kotlin arrays</a> و<a dir="ltr" href="https://kotlinlang.org/docs/collections-overview.html">collections</a>، اتراجعوا 2026-10-10.</p>

<ul dir="rtl" lang="ar">
<li><strong>Hash map invariant:</strong> قبل index الحالية، <code dir="ltr">earliestIndex</code> فيها أول موضع لكل قيمة في الجزء السابق فقط. نبحث عن complement قبل إدخال الحالية، فلا نستخدم نفس العنصر مرتين.</li>
<li><strong>Two-pointer invariant:</strong> في array مرتبة تصاعديًا، لو sum أقل من target، أي pair مع القيمة اليسرى الحالية وقيمة داخل الحدود لا تكفي؛ حرك left للأمام. لو sum أكبر، حرك right للخلف.</li>
<li><strong>Overflow:</strong> احسب target minus current وsum في <code dir="ltr">Long</code> قبل المقارنة. overflow في <code dir="ltr">Int</code> ممكن تصنع جوابًا خاطئًا.</li>
</ul>

## Mechanism and execution trace

<p dir="rtl" lang="ar">دالة <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/PairSearch.kt">pairIndicesForTarget</a> تمشي مرة على <code dir="ltr">IntArray</code> غير مرتبة. عند كل index تحسب complement بـ Long؛ لو تقع في مدى Int وتوجد في map ترجع أول index محفوظة ثم الحالية. غير كده تخزن الحالية إن لم تكن موجودة. ده يحدد النتيجة: أول pair بحسب second index أثناء المسح، وليس أصغر first index في كل الحلول الممكنة.</p>

```kotlin
val values = intArrayOf(1, 2, 3, 4)
pairIndicesForTarget(values, 5) // (1, 2): first found at second index 2
```

<table dir="rtl" lang="ar">
<thead><tr><th>i والقيمة</th><th>المطلوب قبل الإدخال</th><th>map قبل الخطوة</th><th>القرار</th></tr></thead>
<tbody>
<tr><td dir="ltr">0, 1</td><td dir="ltr">4</td><td>فارغة</td><td>خزّن <code dir="ltr">1 → 0</code>.</td></tr>
<tr><td dir="ltr">1, 2</td><td dir="ltr">3</td><td><code dir="ltr">1 → 0</code></td><td>خزّن <code dir="ltr">2 → 1</code>.</td></tr>
<tr><td dir="ltr">2, 3</td><td dir="ltr">2</td><td><code dir="ltr">1 → 0, 2 → 1</code></td><td>ارجع <code dir="ltr">(1, 2)</code> قبل النظر إلى 4.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">لو المطلوب values فقط والـ array مترتبة، <code dir="ltr">pairValuesInSorted</code> تتحقق أولًا من ترتيب غير تنازلي ثم تستخدم left/right. مثال <code dir="ltr">[1,2,5,7,9]</code> وtarget 9: <code dir="ltr">1+9=10</code> فحرك right؛ <code dir="ltr">1+7=8</code> فحرك left؛ <code dir="ltr">2+7=9</code> فتوقف. التحقق O(n)، والبحث O(n)، ومساحة إضافية O(1). <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/PairSearchTest.kt">اختبارات المعمل</a> تثبت العقد.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط شائع:</strong> ترتب input عشان تستخدم two pointers ثم ترجع positions الجديدة كأنها original indices. وغلط تاني إنك تدخل current value في map قبل البحث، فـ target يساوي ضعف القيمة قد يستخدم نفس العنصر مرتين. وغلط ثالث إنك تحسب <code dir="ltr">Int.MAX_VALUE + 1</code> كـ Int وتفسر overflow كحل.</p>

```kotlin
// Wrong if original indices are required:
val sorted = values.sorted()
// Returning positions in sorted is not returning positions in values.
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم hash map للـ original indices، وابحث قبل الإدخال، واحسب complement في Long. لو input sorted وcontract تطلب values، two pointers أبسط. لو sorted input لكن original indices لازمة، تقدر ترتب pairs من value/index مع تكلفة فرز O(n log n) ومساحة مناسبة، أو تستخدم map وتحتفظ بالأصل من غير فرز. اختر بناءً على العقد، لا اسم pattern.</p>

## Complexity and alternatives

<p dir="rtl" lang="ar">الـ map algorithm تمر O(n) عمليات lookup/insert. Java <code dir="ltr">HashMap</code> توثق أداء constant time للعمليات الأساسية <strong>بافتراض</strong> hash distribution جيد، لذلك الزمن المتوقع تقريبًا O(n) مع مساحة O(n)؛ لا تقل worst-case O(n) بلا شروط. الـ two pointers على input مرتبة يستهلك O(n) وقت وO(1) مساحة إضافية بعد فحص الترتيب. لو احتجت فرز input أولًا، أضف تكلفة O(n log n) وناقش أثر تغيير الترتيب على indices. <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html">Java HashMap contract</a>.</p>

<p dir="rtl" lang="ar">Key هنا <code dir="ltr">Int</code> مستقرة؛ لو استبدلتها بـ mutable object، سلوك map بعد تغيير equality قد يصبح غير محدد. <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html">Java Map contract</a>. في production mobile، قياس allocations والـ input size مهم قبل تحسين مبكر؛ benchmark لم يحدث هنا.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة اختبارات JUnit تغطي original indices وعدم تغيير input، duplicates، overflow false pair، extremes سالبة/موجبة، أول pair بحسب second index، two pointers صحيحة، no pair ورفض input غير مرتبة. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> من معمل JVM وراجع <a dir="ltr" href="../BUILD-VERIFICATION.md">الدليل</a>. الاختبارات لا تثبت worst-case أداء map ولا workload Android حقيقي.</p>

<p dir="rtl" lang="ar">حالات إضافية: array فارغة، عنصر واحد، target صفر، عدة حلول، inputs ضخمة، hash collisions غير اعتيادية. المعمل يرجع null عند عدم وجود pair، ويستخدم عنصرين مختلفين دائمًا لأن lookup قبل الإدخال. لو شرط المنتج يفضل lexicographically smallest pair، التنفيذ الحالي لا يحقق العقد؛ يحتاج اختيار مختلف واختبار جديد.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> أوضح العقد الأول. لو مطلوب original indices في input غير مرتبة، map تحفظ أول index للقيم اللي شفتها. قبل ما أدخل القيمة الحالية أدور على complement، وبـ Long عشان overflow ما يخدعنيش. لو input sorted ومطلوب values، left/right invariant تخليني أحذف جزء من مساحة البحث كل خطوة. أذكر شروط التعقيد وedge cases.</p>

**English, about 20 seconds:** “I clarify whether the output is original indices or values and whether the input is sorted. For original indices I scan once with a map, checking the complement before insertion. I use Long arithmetic to avoid overflow.”

**English, about 60–90 seconds:** “The one-pass map invariant is that before index i, the map holds the earliest index of each value in the prefix. I compute the complement in Long, look it up before inserting the current value, and return a pair of distinct original indices. This returns the first pair encountered by second index. Under well-distributed hashing the expected time is linear with linear extra space; I do not promise a hash-map worst-case bound from that average. If the input is already sorted and only values are needed, two pointers move inward based on whether the Long sum is below or above target, giving linear time and constant extra space after sortedness validation. I test duplicates, no solution, overflow and nonmutation.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>ليه lookup قبل insert؟</strong> عشان العنصر الحالي ما يطابقش نفسه عند target ضعف قيمته.</li>
<li><strong>هل map O(1) دائمًا؟</strong> لأ؛ Java docs تشترط توزيع hash مناسب للأداء constant-time الأساسي.</li>
<li><strong>لو input غير مرتبة وتحتاج values فقط، هل الفرز أفضل؟</strong> يعتمد على memory وoutput والعقود؛ map متوقعة O(n)، والفرز O(n log n) وقد يغير input لو in-place.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“الفرز يحافظ على original indices.” غلط إلا لو حفظت index الأصلية مع القيمة.</li>
<li>“<code dir="ltr">[3]</code> مع target 6 فيها pair.” غلط؛ تحتاج عنصرين مختلفين.</li>
<li>“<code dir="ltr">Int</code> arithmetic كافية لكل target.” غلط عند حدود overflow.</li>
<li>“HashMap دائمًا O(1) بلا افتراضات.” غلط؛ راجع شرط توزيع hash.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات سريعة:</strong> <code dir="ltr">[3,3]</code> target 6 يرجع <code dir="ltr">(0,1)</code>. <code dir="ltr">[Int.MAX_VALUE,1]</code> target <code dir="ltr">Int.MIN_VALUE</code> ترجع null. راجع <a dir="ltr" href="../Flashcards-Revision/SYS-001.md">البطاقات</a> و<a dir="ltr" href="../Real-World-Scenarios/SCN-008-overflow-batch-pair.md">السيناريو</a>.</p>

**Evidence limit:** Kotlin/JVM tests cover the concrete algorithms on selected edge cases. Complexity claims follow loop analysis and the conditional Java HashMap contract; no benchmark or Android workload was run.
