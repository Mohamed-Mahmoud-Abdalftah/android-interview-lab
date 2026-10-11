---
id: CON-Q010-ANSWER
question_id: CON-Q010
status: reviewed
---
# CON-Q010 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use structured lock APIs so cancellation releases ownership, and keep cleanup bounded.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A coroutine is cancelled while waiting for or holding a Mutex. What guarantees do you need for acquisition, finally cleanup, and shared-state consistency?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Cancellation and locks:</strong> إلغاء coroutine يغيّر Job state ويوقظ suspension points المتعاونة بـCancellationException. CPU loop بلا checkpoint أوI/O خارجية قد تكمل. catch واسع يحول cancellation لـfailure عادية ويخلي code تنشر state بعد انتهاء الـowner.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCancellation and locks: اكتب harmful interleaving، اجمع fields في atomic state أو Mutex قصيرة، أو confined owner؛ حدد queue bound/drop policy من معنى الحدث.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Coroutines and visible volatile fields make every compound state transition thread-safe.”

<p dir="rtl" lang="ar">في <strong>Cancellation and locks</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Cancellation and locks: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Cancellation and locks: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Cancellation and locks، الـshortcut هي: <bdi dir="ltr">Coroutines and visible volatile fields make every compound state transition thread-safe.</bdi> ودي تكسر: الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Cancellation and locks: استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Cancellation and locks: immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.</span>

## English model answer

“Use structured lock APIs so cancellation releases ownership, and keep cleanup bounded. I would state the shared invariant, demonstrate the harmful interleaving, and choose immutability, confinement, a mutex, or atomic state according to the whole invariant. I would force harmful interleavings, verify atomic state transitions, and cover cancellation while the critical section is active.”
