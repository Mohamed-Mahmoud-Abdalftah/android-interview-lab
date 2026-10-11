---
id: COR-Q027-ANSWER
question_id: COR-Q027
status: reviewed
---
# COR-Q027 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A shared scheduler gives one virtual clock and one queue, so advance and runCurrent control all subject work consistently. Separate schedulers can leave work invisible to the test's clock.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الاختبار يملك كل scopes والdispatchers وvirtual clock؛ مفيش wall-clock sleep أو scheduler خفية خارج سيطرته.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Why should test dispatchers in one test usually share a TestCoroutineScheduler?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في One scheduler rule:</strong> runTest تبني TestScope بvirtual clock وتراقب children. لما كل TestDispatcher تشارك نفس scheduler، runCurrent وadvanceUntilIdle يتحكموا في كل الشغل؛ أي real dispatcher أوsleep يرجع race مرتبطة بسرعة الجهاز.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـOne scheduler rule: حقن TestDispatcher واحدة تشارك scheduler، استخدم runCurrent/advanceUntilIdle وbounded collectors، ونظف Dispatchers.Main والbackground jobs.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Increase delay() or Thread.sleep until the coroutine test stops flaking.”

<p dir="rtl" lang="ar">في <strong>One scheduler rule</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الاختبار يملك كل scopes والdispatchers وvirtual clock؛ مفيش wall-clock sleep أو scheduler خفية خارج سيطرته. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في One scheduler rule: integration test بreal time مطلوب فقط للboundary الحقيقية؛ logic scheduling يفضل deterministic virtual time.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار One scheduler rule: كرر الاختبار مع ordering مختلفة، افشل لو فيه unfinished coroutine، وتأكد إن take/first أو backgroundScope تقفل collector بدل انتظار لا نهائي.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في One scheduler rule، الـshortcut هي: <bdi dir="ltr">Increase delay() or Thread.sleep until the coroutine test stops flaking.</bdi> ودي تكسر: الاختبار يملك كل scopes والdispatchers وvirtual clock؛ مفيش wall-clock sleep أو scheduler خفية خارج سيطرته.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار One scheduler rule: كرر الاختبار مع ordering مختلفة، افشل لو فيه unfinished coroutine، وتأكد إن take/first أو backgroundScope تقفل collector بدل انتظار لا نهائي.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في One scheduler rule: integration test بreal time مطلوب فقط للboundary الحقيقية؛ logic scheduling يفضل deterministic virtual time.</span>

## English model answer

“A shared scheduler gives one virtual clock and one queue, so advance and runCurrent control all subject work consistently. Separate schedulers can leave work invisible to the test's clock. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
