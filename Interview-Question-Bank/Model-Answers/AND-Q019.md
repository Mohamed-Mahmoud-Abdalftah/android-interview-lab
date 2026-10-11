---
id: AND-Q019-ANSWER
question_id: AND-Q019
status: reviewed
---
# AND-Q019 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A queued callback captures the Activity or view until execution or removal. Tie callbacks to a lifecycle owner, remove them, or move state work to a longer-lived owner without capturing views.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـqueued callback تفضل ماسكة كل captures لحد التنفيذ أو الإزالة؛ view owner المنتهية لازم لا تبقى reachable من queue أطول عمرًا.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">How can a delayed callback retain a destroyed screen, and what is the correction?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Handler leak:</strong> MessageQueue تحتفظ بالـRunnable لحد وقت التنفيذ. لو الـlambda قافلة على Activity أوView، السلسلة Queue → Message → Runnable → Activity تمنع الـGC حتى لو الشاشة اتقفلت.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـHandler leak: استخدم lifecycle-owned callback أو removeCallbacks في cleanup، وانقل state work لowner أطول عمرًا من غير capture للـActivity أو View.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The callback is small, so capturing the Activity cannot leak it.”

<p dir="rtl" lang="ar">في <strong>Handler leak</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـqueued callback تفضل ماسكة كل captures لحد التنفيذ أو الإزالة؛ view owner المنتهية لازم لا تبقى reachable من queue أطول عمرًا. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Handler leak: WeakReference تخفي symptom وقد تسقط العمل؛ ownership وexplicit cancellation أوضح وأقوى.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Handler leak: جدول callback مؤجلة، اقفل الشاشة قبل التنفيذ، اعمل GC/heap inspection وتأكد إن الـActivity القديمة غير retained وإن callback لا تعدّل dead view.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Handler leak، الـshortcut هي: <bdi dir="ltr">The callback is small, so capturing the Activity cannot leak it.</bdi> ودي تكسر: الـqueued callback تفضل ماسكة كل captures لحد التنفيذ أو الإزالة؛ view owner المنتهية لازم لا تبقى reachable من queue أطول عمرًا.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Handler leak: جدول callback مؤجلة، اقفل الشاشة قبل التنفيذ، اعمل GC/heap inspection وتأكد إن الـActivity القديمة غير retained وإن callback لا تعدّل dead view.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Handler leak: WeakReference تخفي symptom وقد تسقط العمل؛ ownership وexplicit cancellation أوضح وأقوى.</span>

## English model answer

“A queued callback captures the Activity or view until execution or removal. Tie callbacks to a lifecycle owner, remove them, or move state work to a longer-lived owner without capturing views. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
