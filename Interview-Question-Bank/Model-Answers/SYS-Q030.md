---
id: SYS-Q030-ANSWER
question_id: SYS-Q030
status: reviewed
---
# SYS-Q030 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use invariants, failure injection, load model, observability, and staged rollout to test assumptions.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل mutable state لها authority وupdate path وpersistence/conflict contract، والتصميم مربوط بأرقام scale وفشل قابل للاختبار.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Turn a mobile sync design into a verification plan with failure injection for process death, offline edits, duplicates, gaps, conflicts, and account switching.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Design verification:</strong> قبل رسم components بنحوّل requirements إلى state machine وidentities وSLO. كل mutable state لها authority واحدة وpersistence level وconflict policy؛ البدائل تتقارن بنفس معايير latency وconsistency وcost وrecovery، ثم failure injection تختبر assumptions.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـDesign verification: اسأل عن latency/offline/consistency/privacy، ارسم state machine وحدود client/server، قارن البدائل بمعايير ثابتة، وحدد migration وrollback.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Choose the most scalable architecture first and fill in requirements later.”

<p dir="rtl" lang="ar">في <strong>Design verification</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل mutable state لها authority وupdate path وpersistence/conflict contract، والتصميم مربوط بأرقام scale وفشل قابل للاختبار. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Design verification: اختار design أبسط لو scale أو consistency لا تبرر distributed coordination؛ اذكر trigger رقمي لإعادة النظر.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Design verification: حوّل أهم assumptions لـload model وفشل injected: duplicate، gap، account switch، process death؛ راقب SLO وcorrectness invariant قبل rollout.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Design verification، الـshortcut هي: <bdi dir="ltr">Choose the most scalable architecture first and fill in requirements later.</bdi> ودي تكسر: كل mutable state لها authority وupdate path وpersistence/conflict contract، والتصميم مربوط بأرقام scale وفشل قابل للاختبار.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Design verification: حوّل أهم assumptions لـload model وفشل injected: duplicate، gap، account switch، process death؛ راقب SLO وcorrectness invariant قبل rollout.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Design verification: اختار design أبسط لو scale أو consistency لا تبرر distributed coordination؛ اذكر trigger رقمي لإعادة النظر.</span>

## English model answer

“Use invariants, failure injection, load model, observability, and staged rollout to test assumptions. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
