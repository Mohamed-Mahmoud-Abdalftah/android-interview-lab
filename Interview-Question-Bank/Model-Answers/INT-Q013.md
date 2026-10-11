---
id: INT-Q013-ANSWER
question_id: INT-Q013
status: reviewed
---
# INT-Q013 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “One owner coordinates decisions, communications, operations, and a shared factual timeline.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A mobile incident has ten engineers changing things at once. Define Incident Commander, communications, investigation, mitigation, and scribe roles and their decision boundaries.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Incident roles:</strong> وقت incident بنفصل observation عن hypothesis. coordinator واحدة تحفظ timeline، mitigation reversible تقلل الضرر، وبعدها experiment تفرق بين سببين. في security، client input غير موثوق والbackend تعيد authorization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـIncident roles: حدد versions/users/data impact، عيّن roles، rollback/flag بأقل blast radius، ثم اختبر hypothesis بالملاحظة الأكثر تمييزًا وسجل follow-ups قابلة للإغلاق.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Wait for the exact root cause before mitigating a high-impact incident.”

<p dir="rtl" lang="ar">في <strong>Incident roles</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Incident roles: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Incident roles: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Incident roles، الـshortcut هي: <bdi dir="ltr">Wait for the exact root cause before mitigating a high-impact incident.</bdi> ودي تكسر: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Incident roles: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Incident roles: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</span>

## English model answer

“One owner coordinates decisions, communications, operations, and a shared factual timeline. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
