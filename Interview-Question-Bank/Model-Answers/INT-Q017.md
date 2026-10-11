---
id: INT-Q017-ANSWER
question_id: INT-Q017
status: reviewed
---
# INT-Q017 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Map external intents, network, storage, IPC, WebView, vendor SDKs, and backend authority.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Threat-model a mobile payment flow across app, OS intent, terminal SDK, backend, and provider. What input is untrusted at each boundary?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Trust boundaries:</strong> وقت incident بنفصل observation عن hypothesis. coordinator واحدة تحفظ timeline، mitigation reversible تقلل الضرر، وبعدها experiment تفرق بين سببين. في security، client input غير موثوق والbackend تعيد authorization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTrust boundaries: ارسم trust boundaries، رتب المخاطر، اختبر hostile input/authorization وrelease percentiles، واعرض البدائل والrollback signal بوضوح.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Performance wins justify moving authorization to the client or embedding a fixed secret in the APK.”

<p dir="rtl" lang="ar">في <strong>Trust boundaries</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Trust boundaries: تحسين صغير reversible قد يسبق redesign؛ لا تقبل إزالة auth check أوhard-coded key مقابل startup أسرع.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Trust boundaries: شغّل unauthorized/oversized/replayed inputs وrepresentative macro journey، وتأكد من redaction وعدم تخطي correctness مقابل performance.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Trust boundaries، الـshortcut هي: <bdi dir="ltr">Performance wins justify moving authorization to the client or embedding a fixed secret in the APK.</bdi> ودي تكسر: الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Trust boundaries: شغّل unauthorized/oversized/replayed inputs وrepresentative macro journey، وتأكد من redaction وعدم تخطي correctness مقابل performance.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Trust boundaries: تحسين صغير reversible قد يسبق redesign؛ لا تقبل إزالة auth check أوhard-coded key مقابل startup أسرع.</span>

## English model answer

“Map external intents, network, storage, IPC, WebView, vendor SDKs, and backend authority. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
