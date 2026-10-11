---
id: PRO-Q015-ANSWER
question_id: PRO-Q015
status: reviewed
---
# PRO-Q015 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Bound exponential delay, add jitter, honor server guidance, and stop on permanent failure.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Thousands of clients reconnect after an outage. Derive a capped exponential backoff with jitter, explain when to honor Retry-After, and name failures that must not be retried.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Backoff and jitter:</strong> connect/read/call timeouts بتحصل في مراحل مختلفة. timeout بعد إرسال write لا تثبت إن server لم تنفذها. لذلك operation ID وidempotency/status lookup يمنعوا duplicate effect، وsingle-flight تخلي concurrent 401 تشارك refresh واحدة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBackoff and jitter: صنّف connect/read/call/application timeout، استخدم single-flight للrefresh، cap وjitter للretry، واعمل status lookup للwrite ذات النتيجة المجهولة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Retry every exception with exponential backoff; the server will handle duplicates.”

<p dir="rtl" lang="ar">في <strong>Backoff and jitter</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Backoff and jitter: للread الآمنة automatic retry مناسبة؛ للwrite غير idempotent ارجع unknown واعمل reconcile بدل محاولة جديدة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Backoff and jitter: حاكي concurrent 401 وtimeout قبل/بعد server commit وRetry-After وفشل permanent؛ اثبت refresh واحدة وعدم duplicate business effect.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Backoff and jitter، الـshortcut هي: <bdi dir="ltr">Retry every exception with exponential backoff; the server will handle duplicates.</bdi> ودي تكسر: كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Backoff and jitter: حاكي concurrent 401 وtimeout قبل/بعد server commit وRetry-After وفشل permanent؛ اثبت refresh واحدة وعدم duplicate business effect.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Backoff and jitter: للread الآمنة automatic retry مناسبة؛ للwrite غير idempotent ارجع unknown واعمل reconcile بدل محاولة جديدة.</span>

## English model answer

“Bound exponential delay, add jitter, honor server guidance, and stop on permanent failure. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
