---
id: KOT-006
title: Revision: JVM, DEX/ART boundary and Big-O
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 120
prerequisite_ids: [KOT-001, KOT-002, KOT-005]
learning_outcomes:
  - Trace Kotlin source through JVM class files, D8 and DEX without treating ART as a JVM
  - Separate language semantics, build artifacts and runtime optimization when debugging
  - Derive time and space complexity from loops and data-structure operations
  - Compare a quadratic duplicate scan with an expected-linear hash-set scan using deterministic evidence
  - Explain why Big-O, operation counts and device benchmarks answer different questions
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_status: verified
source_urls:
  - https://kotlinlang.org/docs/compiler-reference.html
  - https://developer.android.com/tools/d8
  - https://developer.android.com/guide/platform
  - https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/DuplicateScan.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/DuplicateScanTest.kt
question_ids: [KOT-Q026, KOT-Q027, KOT-Q028, KOT-Q029, KOT-Q030]
---

# KOT-006 — Revision: JVM, DEX/ART boundary and Big-O

**مسار الساعتين:** 30 دقيقة مراجعة mental model، 20 دقيقة تتبع build/runtime، 35 دقيقة [LAB-017](../Coding-Challenges/LAB-017-duplicate-scan-complexity.md)، 25 دقيقة [الأسئلة والإجابات](../Interview-Question-Bank/BY-TOPIC.md)، و10 دقائق [speaking](../Speaking-Shadowing/DAY-06.md).

## Mental model — افصل اللغة عن الـartifact عن الـruntime

<p dir="rtl" lang="ar">لما تكتب Kotlin في Android، عندك تلات طبقات لازم ما تخلطهمش. أول طبقة هي <strong>معنى الكود</strong>: nullability، equality، generics، والـcontrol flow اللي Kotlin محدداهم. تاني طبقة هي <strong>ناتج الـbuild</strong>: Kotlin/JVM compiler يطلع Java-compatible <code dir="ltr">.class</code> bytecode، وبعدها Android toolchain تستخدم <code dir="ltr">D8</code> عشان تحوّل Java bytecode إلى <code dir="ltr">DEX</code>. تالت طبقة هي <strong>التنفيذ على الجهاز</strong>: Android Runtime، أو <code dir="ltr">ART</code>، تشغّل DEX داخل process التطبيق وتقدر تستخدم interpreter وJIT وAOT وGC حسب إصدار الجهاز وحالته.</p>

```text
Kotlin source (.kt)
        │ Kotlin/JVM compiler
        ▼
JVM class files (.class) + Kotlin metadata
        │ Android build tools / D8 (and release optimization when configured)
        ▼
Dalvik Executable bytecode (classes.dex)
        │ ART in the app process
        ▼
interpreted and/or compiled machine code while the app runs
```

<p dir="rtl" lang="ar">السلسلة دي تمنع إجابات مقابلة مضللة. Android مش بتشغّل <code dir="ltr">.class</code> مباشرة كإنها desktop JVM، وDEX مش native machine code في حد ذاتها، ووجود JIT/AOT مش وعد إن كل method هتبقى compiled بنفس الشكل على كل جهاز. لو bug في null contract، ما تلومش ART. ولو crash ظهر في release بس، ساعتها تسأل عن optimization، mapping، reflection rules، generated code، وفرق الـconfiguration بأدلة.</p>

## Mechanism and execution trace — من source لحد النتيجة

<p dir="rtl" lang="ar">اتتبع المثال البسيط ده من غير ما تفترض شكل bytecode ثابت. الـcompiler يطبق semantics الخاصة بـKotlin ويولد class files. D8 تقرأ class files والـdependencies وتطلع DEX مناسبة للـAndroid target، وممكن تعمل desugaring لبعض Java language/library features حسب إعدادات البناء. وقت التشغيل ART تحمل classes المطلوبة وتدير الذاكرة والتنفيذ. النتيجة المنطقية للدالة تفضل راجعة لعقد الكود؛ استراتيجية التنفيذ الداخلية ممكن تتغير.</p>

```kotlin
fun safeLength(value: String?): Int = value?.length ?: 0
```

```text
input null  -> null check -> fallback branch -> 0
input "Ada" -> non-null branch -> length     -> 3
```

<p dir="rtl" lang="ar">لو عايز تعرف generated artifact فعلًا، افحصه من نفس variant والأدوات اللي بتبني بيها. ما تستنتجش عدد allocations أو instructions من شكل source بس، وما تنقلش استنتاج من JVM test إلى ART performance. الـJVM test يثبت semantics الخاصة بالmodel اللي شغّلته؛ Android benchmark أو profile يجاوب عن الجهاز والvariant والسيناريو اللي قستهم.</p>

## Big-O — وصف النمو مش stopwatch

