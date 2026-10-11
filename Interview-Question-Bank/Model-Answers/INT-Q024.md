---
id: INT-Q024-ANSWER
question_id: INT-Q024
status: reviewed
---
# INT-Q024 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Separate what you know, infer, and would verify without bluffing.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">You do not remember an exact Android version rule. Demonstrate how to state what you know, isolate the uncertainty, and describe the authoritative verification.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Uncertainty language:</strong> الإجابة القوية تبدأ conclusion قصيرة، ثم mechanism ومثال وفشل وtrade-off حسب الوقت. المرشح يفصل اللي نفذه عن اللي صممه نظريًا، ويسأل عن constraint تغير القرار بدل ما يفترضها.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـUncertainty language: ابدأ answer headline، اسأل constraint مؤثرة، فكر بصوت مرتب، سمّي uncertainty وخطة verification، واختم بقرار واختبار.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A long memorized answer and confident wording are enough even when the evidence was never executed.”

<p dir="rtl" lang="ar">في <strong>Uncertainty language</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Uncertainty language: قل “I have not run that on Android; here is the JVM model and how I would verify it” بدل bluff أو توقف كامل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Uncertainty language: سجل 20 ثانية و90 ثانية لنفس السؤال، راجع fillers والmissing boundary، ثم أعد سؤال follow-up من غير قراءة نص محفوظ.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Uncertainty language، الـshortcut هي: <bdi dir="ltr">A long memorized answer and confident wording are enough even when the evidence was never executed.</bdi> ودي تكسر: الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Uncertainty language: سجل 20 ثانية و90 ثانية لنفس السؤال، راجع fillers والmissing boundary، ثم أعد سؤال follow-up من غير قراءة نص محفوظ.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Uncertainty language: قل “I have not run that on Android; here is the JVM model and how I would verify it” بدل bluff أو توقف كامل.</span>

## English model answer

“Separate what you know, infer, and would verify without bluffing. I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people. I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.”
