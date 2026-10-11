---
id: INT-Q015-ANSWER
question_id: INT-Q015
status: reviewed
---
# INT-Q015 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Actions change code, tests, detection, or process and include owner, deadline, and proof of completion.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Turn 'be more careful' into owned, testable follow-ups. Which actions change prevention, detection, mitigation, and recovery?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Post-incident actions:</strong> وقت incident بنفصل observation عن hypothesis. coordinator واحدة تحفظ timeline، mitigation reversible تقلل الضرر، وبعدها experiment تفرق بين سببين. في security، client input غير موثوق والbackend تعيد authorization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـPost-incident actions: حدد versions/users/data impact، عيّن roles، rollback/flag بأقل blast radius، ثم اختبر hypothesis بالملاحظة الأكثر تمييزًا وسجل follow-ups قابلة للإغلاق.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Wait for the exact root cause before mitigating a high-impact incident.”

<p dir="rtl" lang="ar">في <strong>Post-incident actions</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Post-incident actions: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Post-incident actions: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Post-incident actions، الـshortcut هي: <bdi dir="ltr">Wait for the exact root cause before mitigating a high-impact incident.</bdi> ودي تكسر: الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Post-incident actions: اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Post-incident actions: pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.</span>

## English model answer

“Actions change code, tests, detection, or process and include owner, deadline, and proof of completion. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