<p dir="rtl" lang="ar"><code dir="ltr">Big-O</code> بتوصف إزاي تكلفة algorithm تكبر لما حجم input، اللي بنسميه <code dir="ltr">n</code>، يكبر. هي بتشيل constants والحدود الأقل عشان تركز على شكل النمو. ده مش معناه إن constants مالهاش قيمة في production؛ معناه إن سؤال التعقيد وسؤال الزمن الفعلي سؤالين مختلفين. دالة <code dir="ltr">O(n)</code> ممكن تبقى أبطأ على input صغير من دالة <code dir="ltr">O(n²)</code> بسبب allocation أو cache locality، لكن مع نمو كبير الـquadratic work غالبًا هيتضخم أسرع.</p>

```kotlin
fun firstDuplicateNested(values: IntArray): Int? {
    for (current in values.indices) {
        for (previous in 0 until current) {
            if (values[previous] == values[current]) return values[current]
        }
    }
    return null
}
```

<p dir="rtl" lang="ar">في أسوأ حالة مفيش duplicate، فالـinner loop تعمل <code dir="ltr">0 + 1 + 2 + ... + (n-1)</code> مقارنة. المجموع <code dir="ltr">n(n-1)/2</code>، وبالتالي الزمن <code dir="ltr">O(n²)</code>. المساحة الإضافية <code dir="ltr">O(1)</code> لأننا مخزّناش collection بتكبر مع input. لو duplicate في أول عنصرين، الدالة تخرج بسرعة؛ دي best case، لكنها ما تلغيش worst-case growth.</p>

## Wrong and corrected implementation — من nested scan لـHashSet

<p dir="rtl" lang="ar"><strong>التنفيذ الغلط في مسار كبير:</strong> نراجع كل عنصر مع كل اللي قبله. هو صحيح وظيفيًا وقد يكون مناسب لـinput صغير جدًا ومقيد، لكن لو list جاية من import أو sync وعددها ممكن يكبر، لازم تسجل الافتراض ده أو تختار data structure أنسب.</p>

```kotlin
fun firstDuplicateWithSet(values: IntArray): Int? {
    val seen = HashSet<Int>(values.size)
    for (value in values) {
        if (!seen.add(value)) return value
    }
    return null
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> الـset تحفظ اللي شوفناه. كل عنصر يعمل insert/lookup واحدة، فالتكلفة المتوقعة <code dir="ltr">O(n)</code> لما hash distribution مناسبة وعمليات الجدول المتوقعة ثابتة. المساحة الإضافية <code dir="ltr">O(n)</code>. كلمة “متوقعة” مهمة: ما تقولش إن hash lookup <code dir="ltr">O(1)</code> مطلقة لكل implementation وكل adversarial input. كمان <code dir="ltr">HashSet&lt;Int&gt;</code> على JVM/ART ممكن تعمل boxing للـInt؛ لو المسار hot وحجم البيانات كبير، قِس وراجع primitive-friendly بديل مناسب بدل micro-optimization بالتخمين.</p>

## Deterministic execution trace

```text
input = [5, 1, 9, -3, 7]  // no duplicate

nested comparisons:
index 0 -> 0
index 1 -> 1
index 2 -> 2
index 3 -> 3
index 4 -> 4
total   -> 10 = n(n-1)/2

