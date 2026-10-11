---
id: AND-Q011-ANSWER
question_id: AND-Q011
status: reviewed
---
# AND-Q011 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> Navigation host تملك ordered entries؛ route تحمل stable IDs فقط، وكل entry point يبني authorized stack وBack behavior متوقع.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Explain why launchMode is not a substitute for modeling navigation state.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Task and back-stack semantics:</strong> NavHost تملك sequence من back-stack entries، وكل entry لها lifecycle وSavedStateHandle. route المفروض تحمل ID صغيرة لاobject stale؛ singleTop يقارن القمة فقط، وdeep link لازم تبني stack منطقية بعد validation وauthorization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTask and back-stack semantics: عرّف typed route، reload data بالID، اختار singleTop/popUpTo من UX، ومرر external entry عبر validation وauth قبل destination.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Passing the whole domain object and adding singleTop solves stale arguments and all duplicates.”

<p dir="rtl" lang="ar">في <strong>Task and back-stack semantics</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: Navigation host تملك ordered entries؛ route تحمل stable IDs فقط، وكل entry point يبني authorized stack وBack behavior متوقع. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Task and back-stack semantics: singleTop يمنع duplicate في القمة فقط؛ state-based navigation أو popUpTo أوضح لما المطلوب إزالة history أوسع.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Task and back-stack semantics: شغّل normal launch وdeep link وnotification وduplicate taps ثم recreation؛ تحقق من entries والarguments وBack وinvalid link rejection.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Task and back-stack semantics، الـshortcut هي: <bdi dir="ltr">Passing the whole domain object and adding singleTop solves stale arguments and all duplicates.</bdi> ودي تكسر: Navigation host تملك ordered entries؛ route تحمل stable IDs فقط، وكل entry point يبني authorized stack وBack behavior متوقع.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Task and back-stack semantics: شغّل normal launch وdeep link وnotification وduplicate taps ثم recreation؛ تحقق من entries والarguments وBack وinvalid link rejection.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Task and back-stack semantics: singleTop يمنع duplicate في القمة فقط؛ state-based navigation أو popUpTo أوضح لما المطلوب إزالة history أوسع.</span>

## English model answer

“Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
