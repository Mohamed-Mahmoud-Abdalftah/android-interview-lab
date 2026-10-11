---
id: ARC-Q029-ANSWER
question_id: ARC-Q029
status: reviewed
---
# ARC-Q029 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Challenge assumptions with evidence and offer a viable alternative plus consequences.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> المراجعة تبدأ بـcorrectness invariant وownership وfailure path؛ القرار يوثق forces وalternatives وconsequences وrevisit trigger.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">You disagree with an accepted ADR after new production evidence appears. How do you challenge it constructively, what evidence is enough to reopen it, and how do you keep delivery moving meanwhile?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في ADR challenge:</strong> المراجعة القوية تتبع input إلى state mutation وside effect ثم failure path. الـADR تحفظ السبب والبدائل والنتائج وrevisit trigger؛ هي سجل قرار، مش شهادة إن القرار أبدي.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـADR challenge: تتبع input إلى state وside effect، صنّف blocker بالدليل، واقترح بديل viable؛ وثّق trade-off بدل تعليق style عام.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The architecture looks familiar, so naming and layer count are enough for approval.”

<p dir="rtl" lang="ar">في <strong>ADR challenge</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: المراجعة تبدأ بـcorrectness invariant وownership وfailure path؛ القرار يوثق forces وalternatives وconsequences وrevisit trigger. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في ADR challenge: suggestion غير blocking لو لا تمس correctness/security؛ متستخدمش سلطة reviewer لفرض preference بلا evidence.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار ADR challenge: حوّل الـinvariant لboundary test أو failure injection، وتأكد إن ADR فيها trigger قابل للقياس وإن conflict/ordering policy قابلة لإعادة الإنتاج.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في ADR challenge، الـshortcut هي: <bdi dir="ltr">The architecture looks familiar, so naming and layer count are enough for approval.</bdi> ودي تكسر: المراجعة تبدأ بـcorrectness invariant وownership وfailure path؛ القرار يوثق forces وalternatives وconsequences وrevisit trigger.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار ADR challenge: حوّل الـinvariant لboundary test أو failure injection، وتأكد إن ADR فيها trigger قابل للقياس وإن conflict/ordering policy قابلة لإعادة الإنتاج.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في ADR challenge: suggestion غير blocking لو لا تمس correctness/security؛ متستخدمش سلطة reviewer لفرض preference بلا evidence.</span>

## English model answer

“Challenge assumptions with evidence and offer a viable alternative plus consequences. I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis. I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.”
