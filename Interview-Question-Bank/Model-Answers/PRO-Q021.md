---
id: PRO-Q021-ANSWER
question_id: PRO-Q021
status: reviewed
---
# PRO-Q021 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Name the user journey, metric, percentile, device class, build, and competing cause before collecting data.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Cold startup became 20% slower in one local run. Define a measurement plan that can tell regression from noise, including build type, startup mode, device class, iterations, and percentile.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Measurement question:</strong> القياس يبدأ journey وbuild وdevice class ثابتين. Perfetto يربط scheduling وBinder وI/O وframes على timeline، heap dump تبحث عن retained paths، وMacrobenchmark تقارن startup أوframe percentiles. أداة واحدة لا تجيب كل الأسئلة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMeasurement question: عرّف user metric وcohort، اجمع trace على profileable release-like build، وافصل scheduling/Binder/I/O/frame أو allocation/retention حسب السؤال.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “One fast debug run or one large heap snapshot proves the production diagnosis.”

<p dir="rtl" lang="ar">في <strong>Measurement question</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Measurement question: Macrobenchmark يقيس journey؛ heap dump يثبت retention؛ Perfetto يشرح timeline. اختار الأداة حسب hypothesis.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Measurement question: كرر بعد warm-up عند نقاط ثابتة، قارن percentiles مع baseline، واثبت إن التحسن لا يكسر memory أو correctness أو accessibility guardrail.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Measurement question، الـshortcut هي: <bdi dir="ltr">One fast debug run or one large heap snapshot proves the production diagnosis.</bdi> ودي تكسر: المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Measurement question: كرر بعد warm-up عند نقاط ثابتة، قارن percentiles مع baseline، واثبت إن التحسن لا يكسر memory أو correctness أو accessibility guardrail.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Measurement question: Macrobenchmark يقيس journey؛ heap dump يثبت retention؛ Perfetto يشرح timeline. اختار الأداة حسب hypothesis.</span>

## English model answer

“Name the user journey, metric, percentile, device class, build, and competing cause before collecting data. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
