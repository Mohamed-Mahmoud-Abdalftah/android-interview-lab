---
id: COR-Q015-ANSWER
question_id: COR-Q015
status: reviewed
---
# COR-Q015 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “I use runTest, gates such as CompletableDeferred, start the child, advance the scheduler to the known suspension point, cancel the parent, and assert cancellation plus exactly-once cleanup and no later publication.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـcancellation cooperative وتنتشر كـCancellationException؛ cleanup قصيرة ومحدودة، وأي timeout لها owner ومعنى منفصل عن failure وunknown outcome.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Design a deterministic test for cancellation and cleanup without Thread.sleep.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Cancellation verification:</strong> إلغاء coroutine يغيّر Job state ويوقظ suspension points المتعاونة بـCancellationException. CPU loop بلا checkpoint أوI/O خارجية قد تكمل. catch واسع يحول cancellation لـfailure عادية ويخلي code تنشر state بعد انتهاء الـowner.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCancellation verification: أضف checkpoint محسوبة في CPU loop، أعد رمي CancellationException، وخلي NonCancellable لcleanup bounded فقط مع حفظ سبب الـtimeout.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The suspend modifier makes all work cancellable and CancellationException should be mapped to a normal error.”

<p dir="rtl" lang="ar">في <strong>Cancellation verification</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـcancellation cooperative وتنتشر كـCancellationException؛ cleanup قصيرة ومحدودة، وأي timeout لها owner ومعنى منفصل عن failure وunknown outcome. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Cancellation verification: yield تفيد fairness؛ ensureActive أرخص لو محتاج check فقط. timeout في UI لا يلغي بالضرورة server operation.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Cancellation verification: باستخدام runTest وgates، أوقف التنفيذ عند suspension/checkpoint، cancel الـparent، واثبت no publication بعد الإلغاء وcleanup مرة واحدة من غير leaked child.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Cancellation verification، الـshortcut هي: <bdi dir="ltr">The suspend modifier makes all work cancellable and CancellationException should be mapped to a normal error.</bdi> ودي تكسر: الـcancellation cooperative وتنتشر كـCancellationException؛ cleanup قصيرة ومحدودة، وأي timeout لها owner ومعنى منفصل عن failure وunknown outcome.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Cancellation verification: باستخدام runTest وgates، أوقف التنفيذ عند suspension/checkpoint، cancel الـparent، واثبت no publication بعد الإلغاء وcleanup مرة واحدة من غير leaked child.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Cancellation verification: yield تفيد fairness؛ ensureActive أرخص لو محتاج check فقط. timeout في UI لا يلغي بالضرورة server operation.</span>

## English model answer

“I use runTest, gates such as CompletableDeferred, start the child, advance the scheduler to the known suspension point, cancel the parent, and assert cancellation plus exactly-once cleanup and no later publication. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
