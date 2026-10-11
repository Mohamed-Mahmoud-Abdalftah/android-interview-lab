---
id: ARC-Q025-ANSWER
question_id: ARC-Q025
status: reviewed
---
# ARC-Q025 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “More modules can improve isolation and parallelism but add configuration, graph, and API maintenance cost.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الmodule تجمع code تتغير معًا وتصدر contract صغيرة؛ dependency graph لا تكشف internals ولا تعمل cycle.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Two teams share a large core module. Changes trigger broad rebuilds and no one owns regressions. Propose an incremental split and define the measurements that would tell you whether it helped.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Build and ownership trade-offs:</strong> Gradle module تعمل compilation وdependency boundary حقيقية، لكن كل boundary تزود configuration وAPI surface. الاتجاه الصحيح يخلي feature تشوف contract صغيرة، بينما implementation تفضل internal عشان تغييرها لا يجبر graph كلها تعيد البناء أوالتعديل.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBuild and ownership trade-offs: حدد change axis وowner، انقل contract لأقرب stable boundary، اخفِ implementation، وقِس build/coordination cost قبل زيادة modules.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “More Gradle modules always mean cleaner architecture and faster builds.”

<p dir="rtl" lang="ar">في <strong>Build and ownership trade-offs</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الmodule تجمع code تتغير معًا وتصدر contract صغيرة؛ dependency graph لا تكشف internals ولا تعمل cycle. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Build and ownership trade-offs: package boundary داخل module أفضل لو مفيش independent ownership أو build isolation؛ module زيادة لها تكلفة مستمرة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Build and ownership trade-offs: استخدم dependency graph/API check، امنع forbidden dependency، وغيّر implementation في module وتأكد إن consumers لا تحتاج تعديل.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Build and ownership trade-offs، الـshortcut هي: <bdi dir="ltr">More Gradle modules always mean cleaner architecture and faster builds.</bdi> ودي تكسر: الmodule تجمع code تتغير معًا وتصدر contract صغيرة؛ dependency graph لا تكشف internals ولا تعمل cycle.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Build and ownership trade-offs: استخدم dependency graph/API check، امنع forbidden dependency، وغيّر implementation في module وتأكد إن consumers لا تحتاج تعديل.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Build and ownership trade-offs: package boundary داخل module أفضل لو مفيش independent ownership أو build isolation؛ module زيادة لها تكلفة مستمرة.</span>

## English model answer

“More modules can improve isolation and parallelism but add configuration, graph, and API maintenance cost. I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis. I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.”