set insert attempts:
5, 1, 9, -3, 7 -> 5 = n
```

<p dir="rtl" lang="ar">في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/DuplicateScan.kt">DuplicateScan</a> بنرجّع عدد probes عشان الاختبار يشوف control-flow work من غير timer. الاختبار على خمس قيم unique يثبت 10 مقارنات للـnested و5 insert attempts للـset. ده دليل على implementation الحالي، مش benchmark ولا إثبات إن set أسرع بعدد nanoseconds على موبايل معين.</p>

## Arrays, collections and boundary costs

<p dir="rtl" lang="ar"><code dir="ltr">IntArray</code> بتمثل primitive int storage على JVM target، بينما <code dir="ltr">List&lt;Int&gt;</code> واجهة generic وقد تدخل boxing حسب التنفيذ والعمليات. ده لا يخلي <code dir="ltr">IntArray</code> اختيار تلقائي لكل API؛ List أسهل في immutability والتجميع، والـarray مناسبة في loops رقمية أو interop boundaries. اختار من contract، وبعدين قِس لو الأداء مؤثر.</p>

<p dir="rtl" lang="ar">الـalgorithm هنا ما بتعدّلاش input. دي property مهمة في feature boundary: caller يقدر يحتفظ بنفس الترتيب، والاختبار يقارن snapshot قبل وبعد. لو قررت sort عشان تستخدم adjacent scan، لازم تحسب <code dir="ltr">O(n log n)</code> وقرار mutation أو copy والمساحة، وتوضح إن ترتيب input الأصلي هيتحافظ عليه إزاي.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة اختبارات JUnit اتكتبت الأول وفشل compilation لأن implementation ما كانتش موجودة. بعد التنفيذ، الاختبارات غطت empty/single، أول duplicate حسب ترتيب الظهور، unique worst case، early exit، حدود Int، عدم تعديل input، والفرق بين operation count وelapsed time. شغّل <code dir="ltr">./gradlew test --tests academy.DuplicateScanTest --no-daemon</code> من مشروع الـJVM.</p>

<p dir="rtl" lang="ar">الاختبارات لا تثبت D8 output أو ART optimization أو allocation count أو device latency. الأدلة دي تحتاج Android toolchain موجودة، variant معروف، APK/DEX inspection، وbenchmark أو profiler على target devices. ما نحولش unit test ناجحة لادعاء performance production.</p>

## Practical scenario — لما الـUI تعلق واللوم يروح للـruntime

<p dir="rtl" lang="ar">في <a dir="ltr" href="../Real-World-Scenarios/SCN-018-quadratic-import-freeze.md">SCN-018</a>، import صغير كان شغال، وبعد عميل كبير الشاشة بقت تعلق. الفريق افترض إن ART أو release optimization السبب. التحقيق الصح يبدأ بحجم input، thread، trace، loop counts، وفرق variants. لو nested scan بتعمل حوالي 50 مليون مقارنة لعشرة آلاف عنصر unique، تغيير الـruntime مش أصل المشكلة. تصلح algorithm، تحط limits أو chunking حسب الـUX، وبعدين تقيس على الجهاز.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> Kotlin/Android ليها pipeline: Kotlin/JVM compiler يطلع class bytecode، وD8 تحولها DEX، وART تشغّل DEX داخل process التطبيق باستراتيجيات تنفيذ ممكن تختلف حسب الجهاز. ده منفصل عن تعقيد الـalgorithm. Big-O بتوصف نمو الشغل، مش زمن ثابت. nested duplicate scan أسوأ حالاتها <code dir="ltr">O(n²)</code> ومساحتها <code dir="ltr">O(1)</code>، والـHashSet حل متوقع <code dir="ltr">O(n)</code> بزمن ومساحة <code dir="ltr">O(n)</code>. أستخدم operation counts للاختبار وbenchmark للجهاز قبل claim أداء.</p>

**English interview answer:** “For Android, Kotlin/JVM source is compiled to JVM class files, and D8 converts Java bytecode to DEX. ART executes DEX in the application process and may interpret or compile code depending on the runtime and device. I keep that pipeline separate from algorithmic complexity. A nested duplicate scan has quadratic worst-case work, while a hash-set scan is expected linear time with linear extra space. Deterministic operation counts verify the control flow; device benchmarks are still required for latency or allocation claims.”

## Senior follow-ups

1. **Does ART run JVM bytecode directly?** Android build tools convert Java bytecode to DEX; ART executes DEX in Android's runtime model.
2. **Can a JUnit test prove the release APK is optimized correctly?** It proves the JVM model behavior only; inspect the release artifact and run Android-specific tests or benchmarks for that claim.
3. **Why say expected O(n) for the set solution?** It depends on expected constant-time hash operations under a suitable distribution; collision behavior and implementation details still matter.
4. **When is O(n²) acceptable?** When the input has a real small upper bound, the simpler code is safer, and that bound is enforced and tested. Document the decision.
5. **What would you measure before optimizing boxing?** Allocations, GC pressure, CPU samples and end-to-end latency on the relevant device and build variant.

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li><strong>“Android JVM عادية”:</strong> Kotlin/JVM تطلع class files، وبعدها Android toolchain تنتج DEX وART تنفذها.</li>
<li><strong>“DEX native code”:</strong> DEX bytecode؛ ART هي اللي تدير التنفيذ والتحويلات المناسبة للruntime.</li>
<li><strong>“Big-O benchmark”:</strong> Big-O شكل نمو، والـbenchmark قياس لسيناريو وبيئة محددين.</li>
<li><strong>“HashSet دايمًا O(1)”:</strong> قل expected constant time مع assumptions، واحسب المساحة والـboxing.</li>
<li><strong>“early return تخلي nested O(1)”:</strong> دي best case؛ أسوأ حالة ما زالت quadratic.</li>
<li><strong>“unit tests تثبت device performance”:</strong> بتثبت semantics والـoperation trace اللي صممناه فقط.</li>
</ul>

**حدود الدليل:** اتنفذ Kotlin/JVM model وJUnit tests. ما فيش Android SDK في البيئة الحالية، لذلك ما اتعملش D8/DEX inspection، ART profiling، Android benchmark أو APK variant comparison.
