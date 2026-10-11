---
id: INT-Q018-ANSWER
question_id: INT-Q018
status: reviewed
---
# INT-Q018 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Measure representative journeys and percentiles on controlled release builds.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A debug build is slow but release feels fine. Explain which performance conclusions are valid and build a representative measurement instead of arguing from either run.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Release-like performance:</strong> performance claim تحتاج نفس journey وrelease build وdevice class وpercentile. الـtrade-off يتقال كـinvariant بنحميها، تكلفة مقاسة، بدائل، وrollback signal؛ من غيرهم تبقى preference لاقرار هندسي.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRelease-like performance: ارسم trust boundaries، رتب المخاطر، اختبر hostile input/authorization وrelease percentiles، واعرض البدائل والrollback signal بوضوح.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Performance wins justify moving authorization to the client or embedding a fixed secret in the APK.”

<p dir="rtl" lang="ar">في <strong>Release-like performance</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Release-like performance: تحسين صغير reversible قد يسبق redesign؛ لا تقبل إزالة auth check أوhard-coded key مقابل startup أسرع.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Release-like performance: شغّل unauthorized/oversized/replayed inputs وrepresentative macro journey، وتأكد من redaction وعدم تخطي correctness مقابل performance.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Release-like performance، الـshortcut هي: <bdi dir="ltr">Performance wins justify moving authorization to the client or embedding a fixed secret in the APK.</bdi> ودي تكسر: الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Release-like performance: شغّل unauthorized/oversized/replayed inputs وrepresentative macro journey، وتأكد من redaction وعدم تخطي correctness مقابل performance.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Release-like performance: تحسين صغير reversible قد يسبق redesign؛ لا تقبل إزالة auth check أوhard-coded key مقابل startup أسرع.</span>

## English model answer

“Measure representative journeys and percentiles on controlled release builds. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
