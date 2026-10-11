---
id: ART-Q008-ANSWER
question_id: ART-Q008
status: reviewed
---
# ART-Q008 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Generic and nullable primitives may allocate or box; prove user impact with profiles before redesign.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> generic JVM collections تخزن references، فـInt غالبًا تتعمل لها boxing إلى Integer؛ القيمة النظرية O(n) لا تصف allocation وGC cost على hot path.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A hot Kotlin loop stores millions of Int values in generic collections. Explain where boxing appears, how you would measure its cost, and when specialized storage is justified.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Boxing and allocation:</strong> generic JVM collections تخزن references، فـInt غالبًا تتعمل لها boxing إلى Integer؛ القيمة النظرية O(n) لا تصف allocation وGC cost على hot path. اثبت allocation في profiler أوbenchmark، قلل temporary objects، واستخدم primitive array أوspecialized collection فقط في measured hot path مع API boundary واضحة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBoxing and allocation: اثبت allocation في profiler أوbenchmark، قلل temporary objects، واستخدم primitive array أوspecialized collection فقط في measured hot path مع API boundary واضحة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Kotlin Int is always stored as an unboxed primitive, including inside generic collections.”

<p dir="rtl" lang="ar">في <strong>Boxing and allocation</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: generic JVM collections تخزن references، فـInt غالبًا تتعمل لها boxing إلى Integer؛ القيمة النظرية O(n) لا تصف allocation وGC cost على hot path. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Boxing and allocation: List&lt;Int&gt; أوضح ومناسب لمعظم paths؛ optimization المتخصصة تستحق فقط لما القياس يربط boxing بمشكلة مستخدم.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Boxing and allocation: قارن نفس workload وrelease build مع warm-up، راقب allocations/op وGC وframe time، وتأكد إن overflow وsemantics لم تتغير مع representation الجديدة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Boxing and allocation، الـshortcut هي: <bdi dir="ltr">Kotlin Int is always stored as an unboxed primitive, including inside generic collections.</bdi> ودي تكسر: generic JVM collections تخزن references، فـInt غالبًا تتعمل لها boxing إلى Integer؛ القيمة النظرية O(n) لا تصف allocation وGC cost على hot path.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Boxing and allocation: قارن نفس workload وrelease build مع warm-up، راقب allocations/op وGC وframe time، وتأكد إن overflow وsemantics لم تتغير مع representation الجديدة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Boxing and allocation: List&lt;Int&gt; أوضح ومناسب لمعظم paths؛ optimization المتخصصة تستحق فقط لما القياس يربط boxing بمشكلة مستخدم.</span>

## English model answer

“Generic and nullable primitives may allocate or box; prove user impact with profiles before redesign. I would name the exact build or runtime stage, inspect its input and output artifact, and avoid transferring guarantees between Kotlin, JVM bytecode, DEX tooling, and ART. I would inspect the release artifact, mapping, DEX or runtime trace from the exact affected build and device version.”
