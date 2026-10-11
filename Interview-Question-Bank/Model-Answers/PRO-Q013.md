---
id: PRO-Q013-ANSWER
question_id: PRO-Q013
status: reviewed
---
# PRO-Q013 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Concurrent 401 responses share one refresh result and avoid recursive authentication loops.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل مجموعة 401 ناتجة عن نفس الـexpired token تشارك refresh واحدة، وكل request أصلية تُعاد مرة واحدة فقط؛ فشل refresh ينهي الجلسة بدل loop جديدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Ten requests receive 401 at the same time and each starts a token refresh. Design a single-flight refresh flow, including refresh failure, a repeated 401, cancellation, and replaying the original requests once.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Token refresh single-flight:</strong> كل مجموعة 401 ناتجة عن نفس الـexpired token تشارك refresh واحدة، وكل request أصلية تُعاد مرة واحدة فقط؛ فشل refresh ينهي الجلسة بدل loop جديدة. احمِ refresh بsingle-flight primitive، افحص إن الـtoken التي فشلت ما زالت current، انشر token الجديدة atomically، ثم replay مرة واحدة. لو refresh رجعت 401 أوفشلت نهائيًا امسح session واطلب login.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـToken refresh single-flight: احمِ refresh بsingle-flight primitive، افحص إن الـtoken التي فشلت ما زالت current، انشر token الجديدة atomically، ثم replay مرة واحدة. لو refresh رجعت 401 أوفشلت نهائيًا امسح session واطلب login.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Let every failed request refresh independently and keep retrying until one succeeds.”

<p dir="rtl" lang="ar">في <strong>Token refresh single-flight</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل مجموعة 401 ناتجة عن نفس الـexpired token تشارك refresh واحدة، وكل request أصلية تُعاد مرة واحدة فقط؛ فشل refresh ينهي الجلسة بدل loop جديدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Token refresh single-flight: Authenticator مركزي مناسب لو الـHTTP stack تضمن serialization؛ repository-level coordination أوضح لو token جزء من session state machine أوسع.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Token refresh single-flight: ابدأ عشر requests بنفس الـtoken، أرجع لهم 401 معًا، وتأكد من refresh call واحدة وعشر replays فقط. غطّ cancellation وrefresh failure و401 ثانية بعد replay.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Token refresh single-flight، الـshortcut هي: <bdi dir="ltr">Let every failed request refresh independently and keep retrying until one succeeds.</bdi> ودي تكسر: كل مجموعة 401 ناتجة عن نفس الـexpired token تشارك refresh واحدة، وكل request أصلية تُعاد مرة واحدة فقط؛ فشل refresh ينهي الجلسة بدل loop جديدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Token refresh single-flight: ابدأ عشر requests بنفس الـtoken، أرجع لهم 401 معًا، وتأكد من refresh call واحدة وعشر replays فقط. غطّ cancellation وrefresh failure و401 ثانية بعد replay.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Token refresh single-flight: Authenticator مركزي مناسب لو الـHTTP stack تضمن serialization؛ repository-level coordination أوضح لو token جزء من session state machine أوسع.</span>

## English model answer

“Concurrent 401 responses share one refresh result and avoid recursive authentication loops. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
