---
id: INT-Q022-ANSWER
question_id: INT-Q022
status: reviewed
---
# INT-Q022 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Add mechanism, concrete example, failure path, and trade-off.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Expand the same structured-concurrency answer to ninety seconds without rambling: include cancellation, failure propagation, ownership, and a concrete Android example.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Ninety-second depth:</strong> الإجابة القوية تبدأ conclusion قصيرة، ثم mechanism ومثال وفشل وtrade-off حسب الوقت. المرشح يفصل اللي نفذه عن اللي صممه نظريًا، ويسأل عن constraint تغير القرار بدل ما يفترضها.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـNinety-second depth: ابدأ answer headline، اسأل constraint مؤثرة، فكر بصوت مرتب، سمّي uncertainty وخطة verification، واختم بقرار واختبار.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A long memorized answer and confident wording are enough even when the evidence was never executed.”

<p dir="rtl" lang="ar">في <strong>Ninety-second depth</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Ninety-second depth: قل “I have not run that on Android; here is the JVM model and how I would verify it” بدل bluff أو توقف كامل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Ninety-second depth: سجل 20 ثانية و90 ثانية لنفس السؤال، راجع fillers والmissing boundary، ثم أعد سؤال follow-up من غير قراءة نص محفوظ.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Ninety-second depth، الـshortcut هي: <bdi dir="ltr">A long memorized answer and confident wording are enough even when the evidence was never executed.</bdi> ودي تكسر: الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Ninety-second depth: سجل 20 ثانية و90 ثانية لنفس السؤال، راجع fillers والmissing boundary، ثم أعد سؤال follow-up من غير قراءة نص محفوظ.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Ninety-second depth: قل “I have not run that on Android; here is the JVM model and how I would verify it” بدل bluff أو توقف كامل.</span>

## English model answer

“Add mechanism, concrete example, failure path, and trade-off. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
