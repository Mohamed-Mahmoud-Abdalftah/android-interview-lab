---
id: PRO-Q024-ANSWER
question_id: PRO-Q024
status: reviewed
---
# PRO-Q024 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Distinguish allocation churn, retained objects, native memory, and process pressure before calling a leak.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Memory grows after opening and closing a screen ten times. Design an investigation that separates a retained Activity from allocation churn, bitmap or native memory, and normal heap growth.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Memory evidence:</strong> القياس يبدأ journey وbuild وdevice class ثابتين. Perfetto يربط scheduling وBinder وI/O وframes على timeline، heap dump تبحث عن retained paths، وMacrobenchmark تقارن startup أوframe percentiles. أداة واحدة لا تجيب كل الأسئلة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMemory evidence: عرّف user metric وcohort، اجمع trace على profileable release-like build، وافصل scheduling/Binder/I/O/frame أو allocation/retention حسب السؤال.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “One fast debug run or one large heap snapshot proves the production diagnosis.”

<p dir="rtl" lang="ar">في <strong>Memory evidence</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Memory evidence: Macrobenchmark يقيس journey؛ heap dump يثبت retention؛ Perfetto يشرح timeline. اختار الأداة حسب hypothesis.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Memory evidence: كرر بعد warm-up عند نقاط ثابتة، قارن percentiles مع baseline، واثبت إن التحسن لا يكسر memory أو correctness أو accessibility guardrail.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Memory evidence، الـshortcut هي: <bdi dir="ltr">One fast debug run or one large heap snapshot proves the production diagnosis.</bdi> ودي تكسر: المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Memory evidence: كرر بعد warm-up عند نقاط ثابتة، قارن percentiles مع baseline، واثبت إن التحسن لا يكسر memory أو correctness أو accessibility guardrail.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Memory evidence: Macrobenchmark يقيس journey؛ heap dump يثبت retention؛ Perfetto يشرح timeline. اختار الأداة حسب hypothesis.</span>

## English model answer

“Distinguish allocation churn, retained objects, native memory, and process pressure before calling a leak. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
