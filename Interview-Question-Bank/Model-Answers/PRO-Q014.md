---
id: PRO-Q014-ANSWER
question_id: PRO-Q014
status: reviewed
---
# PRO-Q014 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A timed-out write may have committed; represent unknown and reconcile by operation identity.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> timeout بعد إرسال write لا يثبت success ولاfailure؛ العملية تفضل Unknown ومربوطة بـstable operation ID لحد ما backend تؤكد الحالة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A payment request times out after the backend may have committed it. Model the client state and user experience until the result can be reconciled. Why are both success and failure unsafe guesses?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Unknown outcome:</strong> timeout بعد إرسال write لا يثبت success ولاfailure؛ العملية تفضل Unknown ومربوطة بـstable operation ID لحد ما backend تؤكد الحالة. اعرض Pending confirmation، امنع إنشاء charge جديدة، واستعلم بـoperation ID أوidempotency key. عند رجوع النتيجة حوّل الحالة مرة واحدة إلى Succeeded أوFailed وسجّل reconciliation واضح.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـUnknown outcome: اعرض Pending confirmation، امنع إنشاء charge جديدة، واستعلم بـoperation ID أوidempotency key. عند رجوع النتيجة حوّل الحالة مرة واحدة إلى Succeeded أوFailed وسجّل reconciliation واضح.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A timeout means the payment failed, so immediately create a new payment request.”

<p dir="rtl" lang="ar">في <strong>Unknown outcome</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: timeout بعد إرسال write لا يثبت success ولاfailure؛ العملية تفضل Unknown ومربوطة بـstable operation ID لحد ما backend تؤكد الحالة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Unknown outcome: للread الآمنة retry تلقائية مقبولة؛ للwrite غير idempotent من غير status API تحتاج manual reconciliation بدل تخمين النتيجة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Unknown outcome: اقطع الاتصال قبل وصول request، وبعد backend commit وقبل response، ووقت status lookup. اثبت إن الحالة الثانية تصبح Unknown وإن retry لا تعمل duplicate charge.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Unknown outcome، الـshortcut هي: <bdi dir="ltr">A timeout means the payment failed, so immediately create a new payment request.</bdi> ودي تكسر: timeout بعد إرسال write لا يثبت success ولاfailure؛ العملية تفضل Unknown ومربوطة بـstable operation ID لحد ما backend تؤكد الحالة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Unknown outcome: اقطع الاتصال قبل وصول request، وبعد backend commit وقبل response، ووقت status lookup. اثبت إن الحالة الثانية تصبح Unknown وإن retry لا تعمل duplicate charge.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Unknown outcome: للread الآمنة retry تلقائية مقبولة؛ للwrite غير idempotent من غير status API تحتاج manual reconciliation بدل تخمين النتيجة.</span>

## English model answer

“A timed-out write may have committed; represent unknown and reconcile by operation identity. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
