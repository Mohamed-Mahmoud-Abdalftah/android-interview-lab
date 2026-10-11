---
id: COR-Q020-ANSWER
question_id: COR-Q020
status: reviewed
---
# COR-Q020 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “The coroutine may keep collecting while the view is stopped, wasting work or updating a dead view. I use lifecycle-aware collection with the correct owner and keep the producer lifetime separate from a collector lifetime.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> بس الـcurrent lifecycle/request owner ينشر state؛ إلغاء collector قد لا يرجع external effect ولا يمنع completion قديمة من commit.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Why is collecting a UI Flow in a plain launch risky on Android?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Lifecycle collection:</strong> latest operators تلغي coroutine القديمة، لكنها لا تعمل rollback لrequest وصلت server ولا تمنع callback غير متعاونة. لذلك owner تستخدم generation أوoperation ID عند commit النهائي، والـcollector نفسها ترتبط بالـview lifecycle.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـLifecycle collection: اربط collection بالـview lifecycle، استخدم latest operator لتقليل الشغل، وحط generation أو operation identity check عند آخر state mutation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “collectLatest or flatMapLatest rolls back old external work and guarantees it can never publish.”

<p dir="rtl" lang="ar">في <strong>Lifecycle collection</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: بس الـcurrent lifecycle/request owner ينشر state؛ إلغاء collector قد لا يرجع external effect ولا يمنع completion قديمة من commit. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Lifecycle collection: لو كل result لها business meaning استخدم queue/order بدل latest cancellation؛ latest صحيح فقط عندما القديم أصبح غير مطلوب.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Lifecycle collection: ابدأ R1 ثم R2، أوقف وأعد lifecycle، خلّي R1 تكمل بعد R2 رغم cancellation، واثبت إن R2 وحدها تنشر والcollector القديمة انتهت.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Lifecycle collection، الـshortcut هي: <bdi dir="ltr">collectLatest or flatMapLatest rolls back old external work and guarantees it can never publish.</bdi> ودي تكسر: بس الـcurrent lifecycle/request owner ينشر state؛ إلغاء collector قد لا يرجع external effect ولا يمنع completion قديمة من commit.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Lifecycle collection: ابدأ R1 ثم R2، أوقف وأعد lifecycle، خلّي R1 تكمل بعد R2 رغم cancellation، واثبت إن R2 وحدها تنشر والcollector القديمة انتهت.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Lifecycle collection: لو كل result لها business meaning استخدم queue/order بدل latest cancellation؛ latest صحيح فقط عندما القديم أصبح غير مطلوب.</span>

## English model answer

“The coroutine may keep collecting while the view is stopped, wasting work or updating a dead view. I use lifecycle-aware collection with the correct owner and keep the producer lifetime separate from a collector lifetime. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
