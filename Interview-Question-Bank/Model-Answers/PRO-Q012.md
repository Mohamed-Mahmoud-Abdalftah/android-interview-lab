---
id: PRO-Q012-ANSWER
question_id: PRO-Q012
status: reviewed
---
# PRO-Q012 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Retry only classified transient failures and only when operation semantics are safe or idempotent.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A POST /orders request timed out after bytes were sent. Is an automatic retry safe? Design the idempotency key, retry classification, and status lookup needed to prevent a duplicate order.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Retry safety:</strong> connect/read/call timeouts بتحصل في مراحل مختلفة. timeout بعد إرسال write لا تثبت إن server لم تنفذها. لذلك operation ID وidempotency/status lookup يمنعوا duplicate effect، وsingle-flight تخلي concurrent 401 تشارك refresh واحدة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRetry safety: صنّف connect/read/call/application timeout، استخدم single-flight للrefresh، cap وjitter للretry، واعمل status lookup للwrite ذات النتيجة المجهولة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Retry every exception with exponential backoff; the server will handle duplicates.”

<p dir="rtl" lang="ar">في <strong>Retry safety</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Retry safety: للread الآمنة automatic retry مناسبة؛ للwrite غير idempotent ارجع unknown واعمل reconcile بدل محاولة جديدة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Retry safety: حاكي concurrent 401 وtimeout قبل/بعد server commit وRetry-After وفشل permanent؛ اثبت refresh واحدة وعدم duplicate business effect.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Retry safety، الـshortcut هي: <bdi dir="ltr">Retry every exception with exponential backoff; the server will handle duplicates.</bdi> ودي تكسر: كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Retry safety: حاكي concurrent 401 وtimeout قبل/بعد server commit وRetry-After وفشل permanent؛ اثبت refresh واحدة وعدم duplicate business effect.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Retry safety: للread الآمنة automatic retry مناسبة؛ للwrite غير idempotent ارجع unknown واعمل reconcile بدل محاولة جديدة.</span>

## English model answer

“Retry only classified transient failures and only when operation semantics are safe or idempotent. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
